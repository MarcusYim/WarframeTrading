import csv
from tkinter import *
from tkinter import ttk

def getBuyableItemsFromCsv():
    with open("buyableItems.csv") as f:
        return csv.reader(f).__next__()

if __name__ == '__main__':
    root = Tk()
    frm = ttk.Frame(root, padding=30)
    frm.grid()
    ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)

    print(getBuyableItemsFromCsv())

    while True:
        root.update_idletasks()
        root.update()

