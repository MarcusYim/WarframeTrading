import json
import os
import sqlite3
import time
from multiprocessing.pool import ThreadPool

import pandas as pd

import requests

# pull orders, filter out non-max
# update order database
# select count(*) from orders where instr(user, '''status'': ''ingame''') > 0;


allCon = sqlite3.connect("allItems.db")
allCur = allCon.cursor()


def replaceTuples(tups: list):
    for i in range(len(tups)):
        tups[i] = tups[i][0]
    return tups


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
        return pd.DataFrame.from_dict(data)

    print(r.status_code)
    return pd.DataFrame()


allDFs = []

with ThreadPool() as pool:
    for result in pool.map(getItemTask, getAllItems(), chunksize=450):
        allDFs.append(result)

# for item in getAllItems():
#    link = getDataLink(item)
#    r = requests.get(link)

#   print(item)

#  if str(r.status_code)[0] != "2":
#     continue

#    data = r.json()["payload"]["orders"]

#   itemDF = pd.DataFrame.from_dict(data)

#  allDFs.append(itemDF)

allDF = pd.concat(allDFs)

allDF.to_csv("allOrderData.csv")

os.remove("allOrderDataBackup.csv")
