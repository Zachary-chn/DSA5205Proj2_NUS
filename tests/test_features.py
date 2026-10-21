from pathlib import Path

import numpy as np
import pandas as pd

from combined_momentum.config import ProjectConfig
from combined_momentum.data import _annualized_log_price_slope
from combined_momentum.features import build_model_table, feature_columns


def make_config(tmp_path: Path) -> ProjectConfig:
    values = {
        "project": {"name": "test", "random_seed": 5205},
        "paths": {
            "raw_prices": "data/raw.csv",
            "monthly_prices": "data/monthly.csv",
            "model_table": "data/model.csv",
            "artifacts_dir": "artifacts",
        },
        "data": {"minimum_assets_per_month": 3},
        "features": {
            "trend_windows_months": [3, 6, 12],
            "volatility_window_months": 3,
            "include_cross_sectional_ranks": True,
            "winsorize_lower": 0.01,
            "winsorize_upper": 0.99,
        },
        "split": {},
        "model": {},
        "strategy": {},
        "evaluation": {},
    }
    return ProjectConfig(values=values, root=tmp_path, config_path=tmp_path / "config.yaml")


def test_features_use_trailing_information_and_forward_target(tmp_path):
    config = make_config(tmp_path)
    dates = pd.date_range("2018-01-31", periods=24, freq="ME")
    rows = []
    for number, ticker in enumerate(["A", "B", "C", "D"], start=1):
        prices = 100 * np.cumprod(np.repeat(1 + number / 100, len(dates)))
        for date, price in zip(dates, prices):
            rows.append({"date": date, "ticker": ticker, "adjusted_close": price})
    monthly = pd.DataFrame(rows).sort_values(["ticker", "date"])
    monthly["return_1m"] = monthly.groupby("ticker")["adjusted_close"].pct_change(fill_method=None)
    monthly["execution_date"] = monthly["date"] + pd.offsets.BDay(1)
    monthly["execution_price"] = monthly["adjusted_close"]
    monthly["return_date"] = monthly.groupby("ticker")["execution_date"].shift(-1)
    monthly["target_return_1m"] = monthly.groupby("ticker")["return_1m"].shift(-1)

    table = build_model_table(monthly, config)
    assert set(feature_columns(config)).issubset(table.columns)
    assert table.groupby("signal_date")["ticker"].nunique().min() >= 3
    labelled = table.dropna(subset=["target_return_1m"])
    assert (labelled["execution_date"] > labelled["signal_date"]).all()
    assert (labelled["return_date"] > labelled["execution_date"]).all()
    assert table.groupby("signal_date")["rank_trend_12m"].max().eq(1.0).all()
    monthly_excess_mean = labelled.groupby("signal_date")["target_excess_return_1m"].mean()
    assert np.allclose(monthly_excess_mean, 0.0, atol=1e-12)


def test_composite_momentum_is_fixed_average_of_ranked_trends(tmp_path):
    config = make_config(tmp_path)
    config.values["features"]["composite_momentum"] = {
        "name": "momentum_score",
        "rank_weights": {6: 0.5, 12: 0.5},
    }
    dates = pd.date_range("2018-01-31", periods=24, freq="ME")
    rows = []
    for number, ticker in enumerate(["A", "B", "C", "D"], start=1):
        prices = 100 * np.cumprod(np.repeat(1 + number / 100, len(dates)))
        for date, price in zip(dates, prices):
            rows.append({"date": date, "ticker": ticker, "adjusted_close": price})
    monthly = pd.DataFrame(rows).sort_values(["ticker", "date"])
    monthly["return_1m"] = monthly.groupby("ticker")["adjusted_close"].pct_change(fill_method=None)
    monthly["execution_date"] = monthly["date"] + pd.offsets.BDay(1)
    monthly["execution_price"] = monthly["adjusted_close"]
    monthly["return_date"] = monthly.groupby("ticker")["execution_date"].shift(-1)
    monthly["target_return_1m"] = monthly.groupby("ticker")["return_1m"].shift(-1)

    table = build_model_table(monthly, config)
    expected = 0.5 * table["rank_trend_6m"] + 0.5 * table["rank_trend_12m"]
    assert feature_columns(config) == ["momentum_score"]
    assert np.allclose(table["momentum_score"], expected)


def test_path_trend_mapping_separates_direction_from_relative_strength(tmp_path):
    config = make_config(tmp_path)
    config.values["features"] = {
        "mapping": "path_trend_and_relative_strength",
        "path_trend_window_months": 12,
        "relative_strength_window_months": 12,
        "winsorize_lower": 0.01,
        "winsorize_upper": 0.99,
    }
    dates = pd.date_range("2018-01-31", periods=24, freq="ME")
    paths = {
        "UP": np.linspace(100, 140, len(dates)),
        "FLAT": np.repeat(100.0, len(dates)),
        "DOWN": np.linspace(140, 100, len(dates)),
        "NOISY": 100 + 15 * np.sin(np.arange(len(dates))) + np.linspace(0, 10, len(dates)),
    }
    rows = [
        {"date": date, "ticker": ticker, "adjusted_close": price}
        for ticker, prices in paths.items()
        for date, price in zip(dates, prices)
    ]
    monthly = pd.DataFrame(rows).sort_values(["ticker", "date"])
    monthly["return_1m"] = monthly.groupby("ticker")["adjusted_close"].pct_change(fill_method=None)
    monthly["execution_date"] = monthly["date"] + pd.offsets.BDay(1)
    monthly["execution_price"] = monthly["adjusted_close"]
    monthly["return_date"] = monthly.groupby("ticker")["execution_date"].shift(-1)
    monthly["target_return_1m"] = monthly.groupby("ticker")["return_1m"].shift(-1)

    table = build_model_table(monthly, config)
    latest = table.loc[table["signal_date"].eq(table["signal_date"].max())].set_index("ticker")
    assert feature_columns(config) == ["own_trend_12m", "relative_strength_12m"]
    assert latest.loc["UP", "own_trend_12m"] > 0
    assert latest.loc["DOWN", "own_trend_12m"] < 0
    assert abs(latest.loc["FLAT", "own_trend_12m"]) < 1e-12
    assert latest["relative_strength_12m"].nunique() == 4


def test_one_month_daily_trend_slope_has_the_correct_direction():
    assert _annualized_log_price_slope(np.linspace(100, 110, 21)) > 0
    assert _annualized_log_price_slope(np.linspace(110, 100, 21)) < 0
    assert abs(_annualized_log_price_slope(np.repeat(100.0, 21))) < 1e-12

