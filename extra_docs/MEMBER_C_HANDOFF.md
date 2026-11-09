# Member C handoff: trading and final holdout evaluation

Run ID: `20261024T155915Z_final_us_industry_project`.
Artifact directory (relative to repository root):
`artifacts/20261024T155915Z_final_us_industry_project/`.

## Scope and frozen decisions

Member C consumes A's processed monthly prices and B's saved predictions. C does
not retrain, deserialize, or modify B's model. The original feature definitions,
20-ETF universe, Ridge alpha 0.1, positive-score filter, Top-5 rule, 20% targets,
monthly schedule, cash return of zero, and 10 bp one-way trading fee are retained.
Alphabetical ticker order breaks exact score ties deterministically.

The model was fitted once before the first test decision and remains fixed.
There is no rolling refit during C's test. The final test contains 84 signal
months, January 2019–December 2025. Execution starts 1 February 2019; the final
holding period ends 2 February 2026. Training and validation rows never enter
C's portfolio. B's unavailable boundary labels are excluded by B's original
model code. No test performance is used for model or rule selection.

## Accounting and benchmark assumptions

Targets are weights of wealth after costs. At each execution date, pretrade ETF
weights drift from the preceding holding period's ETF and cash returns. The
first portfolio starts entirely in cash. C solves the self-financing equation
`c = 0.001 * sum(abs((1-c)*target - pretrade_weight))`, where `c` is cost divided
by pretrade wealth. Buying and selling both incur the same fee; cash transfers
have no fee. Monthly net return is `(1-c)*(1+gross_return)-1`, including cash in
gross return. This replaces the earlier target-to-target turnover approximation
and additive return/cost approximation. Selected ETF targets remain 20% each.

`trades.csv` reports drifted `previous_weight`, after-cost `target_weight`,
actual `executed_weight`, signed and absolute changes, and per-ETF costs.
Executed weights, trades and fees are fractions of wealth before execution.
Turnover is total absolute ETF notional, without division by two. A complete
rotation can approach 200%. There is no terminal sale: ending wealth is marked
to market. Sum of monthly cost fractions is neither a dollar cost nor the
compounded performance drag.

The equal-weight universe is restored to 5% per ETF each month and uses the
same drift/cost solver. SPY is bought once, incurs the same entry fee, and is
then held. Both gross and net comparison returns, turnover and fees appear in
`portfolio_returns.csv`. All three investments use identical holding dates.
Missing, duplicate or misaligned benchmark observations raise an error; they
are never removed from the comparison or replaced with zero.

Adjusted closes approximate total-return execution and distribution
reinvestment. No separate tax, spread, market impact, cash trading fee, or
intramonth trading is modeled. Exact closing-price fills and weight sizing are
idealized; capacity is not tested. The ETF list was selected retrospectively,
so survivorship and selection bias remain possible. Overlapping sector and
industry exposures mean diversification across tickers is not diversification
across independent risks. A fixed model can become stale during the test.

## SMH historical-series disclosure for Member D

The retained SMH series includes Semiconductor HOLDRS Trust history before 21 December 2011 and the successor Market Vectors Semiconductor ETF (now VanEck Semiconductor ETF) thereafter. Participating HOLDRS holders exchanged receipts on 20 December 2011; the ETF began trading under SMH on 21 December. Describe this as a predecessor-linked investment series, not as the current ETF having existed before January 2007.

A subsequent read-only check of saved prices for 15–23 December 2011 found no obvious transition discontinuity: the 20–21 December return was approximately -1.1655% in both Close and Adjusted Close. Yahoo's complete adjustment methodology and investor-specific transition returns have not been independently verified. The original launch-date description did not explicitly establish a predecessor-aware rule before selection; this is a later documentation clarification, with the existing universe, data, model and results retained unchanged. Member D should include this qualification in the report's data/universe and limitations sections. Full details and primary-source references are in [the universe disclosure](FINAL_US_INDUSTRY_UNIVERSE.md#smh-predecessor-history-and-december-2011-transition).

## Metrics and figures

Annualized return is geometric CAGR using 12 periods per year. Annualized
volatility is sample monthly standard deviation times sqrt(12). Sharpe uses
mean monthly net return divided by sample standard deviation times sqrt(12),
with risk-free return zero. It is undefined if volatility is zero. Drawdown is
measured at monthly endpoints against the running wealth peak including
initial wealth 1. Equity and drawdown curves include that initial point.

Annual results group holding-period endings by `return_date` year; the first
and last years are partial and the `months` column must be retained. Return
for each year is the actual compounded return of its included periods, not an
extrapolation to a full year. Within-year volatility and Sharpe are annualized.

Prediction metrics use B's original code: RMSE, MAE, average monthly Spearman
rank IC, and OOS R-squared against the historical training-label mean available
at the validation boundary. The R-squared denominator uses that same fixed
baseline for testing. Weak or negative results must remain in D's report. The additional yearly
prediction table and R-squared figure use the same fixed training mean and
the same realisation-year convention; they are descriptive, not model selection.

## Reproduction without changing A or B

Use Python 3.11+ from the repository root. The completed C run uses Python 3.12.
On macOS/Linux:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r artifacts/20261024T155915Z_final_us_industry_project/member_c_requirements.txt
MPLCONFIGDIR=.venv/matplotlib .venv/bin/python -m pytest
MPLCONFIGDIR=.venv/matplotlib .venv/bin/python scripts/run_pipeline.py --config configs/final_us_industry_project.yaml --stage backtest --run-id 20261024T155915Z_final_us_industry_project
MPLCONFIGDIR=.venv/matplotlib .venv/bin/python scripts/run_pipeline.py --config configs/final_us_industry_project.yaml --stage evaluate --run-id 20261024T155915Z_final_us_industry_project
```

`requirements.txt` remains the general project environment file; C's frozen
requirements record the exact installed versions. On Windows use
`.venv\Scripts\python.exe` instead of `.venv/bin/python`, and omit the POSIX
`MPLCONFIGDIR=...` prefix. Do not run `--stage model`, `--stage data`,
`--stage features`, `--force-download`, or the default `all` stage to reproduce C.

The original `run_metadata.json` is B's immutable record. C writes
`member_c_backtest_metadata.json` and `member_c_evaluate_metadata.json` with its
own environment, source hashes, input hashes, stage summary and UTC timestamp.
C refuses a changed configuration or model-table hash. Keep both C metadata
files with the final outputs: the evaluation stage requires the backtest
metadata. Keep the frozen requirements to reproduce the recorded environment.

The optional standalone verifier, original-input checksum manifest, historical
JUnit XML and verification JSON are retained locally and excluded from Git.
They are not pipeline or pytest dependencies and are not required for Member D's
handoff or the reproduction commands above. The external-review audit report
was removed during repository cleanup.

## Output contract for Member D

| File | Contents |
|---|---|
| `positions.csv` | All 20 ETF rows per test signal; scores, eligibility, selection, 0/20% targets, cash |
| `trades.csv` | Drifted previous weights, actual trade amounts, turnover components and costs |
| `portfolio_returns.csv` | Execution/return dates, strategy gross/net returns and cash, all comparison gross/net returns and costs |
| `prediction_metrics.csv` | B's prediction metrics for train, validation and untouched test |
| `metrics.csv` | Post-cost CAGR, volatility, Sharpe, drawdown, positive-period rate, cumulative return, turnover and costs |
| `cumulative_returns.csv` | Initial wealth row plus 84 end-period wealth/drawdown observations per investment |
| `annual_prediction_metrics.csv` | Fixed-baseline test R-squared and RMSE by realisation year |
| `annual_performance.csv` | Returns, annualized volatility and Sharpe by realisation year, with number of months |
| `figures/test_prediction_scatter.png` | Test predictions against realised returns |
| `figures/test_prediction_r2.png` | Fixed-baseline test R-squared by realisation year |
| `figures/equity_curve.png` | Post-cost wealth comparison starting at 1 |
| `figures/drawdown.png` | Drawdowns including initial wealth |
| `figures/annual_performance.png` | Return and Sharpe comparison by realisation year |
| `member_c_*_metadata.json` | Separate C stage provenance; preserves B metadata |
| `member_c_requirements.txt` | Frozen C dependencies |

C changed trading/accounting, evaluation, targeted shared pipeline provenance,
and relevant documentation. A/B outputs and configuration remain untouched.

## Verification and final results

The complete suite passed: **25 tests**, including synthetic position, cash,
drift, complete rotation, self-financing budget, transaction-cost, missing-data,
benchmark, alignment, look-ahead, metric, plot and provenance tests. The original
feature tests also passed. `pip check` found no broken requirements.
The historical JUnit report is kept only in the optional local review bundle;
teammates can run the committed pytest suite to verify the implementation.
Synthetic integration tests forbid data building/training and verify B's file
bytes remain unchanged.

After tests passed, the fixed final backtest and evaluation were each run once,
and both succeeded. No model/rule changes followed inspection of test results.
During the original verification, an optional local script passed **20 checks**, including an
independent cash-and-ETF dollar ledger, all 84 aligned periods, all 20 ETFs per
month, exact correspondence to B's selected ranks, costs and drawdowns, and
unchanged checksums for **all 12 original data/artifact files**. C's stage metadata
also confirms configuration and model-table hashes match B's record.

| Investment (after costs) | CAGR | Annualized volatility | Sharpe | Maximum drawdown |
|---|---:|---:|---:|---:|
| Three-signal Top-5 strategy | 20.19% | 29.95% | 0.771 | -43.57% |
| Monthly equal-weight universe | 14.76% | 20.69% | 0.775 | -33.89% |
| Buy-and-hold SPY | 16.20% | 17.26% | 0.962 | -23.79% |

The strategy's terminal wealth is **3.6235 per initial unit** (262.35% cumulative
return), versus 2.6214 for equal weight and 2.8604 for SPY. It held five ETFs in
all 84 test months, so the cash fallback did not activate in this holdout;
synthetic tests cover zero/fewer positive predictions. Mean monthly strategy
turnover was **89.48%** of pretrade wealth. Its sum of monthly fee fractions was
0.075159 (7.5159 percentage points as a sum; not compounded drag or a dollar fee),
compared with 0.003985 for equal weight and 0.000999 for SPY.

Test predictions: **1,680 observations**, RMSE **0.077828**, MAE **0.056103**,
OOS R-squared **0.005713** (0.5713%), and average monthly rank IC **0.019424**.
The positive test prediction skill is small; B's validation rank IC remained
negative (-0.067637). These results do not establish stable forecasting ability.

The strategy achieved higher compounded return, but its Sharpe was slightly
below equal weight and materially below SPY, with larger volatility and losses
from peak wealth. It therefore did not demonstrate superior risk-adjusted
performance. In the full realisation years, its highest return was 2021
(+43.09%); 2020 combined a modest +4.43% return with 57.90% annualized volatility.
It gained +17.78% in the 2022 endpoint grouping while SPY lost 8.20%. These are
fixed descriptive comparisons, not grounds for changing the rule. The 2019
and 2026 groups contain only 10 and 2 observations; especially the latter's
annualized Sharpe should not be interpreted as a stable estimate.

Remaining limitations are the idealized adjusted-close fills, constant cost,
retrospective ETF universe, correlated exposures, zero risk-free/cash assumption,
fixed-model staleness, and a single holdout without statistical uncertainty
estimates or factor attribution. No superiority or alpha claim is made.
Member D still needs to integrate these artifacts into the report/video and
complete the contribution note; C has not edited D's result worksheet or report.
