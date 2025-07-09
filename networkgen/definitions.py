from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

__all__ = ["NodeDef", "EdgeDef"]


@dataclass(slots=True)
class NodeDef:
    """Definition for how to build a **node ID** and its attributes."""

    name: str                    # unique handle used by EdgeDefs
    id_column: str           # only one id column (why the fuck would we have more???)
    id_prefix: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)  # node_attr -> column


@dataclass(slots=True)
class EdgeDef:
    """Definition for an edge based on two *NodeDef*s."""

    name: str
    source_node: str             # NodeDef.name for source
    target_node: str             # NodeDef.name for target
    weight: str = "count"         # future‑proof: could be a column name
    metadata: Dict[str, str] = field(default_factory=dict)  # edge_attr -> column
    data_source_ids: Optional[List[str]] = None             # restrict to subset