import os, sys
sys.path.append(os.getenv("BOOKIE_PROCESSING"))
from util.scraper import Scraper
from util.translate_name import get_clean_name
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import time
from selenium.webdriver.common.by import By

class Ladbrokes(Scraper):
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

        for box in boxes[:15]:
            competition = box.find("div", {'class': 'accordion-left-side'}).text
            print(competition)
            rows = box.find_all("div", {'class':'sport-card'})

            for row in rows:
                date_time = row.find("div",{"class":"sport-card-left"}).text
                datetime_object = datetime.strptime(date_time.strip(),'%H:%M %d %b')

                players_soup = row.find('div',{'class':'sport-card-names odds-names-list'})

                fst = players_soup.find('a', {'data-crlat':'EventFirstName'}).text
                snd = players_soup.find('a', {'data-crlat':'EventSecondName'}).text
                players = [fst, snd]

                odds_soup = row.find_all("span", class_="odds-price")
                odds = self.get_odds(odds_soup)

                if len(odds) == 0:
                    continue

                elif len(odds) == 2 or len(odds) == 3:
                    odds_new = odds


                print(len(odds))
                players = self.format_player_names(players, sport)

                players, odds = self.sort_order(players, odds_new)
                matches.append(players)

                odds_all.append(odds)
                competitions.append(competition.split("-")[1])
                sports.append(sport)
                dates.append(datetime_object.strftime('%Y-%m-%d'))
                times.append(datetime_object.strftime('%H:%M:%S'))
                bet_ids.append(int(row.get('data-eventid')))




        print(len(competitions))
        print(len(matches))
        print(len(dates))
        print(len(odds_all))
        df = pd.DataFrame({"sport":sports, "competition": competitions, "match": matches, "date": dates, "time": times, "odds": odds_all,"bet_ids":bet_ids})


        return df