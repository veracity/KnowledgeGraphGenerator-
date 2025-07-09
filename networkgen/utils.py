"""Utility helpers: hashing, flexible pandas reader, etc."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

__all__ = [
    "sha256_file",
    "read_any",
]


def sha256_file(path: Path | str, chunk_size: int = 65536) -> str:
    """Return *hex* SHA-256 digest for *path* (binary-read)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def read_any(path: Path | str, **kwargs) -> pd.DataFrame:
    """Load CSV/XLSX/JSON/Parquet via pandas, by suffix."""
    p = Path(path)
    suf = p.suffix.lower()
    if suf in {".csv", ".tsv"}:
        return pd.read_csv(p, **kwargs)
    if suf in {".xlsx", ".xls"}:
        return pd.read_excel(p, **kwargs)
    if suf == ".json":
        return pd.read_json(p, **kwargs)
    if suf == ".parquet":
        return pd.read_parquet(p, **kwargs)
    raise ValueError(f"Unsupported file type: {p}")

def json_dumps_compact(obj: Any) -> str:
    """Dump JSON without spaces/newlines (useful for YAML scalar)."""
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)