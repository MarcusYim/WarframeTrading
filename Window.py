import sqlite3
from datetime import datetime
from functools import partial
from tkinter.constants import *

import requests

from VerticalScrolledFrame import VerticalScrolledFrame
import tkinter.ttk as ttk
import tkinter as tk

api_url = 'https://api.warframe.market/v1/auth/signin'
email = 'scholarsedgetutoringbellevue@gmail.com'
password = 'abcdefg'

class Window:

    def __init__(self, master, buyList, sellList):
        self.frame = VerticalScrolledFrame(master)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.invCon = sqlite3.connect("allOrders.db")
        self.invCur = self.invCon.cursor()

        self.generateOptionMenu("buy", buyList)
        self.generateConfirmationMenu("buy", buyList)
        self.generateOptionMenu("sell", sellList)
        self.generateConfirmationMenu("sell", sellList)

    def postBuyOrder(self, frame, item):
        #send api call
        frame.destroy()

    def postSellOrder(self, frame, item):
        #send api call
        frame.destroy()

    def boughtItem(self, frame, item):
        self.removeItemFromFile(item, "buyableItems.csv")
        self.invCur.execute(f"INSERT INTO inventory VALUES({item}, -1, {datetime.now})")
        print("bought: " + item)
        frame.destroy()

    def soldItem(self, frame, item):
        self.removeItemFromFile(item, "sellableItems.csv")
        print("sold: " + item)
        frame.destroy()

    def removeItemFromFile(self, item, file):
        with open(file, "r") as fout:
            line = fout.read().replace(item + ",", "")
            line = line.replace(item, "")

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
            action.config(command=partial(self.postBuyOrder if mode == "buy" else self.postSellOrder, cell, list[i]))
            action.pack(in_=cell, side=RIGHT, padx=10, anchor="e")

            item = tk.Label(self.frame.interior, text=list[i])
            item.pack(in_=cell, padx=10, anchor="w")

    def generateConfirmationMenu(self, mode, list):
        menu = tk.Frame(self.frame.interior)
        menu.pack(padx=10, pady=5, expand=True, side=LEFT, anchor="n")

        tk.Label(self.frame.interior, text="confirm " + mode + " order", underline=True, font='Helvetica 10 bold').pack(in_=menu, pady=10, anchor="n")

        for i in range(len(list)):
            cell = tk.Frame(self.frame.interior)
            cell.pack(in_=menu, padx=10, pady=5, fill=X, anchor="w")

            cancel = ttk.Button(self.frame.interior, text="cancel")
            cancel.config(command=partial(self.cancelItem, cell, cancel))
            cancel.pack(in_=cell, side=RIGHT, padx=10, anchor="e")

            action = ttk.Button(self.frame.interior, text="confirm buy order" if mode == "buy" else "confirm sell order")
            action.config(command=partial(self.boughtItem if mode == "buy" else self.soldItem, cell, list[i]))
            action.pack(in_=cell, side=RIGHT, padx=10, anchor="e")

            item = tk.Label(self.frame.interior, text=list[i])
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

        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code == 200:

            auth_token = response.headers['set-cookie']
        else:
            print(f"Authorization request failed with status code {response.status_code}")
            print(response.text)