# DSA5205 Project 2：三信号股票行业 ETF 轮动策略

[English README](README.md)

本仓库是一个面向四人小组的、可以直接交接和执行的项目框架。研究问题、特征公式、模型类型、交易规则、文件接口和运行命令已经确定；最终清洗数据、特征表、拟合模型、验证选择、测试结果、系数解释和收益分析则有意留空，由组员分别运行并汇总。

## 1. 项目当前状态

| 环节 | 当前状态 | 负责人 |
|---|---|---|
| 最终原始数据 | 已下载，尚未校验或转换 | 组员 A |
| 最终清洗数据及三特征模型表 | 空，尚未生成 | 组员 A |
| 模型训练与验证 | 空，尚未运行 | 组员 B |
| 交易实施与最终测试 | 空，尚未运行 | 组员 C |
| 最终报告与展示 | 空 | 组员 D |

在正式整理本仓库之前，我们随便取过一小组 ETF，用来确认特征公式和运行流程大致可行。这部分探索数据不属于正式项目的数据集、训练过程或最终报告结果。

## 2. 研究设想

我们在每个月末比较一组股票行业 ETF。研究假设是：一只 ETF 下个月的总收益，可能与其近期价格路径中的三个不同部分有关。

1. **近期相对趋势：** 最近一个月的价格趋势相对于同一日期的其他候选 ETF 更强还是更弱。
2. **中期相对强弱：** 最近六个月内，它相对于同一日期的其他行业 ETF 表现更强还是更弱。
3. **风险强度：** 最近六个月内，它的日收益路径相对稳定还是波动较大。

三个部分的语义彼此独立。第一个比较不同 ETF 的近期趋势，第二个比较它们的中期收益，第三个衡量近期波动的绝对幅度。Ridge 回归负责从历史数据中估计每个部分的重要程度，以及它与下个月收益之间究竟是正向还是负向关系。

最终系数的方向不提前指定。组员必须在完成尚未使用的最终数据测试后，再汇报实际系数及其经济含义。

## 3. 最终 ETF 样本

最终候选池由 20 只在美国上市的股票行业 ETF 构成。所有候选 ETF 都代表美国股票市场中的一个行业部分，因此可以在同一个月进行合理比较，同时保持足够的行业差异。名单包括 9 只宽行业 ETF 和 11 只细分行业 ETF。

| 分组 | ETF | 行业范围 |
|---|---|---|
| 宽行业 | XLY | 非必需消费品 |
| 宽行业 | XLP | 必需消费品 |
| 宽行业 | XLE | 能源 |
| 宽行业 | XLF | 金融 |
| 宽行业 | XLV | 医疗保健 |
| 宽行业 | XLI | 工业 |
| 宽行业 | XLK | 信息技术 |
| 宽行业 | XLB | 材料 |
| 宽行业 | XLU | 公用事业 |
| 细分行业 | IBB | 生物科技 |
| 细分行业 | IYR | 美国房地产 |
| 细分行业 | ITB | 美国住宅建设 |
| 细分行业 | KBE | 银行业 |
| 细分行业 | KRE | 区域银行 |
| 细分行业 | XHB | 房屋建造商 |
| 细分行业 | XME | 金属与采矿 |
| 细分行业 | XOP | 石油与天然气勘探生产 |
| 细分行业 | XRT | 零售 |
| 细分行业 | SMH | 半导体 |
| 细分行业 | IYT | 运输 |

SPY 会一并下载，但只作为美国股票市场的买入并持有比较对象，不参与特征排名、模型训练或 Top 5 选取。样本从 2007 年 1 月开始，此时 20 只候选 ETF 都已经成立。名单依据美国股票行业属性、成立时间、数据覆盖和调整后日价格可获得性确定，说明中的纳入规则不使用策略历史收益。

完整的样本规则和来源见 [`extra_docs/FINAL_US_INDUSTRY_UNIVERSE.md`](extra_docs/FINAL_US_INDUSTRY_UNIVERSE.md)。目前项目参数设计成 [`configs/final_us_industry_project.yaml`](configs/final_us_industry_project.yaml) 中记录的内容。

## 4. 三个特征的准确公式

令 `P(i,t)` 表示在信号日期 `t` 已知的 ETF `i` 的拆股和分红调整后收盘价。

### 特征一：一个月当前趋势排名

使用最近 21 个交易日，将调整后价格的对数对日序号进行线性回归：

```text
log(P(i,d)) = a(i,t) + b(i,t) * d + error(i,d)
current_trend_1m(i,t) = 252 * b(i,t)
```

随后把斜率转换为同一信号日期内的横截面百分位排名：

```text
rank_current_trend_1m(i,t) = rank(i,t) / N(t) - 0.5
```

数值越高，表示该 ETF 最近一个月的价格方向相对于其他候选 ETF 越强。使用排名可以降低低波动行业和高波动行业之间的量纲差异。

### 特征二：六个月相对强弱排名

首先计算六个月调整价格收益：

```text
relative_return_6m(i,t) = P(i,t) / P(i,t-6 months) - 1
```

在同一日期的横截面中进行 1% 和 99% 分位数缩尾，再转换为排名：

```text
relative_strength_6m(i,t)
    = rank(relative_return_6m(i,t)) / N(t) - 0.5
```

数值越高，表示该 ETF 在过去六个月中战胜了更多候选行业 ETF。

### 特征三：六个月已实现波动率

使用最近 126 个交易日的调整价格日收益：

```text
daily_return(i,d) = P(i,d) / P(i,d-1) - 1
risk_volatility_6m(i,t)
    = sqrt(252) * sample_std(daily_return over 126 days)
```

该特征保留绝对数值，不进行横截面排名，因为它的作用就是区分真实的低波动和高波动价格路径。

### 预测标签

信号在月份最后一个交易日收盘后形成。`execution_price(i,t)` 是信号形成后的第一个可用调整收盘价。下一个月的预测标签为：

```text
target_return_1m(i,t)
    = execution_price(i,t+1) / execution_price(i,t) - 1
```

信号日期的收盘价不会同时被当作可成交价格，从而避免使用构造信号的同一个收盘价完成交易。

## 5. 模型与验证 SOP

模型把所有候选 ETF 的月度观察放在一起，估计一套通用的 Ridge 规则。拟合之前，只使用训练集的均值和标准差对各项特征进行标准化。

```text
在截距和 beta 上最小化：
    sum[(target_return_1m - intercept - X * beta)^2]
    + alpha * sum[beta_j^2]
```

预先确定的正则化参数候选值为：

```text
alpha = [0.01, 0.1, 1, 10, 100]
```

时间划分已经在 YAML 配置文件中固定：

| 阶段 | 信号日期 | 允许的用途 |
|---|---|---|
| 训练集 | 截止 2014-12-31 | 拟合标准化器和每个候选 Ridge 模型 |
| 验证集 | 2015-01-01 至 2018-12-31 | 根据平均月度 Spearman 排名 IC 选择 alpha |
| 测试集 | 2019-01-01 至 2025-12-31 | 由组员 C 进行最终测试 |

组员 B 必须保存每个 alpha 的验证得分。选定 alpha 后，使用训练集加验证集重新拟合标准化器和 Ridge 模型。测试数据不能参与标准化、alpha 选择、特征定义、ETF 名单确定或交易规则确定。

## 6. 从预测到交易的规则

在每个信号日期，为 20 只候选 ETF 生成预测。只保留预测下个月收益为正的 ETF，按照预测值从高到低排序，最多选择五只。每只被选中的 ETF 获得 20% 目标权重。若正预测不足五只，未使用的部分保留为现金，因此组合始终是只做多且不使用杠杆。

组合在下一个可用交易日收盘价再平衡。令 `w(i,t)` 为新的目标权重，`w(i,t-1)` 为上期目标权重：

```text
one_way_turnover(t) = sum_i |w(i,t) - w(i,t-1)|
transaction_cost(t) = 0.001 * one_way_turnover(t)
net_return(t) = gross_return(t) + cash_return(t) - transaction_cost(t)
```

必须与候选 ETF 等权组合以及买入并持有 SPY 进行比较。最终需要报告扣除成本后的年化收益、年化波动率、Sharpe ratio 和最大回撤。预测 RMSE、样本外 R-squared 和月度排名 IC 也必须报告，即使结果较弱或为负。

## 7. 四人分工与数据交接

实际运行存在先后顺序，但由于每个环节的文件接口已经固定，四位组员可以并行编写、检查和准备各自负责的内容。

| 负责人 | 需要完成的工作 | 输入 | 输出 |
|---|---|---|---|
| 组员 A：数据与特征 | 清洗并校验原始价格，对齐月度信号与成交日期，计算标签，构造目前设计的三个特征并交付模型表 | 最终 YAML 和原始 CSV | 月度 CSV 和 `model_table_us_industry.csv` |
| 组员 B：训练与验证 | 读取完整模型表，执行时间划分，拟合仅使用训练数据的标准化器，比较目前设计的 alpha 候选值并保存 Ridge 模型 | 模型表 | 拟合模型、验证表、系数和预测文件 |
| 组员 C：交易与测试 | 实施正预测 Top 5 规则，生成仓位和交易，计算成本与基准比较，并生成最终测试指标和图表 | B 的模型预测和最终 YAML | 仓位、交易、组合收益、测试指标、年度结果和图表 |
| 组员 D：最终报告 | 把研究设想、公式、方法和输出整合进报告与视频，并确认所有数字对应同一个 run ID | 组员 A-C 的输出 | 最终报告、展示或视频材料以及贡献说明 |

每位组员在读取上一阶段文件之前，都应确认上一阶段已经完成交接。A 完成数据和特征后交给 B，B 完成训练和验证后交给 C，C 完成交易和测试后交给 D。D 根据这些文件写报告。

每个人都有一份从头到尾可逐项执行的独立 SOP。组员只需打开自己的文件：

- [组员 A SOP：数据清洗与特征构造](SOP_A_DATA_AND_FEATURES.md)
- [组员 B SOP：模型训练与验证](SOP_B_TRAIN_AND_VALIDATE.md)
- [组员 C SOP：交易实施与最终测试](SOP_C_TRADING_AND_TESTING.md)
- [组员 D SOP：最终报告与提交](SOP_D_FINAL_REPORT.md)

四份英文版分别为 [`SOP_A_DATA_AND_FEATURES_EN.md`](SOP_A_DATA_AND_FEATURES_EN.md)、[`SOP_B_TRAIN_AND_VALIDATE_EN.md`](SOP_B_TRAIN_AND_VALIDATE_EN.md)、[`SOP_C_TRADING_AND_TESTING_EN.md`](SOP_C_TRADING_AND_TESTING_EN.md) 和 [`SOP_D_FINAL_REPORT_EN.md`](SOP_D_FINAL_REPORT_EN.md)。

## 8. 文件与字段规范

全部表格使用带表头的 UTF-8 CSV。日期格式为 `YYYY-MM-DD`；收益、权重和成本使用小数；ticker 使用大写字符串。任何阶段都不应手动修改另一阶段生成的文件。

| 阶段 | 预期路径 | 必须包含的内容 |
|---|---|---|
| 原始下载 | `data/raw/prices_daily_us_industry.csv` | `date,ticker,adjusted_close,raw_close,dividends,stock_splits,source,downloaded_at_utc` |
| 月度清洗数据 | `data/processed/prices_monthly_us_industry.csv` | 信号日期、ticker、调整价格、下一成交日期和价格、趋势输入、波动率输入、目标收益 |
| 模型表 | `data/processed/model_table_us_industry.csv` | 每个候选 ETF 和信号日期一行，准确包含三个特征、标签和成交日期 |
| 模型输出 | `artifacts/<run_id>/predictions.csv` | 数据划分、三个特征、实际收益、预测值、预测排名和选定 alpha |
| 组合输出 | `artifacts/<run_id>/positions.csv`、`trades.csv`、`portfolio_returns.csv` | 选择标记、权重、权重变化、换手率、成本和净收益 |
| 评估输出 | `artifacts/<run_id>/metrics.csv`、`annual_performance.csv`、`figures/` | 题目要求的指标和样本外图表 |

最终 processed 文件和最终 artifact 目录目前有意不存在。

## 9. 数据阶段检查标准

这些检查属于组员 A 的数据处理步骤。只要任一必要条件不满足，数据阶段就立即停止；不再单独生成所谓的“数据质量报告”：

```text
主键                     = (date, ticker)，且唯一
adjusted_close           > 0，且不得缺失
配置中的代码             = 20 只候选 ETF 加 SPY
每只候选 ETF 的最短历史  = 24 个月
每只代码的日历覆盖率     >= 95%
每月具有完整特征的候选数 >= 18
```

调整检查需要比较调整收盘价和原始收盘价计算的日收益。二者在分红或公司行动附近出现差异属于预期现象，需要记录和解释，不应自动删除。

## 10. 运行命令

在项目根目录使用 Python 3.11 或更高版本：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
```

原始价格文件已经下载。如果需要从公开来源重新获取：

```powershell
python scripts\download_raw_data.py --config configs\final_us_industry_project.yaml
```

每个人只运行自己 SOP 中的阶段。组员 A 运行：

```powershell
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage data
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage features
```

组员 B 运行：

```powershell
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage model
```

组员 B 把生成的 run ID 交给组员 C。组员 C 在两个命令中显式填写这个 ID：

```powershell
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage backtest --run-id <RUN_ID>
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage evaluate --run-id <RUN_ID>
```

组员 D 读取同一个 run 文件夹并填写 [`extra_docs/FINAL_RESULTS_TEMPLATE.md`](extra_docs/FINAL_RESULTS_TEMPLATE.md)。任何人都不应手动修改自动生成的数据文件或结果文件。

全组完成所有阶段检查后，可使用下面的命令进行一次干净的端到端复现：

```powershell
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml
```

## 11. 项目目录结构

```text
configs/
    final_us_industry_project.yaml       目前使用的项目参数
data/raw/
    prices_daily_us_industry.csv         最终未处理输入
data/processed/
    组员 A 生成的月度数据和三特征模型表
SOP_*.md
    组员 A-D 各自的中英文执行说明
extra_docs/
    ETF 样本定义、空白结果表和贡献说明模板
scripts/
    download_raw_data.py 和 run_pipeline.py
src/combined_momentum/
    可复现的流水线实现
tests/
    公式、时间泄漏和组合规则测试
artifacts/
    组员 B 创建运行目录，组员 C 补充测试与交易结果
submission/
    组员 D 存放最终报告及视频或其他提交材料
```

## 12. 当前有意留空的内容

项目目前不会对最终数据质量、选定 alpha、系数大小或方向、预测能力、入选 ETF、换手率、收益、Sharpe ratio、最大回撤、基准比较、成功时期、失败时期或经济解释作出任何结论。组员完成流水线之前，这些内容应一直在最终结果工作表中保持为空。

最终报告和 15–25 分钟视频应按照与本 README 相同的顺序展开：市场和交易时点、数据检查、特征公式、Ridge 与过拟合控制、时间顺序验证、预测到仓位的规则、交易成本、最终测试、结果解释和可复现性。所有最终数字和图表都必须来自同一个 run ID。
