from selenium.common.exceptions import NoSuchElementException
from .scraping_utilities import Scraping_utilities
from .utilities import Utilities
import sys
import urllib.request
import re
from dateutil.parser import parse
import dateutil
import datetime
from selenium.webdriver.common.by import By
import logging


logger = logging.getLogger(__name__)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(format)
logger.addHandler(ch)

class Finder:
    @staticmethod
    def __get_status_link(link_list):
        status = ""
        for link in link_list:
            link_value = link.get_attribute("href")
            if "/posts/" in link_value and "/groups/" in link_value:
                status = link
                break
            if "/posts/" in link_value:
                status = link
                break
            if "/videos/pcb" in link_value:
                status = link
                break
            elif "/photos/" in link_value:
                status = link
                break
            if "fbid=" in link_value:
                status = link
                break
            elif "/group/" in link_value:
                status = link
                break
            if "/videos/" in link_value:
                status = link
                break
            elif "/groups/" in link_value:
                status = link
                break
        return status
    
    @staticmethod
    def __find_status(post, layout):
        """finds URL of the post, then extracts link from that URL and returns it"""
        try:
            link = None
            status_link = None
            if layout == "old":
                status_link = post.find_element(By.CLASS_NAME, "_5pcq").get_attribute(
                    "href"
                )
                status = Scraping_utilities._Scraping_utilities__extract_id_from_link(
                    status_link
                )
            elif layout == "new":
                link = post.find_element(
                    By.CSS_SELECTOR, 'span > a[aria-label][role="link"]'
                )
                status_link = link.get_attribute("href")
                status = Scraping_utilities._Scraping_utilities__extract_id_from_link(
                    status_link
                )
        except NoSuchElementException:
            status = "NA"

        except Exception as ex:
            logger.exception("Error at find_status method : {}".format(ex))
            status = "NA"

        return (status, status_link, link)
    
    @staticmethod
    def __find_share(post, layout):
        """finds shares count of the facebook post using selenium's webdriver's method"""
        try:
            if layout == "old":
                shares = post.find_element(
                    By.CSS_SELECTOR, "._355t._4vn2"
                ).get_attribute("textContent")
                shares = Scraping_utilities._Scraping_utilities__extract_numbers(shares)
            elif layout == "new":
                element = post.find_element(
                    By.CSS_SELECTOR, 'div:nth-child(2) > span > div > div > div:nth-child(1) > span'
                )
                shares = "0"
                if not element:
                  return shares
                return element.text
            return shares
        except NoSuchElementException:
            shares = 0

        except Exception as ex:
            logger.exception("Error at Find Share method : {}".format(ex))
            shares = 0

        return shares
    

    @staticmethod
    def __find_reactions(post):
        """finds all reaction of the facebook post using selenium's webdriver's method"""
        try:
            reactions_all = post.find_element(
                By.CSS_SELECTOR, '[aria-label="See who reacted to this"]'
            )
        except NoSuchElementException:
            reactions_all = ""
        except Exception as ex:
            logger.exception("Error at find_reactions method : {}".format(ex))
        return reactions_all

    @staticmethod
    def __find_comments(post, layout):
        """finds comments count of the facebook post using selenium's webdriver's method"""
        try:
            comments = ""
            if layout == "old":
                comments = post.find_element(By.CSS_SELECTOR, "a._3hg-").get_attribute(
                    "textContent"
                )
                # extract numbers from text
                comments = Scraping_utilities._Scraping_utilities__extract_numbers(
                    comments
                )
            elif layout == "new":
                element = post.find_element(
                    By.CSS_SELECTOR, 'div:nth-child(1) > span > div > div > div:nth-child(1) > span'
                )
                comments = 0
                if element is None:
                    return comments
                return element.text
        except NoSuchElementException:
            comments = 0
        except Exception as ex:
            logger.exception("Error at find_comments method : {}".format(ex))
            comments = 0

        return comments

    @staticmethod
    def __fetch_post_passage(href):

        response = urllib.request.urlopen(href)

        text = response.read().decode("utf-8")

        post_message_div_finder_regex = (
            '<div data-testid="post_message" class=".*?" data-ft=".*?">(.*?)<\/div>'
        )

        post_message = re.search(post_message_div_finder_regex, text)

        replace_html_tags_regex = "<[^<>]+>"
        message = re.sub(replace_html_tags_regex, "", post_message.group(0))

        return message

    @staticmethod
    def __element_exists(element, css_selector):
        try:
            found = element.find_element(By.CSS_SELECTOR, css_selector)
            return True
        except NoSuchElementException:
            return False

    @staticmethod
    def __find_content(post, driver, layout):
        """finds content of the facebook post using selenium's webdriver's method and returns string containing text of the posts"""
        try:
            if layout == "old":
                post_content = post.find_element(By.CLASS_NAME, "userContent")
                # if 'See more' or 'Continue reading' is present in post
                if Finder._Finder__element_exists(
                    post_content, "span.text_exposed_link > a"
                ):
                    element = post_content.find_element(
                        By.CSS_SELECTOR, "span.text_exposed_link > a"
                    )  
                    if element.get_attribute("onclick"):
                        Utilities._Utilities__click_see_more(driver, post_content)
                        content = (
                            Scraping_utilities._Scraping_utilities__extract_content(
                                post_content
                            )
                        ) 
                    elif element.get_attribute("target"):
                        content = Finder._Finder__fetch_post_passage(
                            element.get_attribute("href")
                        )
                    else:
                        content = post_content.get_attribute("textContent")
                else:
                    content = post_content.get_attribute("textContent")
            elif layout == "new":
                post_content = post.find_element(
                    By.CSS_SELECTOR, '[data-ad-preview="message"]'
                )
                if Finder._Finder__element_exists(
                    post_content, 'div[dir="auto"] > div[role]'
                ):
                    element = post_content.find_element(
                        By.CSS_SELECTOR, 'div[dir="auto"] > div[role]'
                    )  
                    if element.get_attribute("target"):
                        content = Finder._Finder__fetch_post_passage(
                            element.get_attribute("href")
                        )
                    else:
                        Utilities._Utilities__click_see_more(
                            driver, post_content, 'div[dir="auto"] > div[role]'
                        )
                        content = post_content.get_attribute(
                            "textContent"
                        )  
                else:
                    
                    content = post_content.get_attribute("textContent")

        except NoSuchElementException:
            content = ""
        except Exception as ex:
            logger.exception("Error at find_content method : {}".format(ex))
            content = ""
        return content

    @staticmethod
    def __find_posted_time(post, layout, link_element):
        """finds posted time of the facebook post using selenium's webdriver's method"""
        try:
            if layout == "old":
                posted_time = post.find_element(By.TAG_NAME, "abbr").get_attribute(
                    "data-utime"
                )
                return datetime.datetime.fromtimestamp(float(posted_time)).isoformat()
            elif layout == "new":
                aria_label_value = link_element.get_attribute("aria-label")
                timestamp = (
                    parse(aria_label_value).isoformat()
                    if len(aria_label_value) > 5
                    else Scraping_utilities._Scraping_utilities__convert_to_iso(
                        aria_label_value
                    )
                )
                return timestamp
        except dateutil.parser._parser.ParserError:
            timestamp = Scraping_utilities._Scraping_utilities__convert_to_iso(
                aria_label_value
            )
            return timestamp
        except TypeError:
            timestamp = ""
        except Exception as ex:
            logger.exception("Error at find_posted_time method : {}".format(ex))
            timestamp = ""
            return timestamp

    @staticmethod
    def __find_video_url(post):
        """finds video of the facebook post using selenium's webdriver's method"""
        try:
            video_element = post.find_elements(By.TAG_NAME, "video")
            srcs = []
            for video in video_element:
                srcs.append(video.get_attribute("src"))
        except NoSuchElementException:
            video = []
            pass
        except Exception as ex:
            video = []
            logger.exception("Error at find_video_url method : {}".format(ex))

        return srcs

    @staticmethod
    def __find_image_url(post, layout):
        """finds all image of the facebook post using selenium's webdriver's method"""
        try:
            if layout == "old":
                images = post.find_elements(
                    By.CSS_SELECTOR, "img.scaledImageFitWidth.img"
                )
            elif layout == "new":
                images = post.find_elements(
                    By.CSS_SELECTOR, "div > img[referrerpolicy]"
                )
            sources = (
                [image.get_attribute("src") for image in images]
                if len(images) > 0
                else []
            )
        except NoSuchElementException:
            sources = []
            pass
        except Exception as ex:
            logger.exception("Error at find_image_url method : {}".format(ex))
            sources = []

        return sources

    @staticmethod
    def __find_all_posts(driver, layout):
        """finds all posts of the facebook page using selenium's webdriver's method"""
        try:
            if layout == "old":
                all_posts = driver.find_elements(
                    By.CSS_SELECTOR, "div.userContentWrapper"
                )
            elif layout == "new":
                all_posts = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
            return all_posts
        except NoSuchElementException:
            logger.error("Cannot find any posts! Exiting!")
            Utilities.__close_driver(driver)
            sys.exit(1)
        except Exception as ex:
            logger.exception("Error at find_all_posts method : {}".format(ex))
            Utilities.__close_driver(driver)
            sys.exit(1)

    @staticmethod
    def __find_name(driver, layout):
        """finds name of the facebook page using selenium's webdriver's method"""
        try:
            if layout == "old":
                name = driver.find_element(By.CSS_SELECTOR, "a._64-f").get_attribute(
                    "textContent"
                )
            elif layout == "new":
                name = driver.find_element(By.TAG_NAME, "strong").get_attribute(
                    "textContent"
                )
            return name
        except Exception as ex:
            logger.exception("Error at __find_name method : {}".format(ex))

    @staticmethod
    def __detect_ui(driver):
        try:
            driver.find_element(By.ID, "pagelet_bluebar")
            return "old"
        except NoSuchElementException:
            return "new"
        except Exception as ex:
            logger.exception("Error art __detect_ui: {}".format(ex))
            Utilities.__close_driver(driver)
            sys.exit(1)

    @staticmethod
    def __find_reaction(layout, reactions_all):
        try:
            if layout == "old":
                return reactions_all.find_elements(By.TAG_NAME, "a")
            elif layout == "new":
                return reactions_all.find_elements(By.TAG_NAME, "div")

        except Exception as ex:
            logger.exception("Error at find_reaction : {}".format(ex))
            return ""

    @staticmethod
    def __accept_cookies(driver):
        try:
            button = driver.find_elements(
                By.CSS_SELECTOR, '[aria-label="Allow essential and optional cookies"]'
            )
            button[-1].click()
        except (NoSuchElementException, IndexError):
            pass
        except Exception as ex:
            logger.exception("Error at accept_cookies: {}".format(ex))
            sys.exit(1)
