from VerticalScrolledFrame import VerticalScrolledFrame
import tkinter.ttk as ttk
import tkinter as tk


class Window():
    def __init__(self, master, *args, **kwargs):
        self.frame = VerticalScrolledFrame(master)
        self.frame.pack(expand=True, fill=tk.BOTH)
        self.label = ttk.Label(master, text="Shrink the window to activate the scrollbar.")
        self.label.pack()

        for i in range(10):
            ttk.Button(self.frame.interior, text=f"Button {i}").pack(padx=10, pady=5)
