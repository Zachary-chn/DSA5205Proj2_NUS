from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import ProjectConfig
from .features import feature_columns
from .io import write_table


def make_ridge(alpha: float, positive: bool = False) -> Pipeline:
    return Pipeline(
        steps=[
            ("scale", StandardScaler()),
            ("ridge", Ridge(alpha=float(alpha), positive=positive)),
        ]
    )


def monthly_spearman_ic(frame: pd.DataFrame, target_column: str) -> float:
    correlations: list[float] = []
    for _, group in frame.groupby("signal_date"):
        if len(group) < 3 or group["prediction"].nunique() < 2 or group[target_column].nunique() < 2:
            continue
        correlations.append(
            float(group["prediction"].corr(group[target_column], method="spearman"))
        )
    return float(np.mean(correlations)) if correlations else np.nan


def _available_model_samples(table: pd.DataFrame, target_column: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Use only labels known by the first validation/test signal, after the close."""
    signal_dates = pd.to_datetime(table["signal_date"])
    return_dates = pd.to_datetime(table["return_date"])
    labelled = table[target_column].notna()
    train = table["split"].eq("train")
    validation = table["split"].eq("validation")
    validation_start = signal_dates.loc[validation].min()
    test_start = signal_dates.loc[table["split"].eq("test")].min()
    return (
        table.loc[labelled & train & return_dates.le(validation_start)],
        table.loc[labelled & validation & return_dates.le(test_start)],
        table.loc[labelled & (train | validation) & return_dates.le(test_start)],
    )


def fit_and_predict(
    table: pd.DataFrame,
    config: ProjectConfig,
    run_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    features = feature_columns(config)
    model_settings = config.section("model")
    target_column = str(model_settings.get("target_column", "target_return_1m"))
    positive_coefficients = bool(model_settings.get("positive_coefficients", False))
    if target_column not in table.columns:
        raise ValueError(f"Configured model target is missing from the model table: {target_column}")
    train, validation, refit_data = _available_model_samples(table, target_column)

    alpha_rows: list[dict[str, float]] = []
    candidate_models: dict[float, Pipeline] = {}
    for alpha in map(float, model_settings["alpha_grid"]):
        candidate = make_ridge(alpha, positive=positive_coefficients)
        candidate.fit(train[features], train[target_column])
        validation_scored = validation[["signal_date", target_column]].copy()
        validation_scored["prediction"] = candidate.predict(validation[features])
        ic = monthly_spearman_ic(validation_scored, target_column)
        mse = float(np.mean((validation_scored["prediction"] - validation_scored[target_column]) ** 2))
        alpha_rows.append({"alpha": alpha, "validation_monthly_spearman_ic": ic, "validation_mse": mse})
        candidate_models[alpha] = candidate

    alpha_results = pd.DataFrame(alpha_rows).sort_values(
        ["validation_monthly_spearman_ic", "validation_mse"],
        ascending=[False, True],
        na_position="last",
    )
    if alpha_results["validation_monthly_spearman_ic"].notna().any():
        selected_alpha = float(alpha_results.iloc[0]["alpha"])
    else:
        selected_alpha = float(alpha_results.sort_values("validation_mse").iloc[0]["alpha"])

    train_model = candidate_models[selected_alpha]
    final_model = make_ridge(selected_alpha, positive=positive_coefficients)
    final_model.fit(refit_data[features], refit_data[target_column])

    scored = table.loc[table["split"].isin(["train", "validation", "test"])].copy()
    early_mask = scored["split"].isin(["train", "validation"])
    scored["predicted_return"] = np.nan
    scored.loc[early_mask, "predicted_return"] = train_model.predict(scored.loc[early_mask, features])
    scored.loc[~early_mask, "predicted_return"] = final_model.predict(scored.loc[~early_mask, features])
    scored["model_fit"] = np.where(early_mask, "train_only", "train_plus_validation")
    scored["selected_alpha"] = selected_alpha
    scored["prediction_rank"] = scored.groupby("signal_date")["predicted_return"].rank(
        ascending=False, method="first"
    )

    keep = [
        "signal_date",
        "execution_date",
        "return_date",
        "ticker",
        "split",
        *features,
        "target_return_1m",
        target_column,
        "predicted_return",
        "prediction_rank",
        "model_fit",
        "selected_alpha",
    ]
    predictions = scored[list(dict.fromkeys(keep))].sort_values(
        ["signal_date", "prediction_rank"]
    ).reset_index(drop=True)

    standardized_coefficients = final_model.named_steps["ridge"].coef_
    coefficients = pd.DataFrame(
        {
            "feature": features,
            "standardized_coefficient": standardized_coefficients,
            "absolute_coefficient": np.abs(standardized_coefficients),
        }
    ).sort_values("absolute_coefficient", ascending=False)

    run_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, run_dir / "model.joblib")
    write_table(alpha_results, run_dir / "alpha_validation.csv")
    write_table(coefficients, run_dir / "coefficients.csv")
    write_table(predictions, run_dir / "predictions.csv")
    validation_metrics = prediction_metrics(
        predictions,
        float(train[target_column].mean()),
        target_column,
        split_names=("train", "validation"),
    )
    write_table(validation_metrics, run_dir / "validation_prediction_metrics.csv")
    latest_date = predictions["signal_date"].max()
    latest = predictions.loc[predictions["signal_date"].eq(latest_date)].copy()
    write_table(latest, run_dir / "latest_signal_predictions.csv")
    return predictions, alpha_results, coefficients


def prediction_metrics(
    predictions: pd.DataFrame,
    train_mean: float,
    target_column: str,
    split_names: tuple[str, ...] = ("train", "validation", "test"),
) -> pd.DataFrame:
    train, validation, _ = _available_model_samples(predictions, target_column)
    if not train.empty:
        train_mean = float(train[target_column].mean())
    early_samples = {"train": train, "validation": validation}
    rows = []
    for split_name in split_names:
        subset = predictions.loc[
            predictions["split"].eq(split_name) & predictions[target_column].notna()
        ].copy()
        subset = early_samples.get(split_name, subset)
        error = subset["predicted_return"] - subset[target_column]
        model_sse = float(np.square(error).sum())
        baseline_sse = float(np.square(subset[target_column] - train_mean).sum())
        rows.append(
            {
                "split": split_name,
                "observations": len(subset),
                "rmse": float(np.sqrt(np.square(error).mean())),
                "mae": float(error.abs().mean()),
                "r2_vs_train_mean": 1.0 - model_sse / baseline_sse if baseline_sse > 0 else np.nan,
                "monthly_spearman_ic": monthly_spearman_ic(
                    subset.rename(columns={"predicted_return": "prediction"}),
                    target_column,
                ),
            }
        )
    return pd.DataFrame(rows)


def plot_test_predictions(predictions: pd.DataFrame, target_column: str, path: Path) -> None:
    test = predictions.loc[
        predictions["split"].eq("test") & predictions[target_column].notna()
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axis = plt.subplots(figsize=(6.5, 5.5))
    axis.scatter(test["predicted_return"], test[target_column], alpha=0.4, s=18)
    axis.axhline(0.0, color="black", linewidth=0.8)
    axis.axvline(0.0, color="black", linewidth=0.8)
    axis.set_title("Out-of-sample predictions and realised returns")
    axis.set_xlabel(f"Predicted {target_column}")
    axis.set_ylabel(f"Realised {target_column}")
    axis.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)

