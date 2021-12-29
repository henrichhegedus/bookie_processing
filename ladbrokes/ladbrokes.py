import os, sys
sys.path.append(os.getenv("BOOKIE_PROCESSING"))
from util.scraper import Scraper
from util.translate_name import get_clean_name
from util.util import *
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import time

class Ladbrokes(Scraper):
    def __init__(self,url):
        super().__init__(url, 'Ladbrokes')

    def load_all(self):
        i = 1
        time.sleep(5)
        while self.check_exists_by_xpath('//*[@id="content"]/sport-main-component/div[2]/div/sport-matches-page/sport-matches-tab/accordion['+ str(i) +']'):
            try:
                element = self.browser.find_element_by_xpath('//*[@id="content"]/sport-main-component/div[2]/div/sport-matches-page/sport-matches-tab/accordion['+ str(i) +']')
                if element.get_attribute("class") != 'is-expanded':
                    scrollElementIntoMiddle = """var viewPortHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
                                                var elementTop = arguments[0].getBoundingClientRect().top;
                                                window.scrollBy(0, elementTop-(viewPortHeight/2));"""

                    self.browser.execute_script(scrollElementIntoMiddle,  element)
                    element.click()
            except:
                pass
            i += 1

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
            fst = self.abreviate_name_single(match[0], sport)
            snd = self.abreviate_name_single(match[1], sport)

            return [fst, snd]

        except:
            return match

    def get_odds(self, odds_soup):
        odds = []
        try:
            for o in odds_soup:
                numerator, denominator = o.text.split('/')
                odds.append(1 + round(int(numerator)/int(denominator),2))
            return odds

        except:
            return []

    def read_values(self, sport):
        self.translations_path = f"{os.getenv('BOOKIE_PROCESSING')}/ladbrokes/translations/{sport}.pkl"
        self.load_translation_table()

        soup = bs(self.browser.page_source, features="lxml")

        boxes = soup.find_all("accordion", {'class':'is-expanded'})

        dates = list()
        matches = list()
        odds_all = list()
        competitions = list()
        bet_ids = list()
        times = list()
        sports = list()

        for box in boxes:
            try:
                competition = box.find("div", {'class': 'accordion-left-side'}).text
            except:
                competition = "unknown"
            rows = box.find_all("div", {'class':'sport-card'})

            for row in rows:
                date_time = row.find("div",{"class":"sport-card-left"}).text
                datetime_object = datetime.strptime(date_time.strip(),'%H:%M %d %b')
                datetime_now = datetime.now()
                if datetime_object.month < datetime_now.month:
                    datetime_object = datetime_object.replace(year = datetime_now.year + 1)
                else:
                    datetime_object = datetime_object.replace(year = datetime_now.year)

                # deal with players
                players_soup = row.find('div',{'class':'sport-card-names odds-names-list'})

                fst = players_soup.find('a', {'data-crlat':'EventFirstName'}).text
                snd = players_soup.find('a', {'data-crlat':'EventSecondName'}).text
                players = [fst, snd]

                # deal with odds
                odds_soup = row.find_all("span", class_="odds-price")
                odds = self.get_odds(odds_soup)
                if len(odds) == 0:
                    continue

                elif len(odds) == 2 or len(odds) == 3:
                    odds_new = odds

                match = self.format_player_names(players, sport)
                match, odds = sort_order(match, odds_new)

                # compute rest
                date = datetime_object.strftime('%Y-%m-%d')
                time = datetime_object.strftime('%H:%M:%S')
                bet_id = int(row.get('data-eventid'))

                matches.append(match)
                odds_all.append(odds)
                competitions.append(competition)
                sports.append(sport)
                dates.append(date)
                times.append(time)
                bet_ids.append(bet_id)

                self.db.insert_scrape_single({"sport":sport, "competition": competition, "match": match, "date": date, "time": time, "odds": odds,"bet_ids":bet_id})


        df = pd.DataFrame({"sport":sports, "competition": competitions, "match": matches, "date": dates, "time": times, "odds": odds_all,"bet_ids":bet_ids})

        self.close_browser()
        return df