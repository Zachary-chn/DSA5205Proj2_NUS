import pandas as pd

from combined_momentum.config import ProjectConfig
from combined_momentum.strategy import build_positions


def test_top_k_positive_rule_and_cash_weight(tmp_path):
    config = ProjectConfig(
        values={
            "strategy": {"top_k": 2, "require_positive_prediction": True},
            "project": {}, "paths": {}, "data": {}, "features": {},
            "split": {}, "model": {}, "evaluation": {},
        },
        root=tmp_path,
        config_path=tmp_path / "config.yaml",
    )
    rows = []
    for date, predictions in [
        ("2022-01-31", [0.03, 0.02, -0.01, -0.02]),
        ("2022-02-28", [0.01, -0.01, -0.02, -0.03]),
    ]:
        for ticker, prediction in zip(["A", "B", "C", "D"], predictions):
            rows.append(
                {
                    "signal_date": date,
                    "return_date": pd.Timestamp(date) + pd.offsets.MonthEnd(1),
                    "ticker": ticker,
                    "split": "test",
                    "predicted_return": prediction,
                    "target_return_1m": 0.01,
                }
            )
    positions = build_positions(pd.DataFrame(rows), config)
    grouped = positions.groupby("signal_date").agg(
        holdings=("selected", "sum"),
        asset_weight=("target_weight", "sum"),
        cash_weight=("cash_weight", "first"),
    )
    assert grouped["holdings"].tolist() == [2, 1]
    assert grouped["asset_weight"].tolist() == [1.0, 0.5]
    assert grouped["cash_weight"].tolist() == [0.0, 0.5]
    assert (grouped["asset_weight"] + grouped["cash_weight"]).round(10).eq(1.0).all()
    assert positions["target_weight"].ge(0).all()

