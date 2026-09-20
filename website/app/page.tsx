const sectors = [
  {
    number: "01",
    name: "Technology",
    thesis: "Growth, platforms, and accelerated computing",
    tickers: ["AAPL", "MSFT", "NVDA", "GOOGL", "META"],
  },
  {
    number: "02",
    name: "Financials",
    thesis: "Credit, capital markets, and payment networks",
    tickers: ["JPM", "GS", "BAC", "V", "MA"],
  },
  {
    number: "03",
    name: "Consumer",
    thesis: "Retail, staples, brands, and household demand",
    tickers: ["COST", "WMT", "PG", "KO", "NKE"],
  },
];

const strategies = [
  {
    name: "Equal weight",
    label: "Baseline",
    returnValue: "24.69%",
    volatility: "14.95%",
    sharpe: "1.397",
    drawdown: "−20.13%",
    width: "66%",
  },
  {
    name: "Minimum volatility",
    label: "Defensive",
    returnValue: "19.54%",
    volatility: "11.90%",
    sharpe: "1.323",
    drawdown: "−13.72%",
    width: "53%",
  },
  {
    name: "Maximum Sharpe",
    label: "Return-seeking",
    returnValue: "34.53%",
    volatility: "18.27%",
    sharpe: "1.682",
    drawdown: "−22.35%",
    width: "93%",
  },
];

const maxSharpeWeights = [
  ["NVDA", 25.0],
  ["KO", 25.0],
  ["WMT", 20.0],
  ["JPM", 15.63],
  ["GOOGL", 8.82],
  ["META", 5.55],
] as const;

const workflow = [
  ["01", "Acquire", "Pull daily prices through interchangeable provider adapters."],
  ["02", "Validate", "Standardize the schema, flag gaps, and record a SHA-256 manifest."],
  ["03", "Model", "Estimate returns and shrink covariance before applying constraints."],
  ["04", "Test", "Run rolling out-of-sample backtests with costs and rebalancing."],
] as const;

export default function Home() {
  return (
    <main>
      <header className="site-header shell">
        <a className="brand" href="#top" aria-label="Market Portfolio Lab home">
          <span className="brand-mark" aria-hidden="true">MP</span>
          <span>Market Portfolio Lab</span>
        </a>
        <nav aria-label="Primary navigation">
          <a href="#universe">Universe</a>
          <a href="#results">Results</a>
          <a href="#method">Method</a>
          <a href="#daily">Daily log</a>
        </nav>
        <a className="github-link" href="https://github.com/qwcqwc12138-byte/qwcqwc" target="_blank" rel="noreferrer">
          View GitHub <span aria-hidden="true">↗</span>
        </a>
      </header>

      <section className="hero shell" id="top">
        <div className="eyebrow"><span className="status-dot" /> Completed research window · Aug 15–Sep 14, 2026</div>
        <div className="hero-grid">
          <div className="hero-copy">
            <p className="kicker">Python market research / v0.2</p>
            <h1>Evidence over<br /><em>excitement.</em></h1>
            <p className="hero-lede">
              A reproducible stock-market laboratory that turns multi-source price data into
              constrained portfolios, out-of-sample tests, and conclusions you can audit.
            </p>
            <div className="hero-actions">
              <a className="button button-primary" href="#results">Explore the findings</a>
              <a className="button button-quiet" href="#method">Read the methodology <span aria-hidden="true">↓</span></a>
            </div>
          </div>

          <aside className="snapshot" aria-label="Research snapshot">
            <div className="snapshot-head">
              <span>Research snapshot</span>
              <span className="snapshot-date">14 SEP 2026</span>
            </div>
            <div className="snapshot-hero-stat">
              <span className="metric-label">Verified price records</span>
              <strong>13,905</strong>
              <span className="metric-note">927 trading days × 15 stocks</span>
            </div>
            <div className="mini-metrics">
              <div><span>Coverage</span><strong>100%</strong></div>
              <div><span>Duplicate keys</span><strong>0</strong></div>
              <div><span>Missing closes</span><strong>0</strong></div>
            </div>
            <div className="signal-lines" aria-hidden="true">
              {[38, 53, 45, 67, 61, 82, 70, 88, 76, 91, 86, 98].map((height, index) => (
                <span key={index} style={{ height: `${height}%` }} />
              ))}
            </div>
            <div className="snapshot-foot"><span>2023-01-03</span><span>2026-09-14</span></div>
          </aside>
        </div>
      </section>

      <div className="ticker-rail" aria-label="Stock universe ticker symbols">
        <div className="ticker-track shell">
          {sectors.flatMap((sector) => sector.tickers).map((ticker, index) => (
            <span key={ticker}><i>{String(index + 1).padStart(2, "0")}</i>{ticker}</span>
          ))}
        </div>
      </div>

      <section className="section shell intro" id="method">
        <div className="section-label">01 / Research system</div>
        <div className="section-heading-grid">
          <h2>One pipeline.<br />Every assumption visible.</h2>
          <p>
            The project separates data collection from research logic. Yahoo Finance, Alpha
            Vantage, and Nasdaq Data Link all resolve to the same long-form market schema before
            any statistic is calculated. An independent 300-row spot check matched AAPL, JPM,
            and COST across Alpha Vantage and Yahoo Finance; 1,198 of 1,200 OHLC values were
            within 0.01%.
          </p>
        </div>
        <div className="workflow-grid">
          {workflow.map(([number, title, copy]) => (
            <article className="workflow-card" key={title}>
              <span>{number}</span>
              <h3>{title}</h3>
              <p>{copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section universe-section" id="universe">
        <div className="shell">
          <div className="section-label light">02 / Research universe</div>
          <div className="section-heading-grid light-heading">
            <h2>Fifteen companies.<br />Three economic lenses.</h2>
            <p>
              A deliberately compact US equity universe makes every allocation interpretable.
              Sector caps prevent the optimizer from turning one historical pattern into the
              entire thesis.
            </p>
          </div>
          <div className="sector-grid">
            {sectors.map((sector) => (
              <article className="sector-card" key={sector.name}>
                <span className="sector-number">{sector.number}</span>
                <h3>{sector.name}</h3>
                <p>{sector.thesis}</p>
                <div className="ticker-list">
                  {sector.tickers.map((ticker) => <span key={ticker}>{ticker}</span>)}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section shell results-section" id="results">
        <div className="section-label">03 / Out-of-sample results</div>
        <div className="section-heading-grid">
          <h2>Risk changed with<br />the objective.</h2>
          <p>
            Rolling tests span January 4, 2024 through September 14, 2026. Each rebalance uses only
            information available at that date, then applies the target portfolio to the next
            holding period.
          </p>
        </div>

        <div className="result-table" role="table" aria-label="Strategy performance comparison">
          <div className="result-row result-header" role="row">
            <span role="columnheader">Strategy</span><span role="columnheader">Annual return</span>
            <span role="columnheader">Volatility</span><span role="columnheader">Sharpe</span>
            <span role="columnheader">Max drawdown</span>
          </div>
          {strategies.map((strategy) => (
            <div className="result-row" role="row" key={strategy.name}>
              <div role="cell"><strong>{strategy.name}</strong><small>{strategy.label}</small></div>
              <div role="cell"><strong>{strategy.returnValue}</strong><span className="result-bar"><i style={{ width: strategy.width }} /></span></div>
              <strong role="cell">{strategy.volatility}</strong>
              <strong role="cell">{strategy.sharpe}</strong>
              <strong className="negative" role="cell">{strategy.drawdown}</strong>
            </div>
          ))}
        </div>
        <p className="result-note">
          Historical results after a 10 bps trading-cost assumption. They are not forecasts,
          expected returns, or a promise of future performance.
        </p>

        <div className="finding-grid">
          <article className="finding-copy">
            <span className="mini-label">Maximum Sharpe / full-sample estimate</span>
            <h3>A concentrated answer—with explicit boundaries.</h3>
            <p>
              The optimizer reached both the 25% single-stock cap and the 45% sector cap. That is
              useful evidence: the constraints are actively controlling concentration, not merely
              decorating the model.
            </p>
            <div className="constraint-row"><span>Single stock cap</span><strong>25%</strong></div>
            <div className="constraint-row"><span>Single sector cap</span><strong>45%</strong></div>
            <div className="constraint-row"><span>Position direction</span><strong>Long only</strong></div>
          </article>
          <div className="weights-card" aria-label="Maximum Sharpe portfolio weights">
            <div className="weights-title"><span>Allocation</span><span>Weight</span></div>
            {maxSharpeWeights.map(([ticker, weight]) => (
              <div className="weight-row" key={ticker}>
                <strong>{ticker}</strong>
                <span className="weight-track"><i style={{ width: `${weight * 4}%` }} /></span>
                <b>{weight.toFixed(2)}%</b>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section daily-section" id="daily">
        <div className="shell daily-grid">
          <div>
            <div className="section-label light">04 / One-month research window</div>
            <h2>Fresh data.<br /><em>Same discipline.</em></h2>
            <p className="daily-lede">
              The completed daily sequence refreshed prices, validated the panel, reran the study,
              and compared every result with the previous successful run. Weekend packages retained
              the most recent market session while preserving the same audit trail.
            </p>
            <div className="schedule-pill"><span className="status-dot" /> 31 complete · Project closed</div>
          </div>
          <div className="run-card">
            <div className="run-card-head"><span>DAILY_RUN.yaml</span><span>COMPLETE</span></div>
            {[
              ["18:00", "Refresh market data"],
              ["18:04", "Validate schema + coverage"],
              ["18:06", "Optimize + backtest"],
              ["18:10", "Compare + publish summary"],
            ].map(([time, task]) => (
              <div className="run-step" key={task}>
                <span>{time}</span><i className="active-step" /><strong>{task}</strong>
              </div>
            ))}
            <div className="run-window"><span>START</span><strong>15 AUG 2026</strong><span>END</span><strong>14 SEP 2026</strong></div>
          </div>
        </div>
      </section>

      <section className="section shell principles">
        <div className="section-label">05 / Guardrails</div>
        <div className="principles-grid">
          <h2>The model is useful<br />because its limits<br />are documented.</h2>
          <div className="principle-list">
            <details open>
              <summary>Estimation risk <span>01</span></summary>
              <p>Historical mean returns are noisy. Maximum-Sharpe allocations are especially sensitive to the lookback window and end date.</p>
            </details>
            <details>
              <summary>Universe bias <span>02</span></summary>
              <p>The current-company universe does not include delisted firms and therefore contains survivorship bias.</p>
            </details>
            <details>
              <summary>Execution realism <span>03</span></summary>
              <p>The backtest includes trading costs but not bid–ask spread, taxes, market impact, capacity limits, or fractional-share constraints.</p>
            </details>
            <details>
              <summary>Data licensing <span>04</span></summary>
              <p>The AAPL, JPM, and COST spot check supports recent unadjusted prices. Provider terms, rate limits, entitlements, and independent verification of adjusted prices and corporate actions still apply.</p>
            </details>
          </div>
        </div>
      </section>

      <footer>
        <div className="shell footer-grid">
          <div>
            <span className="brand footer-brand"><span className="brand-mark">MP</span>Market Portfolio Lab</span>
            <p>Reproducible market research in Python.</p>
          </div>
          <div><span>DATA</span><p>Yahoo Finance<br />Alpha Vantage<br />Nasdaq Data Link</p></div>
          <div><span>METHODS</span><p>Ledoit–Wolf shrinkage<br />Constrained optimization<br />Rolling backtests</p></div>
          <div><span>NOTICE</span><p>Research and educational use only. This website does not provide investment advice.</p></div>
        </div>
        <div className="shell footer-bottom"><span>© 2026 Market Portfolio Lab</span><span>Built for auditability, not prediction.</span></div>
      </footer>
    </main>
  );
}
