from typing import Set, Union
from data.data import Data
from data.edge import Edge
from data.node import Node
from data.edgeDef import EdgeDef
from data.nodeDef import NodeDef

import csv
import xml.etree.ElementTree as ET

class DataManager:
    __nodeDefs: Set[NodeDef]
    __edgeDefs: Set[EdgeDef]
    __nodes: Set[Node]
    __edges: Set[Edge]
    __data: Set[Data]

    def __init__(self) -> None:
        self.__nodeDefs = set()
        self.__edgeDefs = set()
        self.__nodes = set()
        self.__edges = set()
        self.__data = set()
        self.__graph_type = "directed"
        self.__node_output = ""
        self.__edge_output = ""
        return

    @property
    def graph_type(self) -> str:
        return self.__graph_type

    @graph_type.setter
    def graph_type(self, value: str) -> None:
        self.__graph_type = value

    @property
    def nodeOutput(self) -> str:
        return self.__node_output

    @nodeOutput.setter
    def nodeOutput(self, value: str) -> None:
        self.__node_output = value

    @property
    def edgeOutput(self) -> str:
        return self.__edge_output

    @edgeOutput.setter
    def edgeOutput(self, value: str) -> None:
        self.__edge_output = value

    def clear(self) -> None:
        self.__nodeDefs = set()
        self.__edgeDefs = set()
        self.__nodes = set()
        self.__edges = set()
        self.__data = set()
        self.__graph_type = "directed"
        self.__node_output = ""
        self.__edge_output = ""
        return

    @property
    def data(self) -> Set[Data]:
        return self.__data

    @property
    def nodeDefs(self) -> Set[NodeDef]:
        return self.__nodeDefs

    @property
    def edgeDefs(self) -> Set[EdgeDef]:
        return self.__edgeDefs

    def addData(self, data: Data) -> None:
        self.__data.add(data)
        return

    def findData(self, path: str, name: str, type: str) -> Union[Data, None]:
        for d in self.__data:
            if d.name == name and d.path == path and d.type == type:
                return d

    def removeData(self, data: Data) -> None:
        self.__data.remove(data)
        self.__nodeDefs = set()
        self.__edgeDefs = set()
        self.__nodes = set()
        self.__edges = set()
        return

    def addNodeDef(self, d: NodeDef) -> None:
        self.__nodeDefs.add(d)
        return
    
    def removeNodeDef(self, d: NodeDef) -> None:
        self.__nodeDefs.remove(d)
        return

    def findNodeDef(self, field: str) -> Union[NodeDef, None]:
        for n in self.__nodeDefs:
            if n.field == field:
                return n 
        return None

    def addEdgeDef(self, d: EdgeDef) -> None:
        self.__edgeDefs.add(d)
        return

    def removeEdgeDef(self, d: EdgeDef) -> None:
        self.__edgeDefs.remove(d)
        return

    def findEdgeDef(self, source: str, target: str) -> Union[EdgeDef, None]:
        sourceNode = self.findNodeDef(source)
        targetNode = self.findNodeDef(target)

        for e in self.__edgeDefs:
            if e.source == sourceNode and e.target == targetNode:
                return e

        return None

    def generateData(self) -> None:
        source = list(self.__data)[0]
        if not source.loaded:
            source.loadData()
        [n.createNodes(source) for n in self.__nodeDefs]
        [e.createEdges(source) for e in self.__edgeDefs]
        return

    def generateNodeFile(self, path: str) -> None:
        [self.__nodes.update(d.nodes) for d in self.__nodeDefs]
        self._writeCsv(path, [n.as_dict for n in self.__nodes])
        return

    def generateEdgeFile(self, path: str) -> None:
        [self.__edges.update(d.edges) for d in self.__edgeDefs]
        self._writeCsv(path, [e.as_dict for e in self.__edges])
        return

    @staticmethod
    def _writeCsv(path: str, records: list) -> None:
        if not records:
            open(path, "w", encoding="utf-8").close()
            return
        fieldnames = list(records[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(records)
        return

    def _collectGraph(self):
        nodes = set()
        edges = set()
        [nodes.update(d.nodes) for d in self.__nodeDefs]
        [edges.update(d.edges) for d in self.__edgeDefs]
        return nodes, edges

    @staticmethod
    def _gmlEscape(value) -> str:
        return str(value).replace("&", "&amp;").replace('"', "&quot;")

    def generateGraphmlFile(self, path: str) -> None:
        nodes, edges = self._collectGraph()

        ns = "http://graphml.graphdrawing.org/xmlns"
        ET.register_namespace("", ns)
        graphml = ET.Element(f"{{{ns}}}graphml")

        keys = [
            ("d_label", "node", "label", "string"),
            ("d_field", "node", "field", "string"),
            ("e_label", "edge", "label", "string"),
            ("e_weight", "edge", "weight", "double"),
        ]
        for keyId, domain, name, attrType in keys:
            key = ET.SubElement(graphml, f"{{{ns}}}key")
            key.set("id", keyId)
            key.set("for", domain)
            key.set("attr.name", name)
            key.set("attr.type", attrType)

        graph = ET.SubElement(graphml, f"{{{ns}}}graph")
        graph.set("edgedefault", "directed" if self.__graph_type == "directed" else "undirected")

        for n in nodes:
            node = ET.SubElement(graph, f"{{{ns}}}node")
            node.set("id", n.id)
            labelData = ET.SubElement(node, f"{{{ns}}}data")
            labelData.set("key", "d_label")
            labelData.text = str(n.name)
            fieldData = ET.SubElement(node, f"{{{ns}}}data")
            fieldData.set("key", "d_field")
            fieldData.text = str(n.field)

        for i, e in enumerate(edges):
            edge = ET.SubElement(graph, f"{{{ns}}}edge")
            edge.set("id", f"e{i}")
            edge.set("source", e.source.id)
            edge.set("target", e.target.id)
            edge.set("directed", "true" if e.directed else "false")
            labelData = ET.SubElement(edge, f"{{{ns}}}data")
            labelData.set("key", "e_label")
            labelData.text = str(e.as_dict["Label"])
            weightData = ET.SubElement(edge, f"{{{ns}}}data")
            weightData.set("key", "e_weight")
            weightData.text = str(e.weight)

        tree = ET.ElementTree(graphml)
        ET.indent(tree, space="  ")
        tree.write(path, encoding="UTF-8", xml_declaration=True)
        return

    def generateGexfFile(self, path: str) -> None:
        nodes, edges = self._collectGraph()

        ns = "http://www.gexf.net/1.2draft"
        ET.register_namespace("", ns)
        gexf = ET.Element(f"{{{ns}}}gexf")
        gexf.set("version", "1.2")

        graph = ET.SubElement(gexf, f"{{{ns}}}graph")
        graph.set("mode", "static")
        graph.set("defaultedgetype", "directed" if self.__graph_type == "directed" else "undirected")

        attributes = ET.SubElement(graph, f"{{{ns}}}attributes")
        attributes.set("class", "node")
        attribute = ET.SubElement(attributes, f"{{{ns}}}attribute")
        attribute.set("id", "0")
        attribute.set("title", "field")
        attribute.set("type", "string")

        nodesEl = ET.SubElement(graph, f"{{{ns}}}nodes")
        for n in nodes:
            node = ET.SubElement(nodesEl, f"{{{ns}}}node")
            node.set("id", n.id)
            node.set("label", str(n.name))
            attvalues = ET.SubElement(node, f"{{{ns}}}attvalues")
            attvalue = ET.SubElement(attvalues, f"{{{ns}}}attvalue")
            attvalue.set("for", "0")
            attvalue.set("value", str(n.field))

        edgesEl = ET.SubElement(graph, f"{{{ns}}}edges")
        for i, e in enumerate(edges):
            edge = ET.SubElement(edgesEl, f"{{{ns}}}edge")
            edge.set("id", str(i))
            edge.set("source", e.source.id)
            edge.set("target", e.target.id)
            edge.set("type", "directed" if e.directed else "undirected")
            edge.set("weight", str(e.weight))
            label = str(e.as_dict["Label"])
            if label:
                edge.set("label", label)

        tree = ET.ElementTree(gexf)
        ET.indent(tree, space="  ")
        tree.write(path, encoding="UTF-8", xml_declaration=True)
        return

    def generateGmlFile(self, path: str) -> None:
        nodes, edges = self._collectGraph()

        indexMap = {}
        lines = ["graph [", f"  directed {1 if self.__graph_type == 'directed' else 0}"]

        for i, n in enumerate(nodes):
            indexMap[n.id] = i
            lines.append("  node [")
            lines.append(f"    id {i}")
            lines.append(f'    label "{self._gmlEscape(n.name)}"')
            lines.append(f'    field "{self._gmlEscape(n.field)}"')
            lines.append("  ]")

        for e in edges:
            lines.append("  edge [")
            lines.append(f"    source {indexMap[e.source.id]}")
            lines.append(f"    target {indexMap[e.target.id]}")
            label = str(e.as_dict["Label"])
            if label:
                lines.append(f'    label "{self._gmlEscape(label)}"')
            lines.append(f"    weight {e.weight}")
            lines.append("  ]")

        lines.append("]")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return