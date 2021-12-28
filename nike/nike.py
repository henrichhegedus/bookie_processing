import os, sys
sys.path.append(os.getenv("BOOKIE_PROCESSING"))
from util.scraper import Scraper
from util.translate_name import get_clean_name
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
from util.util import *

class Nike(Scraper):
    def __init__(self,url):
        super().__init__(url, 'Nike')

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

    def abreviate_name_single(self, name, sport):
        try:
            abv_name = self.translations[name]
        except:
            abv_name, _ = get_clean_name(name, sport)
            self.translations[name] = abv_name      # add to the translations
            self.append_translation_table()
        return abv_name

    def format_player_names(self, match, sport):
        try:
            match[1] = match[1].split('\n')[0]
        except:
            pass

        match0_split = match[0].split("/")
        print(match)
        # if 1 player is on a team
        if len(match0_split) == 1:
            try:
                fst = self.abreviate_name_single(match[0], sport)
                snd = self.abreviate_name_single(match[1], sport)

                return [fst, snd]

            except:
                return match

        # if 2 players are playing on one team
        elif len(match0_split) == 2:
            match1_split = match[1].split('/')
            try:
                fst = f'{self.abreviate_name_single(match0_split[0], sport)}/{self.abreviate_name_single(match0_split[1], sport)}'
                snd = f'{self.abreviate_name_single(match1_split[0], sport)}/{self.abreviate_name_single(match1_split[1], sport)}'
                print([fst, snd])
                return [fst, snd]

            except:
                return match


    def get_odds(self, odds_soup):
        try:
            return [float(o.text.replace(",", ".")) for o in odds_soup]

        except:
            odds = []
            for o in odds_soup:
                try:
                    odds.append(float(o.text.replace(",", ".")))
                except:
                    odds.append(0)
            return odds

    def read_values(self, sport):
        self.translations_path = f"{os.getenv('BOOKIE_PROCESSING')}/nike/translations/{sport}.pkl"
        self.load_translation_table()

        soup = bs(self.browser.page_source, features="lxml")

        boxes = soup.find_all("div", {'data-atid':'n1-league-box'})

        dates = list()
        matches = list()
        odds_all = list()
        competitions = list()
        bet_ids = list()
        times = list()
        sports = list()

        for box in boxes[:15]:
            rows = box.find_all("div", class_ = "flex bet-view-prematch-row")

            for row in rows:
                match_details = row.attrs

                _, bet_id, competition, match, date_time, _ = match_details["title"].split("|")
                match = [p.strip() for p in match.split("vs")]

                # compute odds
                odds_soup = row.find_all("span", class_="bet-center")
                odds = self.get_odds(odds_soup)

                if len(odds) == 0:
                    continue

                elif len(odds) == 2:
                    odds_new = odds

                elif len(odds) == 6:
                    odds_new = [odds[0], odds[1], odds[2]]

                datetime_object = datetime.strptime(date_time.strip(),'%d.%m.%Y %H:%M')

                match = self.format_player_names(match, sport)
                match, odds = sort_order(match, odds_new)

                # compute remaining rows
                competition = competition.split("-")[1]
                date = datetime_object.strftime('%Y-%m-%d')
                time = datetime_object.strftime('%H:%M:%S')
                bet_id = int(bet_id.strip()[3:])

                odds_all.append(odds)
                matches.append(match)
                competitions.append(competition)
                sports.append(sport)
                dates.append(date)
                times.append(time)
                bet_ids.append(bet_id)

                self.db.insert_scrape_single({"sport":sport, "competition": competition, "match": match, "date": date, "time": time, "odds": odds,"bet_ids":bet_id})

        df = pd.DataFrame({"sport":sports, "competition": competitions, "match": matches, "date": dates, "time": times, "odds": odds_all,"bet_ids":bet_ids})
        self.close_browser()
        return df