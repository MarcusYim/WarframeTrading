import ast
import csv
from tkinter import *
from tkinter import ttk

from Window import Window


def getBuyableItemsFromCsv():
    with open("buyableItems.csv") as f:
        list = csv.reader(f).__next__()

    retList = []
    for item in list:
        retList.append(ast.literal_eval(item))

    return retList

if __name__ == '__main__':
    root = Tk()

    window = Window(root, getBuyableItemsFromCsv(), [("a", 1, 1), ("b", 2, 2), ("c", 3, 3), ("d", 4, 4)])


    while True:
        root.update_idletasks()
        root.update()
