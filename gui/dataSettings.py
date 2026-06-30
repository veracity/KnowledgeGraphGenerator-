import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

from data.table import Table

def dataSettings(app):

    pdTypes = [
        "integer",
        "string",
        "float",
        "boolean"
    ]

    dataItems = {}

    def handleChangeTab(event):
        previous = dataItems.get(dataTreeSettings.focus())

        dataTreeSettings.delete(*dataTreeSettings.get_children())
        dataItems.clear()
        target = None
        for d in app.dataManager.data:
            iid = dataTreeSettings.insert('', tk.END, values=(d.path, d.name, d.type))
            dataItems[iid] = d
            if d == previous:
                target = iid

        if not app.dataManager.data:
            [child.destroy() for child in canvas.winfo_children()]

        children = dataTreeSettings.get_children()
        if target is None and children:
            target = children[0]
        if target is not None:
            dataTreeSettings.focus(target)
            dataTreeSettings.selection_set(target)
        return

    def handleSelect(event):

        def changeType(table: Table, column: str, inType: str, menu: tk.StringVar):
            oldText = menu.get()
            try:
                table.set_column_type(column, inType)
            except Exception:
                showerror(title="Formatting error", message="Cannot change type of field. Make sure the formatting is correct.\nTry removing spaces in number fields.")
                menu.set(oldText)
            return

        [child.destroy() for child in canvas.winfo_children()]

        data = dataItems.get(dataTreeSettings.focus())
        if data is None:
            return

        fieldNameFrame = ttk.Frame(canvas, width=600)

        if (not data.loaded): data.loadData()

        columns = data.df.columns

        firstRow = ttk.Frame(fieldNameFrame, width=600)
        firstRow.grid(column=0, row=0, sticky='news', columnspan=4, pady=(0, 6))
        firstRow.grid_propagate(False)
        ttk.Label(firstRow, text="Field", anchor="w", font=("TkDefaultFont", 11, "bold")).pack(side="left")
        ttk.Label(firstRow, text="Type", anchor="e", font=("TkDefaultFont", 11, "bold")).pack(side="right")

        for j, col in enumerate(columns):
            rowFrame = ttk.Frame(fieldNameFrame, width=600, height=34)
            rowFrame.grid_propagate(False)
            optionText = tk.StringVar()
            optionText.set(data.df.column_type(col))

            fieldLabel = ttk.Label(rowFrame, text=col, anchor="w", font=("TkDefaultFont", 11))
            w = ttk.OptionMenu(rowFrame, optionText, optionText.get(), *pdTypes, command=lambda x, df=data.df, c=col, o=optionText, : changeType(df, c, x, o))

            fieldLabel.pack(side="left")
            w.pack(side="right")

            rowFrame.grid(row=j+1, column=0, sticky='news', pady=2)

        canvas.create_window((0,0), anchor="nw", window=fieldNameFrame)
        canvas.config(scrollregion=canvas.bbox("all"))

        return

    frame = ttk.Frame(app)

    sourceframe = ttk.Frame(frame)
    settingsFrame = ttk.Frame(frame)

    dataLabel = ttk.Label(sourceframe, text = "Data sources", anchor="center")
    dataTreeSettings = ttk.Treeview(sourceframe, columns=("path", "name", "type"), show="headings", height=10)

    dataTreeSettings.heading("path", text="path")
    dataTreeSettings.heading("name", text="name")
    dataTreeSettings.heading("type", text="type")
    dataTreeSettings.column("name", width=480, minwidth=300, anchor="w", stretch=True)
    dataTreeSettings.column("type", width=140, minwidth=100, anchor="center", stretch=False)
    dataTreeSettings["displaycolumns"] = ("name", "type")

    dataLabel.grid(row=0, column=0, columnspan=4, sticky='nwe')
    dataTreeSettings.grid(row=1, column=0, columnspan=4, sticky='nwe')

    app.tabs.bind('<<NotebookTabChanged>>', handleChangeTab, add="+")
    dataTreeSettings.bind('<<TreeviewSelect>>', handleSelect)

    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(2, weight=1)
    frame.rowconfigure(0, weight=1)
    frame.rowconfigure(3, weight=1)

    sourceframe.grid(column=1, row=1, pady=(0, 10))

    # settings
    canvas = tk.Canvas(settingsFrame, width=620, height=420)
    vbar = tk.Scrollbar(settingsFrame, orient="vertical", command=canvas.yview)
    vbar.config(command=canvas.yview)
    vbar.pack(side="right", fill="y")
    canvas.config(yscrollcommand=vbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"), add="+")
    canvas.pack(fill="y")
    settingsFrame.grid(column=1, row=2)

    return frame