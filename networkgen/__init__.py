"""High-level re-exports for consumers."""

from .project import Project  # noqa: F401 – key API surface
from .definitions import NodeDef, EdgeDef  # noqa: F401
from .builder import build_graph  # noqa: F401
from .datasource import DataSource  # noqa: F401
from .errors import ProjectError

__all__ = [
    "Project",
    "NodeDef",
    "EdgeDef",
    "DataSource",
    "build_graph",
    "ProjectError"
]
__version__ = "1.0.0"