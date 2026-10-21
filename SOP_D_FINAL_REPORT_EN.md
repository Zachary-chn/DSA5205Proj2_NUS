# Member D: Final Report and Video SOP

## Understand the project first

This project studies sector ETF rotation. Member A prepares the data and three features, Member B uses Ridge to predict next-month returns, and Member C converts predictions into a Top-5 portfolio and performs the final test. Your job is to organise their methods and one consistent set of results into a clear, complete, and reproducible report and video.

Member D does not reprocess data, retrain the model, or rerun the backtest. You must understand the workflow, verify every source, and explain it in language a reader can follow.

## What the project already provides

Research design and calculations are documented in:

```text
README.md
README_CN.md
configs/final_us_industry_project.yaml
extra_docs/FINAL_US_INDUSTRY_UNIVERSE.md
SOP_A_DATA_AND_FEATURES.md
SOP_B_TRAIN_AND_VALIDATE.md
SOP_C_TRADING_AND_TESTING.md
```

Member C gives you an exact run ID. Final numbers and figures are stored in:

```text
artifacts/<run_id>/
```

You do not need to write Python model code. Your working materials are the report, video, `extra_docs/FINAL_RESULTS_TEMPLATE.md`, and contribution statement.

## What you must deliver

The submission directory is currently designed as:

```text
submission/Group_<number>_Report.pdf
submission/Group_<number>_Video.mp4
submission/Group_<number>_Contribution.md
```

If the course accepts a video link, a clearly labelled link file may replace the MP4. Follow the course requirements for final names, report length, and video duration.

## Step 1: Confirm that all files belong to one run

Confirm the run ID with Members B and C. The directory should contain at least:

```text
run_metadata.json
split_summary.csv
alpha_validation.csv
validation_prediction_metrics.csv
coefficients.csv
prediction_metrics.csv
positions.csv
trades.csv
portfolio_returns.csv
metrics.csv
annual_performance.csv
figures/
```

Every report number and figure must come from this run ID. Do not combine attractive results from different run directories.

## Step 2: Complete the results worksheet

Open `extra_docs/FINAL_RESULTS_TEMPLATE.md` and enter the run ID, Git commit, data download time, data range and row count, selected alpha, three coefficients, test prediction metrics, strategy results after costs, both comparison results, and figure names used in the report.

This worksheet is the report's single number checklist. Use it when writing the report and preparing the video so the same metric does not appear in multiple versions.

## Step 3: Write the report

The report is currently designed in the following order.

### 1. Research question

Explain whether recent trend, relative performance, and risk may help predict a sector ETF's next-month return, and whether those predictions can form a monthly rotation strategy after transaction costs.

### 2. Data and ETF universe

Describe the 20 U.S. industry ETFs, the broad-sector and specialised-industry structure, sample dates, adjusted closing prices, and why SPY is only a market comparison. Explain that the universe was defined from industry exposure, launch date, and data completeness.

### 3. Timing

Explain that the signal is formed after the month-end close and execution occurs at the next available close. Describe the purpose of the training, validation, and test periods and why the dates cannot be randomly shuffled.

### 4. Features and prediction target

Explain the one-month relative trend, six-month relative performance, and six-month volatility in plain language and include the exact README formulas. The target is the one-month return from the current execution price to the next execution price.

### 5. Ridge and validation

Explain the linear prediction, feature scaling, purpose of Ridge regularisation, five alpha candidates, and use of average monthly validation Spearman IC to choose alpha.

### 6. Trading rule and costs

Explain the positive-prediction filter, maximum of five ETFs, fixed 20% weight per selected ETF, cash when fewer than five qualify, turnover, 10-basis-point cost, and return-after-cost formula.

### 7. Final test results

Report prediction metrics first. Then compare the strategy, equal-weight 20-ETF universe, and SPY using annualised return, volatility, Sharpe ratio, maximum drawdown, and cumulative return. Include cumulative wealth, drawdown, annual return, and prediction-versus-realised-return figures.

### 8. What the model learned

Use `coefficients.csv` to explain coefficient signs and relative sizes. Describe associations found in the data, not certain causal effects.

### 9. Strong and weak periods

Use annual results and figures to explain when the strategy performed better or worse. Consider the number of holdings, cash allocation, risk, and turnover as possible explanations.

### 10. Limitations and conclusion

Discuss sample size, ETF launch dates, transaction-cost assumptions, monthly rebalancing, the linear model, and changing market conditions. Report weak results directly and explain them.

### 11. Reproducibility and contributions

Record the configuration file, run ID, Git commit, common run command, and each member's contribution.

## Step 4: Prepare tables, figures, and video

Tables should include the sample range, five-alpha validation results, three model coefficients, and final metrics for all three portfolios. Automatically generated figures are in `artifacts/<run_id>/figures/`. Label each table and figure with the test period, whether transaction costs are included, and the benchmark name.

Use the same structure for the video. Do not introduce a different temporary result set. Members may present their own sections; Member D coordinates the introduction, conclusion, visual style, and timing.

## Step 5: Complete the consistency check

Member D does not rerun the data, model, or backtest. Check the run ID, test dates, alpha, coefficients, metrics, and figure paths used in the report. Return inconsistencies to the responsible member instead of manually changing generated results.

Record the reproducibility commands in the report:

```powershell
python -m pytest
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml
```

Copy `extra_docs/CONTRIBUTION_NOTE_TEMPLATE.md` and complete names, responsibilities, checked files, and presentation sections. Before submission, confirm that the report and video use one run ID, formulas match the README, results include transaction costs, the equal-weight portfolio, and SPY, and all filenames follow the course requirements.
