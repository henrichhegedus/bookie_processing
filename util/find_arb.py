import difflib
import pandas as pd
import numpy as np
import unidecode
import yaml
from database import Database

stream = open("db_config.yaml", 'r')
db_config = yaml.load(stream,Loader=yaml.FullLoader)

database = Database(db_config)
scrape_data = database.get_scrape()

def prune(name):
    names = [subname for subname in name.split(" ") if len(subname) > 3]
    for i in range(len(names)):
        names[i] = unidecode.unidecode(names[i]).lower()

    return names

# find all bookies
bookies = set(scrape_data["bookie"])
bookie_dicts = dict()
sports = set()
for bookie in bookies:
    bool_mask = scrape_data["bookie"] == bookie
    masked_df = scrape_data.where(bool_mask, inplace = False)
    masked_df.dropna(subset = ["date"], inplace=True)

    masked_df['team1'].apply(prune)
    masked_df['team2'].apply(prune)

    bookie_dicts[bookie] = masked_df
    sports = sports.union(set(sorted(masked_df["sport"].unique())))






def is_any_in_any(l1, l2):
    for e1 in l1:
        for e2 in l2:
            if e1 in e2 or e2 in e1:
                return True
    return False

def market_margin(odds):
    sum = 0
    for odd in odds:
        if odd != np.nan:
            sum += 1/odd

    return sum

def margins(all_ods):
    maxima_ind = np.nanargmax(all_ods, axis = 0)


    max_val = []
    for i in range(len(maxima_ind)):
        max_val.append(all_ods[:,i][maxima_ind[i]])

    margin = market_margin(max_val)

    if margin < 1:
        print(all_ods)
        print(maxima_ind)
        print(max_val)
    return margin, maxima_ind

def look_for_arb(pairs, sport):
    arbs = {"sport":[], "competition":[], "team1":[], "team2":[], "bookie1":[], "bookiex":[], "bookie2":[], "odds1":[], "oddsx":[], "odds2":[], "margin":[]}
    for pair in pairs:
        all_ods = list()
        #print(pair)
        for bookie in pair.keys():
            if pair[bookie][1]:
                # is swapped
                odds1 = sport_sorted_bookies[sport][bookie].loc[pair[bookie][0], "odds2"]
                oddsx = sport_sorted_bookies[sport][bookie].loc[pair[bookie][0], "oddsx"]
                odds2 = sport_sorted_bookies[sport][bookie].loc[pair[bookie][0], "odds1"]
            else:
                odds1 = sport_sorted_bookies[sport][bookie].loc[pair[bookie][0], "odds1"]
                oddsx = sport_sorted_bookies[sport][bookie].loc[pair[bookie][0], "oddsx"]
                odds2 = sport_sorted_bookies[sport][bookie].loc[pair[bookie][0], "odds2"]


            if oddsx == None:
                all_ods.append([odds1, odds2])
            else:
                all_ods.append([odds1, oddsx, odds2])

        margin, bookie_ind = margins(np.array(all_ods))
        if margin < 1:
            print(pair)
            bookie0_row = pair[bookies[bookie_ind[0]]][0]
            bookie2_row = pair[bookies[bookie_ind[2]]][0]
            print(sport_sorted_bookies[sport][bookies[bookie_ind[0]]].loc[bookie0_row, "team1"], sport_sorted_bookies[sport][bookies[bookie_ind[0]]].loc[bookie0_row, "team2"])
            print(sport_sorted_bookies[sport][bookies[bookie_ind[2]]].loc[bookie2_row, "team1"], sport_sorted_bookies[sport][bookies[bookie_ind[2]]].loc[bookie2_row, "team2"])

        bookies = list(pair.keys())
        arbs["bookie1"].append(bookies[bookie_ind[0]])
        bookie0_row = pair[bookies[bookie_ind[0]]][0]
        arbs["odds1"].append(sport_sorted_bookies[sport][bookies[bookie_ind[0]]].loc[bookie0_row, "odds1"])

        if len(bookie_ind) == 2:
            arbs["bookie2"].append(bookies[bookie_ind[1]])
            arbs["bookiex"].append("Null")
            bookie2_row = pair[bookies[bookie_ind[1]]][0]
            arbs["odds2"].append(sport_sorted_bookies[sport][bookies[bookie_ind[1]]].loc[bookie2_row, "odds2"])
            arbs["oddsx"].append("Null")
        else:
            arbs["bookiex"].append(bookies[bookie_ind[1]])
            arbs["bookie2"].append(bookies[bookie_ind[2]])
            bookiex_row = pair[bookies[bookie_ind[1]]][0]
            bookie2_row = pair[bookies[bookie_ind[2]]][0]
            arbs["oddsx"].append(sport_sorted_bookies[sport][bookies[bookie_ind[1]]].loc[bookiex_row, "oddsx"])
            arbs["odds2"].append(sport_sorted_bookies[sport][bookies[bookie_ind[2]]].loc[bookie2_row, "odds2"])
        arbs["margin"].append(margin)
        arbs["sport"].append(sport)

        arbs["competition"].append(sport_sorted_bookies[sport][bookies[bookie_ind[0]]].loc[bookie0_row, "competition"])
        arbs["team1"].append(sport_sorted_bookies[sport][bookies[bookie_ind[0]]].loc[bookie0_row, "team1"])
        arbs["team2"].append(sport_sorted_bookies[sport][bookies[bookie_ind[0]]].loc[bookie0_row, "team2"])

    return pd.DataFrame(arbs)

def recursive_pair_finding(bookies, pairs = []):
    bookie_names = list(bookies.keys())
    if len(bookie_names) == 1:
        return pairs
    main_bookie = bookies[bookie_names[0]]
    paired_rows = dict()

    #iterate through rows of main bookie
    for i_main_bookie, row_main_bookie in main_bookie.iterrows():
        competition_main_bookie = row_main_bookie["competition"]
        club1_main, club2_main = row_main_bookie["team1"], row_main_bookie["team2"]
        date_main_bookie = row_main_bookie["date"]
        time_main_bookie = row_main_bookie["time"]
        pair = {bookie_names[0]:(i_main_bookie, False, 1)}

        # go through every side bookie looking for pairs
        for bookie in bookie_names[1:]:
            side_bookie = bookies[bookie]
            paired_rows[bookie] = list()

            for i_side_bookie, row_side_bookie in side_bookie.iterrows():
                competition_side_bookie = row_side_bookie["competition"]
                club1_side_bookie, club2_side_bookie = row_side_bookie["team1"], row_side_bookie["team2"]
                date_side_bookie = row_side_bookie["date"]
                time_side_bookie = row_side_bookie["time"]

                if date_side_bookie == date_main_bookie and time_side_bookie == time_main_bookie:
                    ratio = difflib.SequenceMatcher(None, competition_main_bookie, competition_side_bookie).ratio()
                    if ratio > 0.5:
                        ratio1 = difflib.SequenceMatcher(None, club1_side_bookie, club1_main).ratio()
                        ratio2 = difflib.SequenceMatcher(None, club2_side_bookie, club2_main).ratio()
                        if ratio1 > 0.61 and ratio2 > 0.61:
                            pair[bookie] = (i_side_bookie, False, ratio)
                            paired_rows[bookie].append(i_side_bookie)
                            break

                        ratio1 = difflib.SequenceMatcher(None, club1_side_bookie, club2_main).ratio()
                        ratio2 = difflib.SequenceMatcher(None, club2_side_bookie, club1_main).ratio()
                        if ratio1 > 0.61 and ratio2 > 0.61:
                            pair[bookie] = (i_side_bookie, True, ratio)
                            paired_rows[bookie].append(i_side_bookie)
                            break

        if len(pair.keys())>1:
            pairs.append(pair)


    # reduce data
    bookies.pop(bookie_names[0])

    return recursive_pair_finding(bookies, pairs)

sport_sorted_bookies = dict()

database.delete_arbs()

for sport in sports:
    if sport == "futbal":
        pairs = list()
        sport_sorted_bookies[sport] = dict()

        for bookie in bookie_dicts.keys():
            scrape_mask = scrape_data["sport"] == sport
            bookie_mask = scrape_data["bookie"] == bookie
            masked_df = scrape_data.where(scrape_mask & bookie_mask, inplace = False)
            masked_df = masked_df.dropna(subset = ["date"])
            sport_sorted_bookies[sport][bookie] = masked_df.reset_index()
        #print(sport_sorted_bookies.keys())
        pairs = recursive_pair_finding(sport_sorted_bookies[sport].copy())
        arbs = look_for_arb(pairs, sport)
        database.insert_arbs_to_db(arbs)


database.close_connection()





