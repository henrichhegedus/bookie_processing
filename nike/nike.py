import os, sys
sys.path.append(os.getenv("BOOKIE_PROCESSING"))
from util.scraper import Scraper
from util.translate_name import get_clean_name
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd

class Nike(Scraper):
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

    def sort_order(self, matches, odds):
        """
            Make sure matches and odds are in alphabeticla order
            :param matches:
            :param odds:
            :return:
            """
        if None in matches:
            players = f'{matches[0]} v {matches[1]}'
            return players, odds

        else:
            matches_sorted = sorted(matches)
            if matches_sorted != matches:
                odds = odds[::-1]

            # format matches into one string
            players = f'{matches_sorted[0]} v {matches_sorted[1]}'
            return players, odds

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
                #print(row.find("div", class_ = "bet-table-left ellipsis").attrs["data-meta"])
                #players = eval(row.find("div", class_ = "bet-table-left ellipsis").attrs["data-meta"])["participants"]
                match_details = row.attrs
                #players = eval(match_details["participants"])
                _, bet_id, competition, players, date_time, _ = match_details["title"].split("|")
                players = [p.strip() for p in players.split("vs")]

                odds_soup = row.find_all("span", class_="bet-center")
                odds = [float(o.text.replace(",", ".")) for o in odds_soup]

                if len(odds) == 0:
                    continue

                elif len(odds) == 2:
                    odds_new = odds

                elif len(odds) == 6:
                    odds_new = [odds[0], odds[1], odds[2]]

                datetime_object = datetime.strptime(date_time.strip(),'%d.%m.%Y %H:%M')
                print(len(odds))
                players = self.format_player_names(players, sport)

                players, odds = self.sort_order(players, odds_new)
                matches.append(players)

                odds_all.append(odds)
                competitions.append(competition.split("-")[1])
                sports.append(sport)
                dates.append(datetime_object.strftime('%Y-%m-%d'))
                times.append(datetime_object.strftime('%H:%M:%S'))
                bet_ids.append(int(bet_id.strip()[3:]))




        print(len(competitions))
        print(len(matches))
        print(len(dates))
        print(len(odds_all))
        df = pd.DataFrame({"sport":sports, "competition": competitions, "match": matches, "date": dates, "time": times, "odds": odds_all,"bet_ids":bet_ids})


        return df