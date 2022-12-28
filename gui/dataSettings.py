import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

from pandas import DataFrame
from data.data import Data

def dataSettings(app):

    pdTypes = [
        "integer",
        "string",
        "float",
        "boolean"
    ]

    def handleChangeTab(event):
        dataTreeSettings.delete(*dataTreeSettings.get_children())
        for d in app.dataManager.data:
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

        dataList = list(app.dataManager.data)

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

    frame = ttk.Frame(app)

    sourceframe = ttk.Frame(frame)
    settingsFrame = ttk.Frame(frame)

    dataLabel = tk.Label(sourceframe, text = "Data sources", anchor="center")
    dataTreeSettings = ttk.Treeview(sourceframe, columns=("path", "name", "type"), show="headings")

    dataTreeSettings.heading("path", text="path")
    dataTreeSettings.heading("name", text="name")
    dataTreeSettings.heading("type", text="type")

    dataLabel.grid(row=0, column=0, columnspan=4, sticky='nwe')
    dataTreeSettings.grid(row=1, column=0, columnspan=4, sticky='nwe')

    app.tabs.bind('<<NotebookTabChanged>>', handleChangeTab, add="+")
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

    return frame