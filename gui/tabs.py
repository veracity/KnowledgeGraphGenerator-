from pathlib import Path

import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from networkgen.datasource import DataSource  # noqa: E402
matplotlib.use("TkAgg")

import networkx as nx

from networkgen.builder import build_graph
from networkgen.definitions import EdgeDef, NodeDef

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .app import NetGenApp

class BaseTab(ttk.Frame):
    """Common base for all tabs."""

    def __init__(self, master, app: "NetGenApp"):
        super().__init__(master)
        self.app = app

    def refresh(self):
        """Called when project changes - override in subclasses."""
        pass

    def commit(self):
        """Push UI state into the Project object (before save/export)."""
        pass


class DataTab(BaseTab):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._build_widgets()

    def _build_widgets(self):
        frame = self
        # Top button bar
        bar = ttk.Frame(frame)
        bar.pack(fill=tk.X, pady=4)
        ttk.Button(bar, text="Add Source…", command=self.add_source).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Refresh", command=self.update).pack(side=tk.LEFT, padx=2)

        # Listbox of data sources
        self.listbox = tk.Listbox(frame, selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def add_source(self):
        file_path = filedialog.askopenfilename(title="Select data file",
                                               filetypes=[("All supported", "*.csv *.xlsx *.xls *.parquet *.json"),
                                                          ("CSV", "*.csv"),
                                                          ("Excel", "*.xlsx *.xls"),
                                                          ("Parquet", "*.parquet"),
                                                          ("JSON", "*.json")])
        if not file_path:
            return
        if self.app.project is None:
            messagebox.showwarning("No project", "Create or open a project first.")
            return
        path = Path(file_path)
        source_id = path.stem
        # Ensure unique id
        existing_ids = {ds.id for ds in self.app.project.data_sources.values()}
        counter = 1
        base_id = source_id
        while source_id in existing_ids:
            source_id = f"{base_id}_{counter}"
            counter += 1
        ds = DataSource(source_id, path)
        self.app.project.data_sources[source_id] = ds
        self.refresh()

    def remove_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if self.app.project is None:
            return
        key = list(self.app.project.data_sources.keys())[idx]
        del self.app.project.data_sources[key]
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        if self.app.project is None:
            return
        for ds in self.app.project.data_sources.values():
            status = "⚠️ changed" if ds.has_changed() else "✅"
            self.listbox.insert(tk.END, f"{status}  {ds.id}: {ds.path}")

    def update(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if self.app.project is None:
            return
        key = list(self.app.project.data_sources.keys())[idx]
        self.app.project.data_sources[key].update()
        self.refresh()


class NodesTab(BaseTab):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._build_widgets()

    def _build_widgets(self):
        frame = self
        bar = ttk.Frame(frame)
        bar.pack(fill=tk.X, pady=4)
        ttk.Button(bar, text="Add NodeDef", command=self.add_nodedef).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Edit Selected", command=self.edit_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=2)

        columns = ("name", "columns", "prefix", "metadata")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def add_nodedef(self):
        self._open_editor()

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        index = int(sel[0])
        nodedef = list(self.app.project.node_defs if self.app.project else [])[index]
        self._open_editor(nodedef, index)

    def _open_editor(self, nodedef: NodeDef | None = None, index: int | None = None):
        if self.app.project is None or not self.app.project.data_sources:
            messagebox.showwarning("No data", "Add at least one data source first.")
            return
        any_ds = next(iter(self.app.project.data_sources.values()))
        try:
            df = any_ds.df.head(10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load {any_ds.path}: {e}")
            return
        cols = list(df.columns)

        editor = NodeDefEditor(self, cols, nodedef)
        self.wait_window(editor)
        if editor.ok_pressed:
            new_def = editor.result
            if new_def:
                if index is None:
                    self.app.project.node_defs.append(new_def)
                else:
                    self.app.project.node_defs[index] = new_def
            self.refresh()

    def remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        index = int(sel[0])
        del self.app.project.node_defs[index] # type: ignore
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        if self.app.project is None:
            return
        for idx, ndef in enumerate(self.app.project.node_defs):
            self.tree.insert("", tk.END, iid=str(idx), values=(ndef.name, ndef.id_column, ndef.id_prefix or "", str(ndef.metadata)))

class NodeDefEditor(tk.Toplevel):
    def __init__(self, master, columns: list[str], ndef: NodeDef | None):
        super().__init__(master)
        self.title("Node Definition")
        self.ok_pressed = False
        self.result: NodeDef | None = None

        # Variables
        self.name_var = tk.StringVar(value=ndef.name if ndef else "")
        self.id_column_var = tk.StringVar(value=ndef.id_column if ndef else "")
        self.prefix_var = tk.StringVar(value=ndef.id_prefix if ndef else "")
        self.meta_key_var = tk.StringVar()
        self.meta_type_var = tk.StringVar(value="Column")
        self.meta_col_var = tk.StringVar()
        self.meta_const_var = tk.StringVar()

        # Name
        ttk.Label(self, text="Name").pack(anchor=tk.W, padx=5)
        ttk.Entry(self, textvariable=self.name_var, width=40).pack(fill=tk.X, padx=5, pady=2)

        # Columns
        ttk.Label(self, text="ID column").pack(anchor=tk.W, padx=5)
        ttk.Combobox(self, textvariable=self.id_column_var, values=columns, width=40).pack(fill=tk.X, padx=5, pady=2)

        # Prefix
        ttk.Label(self, text="ID prefix (optional)").pack(anchor=tk.W, padx=5)
        ttk.Entry(self, textvariable=self.prefix_var, width=40).pack(fill=tk.X, padx=5, pady=2)

        # Metadata mapping table
        ttk.Label(self, text="Metadata mapping").pack(anchor=tk.W, padx=5, pady=(6, 0))
        meta_frame = ttk.Frame(self)
        meta_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.meta_tree = ttk.Treeview(meta_frame, columns=("key", "value"), show="headings", height=4)
        self.meta_tree.heading("key", text="Attribute")
        self.meta_tree.heading("value", text="Value")
        self.meta_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Populate if editing
        if ndef:
            for k, v in ndef.metadata.items():
                self.meta_tree.insert("", tk.END, values=(k, v))

        # Controls to add mapping
        ctrl = ttk.Frame(meta_frame)
        ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        ttk.Label(ctrl, text="Attr:").pack(anchor=tk.W)
        ttk.Entry(ctrl, textvariable=self.meta_key_var, width=12).pack(pady=2)
        ttk.Label(ctrl, text="Type:").pack(anchor=tk.W)
        type_combo = ttk.Combobox(ctrl, textvariable=self.meta_type_var,
                                  values=("Column", "Constant"), state="readonly", width=12)
        type_combo.pack(pady=2)

        # Column vs Constant widgets
        self.col_combo = ttk.Combobox(ctrl, textvariable=self.meta_col_var,
                                      values=columns, width=12)
        self.const_entry = ttk.Entry(ctrl, textvariable=self.meta_const_var, width=12)
        self.col_combo.pack(pady=2)
        self.const_entry.pack_forget()

        # Trace type changes
        self.meta_type_var.trace_add("write", self._on_type_change)

        ttk.Button(ctrl, text="Add", command=self._add_meta).pack(pady=(6, 2))
        ttk.Button(ctrl, text="Remove", command=self._remove_meta).pack()

        # Buttons
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill=tk.X, pady=4)
        ttk.Button(btn_bar, text="OK", command=self._on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_bar, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

    def _on_type_change(self, *_):
        if self.meta_type_var.get() == "Column":
            self.const_entry.pack_forget()
            self.col_combo.pack(pady=2)
        else:
            self.col_combo.pack_forget()
            self.const_entry.pack(pady=2)

    def _add_meta(self):
        key = self.meta_key_var.get().strip()
        if not key:
            messagebox.showwarning("Invalid", "Attribute name cannot be empty.")
            return
        if self.meta_type_var.get() == "Column":
            spec = self.meta_col_var.get().strip()
            if not spec:
                messagebox.showwarning("Invalid", "Select a column name.")
                return
        else:
            spec = self.meta_const_var.get().strip()
            if not spec:
                messagebox.showwarning("Invalid", "Enter a constant value.")
                return
        self.meta_tree.insert("", tk.END, values=(key, spec))
        # clear inputs
        self.meta_key_var.set("")
        self.meta_col_var.set("")
        self.meta_const_var.set("")

    def _remove_meta(self):
        for iid in self.meta_tree.selection():
            self.meta_tree.delete(iid)

    def _on_ok(self):
        name = self.name_var.get().strip()
        id_col = self.id_column_var.get().strip()
        prefix = self.prefix_var.get().strip() or None
        if not id_col:
            messagebox.showwarning("Invalid", "Each node needs an ID column.")
            return
        metadata = {self.meta_tree.item(iid, "values")[0]: self.meta_tree.item(iid, "values")[1]
                    for iid in self.meta_tree.get_children()}
        self.result = NodeDef(
            name=name, id_column=id_col, id_prefix=prefix, metadata=metadata
        )
        self.ok_pressed = True
        self.destroy()

# class NodeDefEditor(tk.Toplevel):
#     def __init__(self, master, columns: list[str], ndef: NodeDef | None):
#         super().__init__(master)
#         self.title("Node Definition")
#         self.ok_pressed = False
#         self.result: NodeDef | None = None

#         self.name_var = tk.StringVar(value=ndef.name if ndef else "")
#         self.id_column_var = tk.StringVar(value=ndef.id_column if ndef else "")
#         self.prefix_var = tk.StringVar(value=ndef.id_prefix if ndef else "")
#         self.meta_key_var = tk.StringVar()
#         self.meta_col_var = tk.StringVar()

#         # Name
#         ttk.Label(self, text="Name").pack(anchor=tk.W, padx=5)
#         ttk.Entry(self, textvariable=self.name_var, width=40).pack(fill=tk.X, padx=5, pady=2)

#         # Columns
#         ttk.Label(self, text="ID column").pack(anchor=tk.W, padx=5)
#         ttk.Combobox(self, textvariable=self.id_column_var, values=columns, width=40).pack(fill=tk.X, padx=5, pady=2)

#         # Prefix
#         ttk.Label(self, text="ID prefix (optional)").pack(anchor=tk.W, padx=5)
#         ttk.Entry(self, textvariable=self.prefix_var, width=40).pack(fill=tk.X, padx=5, pady=2)

#         # Metadata mapping table
#         ttk.Label(self, text="Metadata mapping").pack(anchor=tk.W, padx=5, pady=(6, 0))
#         meta_frame = ttk.Frame(self)
#         meta_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
#         self.meta_tree = ttk.Treeview(meta_frame, columns=("key", "column"), show="headings", height=4)
#         self.meta_tree.heading("key", text="Attribute")
#         self.meta_tree.heading("column", text="Column")
#         self.meta_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#         # Populate if editing
#         if ndef:
#             for k, v in ndef.metadata.items():
#                 self.meta_tree.insert("", tk.END, values=(k, v))

#         # Controls to add mapping
#         ctrl = ttk.Frame(meta_frame)
#         ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=4)
#         ttk.Label(ctrl, text="Attr:").pack(anchor=tk.W)
#         ttk.Entry(ctrl, textvariable=self.meta_key_var, width=12).pack(pady=2)
#         ttk.Label(ctrl, text="Column:").pack(anchor=tk.W)
#         col_combo = ttk.Combobox(ctrl, textvariable=self.meta_col_var, values=columns, width=12)
#         col_combo.pack(pady=2)
#         ttk.Button(ctrl, text="Add", command=self._add_meta).pack(pady=(6, 2))
#         ttk.Button(ctrl, text="Remove", command=self._remove_meta).pack()

#         # Buttons
#         btn_bar = ttk.Frame(self)
#         btn_bar.pack(fill=tk.X, pady=4)
#         ttk.Button(btn_bar, text="OK", command=self._on_ok).pack(side=tk.RIGHT, padx=5)
#         ttk.Button(btn_bar, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

#     def _add_meta(self):
#         key = self.meta_key_var.get().strip()
#         col = self.meta_col_var.get().strip()
#         if not key or not col:
#             return
#         self.meta_tree.insert("", tk.END, values=(key, col))
#         self.meta_key_var.set("")
#         self.meta_col_var.set("")

#     def _remove_meta(self):
#         sel = self.meta_tree.selection()
#         for iid in sel:
#             self.meta_tree.delete(iid)

#     def _on_ok(self):
#         name = self.name_var.get().strip()
#         id_col = self.id_column_var.get().strip()
#         prefix = self.prefix_var.get().strip() or None
#         metadata = {self.meta_tree.item(iid, "values")[0]: self.meta_tree.item(iid, "values")[1]
#                     for iid in self.meta_tree.get_children()}
#         if not id_col:
#             messagebox.showwarning("Invalid", "Each node needs a id column")
#             return
#         self.result = NodeDef(name=name, id_column=id_col, id_prefix=prefix, metadata=metadata) # type: ignore
#         self.ok_pressed = True
#         self.destroy()


class EdgesTab(BaseTab):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._build_widgets()

    def _build_widgets(self):
        frame = self
        bar = ttk.Frame(frame)
        bar.pack(fill=tk.X, pady=4)
        ttk.Button(bar, text="Add EdgeDef…", command=self.add_edgedef).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Edit Selected…", command=self.edit_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=2)

        columns = ("name", "source", "target", "weight", "metadata")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def add_edgedef(self):
        ndefs = self.app.project.node_defs if self.app.project else []
        self._open_editor(None, ndefs)

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        index = int(sel[0])
        edef = self.app.project.edge_defs[index] if self.app.project else None
        self._open_editor(edef, None, index)

    def remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        index = int(sel[0])
        if self.app.project:
            del self.app.project.edge_defs[index]
        self.refresh()

    def _open_editor(self, edef: EdgeDef | None = None, ndefs: list[NodeDef] | None = None, index: int | None = None):
        if self.app.project is None or not self.app.project.data_sources:
            messagebox.showwarning("No data", "Add at least one data source first.")
            return
        any_ds = next(iter(self.app.project.data_sources.values()))
        try:
            df = any_ds.df.head(10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load {any_ds.path}: {e}")
            return
        cols = list(df.columns)
        name = edef.name if edef else ""
        editor = EdgeDefEditor(self, name , cols, edef, ndefs)
        self.wait_window(editor)
        if editor.ok_pressed:
            new_def = editor.result
            if new_def:
                if index is None:
                    self.app.project.edge_defs.append(new_def)
                else:
                    self.app.project.edge_defs[index] = new_def
            self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        if self.app.project is None:
            return
        for idx, edef in enumerate(self.app.project.edge_defs):
            self.tree.insert("", tk.END, iid=str(idx),
                             values=(edef.name, edef.source_node, edef.target_node, edef.weight, str(edef.metadata)))


class EdgeDefEditor(tk.Toplevel):
    def __init__(self, master, name: str, columns: list[str], edef: EdgeDef | None, ndefs: list[NodeDef] | None):
        super().__init__(master)
        self.title("Edge Definition")
        self.ok_pressed = False
        self.result: EdgeDef | None = None

        self.name_var = tk.StringVar(value=name)
        self.source_var = tk.StringVar(value=edef.source_node if edef else (columns[0] if columns else ""))
        self.target_var = tk.StringVar(value=edef.target_node if edef else (columns[1] if len(columns) > 1 else ""))
        self.weight_var = tk.StringVar(value=edef.weight if edef else "count")
        self.meta_key_var = tk.StringVar()
        self.meta_col_var = tk.StringVar()

        ndef_cols = set(n.name for n in ndefs or []).difference( set([self.source_var.get(), self.target_var.get()]))

        # Source/target selectors
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.name_var).grid(row=0, column=1, sticky=tk.EW)
        ttk.Label(frame, text="Source column:").grid(row=1, column=0, sticky=tk.W)
        ttk.Combobox(frame, textvariable=self.source_var, values=list(ndef_cols)).grid(row=1, column=1, sticky=tk.EW, pady=(4, 0))
        ttk.Label(frame, text="Target column:").grid(row=2, column=0, sticky=tk.W, pady=(4, 0))
        ttk.Combobox(frame, textvariable=self.target_var, values=list(ndef_cols)).grid(row=2, column=1, sticky=tk.EW, pady=(4, 0))

        frame.columnconfigure(1, weight=1)

        # Metadata mapping
        ttk.Label(self, text="Metadata mapping").pack(anchor=tk.W, padx=5, pady=(6, 0))
        meta_frame = ttk.Frame(self)
        meta_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.meta_tree = ttk.Treeview(meta_frame, columns=("key", "column"), show="headings", height=4)
        self.meta_tree.heading("key", text="Attribute")
        self.meta_tree.heading("column", text="Column")
        self.meta_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if edef:
            for k, v in edef.metadata.items():
                self.meta_tree.insert("", tk.END, values=(k, v))

        ctrl = ttk.Frame(meta_frame)
        ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        ttk.Label(ctrl, text="Attr:").pack()
        ttk.Entry(ctrl, textvariable=self.meta_key_var, width=12).pack(pady=2)
        ttk.Label(ctrl, text="Column:").pack()
        col_combo = ttk.Combobox(ctrl, textvariable=self.meta_col_var, values=columns, width=12)
        col_combo.pack(pady=2)
        ttk.Button(ctrl, text="Add", command=self._add_meta).pack(pady=(6, 2))
        ttk.Button(ctrl, text="Remove", command=self._remove_meta).pack()

        # Buttons
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill=tk.X, pady=4)
        ttk.Button(btn_bar, text="OK", command=self._on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_bar, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

    def _add_meta(self):
        key = self.meta_key_var.get().strip()
        col = self.meta_col_var.get().strip()
        if not key or not col:
            return
        self.meta_tree.insert("", tk.END, values=(key, col))
        self.meta_key_var.set("")
        self.meta_col_var.set("")

    def _remove_meta(self):
        sel = self.meta_tree.selection()
        for iid in sel:
            self.meta_tree.delete(iid)

    def _on_ok(self):
        source = self.source_var.get().strip()
        target = self.target_var.get().strip()
        name = self.name_var.get().strip()
        if not source or not target:
            messagebox.showwarning("Invalid", "Source and target columns are required.")
            return
        
        if source == target:
            messagebox.showwarning("Invalid", "Source and target columns cannot be the same.")
            return
        
        metadata = {self.meta_tree.item(iid, "values")[0]: self.meta_tree.item(iid, "values")[1]
                    for iid in self.meta_tree.get_children()}
        self.result = EdgeDef(name=name, source_node=source, target_node=target, metadata=metadata)
        self.ok_pressed = True
        self.destroy()


class PreviewTab(BaseTab):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.figure = plt.Figure(figsize=(5, 4)) # type: ignore
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        ttk.Button(self, text="Refresh Preview", command=self.refresh).pack(pady=4)

    def refresh(self):
        self.ax.clear()
        if self.app.project is None or not self.app.project.data_sources:
            self.ax.set_title("No data")
            self.canvas.draw()
            return
        # Build in a worker thread so UI stays responsive
        threading.Thread(target=self._build_and_draw, daemon=True).start()

    def _build_and_draw(self):
        try:
            if self.app.project:
                G = build_graph(self.app.project)
        except Exception as e:
            self.ax.clear()
            self.ax.text(0.5, 0.5, f"Error: {e}", ha="center", va="center")
            self.canvas.draw()
            return
        pos = nx.spring_layout(G, k=0.5, seed=42)
        self.ax.clear()
        nx.draw(G, pos, ax=self.ax, with_labels=False, node_size=50)
        self.ax.set_title(f"Preview ({len(G)} nodes, {G.number_of_edges()} edges)")
        self.canvas.draw()

    def commit(self):
        pass


class ExportTab(BaseTab):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._build_widgets()

    def _build_widgets(self):
        ttk.Label(self, text="Export options").pack(anchor=tk.W, padx=5, pady=(5, 0))
        ttk.Button(self, text="Build & save GraphML", command=self.export_graphml).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Button(self, text="Build & save nodes/edges CSV", command=self.export_csv).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Button(self, text="Build & save GEXF", command=self.export_gexf).pack(anchor=tk.W, padx=5, pady=2)

    def refresh(self):
        pass

    def commit(self):
        pass

    def export_graphml(self):
        self._export("graphml")

    def export_gexf(self):
        self._export("gexf")

    def export_csv(self):
        self._export("csv")

    def _export(self, fmt: str):
        if self.app.project is None:
            messagebox.showwarning("No project", "Create or open a project first.")
            return
        self.app._collect_tabs_into_project()
        try:
            if fmt == "graphml":
                path = self.app.project.export_graphml()
            elif fmt == "gexf":
                path = self.app.project.export_gexf()
            elif fmt == "csv":
                paths = self.app.project.export_csv()
                messagebox.showinfo("Exported", f"CSV files written:\n{paths[0]}\n{paths[1]}")
                return
            else:
                raise ValueError(fmt)
            messagebox.showinfo("Exported", f"{fmt.upper()} written to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")