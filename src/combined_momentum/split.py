from __future__ import annotations

import pandas as pd

from .config import ProjectConfig


def assign_splits(frame: pd.DataFrame, config: ProjectConfig) -> pd.DataFrame:
    result = frame.copy()
    dates = pd.to_datetime(result["signal_date"])
    settings = config.section("split")
    train_end = pd.Timestamp(settings["train_end"])
    validation_end = pd.Timestamp(settings["validation_end"])
    test_end = pd.Timestamp(settings["test_end"])

    if not train_end < validation_end < test_end:
        raise ValueError("Split dates must satisfy train_end < validation_end < test_end")

    result["split"] = "outside"
    result.loc[dates <= train_end, "split"] = "train"
    result.loc[(dates > train_end) & (dates <= validation_end), "split"] = "validation"
    result.loc[(dates > validation_end) & (dates <= test_end), "split"] = "test"

    labelled = result["target_return_1m"].notna()
    for split_name in ("train", "validation", "test"):
        if result.loc[labelled & result["split"].eq(split_name)].empty:
            raise ValueError(f"No labelled observations available for split={split_name}")
    return result

