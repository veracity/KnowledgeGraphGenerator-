from tkinter import filedialog, ttk
from tkinter.messagebox import showerror, showinfo
import tkinter as tk

def generateData(app):
    def handleNodePath():
        filetypes = (
            ('csv', '*.csv'),
        )

        filename = filedialog.asksaveasfilename(initialdir='./', filetypes=filetypes, title="Select file for nodes")
        if filename != None:
            nodePath.set(f"{filename}.csv")
        return

    def handleEdgePath():
        filetypes = (
            ('csv', '*.csv'),
        )

        filename = filedialog.asksaveasfilename(initialdir='./', filetypes=filetypes, title="Select file for edges")
        if filename != None:
            edgePath.set(f"{filename}.csv")
        return

    def save():
        if (nodePath.get() == "path" or edgePath.get() == "path"): 
            showerror(title="File path not set", message="You need to set a file path for both nodes and edges.")
            return

        print("generating data")
        app.dataManager.generateData()

        app.dataManager.generateNodeFile(nodePath.get())
        app.dataManager.generateEdgeFile(edgePath.get())

        showinfo(title="Graph files generated", message="The graph files have been generated. You can view them in the path you specified.")
        return

    frame = ttk.Frame(app)
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