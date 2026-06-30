import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
from data.edgeDef import EdgeDef
from data.nodeDef import NodeDef

def edgeSettings(app):
    edgeItems = {}

    def selectedEdge():
        sel = edgeList.selection()
        if len(sel) == 1:
            return edgeItems.get(sel[0])
        return None

    def updateButtons(event=None):
        edge = selectedEdge()
        if edge is not None:
            addEditButton.config(text="Edit Edge")
            removeButton.config(state=tk.NORMAL)
        else:
            addEditButton.config(text="Add Edge")
            removeButton.config(state=tk.DISABLED)
        return

    def refreshEdges():
        edgeList.delete(*edgeList.get_children())
        edgeItems.clear()
        for e in list(app.dataManager.edgeDefs):
            iid = edgeList.insert('', tk.END, values=(e.source.name, e.target.name, "Yes" if e.directed else "No"))
            edgeItems[iid] = e
        updateButtons()
        return

    def handleChangeTab(event):
        refreshEdges()
        return

    def edgeExists(source: NodeDef, target: NodeDef) -> bool:
        for e in app.dataManager.edgeDefs:
            if e.source == source and e.target == target:
                return True
        return False

    def openEdgeDialog(edge):
        sources = list(app.dataManager.data)
        nodeDefs = list(app.dataManager.nodeDefs)
        if len(nodeDefs) < 2:
            showinfo(title="Not enough nodes", message="You need at least two defined nodes to create an edge.")
            return
        if not sources:
            showinfo(title="No data available", message="Add a data source before defining edges.")
            return

        nameToSource = {d.name: d for d in sources}
        nameToNode = {n.name: n for n in nodeDefs}

        dialog = tk.Toplevel(app)
        dialog.title("Edit Edge" if edge is not None else "Add Edge")
        dialog.transient(app)
        dialog.resizable(False, False)

        body = ttk.Frame(dialog, padding=16)
        body.grid(row=0, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)

        ttk.Label(body, text="Data source").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        dsVar = tk.StringVar()
        dsBox = ttk.Combobox(body, textvariable=dsVar, values=list(nameToSource.keys()), state="readonly", width=28)
        dsBox.grid(row=0, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(body, text="Source node").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        sourceVar = tk.StringVar()
        sourceBox = ttk.Combobox(body, textvariable=sourceVar, values=[], state="readonly", width=28)
        sourceBox.grid(row=1, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(body, text="Target node").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        targetVar = tk.StringVar()
        targetBox = ttk.Combobox(body, textvariable=targetVar, values=[], state="readonly", width=28)
        targetBox.grid(row=2, column=1, sticky="ew", padx=4, pady=4)

        directedVar = tk.IntVar()
        directedCheck = ttk.Checkbutton(body, text="Directed", variable=directedVar)
        directedCheck.grid(row=3, column=0, columnspan=2, sticky="w", padx=4, pady=4)

        def nodesForSource(d):
            cols = set(d.columns) if d is not None else set()
            return [n.name for n in nodeDefs if n.field in cols]

        def refreshNodeOptions(event=None):
            names = nodesForSource(nameToSource.get(dsVar.get()))
            sourceBox.config(values=names)
            targetBox.config(values=names)
            if sourceVar.get() not in names:
                sourceVar.set("")
            if targetVar.get() not in names:
                targetVar.set("")
            return

        dsBox.bind("<<ComboboxSelected>>", refreshNodeOptions)

        if edge is not None:
            chosen = None
            for d in sources:
                cols = set(d.columns)
                if edge.source.field in cols and edge.target.field in cols:
                    chosen = d
                    break
            if chosen is not None:
                dsVar.set(chosen.name)
            refreshNodeOptions()
            sourceVar.set(edge.source.name)
            targetVar.set(edge.target.name)
            directedVar.set(1 if edge.directed else 0)
        else:
            dsVar.set(sources[0].name)
            refreshNodeOptions()

        def onSave():
            sname = sourceVar.get()
            tname = targetVar.get()
            if not sname or not tname:
                showerror(title="Missing fields", message="Please select both a source and a target node.", parent=dialog)
                return
            if sname == tname:
                showerror(title="Invalid edge", message="Source and target must be different nodes.", parent=dialog)
                return

            source = nameToNode.get(sname)
            target = nameToNode.get(tname)
            directed = bool(directedVar.get())

            if edge is not None:
                app.dataManager.removeEdgeDef(edge)

            if edgeExists(source, target):
                showerror(title="Duplicate edge", message="An edge between these nodes already exists.", parent=dialog)
                if edge is not None:
                    app.dataManager.addEdgeDef(edge)
                return

            newEdge = EdgeDef(source, target, directed, name=source.name)
            app.dataManager.addEdgeDef(newEdge)
            refreshEdges()
            app.setStatus("Edge updated." if edge is not None else "Edge added.")
            dialog.destroy()
            return

        buttonRow = ttk.Frame(body)
        buttonRow.grid(row=4, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttonRow, text="Cancel", command=dialog.destroy).pack(side="right", padx=4)
        ttk.Button(buttonRow, text="Save", command=onSave).pack(side="right", padx=4)

        dialog.update_idletasks()
        x = app.winfo_rootx() + (app.winfo_width() - dialog.winfo_width()) // 2
        y = app.winfo_rooty() + (app.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        dialog.grab_set()
        dsBox.focus_set()
        return

    def handleAddEdit():
        openEdgeDialog(selectedEdge())
        return

    def handleRemove():
        edge = selectedEdge()
        if edge is None:
            return
        app.dataManager.removeEdgeDef(edge)
        refreshEdges()
        app.setStatus("Edge removed.")
        return

    frame = ttk.Frame(app, padding=12)
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(2, weight=1)
    frame.rowconfigure(0, weight=1)

    content = ttk.Frame(frame)
    content.grid(row=0, column=1, sticky="ns")
    content.columnconfigure(0, weight=1)
    content.rowconfigure(1, weight=1)

    edgeLabel = ttk.Label(content, text="Edges", anchor="center")
    edgeLabel.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))

    edgeList = ttk.Treeview(content, columns=("source", "target", "directed"), show="headings")
    edgeList.heading("source", text="Source")
    edgeList.heading("target", text="Target")
    edgeList.heading("directed", text="Directed")
    edgeList.grid(row=1, column=0, sticky="nsew")

    scroll = ttk.Scrollbar(content, orient="vertical", command=edgeList.yview)
    edgeList.configure(yscrollcommand=scroll.set)
    scroll.grid(row=1, column=1, sticky="ns")

    buttonFrame = ttk.Frame(content)
    buttonFrame.grid(row=1, column=2, sticky="n", padx=(12, 0))

    addEditButton = ttk.Button(buttonFrame, text="Add Edge", command=handleAddEdit)
    addEditButton.grid(row=0, column=0, sticky="ew", pady=(0, 4))

    removeButton = ttk.Button(buttonFrame, text="Remove Edge", command=handleRemove, state=tk.DISABLED)
    removeButton.grid(row=1, column=0, sticky="ew", pady=4)

    edgeList.bind("<<TreeviewSelect>>", updateButtons)
    app.tabs.bind('<<NotebookTabChanged>>', handleChangeTab, add="+")

    return frame