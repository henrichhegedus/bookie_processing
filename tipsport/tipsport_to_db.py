from tipsport import Tipsport
import time
import yaml
from util.database import Database

import sys
import os
sys.path.append(os.getenv("BOOKIE_PROCESSING"))

stream = open("tipsport/tipsport_sports.yaml", 'r')
tipsport_sports = yaml.load(stream,Loader=yaml.FullLoader)

stream = open("util/db_config.yaml", 'r')
db_config = yaml.load(stream,Loader=yaml.FullLoader)

for sport in tipsport_sports.keys():
    url = tipsport_sports[sport]
    scraper = Tipsport(url)
    time.sleep(20)
    df = scraper.read_values(sport)
    print(df)
    df.to_csv(f"tipsport_{sport}.csv")

    database = Database(db_config)
    database.insert_scrape_to_db("tipsport", df)

    scraper.close_browser()
