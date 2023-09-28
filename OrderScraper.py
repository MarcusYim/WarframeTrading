import csv
import json
import os
import sqlite3
import time
from multiprocessing.pool import ThreadPool

import GenerateMaxRanks as mr

import pandas as pd

import requests

# pull orders, filter out non-max
# update order database
# select count(*) from orders where instr(user, '''status'': ''ingame''') > 0;


allCon = sqlite3.connect("allItems.db")
allCur = allCon.cursor()

maxRanks = pd.read_csv("maxRankData.csv")


def replaceTuples(tups: list):
    for i in range(len(tups)):
        tups[i] = tups[i][0]
    return tups


def getMaxRank(item: str):
    return int(maxRanks.loc[maxRanks["0"] == "adaptation", "1"].to_list()[0])


def getAllItems():
    return replaceTuples(allCur.execute("SELECT DISTINCT name FROM allItems").fetchall())


csvFileName = "allOrderData.csv"

try:
    os.rename(csvFileName, "allOrderDataBackup.csv")
except FileNotFoundError:
    pass
except FileExistsError:
    raise Exception("Remove the backup or the main csv file, one shouldn't be there for this to run.")


def getDataLink(item: str):
    return f"https://api.warframe.market/v1/items/{item}/orders"


def getItemTask(item: str):
    link = getDataLink(item)
    r = requests.get(link)
    print(item)

    if str(r.status_code)[0] == "2":
        data = r.json()["payload"]["orders"]
        itemDF = pd.DataFrame.from_dict(data)

        try:
            itemDF["name"] = item
            itemDF = itemDF[itemDF["user"].astype("string").str.contains("\'status\': \'ingame\'", regex=False)]
            itemDF = itemDF[itemDF["mod_rank"] == getMaxRank(item)]
        except KeyError:
            pass

        return itemDF

    print(r.status_code)
    return pd.DataFrame()


allDFs = []

with ThreadPool() as pool:
    for result in pool.map(getItemTask, getAllItems(), chunksize=450):
        allDFs.append(result)

allDF = pd.concat(allDFs)

allDF.to_csv("allOrderData.csv")

os.remove("allOrderDataBackup.csv")

try:
    os.remove("allOrders.db")
except FileNotFoundError:
    pass

open("allOrders.db", "x")
con = sqlite3.connect("allOrders.db")
cur = con.cursor()
cur.execute("CREATE TABLE allOrders(row int, platinum int, order_type varchar(10), quantity int, user varchar(10), "
            "platform varchar(10), creation_date datetime, last_update datetime, visible varchar(10), id varchar("
            "10), mod_rank real, region varchar(10), name varchar(10));")

file = open('allOrderData.csv')
contents = csv.reader(file)
insert_items = "INSERT INTO allOrders VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)"
cur.executemany(insert_items, contents)
con.commit()
con.close()