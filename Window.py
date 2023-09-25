from functools import partial
from tkinter.constants import *

from VerticalScrolledFrame import VerticalScrolledFrame
import tkinter.ttk as ttk
import tkinter as tk


class Window:
    def __init__(self, master, buyList):
        self.frame = VerticalScrolledFrame(master)
        self.frame.pack(expand=True, fill=tk.BOTH)

        for i in range(len(buyList)):
            cell = tk.Frame(self.frame.interior)
            cell.pack(side=BOTTOM, padx=10, pady=5,)

            cancel = ttk.Button(self.frame.interior, text="cancel")
            cancel.config(command=partial(self.destroy, cell))
            cancel.pack(in_=cell, side=RIGHT)

            bought = ttk.Button(self.frame.interior, text="bought")
            bought.config(command=partial(self.destroy, cell))
            bought.pack(in_=cell, side=RIGHT)

            item = tk.Label(self.frame.interior, text=buyList[i])
            item.pack(in_=cell)

    def destroy(self, frame):
        print("beans")
        frame.destroy()
