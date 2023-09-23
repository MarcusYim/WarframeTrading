import csv
import sqlite3
import sys

import numpy as np
import pandas as pd
import scipy as sp
import os

# SELECT name, id, platinum, mod_rank FROM allOrders WHERE mod_rank = (SELECT max(mod_rank) FROM allOrders a1 WHERE a1.name = allOrders.name)

if not os.path.isfile("allItems.db"):
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

# replace later to update allOrders
if not os.path.isfile("allOrders.db"):
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

if not os.path.isfile("inventory.db"):
    open("inventory.db", "x")
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE inventory(name varchar(10), buy_price real, buy_date datetime);")
    con.commit()
    con.close()

itemsCon = sqlite3.connect("allItems.db")
itemsCur = itemsCon.cursor()

ordersCon = sqlite3.connect("allOrders.db")
ordersCur = ordersCon.cursor()


def getAllItems():
    return replaceTuples(itemsCur.execute("SELECT DISTINCT name FROM allItems").fetchall())


def replaceTuples(tups: list):
    for i in range(len(tups)):
        tups[i] = tups[i][0]
    return tups


def getMedians(name: str):
    return replaceTuples(
        itemsCur.execute(f"SELECT median FROM allItems WHERE name = '{name}' AND order_type = 'closed'").fetchall())


def getAverageRange(name: str):
    ranges = replaceTuples(
        itemsCur.execute(f"SELECT range FROM allItems WHERE name = '{name}' AND order_type = 'closed'").fetchall())
    return sum(ranges) / len(ranges)


def getAverageVolume(name: str):
    volume = replaceTuples(
        itemsCur.execute(f"SELECT volume FROM allItems WHERE name = '{name}' AND order_type = 'closed'").fetchall())
    return sum(volume) / len(volume)


# calculates the spread in the current orders
# using the range value from allItems is not real-time enough
def getOrderSpreads(name: str):
    return ordersCur.execute("WITH maxes(max, name) AS (select MAX(platinum), name FROM allOrders WHERE order_type = "
                             f"'buy' AND name = '{name}') SELECT MIN(platinum) - max FROM allOrders, maxes WHERE "
                             "allOrders.name = maxes.name AND allOrders.order_type = 'sell' AND allOrders.name = '"
                             f"{name}';").fetchone()[0]


buyable = []

for item in getAllItems():
    slope = sp.stats.linregress(list(range(1, 8)), getMedians(item)).slope
    volume = getAverageVolume(item)

    try:
        orderSpread = getOrderSpreads(item)
        if slope > -0.1 and orderSpread < 5 and volume > 50:
            buyable.append(item)
    except TypeError:
        pass


print(buyable)
