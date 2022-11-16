from numpy import isin
from data.node import Node


class Edge:
    __source: Node
    __target: Node
    __directed: bool
    __weight: int
    __label: str

    def __init__(self, source: Node, target: Node, label: str, directed: bool) -> None:
        self.__source = source
        self.__target = target
        self.__directed = directed
        self.__label = label
        self.__weight = 1

    @property
    def source(self) -> Node:
        return self.__source

    @property
    def target(self) -> Node:
        return self.__target

    @property
    def directed(self) -> bool:
        return self.__directed

    @property
    def weight(self) -> int:
        return self.__weight

    def add(self, weight: int=1) -> None:
        self.__weight += weight
        return

    @property
    def as_dict(self) -> dict:
        return {
            "Source": self.__source.id,
            "Target": self.__target.id,
            "Label": self.__label,
            "Weight": self.__weight,
            "Type": "Directed" if self.__directed else "Undirected"
        }

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Edge): return False
        if self.__directed != __o.directed: return False
        if self.__directed:
            if self.__source != __o.source or self.__target != __o.target: return False
        else:
            if (self.__source != __o.source and self.__source != __o.target) or (self.__target != __o.target and self.__target != __o.source):
                return False
        self.add()
        return True

    def __hash__(self) -> int:
        return hash(f"{self.__source.id}{self.__target.id}")