from typing import Set
from data.data import Data
from data.edge import Edge
from data.nodeDef import NodeDef

class EdgeDef:
    __source: NodeDef
    __target: NodeDef
    __directed: bool
    __edges: Set[Edge]
    __label: str

    def __init__(self, source: NodeDef, target: NodeDef, directed: bool, label: str = "", name: str = None, weight: str = "count", metadata: dict = None, data_source_ids=None) -> None:
        self.__source = source
        self.__target = target
        self.__directed = directed
        self.__edges = set()
        self.__label = label
        self.__name = name if name is not None else str(source)
        self.__weight = weight
        self.__metadata = dict(metadata) if metadata is not None else {}
        self.__data_source_ids = data_source_ids
        pass

    @property
    def source(self) -> NodeDef:
        return self.__source

    @property
    def target(self) -> NodeDef:
        return self.__target

    @property
    def name(self) -> str:
        return self.__name

    @property
    def weight(self) -> str:
        return self.__weight

    @property
    def metadata(self) -> dict:
        return self.__metadata

    @property
    def data_source_ids(self):
        return self.__data_source_ids

    @property
    def directed(self) -> bool:
        return self.__directed

    @property
    def edges(self) -> Set[Edge]:
        return self.__edges

    @property
    def label(self) -> str:
        return self.__label

    def createEdges(self, data: Data) -> None:
        self.__edges.update([Edge(s, t, self.__label, self.__directed) for s,t in zip(self.__source.getAllNodes(data), self.__target.getAllNodes(data))])
        return