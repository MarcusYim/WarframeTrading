from functools import partial

from VerticalScrolledFrame import VerticalScrolledFrame
import tkinter.ttk as ttk
import tkinter as tk


class Window:
    def __init__(self, master):
        self.frame = VerticalScrolledFrame(master)
        self.frame.pack(expand=True, fill=tk.BOTH)

        for i in range(10):
            b = ttk.Button(self.frame.interior, text=f"Button {i}")
            b.config(command=partial(self.destroy, b))
            b.pack(padx=10, pady=5)

    def destroy(self, button):
        print("beans")
        button.destroy()
