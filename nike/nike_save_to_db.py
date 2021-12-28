from nike import Nike
import yaml
import os, sys
sys.path.append(os.getenv("BOOKIE_PROCESSING"))

stream = open(os.getenv("BOOKIE_PROCESSING")+"/nike/nike_sports.yaml", 'r')
nike_sports = yaml.load(stream,Loader=yaml.FullLoader)

for sport in nike_sports.keys():
    url = nike_sports[sport]
    scraper = Nike(url)
    df = scraper.read_values(sport)
    df.to_csv(os.getenv("BOOKIE_PROCESSING")+f"/nike/data_log/nike_{sport}.csv")


