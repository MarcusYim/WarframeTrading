import sqlite3
from datetime import datetime
from functools import partial
from tkinter.constants import *

import requests

from VerticalScrolledFrame import VerticalScrolledFrame
import tkinter.ttk as ttk
import tkinter as tk

auth_url = 'https://api.warframe.market/v1/auth/signin'
order_url = 'https://api.warframe.market/v1/profile/orders'
item_url = 'https://api.warframe.market/v1/items/'
email = 'scholarsedgetutoringbellevue@gmail.com'
password = 'abcdefg'


class Window:

    def __init__(self, master, buyList, sellList):
        self.frame = VerticalScrolledFrame(master)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.invCon = sqlite3.connect("inventory.db")
        self.invCur = self.invCon.cursor()

        self.generateOptionMenu("buy", buyList)
        self.generateConfirmationMenu("buy", buyList)
        self.generateOptionMenu("sell", sellList)
        self.generateConfirmationMenu("sell", sellList)

    def postBuyOrder(self, frame, name, platinum, rank):
        authToken = self.retrieveAuthToken()
        self.makeOrderRequest(authToken=authToken, name=name, orderType="buy", platinum=platinum, quantity=1, rank=rank)

        frame.destroy()

    def postSellOrder(self, frame, name, platinum, rank):
        authToken = self.retrieveAuthToken()
        self.makeOrderRequest(authToken=authToken, name=name, orderType="sell", platinum=platinum, quantity=1,
                              rank=rank)

        frame.destroy()

    def boughtItem(self, frame, name, platinum, rank):
        self.removeItemFromFile("buyableItems.csv", name, platinum, rank)
        self.invCur.execute(f"INSERT INTO inventory VALUES('{name}', {platinum}, datetime('now'))")
        print("bought: " + name)
        self.invCon.commit()
        frame.destroy()

    def soldItem(self, frame, name, platinum, rank):
        self.removeItemFromFile("sellableItems.csv", name, platinum, rank)

        self.invCur.execute(f"DELETE FROM inventory WHERE buy_date IN (SELECT buy_date FROM (SELECT buy_date FROM "
                            f"inventory WHERE name = '{name}' ORDER BY buy_date LIMIT 1))")

        print("sold: " + name)
        self.invCon.commit()
        frame.destroy()

    def removeItemFromFile(self, file, name, platinum, rank):
        with open(file, "r") as fout:
            line = fout.read().replace(f"\"(\'{name}\', {platinum}, {rank})\",", "")
            line = line.replace(f"\"(\'{name}\', {platinum}, {rank})\"", "")

        with open(file, "w+") as fin:
            fin.write(line)

        fout.close()
        fin.close()

    def cancelItem(self, frame):
        frame.destroy()

    def generateOptionMenu(self, mode, list):
        menu = tk.Frame(self.frame.interior)
        menu.pack(padx=10, pady=5, expand=True, side=LEFT, anchor="n")

        tk.Label(self.frame.interior, text="post " + mode + " order", underline=True, font='Helvetica 10 bold').pack(
            in_=menu, pady=10, anchor="n")

        for i in range(len(list)):
            cell = tk.Frame(self.frame.interior)
            cell.pack(in_=menu, padx=10, pady=5, fill=X, anchor="w")

            cancel = ttk.Button(self.frame.interior, text="reject")
            cancel.config(command=partial(self.cancelItem, cell, cancel))
            cancel.pack(in_=cell, side=RIGHT, padx=10, anchor="e")

            action = ttk.Button(self.frame.interior, text="post buy order" if mode == "buy" else "post sell order")
            action.config(command=partial(self.postBuyOrder if mode == "buy" else self.postSellOrder, cell, list[i][0],
                                          list[i][1], list[i][2]))
            action.pack(in_=cell, side=RIGHT, padx=10, anchor="e")

            item = tk.Label(self.frame.interior, text=list[i][0])
            item.pack(in_=cell, padx=10, anchor="w")

    def generateConfirmationMenu(self, mode, list):
        menu = tk.Frame(self.frame.interior)
        menu.pack(padx=10, pady=5, expand=True, side=LEFT, anchor="n")

        tk.Label(self.frame.interior, text="confirm " + mode + " order", underline=True, font='Helvetica 10 bold').pack(
            in_=menu, pady=10, anchor="n")

        for i in range(len(list)):
            cell = tk.Frame(self.frame.interior)
            cell.pack(in_=menu, padx=10, pady=5, fill=X, anchor="w")

            cancel = ttk.Button(self.frame.interior, text="cancel")
            cancel.config(command=partial(self.cancelItem, cell, cancel))
            cancel.pack(in_=cell, side=RIGHT, padx=10, anchor="e")

            action = ttk.Button(self.frame.interior,
                                text="confirm buy order" if mode == "buy" else "confirm sell order")
            action.config(command=partial(self.boughtItem if mode == "buy" else self.soldItem, cell, list[i][0], list[i][1], list[i][2]))
            action.pack(in_=cell, side=RIGHT, padx=10, anchor="e")

            item = tk.Label(self.frame.interior, text=list[i][0])
            item.pack(in_=cell, padx=10, anchor="w")

    def retrieveAuthToken(self):
        payload = {
            'email': email,
            'password': password
        }

        headers = {
            'Authorization': 'JWT',
            'Content-Type': 'application/json'
        }

        response = requests.post(auth_url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.headers['set-cookie'].replace("JWT=", "")
        else:
            print(f"Authorization request failed with status code {response.status_code}")
            return None

    def makeOrderRequest(self, authToken, name, orderType, platinum, quantity, rank):
        response = requests.get(item_url + name)

        if response.status_code == 200:
            itemId = response.json()["payload"]["item"]["id"]
        else:
            raise ValueError("Item name not recognized")

        payload = {
            'item': itemId,
            'order_type': orderType,
            'platinum': platinum,
            'quantity': quantity,
            'visible': True,
        }

        headers = {
            'Authorization': 'JWT',
            'Content-Type': 'application/json'
        }

        if rank != -1:
            payload['rank'] = rank

        session = requests.Session()
        session.cookies.set('JWT', authToken)

        response = session.post(order_url, json=payload, headers=headers)

        if response.status_code == 200:
            print("POST request was successful:")
            print(response.text)

        else:
            print("POST request failed:")
            print(response.text)
            raise ValueError()
