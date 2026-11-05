from __future__ import annotations

import numpy as np
import pandas as pd

from .config import ProjectConfig


def build_positions(predictions: pd.DataFrame, config: ProjectConfig) -> pd.DataFrame:
    settings = config.section("strategy")
    top_k = int(settings["top_k"])
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    test = predictions.loc[predictions["split"].eq("test")].copy()
    if test.empty:
        raise ValueError("No test predictions are available for backtesting")
    if test.duplicated(["signal_date", "ticker"]).any():
        raise ValueError("Duplicate test signal-ticker rows")
    # Missing future outcomes must never silently change the investable universe.
    if not np.isfinite(test[["predicted_return", "target_return_1m"]].to_numpy(dtype=float)).all():
        raise ValueError("Test predictions and realised returns must be finite and complete")
    if (test["target_return_1m"] <= -1).any():
        raise ValueError("ETF returns must exceed -100%")
    test = test.sort_values(["signal_date", "ticker"])
    test["eligible"] = True
    if settings.get("require_positive_prediction", True):
        test["eligible"] = test["predicted_return"] > 0
    test["eligible_rank"] = (
        test["predicted_return"].where(test["eligible"]).groupby(test["signal_date"])
        .rank(ascending=False, method="first")
    )
    test["selected"] = test["eligible"] & test["eligible_rank"].le(top_k)
    test["target_weight"] = np.where(test["selected"], 1.0 / top_k, 0.0)
    test["cash_weight"] = 1.0 - test.groupby("signal_date")["target_weight"].transform("sum")
    return test.reset_index(drop=True)


def build_trades(
    positions: pd.DataFrame, transaction_cost_bps: float, monthly_cash_return: float = 0.0,
) -> pd.DataFrame:
    """Self-financing rebalance: weights target wealth remaining after execution costs.

    All notionals and costs are fractions of wealth immediately before the trade.
    Only the previous holding period's returns determine current drifted weights.
    """
    rate = float(transaction_cost_bps) / 10_000.0
    if not 0 <= rate < 1:
        raise ValueError("Transaction cost rate must be in [0, 1)")
    tickers = sorted(positions["ticker"].unique())
    previous = pd.Series(0.0, index=tickers)
    rows = []
    for _, group in positions.sort_values(["signal_date", "ticker"]).groupby("signal_date", sort=True):
        group = group.set_index("ticker").reindex(tickers)
        if group["target_weight"].isna().any():
            raise ValueError("Every month must include the complete candidate universe")
        target = group["target_weight"]
        if (target < 0).any() or target.sum() > 1 + 1e-12:
            raise ValueError("Weights must be long-only and unleveraged")
        # Solve c = rate * sum(abs((1-c)*target - pretrade_weight)).
        cost = 0.0
        for _ in range(200):
            updated = rate * float(((1 - cost) * target - previous).abs().sum())
            if abs(updated - cost) < 1e-14:
                cost = updated
                break
            cost = updated
        else:
            raise ValueError("Self-financing cost calculation did not converge")
        trades = group[["signal_date", "execution_date", "return_date", "target_weight"]].copy()
        trades["previous_weight"] = previous
        trades["executed_weight"] = (1 - cost) * target
        trades["weight_change"] = trades["executed_weight"] - previous
        trades["absolute_weight_change"] = trades["weight_change"].abs()
        trades["estimated_cost"] = rate * trades["absolute_weight_change"]
        rows.append(trades.reset_index())
        gross = float((target * group["target_return_1m"]).sum()) + (1 - target.sum()) * monthly_cash_return
        if not np.isfinite(gross) or 1 + gross <= 0:
            raise ValueError("Non-positive or invalid portfolio wealth")
        previous = target * (1 + group["target_return_1m"]) / (1 + gross)
    return pd.concat(rows, ignore_index=True).sort_values(["signal_date", "ticker"]).reset_index(drop=True)
