"""Convert Project + pandas tables → NetworkX graph."""
from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

import networkx as nx
import pandas as pd

from .definitions import NodeDef
from .errors import ProjectError

if TYPE_CHECKING:
    from .project import Project

__all__ = ["build_graph"]

# ------------------------------------------------------------------

def _node_id(row: pd.Series, ndef: NodeDef) -> str:
    """Compute the node ID for *row* using *ndef*."""
    node_id = row[ndef.id_column]
    if ndef.id_prefix:
        node_id = f"{ndef.id_prefix}{node_id}"
    return node_id

def _resolve_attr(row: pd.Series, spec: Any) -> Any:
    """Return the attribute value for *spec*.

    * If *spec* is a string equal to a column in the row, return that
      column's value.
    * Otherwise return *spec* literally (constant).
    """
    if isinstance(spec, str) and spec in row.index:
        return row[spec]
    return spec

def build_graph(project: "Project", sample_rows: Optional[int] = None) -> nx.Graph:
    """Generate a NetworkX Graph/DiGraph from *project*.  If *sample_rows*
    is given, only the first N rows of each data source are used (for
    preview purposes)."""
    G = nx.DiGraph() if project.graph_type == "directed" else nx.Graph()

    # Map NodeDef.name → NodeDef for quick lookup
    node_map: Dict[str, NodeDef] = {n.name: n for n in project.node_defs}

    # Validate EdgeDefs
    for edef in project.edge_defs:
        if edef.source_node not in node_map or edef.target_node not in node_map:
            raise ProjectError(
                f"EdgeDef '{edef.name}' references unknown NodeDefs "
                f"('{edef.source_node}', '{edef.target_node}')"
            )

    for ds in project.data_sources.values():
        if sample_rows:
            df = ds.df.head(sample_rows)
        else:
            df = ds.df

        for edef in project.edge_defs:
            if edef.data_source_ids and ds.id not in edef.data_source_ids:
                continue  # skip edge for this data source

            src_ndef = node_map[edef.source_node]
            tgt_ndef = node_map[edef.target_node]

            for _, row in df.iterrows():
                u = _node_id(row, src_ndef)
                v = _node_id(row, tgt_ndef)

                # Add/merge nodes first (latest metadata wins)
                for node_id, ndef in ((u, src_ndef), (v, tgt_ndef)):
                    if node_id not in G:
                        attrs = {k: _resolve_attr(row, spec) for k, spec in ndef.metadata.items()}
                        G.add_node(node_id, **attrs)
                    else:
                        for k, spec in ndef.metadata.items():
                            G.nodes[node_id][k] = _resolve_attr(row, spec)

                # Add/merge edge
                if G.has_edge(u, v):
                    G[u][v]["weight"] += 1
                else:
                    edge_attrs = {k: row[col] for k, col in edef.metadata.items()}
                    G.add_edge(u, v, weight=1, **edge_attrs)

    return G