"""Build a lightweight sub‑graph from the first *n* rows of every table."""
from __future__ import annotations

from typing import Any

import networkx as nx

from networkgen.project import Project

from .builder import build_graph

__all__ = ["build_preview_graph", "plot_preview"]


PREVIEW_ROWS = 100


def build_preview_graph(project: Project, rows: int = PREVIEW_ROWS):
    """Like *build_graph* but truncates each DataFrame first."""
    # Monkey‑patch: temporarily replace each ds.df with head(rows)
    orig_dfs = {}
    try:
        for ds in project.data_sources.values():
            if ds._df is None:
                ds.df  # trigger load
            orig_dfs[ds.id] = ds._df
            ds._df = ds._df.head(rows)  # type: ignore[index]
        return build_graph(project)
    finally:
        # Restore full DataFrames
        for ds in project.data_sources.values():
            ds._df = orig_dfs[ds.id]

def plot_preview(G: nx.Graph, ax=None, **kwargs: Any):  # pragma: no cover
    import matplotlib.pyplot as plt

    if ax is None:
        fig, ax = plt.subplots()
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx(G, pos=pos, ax=ax, with_labels=False, node_size=50)
    ax.set_xticks([])
    ax.set_yticks([])
    return ax
