import csv
import sqlite3
import sys

import numpy as np
import pandas as pd
import scipy as sp
import os

import matplotlib.pyplot as plt

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


if not os.path.isfile("inventory.db"):
    open("inventory.db", "x")
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE inventory(name varchar(10), buy_price real, buy_date datetime);")
    con.commit()
    con.close()

con = sqlite3.connect("allItems.db")
cur = con.cursor()


def getAllItems():
    return replaceTuples(cur.execute("SELECT DISTINCT name FROM allItems").fetchall())


def replaceTuples(tups: list):
    for i in range(len(tups)):
        tups[i] = tups[i][0]
    return tups


def getMedians(name: str):
    return replaceTuples(
        cur.execute(f"SELECT median FROM allItems WHERE name = '{name}' AND order_type = 'closed'").fetchall())


def getAverageRange(name: str):
    ranges = replaceTuples(
        cur.execute(f"SELECT range FROM allItems WHERE name = '{name}' AND order_type = 'closed'").fetchall())
    return sum(ranges) / len(ranges)

def getAverageVolume(name: str):
    volume = replaceTuples(
        cur.execute(f"SELECT volume FROM allItems WHERE name = '{name}' AND order_type = 'closed'").fetchall())
    return sum(volume) / len(volume)


buyable = []

for item in getAllItems():
    slope = sp.stats.linregress(list(range(1, 8)), getMedians(item)).slope
    avRange = getAverageRange(item)
    volume = getAverageVolume(item)
    if slope > -0.1 and avRange < 5 and volume > 50:
        buyable.append(item)

print(buyable)

