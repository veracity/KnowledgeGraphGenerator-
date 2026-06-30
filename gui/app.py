import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import showerror, askyesno, showwarning

import os

import sv_ttk

from data.dataManager import DataManager
from data.project import saveProject, loadProject
from gui.dataSettings import dataSettings
from gui.dataSource import dataSource
from gui.edgeSettings import edgeSettings
from gui.generateData import generateData
from gui.nodeSettings import nodeSettings
from gui.paths import documentsDir

PROJECT_FILENAME = "project.ngproj"

GRAPH_EXPORTERS = {
    "graphml": lambda dm, path: dm.generateGraphmlFile(path),
    "gexf": lambda dm, path: dm.generateGexfFile(path),
    "gml": lambda dm, path: dm.generateGmlFile(path),
}

class App(tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self.title("Knowledge Graph Generator")
        self.geometry("900x600")
        self.minsize(700, 450)

        sv_ttk.set_theme("light")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.dataManager = DataManager()
        self.projectPath = None

        self.status = tk.StringVar(value="Ready")

        self.createMenu()

        self.tabs = self.createTabs()

        self.tabs.add(dataSource(self), text="Add data source")
        self.tabs.add(dataSettings(self), text="Data Settings")
        self.tabs.add(nodeSettings(self), text="Define Nodes")
        self.tabs.add(edgeSettings(self), text="Define Edges")
        self.tabs.add(generateData(self), text="Generate Graph Data")

        statusBar = ttk.Label(self, textvariable=self.status, anchor="w", relief="sunken")
        statusBar.grid(column=0, row=1, sticky='we')

        self.after(0, self.ensureProject)

        return

    def setStatus(self, message: str) -> None:
        self.status.set(message)
        return

    def createMenu(self) -> None:
        menubar = tk.Menu(self)
        fileMenu = tk.Menu(menubar, tearoff=0)
        fileMenu.add_command(label="New Project", command=self.newProject)
        fileMenu.add_command(label="Open Project...", command=self.openProject)
        fileMenu.add_separator()
        fileMenu.add_command(label="Save Project", command=self.saveProject)
        fileMenu.add_command(label="Save Project As...", command=self.saveProjectAs)
        menubar.add_cascade(label="File", menu=fileMenu)
        self.config(menu=menubar)
        return

    def refreshTabs(self) -> None:
        self.tabs.event_generate("<<NotebookTabChanged>>")
        return

    def newProject(self) -> None:
        if self.projectPath is not None and not askyesno(title="New Project", message="Start a new project? Any unsaved changes will be lost."):
            return
        folder = filedialog.askdirectory(title="New Project Folder", initialdir=documentsDir())
        if not folder:
            return
        path = os.path.join(folder, PROJECT_FILENAME)
        if os.path.isfile(path) and not askyesno(title="Project exists", message=f"A {PROJECT_FILENAME} already exists in this folder. Overwrite it?"):
            return
        self.dataManager.clear()
        self.projectPath = path
        self._writeProject(path)
        self.title(f"Knowledge Graph Generator - {folder}")
        self.refreshTabs()
        self.setStatus("Started a new project.")
        return

    def ensureProject(self) -> None:
        if self.projectPath is not None:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Welcome")
        dialog.transient(self)
        dialog.resizable(False, False)
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)

        body = ttk.Frame(dialog, padding=20)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Create or open a project to begin.", font=("TkDefaultFont", 11)).pack(pady=(0, 16))

        buttons = ttk.Frame(body)
        buttons.pack()

        def doNew():
            self.newProject()
            if self.projectPath is not None:
                dialog.destroy()
            return

        def doOpen():
            self.openProject()
            if self.projectPath is not None:
                dialog.destroy()
            return

        def doQuit():
            dialog.destroy()
            self.destroy()
            return

        ttk.Button(buttons, text="New Project", command=doNew).pack(side="left", padx=6)
        ttk.Button(buttons, text="Open Project", command=doOpen).pack(side="left", padx=6)
        ttk.Button(buttons, text="Quit", command=doQuit).pack(side="left", padx=6)

        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.grab_set()
        return

    def openProject(self) -> None:
        folder = filedialog.askdirectory(title="Open Project Folder", initialdir=documentsDir())
        if not folder:
            return
        path = os.path.join(folder, PROJECT_FILENAME)
        if not os.path.isfile(path):
            showerror(title="Could not open project", message=f"No {PROJECT_FILENAME} found in the selected folder.")
            return
        try:
            changedSources = loadProject(self.dataManager, path)
        except Exception as error:
            showerror(title="Could not open project", message=str(error))
            return
        self.projectPath = path
        self.title(f"Knowledge Graph Generator - {folder}")
        self.refreshTabs()
        self.setStatus(f"Opened project: {path}")
        if changedSources:
            self.promptRecreate(folder, changedSources)
        return

    def promptRecreate(self, folder: str, changedSources: list) -> None:
        outputs = self._existingOutputs(folder)
        if not outputs:
            showwarning(
                title="Data sources changed",
                message="These data source(s) changed since the project was saved:\n"
                + "\n".join(changedSources)
                + "\n\nNo previous graph output was found to recreate.",
            )
            return

        if not askyesno(
            title="Data sources changed",
            message="These data source(s) changed since the project was saved:\n"
            + "\n".join(changedSources)
            + "\n\nRecreate the existing graph output with the updated data?",
        ):
            return

        try:
            self.dataManager.generateData()
            for filePath, kind in outputs:
                if kind == "csv":
                    nodeFile, edgeFile = filePath
                    self.dataManager.generateNodeFile(nodeFile)
                    self.dataManager.generateEdgeFile(edgeFile)
                else:
                    GRAPH_EXPORTERS[kind](self.dataManager, filePath)
        except Exception as error:
            showerror(title="Could not recreate output", message=str(error))
            return
        if self.projectPath is not None:
            self._writeProject(self.projectPath)
        self.setStatus("Recreated graph output with updated data.")
        return

    def _existingOutputs(self, folder: str) -> list:
        outputs = []
        nodeFile = os.path.join(folder, "nodes.csv")
        edgeFile = os.path.join(folder, "edges.csv")
        if os.path.isfile(nodeFile) and os.path.isfile(edgeFile):
            outputs.append(((nodeFile, edgeFile), "csv"))
        for kind, ext in (("graphml", ".graphml"), ("gexf", ".gexf"), ("gml", ".gml")):
            candidate = os.path.join(folder, f"graph{ext}")
            if os.path.isfile(candidate):
                outputs.append((candidate, kind))
        return outputs

    def saveProject(self) -> None:
        if self.projectPath is None:
            self.saveProjectAs()
            return
        self._writeProject(self.projectPath)
        return

    def saveProjectAs(self) -> None:
        folder = filedialog.askdirectory(title="Save Project Folder", initialdir=documentsDir())
        if not folder:
            return
        path = os.path.join(folder, PROJECT_FILENAME)
        self._writeProject(path)
        self.projectPath = path
        self.title(f"Knowledge Graph Generator - {folder}")
        return

    def _writeProject(self, path: str) -> None:
        try:
            saveProject(self.dataManager, path)
        except Exception as error:
            showerror(title="Could not save project", message=str(error))
            return
        self.setStatus(f"Saved project: {path}")
        return

    def createTabs(self) -> ttk.Notebook:
        tabs = ttk.Notebook(self)
        tabs.grid(column=0, row=0, sticky='nswe')
        return tabs