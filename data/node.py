import uuid

class Node:
    __field: str
    __name: str
    __id: uuid.UUID
    __label: str

    def __init__(self, field: str, name: str, label: str = "") -> None:
        self.__id = uuid.uuid4()
        self.__field = field
        self.__name = name
        self.__label = label
        
    @property
    def name(self) -> str:
        return self.__name

    @property
    def field(self) -> str:
        return self.__field

    @property
    def id(self) -> str:
        return str(self.__id)

    @property
    def label(self) -> str:
        return self.__label

    @property
    def as_dict(self) -> dict:
        return {
            "ID": self.__id,
            "Name": self.__name,
            "Field": self.__field,
            "Label": self.__label
        }

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Node): return False
        if self.__field != __o.field and self.__name != __o.name: return False
        return True

    def __hash__(self) -> int:
        return hash(self.__id)
    
