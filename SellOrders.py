import csv
import datetime
import sqlite3
from FindDeals import replaceTuples, getAverageVolume, getMaxRank, ordersCur, getOrderSpreads, getAverageMedian
import os

profitMargin = 0.02  # must sell at a minimum x% profit if not dumping
minHold = 7  # hold items for x days before considering dumping

# it would be nice if these were somehow set in the ui bc I don't want to pull these from FindDeals
volumeThresh = 50
medianThresh = 0.05  # ensure sale price consistency

invCon = sqlite3.connect("inventory.db")
invCur = invCon.cursor()

def getInventory():
    return replaceTuples(invCur.execute("SELECT strftime('%Y %m %d %H %M %S %s','buy_date') FROM inventory").fetchall())
# using exact datetime value of buy command as an ID to prevent confusion from owning two items of same type
# just means we have to back trace item name from what time it was bought

def traceName(buy_date: str):
    return invCur.execute(f"SELECT name FROM inventory WHERE strftime('%Y %m %d %H %M %S %s','buy_date') = '{buy_date}'").fetchone()[0]

def getBoughtPrice(buy_date: str):
    return invCur.execute(f"SELECT buy_price FROM inventory WHERE strftime('%Y %m %d %H %M %S %s','buy_date') = '{buy_date}'").fetchone()[0]

def getMinSellOrder(name: str):
    return ordersCur.execute(f"SELECT MIN(platinum) FROM allOrders WHERE order_type = 'sell' AND name = '{name}'").fetchone()[0]


# actually listing what to sell

sellable = []

# remember that item = time item was bought, not item name
for item in getInventory():
    profitCheck = (1 + profitMargin) * getBoughtPrice(item)
    volume = getAverageVolume(traceName(item))

    try:
        spread = getOrderSpreads(traceName(item))
        if profitCheck <= getMinSellOrder(traceName(item)) and volume >= volumeThresh and spread <= medianThresh * getAverageMedian(traceName(item)):
            sellable.append((item, getMinSellOrder(traceName(item)), getMaxRank(traceName(item))))
        # elif [has been 7 days]:
            # sellable.append((item, getMinSellOrder(traceName(item)), getMaxRank(traceName(item))))
    except TypeError:
        pass

try:
    os.remove("sellableItems.csv")
except FileNotFoundError:
    pass

with open("sellableItems.csv", "w") as r:
    write = csv.writer(r)
    write.writerow(sellable)
