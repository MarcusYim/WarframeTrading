from functools import partial
from tkinter.constants import *

from VerticalScrolledFrame import VerticalScrolledFrame
import tkinter.ttk as ttk
import tkinter as tk


class Window:
    def __init__(self, master, buyList, sellList):
        self.frame = VerticalScrolledFrame(master)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.generateMenu("bought", buyList)
        self.generateMenu("sold", sellList)

    def boughtItem(self, frame, item):
        self.removeItemFromFile(item, "buyableItems.csv")
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

    def generateMenu(self, mode, list):
        menu = tk.Frame(self.frame.interior)
        menu.pack(padx=10, pady=5, expand=True, side=LEFT, anchor="n")

        for i in range(len(list)):
            cell = tk.Frame(self.frame.interior)
            cell.pack(in_=menu, padx=10, pady=5, fill=X, anchor="w")

            cancel = ttk.Button(self.frame.interior, text="cancel")
            cancel.config(command=partial(self.cancelItem, cell, cancel))
            cancel.pack(in_=cell, side=RIGHT, padx=10, anchor="e")

            action = ttk.Button(self.frame.interior, text=mode)
            action.config(command=partial(self.boughtItem if mode == "bought" else self.soldItem, cell, list[i]))
            action.pack(in_=cell, side=RIGHT, padx=10, anchor="e")

            item = tk.Label(self.frame.interior, text=list[i])
            item.pack(in_=cell, padx=10, anchor="w")