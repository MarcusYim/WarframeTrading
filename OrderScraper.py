import json
import os
import sqlite3
import pandas as pd

import requests

# pull orders, filter out non-max
# update order database
# select count(*) from orders where instr(user, '''status'': ''ingame''') > 0;


allCon = sqlite3.connect("allItems.db")
allCur = allCon.cursor()


def getAllItems():
    return allCur.execute("SELECT DISTINCT name FROM allItems").fetchall()


csvFileName = "allOrderData.csv"

try:
    os.rename(csvFileName, "allOrderDataBackup.csv")
except FileNotFoundError:
    pass
except FileExistsError:
    raise Exception("Remove the backup or the main csv file, one shouldn't be there for this to run.")


def getDataLink(item: str):
    return f"https://api.warframe.market/v1/items/{item}/orders"

allDF = pd.DataFrame()

for item in getAllItems():
    link = getDataLink(item)
    r = requests.get(link)

    if str(r.status_code)[0] != "2":
        print(r.status_code)
        continue

    data = r.json()["payload"]["orders"]

    itemDF = pd.DataFrame.from_dict(data)

    allDF = pd.concat([allDF, itemDF])

allDF.to_csv("sample.csv")