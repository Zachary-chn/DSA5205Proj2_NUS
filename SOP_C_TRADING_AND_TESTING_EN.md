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

Let `v(i,t)` be the ETF weight immediately before rebalancing. For the first
trade, every `v` is zero (the portfolio starts in cash). Later weights include
only returns realised during the previous holding period:

```text
v(i,t) = w(i,t-1) * (1 + r(i,t-1)) / (1 + gross_return(t-1))
gross_return(t) = sum_i[w(i,t) * r(i,t)] + cash_weight(t) * monthly_cash_return
c(t) = 0.001 * sum_i abs((1 - c(t)) * w(i,t) - v(i,t))
executed_weight(i,t) = (1 - c(t)) * w(i,t)
weight_change(i,t) = executed_weight(i,t) - v(i,t)
one_way_turnover(t) = sum_i abs(weight_change(i,t))
net_return(t) = (1 - c(t)) * (1 + gross_return(t)) - 1
```

The solver pays the 10 bp fee on all ETF purchases and sales from portfolio
wealth before buying the new holdings. Targets remain 20% per selected ETF
of wealth after costs. `previous_weight` in `trades.csv` means drifted pretrade
weight; trade amounts and costs are fractions of pretrade wealth. Cash has no
trading fee and earns zero. Turnover is total absolute ETF notional (no factor
of one half); selling one fully invested portfolio and buying another can
approach 200%. No terminal liquidation fee is charged: ending wealth is marked
to market. Adjusted closes approximate dividend reinvestment and execution;
there is no separate spread, tax, market impact, or intramonth trading model.

Execution uses A's next-trading-close dates. Returns must be complete, candidate
membership must match the configured universe, and holding periods must join
without gaps or overlap. Missing data raise an error; missing future returns
never silently remove ETFs from selection.

## Step 4: Build the two comparisons

The equal-weight universe holds all 20 candidate ETFs equally every month. It shows whether model-based selection improves on simply holding the sector universe.

SPY represents the broad U.S. equity market. Its return is read from Member A's monthly table. SPY does not enter model training or Top-5 selection. Both comparisons pay the
same 10 bp one-way fee as the strategy. Equal weight is restored monthly using
drifted holdings and the same self-financing cost solver. SPY pays an initial
purchase fee and is then held without rebalancing. Gross and net benchmark
returns and costs are retained in `portfolio_returns.csv`. All three series
must share identical execution and return dates. Missing, duplicate, or
misaligned SPY observations raise an error.

## Step 5: Run the backtest and evaluation

The completed A/B handoff uses run ID
`20261024T155915Z_final_us_industry_project`. Replace `<RUN_ID>` below with it.
Use Python 3.11+ and install `requirements.txt` in a virtual environment first.
On macOS/Linux use `/` in script paths; Windows commands are shown below:

```powershell
python -m pytest
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage backtest --run-id <RUN_ID>
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage evaluate --run-id <RUN_ID>
```

`backtest` creates positions, trades, and monthly portfolio returns. `evaluate`
produces final metrics and figures. These stages preserve B's `run_metadata.json`
and save their own `member_c_backtest_metadata.json` and
`member_c_evaluate_metadata.json`, including input/source hashes and the C
runtime environment. Do not run `--stage model` or the default `all` stage to
reproduce C; those would retrain B's model.

The model is frozen before the first test decision; it is not refitted during
testing. Signal months are January 2019–December 2025; holding periods run from
1 February 2019 through 2 February 2026. Annual results group the ending
`return_date` by year and include partial boundary years. Maximum drawdown
includes initial wealth of one; cumulative curves include that initial point.
Annualized return is CAGR; volatility uses sample monthly standard deviation
and sqrt(12); Sharpe uses mean monthly return divided by sample standard
deviation times sqrt(12), with a zero risk-free rate. Zero volatility gives an
undefined Sharpe. Total transaction cost is a sum of monthly cost fractions,
not a dollar amount or the compounded performance drag.

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
annual_prediction_metrics.csv
member_c_backtest_metadata.json
member_c_evaluate_metadata.json
figures/test_prediction_scatter.png
figures/test_prediction_r2.png
figures/equity_curve.png
figures/drawdown.png
figures/annual_performance.png
```

Confirm that ETF weights plus cash equal one each month, individual ETF weights are only zero or 0.2, no more than five ETFs are selected, costs are non-negative, all three portfolios use the same test months, and all files belong to the same run ID.

The final methodology, reproduction commands and result discussion are in
`extra_docs/MEMBER_C_HANDOFF.md`.

Give Member D the run ID, full artifact path, and `metrics.csv`. State whether both commands succeeded and whether you changed any trading code. Your responsibility ends with the final test files and figures.
