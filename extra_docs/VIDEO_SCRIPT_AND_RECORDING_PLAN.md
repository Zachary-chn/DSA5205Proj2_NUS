# Group 18 — final video script and recording plan

Final arrangement: A → B → C → D. A, B and C explain the existing implementation and frozen outputs without executing pipeline commands. D alone executes all five stages in one isolated workspace on one machine. There are no ZIP handoffs between presenters. Each person records one screen-and-audio section; join the four finished videos with straight cuts.

## Part A — Storyboard and slide assignment

Use `extra_docs/VIDEO_PRESENTATION.pptx` in 16:9 presentation mode. All diagram elements, tables and text are editable; the five result plots are embedded original PNGs. No pipeline was executed while preparing these materials. The presentation uses corrected code/artifact facts even where the report still contains pending corrections.

`FROZEN` below means `artifacts/20261024T155915Z_final_us_industry_project/`. Source paths are relative to the repository root. VS Code tabs should be pre-opened; highlight a small relevant block rather than scroll through whole files. A–C open saved outputs read-only and do not run the commands displayed in D's instructions.

| Approximate global time | Presenter | Slide / screen sequence | Files/functions to show | Purpose |
|---|---|---|---|---|
| 00:00–00:40 | Member A | 1: question, presenter roles, workflow | No code yet | Economic rationale and workflow |
| 00:40–02:30 | Member A | 2 → VS Code → 2 | YAML; raw CSV; `data.py:validate_daily_prices`, `_annualized_log_price_slope`; `features.py:build_model_table` active branch | Universe, source, cleaning and three features |
| 02:30–04:00 | Member A | 3 → saved model-table row → 3 | `data.py:to_monthly_prices`; `data/processed/model_table_us_industry.csv` | Signal/entry/endpoint and target |
| 04:00–05:30 | Member B | 4 → code → 4 | `model.py:make_ridge` | Ridge, standardisation, fitting method |
| 05:30–07:20 | Member B | 3 reused → code → 4 | `split.py:assign_splits`; `model.py:_available_model_samples` | Chronology, unavailable labels and sample counts |
| 07:20–09:00 | Member B | 4 → saved tables → 4 | `model.py:fit_and_predict`; `FROZEN/alpha_validation.csv`, `validation_prediction_metrics.csv`, `predictions.csv`, `coefficients.csv` | Alpha selection, weak validation, fixed refit |
| 09:00–10:00 | Member C | 5 only | Selection rule; no code/CSV yet | Positive filter, Top-5, cash |
| 10:00–11:10 | Member C | 6 only | Equation legend and benchmark strip | Drift, fee budget and fairness |
| 11:10–11:50 | Member C | One VS Code visit → 7 | `strategy.py:build_positions` (24–34), `build_trades` (59–79); `backtest.py:_account_portfolio` (20–25) | Three short excerpts in one visit; no CSVs or execution |
| 11:50–12:50 | Member C | 7 → full-size scatter → full-size R² PNG → 8 | `figures/test_prediction_scatter.png`, `test_prediction_r2.png` | Weak OOS forecasting |
| 12:50–14:00 | Member C | 8 → full-size equity PNG → 8 | `figures/equity_curve.png` | Growth versus risk; no additional code/CSV switches |
| 14:00–15:15 | Member C | 9 → full-size drawdown → full-size annual PNG → 10 | `figures/annual_performance.png`, `drawdown.png` | Endpoint-year groups and sampled drawdown |
| 15:15–16:30, up to 17:00 | Member C | 10 | No established risk-adjusted alpha | Limitations, conclusion, handover |
| Approximately 16:30–21:30; adjust after rehearsal | Member D | VS Code/terminal only | One isolated workspace; five commands in Part C | Actual complete workflow; target 4–6 minutes |

### Timing budget

Actual spoken-word counts exclude all bracketed actions, code locators, commands, tables and wait instructions. Narration over a code/figure view is already counted once. Use approximately 125 words per minute so the guided excerpts remain short and the results have room to breathe.

| Internal presenter | Spoken words | Speech at 125 wpm | Brief navigation allowance | Expected section |
|---|---:|---:|---|---|
| Member A | 461 | 3:41 | About 20–30 seconds | About 4:00–4:15 |
| Member B | 589 | 4:43 | About 20–30 seconds | About 5:00 |
| Member C | 946 | 7:34 | About 15–25 seconds, with pre-opened images | About 7:45–8:00 |
| Member D | 429 | 3:26 | Actual command/output navigation and uncovered processing | Target 4–6 minutes; runtime unmeasured |
| Total | 2,425 | 19:24 speech alone | Navigation plus uncovered execution time | Aim for 21–22 minutes; roughly 20–23 minutes depending on execution |

At 120 wpm the spoken text takes 20:12; at 135 wpm it takes 17:58. Do not add every code hold as extra silent time: the following narration is the hold. Short excerpts should take about 10–20 seconds each; in a longer explanation, change the highlighted statement at the indicated sentence, not the entire window. If rehearsal needs more time, shorten cursor travel/scrolling first and transparently trim genuine processing waits. Stay within the assignment's 15–25 minutes. Exact stage durations have not been measured and the local timestamps are not runtime promises.

Do not add silent screens to fill a nominal slot. Speech and command execution can overlap and must not be added twice. D's exact runtime is unknown: rehearse on the recording machine. The 4–6 minute demo allowance is a recording target, not a claim that stages finish within a measured time. Shorten only genuine long waits with a clearly labelled cut. A–C should need only brief screen switches, not silent demonstrations.

### Verified code-excerpt locator sheet — internal recording notes

Use this sheet for pre-opening tabs; the live cues repeat the exact instructions at the speaking point. Every source path is repository-relative. The four source-review families A/B/C/D below are internal coordination IDs, not audience-facing labels. No code excerpt requires a complete-function scroll. D1–D3 are locator backups for rehearsal/debugging, not additional required on-camera visits; default demo screen is the running terminal and its generated outputs.

| Cue ID | File / function | Display lines | Highlight | Literal fallback search | Relevant statements |
|---|---|---|---|---|---|
| A1 | `src/combined_momentum/data.py` / `validate_daily_prices` | 178–196 | 178–188; then 190–196 | `if checked.duplicated(["date", "ticker"]).any():` | Duplicate/positive-price/symbol checks, then observed-date coverage threshold. |
| A2 | `src/combined_momentum/data.py` / `_annualized_log_price_slope` | 21–31 | 25–31 | `return 252.0 * daily_slope` | Regress log prices on the day index and annualise the slope. |
| A3 | `src/combined_momentum/features.py` / `build_model_table` | 96–114 | 99–105; then 112–114 | `frame["rank_current_trend_1m"] = (` | Six-month return, same-month clipping/ranking and current-trend rank. |
| A4 | `src/combined_momentum/data.py` / `to_monthly_prices` | 238–245 | 239–244 | `ordered["risk_volatility_6m"] = (` | Rolling sample volatility of daily returns, multiplied by square root of 252. |
| A5 | `src/combined_momentum/data.py` / `to_monthly_prices` | 246–261 | 246–249; then 259–261 | `next_execution_price = monthly.groupby("ticker")["execution_price"].shift(-1)` | Next-trading-close entry and next execution-price return target. |
| A6 | `src/combined_momentum/features.py` / `build_model_table` | 224–229 | 225–229 | `complete_features = frame[features].notna().all(axis=1)` | Nonfinite handling, complete-feature eligibility and monthly asset-count threshold. |
| B1 | `src/combined_momentum/model.py` / `make_ridge` | 20–26 | 23–24 | `("scale", StandardScaler()),` | Scaler and Ridge in the same fitted pipeline; no explicit solver override. |
| B2 | `src/combined_momentum/split.py` / `assign_splits` | 19–22 | 20–22 | `result["split"] = "outside"` | Assign chronological signal-date split labels. |
| B3 | `src/combined_momentum/model.py` / `_available_model_samples` | 40–53 | 47–52 | `table.loc[labelled & train & return_dates.le(validation_start)],` | Filter training/validation/refit rows by when their labels become available. |
| B4 | `src/combined_momentum/model.py` / `fit_and_predict` | 71–84 | 71–77; then 81–84 | `["validation_monthly_spearman_ic", "validation_mse"],` | Fit five training candidates, score validation, sort highest IC then lowest MSE. |
| B5 | `src/combined_momentum/model.py` / `fit_and_predict` | 91–103 | 92–100 | `scored["model_fit"] = np.where(early_mask, "train_only", "train_plus_validation")` | Single final refit; train-only early predictions versus final-model test predictions. |
| C1 | `src/combined_momentum/strategy.py` / `build_positions` | 24–34 | 26–34 | `test["target_weight"] = np.where(test["selected"], 1.0 / top_k, 0.0)` | Alphabetical ties, positive filter, Top-5 targets and residual cash. |
| C2 | `src/combined_momentum/strategy.py` / `build_trades` | 59–79 | 79; then 59–64 and 70–74 | `updated = rate * float(((1 - cost) * target - previous).abs().sum())` | Prior-period drift feeds current trades; solve costs and record actual ETF notionals. |
| C3 | `src/combined_momentum/backtest.py` / `_account_portfolio` | 20–25 | 24–25 | `portfolio["net_return"] = (1 - portfolio.transaction_cost) * (` | Merge actual fees and compound the post-fee investment budget with gross returns. |
| D1 | `src/combined_momentum/data.py` / `prepare_data` | 271–290 | 275; then 286–290 | `should_download = bool(settings.get("download", True)) and (force_download or not raw_path.exists())` | Cached-input branch, validation and monthly output; use only during an actual long data-stage wait. |
| D2 | `src/combined_momentum/model.py` / `_available_model_samples` | 40–53 | 50–52 | `table.loc[labelled & validation & return_dates.le(test_start)],` | Past-available labels; use only while the actual model command is still processing. |
| D3 | `src/combined_momentum/pipeline.py` / `run_pipeline` | 167–189 | 171–174; then 179–188 | `if original["config_sha256"] != file_sha256(config.config_path):` | Hash guards on backtest/evaluation inputs/source; use only during a real stage wait. |

These line references describe the actual source on disk, not a report excerpt. Supporting output fields are verified against saved CSV headers. Commands have been checked against `scripts/run_pipeline.py:15–24` (`parse_args`) and `28–37` (`main`); completion-field names come from `pipeline.py:71–119` and `122–152`. Fallback search: `print(json.dumps({"run_dir": str(run_dir)` locates the CLI completion print. No commands were run to prepare these instructions.

## Part B — Complete narration with synchronised screen actions

Only **Spoken** paragraphs are read aloud. Every bracketed line is an action, not speech. Follow cues from top to bottom; do not run ahead because a nominal timestamp has arrived. Code/figure visits are included in the narration time, not extra silent clips. Local times restart for each recording and are navigation guides only.

### Pre-recording setup — internal instructions, not narration

- Presenter assignments remain in Part A. Only the final demonstration executes commands. The first three recordings use original source and frozen outputs read-only.
- Pre-open PowerPoint in slideshow mode and VS Code. Disable Auto Save and save-on-format actions for the demonstration, close unrelated tabs and notifications, show line numbers, and use a readable code font (about 20–22 px). At this size a 10–21-line excerpt fits comfortably; hide Explorer/terminal for source views.
- VS Code navigation: open a repository-relative file with Quick Open (`Cmd+P` on macOS, `Ctrl+P` on Windows/Linux); use Go to Line (`Ctrl+G`, including Control+G on macOS) for the starting line. Select the exact highlighted lines without typing or editing. Search fallback strings are literal, case-sensitive searches with regex disabled. Do not scroll through entire functions.
- All line references below were read and verified in the current codebase on 9 November 2026. If the files change later, use the unique fallback string and recheck the local context; never assume the old line number still points at the right code.
- Prepare the output tabs specified below before recording. In a CSV, keep the header visible where possible; use Find to reach a specified row. Do not open every supporting CSV simply because it exists. For narrow date demonstrations, show the leading columns only. The later feature/target columns can remain off screen.
- For results, pre-open all five frozen PNGs. The scripted route shows them full size at fixed points, so there is no on-camera decision about whether slide labels are large enough. Slides 7–9 remain the audience's overview; full-size originals provide readable axes and legends at 1920×1080. After each PNG, follow the explicit return cue.
- Rehearse switching windows once without executing pipeline stages. Prepare the isolated workspace in Part C before the final recording. For the final demonstration, keep VS Code's integrated terminal and Explorer available together, and use the shell/session that holds the exported variables. The command examples here are future instructions, not evidence of an executed run.

### Data preparation, features and target timing (target about 4 minutes; slides 1–3)

[LOCAL GUIDE 00:00–00:45 — question and motivation]

[SHOW SLIDE 1] Display slide 1 in slideshow mode.

**Spoken:** Hi, we're Group 18. Our project asks whether three simple price signals can help us choose between industry ETFs each month. We'll explain how we prepared the data, trained the model and turned forecasts into a portfolio. We'll then discuss the results, before our final presenter runs the complete workflow in a separate demonstration workspace.

[POINT TO VISUAL] Follow the five workflow boxes from Data to Evaluate as you describe the project.

**Spoken:** The idea is that industries don't all respond to the economy in the same way. Recent strength might continue as information spreads, but a sharp short-term move might also reverse. We combine signals from different horizons and let the model estimate their relationship with the next holding-period return.

[LOCAL GUIDE 00:45–01:30 — universe and source]

[SHOW SLIDE 2] Display slide 2 in slideshow mode.

**Spoken:** We use 20 U.S.-listed sector and industry ETFs, with monthly decisions in U.S. dollars. SPY is our broad-market benchmark and stays outside the candidate rankings.

[SWITCH TO VS CODE] Switch to the prepared output-viewing window.

[OPEN SAVED OUTPUT] `configs/final_us_industry_project.yaml`. Go to lines 11–22; point to `tickers` (15), `benchmark_tickers` (16), source/date settings (12–19). This is configuration, not a function. Read-only view; do not edit or save.

**Spoken:** Daily prices come from Yahoo Finance. The saved snapshot runs from January 2007 to October 2026; only data through February 2026 are needed to finish our final test holding period.

[RETURN TO SLIDE 2] Switch back to PowerPoint slideshow, slide 2.

[POINT TO VISUAL] Point to the predecessor-history qualification at the bottom of slide 2.

**Spoken:** Adjusted closes approximate returns including splits and distributions. There is one important history qualification: before December 2011, SMH represents Semiconductor HOLDRS Trust, a predecessor instrument. We aren't claiming that today's ETF existed throughout the earlier sample.

[LOCAL GUIDE 01:30–02:50 — one grouped cleaning/features code visit]

[SWITCH TO VS CODE] Use the prepared source-code window; do not execute commands.

[OPEN CODE — A1] `src/combined_momentum/data.py` → function `validate_daily_prices`. Go to line 178; keep only lines 178–196 in view.

[HIGHLIGHT CODE — A1] Highlight 178–188; then 190–196. Duplicate/positive-price/symbol checks, then observed-date coverage threshold. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `if checked.duplicated(["date", "ticker"]).any():`.

**Spoken:** The cleaning code checks duplicate records, positive prices, required symbols and coverage. It doesn't fill gaps or remove large market returns just because they look unusual.

[OPEN CODE — A6] `src/combined_momentum/features.py` → `build_model_table`, lines 224–229. Highlight 225–229: nonfinite values become missing, complete features are required and monthly candidate counts are checked. Fallback search: `complete_features = frame[features].notna().all(axis=1)`. Spend about 10 seconds here, including a brief pointer sweep; stay in the same VS Code visit.

**Spoken:** Rows need all three inputs, with at least 18 eligible ETFs in a month.

[OPEN CODE — A2] `src/combined_momentum/data.py` → function `_annualized_log_price_slope`. Go to line 21; keep only lines 21–31 in view.

[HIGHLIGHT CODE — A2] Highlight 25–31. Regress log prices on the day index and annualise the slope. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `return 252.0 * daily_slope`.

**Spoken:** The first input ranks the slope of log prices over 21 trading days. It asks which ETFs have the strongest recent trend.

[OPEN CODE — A3] `src/combined_momentum/features.py` → function `build_model_table`. Go to line 96; keep only lines 96–114 in view.

[HIGHLIGHT CODE — A3] Highlight 99–105; then 112–114. Six-month return, same-month clipping/ranking and current-trend rank. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `frame["rank_current_trend_1m"] = (`.

**Spoken:** The second ranks six-month returns, after limiting cross-sectional extremes at the first and ninety-ninth percentiles. It captures medium-term relative strength.

[OPEN CODE — A4] `src/combined_momentum/data.py` → function `to_monthly_prices`. Go to line 238; keep only lines 238–245 in view.

[HIGHLIGHT CODE — A4] Highlight 239–244. Rolling sample volatility of daily returns, multiplied by square root of 252. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `ordered["risk_volatility_6m"] = (`.

**Spoken:** The third measures the sample volatility of 126 daily returns. It stays in absolute units, so the model can distinguish calmer from more volatile price paths.

[RETURN TO SLIDE 2] Switch back to PowerPoint slideshow, slide 2.

**Spoken:** These inputs are deliberately small in number. They describe recent direction, medium-term performance and risk without adding many possible explanations to a limited sample. All are calculated from prices already observed at the decision, rather than from information revealed later.

[LOCAL GUIDE 02:50–04:15 — label timing and one saved row]

[SHOW SLIDE 3] Display slide 3 in slideshow mode.

[POINT TO VISUAL] Point first to 31 Jan, then 1 Feb in the timing strip.

**Spoken:** The timing is just as important as the inputs. We observe the month-end close, calculate a signal after that close, and assume execution at the next trading close.

[SWITCH TO VS CODE] Use the prepared source-code window; do not execute commands.

[OPEN CODE — A5] `src/combined_momentum/data.py` → function `to_monthly_prices`. Go to line 246; keep only lines 246–261 in view.

[HIGHLIGHT CODE — A5] Highlight 246–249; then 259–261. Next-trading-close entry and next execution-price return target. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `next_execution_price = monthly.groupby("ticker")["execution_price"].shift(-1)`.

**Spoken:** The target is the return from that entry to the following monthly execution price.

[RETURN TO SLIDE 3] Switch back to PowerPoint slideshow, slide 3.

[POINT TO VISUAL] Trace 31 Jan 2019 → 1 Feb 2019 → 1 Mar 2019.

**Spoken:** For the first test signal, that means a decision on January thirty-first, 2019, entry on February first, and a holding return ending on March first.

[SWITCH TO VS CODE] Switch to the prepared output-viewing window.

[OPEN SAVED OUTPUT] `data/processed/model_table_us_industry.csv`. Go to line 2762; fallback Find `2019-01-31,2019-02-01,2019-03-01,IBB,`. Point to the first four fields: signal, execution, endpoint and ticker. Do not read the long numeric row. Read-only view; do not edit or save.

**Spoken:** The future return is the answer the model tries to predict, not information used to choose the position. This saved table puts the inputs, target and dates together. Next, we'll explain how we fit the model while respecting when those answers become available.

[RETURN TO SLIDE 3] Switch back to PowerPoint slideshow, slide 3.

### Ridge modelling and chronological validation (target about 5 minutes; slide 4 and slide 3 reused)

[LOCAL GUIDE 00:00–01:30 — model and scaler]

[SHOW SLIDE 4] Display slide 4 in slideshow mode.

**Spoken:** We need one forecast from the three signals, so we use Ridge regression. It's a linear model fitted across all ETF-month observations. A common model shares information across industries, but assumes their return relationships are similar enough for that to help. It won't capture every industry-specific effect or changing market regime.

**Spoken:** Ridge discourages large coefficients. That's useful because the signals overlap and monthly returns are noisy: a complicated-looking pattern can easily be a coincidence.

[SWITCH TO VS CODE] Use the prepared source-code window; do not execute commands.

[OPEN CODE — B1] `src/combined_momentum/model.py` → function `make_ridge`. Go to line 20; keep only lines 20–26 in view.

[HIGHLIGHT CODE — B1] Highlight 23–24. Scaler and Ridge in the same fitted pipeline; no explicit solver override. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `("scale", StandardScaler()),`.

**Spoken:** We standardise inputs before fitting so their different units don't determine the strength of the penalty. The scaler is part of the training pipeline, so it learns its mean and standard deviation from the fitting sample, not from future data.

[RETURN TO SLIDE 4] Switch back to PowerPoint slideshow, slide 4.

[POINT TO VISUAL] Point to the auto/Cholesky footer; keep slide 4 on screen for the environment explanation.

**Spoken:** The implementation uses scikit-learn's automatic solver selection. The saved fitted model records Cholesky as the solver actually used. This is a numerical solution to penalised least squares, not a stochastic training loop. Our configuration records seed 5205, and the metadata records the software versions used.

[LOCAL GUIDE 01:30–03:15 — timeline explanation, followed by one grouped chronology/selection code visit]

[SHOW SLIDE 3] Point to the three split ranges, then the boundary-label statement below them.

**Spoken:** We split chronologically. Training signals run from July 2007 through December 2014. Validation covers 2015 to 2018, and testing covers 2019 to 2025. Training estimates coefficients, validation selects the penalty, and the test evaluates the fixed choice.

[POINT TO VISUAL] Keep slide 3 visible. Trace the unfinished December label into February; no code switch during this conceptual explanation.

**Spoken:** There's a subtler issue at the boundaries. A December signal's return doesn't finish until February. So December 2014 is labelled as training, but its answer isn't known at the first validation signal. We exclude it from candidate fitting. Likewise, December 2018 cannot enter model selection or the final refit because its answer isn't available when testing starts.

[SWITCH TO VS CODE] Begin the grouped chronology/selection/output visit. Remain in VS Code until the explicit return to slide 4 at the end of this section.

[OPEN CODE — B2] `src/combined_momentum/split.py` → function `assign_splits`. Go to line 19; keep only lines 19–22 in view.

[HIGHLIGHT CODE — B2] Highlight 20–22. Assign chronological signal-date split labels. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `result["split"] = "outside"`.

**Spoken:** Randomly mixing months would let later market conditions influence earlier forecasts. These assignments use signal dates; the next check also considers when each return becomes available.

[OPEN CODE — B3] `src/combined_momentum/model.py` → function `_available_model_samples`. Go to line 40; keep only lines 40–53 in view.

[HIGHLIGHT CODE — B3] Highlight 50–51 for the following eligibility/count explanation. Filter training/validation/refit rows by when their labels become available. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `table.loc[labelled & train & return_dates.le(validation_start)],`.

**Spoken:** That leaves 1,780 observations for candidate fitting and 940 for validation. The code uses the return's completion date, not just the signal date, to check availability.

[HIGHLIGHT CODE — B3] Without moving windows, highlight line 52 for about 15–20 seconds. It permits all train/validation rows whose returns are complete at the first test signal, which is why December 2014 can re-enter. Keep the function name and lines 40–53 visible.

**Spoken:** Once selection is finished, December 2014 can re-enter because its return is now known. The final refit has 2,740 observations. This also explains why that number isn't simply the sum of the two earlier eligible samples.

[LOCAL GUIDE 03:15–05:10 — one grouped model-selection/output visit]

[OPEN CODE — B4] `src/combined_momentum/model.py` → function `fit_and_predict`. Go to line 71; keep only lines 71–84 in view.

[HIGHLIGHT CODE — B4] Highlight 71–77 for the candidate-fitting sentence. Fit five training candidates, score validation, sort highest IC then lowest MSE. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `["validation_monthly_spearman_ic", "validation_mse"],`.

**Spoken:** We try five penalty values: 0.01, 0.1, 1, 10 and 100.

[HIGHLIGHT CODE — B4] Now highlight lines 81–84 while explaining the highest-IC rule and MSE tie-break. Stay in the same file; no scroll beyond this 14-line excerpt.

**Spoken:** We choose the highest average monthly Spearman rank IC, which measures whether the model orders next month's better performers above the worse performers. That matches a strategy that will buy the top-ranked forecasts. Exact ties use lower validation mean squared error.

[OPEN SAVED OUTPUT] `artifacts/20261024T155915Z_final_us_industry_project/alpha_validation.csv`. Show lines 1–3. Point to alpha 0.1 and 0.01, their equal IC and the final digits of MSE. Fallback Find `0.1,-0.06763717805151175`. Read-only view; do not edit or save.

**Spoken:** Alpha 0.1 is selected. Its IC ties with 0.01, but its squared error is slightly lower. The selected validation rank IC is about minus 0.06764. It's the best candidate under our rule, but it still ranks returns poorly.

[OPEN SAVED OUTPUT] `artifacts/20261024T155915Z_final_us_industry_project/validation_prediction_metrics.csv`. Show header and validation row, line 3. Point to `r2_vs_train_mean` and `monthly_spearman_ic`; fallback Find `validation,940,`. Read-only view; do not edit or save.

**Spoken:** Validation R-squared is slightly positive, about 0.000448. These aren't contradictory: ranking and squared forecast errors measure different things.

**Spoken:** Our prediction R-squared uses a fixed historical training mean as its comparison. That baseline stays unchanged in testing. We don't compare against a mean calculated from future test returns, or update the baseline using information that wasn't available at the model-selection boundary.

[OPEN CODE — B5] `src/combined_momentum/model.py` → function `fit_and_predict`. Go to line 91; keep only lines 91–103 in view.

[HIGHLIGHT CODE — B5] Highlight 92–100. Single final refit; train-only early predictions versus final-model test predictions. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `scored["model_fit"] = np.where(early_mask, "train_only", "train_plus_validation")`.

**Spoken:** We refit once on eligible training and validation observations, then freeze the model for every test month. The output identifies training-only predictions separately from test predictions made by that refit.

[OPEN SAVED OUTPUT] `artifacts/20261024T155915Z_final_us_industry_project/coefficients.csv`. Show header and all three rows; point only to coefficient signs. No prediction-table scrolling is required. Read-only view; do not edit or save.

**Spoken:** The fitted signs suggest medium-term continuation, short-term reversal and a positive volatility tilt, but these are associations rather than proven causes.

[RETURN TO SLIDE 4] Switch back to PowerPoint slideshow, slide 4.

**Spoken:** Shrinkage, the small feature set and limited chronological search reduce overfitting; they don't guarantee useful predictions. Next, let's see what happens when those forecasts become investments.

### Trading, performance and interpretation (allow 7–8 minutes; slides 5–10)

[LOCAL GUIDE 00:00–01:00 — allocation]

[SHOW SLIDE 5] Display slide 5 in slideshow mode.

[POINT TO VISUAL] Trace the positive filter → Top 5 → 20% boxes.

**Spoken:** A forecast needs an investment rule before we can judge it as a strategy. We keep only positive predicted returns, choose the five highest scores, and assign 20 percent to each selected ETF. Exact ties are resolved alphabetically. If fewer than five qualify, unused slots stay in cash rather than increasing the other weights. Cash earns zero; we don't borrow or short sell.

[POINT TO VISUAL] Point to the residual-cash example and long-only/no-leverage card.

**Spoken:** In the saved test, five ETFs qualify every month, so the cash fallback never activates. But five tickers don't necessarily mean five independent risks. A bank ETF and a broad financial-sector ETF can have overlapping exposure. Our rule limits individual target weights, not every underlying economic risk.

[LOCAL GUIDE 01:00–02:40 — drift, fees and benchmarks]

[SHOW SLIDE 6] Display slide 6 in slideshow mode.

[POINT TO VISUAL] Point to the drift card, before referring to either equation.

**Spoken:** Between rebalances, holdings move away from their targets. If an ETF starts at 20 percent and rises faster than the rest, it becomes a larger share of wealth. That's drift. We calculate trades from what we actually own after those moves, not just from last month's target weights.

[POINT TO VISUAL] Point to the transaction-cost panel and the 10 bp card.

**Spoken:** We charge ten basis points on each purchase and sale. Turnover adds purchases and sales without dividing by two, so a full rotation can approach 200 percent. Fees come out of the portfolio itself. That leaves less money to invest, and our targets apply to the wealth remaining after fees. The cost calculation finds trades and fees that fit the same budget.

[POINT TO VISUAL] Point to c, then target and pre-trade weight definitions below the cost equation.

**Spoken:** In the equation, c is the fee as a fraction of wealth before trading. The target weights refer to wealth after fees; the pre-trade weights describe the holdings after they have drifted. The sum adds the ETF trade amounts.

[POINT TO VISUAL] Point to the separate net holding-period return equation.

**Spoken:** Gross return is what the holdings earn before fees. Net return reflects the fee and the return on the wealth still invested. We compound net returns. Entry fees are included, but there is no terminal liquidation: ending holdings are marked to market.

[POINT TO VISUAL] Point to the equal-weight/SPY strip at the bottom of slide 6.

**Spoken:** Equal weight holds all 20 ETFs at five percent each and rebalances monthly with the same accounting. SPY pays the same entry fee rate and is then held. Both share the strategy's execution dates. The rate is consistent, but total fees differ because trading differs. Missing or misaligned benchmark observations raise an error instead of disappearing from the comparison.

[LOCAL GUIDE 02:40–03:25 — one code visit, three excerpts only]

[SWITCH TO VS CODE] Use the prepared source-code window; do not execute commands.

[OPEN CODE — C1] `src/combined_momentum/strategy.py` → function `build_positions`. Go to line 24; keep only lines 24–34 in view.

[HIGHLIGHT CODE — C1] Highlight 26–34. Alphabetical ties, positive filter, Top-5 targets and residual cash. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `test["target_weight"] = np.where(test["selected"], 1.0 / top_k, 0.0)`.

**Spoken:** The selection function applies the positive filter and ranks the remaining forecasts. These lines set fixed target weights and leave unused allocation in cash.

[OPEN CODE — C2] `src/combined_momentum/strategy.py` → function `build_trades`. Go to line 59; keep only lines 59–79 in view.

[HIGHLIGHT CODE — C2] Highlight 79; then 59–64 and 70–74. Prior-period drift feeds current trades; solve costs and record actual ETF notionals. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `updated = rate * float(((1 - cost) * target - previous).abs().sum())`.

**Spoken:** The previous holding period determines the drifted weights. The solver then finds affordable trades and fees together. Executed weights are measured against pre-trade wealth, while target weights refer to what remains after fees.

[OPEN CODE — C3] `src/combined_momentum/backtest.py` → function `_account_portfolio`. Go to line 20; keep only lines 20–25 in view.

[HIGHLIGHT CODE — C3] Highlight 24–25. Merge actual fees and compound the post-fee investment budget with gross returns. Aim for 10–20 seconds with the following narration; no line-by-line reading. Fallback: search the unique literal `portfolio["net_return"] = (1 - portfolio.transaction_cost) * (`.

**Spoken:** This line combines the fee and the return on wealth still invested. Benchmark rules apply consistent dates and costs. Let's now look at the outcomes.

[LOCAL GUIDE 03:25–04:15 — prediction diagnostics]

[RETURN TO SLIDE 7] Switch back to PowerPoint slideshow, slide 7.

[POINT TO VISUAL] Point to the R²/IC strip. Keep the metric definitions visible.

**Spoken:** The forecasting results are weak. There are 1,680 test forecasts across 84 signal months. Test R-squared is about 0.005713: only a 0.57 percent reduction in squared error against the fixed historical training-mean forecast. Average monthly rank IC is about 0.019424, also close to zero.

[OPEN FULL-SIZE FIGURE] `artifacts/20261024T155915Z_final_us_industry_project/figures/test_prediction_scatter.png` in the prepared VS Code image tab. Hide Explorer/terminal; use Fit to Window with axes and legend visible. Narrate while pointing. Never recreate, crop or resave the image.

**Spoken:** The scatter shows narrow predictions against much wider realised returns.

[OPEN FULL-SIZE FIGURE] `artifacts/20261024T155915Z_final_us_industry_project/figures/test_prediction_r2.png` in the prepared VS Code image tab. Hide Explorer/terminal; use Fit to Window with axes and legend visible. Narrate while pointing. Never recreate, crop or resave the image.

**Spoken:** Annual R-squared changes sign. Together with negative validation IC, this doesn't establish stable prediction skill.

[LOCAL GUIDE 04:15–05:30 — growth versus risk]

[RETURN TO SLIDE 8] Switch back to PowerPoint slideshow, slide 8.

[POINT TO VISUAL] Compare CAGR across the three table rows; do not read every cell.

**Spoken:** The portfolio nevertheless achieves higher compound growth. After costs, its annualised return is 20.19 percent, against 14.76 percent for equal weight and 16.20 percent for SPY.

[OPEN FULL-SIZE FIGURE] `artifacts/20261024T155915Z_final_us_industry_project/figures/equity_curve.png` in the prepared VS Code image tab. Hide Explorer/terminal; use Fit to Window with axes and legend visible. Narrate while pointing. Never recreate, crop or resave the image.

**Spoken:** One unit grows to about 3.62, compared with 2.86 in SPY. This is a genuine difference within the saved simulation, but it isn't the whole performance story.

[RETURN TO SLIDE 8] Switch back to PowerPoint slideshow, slide 8.

[POINT TO VISUAL] Point to volatility, then compare strategy and SPY Sharpe.

**Spoken:** We calculate growth geometrically. Volatility uses sample monthly standard deviation, annualised by the square root of twelve. Sharpe uses mean monthly return divided by that standard deviation, with a zero risk-free rate. Strategy volatility is almost 30 percent, compared with about 17 percent for SPY. Its Sharpe is 0.771, below SPY's 0.962 and slightly below equal weight. Higher return therefore does not mean better risk-adjusted performance.

[LOCAL GUIDE 05:30–06:40 — drawdown and annual grouping]

[SHOW SLIDE 9] Display slide 9 in slideshow mode.

[OPEN FULL-SIZE FIGURE] `artifacts/20261024T155915Z_final_us_industry_project/figures/drawdown.png` in the prepared VS Code image tab. Hide Explorer/terminal; use Fit to Window with axes and legend visible. Narrate while pointing. Never recreate, crop or resave the image.

**Spoken:** The drawdown makes the risk difference clear. The strategy's largest sampled fall from a prior peak is 43.57 percent, versus 23.79 percent for SPY. Initial wealth is included, but observations are monthly holding endpoints, so daily losses could have been worse.

[OPEN FULL-SIZE FIGURE] `artifacts/20261024T155915Z_final_us_industry_project/figures/annual_performance.png` in the prepared VS Code image tab. Hide Explorer/terminal; use Fit to Window with axes and legend visible. Narrate while pointing. Never recreate, crop or resave the image.

**Spoken:** Results also vary by period. The strategy trails both benchmarks early, then has strong relative outcomes in 2022 and 2023, before trailing both again in 2024. Annual groups use the year when each holding period ends, not conventional calendar-year investment boundaries. The first and last groups contain ten and two observations. The large annualised Sharpe from only two observations in 2026 should not be treated as reliable evidence.

[LOCAL GUIDE 06:40–08:00 — interpretation and conclusion]

[RETURN TO SLIDE 10] Switch back to PowerPoint slideshow, slide 10.

**Spoken:** Weak forecasts and strong growth can coexist because forecast metrics evaluate all ETFs, while the portfolio holds only the top five. Concentration and favourable periods can strongly affect compounded wealth. The volatility coefficient is consistent with a risk tilt, but we haven't established how much performance came from skill, exposure or luck. We make no claim of statistically significant alpha.

[POINT TO VISUAL] Keep slide 10 visible; no additional CSV or code visit for turnover.

**Spoken:** Trading is also quite active: average monthly turnover is about 89 percent. The sum of monthly fee fractions is about 7.52 percentage points, but that isn't a standalone dollar loss or compounded drag. Each monthly fraction refers to wealth at a different date, which is why the distinction matters.

[POINT TO VISUAL] Point to the limitations strip, then finish on the three conclusion cards.

**Spoken:** Retrospective universe selection can introduce survival and selection bias. SMH includes predecessor history, and vendor adjustments aren't independently reconstructed. Exact close fills, constant fees and zero cash interest simplify real trading. A fixed model can become stale. Chronological code controls also can't prove that every earlier research choice was independent of the holdout. Our conclusion is higher historical growth with more risk, not demonstrated forecasting superiority. To finish, we'll run the complete workflow so you can see how the outputs are produced.

### End-to-end workflow demonstration (target 4–6 minutes; terminal/VS Code only)

[RECORDING NOTE] No PowerPoint needed. Complete Part C setup off camera. Open the demo directory in VS Code and keep one integrated terminal with the same exported variables. Pre-open an empty editor tab for generated outputs. The terminal commands below must be executed exactly once in the isolated copy; the copies in Part C are reference instructions, not additional runs. The setup's `DSA_VIDEO_PYTHON`, `DSA_VIDEO_RUN` and other exports must be present in this shell. If VS Code opened a different shell, export those variables there before recording and verify `pwd`; do not launch a command with empty variables. No stage duration is assumed.

[SWITCH TO VS CODE] Show Explorer rooted in the disposable directory. Keep the terminal visible.

[EXECUTE TERMINAL — identity only]

```sh
pwd
printf '%s\n' "$DSA_VIDEO_RUN"
```

[SHOW WORKSPACE] Point to copied `src/`, `configs/`, `scripts/` and `data/raw/prices_daily_us_industry.csv`. There should be no generated `data/processed/` or `artifacts/video_demo_group18/` yet. Do not open the original frozen artifacts in this recording window.

**Spoken:** I'll now run the full workflow, starting with our saved raw price snapshot. This is a separate demonstration directory, with copied code and configuration. It doesn't contain the frozen model or final results. New outputs will use a different run ID, so this demonstration won't overwrite our submission artifacts. The earlier sections explained existing results; this section shows actual execution.

[FOCUS TERMINAL] Return to the same integrated shell in the demo root.

[EXECUTE TERMINAL — data] Press Enter on camera, then speak the following paragraph while it processes.

```sh
"$DSA_VIDEO_PYTHON" -B scripts/run_pipeline.py \
  --config configs/final_us_industry_project.yaml \
  --stage data
```

**Spoken:** First I run data preparation. It reads the cached Yahoo file, checks the records and builds monthly prices with execution-aligned returns. We aren't making a fresh network download, which could return revised vendor data.

[WAIT FOR SUCCESS — data] Do not advance until the shell prompt returns with no traceback and the actual JSON summary is visible. Point to `stage: data`, `daily_rows`, `monthly_rows`, `assets`; expected cached-input counts are 104601, 4998 and 21. There is no per-ETF progress display in the current CLI. If still processing after the explanation, keep the running terminal visible and say “This stage is still processing.” Do not read a success sentence until it has finished. If necessary, trim only the measured wait with a visible omitted-time label; retain launch and completion.

[OPEN SAVED OUTPUT] `data/processed/prices_monthly_us_industry.csv`. DEMO FILE, opened in the current copied workspace. Show header and first rows with date, ticker, execution date/price. Do not accidentally open the original workspace CSV. Read-only view; do not edit or save.

**Spoken:** Here is the successful summary and the monthly output.

[FOCUS TERMINAL] Return to the same integrated shell in the demo root.

[EXECUTE TERMINAL — features] Press Enter on camera, then speak the following paragraph while it processes.

```sh
"$DSA_VIDEO_PYTHON" -B scripts/run_pipeline.py \
  --config configs/final_us_industry_project.yaml \
  --stage features
```

**Spoken:** Next I run feature construction. It reads that monthly file and writes the three model inputs.

[WAIT FOR SUCCESS — features] Do not advance until the shell prompt returns with no traceback and the actual JSON summary is visible. Point to `stage: features`, `model_rows`, `signal_months`, `assets`; expected 4640, 232 and 20. There is no per-ETF progress display in the current CLI. If still processing after the explanation, keep the running terminal visible and say “This stage is still processing.” Do not read a success sentence until it has finished. If necessary, trim only the measured wait with a visible omitted-time label; retain launch and completion.

[OPEN SAVED OUTPUT] `data/processed/model_table_us_industry.csv`. DEMO FILE. Show the header and first row. Point to three feature names, then signal/execution/return fields. Read-only view; do not edit or save.

**Spoken:** This generated table contains the signal date, entry date, return endpoint and target, alongside the features. These are the data the next command will actually use.

[FOCUS TERMINAL] Return to the same integrated shell in the demo root.

[EXECUTE TERMINAL — model] Press Enter on camera, then speak the following paragraph while it processes.

```sh
"$DSA_VIDEO_PYTHON" -B scripts/run_pipeline.py \
  --config configs/final_us_industry_project.yaml \
  --stage model --run-id "$DSA_VIDEO_RUN"
```

**Spoken:** Now I run the model stage. This single stage fits the five Ridge candidates, compares them on eligible validation observations, selects alpha and refits the final model. Validation isn't a separate command. While it runs, the availability checks keep unfinished labels out of fitting. The model stage writes its settings and environment into metadata.

[WAIT FOR SUCCESS — model] Do not advance until the shell prompt returns with no traceback and the actual JSON summary is visible. Point to `run_dir` ending in `artifacts/video_demo_group18`, `selected_alpha`, `prediction_rows`, `test_rows`; expected 0.1, 4440 and 1680. There is no per-ETF progress display in the current CLI. If still processing after the explanation, keep the running terminal visible and say “This stage is still processing.” Do not read a success sentence until it has finished. If necessary, trim only the measured wait with a visible omitted-time label; retain launch and completion.

**Spoken:** The completion summary reports the selected alpha and prediction count.

[OPEN SAVED OUTPUT] `artifacts/video_demo_group18/alpha_validation.csv`. DEMO FILE. Show header and first two candidates. Point to selected alpha 0.1. Read-only view; do not edit or save.

**Spoken:** Here is the new alpha table.

[OPEN SAVED OUTPUT] `artifacts/video_demo_group18/predictions.csv`. DEMO FILE. Show header, `predicted_return`, `model_fit` and `selected_alpha`. Use horizontal scrolling only to these pre-identified columns; do not read every field. Read-only view; do not edit or save.

**Spoken:** Here are the saved predictions in our demonstration folder. I will use those newly generated predictions for backtesting, rather than substitute the original saved forecasts.

[FOCUS TERMINAL] Return to the same integrated shell in the demo root.

[EXECUTE TERMINAL — backtest] Press Enter on camera, then speak the following paragraph while it processes.

```sh
"$DSA_VIDEO_PYTHON" -B scripts/run_pipeline.py \
  --config configs/final_us_industry_project.yaml \
  --stage backtest --run-id "$DSA_VIDEO_RUN"
```

**Spoken:** The backtest reads that prediction file, forms positions and calculates drift-adjusted trades, fees and benchmark returns. It checks the configuration and model-table hashes against the model record.

[WAIT FOR SUCCESS — backtest] Do not advance until the shell prompt returns with no traceback and the actual JSON summary is visible. Point to `stage: backtest`, `backtest_months`, `average_selected_assets`, `average_turnover`; expected 84, 5.0 and about 0.894751. There is no per-ETF progress display in the current CLI. If still processing after the explanation, keep the running terminal visible and say “This stage is still processing.” Do not read a success sentence until it has finished. If necessary, trim only the measured wait with a visible omitted-time label; retain launch and completion.

[OPEN SAVED OUTPUT] `artifacts/video_demo_group18/trades.csv`. DEMO FILE. Show header and first few rows. Point to `previous_weight`, `target_weight`, `executed_weight` and `estimated_cost`. Read-only view; do not edit or save.

**Spoken:** Here are the separate target, previous and executed weights.

[OPEN SAVED OUTPUT] `artifacts/video_demo_group18/portfolio_returns.csv`. DEMO FILE. Show header and first row: signal 2019-01-31, execution 2019-02-01, endpoint 2019-03-01. This is the holding-period evidence, not a new metric table. Read-only view; do not edit or save.

**Spoken:** Here are the completed holding periods. These files connect the forecasts to the realised portfolio returns.

[FOCUS TERMINAL] Return to the same integrated shell in the demo root.

[EXECUTE TERMINAL — evaluate] Press Enter on camera, then speak the following paragraph while it processes.

```sh
"$DSA_VIDEO_PYTHON" -B scripts/run_pipeline.py \
  --config configs/final_us_industry_project.yaml \
  --stage evaluate --run-id "$DSA_VIDEO_RUN"
```

**Spoken:** Finally, evaluation reads the portfolio returns and predictions, checks their provenance, and writes performance tables and all five figures. It doesn't fit another model.

[WAIT FOR SUCCESS — evaluate] Do not advance until the shell prompt returns with no traceback and the actual JSON summary is visible. Point to `stage: evaluate`, `annualized_return`, `sharpe_ratio`, `max_drawdown`; expected strategy values about 0.201919, 0.770546 and −0.435736. There is no per-ETF progress display in the current CLI. If still processing after the explanation, keep the running terminal visible and say “This stage is still processing.” Do not read a success sentence until it has finished. If necessary, trim only the measured wait with a visible omitted-time label; retain launch and completion.

[OPEN SAVED OUTPUT] `artifacts/video_demo_group18/metrics.csv`. DEMO FILE. Show three portfolio rows and the CAGR/volatility/Sharpe/drawdown columns. Do not edit or save.

**Spoken:** Here are the generated metrics.

[SHOW GENERATED FIGURE DIRECTORY] In the same demo Explorer, expand `artifacts/video_demo_group18/figures/`. Point to the five generated PNG filenames.

**Spoken:** Here is the figure directory.

[OPEN GENERATED FIGURE] Open `artifacts/video_demo_group18/figures/equity_curve.png` full size. This must be the newly generated demo figure, not the frozen PNG. Hide the terminal for the image view.

**Spoken:** And this is the new equity curve. The outputs should agree numerically with the frozen analysis within reasonable floating-point tolerance; any material difference needs investigation, not replacement of the original results.

[FOCUS TERMINAL] Return to the same shell. Execute the original-file preservation check from Part C, subsection 4, now; it only reads the protected original files and compares their hashes.

[WAIT FOR PRESERVATION CHECK] Show the actual “Original protected source, data, model/results and report unchanged.” output. If it fails, do not state that the originals are unchanged; investigate.

[SHOW GENERATED OUTPUTS] Keep the demo `artifacts/video_demo_group18/` folder expanded next to that successful check.

**Spoken:** That completes data preparation, feature construction, model fitting and validation, backtesting with costs, and evaluation. Everything was generated in this isolated directory, and the original protected files remain unchanged. This reproduces the calculation process; it isn't a second independent test of the strategy. It brings us back to our main finding: higher historical growth came with more risk, while forecasting skill remained weak. Thank you.

[END RECORDING] Leave the final folder/check visible for a brief breath, then stop. The recording now contains actual execution of all five stages in order. Do not rerun evaluation to obtain a second success screen. Full environment preparation, safeguards and long-wait handling remain in Part C.

## Part C — D's safe execution procedure

Only D executes pipeline stages. A–C use existing source and saved outputs read-only. No archive transfers, multi-machine stage dependencies or shared demonstration footage are needed.

### 1. Off-camera isolated setup

The following macOS/Linux commands are instructions for the future recording, not commands executed during this preparation. Start in the original repository root with its working `.venv`. The helper copies only source, scripts, configuration, tests, environment specifications and the cached raw snapshot. It deliberately does not copy processed data, trained models or previous results. All generated paths resolve inside the copied workspace because configuration loading uses the parent of the copied `configs` directory.

```sh
export DSA_VIDEO_SOURCE="$PWD"
export DSA_VIDEO_PYTHON="$PWD/.venv/bin/python"
export DSA_VIDEO_DEMO="$(mktemp -d /tmp/dsa5205-video-XXXXXX)"
export DSA_VIDEO_RUN=video_demo_group18

"$DSA_VIDEO_PYTHON" -B - <<'PY'
import hashlib, json, os, shutil
from pathlib import Path
source = Path(os.environ['DSA_VIDEO_SOURCE']).resolve()
demo = Path(os.environ['DSA_VIDEO_DEMO']).resolve()
assert demo != source and source not in demo.parents
assert not any(demo.iterdir())
for name in ('src', 'scripts', 'configs', 'tests'):
    shutil.copytree(source / name, demo / name,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
for name in ('requirements.txt', 'pyproject.toml'):
    shutil.copy2(source / name, demo / name)
(demo / 'data/raw').mkdir(parents=True)
shutil.copy2(source / 'data/raw/prices_daily_us_industry.csv',
             demo / 'data/raw/prices_daily_us_industry.csv')
protected = []
for name in ('src', 'scripts', 'configs', 'data', 'artifacts', 'submission'):
    protected.extend(p for p in (source / name).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts
                     and p.name != '.DS_Store')
manifest = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in protected}
(demo / 'original_hashes.json').write_text(json.dumps(manifest, indent=2))
print('ISOLATED WORKSPACE:', demo)
print('Copied raw input only; no processed data or frozen artifacts.')
PY

cd "$DSA_VIDEO_DEMO"
export MPLCONFIGDIR="$DSA_VIDEO_DEMO/.matplotlib"
export PYTHONDONTWRITEBYTECODE=1
pwd
"$DSA_VIDEO_PYTHON" -B --version
"$DSA_VIDEO_PYTHON" -B -m pip check
```

The original Python interpreter is reused, but code imports and all pipeline outputs resolve to the disposable copy. Bytecode and matplotlib caches are directed away from the original project. Do not install or upgrade packages in the original environment for recording. If needed, create a fresh environment in the demo directory using Python 3.12 and install `FROZEN/member_c_requirements.txt`, then set `DSA_VIDEO_PYTHON` to its absolute interpreter path. B/C's historical environments differ; record the actual environment and compare numbers rather than expecting identical model/PNG bytes across versions. On Windows use equivalent PowerShell syntax and `.venv\Scripts\python.exe`, or run these commands in WSL; do not paste POSIX syntax unchanged into PowerShell.

A new run ID alone would not protect the original workspace: data/features overwrite shared processed paths and model fitting updates `artifacts/LATEST_RUN.txt`. Never execute these commands in the original tree, use the frozen run ID, or pass `--force-download`. Keep the copied YAML unchanged so provenance checks remain meaningful.

### 2. On-camera stage commands — exactly this order

Run separately and show each actual successful completion before proceeding. Pretype commands but press Enter on camera. The active `download: true` reuses the copied raw CSV unless forced; no new download is required for this reproducibility run.

```sh
# 1 — validate/build monthly data from cached raw snapshot
"$DSA_VIDEO_PYTHON" -B scripts/run_pipeline.py \
  --config configs/final_us_industry_project.yaml --stage data

# 2 — construct features and model table
"$DSA_VIDEO_PYTHON" -B scripts/run_pipeline.py \
  --config configs/final_us_industry_project.yaml --stage features

# 3 — candidate fitting, validation selection and final refit
"$DSA_VIDEO_PYTHON" -B scripts/run_pipeline.py \
  --config configs/final_us_industry_project.yaml \
  --stage model --run-id "$DSA_VIDEO_RUN"

# 4 — trading and accounting from newly generated predictions
"$DSA_VIDEO_PYTHON" -B scripts/run_pipeline.py \
  --config configs/final_us_industry_project.yaml \
  --stage backtest --run-id "$DSA_VIDEO_RUN"

# 5 — prediction/portfolio evaluation and figures
"$DSA_VIDEO_PYTHON" -B scripts/run_pipeline.py \
  --config configs/final_us_industry_project.yaml \
  --stage evaluate --run-id "$DSA_VIDEO_RUN"
```

### 3. Completion evidence and expected files

| Stage | Expected files inside disposable root | Show actual evidence |
|---|---|---|
| data | `data/processed/prices_monthly_us_industry.csv` | JSON rows/assets and aligned dates; raw snapshot has 104,601 rows, 21 symbols |
| features | `data/processed/model_table_us_industry.csv` | Three inputs, target and dates; 20 candidates |
| model | `artifacts/video_demo_group18/model.joblib`, `predictions.csv`, `alpha_validation.csv`, `coefficients.csv`, `split_summary.csv`, `validation_prediction_metrics.csv`, `latest_signal_predictions.csv`, `run_metadata.json` | Expected alpha 0.1, 4,440 prediction rows and 1,680 test rows; show actual alpha table and model-fit identifiers |
| backtest | Same new run: `positions.csv`, `trades.csv`, `portfolio_returns.csv`, `member_c_backtest_metadata.json` | 84 periods, five mean holdings; inspect drift/target/executed weights |
| evaluate | Same new run: `metrics.csv`, `prediction_metrics.csv`, `annual_performance.csv`, `annual_prediction_metrics.csv`, `cumulative_returns.csv`, five PNGs and `member_c_evaluate_metadata.json` | Expected strategy CAGR ~0.201919, Sharpe ~0.770546, drawdown ~−0.435736; open generated metrics/equity |

Use generated files as evidence, not the expected-value table. There is no `--stage validation`: validation occurs in `model`. Evaluation requires the backtest metadata; never skip an earlier stage or bypass a failed hash check. Do not run the frozen C reproduction commands from the report appendix: they overwrite C's saved outputs and do not demonstrate model fitting.

Optional read-only table display after actual evaluation:

```sh
"$DSA_VIDEO_PYTHON" -B - <<'PY'
from pathlib import Path
import os
import pandas as pd
p = Path('artifacts') / os.environ['DSA_VIDEO_RUN']
for name in ('alpha_validation.csv', 'prediction_metrics.csv', 'metrics.csv'):
    print('\n' + name)
    print(pd.read_csv(p / name).to_string(index=False))
PY
```

### 4. Confirm original-file preservation

After the stages, optionally show this read-only comparison. Avoid simultaneous report edits during the check, as those legitimate changes would also be detected. Only say the files are unchanged after it passes.

```sh
"$DSA_VIDEO_PYTHON" -B - <<'PY'
import hashlib, json, os
from pathlib import Path
source = Path(os.environ['DSA_VIDEO_SOURCE'])
manifest = json.loads(Path('original_hashes.json').read_text())
changed = [name for name, digest in manifest.items()
           if not (source / name).is_file()
           or hashlib.sha256((source / name).read_bytes()).hexdigest() != digest]
assert not changed, f'Original files changed: {changed}'
print('Original protected source, data, model/results and report unchanged.')
PY
```

### 5. Runtime rehearsal and honest editing

Rehearse once in a fresh disposable workspace before recording and note stage timings. For the recorded run use another new workspace and the same frozen choices; the rehearsal is an operational check, not tuning. Do not rerun in the original project. Rehearsal may reveal environment problems; fix those without changing strategy parameters.

D records screen and narration together in one take where practical. Explain the short stage description while the command runs. If a stage finishes early, inspect its real output rather than stretch the explanation. If a stage exceeds the available explanation, say it is still processing. Keep the launch and actual successful completion. An exceptional long wait can be trimmed with a visible card, for example “Data build: 48 seconds of processing omitted”; replace the number with the measured time. Do not splice frozen results into a failed run or imply instant completion. Retain the uncut recording. If the overall video would exceed 25 minutes, shorten waits transparently before cutting core methodology. If execution fails, do not claim end-to-end success until resolved.

