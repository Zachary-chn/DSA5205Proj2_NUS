# Member B: Model Training and Validation SOP

## Understand the project first

Member A has converted daily prices into a monthly model table and calculated three features: one-month relative trend, six-month relative performance, and six-month volatility. Your job is to train Ridge regression to learn how these features relate to next-month returns and to use the validation period to choose `alpha`.

Your output goes to Member C. Member C does not retrain the model; they convert your predictions into positions and perform the final test.

## What the project already provides

Member A gives you:

```text
data/processed/model_table_us_industry.csv
```

Working starter code is available in:

```text
src/combined_momentum/split.py
src/combined_momentum/model.py
```

You are not expected to implement Ridge from an empty file. Understand the time split, scaling, alpha comparison, and model-saving process; confirm that they match this SOP; then run and inspect the outputs. If the model stage is incorrect, update these files and their tests. Do not manually edit Member A's CSV or change Member C's trading rule.

## What training, validation, and testing mean

The training period estimates model coefficients. The validation period compares candidate alpha values. The test period measures the final prediction and trading performance and belongs to Member C.

The current time design is:

| Part | Signal dates | Use |
|---|---|---|
| Training | Through 2014-12-31 | Fit candidate models |
| Validation | 2015-01-01 to 2018-12-31 | Compare alpha values |
| Test | 2019-01-01 to 2025-12-31 | B generates predictions but does not analyse performance |

The model must learn from earlier observations and predict later ones, so do not randomly shuffle the dates into new splits.

## What you must deliver

The model stage creates:

```text
artifacts/<run_id>/
```

The run ID identifies this particular set of outputs and ensures that Members B, C, and D use the same results. Give the exact run ID and the complete directory to Member C.

## Step 1: Check Member A's model table

The table must contain dates, ticker, `target_return_1m`, and these three features:

```text
rank_current_trend_1m
relative_strength_6m
risk_volatility_6m
```

The model is currently designed to use only these three inputs. Confirm that SPY and duplicate rows are absent. If columns, dates, or ETF counts are wrong, return the issue to Member A instead of repairing the CSV inside the model code.

## Step 2: Understand the current model

The model is currently designed as Ridge linear regression:

```text
predicted_return
  = intercept
    + beta_1 * rank_current_trend_1m
    + beta_2 * relative_strength_6m
    + beta_3 * risk_volatility_6m
```

Ridge minimises:

```text
sum[(actual_return - predicted_return)^2]
  + alpha * sum(beta_j^2)
```

A larger alpha applies more pressure toward smaller coefficients. The current candidate values are:

```text
0.01, 0.1, 1, 10, 100
```

Because the features have different units, the code uses `StandardScaler`. For each candidate model, scaling means and standard deviations must be estimated from the training period only.

## Step 3: Select alpha with the validation period

For each alpha, fit the model on the training rows and generate validation predictions for the 20 ETFs each month. Calculate the monthly Spearman correlation between predicted rankings and realised return rankings, then average the correlations across validation months.

The current selection method chooses the alpha with the highest average monthly Spearman IC. If none of the IC values can be calculated, use the lowest validation MSE. Save all five candidate results in `alpha_validation.csv`.

## Step 4: Generate predictions for Member C

After selecting alpha, refit the scaler and Ridge model on training plus validation rows. Generate `predicted_return` for train, validation, and test rows and save them in `predictions.csv`.

Generating test predictions is not the same as evaluating test performance. Member B saves training and validation metrics in:

```text
validation_prediction_metrics.csv
```

Member C produces the test metrics, positions, and portfolio returns.

## Step 5: Run the model stage

```powershell
python -m pytest
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage model
```

The terminal prints `run_dir`, and the project records the run ID in `artifacts/LATEST_RUN.txt`.

## Step 6: Check and hand off to Member C

The run directory should contain:

| File | Meaning |
|---|---|
| `model.joblib` | Fitted scaler and Ridge model |
| `alpha_validation.csv` | Validation results for five alpha values |
| `validation_prediction_metrics.csv` | Training and validation metrics |
| `coefficients.csv` | Coefficients for the three features |
| `predictions.csv` | Predictions used by Member C |
| `split_summary.csv` | Date range and size of each split |
| `run_metadata.json` | Settings, file hashes, and environment information |

Confirm that the alpha table contains five candidates, the coefficient table contains exactly three features, the split dates are correct, and test rows use the model fitted on training plus validation data. At this point, there should be no `positions.csv`, `portfolio_returns.csv`, final `prediction_metrics.csv`, or test figures.

Give Member C the exact run ID and directory. State the selected alpha, validation IC, and any model-code changes. Your responsibility ends with the prediction file. Do not run `backtest` or `evaluate`, and do not use test results to select alpha again.
