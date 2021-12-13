from Scraping.scraper_misc.scraper import Scraper
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd

class Doxbet(Scraper):
    def load_all(self):
        while self.check_exists_by_xpath("//button[contains(text(),'Zobraziť viac')]"):
            try:
                element = self.browser.find_element_by_xpath("//button[contains(text(),'Zobraziť viac')]")
                self.browser.execute_script("arguments[0].scrollIntoView();", element)
            except:
                pass


    def aktualizuj(self):
        self.browser.find_element_by_xpath('//*[@title="Aktualizovať"]').click()

    def refresh(self):
        self.browser.get(self.url)

    def close_browser(self):
        self.browser.close()

    def read_values(self, sport):
        soup = bs(self.browser.page_source, features="lxml")

        boxes = soup.find_all("div",
                              class_="pl-xs")

        dates = list()
        matches = list()
        odds_all = list()
        competitions = list()
        bet_ids = list()
        times = list()
        sports = list()

        for box in boxes:
            rows = box.find_all("div", class_ = "flex bet-view-prematch-row")

            for row in rows:
                try:
                    #print(row.find("div", class_ = "bet-table-left ellipsis").attrs["data-meta"])
                    #players = eval(row.find("div", class_ = "bet-table-left ellipsis").attrs["data-meta"])["participants"]
                    match_details = row.attrs
                    #players = eval(match_details["participants"])
                    _, bet_id, competition, players, date_time, _ = match_details["title"].split("|")
                    players = [p.strip() for p in players.split("vs")]

                    odds_soup = row.find_all("span", class_="bet-center")
                    odds = [float(o.text.replace(",", ".")) for o in odds_soup]

                    datetime_object = datetime.strptime(date_time.strip(),'%d.%m.%Y %H:%M')

                    dates.append(datetime_object.strftime('%Y-%m-%d'))
                    times.append(datetime_object.strftime('%H:%M:%S'))
                    sports.append(sport)
                    matches.append(players)
                    odds_all.append(odds)
                    competitions.append(competition.split("-")[1])
                    bet_ids.append(int(bet_id.strip()[3:]))
                except Exception:
                    pass




        print(len(competitions))
        print(len(matches))
        print(len(dates))
        print(len(odds_all))
        df = pd.DataFrame({"sport":sports, "competition": competitions, "match": matches, "date": dates, "time": times, "odds": odds_all,"bet_ids":bet_ids})


        return df