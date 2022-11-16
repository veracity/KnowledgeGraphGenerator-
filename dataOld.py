import time
from typing import Any, List, Set, Tuple
import pandas as pd

class Data:
    _path: str = ""
    _name: str = ""
    _type: str = ""
    _df: pd.DataFrame = None
    _loaded: bool = False

    def __init__(self, path) -> None:
        self._path = path
        self._name = path.split("/")[-1].split(".")[0]
        self._type = path.split("/")[-1].split(".")[-1]
        self._loaded = False
        pass

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @property
    def loaded(self) -> bool:
        return self._loaded

    def __repr__(self) -> str:
        return f"path: {self._path}, name: {self._name}, type: {self._type}"

    def __str__(self) -> str:
        return f"path: {self._path}, name: {self._name}, type: {self._type}"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Data): return False
        if (self._path != __o.path): return False
        return True

    def __hash__(self) -> int:
        return hash(self._path)

    def loadData(self) -> None:
        if (self._type == "csv"):
            # parse csv
            # check if there is only one column, then try to parse with another delimiter
            try: 
                self._df = pd.read_csv(self._path, delimiter=';', decimal=',', dtype="string")
                if (self._df.shape[1] == 1):
                    self._df = pd.read_csv(self._path, delimiter=',', decimal='.', dtype="string")
            except Exception as e:
                print(e)
                print("cannot load")
                pass
            pass
        elif (self._type == "xlsx"):
            # parse excel
            pass
        elif (self._type == "json"):
            # Parse json
            pass
        else:
            # Error here
            pass

        self._loaded = True
        # self._df = self._df.astype("string")
        # for d in self._df.columns:
        #     self._df = self._df.drop(self._df[self._df[d].str.strip().str.lower() == "unknown"].index)
        #     pass

        return

class Node:
    _field: str
    _name: str
    _id: str
    _data: List[Any]
    _label: str = ""

    def __init__(self, field: str, name: str) -> None:
        self._field = field
        self._name = name
        self._id = f"{self._field}_{self._name}"
        self._label = ""
        pass

    @property
    def name(self) -> str:
        return self._name

    @property
    def field(self) -> str:
        return self._field

    @property
    def id(self) -> str:
        return self._id

    def addData(self) -> None:
        return

    def to_dict(self) -> dict:
        return {
            "ID": self._id,
            "Name": self._name,
            "Field": self._field
        }

    def __eq__(self, __o: object) -> bool:
        if (not isinstance(__o, Node)): return False
        if (self._field != __o.field and self._name != __o.name): return False
        if (self._id != __o.id): return False
        return True

    def __hash__(self) -> int:
        return hash(self._id)

class Edge:
    _source: str
    _target: str
    _directed: bool
    _weight: int = 0

    def __init__(self, source: str, target: str, directed: bool) -> None:
        self._source = source
        self._target = target
        self._directed = directed
        return

    @property
    def source(self) -> Node:
        return self._source

    @property
    def target(self) -> Node:
        return self._target

    @property
    def weight(self) -> int:
        return self._weight

    def add(self, weight=1) -> None:
        self._weight += weight
        return

    def to_dict(self) -> dict:
        return {
            "Source": f"{self._source}",
            "Target": f"{self._target}",
            "Weight": self._weight,
            "Type": "Directed" if self._directed == True else "Undirected"
        }

    def __eq__(self, __o: object) -> bool:
        if (not isinstance(__o, Edge)): return False
        if (self._directed != __o._directed): return False
        if (self._directed):    
            if (self._source != __o._source or self._target != __o._target): return False
        else:
            if ((self._source != __o._source and self._source != __o.target) or (self._target != __o.target and self._target != __o.source)): return False
        self.add()
        return True

    def __hash__(self) -> int:
        return hash(f"{self._source}_{self._target}")

class NodeDef:
    _field: str
    _data: Data
    _extraData: List[Any]
    
    def __init__(self, field, data) -> None:
        self._field = field
        self._data = data
        pass

    @property
    def field(self) -> str:
        return self._field

    @property
    def data(self) -> Data:
        return self._data

    def createNodesV2(self, dataIn):
        return Node(self._field, dataIn[self._field])

    def __eq__(self, __o: object) -> bool:
        if (not isinstance(__o, NodeDef)): return False
        if (self._field != __o.field): return False
        if (self._data != self._data): return False
        
        return True

    def __hash__(self) -> int:
        return hash(f"{self._field}{self._data.name}{self._data.path}{self._data.type}")

    def __repr__(self) -> str:
        return f"({self._field},{self._data.name})"

    def __str__(self) -> str:
        return f"({self._field},{self._data.name})"

class EdgeDef:
    _source: NodeDef
    _target: NodeDef
    _directed: bool = False
    _data: Data = None

    def __init__(self, source: NodeDef, target: NodeDef, directed: bool, data: Data) -> None:
        self._source = source
        self._target = target
        self._directed = directed
        self._data = data
        return

    @property
    def source(self) -> NodeDef:
        return self._source

    @property
    def target(self) -> NodeDef:
        return self._target

    @property
    def directed(self) -> bool:
        return self._directed

    @property
    def data(self) -> Data:
        return self._data

    def createEdgesV2(self, dataIn):
        return Edge(f"{self._source.field}_{dataIn[self._source.field]}", f"{self._target.field}_{dataIn[self._target.field]}", self._directed)

    def __eq__(self, __o: object) -> bool:
        if (not isinstance(__o, EdgeDef)): return False
        if (self._source != __o.source or self._target != __o.target): return False
        if (self._directed != __o.directed): return False
        return True

    def __hash__(self) -> int:
        return hash(f"{self._source}{self._target}{self._directed}")

    def __str__(self) -> str:
        return f"({self._source},{self._target},{self._directed})"
    
    def __repr__(self) -> str:
        return f"({self._source},{self._target},{self._directed})"

class DataManager:
    _nodeDefs: Set[NodeDef] = set()
    _edgeDefs: Set[EdgeDef] = set()
    _nodes: Set[Node] = set()
    _edges: Set[Edge] = set()
    _data: Set[Data] = set()

    def __init__(self) -> None:
        return

    @property
    def nodeDefs(self) -> Set[NodeDef]:
        return self._nodeDefs

    @property
    def edgeDefs(self) -> Set[EdgeDef]:
        return self._edgeDefs

    @property
    def data(self) -> Set[Data]:
        return self._data

    def addNodeDef(self, node: NodeDef) -> None:
        self._nodeDefs.add(node)
        return

    def findNodeDef(self, field: str, name: str) -> NodeDef:
        r = None

        for nd in list(self._nodeDefs):
            if (nd.field == field and nd.data.name == name):
                r = nd
                break

        return r

    def removeNodeDef(self, node: NodeDef) -> None:
        self._nodeDefs.remove(node)
        return

    def addEdgeDef(self, edge: EdgeDef) -> None:
        self._edgeDefs.add(edge)
        return

    def removeEdgeDef(self, edge: EdgeDef) -> None:
        self._edgeDefs.remove(edge)
        return

    def getNodeDefsByData(self, data: Data) -> Set[NodeDef]:
        s = set()
        [s.add(nd) for nd in self._nodeDefs if nd.data == data]
        return s

    def getEdgeDefsByData(self, data: Data) -> Set[EdgeDef]:
        s = set()
        [s.add(ed) for ed in self._edgeDefs if ed.source.data == data]
        return s

    def addData(self, data: Data) -> None:
        self._data.add(data)
        return

    def findData(self, path:str, name:str, type:str) -> Data:
        r = None

        for d in list(self._data):
            if (d.name == name and d.path == path and d.type == type):
                r = d
                break

        return r

    def generateData(self) -> None:
        start = time.time()
        nodes = set()
        edges = set()

        for data in self._data:
            nd = list(self.getNodeDefsByData(data))
            ed = list(self.getEdgeDefsByData(data))

            data.df.apply(lambda x: [nodes.add(n.createNodesV2(x)) for n in nd], axis=1)
            data.df.apply(lambda x: [edges.add(e.createEdgesV2(x)) for e in ed], axis=1)

            pass

        self._nodes = nodes
        self._edges = edges

        print(f"Finished in: {time.time() - start}")
        return

    def removeData(self, data: Data) -> None:
        for n in list(self._nodeDefs):
            if (n.data == data):
                for e in list(self._edgeDefs):
                    if (e.source == n or e.target == n):
                        self.removeEdgeDef(e)
                self.removeNodeDef(n)
        self._data.remove(data)

        return

    def generateNodeFile(self, path: str) -> None:
        print("generating node file")
        df = pd.DataFrame.from_records([n.to_dict() for n in self._nodes])
        df.to_csv(path, index=False, sep=";", decimal=",")
        return

    def generateEdgeFile(self, path: str) -> None:
        print("generating edge file")
        df = pd.DataFrame.from_records([e.to_dict() for e in self._edges])
        df.to_csv(path, index=False, sep=";", decimal=",")
        return
    