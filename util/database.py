import time
import pandas as pd
import numpy as np
import psycopg2


class Database:
    def __init__(self, config):
        self.connection = psycopg2.connect(user=config["user"],
                                      password=config["password"],
                                      host=config["host"],
                                      port=config["port"],
                                      database=config["database"])
        self.cursor = self.connection.cursor()

    def insert_scrape_to_db(self, bookie, df):

        try:
            for i in range(len(df)):

                one_bet = df.loc[i]
                print(one_bet)

                postgres_insert_query = None

                if len(one_bet["odds"]) == 2:
                    postgres_insert_query = """ INSERT INTO scrape(bookie, sport, competition, event_date, event_time, odds1, odds2, team1, team2, bet_id)
                                                VALUES ('{}','{}','{}','{}','{}',{},{},'{}','{}',{}) 
                                                ON CONFLICT (bookie, bet_id) do update SET odds1 = {}, odds2={};
                                            """
                    postgres_insert_query = postgres_insert_query.format(bookie,
                                                                         one_bet["sport"],
                                                                         one_bet["competition"],
                                                                         one_bet["date"],
                                                                         one_bet["time"],
                                                                         one_bet["odds"][0],
                                                                         one_bet["odds"][1],
                                                                         one_bet["match"][0],
                                                                         one_bet["match"][1],
                                                                         one_bet["bet_ids"],
                                                                         one_bet["odds"][0],
                                                                         one_bet["odds"][1])

                if len(one_bet["odds"])>= 5:
                    postgres_insert_query = """ INSERT INTO arbs_scrape(bookie, sport, competition, event_date, event_time, odds1, oddsx, odds2, team1, team2, bet_id)
                                                VALUES ('{}','{}','{}','{}','{}',{}, {}, {}, '{}','{}',{}) 
                                                ON CONFLICT (bookie, bet_id) do update SET odds1 = {}, oddsx={}, odds2={};
                                            """
                    postgres_insert_query = postgres_insert_query.format(bookie,
                                                                         one_bet["sport"],
                                                                         one_bet["competition"],
                                                                         one_bet["date"],
                                                                         one_bet["time"],
                                                                         one_bet["odds"][0],
                                                                         one_bet["odds"][1],
                                                                         one_bet["odds"][2],
                                                                         one_bet["match"][0],
                                                                         one_bet["match"][1],
                                                                         one_bet["bet_ids"],
                                                                         one_bet["odds"][0],
                                                                         one_bet["odds"][1],
                                                                         one_bet["odds"][2])
                if postgres_insert_query:
                    self.cursor.execute(postgres_insert_query)


                    self.connection.commit()
                    count = self.cursor.rowcount
                    print(count, "Record inserted successfully into mobile table")
                else:
                    pass


        except (Exception, psycopg2.Error) as error:
            print("Error in update operation", error)

    def close_connection(self):
        # closing database connection.
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("PostgreSQL connection is closed")

    def delete_arbs(self):
        try:
            postgres_select_query = "DELETE FROM arbs_arbs"
            self.cursor.execute(postgres_select_query)

        except (Exception, psycopg2.Error) as error:
            print("Error in delete operation", error)

    def get_scrape(self):
        try:
            postgres_select_query = "select * from arbs_scrape"
            self.cursor.execute(postgres_select_query)
            query_result = self.cursor.fetchall()
            rows = np.array(query_result)
            print(rows[0])
            df = pd.DataFrame({"bookie": rows[:,0],"bet_id":rows[:,1], "date": rows[:,2], "time": rows[:,3], "sport": rows[:,4], "competition":rows[:,5],
                                "team1":rows[:,6], "team2":rows[:,7], "odds1":rows[:,8], "oddsx":rows[:,9],"odds2": rows[:,10]})
            return df

        except (Exception, psycopg2.Error) as error:
            print("Error in select operation", error)


    def insert_arbs_to_db(self, df):
        try:
            for i in range(len(df)):
                one_arb = df.loc[i]
                print(one_arb)
                postgres_insert_query = """ INSERT INTO arbs_arbs(sport, competition, team1, team2, bookie1, bookiex, bookie2, odds1, oddsx, odds2, margin)
                                            VALUES ('{}','{}','{}','{}','{}','{}','{}', {}, {}, {}, {});
                                        """
                postgres_insert_query = postgres_insert_query.format(one_arb["sport"],
                                                                     one_arb["competition"],
                                                                     one_arb["team1"],
                                                                     one_arb["team2"],
                                                                     one_arb["bookie1"],
                                                                     one_arb["bookiex"],
                                                                     one_arb["bookie2"],
                                                                     one_arb["odds1"],
                                                                     one_arb["oddsx"],
                                                                     one_arb["odds2"],
                                                                     one_arb["margin"]
                                                                     )


                self.cursor.execute(postgres_insert_query)


                self.connection.commit()
                count = self.cursor.rowcount
                print(count, "Record inserted successfully into mobile table")

        except (Exception, psycopg2.Error) as error:
            print("Error in update operation", error)
