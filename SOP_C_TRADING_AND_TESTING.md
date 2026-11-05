# 组员 C：交易实施与最终测试 SOP

## 先了解整个项目

A 已经整理价格和特征，B 已经训练 Ridge 并为每只 ETF 生成下个月收益预测。你的工作是把预测转换成月度持仓，加入换仓成本，再比较策略、20 只 ETF 等权组合和 SPY 的表现。D 会直接使用你生成的数字和图表写报告。

## 项目已经为你准备了什么

B 会给你一个明确的 run ID。你需要读取：

```text
artifacts/<run_id>/predictions.csv
data/processed/prices_monthly_us_industry.csv
configs/final_us_industry_project.yaml
```

基础代码位于：

```text
src/combined_momentum/strategy.py
src/combined_momentum/backtest.py
src/combined_momentum/evaluation.py
```

你不需要从空白文件开始写回测。你需要读懂预测如何变成仓位、换手率如何变成成本、三个组合如何比较，然后运行并检查结果。发现问题时，由你修改这三个文件和相关测试；不要重新训练 B 的模型，也不要改 A 的特征表。

## 第一步：看懂预测文件

`predictions.csv` 每一行代表某个月的一只 ETF。回测只使用 `split = test` 的行。`predicted_return` 决定持仓，`target_return_1m` 是后来实际发生的收益，用于计算持有结果。

## 第二步：把预测转换成仓位

目前交易规则设计成：删除预测收益小于或等于 0 的 ETF；对剩余 ETF 从高到低排序；最多选择前 5 只；每只入选 ETF 的权重固定为 20%。

| 正预测数量 | 持有数量 | ETF 总权重 | 现金权重 |
|---|---:|---:|---:|
| 5 只或更多 | 5 | 100% | 0% |
| 3 只 | 3 | 60% | 40% |
| 1 只 | 1 | 20% | 80% |
| 0 只 | 0 | 0% | 100% |

少于 5 只时不要把入选 ETF 放大到满仓。组合只做多，不借钱，也不做空。

## 第三步：计算换仓和成本

现已采用漂移权重和自融资交易成本计算，替代旧的目标权重差近似。
完整公式、成本定义及复现说明见
[SOP 英文版第三步](SOP_C_TRADING_AND_TESTING_EN.md#step-3-calculate-turnover-and-transaction-costs)。
每次交易先用上一持有期已实现收益计算交易前权重，再支付买卖金额的 10 bp
成本；每只入选 ETF 仍占扣费后财富的 20%，未使用资金留在现金。

## 第四步：两个比较对象

等权组合每个月平均持有全部 20 只候选 ETF，用来判断模型选股是否优于直接平均持有。SPY 代表美国整体股票市场，它的收益从 A 的月度文件读取，没有进入训练或 Top 5 选择。

## 第五步：运行回测和评估

把 `<RUN_ID>` 换成 B 给你的真实名称：

```powershell
python -m pytest
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage backtest --run-id <RUN_ID>
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage evaluate --run-id <RUN_ID>
```

`backtest` 生成仓位、交易和月度组合收益；`evaluate` 计算最终指标和图表。

预测部分目前包括测试期 RMSE、MAE、样本外 R-squared 和平均月度 Spearman IC。交易部分对策略、等权组合和 SPY 计算年化收益、年化波动率、Sharpe ratio、最大回撤、正收益月份比例和累计收益。策略还报告平均换手率和累计交易成本。结果好坏都原样保留。

## 第六步：检查并交给 D

同一个运行目录中应新增：

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

确认每个月 ETF 权重加现金等于 1；单只 ETF 权重只可能是 0 或 0.2；入选数量不超过 5；交易成本不为负；三种组合使用相同测试月份；所有文件属于同一个 run ID。

把 run ID、完整 artifact 路径和 `metrics.csv` 交给 D，并说明两条命令是否成功、是否修改过交易代码。你的工作到最终测试文件和图表结束。

## C 阶段更新

等权基准每月再平衡并扣除相同的 10 bp 单边成本；SPY 只扣初始买入成本。
缺失或日期不匹配的基准收益会报错。最大回撤包括初始财富 1。
B 的文件保持不变，C 另存阶段元数据。最终交接文档为
[MEMBER_C_HANDOFF.md](extra_docs/MEMBER_C_HANDOFF.md)。
