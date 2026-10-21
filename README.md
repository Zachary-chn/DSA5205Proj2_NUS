# DSA5205 Project 2 - Three-Signal Equity ETF Rotation

[中文版 README](README_CN.md)

This repository is a hand-off framework for a four-person group project. It fixes the research question, feature formulas, model family, trading rule, file interfaces and run commands. It deliberately does **not** contain the final cleaned data, feature table, fitted model, validation choice, test results, coefficient interpretation or performance discussion. Those are the group's work.

## 1. Current project state

| Part | Current status | Who completes it |
|---|---|---|
| Final raw data | Downloaded but not validated or transformed | Member A |
| Final cleaned data and three-feature model table | Empty / not generated | Member A |
| Model training and validation | Empty / not run | Member B |
| Trading implementation and final test | Empty / not run | Member C |
| Final report and presentation | Empty | Member D |

Before finalising this repository, we used a small convenience sample of ETFs to check that the formulas and workflow were sensible. That exploratory data is not part of the formal project dataset, training process or reported results.

## 2. Research idea

At each month-end, we compare a group of equity-sector ETFs. Our hypothesis is that an ETF's next-month total return may depend on three different properties of its recent price path:

1. **Recent relative trend:** whether its one-month price trend is stronger or weaker than the other candidate ETFs on the same date.
2. **Medium-term relative strength:** whether its six-month return is stronger or weaker than the other sector ETFs available on the same date.
3. **Risk intensity:** whether its daily returns have been stable or volatile over the previous six months.

These components are intentionally separate. The first compares very recent trends across ETFs, the second compares their medium-term returns, and the third measures the absolute size of recent fluctuations. Ridge regression estimates how much each component matters and whether its relation with next-month return is positive or negative.

No final coefficient sign is assumed in advance. The group must report the fitted signs and their economic meaning after completing the untouched final run.

## 3. Final ETF universe

The final candidates are 20 U.S.-listed equity sector and industry ETFs. Every candidate represents an investable segment of the U.S. equity market, so the ETFs can be compared at the same monthly signal date while still providing meaningful differences across industries. The list contains nine broad sectors and eleven specialised industries.

| Group | ETF | Exposure |
|---|---|---|
| Broad sector | XLY | Consumer discretionary |
| Broad sector | XLP | Consumer staples |
| Broad sector | XLE | Energy |
| Broad sector | XLF | Financials |
| Broad sector | XLV | Health care |
| Broad sector | XLI | Industrials |
| Broad sector | XLK | Information technology |
| Broad sector | XLB | Materials |
| Broad sector | XLU | Utilities |
| Specialised industry | IBB | Biotechnology |
| Specialised industry | IYR | U.S. real estate |
| Specialised industry | ITB | U.S. home construction |
| Specialised industry | KBE | Banks |
| Specialised industry | KRE | Regional banks |
| Specialised industry | XHB | Homebuilders |
| Specialised industry | XME | Metals and mining |
| Specialised industry | XOP | Oil and gas exploration and production |
| Specialised industry | XRT | Retail |
| Specialised industry | SMH | Semiconductors |
| Specialised industry | IYT | Transportation |

SPY is downloaded separately as the liquid buy-and-hold U.S. equity benchmark. It is not eligible for feature ranks, model estimation, or Top-5 selection. The sample begins in January 2007, after every candidate had launched. Membership is based on U.S. equity sector or industry exposure, launch date, data coverage, and availability of adjusted daily prices. Historical strategy performance is not part of the stated inclusion rule.

Full universe rules and sources are in [`extra_docs/FINAL_US_INDUSTRY_UNIVERSE.md`](extra_docs/FINAL_US_INDUSTRY_UNIVERSE.md). The project is currently designed to use the settings in [`configs/final_us_industry_project.yaml`](configs/final_us_industry_project.yaml).

## 4. Exact feature formulas

Let `P(i,t)` be ETF `i`'s split- and dividend-adjusted closing price known at signal date `t`.

### Feature 1: one-month current-trend rank

For the latest 21 trading days, regress log adjusted price on a daily time index:

```text
log(P(i,d)) = a(i,t) + b(i,t) * d + error(i,d)
current_trend_1m(i,t) = 252 * b(i,t)
```

Convert the slope to a same-date cross-sectional percentile rank:

```text
rank_current_trend_1m(i,t) = rank(i,t) / N(t) - 0.5
```

A higher value means the ETF's latest one-month direction is stronger than most candidates. Ranking removes the large scale difference between low- and high-volatility sectors.

### Feature 2: six-month relative-strength rank

Calculate the six-month adjusted-price return:

```text
relative_return_6m(i,t) = P(i,t) / P(i,t-6 months) - 1
```

Winsorise the same-date cross-section at the 1st and 99th percentiles, then rank it:

```text
relative_strength_6m(i,t) = rank(relative_return_6m(i,t)) / N(t) - 0.5
```

A higher value means the ETF outperformed more of the eligible sector ETFs over the previous six months.

### Feature 3: six-month realised volatility

Using the latest 126 daily adjusted-price returns:

```text
daily_return(i,d) = P(i,d) / P(i,d-1) - 1
risk_volatility_6m(i,t) = sqrt(252) * sample_std(daily_return over 126 days)
```

This feature remains in absolute units because its purpose is to distinguish genuinely calm and volatile price paths.

### Prediction label

The signal is calculated after the final close of month `t`. `execution_price(i,t)` is the first available adjusted close after that signal date. The one-month-ahead label is:

```text
target_return_1m(i,t)
    = execution_price(i,t+1) / execution_price(i,t) - 1
```

The signal-date closing price is never used as an assumed same-close execution price.

## 5. Model and validation SOP

The model pools all candidate ETF-month observations and estimates one common Ridge rule. Before fitting, each feature is standardised using the training sample mean and standard deviation only.

```text
minimise over intercept and beta:
    sum[(target_return_1m - intercept - X * beta)^2]
    + alpha * sum[beta_j^2]
```

The pre-declared penalty grid is:

```text
alpha = [0.01, 0.1, 1, 10, 100]
```

The time split is fixed in the YAML configuration:

| Period | Signal dates | Permitted use |
|---|---|---|
| Training | through 2014-12-31 | fit the scaler and each candidate Ridge model |
| Validation | 2015-01-01 through 2018-12-31 | choose alpha by average monthly Spearman rank IC |
| Test | 2019-01-01 through 2025-12-31 | final testing by Member C |

Member B must save the validation score for every alpha. After selecting alpha, refit the scaler and Ridge model on training plus validation observations. Test rows cannot influence scaling, alpha selection, feature definitions, ETF membership or trading rules.

## 6. Prediction-to-trade rule

At every signal date, score all 20 candidate ETFs. Retain ETFs with a positive predicted next-month return, rank them from highest to lowest, and select at most five. Give each selected ETF a 20% target weight. Any unused allocation remains in cash, so the portfolio is always long-only and unleveraged.

Rebalance at the next available trading close. Let `w(i,t)` be the new target weight and `w(i,t-1)` the previous target weight:

```text
one_way_turnover(t) = sum_i |w(i,t) - w(i,t-1)|
transaction_cost(t) = 0.001 * one_way_turnover(t)
net_return(t) = gross_return(t) + cash_return(t) - transaction_cost(t)
```

The required comparisons are the equal-weight candidate universe and buy-and-hold SPY. Report post-cost annualised return, annualised volatility, Sharpe ratio and maximum drawdown. Prediction RMSE, out-of-sample R-squared and monthly rank IC must also be reported even when weak or negative.

## 7. Four-person data hand-off

The pipeline is sequential at run time, while implementation and checking can proceed in parallel because every interface is fixed.

| Owner | Work to perform | Reads | Writes |
|---|---|---|---|
| Member A - Data and features | Clean and validate the raw prices, align monthly signal/execution dates, calculate the label, construct the three features in the current design and deliver the model table | final YAML and raw CSV | monthly CSV and `model_table_us_industry.csv` |
| Member B - Training and validation | Read the completed model table, apply the chronological split, fit training-only scalers, compare the current alpha candidates and save the Ridge model | model table | fitted model, validation tables, coefficients and prediction file |
| Member C - Trading and testing | Implement the positive-prediction Top-5 rule, positions, trades, transaction costs and benchmark comparison, then produce final test metrics and figures | Member B's predictions and final YAML | positions, trades, portfolio returns, test metrics, annual results and figures |
| Member D - Final report | Integrate the research idea, formulas, methods and outputs into the report and video; check that every number refers to the same run ID | outputs from Members A-C | final report, presentation/video material and contribution statement |

Each member checks the previous hand-off before starting. Member A hands the completed data and feature table to B; B hands the trained model and predictions to C; C hands the trading and test outputs to D; D writes the report from those files.

The executable checklist for each person is separate. Follow the assigned file from top to bottom:

- [Member A SOP: data cleaning and feature construction](SOP_A_DATA_AND_FEATURES.md)
- [Member B SOP: model training and validation](SOP_B_TRAIN_AND_VALIDATE.md)
- [Member C SOP: trading implementation and final testing](SOP_C_TRADING_AND_TESTING.md)
- [Member D SOP: final report and submission](SOP_D_FINAL_REPORT.md)

English copies are also available as [`SOP_A_DATA_AND_FEATURES_EN.md`](SOP_A_DATA_AND_FEATURES_EN.md), [`SOP_B_TRAIN_AND_VALIDATE_EN.md`](SOP_B_TRAIN_AND_VALIDATE_EN.md), [`SOP_C_TRADING_AND_TESTING_EN.md`](SOP_C_TRADING_AND_TESTING_EN.md), and [`SOP_D_FINAL_REPORT_EN.md`](SOP_D_FINAL_REPORT_EN.md).

## 8. File and column contracts

All tables are UTF-8 CSV files with a header row. Dates use `YYYY-MM-DD`; returns, weights and costs use decimal units; tickers use uppercase strings. No stage edits another stage's output manually.

| Stage | Expected path | Required content |
|---|---|---|
| Raw download | `data/raw/prices_daily_us_industry.csv` | `date,ticker,adjusted_close,raw_close,dividends,stock_splits,source,downloaded_at_utc` |
| Monthly clean data | `data/processed/prices_monthly_us_industry.csv` | signal date, ticker, adjusted price, next execution date/price, trend input, volatility input and target return |
| Model table | `data/processed/model_table_us_industry.csv` | one row per candidate ETF and signal date, exactly three features, label and execution dates |
| Model outputs | `artifacts/<run_id>/predictions.csv` | split, three features, actual return, prediction, prediction rank and selected alpha |
| Portfolio outputs | `artifacts/<run_id>/positions.csv`, `trades.csv`, `portfolio_returns.csv` | selection flags, weights, weight changes, turnover, cost and net return |
| Evaluation | `artifacts/<run_id>/metrics.csv`, `annual_performance.csv`, `figures/` | required metrics and out-of-sample plots |

The final processed files and final artifact folder do not exist yet by design.

## 9. Data-stage checks

Member A handles these checks as part of data processing. The data stage stops immediately if any required condition fails; there is no separate data-quality-report deliverable:

```text
primary key              = (date, ticker), unique
adjusted_close           > 0 and not missing
configured symbols       = all 20 candidates plus SPY
minimum candidate history = 24 monthly observations
daily calendar coverage  >= 95% for every configured symbol
assets with complete features per month >= 18
```

The adjustment check compares daily returns from adjusted and raw closes. Differences are expected near distributions or corporate actions and should be described; they are not automatically removed.

## 10. Run commands

Use Python 3.11 or newer from the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
```

The raw file has already been downloaded. To replace it from the public source:

```powershell
python scripts\download_raw_data.py --config configs\final_us_industry_project.yaml
```

Each person runs only the stage assigned in their own SOP. Member A runs:

```powershell
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage data
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage features
```

Member B runs:

```powershell
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage model
```

Member B gives the generated run ID to Member C. Member C uses that explicit ID in both commands:

```powershell
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage backtest --run-id <RUN_ID>
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage evaluate --run-id <RUN_ID>
```

Member D reads the same run folder and completes [`extra_docs/FINAL_RESULTS_TEMPLATE.md`](extra_docs/FINAL_RESULTS_TEMPLATE.md). No member manually edits generated data or artifact files.

For a clean end-to-end reproducibility check after the group has completed all stage reviews:

```powershell
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml
```

## 11. Repository structure

```text
configs/
    final_us_industry_project.yaml       settings currently used by the project
data/raw/
    prices_daily_us_industry.csv         final unprocessed input
data/processed/
    Member A's monthly data and three-feature model table appear here
SOP_*.md
    individual Chinese and English instructions for Members A-D
extra_docs/
    universe definition, empty results worksheet and contribution template
scripts/
    download_raw_data.py and run_pipeline.py
src/combined_momentum/
    reusable pipeline implementation
tests/
    formula, leakage and portfolio-rule tests
artifacts/
    Member B creates the run; Member C adds test and trading outputs
submission/
    Member D places the final report and video/submission material here
```

## 12. What remains deliberately blank

The project currently makes no final statement about data quality, selected alpha, coefficient sizes or signs, prediction quality, chosen holdings, turnover, returns, Sharpe ratio, drawdown, benchmark performance, successful periods, failure periods or economic interpretation. These fields remain empty in the final-results worksheet until the group completes the pipeline.

The report and 15-25 minute video should follow the same order as this README: market and timing, data checks, feature formulas, Ridge and overfitting control, chronological validation, prediction-to-position rule, costs, final testing, interpretation and reproducibility. Every final number and plot must come from the same run ID.
