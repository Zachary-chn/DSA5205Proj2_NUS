from __future__ import annotations

from datetime import datetime, timezone
import time

import numpy as np
import pandas as pd

from .config import ProjectConfig
from .io import write_table


REQUIRED_PRICE_COLUMNS = {"date", "ticker", "adjusted_close"}


def _download_tickers(settings: dict) -> list[str]:
    ordered = [*settings["tickers"], *settings.get("benchmark_tickers", [])]
    return list(dict.fromkeys(map(str, ordered)))


def _annualized_log_price_slope(values: np.ndarray) -> float:
    prices = np.asarray(values, dtype=float)
    if len(prices) < 2 or not np.isfinite(prices).all() or (prices <= 0).any():
        return np.nan
    y = np.log(prices)
    x = np.arange(len(y), dtype=float)
    denominator = float(np.square(x - x.mean()).sum())
    if denominator == 0:
        return np.nan
    daily_slope = float(((x - x.mean()) * (y - y.mean())).sum() / denominator)
    return 252.0 * daily_slope


def download_yahoo_prices(config: ProjectConfig) -> pd.DataFrame:
    client = str(config.section("data").get("client", "yahoo_chart"))
    if client == "yahoo_chart":
        return download_yahoo_chart_prices(config)
    if client != "yfinance":
        raise ValueError(f"Unsupported Yahoo Finance client: {client}")
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("client=yfinance requires installation of the optional yfinance dependency") from exc

    settings = config.section("data")
    tickers = _download_tickers(settings)
    downloaded = yf.download(
        tickers=tickers,
        start=settings["start"],
        end=settings["end"],
        auto_adjust=False,
        actions=True,
        progress=False,
        threads=True,
        group_by="column",
    )
    if downloaded.empty:
        raise RuntimeError("Yahoo Finance returned no rows")

    def extract_field(field: str, output_name: str) -> pd.DataFrame | None:
        if isinstance(downloaded.columns, pd.MultiIndex):
            if field not in downloaded.columns.get_level_values(0):
                return None
            wide = downloaded[field].copy()
        else:
            if field not in downloaded.columns:
                return None
            wide = downloaded[[field]].rename(columns={field: tickers[0]})
        if isinstance(wide, pd.Series):
            wide = wide.to_frame(name=tickers[0])
        wide.index = pd.to_datetime(wide.index).tz_localize(None)
        wide.index.name = "date"
        return wide.reset_index().melt(id_vars="date", var_name="ticker", value_name=output_name)

    adjusted = extract_field("Adj Close", "adjusted_close")
    if adjusted is None:
        adjusted = extract_field("Close", "adjusted_close")
    if adjusted is None:
        raise RuntimeError("Yahoo Finance output contains neither Adj Close nor Close")

    long = adjusted
    for field, output_name in [
        ("Close", "raw_close"),
        ("Dividends", "dividends"),
        ("Stock Splits", "stock_splits"),
    ]:
        extracted = extract_field(field, output_name)
        if extracted is not None:
            long = long.merge(extracted, on=["date", "ticker"], how="left")
    long["ticker"] = long["ticker"].astype(str)
    long["source"] = "yahoo_finance"
    long["downloaded_at_utc"] = datetime.now(timezone.utc).isoformat()
    long = long.dropna(subset=["adjusted_close"]).sort_values(["date", "ticker"]).reset_index(drop=True)
    return long


def download_yahoo_chart_prices(config: ProjectConfig) -> pd.DataFrame:
    """Download Yahoo Finance chart data when the optional yfinance package is absent."""
    import requests

    settings = config.section("data")
    period1 = int(pd.Timestamp(settings["start"], tz="UTC").timestamp())
    period2 = int(pd.Timestamp(settings["end"], tz="UTC").timestamp())
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 combined-momentum-coursework/0.1"})
    frames: list[pd.DataFrame] = []

    for ticker in _download_tickers(settings):
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {
            "period1": period1,
            "period2": period2,
            "interval": "1d",
            "events": "div,splits",
            "includeAdjustedClose": "true",
        }
        response = None
        for attempt in range(3):
            response = session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                break
            if response.status_code not in {429, 500, 502, 503, 504}:
                response.raise_for_status()
            time.sleep(1.0 * (attempt + 1))
        if response is None or response.status_code != 200:
            status = None if response is None else response.status_code
            raise RuntimeError(f"Yahoo Finance download failed for {ticker}; status={status}")

        payload = response.json().get("chart", {})
        if payload.get("error"):
            raise RuntimeError(f"Yahoo Finance returned an error for {ticker}: {payload['error']}")
        result = (payload.get("result") or [None])[0]
        if not result or not result.get("timestamp"):
            raise RuntimeError(f"Yahoo Finance returned no observations for {ticker}")

        timestamps = pd.to_datetime(result["timestamp"], unit="s", utc=True).tz_convert(None).normalize()
        quote = result["indicators"]["quote"][0]
        adjusted_blocks = result["indicators"].get("adjclose") or []
        adjusted = adjusted_blocks[0].get("adjclose") if adjusted_blocks else quote.get("close")
        frame = pd.DataFrame(
            {
                "date": timestamps,
                "ticker": ticker,
                "adjusted_close": adjusted,
                "raw_close": quote.get("close"),
                "dividends": 0.0,
                "stock_splits": 0.0,
            }
        )

        events = result.get("events") or {}
        for event in events.get("dividends", {}).values():
            event_date = pd.to_datetime(event["date"], unit="s", utc=True).tz_convert(None).normalize()
            frame.loc[frame["date"].eq(event_date), "dividends"] = float(event.get("amount", 0.0))
        for event in events.get("splits", {}).values():
            event_date = pd.to_datetime(event["date"], unit="s", utc=True).tz_convert(None).normalize()
            numerator = float(event.get("numerator", 0.0))
            denominator = float(event.get("denominator", 1.0))
            frame.loc[frame["date"].eq(event_date), "stock_splits"] = numerator / denominator
        frames.append(frame)

    long = pd.concat(frames, ignore_index=True)
    long["source"] = "yahoo_finance_chart"
    long["downloaded_at_utc"] = datetime.now(timezone.utc).isoformat()
    return long.dropna(subset=["adjusted_close"]).sort_values(["date", "ticker"]).reset_index(drop=True)


def validate_daily_prices(frame: pd.DataFrame, config: ProjectConfig) -> pd.DataFrame:
    missing = REQUIRED_PRICE_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Daily price file is missing columns: {sorted(missing)}")

    checked = frame.copy()
    checked["date"] = pd.to_datetime(checked["date"])
    checked["ticker"] = checked["ticker"].astype(str)
    checked["adjusted_close"] = pd.to_numeric(checked["adjusted_close"], errors="coerce")

    if checked.duplicated(["date", "ticker"]).any():
        raise ValueError("Daily price file contains duplicate date-ticker rows")
    if checked["adjusted_close"].isna().any() or (checked["adjusted_close"] <= 0).any():
        raise ValueError("Daily adjusted_close must be present and strictly positive")

    settings = config.section("data")
    expected = set(_download_tickers(settings))
    observed = set(checked["ticker"].unique())
    absent = expected.difference(observed)
    if absent:
        raise ValueError(f"No observations found for configured tickers: {sorted(absent)}")

    date_count = checked["date"].nunique()
    coverage = checked.groupby("ticker")["date"].nunique().div(date_count)
    threshold = float(settings.get("minimum_ticker_coverage", 0.85))
    weak = coverage[coverage < threshold]
    if not weak.empty:
        detail = ", ".join(f"{ticker}={value:.1%}" for ticker, value in weak.items())
        raise ValueError(f"Ticker coverage below {threshold:.0%}: {detail}")

    return checked.sort_values(["date", "ticker"]).reset_index(drop=True)


def to_monthly_prices(daily: pd.DataFrame, config: ProjectConfig) -> pd.DataFrame:
    ordered = daily.sort_values(["ticker", "date"]).copy()
    mapping = config.section("features").get("mapping")
    include_current_trend = mapping in {
        "current_trend_and_relative_strength",
        "ranked_current_trend_and_relative_strength",
        "trend_rank_relative_strength_and_risk",
        "trend_rank_relative_strength_long_risk",
    }
    if include_current_trend:
        trend_days = int(config.section("features").get("current_trend_days", 21))
        ordered["current_trend_1m"] = (
            ordered.groupby("ticker")["adjusted_close"]
            .rolling(trend_days, min_periods=trend_days)
            .apply(_annualized_log_price_slope, raw=True)
            .reset_index(level=0, drop=True)
        )
    include_short_risk = mapping == "trend_rank_relative_strength_and_risk"
    include_long_risk = mapping in {
        "trend_rank_relative_strength_and_risk",
        "trend_rank_relative_strength_long_risk",
    }
    if include_short_risk or include_long_risk:
        risk_settings = config.section("features")
        short_days = int(risk_settings.get("risk_short_days", 21))
        long_days = int(risk_settings.get("risk_long_days", 126))
        ordered["return_1d"] = ordered.groupby("ticker")["adjusted_close"].pct_change(
            fill_method=None
        )
    if include_short_risk:
        ordered["risk_volatility_1m"] = (
            ordered.groupby("ticker")["return_1d"]
            .rolling(short_days, min_periods=short_days)
            .std()
            .reset_index(level=0, drop=True)
            * np.sqrt(252.0)
        )
    if include_long_risk:
        ordered["risk_volatility_6m"] = (
            ordered.groupby("ticker")["return_1d"]
            .rolling(long_days, min_periods=long_days)
            .std()
            .reset_index(level=0, drop=True)
            * np.sqrt(252.0)
        )
    ordered["execution_date"] = ordered.groupby("ticker")["date"].shift(-1)
    ordered["execution_price"] = ordered.groupby("ticker")["adjusted_close"].shift(-1)
    ordered["calendar_month"] = ordered["date"].dt.to_period("M")
    monthly = ordered.groupby(["ticker", "calendar_month"], as_index=False).tail(1)
    monthly_columns = ["date", "ticker", "adjusted_close", "execution_date", "execution_price"]
    if include_current_trend:
        monthly_columns.append("current_trend_1m")
    if include_short_risk:
        monthly_columns.append("risk_volatility_1m")
    if include_long_risk:
        monthly_columns.append("risk_volatility_6m")
    monthly = monthly[monthly_columns].copy()
    monthly["return_1m"] = monthly.groupby("ticker")["adjusted_close"].pct_change(fill_method=None)
    monthly["return_date"] = monthly.groupby("ticker")["execution_date"].shift(-1)
    next_execution_price = monthly.groupby("ticker")["execution_price"].shift(-1)
    monthly["target_return_1m"] = next_execution_price.div(monthly["execution_price"]).sub(1.0)

    minimum_history = int(config.section("data").get("minimum_history_months", 24))
    history = monthly.groupby("ticker")["date"].transform("count")
    monthly = monthly.loc[history >= minimum_history].copy()
    if monthly["ticker"].nunique() < int(config.section("data").get("minimum_assets_per_month", 2)):
        raise ValueError("Too few assets remain after the minimum-history check")
    return monthly.sort_values(["date", "ticker"]).reset_index(drop=True)


def prepare_data(config: ProjectConfig, force_download: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    settings = config.section("data")
    raw_path = config.path("raw_prices")

    should_download = bool(settings.get("download", True)) and (force_download or not raw_path.exists())
    if should_download:
        if settings.get("source") != "yahoo_finance":
            raise ValueError(f"No downloader implemented for source={settings.get('source')}")
        daily = download_yahoo_prices(config)
        write_table(daily, raw_path)
    else:
        if not raw_path.exists():
            raise FileNotFoundError(
                f"download=false but the required raw file does not exist: {raw_path}"
            )
        daily = pd.read_csv(raw_path, parse_dates=["date"])

    daily = validate_daily_prices(daily, config)
    monthly = to_monthly_prices(daily, config)
    write_table(monthly, config.path("monthly_prices"))
    return daily, monthly



