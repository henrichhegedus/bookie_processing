from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
from abc import ABC,abstractmethod

class Scraper(ABC):
    def __init__(self, url):
        self.url = url
        
        options = Options()
        options.headless = True
        options.incognito = True
        browser = Firefox(options=options)
        browser.get(self.url)

    @abstractmethod
    def aktualizuj(self):
        pass

    @abstractmethod
    def refresh(self):
        pass

    @abstractmethod
    def read_values(self):
        pass

def get_data(URL):
    options = Options()
    options.headless = False
    options.incognito = True
    options.add_argument("--window-size=1920,1200")

    browser = Firefox(options=options)
    browser.get(URL)

    time.sleep(3)

    browser.find_element_by_xpath('//*[@title="Aktualizovať"]').click()
    time.sleep(3)
    soup = bs(browser.page_source, features="lxml")

    browser.close()

    rows = soup.find_all("div",
                         class_="grid-table-row selectable event-row sport-universal align-items-start text-center row")

    dates = list()
    matches = list()
    odds_all = list()
    for r in rows:
        match_label = r.find("div", class_="match-label").text.strip()
        time_date = r.find("div", class_="date-col").text.strip()
        odds_soup = r.find_all("div", class_="rate")
        odds = [float(o.text.replace(",", ".")) for o in odds_soup]

        dates.append(time_date)
        matches.append(match_label)
        odds_all.append(odds)


    df = pd.DataFrame({"match": matches, "time": dates, "odds": odds_all})
    df.to_csv("2liga_tipos.csv", index=False)
    return df

get_data("https://tipkurz.etipos.sk/#/zapasy/14888c15120c15121?categoryId=14888c15120c15121")