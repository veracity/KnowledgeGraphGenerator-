from typing import Set, Union
from data.data import Data
from data.edge import Edge
from data.node import Node
from data.edgeDef import EdgeDef
from data.nodeDef import NodeDef

import pandas as pd

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
        return

    def addNodeDef(self, d: NodeDef) -> None:
        self.__nodeDefs.add(d)
        return
    
    def removeNodeDef(self, d: NodeDef) -> None:
        self.__nodeDefs.remove(d)
        return

    def findNodeDef(self, field: str) -> Union[NodeDef, None]:
        for n in self.__nodeDefs:
            print(f"field: {n.field}, inField: {field}")
            if n.field == field:
                return n 
        return None

    def addEdgeDef(self, d: EdgeDef) -> None:
        self.__edgeDefs.add(d)
        return

    def removeEdgeDef(self, d: EdgeDef) -> None:
        self.__edgeDefs.remove(d)
        return

    def generateData(self) -> None:
        [n.createNodes(list(self.__data)[0]) for n in self.__nodeDefs]
        [e.createEdges(list(self.__data)[0]) for e in self.__edgeDefs]
        return

    def generateNodeFile(self, path: str) -> None:
        [self.__nodes.update(d.nodes) for d in self.__nodeDefs]
        df = pd.DataFrame.from_records([n.as_dict for n in self.__nodes])
        df.to_csv(path, index=False, sep=';', decimal='.')
        return

    def generateEdgeFile(self, path: str) -> None:
        [self.__edges.update(d.edges) for d in self.__edgeDefs]
        df = pd.DataFrame.from_records([e.as_dict for e in self.__edges])
        df.to_csv(path, index=False, sep=';', decimal='.')
        return