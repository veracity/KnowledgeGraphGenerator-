import tkinter as tk
from tkinter import ttk

from data.dataManager import DataManager
from gui.dataSettings import dataSettings
from gui.dataSource import dataSource
from gui.edgeSettings import edgeSettings
from gui.generateData import generateData
from gui.nodeSettings import nodeSettings

class App(tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self.dataManager = DataManager()

        self.tabs = self.createTabs()

        self.tabs.add(dataSource(self), text="Add data source")
        self.tabs.add(dataSettings(self), text="Data Settings")
        self.tabs.add(nodeSettings(self), text="Define Nodes")
        self.tabs.add(edgeSettings(self), text="Define Edges")
        self.tabs.add(generateData(self), text="Generate Graph Data")

        return

    def createTabs(self) -> ttk.Notebook:
        tabs = ttk.Notebook(self)
        tabs.grid(column=0, row=0, sticky='nswe')
        return tabs