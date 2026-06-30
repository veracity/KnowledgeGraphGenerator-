"""A minimal tabular data container used in place of pandas DataFrame.

Stores data column-wise as plain Python lists and tracks a simple logical
type per column ("string", "integer", "float", "boolean"). This keeps the
application free of the pandas/numpy dependency, which dominates the size of
a frozen/standalone build.
"""


def _to_int(value):
    if value is None or value == "":
        return value
    if isinstance(value, bool):
        return int(value)
    return int(value)


def _to_float(value):
    if value is None or value == "":
        return value
    return float(value)


def _to_string(value):
    if value is None:
        return value
    return str(value)


def _to_boolean(value):
    if value is None or value == "":
        return value
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in ("true", "1", "yes", "y"):
        return True
    if text in ("false", "0", "no", "n"):
        return False
    raise ValueError(f"cannot convert {value!r} to boolean")


CONVERTERS = {
    "integer": _to_int,
    "float": _to_float,
    "string": _to_string,
    "boolean": _to_boolean,
}


def _infer_type(values) -> str:
    seen = set()
    for value in values:
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            seen.add("boolean")
        elif isinstance(value, int):
            seen.add("integer")
        elif isinstance(value, float):
            seen.add("float")
        else:
            seen.add("string")
    if not seen:
        return "string"
    if seen == {"integer"}:
        return "integer"
    if seen <= {"integer", "float"}:
        return "float"
    if seen == {"boolean"}:
        return "boolean"
    return "string"


def unique_columns(names) -> list:
    seen = {}
    result = []
    for index, name in enumerate(names):
        if name is None:
            name = f"Column{index + 1}"
        name = str(name)
        if name in seen:
            seen[name] += 1
            result.append(f"{name}.{seen[name]}")
        else:
            seen[name] = 0
            result.append(name)
    return result


class Table:
    def __init__(self, columns, data=None, types=None) -> None:
        self._columns = list(columns)
        if data is None:
            self._data = {column: [] for column in self._columns}
        else:
            self._data = {column: list(data.get(column, [])) for column in self._columns}
        if types is None:
            self._types = {column: _infer_type(self._data[column]) for column in self._columns}
        else:
            self._types = {column: types.get(column, "string") for column in self._columns}

    @property
    def columns(self) -> list:
        return list(self._columns)

    def __getitem__(self, column):
        return self._data[column]

    def __contains__(self, column) -> bool:
        return column in self._data

    def column_type(self, column) -> str:
        return self._types.get(column, "string")

    def set_column_type(self, column, new_type) -> None:
        converter = CONVERTERS[new_type]
        self._data[column] = [converter(value) for value in self._data[column]]
        self._types[column] = new_type
        return
