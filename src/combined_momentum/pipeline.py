from __future__ import annotations

from pathlib import Path
import platform
import sys
from typing import Any

from importlib.metadata import PackageNotFoundError, version

import pandas as pd

from .backtest import run_backtest
from .config import ProjectConfig, ensure_project_directories
from .data import prepare_data
from .evaluation import evaluate_portfolio
from .features import build_model_table
from .io import file_sha256, make_run_id, read_table, write_json, write_table
from .model import fit_and_predict, plot_test_predictions, prediction_metrics
from .split import assign_splits


VALID_STAGES = {"all", "data", "features", "model", "backtest", "evaluate"}


def _latest_marker(config: ProjectConfig) -> Path:
    return config.path("artifacts_dir") / "LATEST_RUN.txt"


def _resolve_run_dir(config: ProjectConfig, run_id: str | None, create: bool) -> Path:
    artifacts = config.path("artifacts_dir")
    if run_id:
        resolved = artifacts / run_id
    elif create:
        resolved = artifacts / make_run_id(config.section("project")["name"])
    else:
        marker = _latest_marker(config)
        if not marker.exists():
            raise FileNotFoundError("No previous run found. Run the model stage first or pass --run-id")
        resolved = artifacts / marker.read_text(encoding="utf-8").strip()
    if not create and not resolved.exists():
        raise FileNotFoundError(f"Run directory does not exist: {resolved}")
    return resolved


def _record_run(config: ProjectConfig, run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    _latest_marker(config).write_text(run_dir.name, encoding="utf-8")


def _environment_versions() -> dict[str, str]:
    packages = ["joblib", "matplotlib", "numpy", "pandas", "PyYAML", "requests", "scikit-learn", "yfinance"]
    result = {"python": sys.version.split()[0], "platform": platform.platform()}
    for package in packages:
        try:
            result[package] = version(package)
        except PackageNotFoundError:
            result[package] = "not-installed"
    return result


def _load_monthly(config: ProjectConfig) -> pd.DataFrame:
    return read_table(config.path("monthly_prices"), date_columns=("date",))


def _load_model_table(config: ProjectConfig) -> pd.DataFrame:
    return read_table(config.path("model_table"))


def _run_data(config: ProjectConfig, force_download: bool) -> dict[str, Any]:
    daily, monthly = prepare_data(config, force_download=force_download)
    return {
        "daily_rows": len(daily),
        "monthly_rows": len(monthly),
        "assets": int(monthly["ticker"].nunique()),
    }


def _run_features(config: ProjectConfig) -> dict[str, Any]:
    table = build_model_table(_load_monthly(config), config)
    return {
        "model_rows": len(table),
        "signal_months": int(table["signal_date"].nunique()),
        "assets": int(table["ticker"].nunique()),
    }


def _run_model(config: ProjectConfig, run_dir: Path) -> dict[str, Any]:
    table = assign_splits(_load_model_table(config), config)
    predictions, alpha_results, _ = fit_and_predict(table, config, run_dir)
    split_summary = (
        table.groupby("split", as_index=False)
        .agg(
            rows=("ticker", "size"),
            assets=("ticker", "nunique"),
            first_signal=("signal_date", "min"),
            last_signal=("signal_date", "max"),
        )
    )
    write_table(split_summary, run_dir / "split_summary.csv")
    return {
        "prediction_rows": len(predictions),
        "selected_alpha": float(alpha_results.iloc[0]["alpha"]),
        "test_rows": int(predictions["split"].eq("test").sum()),
    }


def _run_backtest(config: ProjectConfig, run_dir: Path) -> dict[str, Any]:
    predictions = read_table(run_dir / "predictions.csv")
    positions, trades, portfolio = run_backtest(predictions, config)
    write_table(positions, run_dir / "positions.csv")
    write_table(trades, run_dir / "trades.csv")
    write_table(portfolio, run_dir / "portfolio_returns.csv")
    return {
        "backtest_months": len(portfolio),
        "average_selected_assets": float(portfolio["selected_assets"].mean()),
        "average_turnover": float(portfolio["turnover"].mean()),
    }


def _run_evaluate(config: ProjectConfig, run_dir: Path) -> dict[str, Any]:
    portfolio = read_table(run_dir / "portfolio_returns.csv")
    predictions = read_table(run_dir / "predictions.csv")
    target_column = str(config.section("model").get("target_column", "target_return_1m"))
    train_mean = float(
        predictions.loc[
            predictions["split"].eq("train") & predictions[target_column].notna(),
            target_column,
        ].mean()
    )
    prediction_results = prediction_metrics(predictions, train_mean, target_column)
    write_table(prediction_results, run_dir / "prediction_metrics.csv")
    plot_test_predictions(
        predictions,
        target_column,
        run_dir / "figures" / "test_prediction_scatter.png",
    )
    annualization = int(config.section("evaluation")["annualization_factor"])
    metrics, curves, annual = evaluate_portfolio(portfolio, annualization, run_dir / "figures")
    write_table(metrics, run_dir / "metrics.csv")
    write_table(curves, run_dir / "cumulative_returns.csv")
    write_table(annual, run_dir / "annual_performance.csv")
    strategy = metrics.loc[metrics["portfolio"].eq("combined_momentum")].iloc[0]
    return {
        "annualized_return": float(strategy["annualized_return"]),
        "sharpe_ratio": float(strategy["sharpe_ratio"]),
        "max_drawdown": float(strategy["max_drawdown"]),
    }


def run_pipeline(
    config: ProjectConfig,
    stage: str = "all",
    run_id: str | None = None,
    force_download: bool = False,
) -> tuple[Path | None, dict[str, Any]]:
    if stage not in VALID_STAGES:
        raise ValueError(f"Unknown stage={stage}; choose from {sorted(VALID_STAGES)}")
    ensure_project_directories(config)
    summary: dict[str, Any] = {"stage": stage}
    run_dir: Path | None = None

    if stage in {"all", "data"}:
        summary["data"] = _run_data(config, force_download)
    if stage in {"all", "features"}:
        summary["features"] = _run_features(config)
    if stage in {"all", "model"}:
        run_dir = _resolve_run_dir(config, run_id, create=True)
        _record_run(config, run_dir)
        summary["model"] = _run_model(config, run_dir)
    elif stage in {"backtest", "evaluate"}:
        run_dir = _resolve_run_dir(config, run_id, create=False)
    if stage in {"all", "backtest"}:
        if run_dir is None:
            raise RuntimeError("Internal error: no run directory for backtest")
        summary["backtest"] = _run_backtest(config, run_dir)
    if stage in {"all", "evaluate"}:
        if run_dir is None:
            raise RuntimeError("Internal error: no run directory for evaluation")
        summary["evaluation"] = _run_evaluate(config, run_dir)

    if run_dir is not None:
        metadata = {
            "run_id": run_dir.name,
            "config_path": str(config.config_path),
            "config_sha256": file_sha256(config.config_path),
            "model_table_sha256": file_sha256(config.path("model_table")),
            "settings": config.values,
            "environment": _environment_versions(),
            "summary": summary,
        }
        write_json(metadata, run_dir / "run_metadata.json")
    return run_dir, summary

