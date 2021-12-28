from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import pickle
from util.database import Database
from selenium.common.exceptions import NoSuchElementException
from abc import ABC,abstractmethod

class Scraper(ABC):
    def __init__(self, url, bookie):
        self.url = url
        self.db = Database(bookie)

        options = Options()
        options.headless = True
        options.incognito = True
        options.binary_location = "/usr/lib/firefox/firefox"
        self.browser = Firefox(options=options)
        self.browser.get(self.url)

    def check_exists_by_xpath(self, xpath):
        try:
            self.browser.find_element_by_xpath(xpath)
            return True

        except NoSuchElementException:
            return False

    def load_translation_table(self):
        try:
            file = open(self.translations_path, 'rb')
            self.translations = pickle.load(file)
            file.close()
        except:
            self.translations = {}      # translation table doesn't exist
            self.write_translation_table()

    def write_translation_table(self):
        with open(self.translations_path, 'wb') as f:
            pickle.dump(self.translations, f)

    def append_translation_table(self):
        with open(self.translations_path, 'wb') as f:
            pickle.dump(self.translations, f)

        with open(self.translations_path, 'rb') as f:
            self.translations = pickle.load(f)

    def close_browser(self):
        self.browser.close()


    @abstractmethod
    def aktualizuj(self):
        pass

    @abstractmethod
    def refresh(self):
        pass

    @abstractmethod
    def read_values(self):
        pass