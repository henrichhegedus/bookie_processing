from nike import Nike
import yaml
from Scraping.scraper_misc.database import Database

stream = open("nike_sports.yaml", 'r')
nike_sports = yaml.load(stream,Loader=yaml.FullLoader)

stream = open("../scraper_misc/db_config.yaml", 'r')
db_config = yaml.load(stream,Loader=yaml.FullLoader)

for sport in nike_sports.keys():
    if sport != "tenis":
        url = nike_sports[sport]
        scraper = Nike(url)
        scraper.load_all()
        df = scraper.read_values(sport)
        df.to_csv(f"nike_{sport}.csv")

        database = Database(db_config)
        database.insert_scrape_to_db("nike", df)
