from __future__ import annotations

import numpy as np
import pandas as pd

from .config import ProjectConfig
from .strategy import build_positions, build_trades


def _account_portfolio(
    positions: pd.DataFrame, rate: float, cash: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    trades = build_trades(positions, rate, cash)
    portfolio = positions.assign(weighted_return=positions.target_weight * positions.target_return_1m).groupby(
        ["signal_date", "return_date"], as_index=False
    ).agg(gross_return=("weighted_return", "sum"), cash_weight=("cash_weight", "first"),
          selected_assets=("selected", "sum"))
    portfolio = portfolio.merge(positions.groupby("signal_date", as_index=False)["execution_date"].first(),
                                on="signal_date", validate="one_to_one")
    costs = trades.groupby("signal_date", as_index=False).agg(
        turnover=("absolute_weight_change", "sum"), transaction_cost=("estimated_cost", "sum"))
    portfolio = portfolio.merge(costs, on="signal_date", validate="one_to_one")
    portfolio["cash_return"] = portfolio.cash_weight * cash
    portfolio["net_return"] = (1 - portfolio.transaction_cost) * (
        1 + portfolio.gross_return + portfolio.cash_return) - 1
    return trades, portfolio


def run_backtest(
    predictions: pd.DataFrame, config: ProjectConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    positions = build_positions(predictions, config)
    expected = set(config.section("data")["tickers"])
    for _, group in positions.groupby("signal_date"):
        if set(group.ticker) != expected:
            raise ValueError("Test month does not contain the configured candidate universe")
    for col in ["signal_date", "execution_date", "return_date"]:
        positions[col] = pd.to_datetime(positions[col], errors="raise")
    if positions[["signal_date", "execution_date", "return_date"]].isna().any().any():
        raise ValueError("Missing execution or return dates")
    if not ((positions.signal_date < positions.execution_date) &
            (positions.execution_date < positions.return_date)).all():
        raise ValueError("Require signal_date < execution_date < return_date")
    dates = positions.groupby("signal_date")[["execution_date", "return_date"]]
    if (dates.nunique() != 1).any().any():
        raise ValueError("ETFs must have identical execution and return dates")
    schedule = dates.first().sort_index()
    if not np.all(schedule.return_date.iloc[:-1].to_numpy() == schedule.execution_date.iloc[1:].to_numpy()):
        raise ValueError("Holding periods must be contiguous without gaps or overlap")
    settings = config.section("strategy")
    cash = (1 + float(settings.get("cash_return_annual", 0))) ** (1 / 12) - 1
    rate = float(settings["transaction_cost_bps"])
    trades, portfolio = _account_portfolio(positions, rate, cash)
    portfolio = portfolio.rename(columns={"gross_return": "gross_strategy_return", "net_return": "strategy_return"})

    equal = positions.copy()
    equal["target_weight"] = 1 / len(expected)
    equal["cash_weight"] = 0.0
    equal["selected"] = True
    _, eq = _account_portfolio(equal, rate, cash)
    for source, dest in [("gross_return", "gross_equal_weight_return"), ("net_return", "equal_weight_return"),
                         ("turnover", "equal_weight_turnover"), ("transaction_cost", "equal_weight_transaction_cost")]:
        portfolio[dest] = eq[source].to_numpy()

    ticker = str(config.section("evaluation")["benchmark_ticker"])
    monthly = pd.read_csv(config.path("monthly_prices"), parse_dates=["date", "execution_date", "return_date"])
    spy = monthly.loc[monthly.ticker.eq(ticker) & monthly.date.isin(schedule.index)].copy()
    if spy.date.duplicated().any():
        raise ValueError("Duplicate benchmark dates")
    spy = spy.set_index("date").reindex(schedule.index)
    if not np.isfinite(spy.target_return_1m.to_numpy(dtype=float)).all():
        raise ValueError("Missing or non-finite benchmark returns on test dates")
    if not (spy.execution_date.eq(schedule.execution_date) & spy.return_date.eq(schedule.return_date)).all():
        raise ValueError("Benchmark holding periods do not match strategy")
    if (spy.target_return_1m <= -1).any():
        raise ValueError("Benchmark returns must exceed -100%")
    # Buy-and-hold SPY: charge the same entry rate; no subsequent rebalancing.
    portfolio["gross_benchmark_return"] = spy.target_return_1m.to_numpy()
    portfolio["benchmark_turnover"] = 0.0
    portfolio.loc[0, "benchmark_turnover"] = 1 / (1 + rate / 10_000)
    portfolio["benchmark_transaction_cost"] = portfolio.benchmark_turnover * rate / 10_000
    portfolio["benchmark_return"] = (1 - portfolio.benchmark_transaction_cost) * (1 + portfolio.gross_benchmark_return) - 1
    portfolio["benchmark_ticker"] = ticker
    return positions, trades, portfolio.sort_values("signal_date").reset_index(drop=True)
