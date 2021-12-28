from tipsport import Tipsport
import time
import yaml
import sys
import os
sys.path.append(os.getenv("BOOKIE_PROCESSING"))

stream = open(os.getenv("BOOKIE_PROCESSING")+"/tipsport/tipsport_sports.yaml", 'r')
tipsport_sports = yaml.load(stream,Loader=yaml.FullLoader)

for sport in tipsport_sports.keys():
    url = tipsport_sports[sport]
    scraper = Tipsport(url)
    time.sleep(20)
    df = scraper.read_values(sport)
    df.to_csv(os.getenv("BOOKIE_PROCESSING")+f"/tipsport/data_log/tipsport_{sport}.csv")
