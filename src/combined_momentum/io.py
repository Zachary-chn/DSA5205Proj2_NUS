from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def read_table(
    path: Path,
    date_columns: tuple[str, ...] = ("date", "signal_date", "execution_date", "return_date"),
) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required pipeline file does not exist: {path}")
    frame = pd.read_csv(path)
    for column in date_columns:
        if column in frame.columns:
            frame[column] = pd.to_datetime(frame[column])
    return frame


def write_table(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, date_format="%Y-%m-%d")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def make_run_id(project_name: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}_{project_name}"


def write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)

