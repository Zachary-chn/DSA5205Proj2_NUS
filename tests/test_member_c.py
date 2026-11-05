"""Synthetic accounting tests; no final-holdout results are used to choose behaviour."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from combined_momentum.config import ProjectConfig
from combined_momentum.strategy import build_positions, build_trades
from combined_momentum.backtest import run_backtest
from combined_momentum.evaluation import performance_metrics, evaluate_portfolio
from combined_momentum.pipeline import run_pipeline


@pytest.fixture
def case(tmp_path):
    values = {
        "strategy": {"top_k": 2, "require_positive_prediction": True,
                     "transaction_cost_bps": 10, "cash_return_annual": 0},
        "data": {"tickers": ["A", "B", "C"]},
        "evaluation": {"benchmark_ticker": "SPY", "annualization_factor": 12},
        "paths": {"monthly_prices": "monthly.csv", "raw_prices": "raw.csv",
                  "model_table": "model.csv", "artifacts_dir": "artifacts"},
        "project": {}, "features": {}, "split": {}, "model": {},
    }
    config = ProjectConfig(values, tmp_path, tmp_path / "config.yaml")
    config.config_path.write_text("synthetic configuration")
    rows = []
    for month, scores, returns in [
        ("2020-01-31", [.03, .02, -.01], [.20, -.10, .04]),
        ("2020-02-28", [.03, .02, 0], [.05, .02, -.01]),
        ("2020-03-31", [-.01, 0, -.02], [-.03, .04, .02]),
    ]:
        signal = pd.Timestamp(month)
        execution = signal + pd.offsets.BDay(1)
        end = (signal.to_period("M") + 1).to_timestamp("M") + pd.offsets.BDay(1)
        for ticker, score, ret in zip(["A", "B", "C"], scores, returns):
            rows.append(dict(signal_date=signal, execution_date=execution, return_date=end,
                             ticker=ticker, split="test", predicted_return=score, target_return_1m=ret))
    frame = pd.DataFrame(rows)
    benchmark = frame.groupby("signal_date", as_index=False).first().rename(columns={"signal_date": "date"})
    benchmark["ticker"] = "SPY"
    benchmark["target_return_1m"] = [.1, -.05, .02]
    benchmark.to_csv(config.path("monthly_prices"), index=False)
    return config, frame


def test_positions_cash_zeros_ties_and_excludes_other_splits(case):
    config, frame = case
    extra = frame.iloc[:1].assign(split="validation", predicted_return=1e9)
    frame.loc[frame.signal_date.eq(frame.signal_date.min()), "predicted_return"] = .02
    p = build_positions(pd.concat([frame, extra]), config)
    first = p[p.signal_date.eq(p.signal_date.min())]
    assert first.loc[first.selected, "ticker"].tolist() == ["A", "B"]
    assert set(p.target_weight) == {0, .5}
    last = p[p.signal_date.eq(p.signal_date.max())]
    assert last.target_weight.sum() == 0
    assert last.cash_weight.eq(1).all()
    assert (p.groupby("signal_date").target_weight.sum() + p.groupby("signal_date").cash_weight.first()).eq(1).all()


@pytest.mark.parametrize("column,value", [("target_return_1m", np.nan), ("predicted_return", np.inf)])
def test_missing_values_fail_instead_of_changing_selection(case, column, value):
    config, frame = case
    frame.loc[0, column] = value
    with pytest.raises(ValueError, match="finite"):
        build_positions(frame, config)


def test_drifted_turnover_self_financing_and_exit(case):
    config, frame = case
    p, trades, portfolio = run_backtest(frame, config)
    by_date = list(trades.groupby("signal_date"))
    first, second, third = [g.set_index("ticker") for _, g in by_date]
    assert first.previous_weight.eq(0).all()
    assert first.estimated_cost.sum() == pytest.approx(.001 / 1.001)
    assert second.loc["A", "previous_weight"] == pytest.approx(.5 * 1.2 / 1.05)
    assert second.loc["B", "previous_weight"] == pytest.approx(.5 * .9 / 1.05)
    assert second.absolute_weight_change.sum() > .14  # same names still require trades
    assert third.target_weight.sum() == 0
    assert third.absolute_weight_change.sum() == pytest.approx(1)
    assert third.estimated_cost.sum() == pytest.approx(.001)
    assert portfolio.strategy_return.iloc[2] == pytest.approx(-.001)
    for _, group in trades.groupby("signal_date"):
        c = group.estimated_cost.sum()
        assert group.estimated_cost.sum() == pytest.approx(.001 * group.absolute_weight_change.sum())
        assert np.allclose(group.executed_weight, (1 - c) * group.target_weight)
        # cash after trades pays all costs; no external cash or leverage.
        previous_cash = 1 - group.previous_weight.sum()
        final_cash = previous_cash - group.weight_change.sum() - c
        assert final_cash == pytest.approx((1 - c) * (1 - group.target_weight.sum()))
    assert portfolio.strategy_return.iloc[0] == pytest.approx(1.05 / 1.001 - 1)


def test_cash_interest_affects_drift(case):
    config, frame = case
    p = build_positions(frame, config)
    p.loc[p.ticker.eq("B"), "target_weight"] = 0
    trades = build_trades(p, 0, monthly_cash_return=.01)
    second = trades[trades.signal_date.eq(pd.Timestamp("2020-02-28"))].set_index("ticker")
    assert second.loc["A", "previous_weight"] == pytest.approx(.5 * 1.2 / (1 + .5*.2 + .5*.01))


def test_no_lookahead_in_positions_and_current_trades(case):
    config, frame = case
    p1, t1, _ = run_backtest(frame, config)
    altered = frame.copy()
    altered.loc[altered.signal_date.ge(pd.Timestamp("2020-02-28")), "target_return_1m"] = .8
    p2, t2, _ = run_backtest(altered, config)
    pd.testing.assert_series_equal(p1.target_weight, p2.target_weight)
    pd.testing.assert_frame_equal(t1[t1.signal_date.le(pd.Timestamp("2020-02-28"))],
                                  t2[t2.signal_date.le(pd.Timestamp("2020-02-28"))])


def test_benchmarks_equal_weight_and_buy_hold_with_same_entry_cost(case):
    config, frame = case
    _, _, result = run_backtest(frame, config)
    assert result.gross_equal_weight_return.iloc[0] == pytest.approx((.2 - .1 + .04) / 3)
    assert result.equal_weight_return.iloc[0] == pytest.approx((1 + (.2 - .1 + .04)/3) / 1.001 - 1)
    assert result.equal_weight_turnover.iloc[1] > 0
    assert result.benchmark_return.iloc[0] == pytest.approx(1.1 / 1.001 - 1)
    assert result.benchmark_return.iloc[1] == pytest.approx(-.05)
    assert result.benchmark_turnover.iloc[1:].eq(0).all()
    assert len(result) == 3


@pytest.mark.parametrize("failure", ["missing", "nan", "duplicate", "dates"])
def test_benchmark_errors_are_explicit(case, failure):
    config, frame = case
    monthly = pd.read_csv(config.path("monthly_prices"))
    if failure == "missing":
        monthly = monthly.iloc[1:]
    elif failure == "nan":
        monthly.loc[0, "target_return_1m"] = np.nan
    elif failure == "duplicate":
        monthly = pd.concat([monthly, monthly.iloc[:1]])
    else:
        monthly.loc[0, "execution_date"] = "2020-02-04"
    monthly.to_csv(config.path("monthly_prices"), index=False)
    with pytest.raises(ValueError, match="[Bb]enchmark"):
        run_backtest(frame, config)


@pytest.mark.parametrize("failure", ["same_close", "overlap", "missing_asset", "duplicate"])
def test_invalid_alignment_and_universe_rejected(case, failure):
    config, frame = case
    if failure == "same_close":
        frame.loc[0, "execution_date"] = frame.loc[0, "signal_date"]
    elif failure == "overlap":
        frame.loc[frame.signal_date.eq(frame.signal_date.min()), "return_date"] = pd.Timestamp("2020-03-03")
    elif failure == "missing_asset":
        frame = frame.iloc[1:]
    else:
        frame = pd.concat([frame, frame.iloc[:1]])
    with pytest.raises(ValueError):
        run_backtest(frame, config)


def test_metrics_initial_loss_compounding_volatility_and_sharpe():
    returns = pd.Series([-.1, .2, -.05])
    m = performance_metrics(returns, 12)
    assert m["cumulative_return"] == pytest.approx(.9 * 1.2 * .95 - 1)
    assert m["annualized_return"] == pytest.approx((.9 * 1.2 * .95)**4 - 1)
    assert m["annualized_volatility"] == pytest.approx(returns.std(ddof=1) * np.sqrt(12))
    assert m["sharpe_ratio"] == pytest.approx(returns.mean() / returns.std(ddof=1) * np.sqrt(12))
    assert m["max_drawdown"] == pytest.approx(-.1)
    assert performance_metrics(pd.Series([0., 0.]), 12)["max_drawdown"] == 0
    assert np.isnan(performance_metrics(pd.Series([0., 0.]), 12)["sharpe_ratio"])
    assert performance_metrics(pd.Series(dtype=float), 12)["observations"] == 0
    with pytest.raises(ValueError, match="finite"):
        performance_metrics(pd.Series([.01, np.nan]), 12)


def test_figures_curves_and_annual_results(case, tmp_path):
    config, frame = case
    _, _, portfolio = run_backtest(frame, config)
    metrics, curves, annual = evaluate_portfolio(portfolio, 12, tmp_path / "figures")
    assert len(curves) == len(portfolio) + 1
    assert curves.wealth_combined_momentum.iloc[0] == 1
    assert curves.return_date.iloc[0] == portfolio.execution_date.iloc[0]
    assert curves.drawdown_combined_momentum.min() == pytest.approx(metrics.max_drawdown.iloc[0])
    assert set(annual.months) == {3}
    for name in ["equity_curve.png", "drawdown.png", "annual_performance.png"]:
        assert (tmp_path / "figures" / name).stat().st_size > 1000


def test_c_stage_preserves_original_metadata_and_inputs(case, monkeypatch):
    config, frame = case
    root = config.path("artifacts_dir") / "synthetic"
    root.mkdir(parents=True)
    config.path("model_table").write_text("synthetic model table")
    early = []
    for split, year in [("train", 2018), ("validation", 2019)]:
        sample = frame.iloc[:3].copy()
        for column in ["signal_date", "execution_date", "return_date"]:
            sample[column] = sample[column] - pd.DateOffset(years=2020 - year)
        sample["split"] = split
        early.append(sample)
    pd.concat([*early, frame]).to_csv(root / "predictions.csv", index=False)
    (root / "model.joblib").write_bytes(b"protected Member B model")
    (root / "alpha_validation.csv").write_text("protected Member B validation")
    def forbidden(*args, **kwargs):
        raise AssertionError("C must never rebuild A's data or retrain B's model")
    monkeypatch.setattr("combined_momentum.pipeline._run_model", forbidden)
    monkeypatch.setattr("combined_momentum.pipeline._run_data", forbidden)
    monkeypatch.setattr("combined_momentum.pipeline._run_features", forbidden)
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    original = {"config_sha256": sha(config.config_path), "model_table_sha256": sha(config.path("model_table")),
                "environment": {"member_b": "original"}}
    (root / "run_metadata.json").write_text(json.dumps(original))
    before = {p: sha(p) for p in root.iterdir()}
    run_pipeline(config, stage="backtest", run_id="synthetic")
    assert all(sha(p) == digest for p, digest in before.items())
    assert (root / "member_c_backtest_metadata.json").exists()
    run_pipeline(config, stage="evaluate", run_id="synthetic")
    assert all(sha(p) == digest for p, digest in before.items())
    assert (root / "member_c_evaluate_metadata.json").exists()
    assert len(pd.read_csv(root / "portfolio_returns.csv")) == 3
    assert (root / "figures" / "test_prediction_r2.png").exists()
    annual_prediction = pd.read_csv(root / "annual_prediction_metrics.csv").iloc[0]
    baseline = pd.concat(early).query("split == 'train'").target_return_1m.mean()
    expected_r2 = 1 - ((frame.predicted_return-frame.target_return_1m)**2).sum() / ((frame.target_return_1m-baseline)**2).sum()
    assert annual_prediction.r2_vs_train_mean == pytest.approx(expected_r2)
    portfolio_path = root / "portfolio_returns.csv"
    saved = portfolio_path.read_bytes()
    portfolio_path.write_bytes(saved + b"\n")
    with pytest.raises(ValueError, match="changed before evaluation"):
        run_pipeline(config, stage="evaluate", run_id="synthetic")
    portfolio_path.write_bytes(saved)
    config.config_path.write_text("changed settings")
    with pytest.raises(ValueError, match="Configuration differs"):
        run_pipeline(config, stage="backtest", run_id="synthetic")


def test_zero_costs_and_cash_only(case):
    config, frame = case
    config.values["strategy"]["transaction_cost_bps"] = 0
    frame["predicted_return"] = -.01
    _, trades, portfolio = run_backtest(frame, config)
    assert trades.estimated_cost.eq(0).all()
    assert portfolio.strategy_return.eq(0).all()
    assert portfolio.equal_weight_return.tolist() == pytest.approx(portfolio.gross_equal_weight_return.tolist())
    assert portfolio.benchmark_return.tolist() == pytest.approx(portfolio.gross_benchmark_return.tolist())


def test_complete_rotation_cost_is_both_purchase_and_sale(case):
    config, frame = case
    # A only in the first month; B only in the second month, with top_k=1.
    config.values["strategy"]["top_k"] = 1
    frame["predicted_return"] = -.01
    frame.loc[0, "predicted_return"] = .1
    frame.loc[4, "predicted_return"] = .1
    _, trades, portfolio = run_backtest(frame, config)
    rotation = trades[trades.signal_date.eq(pd.Timestamp("2020-02-28"))].set_index("ticker")
    cost = 2*.001 / 1.001
    assert rotation.loc["A", "weight_change"] == pytest.approx(-1)
    assert rotation.loc["B", "weight_change"] == pytest.approx(1 - cost)
    assert rotation.estimated_cost.sum() == pytest.approx(cost)
    assert portfolio.strategy_return.iloc[1] == pytest.approx((1 - cost)*1.02 - 1)
