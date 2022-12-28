import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from data.data import Data

def dataSource(app) -> ttk.Frame:
    
    fileSelected = False

    def disableEnable():
        if len(app.dataManager.data) > 0:
            fileSelected = True
            addbutton["state"] = tk.DISABLED
        else:
            fileSelected = False
            addbutton["state"] = tk.ACTIVE
        return

    def addDataSource():

        if fileSelected: return

        filetypes = (
                ('csv', '*.csv'),
                ('excel', '*.xlsx'),
                ('json', '*.json')
            )

        inputFile = filedialog.askopenfile(
            title = "Add data source",
            initialdir='./',
            filetypes=filetypes
        )

        if inputFile != None:
            d = Data(inputFile.name)
            app.dataManager.addData(d)

        tree.delete(*tree.get_children())
        [tree.insert('', tk.END, values=(d.path, d.name, d.type)) for d in app.dataManager.data]

        disableEnable()

        return
    
    def removeDataSource():
        d = tree.item(tree.focus())["values"]
        checkData = app.dataManager.findData(d[0], d[1], d[2])
        if checkData != None: app.dataManager.removeData(checkData)
        
        tree.delete(*tree.get_children())
        [tree.insert('', tk.END, values=(d.path, d.name, d.type)) for d in app.dataManager.data]

        disableEnable()

        return

    dataSources = ttk.Frame(app)
    sourceFrame = ttk.Frame(dataSources)
    buttonFrame = ttk.Frame(dataSources)

    label = tk.Label(sourceFrame, text = "Data sources", anchor="center")
    tree = ttk.Treeview(sourceFrame, columns=("path", "name", "type"), show="headings")

    tree.heading("path", text="path")
    tree.heading("name", text="name")
    tree.heading("type", text="type")

    addbutton = tk.Button(buttonFrame, text="Add data source", command=addDataSource)
    addbutton.grid(column=2, row=1, sticky='nswe')

    removeButton = tk.Button(buttonFrame, text="Remove data source", command=removeDataSource)
    removeButton.grid(column=2, row=2, sticky='nswe')

    label.grid(row=0, column=0, columnspan=2, sticky='nwe')
    tree.grid(row=1, column=0, columnspan=2, sticky='nswe')

    sourceFrame.grid(column=0, row=0)
    buttonFrame.grid(column=1, row=0)

    dataSources.grid(column=0, row=0)

    return dataSources