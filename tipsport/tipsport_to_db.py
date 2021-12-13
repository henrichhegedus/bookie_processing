from tipsport import Tipsport
import time
import yaml
from Scraping.util.Database import Database

import sys
import os
sys.path.append(os.path.abspath("/home/henrich/arbitrage"))

stream = open("Scraping/tipsport/tipsport_sports.yaml", 'r')
tipsport_sports = yaml.load(stream,Loader=yaml.FullLoader)

stream = open("Scraping/util/db_config.yaml", 'r')
db_config = yaml.load(stream,Loader=yaml.FullLoader)

for sport in tipsport_sports.keys():
    if sport != "tenis":
        url = tipsport_sports[sport]
        scraper = Tipsport(url)
        time.sleep(30)
        df = scraper.read_values(sport)
        df.to_csv(f"nike_{sport}.csv")

        database = Database(db_config)
        database.insert_scrape_to_db("tipsport", df)
