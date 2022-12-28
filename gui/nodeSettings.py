import tkinter as tk
from tkinter import ttk

from data.data import Data
from data.nodeDef import NodeDef

def nodeSettings(app):
    def handleChangeTab(event):
            dataTreeNode.delete(*dataTreeNode.get_children())
            [dataTreeNode.insert('', tk.END, values=(d.path, d.name, d.type)) for d in app.dataManager.data]

            nodeList.delete(*nodeList.get_children())
            [nodeList.insert('', tk.END, values=[n.field]) for n in app.dataManager.nodeDefs]

            return

    def handleCheck(value: tk.IntVar, field:str, data: Data):
        if (not data.loaded): data.loadData()
        node = NodeDef(field)
        if (value.get() == 1):
            app.dataManager.addNodeDef(node)
        elif (value.get() == 0):
            app.dataManager.removeNodeDef(node)
        
        nodeList.delete(*nodeList.get_children())
        [nodeList.insert('', tk.END, values=[n.field]) for n in list(app.dataManager.nodeDefs)]
        return

    def handleSelect(event):

        [child.destroy() for child in canvas.winfo_children()]

        dataList = list(app.dataManager.data)

        fieldNameFrame = ttk.Frame(canvas, width=300)

        dataIndex = dataList.index(Data(dataTreeNode.item(dataTreeNode.focus())["values"][0]))
        if (not dataList[dataIndex].loaded): dataList[dataIndex].loadData()

        fields = dataList[dataIndex].df.columns

        firstRow = ttk.Frame(fieldNameFrame)
        firstRow.grid(column=0, row=0, sticky='news', columnspan=4)
        tk.Label(firstRow, text="Field", anchor="center", font="bold").pack(side="left")
        tk.Label(firstRow, text="Node", anchor="center", font="bold").pack(side="right")

        for j, field in enumerate(fields):
            rowFrame = ttk.Frame(fieldNameFrame)
            fieldLabel = tk.Label(rowFrame, text=field, anchor="center")
            checkInt = tk.IntVar()
            check = tk.Checkbutton(rowFrame, variable=checkInt, command=lambda i=checkInt, f=field, d=dataList[dataIndex]: handleCheck(i, f, d))

            fieldLabel.pack(side="left")
            check.pack(side="right")

            rowFrame.grid(column=0, row=j+1, sticky='news')

        canvas.create_window((0,0), anchor="ne", window=fieldNameFrame)
        canvas.config(scrollregion=canvas.bbox("all"))

        return

    frame = ttk.Frame(app)

    sourceframe = ttk.Frame(frame)
    nodeFrame = ttk.Frame(frame)

    dataLabel = tk.Label(sourceframe, text = "Data sources", anchor="center")
    dataTreeNode = ttk.Treeview(sourceframe, columns=("path", "name", "type"), show="headings")

    nodeLabel = tk.Label(sourceframe, text = "Nodes", anchor="center")
    nodeList = ttk.Treeview(sourceframe, columns=("field", "filename"), show="headings")

    dataTreeNode.heading("path", text="path")
    dataTreeNode.heading("name", text="name")
    dataTreeNode.heading("type", text="type")

    nodeList.heading("field", text="Field")
    nodeList.heading("filename", text="File Name")

    app.tabs.bind('<<NotebookTabChanged>>', handleChangeTab, add="+")

    dataTreeNode.bind('<<TreeviewSelect>>', handleSelect)

    dataLabel.grid(row=0, column=0, columnspan=2, sticky='nwe')
    dataTreeNode.grid(row=1, column=0, columnspan=2, sticky='nwe')

    nodeLabel.grid(row=0, column=2, columnspan=1, sticky='nwe')
    nodeList.grid(row=1, column=2, columnspan=1, sticky='new')

    sourceframe.grid(column=0, row=0)

    # show fields list
    # add button to add node

    canvas = tk.Canvas(nodeFrame, width=300, height=300)
    vbar = tk.Scrollbar(nodeFrame, orient="vertical", command=canvas.yview)
    vbar.config(command=canvas.yview)
    vbar.pack(side="right", fill="y")
    canvas.config(yscrollcommand=vbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"), add="+")
    canvas.pack(fill="y")

    nodeFrame.grid(column=0, row=1)

    return frame