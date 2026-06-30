from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import tkinter as tk
import threading
import os

def generateData(app):

    FORMATS = {
        "GraphML": "graphml",
        "GEXF": "gexf",
        "GML": "gml",
        "CSV (nodes + edges)": "csv",
    }

    EXTENSIONS = {
        "graphml": ".graphml",
        "gexf": ".gexf",
        "gml": ".gml",
    }

    def currentFormat():
        return FORMATS.get(formatVar.get(), "graphml")

    def projectFolder():
        if app.projectPath is None:
            return None
        return os.path.dirname(app.projectPath)

    def outputFiles(folder, fmt):
        if fmt == "csv":
            return [os.path.join(folder, "nodes.csv"), os.path.join(folder, "edges.csv")]
        return [os.path.join(folder, f"graph{EXTENSIONS[fmt]}")]

    def updateState(event=None):
        folder = projectFolder()
        hasNodes = len(app.dataManager.nodeDefs) > 0
        if folder is None:
            destinationVar.set("No project open.")
            saveButton["state"] = tk.DISABLED
            return
        files = outputFiles(folder, currentFormat())
        destinationVar.set("Output will be written to:\n" + "\n".join(files))
        saveButton["state"] = tk.NORMAL if hasNodes else tk.DISABLED
        return

    def save():
        folder = projectFolder()
        if folder is None:
            showerror(title="No project", message="Create or open a project before generating output.")
            return
        if len(app.dataManager.nodeDefs) == 0:
            showerror(title="No nodes", message="Define at least one node before generating output.")
            return

        fmt = currentFormat()
        files = outputFiles(folder, fmt)

        saveButton["state"] = tk.DISABLED
        app.setStatus("Generating graph data...")

        def onDone():
            app.setStatus("Graph files generated.")
            updateState()
            showinfo(title="Graph files generated", message="The graph files have been generated in the project folder:\n" + "\n".join(files))
            return

        def onError(error):
            app.setStatus("Generation failed.")
            updateState()
            showerror(title="Generation failed", message=str(error))
            return

        def worker():
            try:
                app.dataManager.generateData()
                if fmt == "csv":
                    app.dataManager.generateNodeFile(files[0])
                    app.dataManager.generateEdgeFile(files[1])
                else:
                    exporters = {
                        "graphml": app.dataManager.generateGraphmlFile,
                        "gexf": app.dataManager.generateGexfFile,
                        "gml": app.dataManager.generateGmlFile,
                    }
                    exporters[fmt](files[0])
            except Exception as error:
                app.after(0, lambda e=error: onError(e))
                return
            app.after(0, onDone)
            return

        threading.Thread(target=worker, daemon=True).start()
        return

    formatVar = tk.StringVar(value="GraphML")
    destinationVar = tk.StringVar(value="")

    frame = ttk.Frame(app, padding=12)
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(2, weight=1)
    frame.rowconfigure(0, weight=1)
    frame.rowconfigure(2, weight=1)

    content = ttk.Frame(frame)
    content.grid(row=1, column=1)

    formatRow = ttk.Frame(content)
    formatRow.grid(row=0, column=0, sticky="ew", pady=(0, 16))
    ttk.Label(formatRow, text="Export format").pack(side="left", padx=(0, 10))
    formatMenu = ttk.OptionMenu(formatRow, formatVar, formatVar.get(), *FORMATS.keys(), command=updateState)
    formatMenu.pack(side="left")

    ttk.Label(content, textvariable=destinationVar, justify="left").grid(row=1, column=0, sticky="w", pady=8)

    saveButton = ttk.Button(content, text="Generate Graph", command=save, state=tk.DISABLED)
    saveButton.grid(row=2, column=0, pady=(20, 0))

    app.tabs.bind('<<NotebookTabChanged>>', updateState, add="+")

    updateState()
    return frame