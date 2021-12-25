from nike import Nike
import yaml
import os, sys
sys.path.append(os.getenv("BOOKIE_PROCESSING"))

from util.database import Database

stream = open("nike/nike_sports.yaml", 'r')
nike_sports = yaml.load(stream,Loader=yaml.FullLoader)

stream = open("util/db_config.yaml", 'r')
db_config = yaml.load(stream,Loader=yaml.FullLoader)

for sport in nike_sports.keys():
    url = nike_sports[sport]
    scraper = Nike(url)
    scraper.load_all()
    df = scraper.read_values(sport)
    df.to_csv(f"nike_{sport}.csv")

    database = Database(db_config)
    database.insert_scrape_to_db("nike", df)
