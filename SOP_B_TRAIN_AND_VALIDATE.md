# 组员 B：模型训练与验证 SOP

## 先了解整个项目

A 已经把日价格整理成月度模型表，并计算了三个特征：一个月相对趋势、六个月相对表现和六个月波动率。你的工作是让 Ridge 回归学习这三个特征与下个月收益之间的关系，并用验证期选择参数 `alpha`。你的输出交给 C；C 不重新训练模型，只把预测转换成持仓并测试。

## 项目已经为你准备了什么

A 会交给你：

```text
data/processed/model_table_us_industry.csv
```

基础代码位于：

```text
src/combined_momentum/split.py
src/combined_momentum/model.py
```

你不需要从零实现 Ridge。你需要读懂时间划分、标准化、alpha 比较和模型保存过程，确认它们与本 SOP 一致，然后运行并检查结果。如果模型阶段有错误，由你修改这两个文件和相关测试；不要手动修改 A 的 CSV，也不要修改 C 的交易规则。

## 训练、验证和测试是什么意思

训练期用于估计模型系数；验证期用于比较不同 alpha；测试期用于最后评估预测和交易结果，由 C 负责。

目前时间范围设计成：

| 部分 | 信号日期 | 用途 |
|---|---|---|
| 训练期 | 截止 2014-12-31 | 拟合候选模型 |
| 验证期 | 2015-01-01 至 2018-12-31 | 比较 alpha |
| 测试期 | 2019-01-01 至 2025-12-31 | B 只生成预测，不分析表现 |

模型只能用较早的数据学习，再预测较晚的数据，所以不能随机打乱时间后重新划分。

## 你要交付什么

模型阶段会创建：

```text
artifacts/<run_id>/
```

`run_id` 是这次运行的名称，用来保证 B、C、D 使用同一套结果。你要把这个名称和运行目录交给 C。

## 第一步：检查 A 的模型表

模型表必须有日期、ticker、`target_return_1m` 和三个模型特征：

```text
rank_current_trend_1m
relative_strength_6m
risk_volatility_6m
```

目前模型输入设计成这三列。确认文件中没有 SPY 和重复行。缺列、日期错误或 ETF 数量不对时，把问题交回 A 重新生成，不要在模型代码中临时补数据。

## 第二步：理解目前使用的模型

目前模型设计成 Ridge 线性回归：

```text
predicted_return
  = intercept
    + beta_1 * rank_current_trend_1m
    + beta_2 * relative_strength_6m
    + beta_3 * risk_volatility_6m
```

Ridge 的计算目标是：

```text
minimise:
  sum[(actual_return - predicted_return)^2]
  + alpha * sum(beta_j^2)
```

alpha 越大，模型越倾向于把系数压小。目前候选值设计成：

```text
0.01, 0.1, 1, 10, 100
```

三个特征的量纲不同，所以模型拟合前使用 `StandardScaler`。每次候选训练的均值和标准差只能从训练期计算。

## 第三步：用验证期选择 alpha

对每个 alpha，代码先在训练期拟合，再为验证期每个月的 20 只 ETF 生成预测。每个月比较预测排名和实际收益排名的 Spearman 相关系数，最后计算所有验证月份的平均值。

目前选择方法设计成平均月度 Spearman IC 最高的 alpha。如果所有 IC 都无法计算，才使用验证 MSE 最低的 alpha。五个候选值的结果都要保存在 `alpha_validation.csv`。

## 第四步：生成 C 需要的预测

选出 alpha 后，代码使用训练期加验证期重新拟合标准化器和 Ridge，然后为 train、validation 和 test 行生成 `predicted_return` 并写入 `predictions.csv`。

B 为测试行生成预测，但不计算测试表现。B 阶段只保存训练和验证指标：

```text
validation_prediction_metrics.csv
```

测试指标、持仓和收益由 C 生成。

## 第五步：运行模型阶段

```powershell
python -m pytest
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml --stage model
```

终端会显示 `run_dir`，项目也会把 run ID 写入 `artifacts/LATEST_RUN.txt`。

## 第六步：检查并交给 C

运行目录中应有：

| 文件 | 含义 |
|---|---|
| `model.joblib` | 标准化器和 Ridge 模型 |
| `alpha_validation.csv` | 五个 alpha 的验证结果 |
| `validation_prediction_metrics.csv` | 训练和验证指标 |
| `coefficients.csv` | 三个特征的系数 |
| `predictions.csv` | C 用来生成持仓的预测 |
| `split_summary.csv` | 三个时间段的数据范围和数量 |
| `run_metadata.json` | 配置、文件哈希和运行环境 |

确认 alpha 表有五个候选值，系数表恰好对应三个特征，三个时间段日期正确，测试行使用训练期加验证期拟合的模型。此时不应出现 `positions.csv`、`portfolio_returns.csv`、最终 `prediction_metrics.csv` 或测试图。

把准确的 run ID 和运行目录交给 C，并说明选择了哪个 alpha、验证期 IC 是多少、是否修改过模型代码。你的工作到预测文件结束。不要运行 `backtest` 或 `evaluate`，也不要根据测试结果重新选择 alpha。
