from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time
from selenium.common.exceptions import NoSuchElementException

from abc import ABC,abstractmethod

class Scraper(ABC):
    def __init__(self, url):
        self.url = url

        options = Options()
        options.headless = False
        options.incognito = True
        self.browser = Firefox(options=options)
        self.browser.get(self.url)

    def check_exists_by_xpath(self, xpath):
        try:
            self.browser.find_element_by_xpath(xpath)
            return True

        except NoSuchElementException:
            return False



    @abstractmethod
    def aktualizuj(self):
        pass

    @abstractmethod
    def refresh(self):
        pass

    @abstractmethod
    def close_browser(self):
        pass

    @abstractmethod
    def read_values(self):
        pass