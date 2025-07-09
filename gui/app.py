from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gui.tabs import DataTab, EdgesTab, ExportTab, NodesTab, PreviewTab

# networkgen imports
from networkgen.errors import ProjectError
from networkgen.project import Project  # type: ignore


class NetGenApp(ttk.Frame):
    """Main application window with tabs."""

    SAMPLE_ROWS_DEFAULT = 100

    def __init__(self, master: tk.Tk | None = None):
        super().__init__(master)
        if not master:
            exit(1)
        self.master.title("Network Graph Generator") # type: ignore
        self.master.geometry("1000x700") # type: ignore
        self.pack(fill=tk.BOTH, expand=True)

        # Current Project (may be None if new / unsaved)
        self.project: Optional[Project] = None
        self.project_path_var = tk.StringVar(value="<no project loaded>")

        self.create_menu()
        self.create_status_bar()
        self.create_tabs()

    def create_menu(self):
        menu = tk.Menu(self.master)
        self.master.config(menu=menu) # type: ignore

        file_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project…", command=self.new_project)
        file_menu.add_command(label="Open Project Folder…", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_command(label="Save Project As…", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

    def create_status_bar(self):
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Label(status_frame, textvariable=self.project_path_var).pack(anchor=tk.W, padx=5, pady=2)

    # ---------- Tabs ----------------------------------------------------------------
    def create_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Instantiate tab frames
        self.data_tab = DataTab(self.notebook, self)
        self.nodes_tab = NodesTab(self.notebook, self)
        self.edges_tab = EdgesTab(self.notebook, self)
        self.preview_tab = PreviewTab(self.notebook, self)
        self.export_tab = ExportTab(self.notebook, self)

        # Add to notebook
        self.notebook.add(self.data_tab, text="Data")
        self.notebook.add(self.nodes_tab, text="Nodes")
        self.notebook.add(self.edges_tab, text="Edges")
        self.notebook.add(self.preview_tab, text="Preview")
        self.notebook.add(self.export_tab, text="Export")

    # ---------- Project actions -----------------------------------------------------
    def new_project(self):
        folder = filedialog.askdirectory(title="Select (or create) project folder")
        if not folder:
            return
        folder_path = Path(folder)
        folder_path.mkdir(parents=True, exist_ok=True)
        self.project = Project(folder_path)
        self.project_path_var.set(str(self.project.folder))
        self.refresh_all_tabs()

    def open_project(self):
        folder = filedialog.askdirectory(title="Choose project folder (containing project.ngproj)")
        if not folder:
            return
        try:
            self.project = Project.open(Path(folder))
        except ProjectError as e:
            messagebox.showerror("Error", str(e))
            return
        self.project_path_var.set(str(self.project.folder))
        self.refresh_all_tabs()

    def save_project(self):
        if self.project is None:
            self.save_project_as()
            return
        self._collect_tabs_into_project()
        try:
            self.project.save()
            messagebox.showinfo("Saved", "Project saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def save_project_as(self):
        folder = filedialog.askdirectory(title="Choose folder to save project")
        if not folder:
            return
        folder_path = Path(folder)
        folder_path.mkdir(parents=True, exist_ok=True)
        if self.project is None:
            self.project = Project(folder_path)
        else:
            self.project.folder = folder_path
        self.project_path_var.set(str(folder_path))
        self.save_project()

    def refresh_all_tabs(self):
        for tab in (self.data_tab, self.nodes_tab, self.edges_tab, self.preview_tab, self.export_tab):
            tab.refresh()

    def _collect_tabs_into_project(self):
        """Pull changes from UI tabs into the Project object before saving/export."""
        if self.project is None:
            return
        self.data_tab.commit()
        self.nodes_tab.commit()
        self.edges_tab.commit()