from __future__ import annotations

import numpy as np
import pandas as pd

from .config import ProjectConfig
from .io import write_table


def feature_columns(config: ProjectConfig) -> list[str]:
    settings = config.section("features")
    if settings.get("mapping") == "trend_rank_relative_strength_long_risk":
        relative_window = int(settings["relative_strength_window_months"])
        return [
            "rank_current_trend_1m",
            f"relative_strength_{relative_window}m",
            "risk_volatility_6m",
        ]
    if settings.get("mapping") == "trend_rank_relative_strength_and_risk":
        relative_window = int(settings["relative_strength_window_months"])
        return [
            "rank_current_trend_1m",
            f"relative_strength_{relative_window}m",
            "risk_volatility_1m",
            "risk_volatility_6m",
        ]
    if settings.get("mapping") == "ranked_current_trend_and_relative_strength":
        relative_window = int(settings["relative_strength_window_months"])
        return ["rank_current_trend_1m", f"relative_strength_{relative_window}m"]
    if settings.get("mapping") == "current_trend_and_relative_strength":
        relative_window = int(settings["relative_strength_window_months"])
        return ["current_trend_1m", f"relative_strength_{relative_window}m"]
    if settings.get("mapping") == "path_trend_and_relative_strength":
        path_window = int(settings["path_trend_window_months"])
        relative_window = int(settings["relative_strength_window_months"])
        return [f"own_trend_{path_window}m", f"relative_strength_{relative_window}m"]
    composite = settings.get("composite_momentum")
    if composite:
        return [str(composite.get("name", "momentum_score"))]
    windows = [int(value) for value in settings["trend_windows_months"]]
    columns = [f"trend_{window}m" for window in windows]
    if settings.get("include_cross_sectional_ranks", True):
        columns.extend(f"rank_trend_{window}m" for window in windows)
    if settings.get("include_volatility", True):
        columns.append(f"volatility_{int(settings['volatility_window_months'])}m")
    return columns


def _cross_sectional_winsorize(series: pd.Series, lower: float, upper: float) -> pd.Series:
    if series.notna().sum() < 3:
        return series
    return series.clip(series.quantile(lower), series.quantile(upper))


def _signed_log_price_trend(values: np.ndarray) -> float:
    """Return annualised log-price slope multiplied by its linear-fit R-squared."""
    prices = np.asarray(values, dtype=float)
    if len(prices) < 2 or not np.isfinite(prices).all() or (prices <= 0).any():
        return np.nan
    y = np.log(prices)
    x = np.arange(len(y), dtype=float)
    x_centered = x - x.mean()
    y_centered = y - y.mean()
    denominator = float(np.square(x_centered).sum())
    if denominator == 0:
        return np.nan
    slope = float((x_centered * y_centered).sum() / denominator)
    fitted = y.mean() + slope * x_centered
    total_variation = float(np.square(y_centered).sum())
    if total_variation == 0:
        return 0.0
    residual_variation = float(np.square(y - fitted).sum())
    r_squared = max(0.0, min(1.0, 1.0 - residual_variation / total_variation))
    return 12.0 * slope * r_squared


def build_model_table(monthly: pd.DataFrame, config: ProjectConfig) -> pd.DataFrame:
    frame = monthly.sort_values(["ticker", "date"]).copy()
    configured_candidates = config.section("data").get("tickers", frame["ticker"].unique())
    candidates = set(map(str, configured_candidates))
    frame = frame.loc[frame["ticker"].isin(candidates)].copy()
    settings = config.section("features")
    lower = float(settings.get("winsorize_lower", 0.01))
    upper = float(settings.get("winsorize_upper", 0.99))
    component_columns: list[str] = []
    if settings.get("mapping") in {
        "current_trend_and_relative_strength",
        "ranked_current_trend_and_relative_strength",
        "trend_rank_relative_strength_and_risk",
        "trend_rank_relative_strength_long_risk",
    }:
        if "current_trend_1m" not in frame.columns:
            raise ValueError(
                "Monthly prices are missing current_trend_1m; rerun the data stage with this mapping"
            )
        relative_window = int(settings["relative_strength_window_months"])
        relative_return = f"relative_return_{relative_window}m"
        relative_strength = f"relative_strength_{relative_window}m"
        frame[relative_return] = frame.groupby("ticker")["adjusted_close"].pct_change(
            relative_window, fill_method=None
        )
        frame[relative_return] = frame.groupby("date")[relative_return].transform(
            lambda values: _cross_sectional_winsorize(values, lower, upper)
        )
        frame[relative_strength] = frame.groupby("date")[relative_return].rank(pct=True) - 0.5
        component_columns = [relative_return]
        if settings.get("mapping") in {
            "ranked_current_trend_and_relative_strength",
            "trend_rank_relative_strength_and_risk",
            "trend_rank_relative_strength_long_risk",
        }:
            frame["rank_current_trend_1m"] = (
                frame.groupby("date")["current_trend_1m"].rank(pct=True) - 0.5
            )
            component_columns = ["current_trend_1m", relative_return]
        if settings.get("mapping") == "trend_rank_relative_strength_and_risk":
            missing_risk = {
                "risk_volatility_1m",
                "risk_volatility_6m",
            }.difference(frame.columns)
            if missing_risk:
                raise ValueError(
                    "Monthly prices are missing risk features; rerun the data stage: "
                    f"{sorted(missing_risk)}"
                )
        if settings.get("mapping") == "trend_rank_relative_strength_long_risk":
            if "risk_volatility_6m" not in frame.columns:
                raise ValueError(
                    "Monthly prices are missing risk_volatility_6m; rerun the data stage"
                )
    elif settings.get("mapping") == "path_trend_and_relative_strength":
        path_window = int(settings["path_trend_window_months"])
        relative_window = int(settings["relative_strength_window_months"])
        own_trend = f"own_trend_{path_window}m"
        relative_return = f"relative_return_{relative_window}m"
        relative_strength = f"relative_strength_{relative_window}m"
        frame[own_trend] = (
            frame.groupby("ticker")["adjusted_close"]
            .rolling(path_window, min_periods=path_window)
            .apply(_signed_log_price_trend, raw=True)
            .reset_index(level=0, drop=True)
        )
        frame[relative_return] = frame.groupby("ticker")["adjusted_close"].pct_change(
            relative_window, fill_method=None
        )
        for column in (own_trend, relative_return):
            frame[column] = frame.groupby("date")[column].transform(
                lambda values: _cross_sectional_winsorize(values, lower, upper)
            )
        frame[relative_strength] = frame.groupby("date")[relative_return].rank(pct=True) - 0.5
        component_columns = [relative_return]
    else:
        windows = [int(value) for value in settings["trend_windows_months"]]
        for window in windows:
            name = f"trend_{window}m"
            frame[name] = frame.groupby("ticker")["adjusted_close"].pct_change(
                window, fill_method=None
            )

        include_volatility = settings.get("include_volatility", True)
        volatility_window = int(settings["volatility_window_months"])
        volatility_name = f"volatility_{volatility_window}m"
        if include_volatility:
            frame[volatility_name] = (
                frame.groupby("ticker")["return_1m"]
                .rolling(volatility_window, min_periods=volatility_window)
                .std()
                .reset_index(level=0, drop=True)
            )

        base_features = [f"trend_{window}m" for window in windows]
        if include_volatility:
            base_features.append(volatility_name)
        for column in base_features:
            frame[column] = frame.groupby("date")[column].transform(
                lambda values: _cross_sectional_winsorize(values, lower, upper)
            )

        if settings.get("include_cross_sectional_ranks", True):
            for window in windows:
                source = f"trend_{window}m"
                frame[f"rank_trend_{window}m"] = frame.groupby("date")[source].rank(pct=True)

        composite = settings.get("composite_momentum")
        if composite:
            if not settings.get("include_cross_sectional_ranks", True):
                raise ValueError("Composite momentum requires cross-sectional ranks")
            weights = {
                int(window): float(weight)
                for window, weight in composite["rank_weights"].items()
            }
            missing_windows = set(weights).difference(windows)
            if missing_windows:
                raise ValueError(
                    "Composite momentum windows are missing from trend_windows_months: "
                    f"{sorted(missing_windows)}"
                )
            if any(weight < 0 for weight in weights.values()) or sum(weights.values()) <= 0:
                raise ValueError(
                    "Composite momentum weights must be non-negative and sum to more than zero"
                )
            composite_name = str(composite.get("name", "momentum_score"))
            total_weight = sum(weights.values())
            frame[composite_name] = sum(
                weight * frame[f"rank_trend_{window}m"]
                for window, weight in weights.items()
            ) / total_weight
            component_columns = [
                column
                for window in weights
                for column in (f"trend_{window}m", f"rank_trend_{window}m")
            ]

    required_targets = {"execution_date", "return_date", "target_return_1m"}
    missing_targets = required_targets.difference(frame.columns)
    if missing_targets:
        raise ValueError(f"Monthly price table is missing execution fields: {sorted(missing_targets)}")
    frame["target_excess_return_1m"] = (
        frame["target_return_1m"]
        - frame.groupby("date")["target_return_1m"].transform("mean")
    )
    frame = frame.rename(columns={"date": "signal_date"})

    features = feature_columns(config)
    frame.replace([np.inf, -np.inf], np.nan, inplace=True)
    complete_features = frame[features].notna().all(axis=1)
    minimum_assets = int(config.section("data").get("minimum_assets_per_month", 2))
    counts = frame.loc[complete_features].groupby("signal_date")["ticker"].transform("count")
    keep_index = frame.loc[complete_features].index[counts >= minimum_assets]
    output_columns = list(dict.fromkeys([
        "signal_date",
        "execution_date",
        "return_date",
        "ticker",
        "adjusted_close",
        *component_columns,
        *features,
        "target_return_1m",
        "target_excess_return_1m",
    ]))
    output = frame.loc[keep_index, output_columns].copy()
    output = output.sort_values(["signal_date", "ticker"]).reset_index(drop=True)
    write_table(output, config.path("model_table"))
    return output

