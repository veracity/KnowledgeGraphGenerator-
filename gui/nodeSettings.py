import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo

from data.nodeDef import NodeDef

def nodeSettings(app):
    nodeItems = {}

    def selectedNode():
        sel = nodeList.selection()
        if len(sel) == 1:
            return nodeItems.get(sel[0])
        return None

    def updateButtons(event=None):
        node = selectedNode()
        if node is not None:
            addEditButton.config(text="Edit Node")
            removeButton.config(state=tk.NORMAL)
        else:
            addEditButton.config(text="Add Node")
            removeButton.config(state=tk.DISABLED)
        return

    def refreshNodes():
        nodeList.delete(*nodeList.get_children())
        nodeItems.clear()
        for n in list(app.dataManager.nodeDefs):
            iid = nodeList.insert('', tk.END, values=(n.field, n.name, n.label))
            nodeItems[iid] = n
        updateButtons()
        return

    def handleChangeTab(event):
        refreshNodes()
        return

    def openNodeDialog(node):
        sources = list(app.dataManager.data)
        if not sources:
            showinfo(title="No data available", message="Add a data source before defining nodes.")
            return

        nameToSource = {d.name: d for d in sources}

        dialog = tk.Toplevel(app)
        dialog.title("Edit Node" if node is not None else "Add Node")
        dialog.transient(app)
        dialog.resizable(False, False)

        body = ttk.Frame(dialog, padding=16)
        body.grid(row=0, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)

        ttk.Label(body, text="Data source").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        sourceVar = tk.StringVar()
        sourceBox = ttk.Combobox(body, textvariable=sourceVar, values=list(nameToSource.keys()), state="readonly", width=28)
        sourceBox.grid(row=0, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(body, text="Field").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        fieldVar = tk.StringVar()
        fieldBox = ttk.Combobox(body, textvariable=fieldVar, values=[], state="readonly", width=28)
        fieldBox.grid(row=1, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(body, text="Name").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        nameVar = tk.StringVar()
        nameEntry = ttk.Entry(body, textvariable=nameVar, width=30)
        nameEntry.grid(row=2, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(body, text="Label").grid(row=3, column=0, sticky="w", padx=4, pady=4)
        labelVar = tk.StringVar()
        labelEntry = ttk.Entry(body, textvariable=labelVar, width=30)
        labelEntry.grid(row=3, column=1, sticky="ew", padx=4, pady=4)

        def refreshFields(event=None):
            d = nameToSource.get(sourceVar.get())
            cols = d.columns if d is not None else []
            fieldBox.config(values=cols)
            if fieldVar.get() not in cols:
                fieldVar.set("")
            return

        sourceBox.bind("<<ComboboxSelected>>", refreshFields)

        if node is not None:
            chosen = None
            for d in sources:
                if node.field in d.columns:
                    chosen = d
                    break
            if chosen is not None:
                sourceVar.set(chosen.name)
            refreshFields()
            fieldVar.set(node.field)
            nameVar.set(node.name)
            labelVar.set(node.label)
        else:
            sourceVar.set(sources[0].name)
            refreshFields()

        def onSave():
            field = fieldVar.get()
            if not field:
                showerror(title="Missing field", message="Please select a data source and field for the node.", parent=dialog)
                return

            name = nameVar.get().strip()
            label = labelVar.get().strip()

            if node is not None:
                app.dataManager.removeNodeDef(node)

            if app.dataManager.findNodeDef(field) is not None:
                showerror(title="Duplicate node", message="A node for this field already exists.", parent=dialog)
                if node is not None:
                    app.dataManager.addNodeDef(node)
                return

            newNode = NodeDef(field, label=label, name=name if name else None)
            app.dataManager.addNodeDef(newNode)
            refreshNodes()
            app.setStatus("Node updated." if node is not None else "Node added.")
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
        sourceBox.focus_set()
        return

    def handleAddEdit():
        openNodeDialog(selectedNode())
        return

    def handleRemove():
        node = selectedNode()
        if node is None:
            return
        app.dataManager.removeNodeDef(node)
        refreshNodes()
        app.setStatus("Node removed.")
        return

    frame = ttk.Frame(app, padding=12)
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(2, weight=1)
    frame.rowconfigure(0, weight=1)

    content = ttk.Frame(frame)
    content.grid(row=0, column=1, sticky="ns")
    content.columnconfigure(0, weight=1)
    content.rowconfigure(1, weight=1)

    nodeLabel = ttk.Label(content, text="Nodes", anchor="center")
    nodeLabel.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))

    nodeList = ttk.Treeview(content, columns=("field", "name", "label"), show="headings")
    nodeList.heading("field", text="Field")
    nodeList.heading("name", text="Name")
    nodeList.heading("label", text="Label")
    nodeList.grid(row=1, column=0, sticky="nsew")

    scroll = ttk.Scrollbar(content, orient="vertical", command=nodeList.yview)
    nodeList.configure(yscrollcommand=scroll.set)
    scroll.grid(row=1, column=1, sticky="ns")

    buttonFrame = ttk.Frame(content)
    buttonFrame.grid(row=1, column=2, sticky="n", padx=(12, 0))

    addEditButton = ttk.Button(buttonFrame, text="Add Node", command=handleAddEdit)
    addEditButton.grid(row=0, column=0, sticky="ew", pady=(0, 4))

    removeButton = ttk.Button(buttonFrame, text="Remove Node", command=handleRemove, state=tk.DISABLED)
    removeButton.grid(row=1, column=0, sticky="ew", pady=4)

    nodeList.bind("<<TreeviewSelect>>", updateButtons)
    app.tabs.bind('<<NotebookTabChanged>>', handleChangeTab, add="+")

    return frame