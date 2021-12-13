from Scraping.scraper_misc.scraper import Scraper
from bs4 import BeautifulSoup as bs
import pandas as pd


class Tipos(Scraper):
    def aktualizuj(self):
        self.browser.find_element_by_xpath('//*[@title="Aktualizovať"]').click()

    def refresh(self):
        self.browser.get(self.url)

    def close_browser(self):
        self.browser.close()

    def read_values(self):
        soup = bs(self.browser.page_source, features="lxml")

        rows = soup.find_all("div",
                             class_="grid-table-row selectable event-row sport-universal align-items-start text-center row")

        dates = list()
        matches = list()
        odds_all = list()
        for r in rows:
            try:
                match_label = r.find("div", class_="match-label").text.strip()
                print(match_label)
                odds_soup = r.find_all("span", class_="bet-center")
                print(odds_soup)
                odds = [float(o.text.replace(",", ".")) for o in odds_soup]

                matches.append(match_label)
                odds_all.append(odds)
            except:
                pass


        df = pd.DataFrame({"match": matches, "time": dates, "odds": odds_all})

        return df