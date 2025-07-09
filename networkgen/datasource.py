"""Lightweight wrapper around a pandas DataFrame on disk."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from .utils import read_any, sha256_file

__all__ = ["DataSource"]


class DataSource:
    """Represents a single table-like file (CSV/XLSX/…).

    It loads lazily, caches a checksum and can answer *has_changed()*.
    """

    def __init__(self, id: str, path: Path | str, checksum: str | None = None):
        self.id = id
        self.path = Path(path)
        self._df: Optional[pd.DataFrame] = None
        self._checksum: Optional[str] = checksum

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = read_any(self.path)
            if self._checksum is None:
                self._checksum = sha256_file(self.path)
        return self._df

    # ------------------------------------------------------------------
    def has_changed(self) -> bool:
        """Return *True* if on-disk checksum differs from cached one."""
        if self._checksum is None:
            # not loaded yet – cannot know, assume changed
            return True
        return sha256_file(self.path) != self._checksum
    
    def update(self) -> None:
        self._df = read_any(self.path)
        self._checksum = sha256_file(self.path)
        return

    def to_dict(self, project_dir: Path) -> dict:
        return {
            "id": self.id,
            "path": str(Path(self.path).relative_to(project_dir)),
            "checksum": self._checksum
        }

    @classmethod
    def from_dict(cls, d: dict, project_dir: Path, checksum: str) -> "DataSource":
        p = project_dir / d["path"]
        return cls(d["id"], p, checksum)
