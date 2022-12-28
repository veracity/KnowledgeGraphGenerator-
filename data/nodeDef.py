from typing import List, Set
from data.data import Data
from data.node import Node

class NodeDef:
    __field: str
    __label: str
    __nodes: Set[Node]
    __metaData: List[str]

    def __init__(self, field: str, label: str = "") -> None:
        self.__field = field
        self.__label = label
        self.__nodes = set()
        self.__metaData = []
        pass

    @property
    def field(self) -> str:
        return self.__field

    @property
    def label(self) -> str:
        return self.__label

    @property
    def nodes(self) -> Set[Node]:
        return self.__nodes

    def addMetaData(self, column: str):
        self.__metaData.append(column)
        return

    def createNodes(self, data: Data) -> None:
        self.__nodes.update([Node(self.__field, d, self.__label) for d in data.df[self.__field]])
        return

    def getAllNodes(self, data: Data) -> List[Node]:
        r = []
        dat = dict()

        for node in self.__nodes:
            dat[node.name] = node

        for d in data.df[self.__field]:
            r.append(dat[d])
            
        return r

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, NodeDef): return False
        if self.__field != __o.field: return False
        return True

    def __hash__(self) -> int:
        return hash(f"{self.__field}{self.__label}")

    def __str__(self) -> str:
        return f"{self.__field}"

    def __repr__(self) -> str:
        return self.__str__()