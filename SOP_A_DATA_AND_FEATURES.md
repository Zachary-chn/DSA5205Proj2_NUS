# 组员 A：数据处理与特征构造 SOP

## 先了解整个项目

这个项目研究美国股票行业 ETF 轮动。我们每个月比较 20 只美国宽行业和细分行业 ETF，用当时已经出现的价格数据预测下一个月的收益。模型会参考三个信息：最近一个月的价格趋势、最近六个月的相对表现，以及最近六个月的波动程度。B 用这些数据训练模型，C 把模型预测转换成持仓并测试，D 整理报告。你的工作位于整个流程的第一步。

## 项目已经为你准备了什么

原始数据已经放在：

```text
data/raw/prices_daily_us_industry.csv
```

这里包含 20 只候选 ETF 和市场基准 SPY 的日价格。候选 ETF 为 `XLY, XLP, XLE, XLF, XLV, XLI, XLK, XLB, XLU, IBB, IYR, ITB, KBE, KRE, XHB, XME, XOP, XRT, SMH, IYT`。你不需要寻找或下载数据。`scripts/download_raw_data.py` 只是数据丢失或全组决定重新下载时才使用的备用程序。

项目也已经提供了基础代码：

```text
src/combined_momentum/data.py
src/combined_momentum/features.py
```

你不需要从空白文件开始写。你的任务是读懂自己负责的代码，确认计算方法与下面的说明一致，运行并检查输出。如果代码与实际数据不匹配，由你修改这两个文件和相关测试；不要修改 B、C 的模型和交易代码。

## 你要交付什么

你需要生成：

```text
data/processed/prices_monthly_us_industry.csv
data/processed/model_table_us_industry.csv
```

第一个文件把日价格整理成月度观察，并安排好信号日期和实际成交日期。第二个文件加入三个特征和下个月实际收益，B 会直接用它训练模型。

## 开始前的准备

在项目根目录打开 PowerShell。第一次使用时执行：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
```

以后重新进入项目，只需要先执行 `.venv\Scripts\Activate.ps1`。如果测试失败，先处理报错，不要继续生成交接文件。

## 第一步：看懂原始文件

打开原始 CSV，确认至少有：

| 字段 | 含义 |
|---|---|
| `date` | 交易日期 |
| `ticker` | ETF 代码 |
| `adjusted_close` | 考虑分红和拆股后的收盘价 |

文件中还可能有 `raw_close`、`dividends`、`stock_splits`、`source` 和 `downloaded_at_utc`。项目的收益、趋势和风险统一使用 `adjusted_close` 计算。

目前数据范围设计成上述 20 只美国行业 ETF 加 SPY。SPY 只用于最后的市场比较，不参与特征排名，也不会进入 B 的训练数据。完整的行业名称和纳入规则见 `extra_docs/FINAL_US_INDUSTRY_UNIVERSE.md`。

## 第二步：检查并整理日价格

这一部分由 `data.py` 中的 `validate_daily_prices()` 和 `to_monthly_prices()` 完成。

`validate_daily_prices()` 应确认：同一个日期和 ticker 只能出现一次；`adjusted_close` 不能缺失且必须大于 0；21 个 ticker 都存在；每只 ETF 的日期覆盖率至少达到配置文件中的 95%。发现问题时程序应直接报错，让你检查原始文件，不能静默删除某只 ETF。

`to_monthly_prices()` 会在每个自然月保留最后一个可用交易日。这个日期叫信号日期，因为模型在这一天收盘后读取价格并形成预测。模拟成交价格使用信号日之后的第一个可用收盘价，避免假设我们能够在看到月末收盘价的同时按同一个价格成交。

月度文件中的关键字段是：

| 字段 | 含义 |
|---|---|
| `date` | 形成特征和预测的月末信号日期 |
| `execution_date` | 信号形成后的第一个可用交易日 |
| `execution_price` | 模拟买入时使用的调整收盘价 |
| `return_date` | 这一期持有结束的日期 |
| `target_return_1m` | 从本期成交价到下一期成交价的实际收益 |

下个月实际收益的公式是：

```text
target_return_1m(i,t)
  = execution_price(i,t+1) / execution_price(i,t) - 1
```

## 第三步：计算三个特征

这一部分先在 `data.py` 中准备日频趋势和波动信息，再由 `features.py` 中的 `build_model_table()` 完成月度排名和模型表。

### 特征一：最近一个月的相对趋势

对每只 ETF 最近 21 个交易日的调整价格取对数，然后用日期顺序解释价格变化：

```text
log(P(i,d)) = a(i,t) + b(i,t) * d + error(i,d)
current_trend_1m(i,t) = 252 * b(i,t)
```

`b` 为正表示这一个月整体向上，为负表示整体向下。随后，在同一个月比较 20 只 ETF 的趋势强弱：

```text
rank_current_trend_1m = 当月趋势的百分位排名 - 0.5
```

这个特征回答：这只 ETF 最近一个月的上升或下降趋势，相比其他候选 ETF 更强还是更弱。

### 特征二：最近六个月的相对表现

```text
relative_return_6m(i,t) = P(i,t) / P(i,t-6 months) - 1
relative_strength_6m = 当月六个月收益的百分位排名 - 0.5
```

排名前，代码会把同月极端值限制在 1% 和 99% 分位之间。这个特征回答：这只 ETF 过去六个月相比其他行业 ETF 表现得更好还是更差。

### 特征三：最近六个月的风险

```text
daily_return(i,d) = P(i,d) / P(i,d-1) - 1
risk_volatility_6m(i,t)
  = sqrt(252) * sample_std(latest 126 daily returns)
```

数值越高表示近期价格波动越大。它保留原始波动率，不转换成 ETF 之间的排名。

## 第四步：运行你负责的阶段

先生成月度数据：

```powershell
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage data
```

确认月度文件出现后，再生成特征表：

```powershell
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage features
```

目前特征表设计成每一行代表某个月的一只候选 ETF，至少包含：

```text
signal_date, execution_date, return_date, ticker,
rank_current_trend_1m, relative_strength_6m, risk_volatility_6m,
target_return_1m
```

## 第五步：交给 B 之前检查

再次运行 `python -m pytest`。确认模型表中只有 20 只候选 ETF，没有 SPY；同一个 `signal_date + ticker` 没有重复；三个特征列都存在；所有有标签的行都满足 `signal_date < execution_date < return_date`。最后一个月没有下个月收益属于正常情况。

检查完成后，把两个 processed 文件和运行说明交给 B。说明中写清运行日期、两条命令是否成功、数据行数、日期范围、ETF 数量，以及你是否修改过代码。这里不需要制作单独的数据质量报告。

你的工作到模型表结束。不要运行 `model`、`backtest` 或 `evaluate`。
