from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ProjectConfig:
    values: dict[str, Any]
    root: Path
    config_path: Path

    def section(self, name: str) -> dict[str, Any]:
        return self.values[name]

    def path(self, key: str) -> Path:
        return self.root / self.values["paths"][key]


def load_config(path: str | Path) -> ProjectConfig:
    config_path = Path(path).resolve()
    with config_path.open("r", encoding="utf-8") as handle:
        values = yaml.safe_load(handle)

    required = {"project", "paths", "data", "features", "split", "model", "strategy", "evaluation"}
    missing = required.difference(values)
    if missing:
        raise ValueError(f"Missing configuration sections: {sorted(missing)}")

    root = config_path.parent.parent
    return ProjectConfig(values=values, root=root, config_path=config_path)


def ensure_project_directories(config: ProjectConfig) -> None:
    for key in ("raw_prices", "monthly_prices", "model_table"):
        config.path(key).parent.mkdir(parents=True, exist_ok=True)
    config.path("artifacts_dir").mkdir(parents=True, exist_ok=True)

