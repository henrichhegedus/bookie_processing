import pandas as pd
import numpy as np
import psycopg2
import datetime
import yaml
import os


class Database:
    def __init__(self, bookie):
        stream = open(os.getenv("BOOKIE_PROCESSING")+"/util/db_config.yaml", 'r')
        db_config = yaml.load(stream,Loader=yaml.FullLoader)

        self.connection = psycopg2.connect(user=db_config["user"],
                                      password=db_config["password"],
                                      host=db_config["host"],
                                      port=db_config["port"],
                                      database=db_config["database"])
        self.cursor = self.connection.cursor()
        self.bookie = bookie

    def insert_scrape_to_db(self, df):
        for i in range(len(df)):
            one_bet = df.loc[i]
            print(one_bet)
            self.insert_scrape_single(one_bet)

    def insert_scrape_single(self, one_bet):
        try:
            postgres_insert_query = None
            if len(one_bet["odds"]) == 2:
                postgres_insert_query = """ INSERT INTO arbitrage.scrape(bookie, sport, competition, event_date, event_time, odds1, odds2, team1, bet_id)
                                                    VALUES ('{}','{}','{}','{}','{}', {}, {},'{}', {}) ON CONFLICT (bet_id) DO UPDATE SET odds1={}, odds2={};
                                                """
                postgres_insert_query = postgres_insert_query.format(self.bookie,
                                                                     one_bet["sport"],
                                                                     one_bet["competition"],
                                                                     one_bet["date"],
                                                                     one_bet["time"],
                                                                     one_bet["odds"][0],
                                                                     one_bet["odds"][1],
                                                                     one_bet["match"],
                                                                     one_bet["bet_ids"],
                                                                     one_bet["odds"][0],
                                                                     one_bet["odds"][1],
                                                                     one_bet["odds"][0],
                                                                     one_bet["odds"][1]
                                                                     )

            if len(one_bet["odds"]) == 3:
                postgres_insert_query = """ INSERT INTO arbitrage.scrape(bookie, sport, competition, event_date, event_time, odds1, oddsx, odds2, team1, bet_id)
                                                    VALUES ('{}','{}','{}','{}','{}',{}, {}, {},'{}',{}) ON CONFLICT (bet_id) DO UPDATE SET odds1={}, oddsx={}, odds2={};
                                                """
                postgres_insert_query = postgres_insert_query.format(self.bookie,
                                                                     one_bet["sport"],
                                                                     one_bet["competition"],
                                                                     one_bet["date"],
                                                                     one_bet["time"],
                                                                     one_bet["odds"][0],
                                                                     one_bet["odds"][1],
                                                                     one_bet["odds"][2],
                                                                     one_bet["match"],
                                                                     one_bet["bet_ids"],
                                                                     one_bet["odds"][0],
                                                                     one_bet["odds"][1],
                                                                     one_bet["odds"][2],
                                                                     one_bet["odds"][0],
                                                                     one_bet["odds"][1],
                                                                     one_bet["odds"][2]
                                                                     )
            if postgres_insert_query:
                self.cursor.execute(postgres_insert_query)


                self.connection.commit()
            else:
                pass

        except (Exception, psycopg2.Error) as error:
            print("Error in insert operation", error)

    def close_connection(self):
        # closing database connection.
        if self.connection:
            self.cursor.close()
            self.connection.close()

    def delete_arbs(self):
        try:
            postgres_select_query = "DELETE FROM arbitrage.arbs"
            self.cursor.execute(postgres_select_query)

        except (Exception, psycopg2.Error) as error:
            print("Error in delete operation", error)

    def get_scrape(self):
        try:
            postgres_select_query = "select * from arbitrage.scrape"
            self.cursor.execute(postgres_select_query)
            query_result = self.cursor.fetchall()
            rows = np.array(query_result)
            df = pd.DataFrame({"bookie": rows[:,1],"bet_id":rows[:,2], "date": rows[:,3], "time": rows[:,4], "sport": rows[:,5], "competition":rows[:,6],
                               "team1":rows[:,7], "odds1":rows[:,8], "oddsx":rows[:,9],"odds2": rows[:,10]})
            df[['odds1', 'oddsx', 'odds2']] = df[['odds1', 'oddsx', 'odds2']].apply(pd.to_numeric)
            return df

        except (Exception, psycopg2.Error) as error:
            print("Error in select operation", error)


    def insert_arbs_to_db(self, df):
        for i in range(len(df)):
            try:
                one_arb = df.loc[i]
                if one_arb['oddsX']:
                    postgres_insert_query = """ INSERT INTO arbitrage.arbs(sport, match, date, time, odds1, oddsx, odds2, margin, bookie1, bookiex, bookie2)
                                                VALUES ('{}','{}','{}','{}',{},{},{}, {}, '{}', '{}', '{}') ON CONFLICT (match,date) DO UPDATE SET odds1={}, oddsx={}, odds2={}, margin={},bookie1='{}',bookiex='{}',bookie2='{}';
                                            """
                    postgres_insert_query = postgres_insert_query.format(one_arb["sport"],
                                                                         one_arb["match"],
                                                                         one_arb["date"],
                                                                         one_arb["time"],
                                                                         one_arb["odds1"],
                                                                         one_arb["oddsX"],
                                                                         one_arb["odds2"],
                                                                         one_arb["margin"],
                                                                         one_arb["bookie1"],
                                                                         one_arb["bookieX"],
                                                                         one_arb["bookie2"],
                                                                         one_arb["odds1"],
                                                                         one_arb["oddsX"],
                                                                         one_arb["odds2"],
                                                                         one_arb["margin"],
                                                                         one_arb["bookie1"],
                                                                         one_arb["bookieX"],
                                                                         one_arb["bookie2"]
                                                                         )
                else:
                    postgres_insert_query = """ INSERT INTO arbitrage.arbs(sport, match, date, time, odds1, odds2, margin, bookie1, bookiex, bookie2)
                                                VALUES ('{}','{}','{}','{}',{}, {}, {}, '{}', '{}', '{}') ON CONFLICT (match,date) DO UPDATE SET odds1={}, odds2={}, margin={},bookie1='{}',bookie2='{}';
                                            """
                    postgres_insert_query = postgres_insert_query.format(one_arb["sport"],
                                                                         one_arb["match"],
                                                                         one_arb["date"],
                                                                         one_arb["time"],
                                                                         one_arb["odds1"],
                                                                         one_arb["odds2"],
                                                                         one_arb["margin"],
                                                                         one_arb["bookie1"],
                                                                         one_arb["bookieX"],
                                                                         one_arb["bookie2"],
                                                                         one_arb["odds1"],
                                                                         one_arb["odds2"],
                                                                         one_arb["margin"],
                                                                         one_arb["bookie1"],
                                                                         one_arb["bookieX"],
                                                                         one_arb["bookie2"]
                                                                         )

                self.cursor.execute(postgres_insert_query)


                self.connection.commit()

            except (Exception, psycopg2.Error) as error:
                print("Error in insert operation", error)

        self.add_positive_to_hist(df[df['margin']>1])

    def add_positive_to_hist(self, db):
        for i in range(len(db)):
            date_today = datetime.datetime.now()
            entry = db.iloc[i]
            try:
                postgres_insert_query = """ INSERT INTO arbitrage.history(date_observed, time_observed, sport, match, date, time, odds1, oddsx, odds2, margin, bookie1, bookiex, bookie2)
                                                    VALUES ('{}','{}','{}','{}','{}','{}',{},{},{}, {}, '{}', '{}', '{}');
                                                """
                postgres_insert_query = postgres_insert_query.format(
                    date_today.strftime('%Y-%m-%d'),
                    date_today.strftime('%H:%M:%S'),
                    entry["sport"],
                    entry["match"],
                    entry["date"],
                    entry["time"],
                    entry["odds1"],
                    entry["oddsX"],
                    entry["odds2"],
                    entry["margin"],
                    entry["bookie1"],
                    entry["bookieX"],
                    entry["bookie2"]
                )
                self.cursor.execute(postgres_insert_query)
                self.connection.commit()

            except (Exception, psycopg2.Error) as error:
                print("Error in insert operation", error)



    def update_daily_max(self, max_entry):
        date_today = datetime.date.today()
        current_week = date_today.isocalendar()[1]
        current_year = date_today.year
        start_of_week = datetime.datetime.strptime(f'{current_year}-{current_week}-1', "%Y-%W-%w")
        try:
            postgres_select_query = f"select * from arbitrage.history where max_date = '{date_today.strftime('%Y-%m-%d')}'"
            self.cursor.execute(postgres_select_query)
            query_result = self.cursor.fetchall()
            rows = np.array(query_result)
            if len(rows) > 0:
                if rows[:,8] < max_entry['margin']:     #update entry for the week
                    # delete current max entry
                    try:
                        postgres_remove_query = f"DELETE FROM arbitrage.history where max_date = {rows[0,0].strftime('%Y-%m-%d')}"
                        self.cursor.execute(postgres_remove_query)

                    except (Exception, psycopg2.Error) as error:
                        print("Error in delete operation", error)
            else:
                pass

            # insert new max entry
            try:
                postgres_insert_query = """ INSERT INTO arbitrage.history(max_date, sport, match, date, time, odds1, oddsx, odds2, margin, bookie1, bookiex, bookie2)
                                                    VALUES ('{}','{}','{}','{}','{}',{},{},{}, {}, '{}', '{}', '{}');
                                                """
                postgres_insert_query = postgres_insert_query.format(
                                                                    date_today.strftime('%Y-%m-%d'),
                                                                    max_entry["sport"],
                                                                    max_entry["match"],
                                                                    max_entry["date"],
                                                                    max_entry["time"],
                                                                    max_entry["odds1"],
                                                                    max_entry["oddsX"],
                                                                    max_entry["odds2"],
                                                                    max_entry["margin"],
                                                                    max_entry["bookie1"],
                                                                    max_entry["bookieX"],
                                                                    max_entry["bookie2"]
                                                                    )
                self.cursor.execute(postgres_insert_query)
                self.connection.commit()

            except (Exception, psycopg2.Error) as error:
                print("Error in insert operation", error)

        except (Exception, psycopg2.Error) as error:
            print("Error in select operation", error)
