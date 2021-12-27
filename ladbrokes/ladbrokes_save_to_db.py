from ladbrokes import Ladbrokes
import yaml
import os, sys
sys.path.append(os.getenv("BOOKIE_PROCESSING"))

from util.database import Database

stream = open("ladbrokes/ladbrokes_sports.yaml", 'r')
sports = yaml.load(stream,Loader=yaml.FullLoader)

stream = open("util/db_config.yaml", 'r')
db_config = yaml.load(stream,Loader=yaml.FullLoader)

for sport in sports.keys():
    url = sports[sport]
    scraper = Ladbrokes(url)
    scraper.load_all()
    df = scraper.read_values(sport)
    df.to_csv(f"ladbrokes/data_log/ladbrokes_{sport}.csv")

    scraper.close_browser()

    database = Database(db_config)
    database.insert_scrape_to_db("ladbrokes", df)
