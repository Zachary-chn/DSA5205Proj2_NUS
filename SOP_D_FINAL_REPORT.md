# 组员 D：最终报告与视频 SOP

## 先了解整个项目

这个项目研究行业 ETF 轮动。A 准备数据并计算三个特征，B 用 Ridge 预测下一月收益，C 把预测转换成 Top 5 组合并完成最终测试。你的工作是把三个人的方法和同一套结果组织成清楚、完整、可以复现的报告与视频。

D 不负责重新处理数据、训练模型或运行回测。你需要理解这些内容，核对来源，再用普通读者能看懂的方式解释。

## 项目已经为你准备了什么

研究设计和计算方法写在：

```text
README.md
README_CN.md
configs/final_us_industry_project.yaml
extra_docs/FINAL_US_INDUSTRY_UNIVERSE.md
SOP_A_DATA_AND_FEATURES.md
SOP_B_TRAIN_AND_VALIDATE.md
SOP_C_TRADING_AND_TESTING.md
```

C 会给你一个明确的 run ID。最终数字和图表位于：

```text
artifacts/<run_id>/
```

你不需要写 Python 模型代码。你的主要工作文件是报告、视频材料、`extra_docs/FINAL_RESULTS_TEMPLATE.md` 和贡献说明。

## 你要交付什么

目前提交目录设计成：

```text
submission/Group_<number>_Report.pdf
submission/Group_<number>_Video.mp4
submission/Group_<number>_Contribution.md
```

如果课程允许提交视频链接，可以用清楚标注的链接文件替代 MP4。最终文件名、报告页数和视频时长以课程要求为准。

## 第一步：确认收到的是同一次运行

先向 B 和 C 确认 run ID。然后检查目录中至少有：

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

报告数字和图表都要来自这个 run ID，不能把不同运行目录里的结果拼在一起。

## 第二步：填写结果工作表

打开 `extra_docs/FINAL_RESULTS_TEMPLATE.md`，填入 run ID、Git commit、数据下载时间、数据行数和范围、验证期选择的 alpha、三个系数、测试预测指标、扣除成本后的策略指标、两个比较对象的指标，以及报告使用的图表名称。

这份工作表是报告的数字清单。写正文和制作视频时都从这里取数，避免同一指标出现不同版本。

## 第三步：写报告

报告目前设计成下面的顺序。

### 1. 研究问题

说明我们想研究：行业 ETF 最近的趋势、相对表现和风险，能否帮助预测下个月收益；预测能否转化成一个考虑交易成本的月度轮动策略。

### 2. 数据与 ETF 样本

介绍 20 只美国行业 ETF 的宽行业与细分行业安排、样本日期和调整收盘价，并说明 SPY 为什么只作为市场比较对象。说明名单依据行业属性、成立时间和数据完整度确定。

### 3. 时间安排

解释月末收盘后形成信号，下一可用收盘价成交。说明训练期、验证期和测试期分别用于什么，以及为什么不能随机打乱时间顺序。

### 4. 三个特征和预测目标

分别解释一个月相对趋势、六个月相对表现和六个月波动率。正文既要有普通语言，也要给出 README 中的准确公式。预测目标是从本期成交价到下一期成交价的一个月收益。

### 5. Ridge 和验证方法

说明线性预测形式、特征标准化、Ridge 正则化的作用、五个 alpha 候选值，以及为什么用验证期平均月度 Spearman IC 选择 alpha。

### 6. 交易规则和成本

说明只选择预测收益为正的 ETF，最多 5 只，每只 20%，不足 5 只的部分放在现金。写明换手率、10 个基点成本和扣费后收益公式。

### 7. 最终测试结果

先汇报预测指标，再汇报策略、20 只 ETF 等权组合和 SPY 的年化收益、波动率、Sharpe ratio、最大回撤和累计收益。图表至少包括累计净值、回撤、年度收益和预测值与实际收益的关系。

### 8. 模型学到了什么

结合 `coefficients.csv` 解释三个系数的正负和相对大小。这里描述的是数据中的关联，不应写成确定的因果关系。

### 9. 表现好和表现差的时期

使用年度结果和图表说明策略在哪些时期表现较好，在哪些时期表现较差，并结合持仓数量、现金比例、风险和换手率讨论可能原因。

### 10. 局限性与结论

讨论样本规模、ETF 成立时间、交易成本假设、月度调仓、线性模型和市场环境变化。结果不理想时直接报告并解释。

### 11. 可复现性和成员贡献

写明配置文件、run ID、Git commit 和统一运行命令，并说明每位成员负责的部分。

## 第四步：制作表格、图和视频

表格至少包括样本范围、五个 alpha 的验证结果、三个模型系数，以及三种组合的测试指标。自动生成的图位于 `artifacts/<run_id>/figures/`。每个表和图都要标注测试期、是否扣除交易成本以及比较对象名称。

视频沿用报告结构。不要加入另一套临时结果。每位成员可以讲解自己负责的部分，D 负责统一开头、结尾、图表风格和时间安排。

## 第五步：完成一致性检查

D 不重新运行数据、模型或回测。逐项核对报告里的 run ID、测试日期、alpha、系数、指标和图表路径。发现不一致时，把问题交回相应负责人检查，D 不在报告中手动修改自动结果。

报告中的复现命令写成：

```powershell
python -m pytest
python scripts\run_pipeline.py --config configs\final_us_industry_project.yaml
```

最后从 `extra_docs/CONTRIBUTION_NOTE_TEMPLATE.md` 复制贡献说明并补全姓名、负责内容、检查过的文件和视频部分。提交前确认报告和视频引用同一个 run ID，公式与 README 一致，结果包括交易成本、等权组合和 SPY，并且文件名符合课程要求。
