import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
from data.data import Data, excel_sheet_names
from gui.paths import documentsDir

def dataSource(app) -> ttk.Frame:
    
    fileSelected = False

    def selectFirst():
        children = tree.get_children()
        if children:
            tree.focus(children[0])
            tree.selection_set(children[0])
        return

    def repopulate():
        tree.delete(*tree.get_children())
        seen = set()
        for d in app.dataManager.data:
            if d.path in seen:
                continue
            seen.add(d.path)
            fileName = os.path.splitext(os.path.basename(d.path))[0]
            tree.insert('', tk.END, values=(d.path, fileName, d.type))
        selectFirst()
        disableEnable()
        return

    def handleChangeTab(event):
        repopulate()
        return

    def disableEnable():
        if len(app.dataManager.data) > 0:
            fileSelected = True
            addbutton["state"] = tk.DISABLED
        else:
            fileSelected = False
            addbutton["state"] = tk.NORMAL
        return

    def addDataSource():

        if fileSelected: return

        filetypes = (
                ('Data files', '*.csv *.xlsx *.json'),
                ('csv', '*.csv'),
                ('excel', '*.xlsx'),
                ('json', '*.json')
            )

        inputFile = filedialog.askopenfile(
            title = "Add data source",
            initialdir=documentsDir(),
            filetypes=filetypes
        )

        if inputFile != None:
            path = inputFile.name
            ext = os.path.splitext(path)[1].lstrip(".").lower()
            if ext == "xlsx":
                sheets = excel_sheet_names(path)
                if len(sheets) > 1:
                    for sheet in sheets:
                        app.dataManager.addData(Data(path, sheet=sheet))
                else:
                    app.dataManager.addData(Data(path))
            else:
                app.dataManager.addData(Data(path))

        repopulate()

        return
    
    def removeDataSource():
        item = tree.item(tree.focus())["values"]
        if not item:
            return
        path = item[0]
        for d in [x for x in app.dataManager.data if x.path == path]:
            app.dataManager.removeData(d)

        repopulate()

        return

    dataSources = ttk.Frame(app)
    sourceFrame = ttk.Frame(dataSources)
    buttonFrame = ttk.Frame(dataSources)

    label = ttk.Label(sourceFrame, text = "Data sources", anchor="center")
    tree = ttk.Treeview(sourceFrame, columns=("path", "name", "type"), show="headings")

    tree.heading("path", text="path")
    tree.heading("name", text="name")
    tree.heading("type", text="type")
    tree["displaycolumns"] = ("name", "type")

    addbutton = ttk.Button(buttonFrame, text="Add data source", command=addDataSource)
    addbutton.grid(column=2, row=1, sticky='nswe')

    removeButton = ttk.Button(buttonFrame, text="Remove data source", command=removeDataSource)
    removeButton.grid(column=2, row=2, sticky='nswe')

    app.tabs.bind('<<NotebookTabChanged>>', handleChangeTab, add="+")

    label.grid(row=0, column=0, columnspan=2, sticky='nwe')
    tree.grid(row=1, column=0, columnspan=2, sticky='nswe')

    dataSources.columnconfigure(0, weight=1)
    dataSources.columnconfigure(3, weight=1)
    dataSources.rowconfigure(0, weight=1)
    dataSources.rowconfigure(2, weight=1)

    sourceFrame.grid(column=1, row=1, padx=10, pady=10)
    buttonFrame.grid(column=2, row=1, padx=10, pady=10, sticky='n')

    return dataSources