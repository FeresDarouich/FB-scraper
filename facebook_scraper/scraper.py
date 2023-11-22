from .initializer import Initializer
from .utilities import Utilities
from .finder import Finder
from .scraping_utilities import Scraping_utilities
import json
import csv
import os
import time
import logging

logger = logging.getLogger(__name__)
format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(format)
logger.addHandler(ch)

class Facebook_scraper:

    def __init__(self, page_name, posts_count=10, browser="chrome", proxy=None, timeout=600, headless=True):
        self.page_name = page_name
        self.posts_count = int(posts_count)
        self.URL = "https://facebook.com/{}".format(self.page_name)
        self.browser = browser
        self.__driver = ''
        self.proxy = proxy
        self.__layout = ''
        self.timeout = timeout
        self.headless = headless
        self.__data_dict = {}  
        self.__extracted_post = set()

    def __start_driver(self):
        """changes the class member __driver value to driver on call"""
        self.__driver = Initializer(
            self.browser, self.proxy, self.headless).init()

    def __handle_popup(self, layout):
        try:
            if layout == "old":
                Utilities._Utilities__close_error_popup(self.__driver)
                Utilities._Utilities__close_popup(self.__driver)
            elif layout == "new":
                Utilities._Utilities__close_modern_layout_signup_modal(
                    self.__driver)
                Utilities._Utilities__close_cookie_consent_modern_layout(
                    self.__driver)

        except Exception as ex:
            logger.exception("Error at handle_popup : {}".format(ex))

    def __check_timeout(self, start_time, current_time):
        return (current_time-start_time) > self.timeout

    def scrap_to_json(self):
        self.__start_driver()
        starting_time = time.time()
        # navigate to URL
        self.__driver.get(self.URL)
        Finder._Finder__accept_cookies(self.__driver)
        self.__layout = Finder._Finder__detect_ui(self.__driver)
        Utilities._Utilities__close_error_popup(self.__driver)
        # wait for post to load
        Utilities._Utilities__wait_for_element_to_appear(
            self.__driver, self.__layout)
        # scroll down to bottom most
        Utilities._Utilities__scroll_down(self.__driver, self.__layout)
        self.__handle_popup(self.__layout)

        name = Finder._Finder__find_name(
            self.__driver, self.__layout)  

        while len(self.__data_dict) <= self.posts_count:
            self.__handle_popup(self.__layout)
            self.__find_elements(name)
            current_time = time.time()
            if self.__check_timeout(starting_time, current_time) is True:
                logger.setLevel(logging.INFO)
                logger.info('Timeout...')
                break
            Utilities._Utilities__scroll_down(
                self.__driver, self.__layout)  # scroll down
        Utilities._Utilities__close_driver(self.__driver)
        self.__data_dict = dict(list(self.__data_dict.items())[
                                0:int(self.posts_count)])

        return json.dumps(self.__data_dict, ensure_ascii=False)

    def __json_to_csv(self, filename, json_data, directory):

        os.chdir(directory)  
        fieldnames = ['id', 'name', 'shares', 'likes', 'loves', 'wow', 'cares', 'sad', 'angry', 'haha', 'reactions_count', 'comments',
                      'content', 'posted_on', 'video', 'image', 'post_url']
        mode = 'w'
        if os.path.exists("{}.csv".format(filename)):
            mode = 'a'
        with open("{}.csv".format(filename), mode, newline='', encoding="utf-8") as data_file:
            writer = csv.DictWriter(data_file, fieldnames=fieldnames)
            if mode == 'w':
                writer.writeheader()  
            for key in json_data:
                row = {'id': key, 'name': json_data[key]['name'], 'shares': json_data[key]['shares'],
                       'likes': json_data[key]['reactions']['likes'], 'loves':  json_data[key]['reactions']['loves'],
                       'wow': json_data[key]['reactions']['wow'], 'cares': json_data[key]['reactions']['cares'],
                       'sad': json_data[key]['reactions']['sad'], 'angry': json_data[key]['reactions']['angry'],
                       'haha': json_data[key]['reactions']['haha'], 'reactions_count': json_data[key]['reaction_count'],
                       'comments': json_data[key]['comments'], 'content': json_data[key]['content'], 'posted_on': json_data[key]['posted_on'],
                       'video': json_data[key]['video'], 'image': " ".join(json_data[key]['image']), 'post_url': json_data[key]['post_url']
                       }
                writer.writerow(row) 

            data_file.close()  




    def get_csv(self, filename, json_data):

        fieldnames = ['id', 'name', 'shares', 'likes', 'loves', 'wow', 'cares', 'sad', 'angry', 'haha', 'reactions_count', 'comments',
                      'content', 'posted_on', 'video', 'image', 'post_url']
        mode = 'w'
        with open("{}.csv".format(filename), mode, newline='', encoding="utf-8") as data_file:
            writer = csv.DictWriter(data_file, fieldnames=fieldnames)
            if mode == 'w':
                writer.writeheader() 
            for key in json_data:
                row = {'id': key, 'name': json_data[key]['name'], 'shares': json_data[key]['shares'],
                       'likes': json_data[key]['reactions']['likes'], 'loves':  json_data[key]['reactions']['loves'],
                       'wow': json_data[key]['reactions']['wow'], 'cares': json_data[key]['reactions']['cares'],
                       'sad': json_data[key]['reactions']['sad'], 'angry': json_data[key]['reactions']['angry'],
                       'haha': json_data[key]['reactions']['haha'], 'reactions_count': json_data[key]['reaction_count'],
                       'comments': json_data[key]['comments'], 'content': json_data[key]['content'], 'posted_on': json_data[key]['posted_on'],
                       'video': json_data[key]['video'], 'image': " ".join(json_data[key]['image']), 'post_url': json_data[key]['post_url']
                       }
                writer.writerow(row)  
            data_file.close()  
        return "{}.csv".format(filename)

    def scrap_to_csv(self, filename, directory=os.getcwd()):
        try:
            data = self.scrap_to_json()  
            self.__json_to_csv(filename, json.loads(data), directory)
            return True
        except Exception as ex:
            logger.exception('Error at scrap_to_csv : {}'.format(ex))
            return False

    def __remove_duplicates(self, all_posts):
        """takes a list of posts and removes duplicates from it and returns the list"""
        if len(self.__extracted_post) == 0:  
            self.__extracted_post.update(all_posts)
            return all_posts  
        else:
            removed_duplicated = [
                post for post in all_posts if post not in self.__extracted_post]
            self.__extracted_post.update(all_posts)
            return removed_duplicated  

    def __close_after_retry(self):
        """returns if class member retry is 0"""
        return self.retry <= 0

    def __no_post_found(self, all_posts):
        """if all_posts were found to be length of 0"""
        if len(all_posts) == 0:
            self.retry -= 1

    def __find_elements(self, name):
        """find elements of posts and add them to data_dict"""
        all_posts = Finder._Finder__find_all_posts(
            self.__driver, self.__layout)  
        all_posts = self.__remove_duplicates(
            all_posts) 
        for post in all_posts:
            try:
                status, post_url, link_element = Finder._Finder__find_status(
                    post, self.__layout)
                if post_url is None:
                    continue
            
                shares = Finder._Finder__find_share(post, self.__layout)
                shares = int(
                    Scraping_utilities._Scraping_utilities__value_to_float(shares))
                reactions_all = Finder._Finder__find_reactions(post)
                all_hrefs_in_react = Finder._Finder__find_reaction(self.__layout, reactions_all,) if type(
                    reactions_all) != str else ""
    
                if type(all_hrefs_in_react) == list:
                    l = [i.get_attribute("aria-label")
                         for i in all_hrefs_in_react]
                else:
                    l = []
                likes = Scraping_utilities._Scraping_utilities__find_reaction_by_text(
                    l, "Like")
                loves = Scraping_utilities._Scraping_utilities__find_reaction_by_text(
                    l, "Love")

                wow = Scraping_utilities._Scraping_utilities__find_reaction_by_text(
                    l, "Wow")

                cares = Scraping_utilities._Scraping_utilities__find_reaction_by_text(
                    l, "Care")
                sad = Scraping_utilities._Scraping_utilities__find_reaction_by_text(
                    l, "Sad")
                angry = Scraping_utilities._Scraping_utilities__find_reaction_by_text(
                    l, "Angry")
                haha = Scraping_utilities._Scraping_utilities__find_reaction_by_text(
                    l, "Haha")

                likes = Scraping_utilities._Scraping_utilities__value_to_float(
                    likes)
                loves = Scraping_utilities._Scraping_utilities__value_to_float(
                    loves)
                wow = Scraping_utilities._Scraping_utilities__value_to_float(
                    wow)
                cares = Scraping_utilities._Scraping_utilities__value_to_float(
                    cares)
                sad = Scraping_utilities._Scraping_utilities__value_to_float(
                    sad)
                angry = Scraping_utilities._Scraping_utilities__value_to_float(
                    angry)
                haha = Scraping_utilities._Scraping_utilities__value_to_float(
                    haha)

                reactions = {"likes": int(likes), "loves": int(loves), "wow": int(wow), "cares": int(cares), "sad": int(sad),
                             "angry":
                             int(angry), "haha": int(haha)}

                total_reaction_count = Scraping_utilities._Scraping_utilities__count_reaction(
                    reactions)

                comments = Finder._Finder__find_comments(post, self.__layout)
                comments = int(
                    Scraping_utilities._Scraping_utilities__value_to_float(comments))
                post_content = Finder._Finder__find_content(
                    post, self.__driver, self.__layout)
                posted_time = Finder._Finder__find_posted_time(
                    post, self.__layout, link_element)

                video = Finder._Finder__find_video_url(post)

                image = Finder._Finder__find_image_url(post, self.__layout)

                self.__data_dict[status] = {
                    "name": name,
                    "shares": shares,
                    "reactions": reactions,
                    "reaction_count": total_reaction_count,
                    "comments": comments,
                    "content": post_content,
                    "posted_on": posted_time,
                    "video": video,
                    "image": image,
                    "post_url": post_url

                }
            except Exception as ex:
                logger.exception(
                    "Error at find_elements method : {}".format(ex))