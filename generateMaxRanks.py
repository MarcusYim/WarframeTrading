import csv
import os
import sqlite3

import pandas as pd

try:
    os.remove("maxRankData.csv")
except FileNotFoundError:
    pass

try:
    os.remove("maxRanks.db")
except FileNotFoundError:
    pass


con = sqlite3.connect("allItems.db")
cur = con.cursor()

max_ranks = cur.execute(
    "SELECT allItems.name, allItems.mod_rank, allItems.date, allItems.order_type from allItems INNER JOIN ("
    "SELECT name, max(mod_rank) mod_rank, item_id, date, order_type from allItems a2 group by name) AS max on "
    "max.name = allItems.name AND max.mod_rank = allItems.mod_rank AND max.date = allItems.date AND "
    "max.order_type = allItems.order_type;").fetchall()

maxDF = pd.DataFrame.from_records(max_ranks)
maxDF = maxDF.replace("", -1.0)
maxDF.to_csv("maxRankData.csv")

open("maxRanks.db", "x")
con = sqlite3.connect("maxRanks.db")
cur = con.cursor()
cur.execute("CREATE TABLE maxRanks(row int, name varchar(10), max_rank real, date datetime, order_type varchar(10));")

file = open('maxRankData.csv')
contents = csv.reader(file)
insert_items = "INSERT INTO maxRanks VALUES(?,?,?,?,?)"
cur.executemany(insert_items, contents)
con.commit()
con.close()