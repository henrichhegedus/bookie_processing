import pandas as pd
import numpy as np
from database import Database

database = Database('arbitrage_finder')
scrape_data = database.get_scrape()

bookie_dicts = dict()
sports = set()

grouped = scrape_data.groupby(['date','team1']).count()
grouped_pairable = grouped[grouped['bookie'] > 1]
index_set = scrape_data.set_index(['date','team1'])

def market_margin(odds):
    sum = 0
    for odd in odds:
        if not np.isnan(odd):
            sum += 1/odd
    return 1/sum

# indexes that have more than one
arbs = {'sport':[], 'bookie1':[], 'bookieX':[], 'bookie2':[], 'odds1':[], 'oddsX':[], 'odds2':[], 'margin':[], 'date':[], 'time':[], 'match':[]}
for i in grouped_pairable.index:
    if 'None' in i[1]:
        pass

    else:
        newdf = index_set.loc[i[0], i[1]]
        odds_arr = newdf[['odds1', 'oddsx', 'odds2']].to_numpy()

        maxima = odds_arr.argmax(axis = 0)
        odds_max = [odds_arr[maxima[0]][0], odds_arr[maxima[1]][1], odds_arr[maxima[2]][2]]

        bookie_arr = newdf['bookie'].to_numpy()
        bookie_max = bookie_arr[maxima]


        arbs['sport'].append(newdf['sport'].to_numpy()[0])
        arbs['match'].append(i[1])
        arbs['date'].append(i[0].strftime('%Y-%m-%d'))
        arbs['time'].append(newdf['time'].to_numpy()[0].strftime('%H:%M:%S'))
        arbs['odds1'].append(odds_max[0])
        arbs['oddsX'].append(odds_max[1])
        arbs['odds2'].append(odds_max[2])
        arbs['margin'].append(market_margin(odds_max))
        arbs['bookie1'].append(bookie_max[0])
        arbs['bookieX'].append(bookie_max[1])
        arbs['bookie2'].append(bookie_max[2])







arbs = pd.DataFrame(arbs)
arbs['oddsX'] = arbs['oddsX'].where(pd.notnull(arbs['oddsX']), None)

database.delete_arbs()
database.insert_arbs_to_db(arbs)
database.close_connection()




