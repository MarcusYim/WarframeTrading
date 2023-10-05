import csv
import sqlite3
import sys

import numpy as np
import pandas as pd
import scipy as sp
import os

slopeThreshold = -0.05
volumeThreshold = 50
percentMedian = 0.05

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

def getAverageMedian(name: str):
    medians = getMedians(name)
    return sum(medians) / len(medians)

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


def getMaxBuyOrder(name: str):
    return \
    ordersCur.execute(f"SELECT MAX(platinum) FROM allOrders WHERE order_type = 'buy' AND name = '{name}'").fetchone()[0]


def getMaxRank(name: str):
    try:
        return int(ordersCur.execute(f"SELECT DISTINCT mod_rank FROM allOrders WHERE name = '{name}'").fetchone()[0])
    except ValueError:
        return -1


buyable = []

for item in getAllItems():
    slope = sp.stats.linregress(list(range(1, 8)), getMedians(item)).slope
    volume = getAverageVolume(item)

    try:
        orderSpread = getOrderSpreads(item)
        if slope >= slopeThreshold and orderSpread <= percentMedian * getAverageMedian(item) and volume >= volumeThreshold:
            buyable.append((item, getMaxBuyOrder(item), getMaxRank(item)))
    except TypeError:
        pass

try:
    os.remove("buyableItems.csv")
except FileNotFoundError:
    pass

with open("buyableItems.csv", "w") as r:
    write = csv.writer(r)
    write.writerow(buyable)
