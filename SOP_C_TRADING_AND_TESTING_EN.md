# Member C: Trading Implementation and Final Testing SOP

## Understand the project first

Member A has prepared prices and features. Member B has trained Ridge and generated next-month return predictions for each ETF. Your job is to convert those predictions into monthly positions, apply rebalancing costs, and compare the strategy with the equal-weight 20-ETF universe and SPY. Member D will use your numbers and figures in the report.

## What the project already provides

Member B gives you an exact run ID. You read:

```text
artifacts/<run_id>/predictions.csv
data/processed/prices_monthly_us_industry.csv
configs/final_us_industry_project.yaml
```

Working starter code is available in:

```text
src/combined_momentum/strategy.py
src/combined_momentum/backtest.py
src/combined_momentum/evaluation.py
```

You are not expected to build the backtest from an empty file. Understand how predictions become weights, how turnover becomes transaction cost, and how the three portfolios are compared. Then run and inspect the outputs. If this stage is incorrect, update these files and their tests. Do not retrain Member B's model or change Member A's feature table.

## Step 1: Understand the prediction file

Each `predictions.csv` row represents one ETF in one month. The backtest uses only rows where `split = test`. `predicted_return` decides the position. `target_return_1m` is the return that later occurred and is used to calculate the result of holding that position.

## Step 2: Convert predictions into positions

The trading rule is currently designed as follows: remove ETFs with predicted returns at or below zero; rank the remaining ETFs from highest to lowest predicted return; select at most five; and assign a fixed 20% weight to every selected ETF.

| Number with positive predictions | Number held | Total ETF weight | Cash weight |
|---|---:|---:|---:|
| 5 or more | 5 | 100% | 0% |
| 3 | 3 | 60% | 40% |
| 1 | 1 | 20% | 80% |
| 0 | 0 | 0% | 100% |

When fewer than five ETFs qualify, do not scale them up to a fully invested portfolio. The strategy is long-only, unleveraged, and does not short ETFs.

## Step 3: Calculate turnover and transaction costs

```text
weight_change(i,t)
  = target_weight(i,t) - target_weight(i,t-1)

one_way_turnover(t)
  = sum_i abs(weight_change(i,t))

transaction_cost(t)
  = one_way_turnover(t) * 10 / 10000
```

The current one-way transaction cost is 10 basis points. The monthly strategy return after costs is:

```text
strategy_return(t)
  = sum_i[target_weight(i,t) * target_return_1m(i,t)]
    + cash_weight(t) * monthly_cash_return
    - transaction_cost(t)
```

The current annual cash return is zero. Execution uses the `execution_date` created by Member A and must not be changed to the signal day's closing price.

## Step 4: Build the two comparisons

The equal-weight universe holds all 20 candidate ETFs equally every month. It shows whether model-based selection improves on simply holding the sector universe.

SPY represents the broad U.S. equity market. Its return is read from Member A's monthly table. SPY does not enter model training or Top-5 selection.

## Step 5: Run the backtest and evaluation

Replace `<RUN_ID>` with the exact name supplied by Member B:

```powershell
python -m pytest
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage backtest --run-id <RUN_ID>
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage evaluate --run-id <RUN_ID>
```

`backtest` creates positions, trades, and monthly portfolio returns. `evaluate` produces final metrics and figures.

Prediction results currently include test RMSE, MAE, out-of-sample R-squared, and average monthly Spearman IC. Trading results include annualised return, annualised volatility, Sharpe ratio, maximum drawdown, positive-month rate, and cumulative return for the strategy, equal-weight portfolio, and SPY. The strategy also reports average turnover and total transaction cost. Preserve the actual results whether they are strong or weak.

## Step 6: Check and hand off to Member D

The same run directory should now contain:

```text
positions.csv
trades.csv
portfolio_returns.csv
prediction_metrics.csv
metrics.csv
cumulative_returns.csv
annual_performance.csv
figures/test_prediction_scatter.png
figures/equity_curve.png
figures/drawdown.png
figures/annual_performance.png
```

Confirm that ETF weights plus cash equal one each month, individual ETF weights are only zero or 0.2, no more than five ETFs are selected, costs are non-negative, all three portfolios use the same test months, and all files belong to the same run ID.

Give Member D the run ID, full artifact path, and `metrics.csv`. State whether both commands succeeded and whether you changed any trading code. Your responsibility ends with the final test files and figures.
