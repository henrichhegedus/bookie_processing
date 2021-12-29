import os, sys
sys.path.append(os.getenv("BOOKIE_PROCESSING"))

from ladbrokes import Ladbrokes
import yaml

stream = open(os.getenv("BOOKIE_PROCESSING")+"/ladbrokes/ladbrokes_sports.yaml", 'r')
sports = yaml.load(stream,Loader=yaml.FullLoader)

for sport in sports.keys():
    url = sports[sport]
    scraper = Ladbrokes(url)
    scraper.load_all()
    df = scraper.read_values(sport)
    scraper.db.close_connection()
    df.to_csv(os.getenv("BOOKIE_PROCESSING")+f"/ladbrokes/data_log/ladbrokes_{sport}.csv")
