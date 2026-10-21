# Member A: Data Processing and Feature Construction SOP

## Understand the project first

This project studies U.S. equity industry ETF rotation. Each month, we compare 20 U.S. broad-sector and specialised-industry ETFs and use information already available at that time to predict their returns over the next month. The model uses three inputs: the latest one-month price trend, the ETF's relative performance over six months, and its volatility over six months.

The workflow is sequential. Member A prepares the data and features, Member B trains and validates the model, Member C converts predictions into trades and performs the final test, and Member D writes the report. Your work is the first stage and becomes Member B's input.

## What the project already provides

The raw data is already stored at:

```text
data/raw/prices_daily_us_industry.csv
```

It contains daily prices for 20 candidate ETFs and the SPY market benchmark. The candidates are `XLY, XLP, XLE, XLF, XLV, XLI, XLK, XLB, XLU, IBB, IYR, ITB, KBE, KRE, XHB, XME, XOP, XRT, SMH, IYT`. You do not need to search for or download data. `scripts/download_raw_data.py` is only a backup tool for use if the file is missing or the group agrees to download a new copy.

The project also provides working starter code in:

```text
src/combined_momentum/data.py
src/combined_momentum/features.py
```

You are not expected to build this stage from an empty file. Your job is to understand the code, confirm that it follows the calculations described below, run it, and inspect the outputs. If the code does not work correctly with the actual data, update these two files and the related tests. Do not change Member B's model code or Member C's trading code.

## What you must deliver

You must generate:

```text
data/processed/prices_monthly_us_industry.csv
data/processed/model_table_us_industry.csv
```

The first file converts daily prices into monthly observations and aligns signal and execution dates. The second adds the three features and the realised next-month return. Member B will train the model directly from this table.

## Initial setup

Open PowerShell in the project root. On first use, run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
```

On later sessions, activate the environment with `.venv\Scripts\Activate.ps1`. If the tests fail, resolve or report the error before producing hand-off files.

## Step 1: Understand the raw file

Open the raw CSV and confirm that it contains at least:

| Column | Meaning |
|---|---|
| `date` | Trading date |
| `ticker` | ETF symbol |
| `adjusted_close` | Closing price adjusted for distributions and splits |

The file may also contain `raw_close`, `dividends`, `stock_splits`, `source`, and `downloaded_at_utc`. Returns, trends, and volatility are all calculated from `adjusted_close`.

The current data design contains the 20 U.S. industry ETFs listed above plus SPY. SPY is only a market benchmark. It must not enter feature ranking or Member B's training table. The full exposure names and inclusion rule are in `extra_docs/FINAL_US_INDUSTRY_UNIVERSE.md`.

## Step 2: Validate and organise daily prices

This work is handled by `validate_daily_prices()` and `to_monthly_prices()` in `data.py`.

`validate_daily_prices()` should confirm that each `date + ticker` pair is unique, `adjusted_close` is present and positive, all 21 symbols exist, and each symbol reaches the 95% date-coverage requirement in the configuration. The program should raise an error when a required condition fails instead of silently removing an ETF.

`to_monthly_prices()` keeps the last available trading date in each calendar month. This becomes the signal date because the model reads prices after that close. The simulated execution price uses the first available close after the signal date, so the strategy does not assume that it can observe and trade on the same closing price.

Key monthly fields are:

| Column | Meaning |
|---|---|
| `date` | Month-end signal date |
| `execution_date` | First available trading date after the signal |
| `execution_price` | Adjusted close used for simulated execution |
| `return_date` | End date of the holding period |
| `target_return_1m` | Realised return from this execution price to the next one |

The prediction target is:

```text
target_return_1m(i,t)
  = execution_price(i,t+1) / execution_price(i,t) - 1
```

## Step 3: Calculate the three features

`data.py` prepares daily trend and volatility inputs. `build_model_table()` in `features.py` completes the monthly ranking and writes the model table.

### Feature 1: Latest one-month relative trend

For each ETF, regress the logarithm of adjusted price on a time index over the latest 21 trading days:

```text
log(P(i,d)) = a(i,t) + b(i,t) * d + error(i,d)
current_trend_1m(i,t) = 252 * b(i,t)
```

A positive slope means the price generally moved upward during the month; a negative slope means it generally moved downward. Compare the slopes of all 20 ETFs on the same date:

```text
rank_current_trend_1m = same-month percentile rank - 0.5
```

This feature answers whether the ETF's latest upward or downward trend is stronger or weaker than the other candidates.

### Feature 2: Six-month relative performance

```text
relative_return_6m(i,t) = P(i,t) / P(i,t-6 months) - 1
relative_strength_6m = same-month percentile rank - 0.5
```

Before ranking, same-month extreme values are limited to the 1st and 99th percentiles. This feature answers whether the ETF performed better or worse than the other sector ETFs over six months.

### Feature 3: Six-month risk

```text
daily_return(i,d) = P(i,d) / P(i,d-1) - 1
risk_volatility_6m(i,t)
  = sqrt(252) * sample_std(latest 126 daily returns)
```

A larger value means larger recent price fluctuations. This feature remains in absolute volatility units and is not converted into a cross-sectional rank.

## Step 4: Run your stages

Generate the monthly table first:

```powershell
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage data
```

After confirming that the monthly file exists, generate the feature table:

```powershell
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage features
```

The model table is currently designed so that each row represents one candidate ETF in one signal month. It must include:

```text
signal_date, execution_date, return_date, ticker,
rank_current_trend_1m, relative_strength_6m, risk_volatility_6m,
target_return_1m
```

## Step 5: Check the hand-off to Member B

Run `python -m pytest` again. Confirm that the model table contains only the 20 candidate ETFs, not SPY; `signal_date + ticker` is unique; all three feature columns exist; and every labelled row satisfies `signal_date < execution_date < return_date`. A missing target in the latest month is normal because its future return is not yet known.

Give Member B both processed files and a short run note containing the run date, whether both commands succeeded, the row count, date range, ETF count, and any code changes you made. A separate data-quality report is not required.

Your responsibility ends with the model table. Do not run the `model`, `backtest`, or `evaluate` stages.
