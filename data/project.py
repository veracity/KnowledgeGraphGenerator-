import json
import os

import yaml

from data.data import Data
from data.nodeDef import NodeDef
from data.edgeDef import EdgeDef

PROJECT_VERSION = 1


def saveProject(dataManager, path: str) -> None:
    """Serialize the current DataManager state to a .ngproj (JSON) file."""

    data_sources = [
        {
            "id": d.id,
            "path": d.path,
            "sheet": d.sheet,
            "checksum": d.checksum,
        }
        for d in dataManager.data
    ]

    node_defs = [
        {
            "name": n.name,
            "id_column": n.field,
            "id_prefix": n.id_prefix,
            "metadata": n.metadata,
        }
        for n in dataManager.nodeDefs
    ]

    edge_defs = [
        {
            "name": e.name,
            "source_node": e.source.name,
            "target_node": e.target.name,
            "weight": e.weight,
            "metadata": e.metadata,
            "data_source_ids": e.data_source_ids,
        }
        for e in dataManager.edgeDefs
    ]

    edges = list(dataManager.edgeDefs)
    if edges and all(not e.directed for e in edges):
        graph_type = "undirected"
    elif edges:
        graph_type = "directed"
    else:
        graph_type = dataManager.graph_type

    project = {
        "version": PROJECT_VERSION,
        "graph_type": graph_type,
        "data_sources": data_sources,
        "node_defs": node_defs,
        "edge_defs": edge_defs,
        "output": {
            "node_file": dataManager.nodeOutput,
            "edge_file": dataManager.edgeOutput,
        },
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(project, f, indent=2)
    return


def loadProject(dataManager, path: str) -> None:
    """Load a .ngproj file and rebuild the DataManager state from it.

    Supports both the current JSON format and the older YAML format. Since
    JSON is a subset of YAML, ``yaml.safe_load`` parses both transparently.
    """

    with open(path, "r", encoding="utf-8") as f:
        project = yaml.safe_load(f)

    if not isinstance(project, dict):
        raise ValueError("Invalid project file: expected a mapping at the top level.")

    dataManager.clear()

    graph_type = project.get("graph_type", "directed")
    directed = graph_type == "directed"
    dataManager.graph_type = graph_type

    base_dir = os.path.dirname(os.path.abspath(path))

    changed_sources = []
    for ds in project.get("data_sources", []):
        ds_path = ds.get("path", "")
        resolved = ds_path
        if ds_path and not os.path.isabs(ds_path) and not os.path.exists(ds_path):
            candidate = os.path.join(base_dir, ds_path)
            if os.path.exists(candidate):
                resolved = candidate
        data = Data(resolved, sheet=ds.get("sheet"))
        dataManager.addData(data)

        stored_checksum = ds.get("checksum")
        if stored_checksum and os.path.exists(resolved):
            current_checksum = data.checksum
            if current_checksum and current_checksum != stored_checksum:
                changed_sources.append(data.name)

    name_to_nodedef = {}
    for nd in project.get("node_defs", []):
        metadata = nd.get("metadata", {}) or {}
        node = NodeDef(
            nd.get("id_column", ""),
            label=metadata.get("Label", ""),
            name=nd.get("name"),
            id_prefix=nd.get("id_prefix"),
            metadata=metadata,
        )
        dataManager.addNodeDef(node)
        name_to_nodedef[node.name] = node

    for ed in project.get("edge_defs", []):
        source = name_to_nodedef.get(ed.get("source_node"))
        target = name_to_nodedef.get(ed.get("target_node"))
        if source is None or target is None:
            continue
        edge = EdgeDef(
            source,
            target,
            directed,
            name=ed.get("name"),
            weight=ed.get("weight", "count"),
            metadata=ed.get("metadata", {}) or {},
            data_source_ids=ed.get("data_source_ids"),
        )
        dataManager.addEdgeDef(edge)

    output = project.get("output", {}) or {}
    dataManager.nodeOutput = output.get("node_file", "")
    dataManager.edgeOutput = output.get("edge_file", "")
    return changed_sources
