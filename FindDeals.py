import csv
import sqlite3
import pandas as pd
import os

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
    cur.execute("CREATE TABLE inventory(name varchar(10), buy_price real);")
    con.commit()
    con.close()

con = sqlite3.connect("allItems.db")
cur = con.cursor()


def getAllItems():
    return cur.execute("SELECT DISTINCT name FROM allItems")


def getMedians(name: str):
    return cur.execute(f"SELECT median FROM allItems WHERE name = '{name}' AND order_type = 'closed'").fetchall()
