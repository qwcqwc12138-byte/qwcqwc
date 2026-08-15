# 基于 Python 的股票市场数据分析与投资组合优化

这是一个教学型量化研究项目，已经打通 **数据获取 → 数据质量 → 探索性分析 → 约束优化 → 样本外回测 → 研究报告** 的完整流程。Yahoo Finance、Alpha Vantage 和 Nasdaq Data Link 行情会先转换为同一套长表格式，再进入经过测试的分析代码。

> 本项目仅用于研究和教学，不构成投资建议。市场数据受各数据供应商的许可、频率限制和使用条款约束。

## 股票池（15 家）

| 行业 | 公司与代码 |
| --- | --- |
| 科技 | Apple (`AAPL`)、Microsoft (`MSFT`)、Nvidia (`NVDA`)、Alphabet (`GOOGL`)、Meta (`META`) |
| 金融 | JPMorgan (`JPM`)、Goldman Sachs (`GS`)、Bank of America (`BAC`)、Visa (`V`)、Mastercard (`MA`) |
| 消费 | Costco (`COST`)、Walmart (`WMT`)、Procter & Gamble (`PG`)、Coca-Cola (`KO`)、Nike (`NKE`) |

股票池由 [`config/universe.yaml`](config/universe.yaml) 管理，后续不需要改代码就能替换股票。

## 快速开始

要求 Python 3.11 或更高版本。在 PowerShell 中运行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

如需在本机启动 JupyterLab，再安装 Notebook 可选依赖：

```powershell
python -m pip install -e ".[dev,notebook]"
```

Yahoo Finance 不需要 API key，可先用它验证完整流程：

```powershell
market-data list-universe
market-data fetch --source yahoo --start 2023-01-01 --end 2026-08-14
market-data validate data/processed/yahoo/prices_2023-01-01_2026-08-14.csv
market-data run-all data/processed/yahoo/prices_2023-01-01_2026-08-14.csv --output-dir artifacts
```

也可以不使用已安装的命令：

```powershell
python -m market_portfolio fetch --source yahoo --start 2023-01-01 --end 2026-08-14
```

输出包括：

- 统一格式的 CSV：`data/processed/<source>/prices_<start>_<end>.csv`
- 可追溯的 JSON 清单：记录数据源、股票、时间区间、行数和文件 SHA-256
- EDA：资产指标、相关矩阵、归一化价格、收益分布、滚动波动率
- 优化：等权、最小波动、最大 Sharpe 的权重、行业暴露和敏感性结果
- 回测：样本外收益、净值、换手率、权重历史、风险指标和净值图

生成文件位于 `artifacts/`，该目录被 Git 忽略。可复现 Notebook 位于 [`notebooks/01_full_research.ipynb`](notebooks/01_full_research.ipynb)，已完成的数值结论位于 [`reports/final_report.md`](reports/final_report.md)。

## 方法与历史结果

默认研究设置为：复权收盘价、252 日训练窗、每 21 个交易日再平衡、10 bps 交易成本、long-only、单股最高 25%、单行业最高 45%。协方差矩阵使用 Ledoit–Wolf 收缩；无风险利率使用美国财政部 2026-08-14 的 13 周国库券 coupon-equivalent 3.80%。

2024-01-04 至 2026-08-14 的滚动样本外结果：

| 方法 | 年化收益 | 年化波动 | Sharpe | 最大回撤 |
| --- | ---: | ---: | ---: | ---: |
| 等权 | 25.77% | 15.03% | 1.46 | -20.13% |
| 最小波动 | 20.67% | 11.93% | 1.41 | -13.72% |
| 最大 Sharpe | 36.25% | 18.40% | 1.76 | -22.35% |

这些是特定历史样本和模型假设下的结果，不是预期回报或未来表现承诺。尤其是最大 Sharpe 对预期收益估计、窗口和交易成本非常敏感。

## API key 与数据源差异

在 `.env` 中设置 key；该文件已被 Git 忽略。

```dotenv
ALPHA_VANTAGE_API_KEY=your_key
NASDAQ_DATA_LINK_API_KEY=your_key
```

然后运行：

```powershell
market-data fetch --source alpha-vantage --start 2026-05-01 --end 2026-08-14
market-data fetch --source nasdaq-data-link --start 2023-01-01 --end 2026-08-14
```

- **Yahoo Finance**：本项目使用开源 `yfinance`。它不是 Yahoo 官方 SDK，适合研究和教学；请自行确认数据使用条款。
- **Alpha Vantage**：逐代码调用日线端点。免费套餐有调用频率和历史深度限制；默认每次请求间隔可在配置中调整。
- **Nasdaq Data Link**：默认读取 `SHARADAR/SEP` 表。它通常需要相应订阅；拥有其他表权限时可修改配置中的 `table_code`。Nasdaq Data Link 是平台，并不保证 API key 自动包含全部美股历史行情。

## 统一数据格式

每一行是一只股票在一个交易日的记录：

`date, ticker, open, high, low, close, adjusted_close, volume, dividend, stock_split, source`

日期、代码和收盘价不能为空；重复的 `date + ticker + source` 会被去重；价格、成交量等字段会转换为数值。调整收盘价不可用时暂以普通收盘价填充，并保留具体数据源名称。

## 开发与测试

```powershell
pytest
ruff check .
```

单元测试不访问互联网，也不消耗 API 配额。GitHub Actions 会在每次 push 和 pull request 时运行相同检查。

## 开源项目借鉴

- [yfinance](https://github.com/ranaroussi/yfinance)：Yahoo Finance 数据访问
- [Alpha Vantage Python wrapper](https://github.com/RomelTorres/alpha_vantage)：API 使用方式参考；当前实现直接调用官方 HTTP 端点，以便显式处理限流和错误信息
- [Nasdaq Data Link Python](https://github.com/Nasdaq/data-link-python)：官方 Python 客户端
- [PyPortfolioOpt](https://github.com/PyPortfolio/PyPortfolioOpt)：约束优化、协方差收缩和组合绩效计算

详细的一月计划和每周验收标准见 [`ROADMAP.md`](ROADMAP.md)。
