import pandas as pd

class Data:
    __path: str
    __name: str
    __type: str
    __df: pd.DataFrame
    __loaded: bool
    __error: bool

    def __init__(self, path: str) -> None:
        self.__path = path
        self.__name = path.split('/')[-1].split(".")[0]
        self.__type = path.split('/')[-1].split(".")[1]
        self.__loaded = False
        self.__error = False
        pass

    @property
    def path(self) -> str:
        return self.__path

    @property
    def name(self) -> str:
        return self.__name

    @property
    def type(self) -> str:
        return self.__type

    @property
    def df(self) -> pd.DataFrame:
        return self.__df

    @property
    def loaded(self) -> bool:
        return self.__loaded

    @property
    def error(self) -> bool:
        return self.__error

    def __str__(self) -> str:
        return f"path: {self.__path}, name: {self.__name}, type: {self.__type}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Data): return False
        if (self.__path != __o.path): return False
        return True
    
    def __hash__(self) -> int:
        return hash(self.__path)

    def loadData(self) -> None:
        self.__error = False
        if self.__type == "csv":
            try:
                self.__df = pd.read_csv(self.__path, delimiter=';', decimal=',', dtype='string')
                if (self.__df.shape[1] == 1):
                    self.__df = pd.read_csv(self.__path, delimiter=',', decimal='.', dtype='string')
            except Exception as e:
                print(e)
                print("could not load")
                self.__error = True
        elif self.__type == "xlsx":
            self.__df = pd.read_excel(self.__path)
            pass
        elif self.__type == "json":
            self.__df = pd.read_json(self.__path)
        return