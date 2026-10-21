from __future__ import annotations

import numpy as np
import pandas as pd

from .config import ProjectConfig
from .strategy import build_positions, build_trades


def run_backtest(
    predictions: pd.DataFrame,
    config: ProjectConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    positions = build_positions(predictions, config)
    settings = config.section("strategy")
    trades = build_trades(positions, float(settings["transaction_cost_bps"]))

    portfolio = (
        positions.assign(weighted_return=positions["target_weight"] * positions["target_return_1m"])
        .groupby(["signal_date", "return_date"], as_index=False)
        .agg(
            gross_strategy_return=("weighted_return", "sum"),
            cash_weight=("cash_weight", "first"),
            selected_assets=("selected", "sum"),
        )
    )
    costs = trades.groupby("signal_date", as_index=False).agg(
        turnover=("absolute_weight_change", "sum"),
        transaction_cost=("estimated_cost", "sum"),
    )
    portfolio = portfolio.merge(costs, on="signal_date", how="left")
    annual_cash = float(settings.get("cash_return_annual", 0.0))
    monthly_cash = (1.0 + annual_cash) ** (1.0 / 12.0) - 1.0
    portfolio["cash_return"] = portfolio["cash_weight"] * monthly_cash
    portfolio["strategy_return"] = (
        portfolio["gross_strategy_return"] + portfolio["cash_return"] - portfolio["transaction_cost"]
    )

    test = predictions.loc[
        predictions["split"].eq("test") & predictions["target_return_1m"].notna()
    ].copy()
    equal_weight = test.groupby("signal_date")["target_return_1m"].mean().rename("equal_weight_return")
    benchmark_ticker = str(config.section("evaluation")["benchmark_ticker"])
    monthly = pd.read_csv(config.path("monthly_prices"), parse_dates=["date"])
    benchmark = (
        monthly.loc[monthly["ticker"].eq(benchmark_ticker), ["date", "target_return_1m"]]
        .dropna(subset=["target_return_1m"])
        .drop_duplicates("date")
        .set_index("date")["target_return_1m"]
        .rename_axis("signal_date")
        .rename("benchmark_return")
    )
    portfolio = portfolio.set_index("signal_date").join(equal_weight).join(benchmark).reset_index()
    portfolio["benchmark_ticker"] = benchmark_ticker
    return positions, trades, portfolio.sort_values("signal_date").reset_index(drop=True)

