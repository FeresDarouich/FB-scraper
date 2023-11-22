from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from random import randint
from selenium.webdriver.common.keys import Keys
import logging
import sys
import time

logger = logging.getLogger(__name__)
format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(format)
logger.addHandler(ch)

class Utilities:
    @staticmethod
    def __close_driver(driver):
        try:
            driver.close()
            driver.quit()
        except Exception as ex:
            logger.exception("Error at close_driver method: {}".format(ex))
    @staticmethod
    def __close_error_popup(driver):
        '''expects driver's instance as a argument and checks if error shows up
        like "We could not process your request. Please try again later" ,
        than click on close button to skip that popup.'''
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a.layerCancel')))  
            button = driver.find_element(By.CSS_SELECTOR, "a.layerCancel")
            button.click()  
        except WebDriverException:
            pass
        except NoSuchElementException:
            pass  

        except Exception as ex:
            # if any other error occured 
            logger.exception(
                "Error at close_error_popup method : {}".format(ex))
            
    @staticmethod
    def __scroll_down_half(driver):
        try:
            driver.execute_scripts("window.scrollTo(0,document.body.scrollHeight / 2);")
        except Exception as ex:
            Utilities.__close_driver(driver)
            logger.exception("Error at scroll_down_half method : {}".format(ex))

    @staticmethod
    def __close_modern_layout_signup_modal(driver):
        try:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            close_button = driver.find_element(
                By.CSS_SELECTOR, '[aria-label="Close"]')
            close_button.click()
        except NoSuchElementException:
            pass
        except Exception as ex:
            logger.exception(
                "Error at close_modern_layout_signup_modal: {}".format(ex))
            
    @staticmethod
    def __scroll_down(driver,layout):
        try:
            if layout == "old":
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
            elif layout == "new":
                body = driver.find_element(By.CSS_SELECTOR, "body")
                for _ in range(randint(1, 3)):
                    body.send_keys(Keys.PAGE_UP)
                time.sleep(randint(5, 6))
                for _ in range(randint(5, 8)):
                    body.send_keys(Keys.PAGE_DOWN)
                
        except Exception as ex:
            Utilities.__close_driver(driver)
            logger.exception("Error at scroll_down method : {}".format(ex))


    @staticmethod
    def __close_popup(driver):
        try:
            WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID,'expanding_cta_close_button')))
            popup_close_button = driver.find_element(By.ID,'expanding_cta_close_button')
            popup_close_button.click()
        except WebDriverException:
            pass
        except NoSuchElementException:
            pass
        except Exception as ex:
            logger.exception("error at close_popup method: {}".format(ex))


    @staticmethod
    def __wait_for_element_to_appear(driver,layout):
        try:
            if layout == "old":
                body = driver.find_element(By.CSS_SELECTOR, "body")
                for _ in range(randint(3,5)):
                    body.send_keys(Keys.PAGE_DOWN)
                WebDriverWait(driver,30).until(EC.presence_of_element_located((By.CCS_SELECTOR,'.userContentWrapper')))
            elif layout == "new":
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-posinset]")))

        except WebDriverException:
            logger.critical("No posts were found!")
            Utilities.__close_driver(driver)
            sys.exit(1)
        except Exception as ex:
            logger.exception(
                "Error at wait_for_element_to_appear method : {}".format(ex))
            Utilities.__close_driver(driver)

    @staticmethod
    def __click_see_more(driver,content,selector = None):
        try:
            if not selector:
                # find element and click 'see more' button
                element = content.find_element(
                    By.CSS_SELECTOR, 'span.see_more_link_inner')
            else:
                element = content.find_element(By.CSS_SELECTOR,
                                               selector)
            driver.execute_script("arguments[0].click();", element)

        except NoSuchElementException:
            # if it doesn't exists than no need to raise any error
            pass
        except AttributeError:
            pass
        except IndexError:
            pass
        except Exception as ex:
            logger.exception("Error at click_see_more method : {}".format(ex))

    @staticmethod 
    def __close_cookie_consent_modern_layout(driver):
        try:
          allow_span = driver.find_element(
             By.XPATH, '//div[contains(@aria-label, "Allow")]/../following-sibling::div')
          allow_span.click()
        except Exception as ex:
            logger.info('The Cookie Consent Prompt was not found!: ', ex)