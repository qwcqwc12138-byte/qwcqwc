# 基于 Python 的股票市场数据分析与投资组合优化

这是一个为期一个月、按周交付的教学型量化研究项目。当前版本完成 **Part 1：股票数据获取** 的可运行骨架：从 Yahoo Finance、Alpha Vantage 和 Nasdaq Data Link 获取行情，并转换为同一套长表格式。

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

Yahoo Finance 不需要 API key，可先用它验证完整流程：

```powershell
market-data list-universe
market-data fetch --source yahoo --start 2023-01-01 --end 2026-08-14
market-data validate data/processed/yahoo/prices_2023-01-01_2026-08-14.csv
```

也可以不使用已安装的命令：

```powershell
python -m market_portfolio fetch --source yahoo --start 2023-01-01 --end 2026-08-14
```

输出包括：

- 统一格式的 CSV：`data/processed/<source>/prices_<start>_<end>.csv`
- 可追溯的 JSON 清单：记录数据源、股票、时间区间、行数和文件 SHA-256

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
- [PyPortfolioOpt](https://github.com/PyPortfolio/PyPortfolioOpt)：第 3 周投资组合优化阶段使用

详细的一月计划和每周验收标准见 [`ROADMAP.md`](ROADMAP.md)。

