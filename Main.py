import csv
from tkinter import *
from tkinter import ttk

from Window import Window


def getBuyableItemsFromCsv():
    with open("buyableItems.csv") as f:
        return csv.reader(f).__next__()


if __name__ == '__main__':
    root = Tk()
    window = Window(root, getBuyableItemsFromCsv(), ["a", "b", "c", "d"])

    print(getBuyableItemsFromCsv())

    while True:
        root.update_idletasks()
        root.update()
