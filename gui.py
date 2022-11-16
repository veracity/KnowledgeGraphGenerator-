import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import showerror, showinfo
from typing import List, Set
from pandas import DataFrame
from data.data import Data

from data.dataManager import DataManager
from data.edgeDef import EdgeDef
from data.nodeDef import NodeDef

pdTypes = [
    "integer",
    "string",
    "float",
    "boolean"
]

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        
        self.dataManager = DataManager()

        self.tabs = self.createTabs()

        self.tabs.add(self.createDataSources(), text="Add data Sources")
        self.tabs.add(self.createSettings(), text="Data Settings")
        self.tabs.add(self.createNodeSettings(), text="Define Nodes")
        self.tabs.add(self.createEdgeSettings(), text="Define Edges")
        self.tabs.add(self.generateData(), text="Generate Graph Data")
        # define edges
        # generate graph and edges

    def createTabs(self):
        tabs = ttk.Notebook(self)
        tabs.grid(column=0, row=0, sticky='nswe')

        return tabs

    def createDataSources(self):
        def addDataSource():
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

            if (inputFile != None):
                d = Data(inputFile.name)
                self.dataManager.addData(d)
            
            tree.delete(*tree.get_children())
            [tree.insert('', tk.END, values=(d.path, d.name, d.type)) for d in self.dataManager.data]

            return

        def removeDataSource():
            d = tree.item(tree.focus())["values"]
            checkData = self.dataManager.findData(d[0], d[1], d[2])
            if checkData != None: self.dataManager.removeData(checkData)
            
            tree.delete(*tree.get_children())
            [tree.insert('', tk.END, values=(d.path, d.name, d.type)) for d in self.dataManager.data]

            return


        dataSources = ttk.Frame(self)
        Sourceframe = ttk.Frame(dataSources)
        buttonFrame = ttk.Frame(dataSources)

        label = tk.Label(Sourceframe, text = "Data sources", anchor="center")
        tree = ttk.Treeview(Sourceframe, columns=("path", "name", "type"), show="headings")

        tree.heading("path", text="path")
        tree.heading("name", text="name")
        tree.heading("type", text="type")

        addbutton = tk.Button(buttonFrame, text="Add data source", command=addDataSource)
        addbutton.grid(column=2, row=1, sticky='nswe')

        removeButton = tk.Button(buttonFrame, text="Remove data source", command=removeDataSource)
        removeButton.grid(column=2, row=2, sticky='nswe')

        label.grid(row=0, column=0, columnspan=2, sticky='nwe')
        tree.grid(row=1, column=0, columnspan=2, sticky='nswe')

        Sourceframe.grid(column=0, row=0)
        buttonFrame.grid(column=1, row=0)

        dataSources.grid(column=0, row=0)

        return dataSources

    def createSettings(self):

        def handleChangeTab(event):
            dataTreeSettings.delete(*dataTreeSettings.get_children())
            for d in self.dataManager.data:
                dataTreeSettings.insert('', tk.END, values=(d.path, d.name, d.type))
            return

        def handleSelect(event):

            def changeType(dataFrame: DataFrame, column: str, inType: str, menu: tk.StringVar):
                # try to set type
                oldText = menu.get()
                # print(dataFrame.head())
                if (inType == "integer"):
                    try:
                        dataFrame[column] = dataFrame[column].astype("int64")
                    except Exception as e:
                        showerror(title="Formatting error", message="Cannot change type of field. Make sure the formatting is correct.\nTry removing spaces in number fields.")
                        menu.set(oldText)
                elif (inType == "string"):
                    try:
                        dataFrame[column] = dataFrame[column].astype("string")
                    except Exception as e:
                        showerror(title="Formatting error", message="Cannot change type of field. Make sure the formatting is correct.")
                        menu.set(oldText)
                elif (inType == "float"):
                    try:
                        dataFrame[column] = dataFrame[column].astype("float64")
                    except Exception as e:
                        showerror(title="Formatting error", message="Cannot change type of field. Make sure the formatting is correct.")
                        menu.set(oldText)
                elif (inType == "boolean"):
                    try:
                        dataFrame[column] = dataFrame[column].astype("boolean")
                    except Exception as e:
                        showerror(title="Formatting error", message="Cannot change type of field. Make sure the formatting is correct.")
                        menu.set(oldText)
                return

            [child.destroy() for child in canvas.winfo_children()]

            fieldNameFrame = ttk.Frame(canvas, width=300)

            dataList = list(self.dataManager.data)

            dataIndex = dataList.index(Data(dataTreeSettings.item(dataTreeSettings.focus())["values"][0]))
            if (not dataList[dataIndex].loaded): dataList[dataIndex].loadData()

            columns = dataList[dataIndex].df.columns

            firstRow = ttk.Frame(fieldNameFrame)
            firstRow.grid(column=0, row=0, sticky='news', columnspan=4)
            tk.Label(firstRow, text="Field", anchor="center", font="bold").pack(side="left")
            tk.Label(firstRow, text="Type", anchor="center", font="bold").pack(side="right")

            for j, col in enumerate(columns):
                rowFrame = ttk.Frame(fieldNameFrame)
                optionText = tk.StringVar()
                optionText.set(str(dataList[dataIndex].df[col].dtype))

                fieldLabel = tk.Label(rowFrame, text=col, anchor="center")
                w = tk.OptionMenu(rowFrame, optionText, *pdTypes, command=lambda x, df=dataList[dataIndex].df, c=col, o=optionText, : changeType(df, c, x.get(), o))

                fieldLabel.pack(side="left")
                w.pack(side="right")

                rowFrame.grid(row=j+1, column=0, sticky='news')

            canvas.create_window((0,0), anchor="nw", window=fieldNameFrame)
            canvas.config(scrollregion=canvas.bbox("all"))

            return


        frame = ttk.Frame(self)

        # Sources
        sourceframe = ttk.Frame(frame)
        settingsFrame = ttk.Frame(frame)

        dataLabel = tk.Label(sourceframe, text = "Data sources", anchor="center")
        dataTreeSettings = ttk.Treeview(sourceframe, columns=("path", "name", "type"), show="headings")

        dataTreeSettings.heading("path", text="path")
        dataTreeSettings.heading("name", text="name")
        dataTreeSettings.heading("type", text="type")

        dataLabel.grid(row=0, column=0, columnspan=4, sticky='nwe')
        dataTreeSettings.grid(row=1, column=0, columnspan=4, sticky='nwe')

        self.tabs.bind('<<NotebookTabChanged>>', handleChangeTab, add="+")
        dataTreeSettings.bind('<<TreeviewSelect>>', handleSelect)

        sourceframe.grid(column=0, row=0)

        # settings
        canvas = tk.Canvas(settingsFrame, width=300, height=300)
        vbar = tk.Scrollbar(settingsFrame, orient="vertical", command=canvas.yview)
        vbar.config(command=canvas.yview)
        vbar.pack(side="right", fill="y")
        canvas.config(yscrollcommand=vbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"), add="+")
        canvas.pack(fill="y")
        settingsFrame.grid(column=0, row=1)

        # Add general info about file

        return frame

    def createNodeSettings(self):

        def handleChangeTab(event):
            dataTreeNode.delete(*dataTreeNode.get_children())
            [dataTreeNode.insert('', tk.END, values=(d.path, d.name, d.type)) for d in self.dataManager.data]

            nodeList.delete(*nodeList.get_children())
            [nodeList.insert('', tk.END, values=[n.field]) for n in self.dataManager.nodeDefs]

            return

        def handleCheck(value: tk.IntVar, field:str, data: Data):
            if (not data.loaded): data.loadData()
            node = NodeDef(field)
            if (value.get() == 1):
                self.dataManager.addNodeDef(node)
            elif (value.get() == 0):
                self.dataManager.removeNodeDef(node)
            
            nodeList.delete(*nodeList.get_children())
            [nodeList.insert('', tk.END, values=[n.field]) for n in list(self.dataManager.nodeDefs)]
            return

        def handleSelect(event):

            [child.destroy() for child in canvas.winfo_children()]

            dataList = list(self.dataManager.data)

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

        frame = ttk.Frame(self)

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

        self.tabs.bind('<<NotebookTabChanged>>', handleChangeTab, add="+")

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

    def createEdgeSettings(self):
        def handleChangeTab(event):
            nodeList.delete(*nodeList.get_children())
            [nodeList.insert('', tk.END, values=[n.field]) for n in list(self.dataManager.nodeDefs)]

            edgeList.delete(*edgeList.get_children())
            [edgeList.insert('', tk.END, values=(e.source, e.target, e.directed)) for e in self.dataManager.edgeDefs]
            return

        def handleSelectNode(event):

            def handleAddEdge(source: NodeDef, optionText: tk.StringVar, directed: tk.IntVar):
                # print(self.dataManager.edgeDefs)
                if (len(optionText.get()) == 0): return
                targetIn = optionText.get()
                print(f"targetIn: {targetIn}")
                target = self.dataManager.findNodeDef(targetIn)
                print(f"target: {target}")
                if target != None:
                    edge = EdgeDef(source, target, bool(directed.get()))

                    self.dataManager.addEdgeDef(edge)

                edgeList.delete(*edgeList.get_children())
                [edgeList.insert('', tk.END, values=(e.source, e.target, e.directed)) for e in list(self.dataManager.edgeDefs)]

                return

            [child.destroy() for child in canvas.winfo_children()]

            frame = ttk.Frame(canvas, width=600)
            insideFrame = ttk.Frame(frame)

            values = nodeList.item(nodeList.focus())["values"]
            node = self.dataManager.findNodeDef(values[0])

            listWithoutSelected = self.dataManager.nodeDefs.copy()
            if node != None:
                listWithoutSelected.remove(node)

                selectedNodeLabel = tk.Label(insideFrame, text=str(node), font="bold")
                connectToLabel = tk.Label(insideFrame, text="Connect to")
                optionText = tk.StringVar()
                options = tk.OptionMenu(insideFrame, optionText, *[str(n) for n in listWithoutSelected])
                
                directedFrame = ttk.Frame(insideFrame)
                directedCheck = tk.IntVar()
                directed = tk.Checkbutton(directedFrame, variable=directedCheck)
                directedLabel = tk.Label(directedFrame, text="Directed")

                addButton = tk.Button(insideFrame, text="Add Edge", command=lambda s=node, o=optionText, d=directedCheck : handleAddEdge(s, o, d))

                selectedNodeLabel.grid(column=0, row=0)
                connectToLabel.grid(row=0, column=1)
                options.grid(row=0, column=2)
                directedFrame.grid(row=1, column=0)
                directedLabel.pack(side="left")
                directed.pack(side="right")
                addButton.grid(row=1, column=1, columnspan=2)
                insideFrame.pack(fill="both", pady=10)

                canvas.create_window((0,2), anchor="center", window=frame)
                canvas.config(scrollregion=canvas.bbox("all"))


            return

        def handleEditEdge():

            return

        def handleRemoveEdge():
            print(edgeList.item(edgeList.focus()))

            for sel in edgeList.selection():
                edgeList.delete(sel)
            return

        frame = ttk.Frame(self)

        sourceframe = ttk.Frame(frame)
        buttonFrame = ttk.Frame(sourceframe)
        settingsFrame = ttk.Frame(frame)

        nodeLabel = tk.Label(sourceframe, text = "Nodes", anchor="center")
        nodeList = ttk.Treeview(sourceframe, columns=("field", "filename"), show="headings")

        edgeLabel = tk.Label(sourceframe, text = "Edges", anchor="center")
        edgeList = ttk.Treeview(sourceframe, columns=("source", "target", "directed"), show="headings")

        nodeList.heading("field", text="Field")
        nodeList.heading("filename", text="File Name")

        edgeList.heading("source", text="Source")
        edgeList.heading("target", text="Target")
        edgeList.heading("directed", text="Directed")

        self.tabs.bind('<<NotebookTabChanged>>', handleChangeTab, add="+")
        nodeList.bind('<<TreeviewSelect>>', handleSelectNode)

        nodeLabel.grid(row=0, column=0, columnspan=2, sticky='new')
        nodeList.grid(row=1, column=0, columnspan=2, sticky='new')
        edgeLabel.grid(row=0, column=2, columnspan=2, sticky='nwe')
        edgeList.grid(row=1, column=2, columnspan=2, sticky='nwe')


        editEdgeButton = tk.Button(buttonFrame, text="Edit Edge", command=handleEditEdge)
        removeEdgeButton = tk.Button(buttonFrame, text="Remove Edge", command=handleRemoveEdge)

        editEdgeButton.grid(row=1, column=0, sticky='news', rowspan=2)
        removeEdgeButton.grid(row=3, column=0, sticky='news', rowspan=2)
        buttonFrame.grid(row=1, column=4, sticky='news')

        canvas = tk.Canvas(settingsFrame, width=600, height=300)
        canvas.pack(fill="y", pady=10)

        fillFrame = ttk.Frame(canvas)
        canvas.create_window((0,0), anchor="ne", window=fillFrame)

        sourceframe.grid(column=0, row=0)
        settingsFrame.grid(column=0, row=1)

        return frame

    def generateData(self):

        def handleNodePath():
            filetypes = (
                ('csv', '*.csv'),
            )

            filename = filedialog.asksaveasfile(initialdir='./', filetypes=filetypes, title="Select file for nodes")
            if filename != None:
                nodePath.set(filename.name)
            return

        def handleEdgePath():
            filetypes = (
                ('csv', '*.csv'),
            )

            filename = filedialog.asksaveasfile(initialdir='./', filetypes=filetypes, title="Select file for nodes")
            if filename != None:
                edgePath.set(filename.name)
            return

        def save():
            if (nodePath.get() == "path" or edgePath.get() == "path"): 
                showerror(title="File path not set", message="You need to set a file path for both nodes and edges.")
                return

            print("generating data")
            self.dataManager.generateData()

            self.dataManager.generateNodeFile(nodePath.get())
            self.dataManager.generateEdgeFile(edgePath.get())

            showinfo(title="Graph files generated", message="The graph files have been generated. You can view them in the path you specified.")
            return


        frame = ttk.Frame(self)
        nodePath = tk.StringVar()
        nodePath.set("path")
        edgePath = tk.StringVar()
        edgePath.set("path")

        nodeFrame = ttk.Frame(frame)
        edgeFrame = ttk.Frame(frame)

        nodePathButton = tk.Button(nodeFrame, text="Set node location", command=handleNodePath)
        nodeLabe = tk.Label(nodeFrame, textvariable=nodePath)

        edgePathButton = tk.Button(edgeFrame, text="Set edge location", command=handleEdgePath)
        edgeLabel = tk.Label(edgeFrame, textvariable=edgePath)

        nodePathButton.pack(side="left")
        nodeLabe.pack(side="right")

        edgePathButton.pack(side="left")
        edgeLabel.pack(side="right")

        saveButton = tk.Button(frame, text="Generate Graph", command=save)

        nodeFrame.grid(column=0, row=0, sticky='w', padx=50, pady=50)
        edgeFrame.grid(column=0, row=1, sticky='w', padx=50)
        saveButton.grid(column=1, row=0, sticky='e', padx=50, pady=50)

        frame.grid(sticky='news')
        return frame