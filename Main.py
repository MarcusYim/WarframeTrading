import ast
import csv
from tkinter import *
from tkinter import ttk

from Window import Window


def getItemsFromCsv(file):
    with open(file) as f:
        list = csv.reader(f).__next__()

    retList = []
    for item in list:
        retList.append(ast.literal_eval(item))

    return retList

if __name__ == '__main__':
    root = Tk()

    window = Window(root, getItemsFromCsv("buyableItems.csv"), getItemsFromCsv("sellableItems.csv"))


    while True:
        root.update_idletasks()
        root.update()
