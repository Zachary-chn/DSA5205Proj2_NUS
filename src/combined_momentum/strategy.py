from __future__ import annotations

import numpy as np
import pandas as pd

from .config import ProjectConfig


def build_positions(predictions: pd.DataFrame, config: ProjectConfig) -> pd.DataFrame:
    settings = config.section("strategy")
    top_k = int(settings["top_k"])
    require_positive = bool(settings.get("require_positive_prediction", True))

    test = predictions.loc[
        predictions["split"].eq("test") & predictions["target_return_1m"].notna()
    ].copy()
    if test.empty:
        raise ValueError("No labelled test predictions are available for backtesting")

    test["eligible"] = True
    if require_positive:
        test["eligible"] = test["predicted_return"] > 0
    test["eligible_rank"] = (
        test["predicted_return"].where(test["eligible"]).groupby(test["signal_date"]).rank(
            ascending=False, method="first"
        )
    )
    test["selected"] = test["eligible"] & test["eligible_rank"].le(top_k)
    test["target_weight"] = np.where(
        test["selected"],
        1.0 / top_k,
        0.0,
    )
    invested = test.groupby("signal_date")["target_weight"].transform("sum")
    test["cash_weight"] = 1.0 - invested
    return test.sort_values(["signal_date", "ticker"]).reset_index(drop=True)


def build_trades(positions: pd.DataFrame, transaction_cost_bps: float) -> pd.DataFrame:
    trades = positions[["signal_date", "execution_date", "return_date", "ticker", "target_weight"]].copy()
    trades["previous_weight"] = trades.groupby("ticker")["target_weight"].shift(1).fillna(0.0)
    trades["weight_change"] = trades["target_weight"] - trades["previous_weight"]
    trades["absolute_weight_change"] = trades["weight_change"].abs()
    trades["estimated_cost"] = trades["absolute_weight_change"] * float(transaction_cost_bps) / 10_000.0
    return trades.sort_values(["signal_date", "ticker"]).reset_index(drop=True)

