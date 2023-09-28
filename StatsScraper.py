import csv
import sqlite3

import requests
from datetime import datetime, timedelta
from tqdm import tqdm
import pandas as pd
import os
import numpy as np

allItemsLink = "https://api.warframe.market/v1/items"
r = requests.get(allItemsLink)
itemList = r.json()["payload"]["items"]
itemNameList = [x["url_name"] for x in itemList if "relic" not in x["url_name"]]
urlLookup = {x["item_name"]: x["url_name"] for x in itemList}

csvFileName = "allItemData.csv"

try:
    os.rename(csvFileName, "allItemDataBackup.csv")
except FileNotFoundError:
    pass
except FileExistsError:
    raise Exception("Remove the backup or the main csv file, one shouldn't be there for this to run.")

def isFullData(data):
    if len(data) == 0:
        return False
    if "mod_rank" in data[0].keys() and len(data) == 6:
        return True
    if "mod_rank" not in data[0].keys() and len(data) == 3:
        return True
    return False


def getDataLink(dayStr):
    return f"https://relics.run/history/price_history_{dayStr}.json"


def getDayStr(daysBack):
    day = datetime.utcnow() - timedelta(daysBack)
    dayStr = datetime.strftime(day, '%Y-%m-%d')
    return dayStr


lastSevenDays = [getDayStr(x) for x in range(1, 9)]

df = pd.DataFrame()

foundData = 0
for dayStr in tqdm(lastSevenDays):
    link = getDataLink(dayStr)
    r = requests.get(link)
    if str(r.status_code)[0] != "2" or foundData >= 7:
        continue
    foundData += 1
    for name, data in r.json().items():
        if isFullData(data):
            itemDF = pd.DataFrame.from_dict(data)

            # display(itemDF)
            try:
                itemDF = itemDF.drop(["open_price", "closed_price", "donch_top", "donch_bot"], axis=1)
                itemDF = itemDF.fillna({"order_type": "closed"})
                itemDF["name"] = urlLookup[name]
                itemDF["range"] = itemDF["max_price"] - itemDF["min_price"]
                if "mod_rank" not in itemDF.columns:
                    itemDF["mod_rank"] = np.nan
                else:
                    itemDF = itemDF[itemDF["mod_rank"] != 0]
                # display(itemDF)

                itemDF = itemDF[
                    ["name", "datetime", "order_type", "volume", "min_price", "max_price", "range", "median",
                     "avg_price", "mod_rank"]]

                df = pd.concat([df, itemDF])
            except KeyError:
                pass

countDF = df.groupby("name").count().reset_index()
popularItems = countDF[countDF["datetime"] == 21]["name"]
df = df[df["name"].isin(popularItems)]
df = df.sort_values(by="name")
itemListDF = pd.DataFrame.from_dict(itemList)
# itemListDF
# df = df.drop("Unnamed: 0", axis=1)
df["item_id"] = df.apply(lambda row: itemListDF[itemListDF["url_name"] == row["name"]].reset_index().loc[0, "id"],
                         axis=1)
df["order_type"] = df.get("order_type").str.lower()
df.to_csv("allItemData.csv", index=False)

with open('allItemData.csv', 'r') as fin:
    data = fin.read().splitlines(True)
with open('allItemData.csv', 'w') as fout:
    fout.writelines(data[1:])

os.remove("allItemDataBackup.csv")

try:
    os.remove("allItems.db")
except FileNotFoundError:
    pass

open("allItems.db", "x")
con = sqlite3.connect("allItems.db")
cur = con.cursor()
cur.execute("CREATE TABLE allItems(name varchar(10), date datetime, order_type varchar(10), volume int, "
            "min_price real, max_price real, range real, median real, avg_price real, mod_rank real, "
            "item_id varchar(10));")

file = open('allItemData.csv')
contents = csv.reader(file)
insert_items = "INSERT INTO allItems VALUES(?,?,?,?,?,?,?,?,?,?,?)"
cur.executemany(insert_items, contents)
con.commit()
con.close()