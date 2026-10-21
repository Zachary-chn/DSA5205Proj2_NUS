from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _max_drawdown(returns: pd.Series) -> float:
    wealth = (1.0 + returns.fillna(0.0)).cumprod()
    drawdown = wealth.div(wealth.cummax()).sub(1.0)
    return float(drawdown.min())


def performance_metrics(returns: pd.Series, annualization: int) -> dict[str, float | int]:
    clean = returns.dropna().astype(float)
    if clean.empty:
        return {
            "observations": 0,
            "annualized_return": np.nan,
            "annualized_volatility": np.nan,
            "sharpe_ratio": np.nan,
            "max_drawdown": np.nan,
            "positive_period_rate": np.nan,
            "cumulative_return": np.nan,
        }
    years = len(clean) / annualization
    cumulative = float((1.0 + clean).prod() - 1.0)
    annual_return = float((1.0 + cumulative) ** (1.0 / years) - 1.0) if years > 0 else np.nan
    annual_volatility = float(clean.std(ddof=1) * np.sqrt(annualization))
    sharpe = (
        float(clean.mean() / clean.std(ddof=1) * np.sqrt(annualization))
        if annual_volatility > 0
        else np.nan
    )
    return {
        "observations": int(len(clean)),
        "annualized_return": annual_return,
        "annualized_volatility": annual_volatility,
        "sharpe_ratio": sharpe,
        "max_drawdown": _max_drawdown(clean),
        "positive_period_rate": float((clean > 0).mean()),
        "cumulative_return": cumulative,
    }


def evaluate_portfolio(
    portfolio: pd.DataFrame,
    annualization: int,
    figures_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    series_map = {
        "combined_momentum": "strategy_return",
        "equal_weight_universe": "equal_weight_return",
        "benchmark": "benchmark_return",
    }
    metric_rows = []
    for name, column in series_map.items():
        row = {"portfolio": name, **performance_metrics(portfolio[column], annualization)}
        if name == "combined_momentum":
            row["average_monthly_turnover"] = float(portfolio["turnover"].mean())
            row["total_transaction_cost"] = float(portfolio["transaction_cost"].sum())
        else:
            row["average_monthly_turnover"] = np.nan
            row["total_transaction_cost"] = np.nan
        metric_rows.append(row)
    metrics = pd.DataFrame(metric_rows)

    curves = portfolio[["signal_date", "return_date"]].copy()
    for name, column in series_map.items():
        curves[f"wealth_{name}"] = (1.0 + portfolio[column].fillna(0.0)).cumprod()
        curves[f"drawdown_{name}"] = curves[f"wealth_{name}"].div(
            curves[f"wealth_{name}"].cummax()
        ).sub(1.0)

    figures_dir.mkdir(parents=True, exist_ok=True)
    _plot_curves(curves, series_map.keys(), figures_dir / "equity_curve.png", drawdown=False)
    _plot_curves(curves, series_map.keys(), figures_dir / "drawdown.png", drawdown=True)
    annual = _annual_performance(portfolio, series_map, annualization)
    _plot_annual_performance(annual, figures_dir / "annual_performance.png")
    return metrics, curves, annual


def _plot_curves(
    curves: pd.DataFrame,
    names,
    path: Path,
    drawdown: bool,
) -> None:
    fig, axis = plt.subplots(figsize=(10, 5.5))
    prefix = "drawdown" if drawdown else "wealth"
    for name in names:
        axis.plot(curves["return_date"], curves[f"{prefix}_{name}"], label=name.replace("_", " "))
    axis.set_title("Out-of-sample drawdown" if drawdown else "Out-of-sample cumulative wealth")
    axis.set_xlabel("Return month")
    axis.set_ylabel("Drawdown" if drawdown else "Growth of 1")
    axis.grid(alpha=0.25)
    axis.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _annual_performance(
    portfolio: pd.DataFrame,
    series_map: dict[str, str],
    annualization: int,
) -> pd.DataFrame:
    dated = portfolio.copy()
    dated["year"] = pd.to_datetime(dated["return_date"]).dt.year
    rows = []
    for year, group in dated.groupby("year"):
        for name, column in series_map.items():
            returns = group[column].dropna()
            annual_return = float((1.0 + returns).prod() - 1.0)
            annual_volatility = float(returns.std(ddof=1) * np.sqrt(annualization))
            rows.append(
                {
                    "year": int(year),
                    "portfolio": name,
                    "months": len(returns),
                    "return": annual_return,
                    "annualized_volatility": annual_volatility,
                    "sharpe_ratio": (
                        float(returns.mean() / returns.std(ddof=1) * np.sqrt(annualization))
                        if annual_volatility > 0
                        else np.nan
                    ),
                }
            )
    return pd.DataFrame(rows)


def _plot_annual_performance(annual: pd.DataFrame, path: Path) -> None:
    pivot = annual.pivot(index="year", columns="portfolio", values="return")
    axis = pivot.plot(kind="bar", figsize=(10, 5.5))
    axis.axhline(0.0, color="black", linewidth=0.8)
    axis.set_title("Out-of-sample return by calendar year")
    axis.set_xlabel("Return year")
    axis.set_ylabel("Return")
    axis.grid(axis="y", alpha=0.25)
    axis.legend(title=None)
    axis.figure.tight_layout()
    axis.figure.savefig(path, dpi=180)
    plt.close(axis.figure)

