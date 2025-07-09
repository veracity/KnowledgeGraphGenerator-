"""Project = config + helper methods for build/save/export."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Literal, Tuple

import yaml
import pandas as pd

from .definitions import NodeDef, EdgeDef
from .datasource import DataSource

_DEFAULT_CONFIG_NAME = "project.ngproj"
_DEFAULT_GRAPH_NAME = "network.graphml"
_DEFAULT_GEXF_NAME = "network.gexf"
_DEFAULT_NODES_CSV = "nodes.csv"
_DEFAULT_EDGES_CSV = "edges.csv"

__all__ = ["Project"]


class Project:
    """Encapsulates everything needed to (re)generate a graph."""

    folder: Path
    graph_type: Literal["directed", "undirected"]
    data_sources: Dict[str, DataSource]
    node_defs: List[NodeDef]
    edge_defs: List[EdgeDef]

    def __init__(
        self,
        folder: Path | str,
        *,
        graph_type: Literal["directed", "undirected"] = "directed",
        data_sources: List[DataSource] | None = None,
        node_defs: List[NodeDef] | None = None,
        edge_defs: List[EdgeDef] | None = None,
    ):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)

        self.graph_type: Literal["directed", "undirected"] = graph_type
        self.data_sources: Dict[str, DataSource] = {
            ds.id: ds for ds in (data_sources or [])
        }
        self.node_defs: List[NodeDef] = node_defs or []
        self.edge_defs: List[EdgeDef] = edge_defs or []

    @property
    def config_path(self) -> Path:
        return self.folder / _DEFAULT_CONFIG_NAME

    @property
    def graph_path(self) -> Path:
        return self.folder / _DEFAULT_GRAPH_NAME

    @property
    def gexf_path(self) -> Path:
        return self.folder / _DEFAULT_GEXF_NAME

    @property
    def nodes_csv_path(self) -> Path:
        return self.folder / _DEFAULT_NODES_CSV

    @property
    def edges_csv_path(self) -> Path:
        return self.folder / _DEFAULT_EDGES_CSV

    def build_graph(self):  # noqa: ANN001 – return type is nx.Graph but optional dep
        from .builder import build_graph  # local import avoids heavy deps unless used

        return build_graph(self)

    def export_graphml(self, overwrite: bool = True) -> Path:
        import networkx as nx

        G = self.build_graph()
        if not overwrite and self.graph_path.exists():
            raise FileExistsError(self.graph_path)
        nx.write_graphml(G, self.graph_path)
        return self.graph_path

    def export_gexf(self, overwrite: bool = True) -> Path:
        """Build and save a *.gexf* file next to the project."""
        import networkx as nx

        G = self.build_graph()
        if not overwrite and self.gexf_path.exists():
            raise FileExistsError(self.gexf_path)
        nx.write_gexf(G, self.gexf_path)
        return self.gexf_path

    def export_csv(self, overwrite: bool = True) -> Tuple[Path, Path]:
        """Write ``nodes.csv`` and ``edges.csv`` in the project folder.

        * ``nodes.csv`` - columns: ``id`` + every node attribute that ever
          appears in the graph (missing values become blank).
        * ``edges.csv`` - as produced by ``nx.to_pandas_edgelist`` (source,
          target, weight, plus any edge attributes).
        """
        import networkx as nx

        G = self.build_graph()

        npath, epath = self.nodes_csv_path, self.edges_csv_path
        if (not overwrite) and (npath.exists() or epath.exists()):
            raise FileExistsError("CSV targets already exist – set overwrite=True")

        nodes_records: List[Dict] = [
            {"id": nid, **attrs} for nid, attrs in G.nodes(data=True)
        ]
        df_nodes = pd.DataFrame(nodes_records).sort_values("id")

        df_edges: pd.DataFrame = nx.to_pandas_edgelist(G)
        front = ["source", "target", "weight"]
        other_cols = [c for c in df_edges.columns if c not in front]
        df_edges = df_edges[front + other_cols]

        # Write
        df_nodes.to_csv(npath, index=False)
        df_edges.to_csv(epath, index=False)

        return npath, epath

    def data_changed(self) -> bool:
        return any(ds.has_changed() for ds in self.data_sources.values())

    def to_dict(self) -> Dict:
        return {
            "version": 1,
            "graph_type": self.graph_type,
            "data_sources": [
                ds.to_dict(self.folder) for ds in self.data_sources.values()
            ],
            "node_defs": [asdict(nd) for nd in self.node_defs],
            "edge_defs": [asdict(ed) for ed in self.edge_defs],
        }

    @classmethod
    def from_dict(cls, folder: Path, cfg: Dict) -> "Project":
        ds_index = [DataSource(dsrc["id"], folder / dsrc["path"], dsrc["checksum"]) for dsrc in cfg.get("data_sources", [])]
        node_defs = [NodeDef(**nd) for nd in cfg.get("node_defs", [])]
        edge_defs = [EdgeDef(**ed) for ed in cfg.get("edge_defs", [])]
        return cls(
            folder=folder,
            graph_type=cfg.get("graph_type", "directed"),
            data_sources=ds_index,
            node_defs=node_defs,
            edge_defs=edge_defs,
        )

    def save(self) -> Path:
        """Write `project.ngproj` inside *folder*."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.to_dict(), f, sort_keys=False, allow_unicode=True)
        return self.config_path

    @classmethod
    def open(cls, folder: Path | str) -> "Project":
        folder = Path(folder)
        cfg_path = folder / _DEFAULT_CONFIG_NAME
        if not cfg_path.exists():
            raise FileNotFoundError(cfg_path)
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(folder, data)
