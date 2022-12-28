import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
from data.edgeDef import EdgeDef
from data.nodeDef import NodeDef

def edgeSettings(app):
    def handleChangeTab(event):
        nodeList.delete(*nodeList.get_children())
        [nodeList.insert('', tk.END, values=[n.field]) for n in list(app.dataManager.nodeDefs)]

        edgeList.delete(*edgeList.get_children())
        [edgeList.insert('', tk.END, values=(e.source, e.target, e.directed)) for e in app.dataManager.edgeDefs]
        return

    def handleSelectNode(event):

        def handleAddEdge(source: NodeDef, optionText: tk.StringVar, directed: tk.IntVar):
            # print(app.dataManager.edgeDefs)
            if (len(optionText.get()) == 0): return
            targetIn = optionText.get()
            print(f"targetIn: {targetIn}")
            target = app.dataManager.findNodeDef(targetIn)
            print(f"target: {target}")
            if target != None:
                edge = EdgeDef(source, target, bool(directed.get()))

                app.dataManager.addEdgeDef(edge)

            edgeList.delete(*edgeList.get_children())
            [edgeList.insert('', tk.END, values=(e.source, e.target, e.directed)) for e in list(app.dataManager.edgeDefs)]

            return

        [child.destroy() for child in canvas.winfo_children()]

        frame = ttk.Frame(canvas, width=600)
        insideFrame = ttk.Frame(frame)

        values = nodeList.item(nodeList.focus())["values"]
        node = app.dataManager.findNodeDef(values[0])

        listWithoutSelected = app.dataManager.nodeDefs.copy()
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
        for sel in edgeList.selection():
            i = edgeList.item(sel)
            edge = app.dataManager.findEdgeDef(i["values"][0], i["values"][1])
            edgeList.delete(sel)
            app.dataManager.removeEdgeDef(edge)
        return

    frame = ttk.Frame(app)

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

    app.tabs.bind('<<NotebookTabChanged>>', handleChangeTab, add="+")
    nodeList.bind('<<TreeviewSelect>>', handleSelectNode)

    nodeLabel.grid(row=0, column=0, columnspan=2, sticky='new')
    nodeList.grid(row=1, column=0, columnspan=2, sticky='new')
    edgeLabel.grid(row=0, column=2, columnspan=2, sticky='nwe')
    edgeList.grid(row=1, column=2, columnspan=2, sticky='nwe')


    editEdgeButton = tk.Button(buttonFrame, text="Edit Edge", command=handleEditEdge, state=tk.DISABLED)
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