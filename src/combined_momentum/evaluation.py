from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _max_drawdown(returns: pd.Series) -> float:
    wealth = (1.0 + returns).cumprod()
    drawdown = wealth.div(wealth.cummax().clip(lower=1.0)).sub(1.0)
    return float(drawdown.min())


def performance_metrics(returns: pd.Series, annualization: int) -> dict[str, float | int]:
    if annualization <= 0:
        raise ValueError("Annualization factor must be positive")
    clean = returns.astype(float)
    if not np.isfinite(clean.to_numpy()).all() or (clean <= -1).any():
        raise ValueError("Returns must be finite, complete and greater than -100%")
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
            prefix = "equal_weight" if name == "equal_weight_universe" else "benchmark"
            row["average_monthly_turnover"] = float(portfolio[f"{prefix}_turnover"].mean())
            row["total_transaction_cost"] = float(portfolio[f"{prefix}_transaction_cost"].sum())
        metric_rows.append(row)
    metrics = pd.DataFrame(metric_rows)

    curves = portfolio[["signal_date", "return_date"]].copy()
    curves["is_initial_wealth"] = False
    for name, column in series_map.items():
        curves[f"wealth_{name}"] = (1.0 + portfolio[column]).cumprod()
        curves[f"drawdown_{name}"] = curves[f"wealth_{name}"].div(
            curves[f"wealth_{name}"].cummax().clip(lower=1.0)
        ).sub(1.0)

    origin = {"signal_date": pd.NaT, "return_date": portfolio["execution_date"].iloc[0],
              "is_initial_wealth": True}
    for name in series_map:
        origin[f"wealth_{name}"] = 1.0
        origin[f"drawdown_{name}"] = 0.0
    curves = pd.concat([pd.DataFrame([origin]), curves], ignore_index=True)

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
            returns = group[column]
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
    fig, axes = plt.subplots(2, 1, figsize=(10, 9))
    for axis, metric, title in zip(axes, ["return", "sharpe_ratio"],
                                   ["Out-of-sample return by realisation year", "Sharpe ratio by realisation year"]):
        annual.pivot(index="year", columns="portfolio", values=metric).plot(kind="bar", ax=axis)
        axis.axhline(0.0, color="black", linewidth=0.8)
        axis.set_title(title + " (boundary years may be partial)")
        axis.set_xlabel("Return year")
        axis.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def evaluate_prediction_years(
    predictions: pd.DataFrame, train_mean: float, target_column: str, figures_dir: Path,
) -> pd.DataFrame:
    """Describe the fixed test predictions by realisation year; never fit a model."""
    test = predictions.loc[predictions["split"].eq("test")].copy()
    test["year"] = pd.to_datetime(test["return_date"]).dt.year
    rows = []
    for year, group in test.groupby("year"):
        actual = group[target_column]
        error = group["predicted_return"] - actual
        baseline_sse = float(((actual - train_mean) ** 2).sum())
        rows.append({
            "year": int(year), "observations": len(group),
            "months": group["signal_date"].nunique(),
            "rmse": float(np.sqrt((error ** 2).mean())),
            "r2_vs_train_mean": 1 - float((error ** 2).sum()) / baseline_sse if baseline_sse > 0 else np.nan,
        })
    annual = pd.DataFrame(rows)
    fig, axis = plt.subplots(figsize=(10, 5.5))
    axis.bar(annual["year"].astype(str), annual["r2_vs_train_mean"])
    axis.axhline(0, color="black", linewidth=.8)
    axis.set_title("Fixed test prediction R-squared by realisation year (boundary years partial)")
    axis.set_xlabel("Return year")
    axis.set_ylabel("R-squared versus fixed training mean")
    fig.tight_layout()
    figures_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(figures_dir / "test_prediction_r2.png", dpi=180)
    plt.close(fig)
    return annual
