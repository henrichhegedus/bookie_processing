# append path to sys.path so that it finds other files
import sys
import os
sys.path.append(os.getenv("BOOKIE_PROCESSING"))

from util.translate_name import get_clean_name
from datetime import datetime
from util.scraper import Scraper
from bs4 import BeautifulSoup as bs
import pandas as pd
import time

class Tipsport(Scraper):
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


    def format_player_names(self, name, sport):
        name = name.replace("'","$")
        try:
            fst, snd = name.split(" - ")

            if "/" not in fst:
                fst = self.abreviate_name_single(fst, sport)
                snd = self.abreviate_name_single(snd, sport)

            return [fst, snd]

        except:
            return name

    def get_odds(self, odds_soup):
        odds_list = list()
        for odd in odds_soup:
            if odd.text == "":
                odds_list.append(0)
            else:
                odds_list.append(float(odd.text.replace(",", ".")))

        print(odds_list)
        if len(odds_list) == 5:
            new_odds_list = [odds_list[0], odds_list[2], odds_list[4]]
            return new_odds_list

        else:
            return odds_list

    def sort_order(self, matches, odds):
        """
        Make sure matches and odds are in alphabeticla order
        :param matches:
        :param odds:
        :return:
        """
        matches_sorted = sorted(matches)

        if matches_sorted != matches:
            odds = odds[::-1]

        players = f'{matches_sorted[0]} v {matches_sorted[1]}'
        return players, odds


    def read_values(self, sport):
        self.translations_path = f"{os.getenv('BOOKIE_PROCESSING')}/tipsport/translations/{sport}.pkl"
        self.load_translation_table()

        soup = bs(self.browser.page_source, features="lxml")

        boxes = soup.find_all("div",
                              class_="o-superSportRow__body")

        times = list()
        dates = list()
        matches = list()
        odds_all = list()
        competitions = list()
        bet_ids = list()
        competition = None
        sports = list()
        for box in boxes:
            rows = box.findAll(True, {'class':['o-competitionRow', 'o-matchRow']})

            for row in rows:
                if row.attrs['class'][0] == "o-competitionRow":
                    competition =  row.find("div", class_ = "colCompetition").text.strip().split("-")[0]

                else:
                    match = self.format_player_names(row.find("span", class_="o-matchRow__matchName").text.strip(), sport)
                    _, _, bet_id, _ = row.attrs["data-atid"].split("||")

                    date_time = row.find("div", class_="o-matchRow__dateClosed").text.strip()

                    odds_soup = row.find_all("div", class_="btnRate")
                    odds = self.get_odds(odds_soup)

                    date_time = date_time[:-5]+" "+date_time[-5:]

                    datetime_object = datetime.strptime(date_time,'%d.%m.%Y %H:%M')

                    if isinstance(match, list): # sometimes is not list and then we dont want to deal with it
                        if match[0] != None and match[1] != None:
                            match, odds = self.sort_order(match, odds)
                            time = datetime_object.strftime('%H:%M:%S')
                            date = datetime_object.strftime('%Y-%m-%d')

                            entry = {'time': time, 'match':match,"sport":sport,"competition":competition,'odds':odds}
                            times.append(time)
                            dates.append(date)
                            bet_ids.append(bet_id)
                            matches.append(match)
                            sports.append(sport)
                            competitions.append(competition)
                            odds_all.append(odds)

        df = pd.DataFrame({"sport":sports, "competition": competitions, "match": matches, "date":dates, "time": times, "odds": odds_all,"bet_ids":bet_ids})


        return df