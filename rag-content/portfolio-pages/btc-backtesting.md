## The Problem

Most crypto backtesting is cargo cult engineering: download historical data, run a strategy, see a big number, declare success. The results look convincing but collapse in live trading because they're overfit, statistically insignificant, or only work in one market regime.

I wanted a backtesting system that would be honest with me — one that doesn't just tell me "this strategy returned 47%" but tells me "this result is statistically significant at the 95% confidence level, stable across parameter variations, and performs consistently in both trending and ranging markets."

## My Role

Solo project. Designed and built the full pipeline: data ingestion, indicator calculation, signal detection, strategy framework, backtesting engine, statistical validation, and report generation.

## The Approach

Five architectural layers, each with a clear boundary:

**Layer 1 — Data:** Downloads market data from Binance across multiple timeframes, stores in SQLite (~2GB), handles gaps and timezone normalization.

**Layer 2 — Indicators:** Calculates technical indicators (RSI, MACD, Bollinger Bands, moving averages, etc.) with configurable parameters. Each indicator is a pure function — same inputs always produce same outputs.

**Layer 3 — Signals:** Detects trading signals from indicator combinations. Plugin architecture with a `BaseStrategy` abstract interface — new strategies slot in without touching the engine.

**Layer 4 — Backtesting:** Simulates strategy execution with realistic assumptions (slippage, fees, position sizing). Walk-forward testing splits data into training and testing windows that slide forward through time — the strategy is always tested on data it hasn't seen.

**Layer 5 — Validation:** This is where it gets interesting.

## The Validation Layer

The `StatisticalValidator` runs 5 significance tests on every backtest:

- **t-test** — Are returns significantly different from zero?
  - **Sharpe ratio confidence interval** — Is the risk-adjusted return real or noise?
  - **Maximum drawdown test** — Is the worst case survivable?
  - **Win rate binomial test** — Is the win rate significantly better than chance?
  - **Profit factor test** — Is gross profit reliably greater than gross loss?
The `SampleSizeValidator` flags low trade counts with severity levels — a strategy that only triggers 12 trades in a year might look great but means nothing statistically.

**Walk-forward overfitting detection:** The system compares parameter performance in training windows vs. testing windows. If a parameter set works great in training but poorly in testing, it's overfit. The coefficient of variation across walk-forward windows measures parameter stability — high variance means the strategy is fragile.

**Regime-aware evaluation:** The `RegimeClassifier` categorizes each period as trending, ranging, or volatile, then reports strategy performance broken down by regime. A strategy that only works in trending markets is useful — but only if you know that's the limitation.

**Assumptions transparency:** `BacktestAssumptions` logs every parameter that affects results — slippage model, fee structure, position sizing rules, data source — so you know exactly what you're measuring.

## What I Built

- **Data pipeline** — Binance API → SQLite, multi-timeframe, gap handling
  - **Plugin strategy framework** — BaseStrategy abstract interface, CLI-driven configuration
  - **Walk-forward backtesting engine** — sliding train/test windows, realistic execution simulation
  - **StatisticalValidator** — 5 significance tests per backtest, automatic pass/fail
  - **SampleSizeValidator** — trade count thresholds with severity classification
  - **RegimeClassifier** — market condition detection and per-regime performance breakdown
  - **HTML report generator** — visual equity curves, drawdown charts, regime overlays
## The Result

A backtesting system I actually trust. When it tells me a strategy works, I know it's been tested on unseen data, validated for statistical significance, checked for overfitting, and broken down by market regime. When it tells me a strategy doesn't work, I know why — and I can trace the failure to specific market conditions.

The pattern — build a pipeline, then build the validation layer that tells you whether to trust the pipeline's output — maps directly to how AI eval systems work. The backtesting engine IS an eval pipeline, just for trading strategies instead of language models.

## Tech Stack

- **Language:** Python
  - **Data:** pandas, SQLite (~2GB), Binance API
  - **Statistics:** scipy (t-tests, binomial), numpy
  - **Visualization:** Plotly (interactive HTML reports)
  - **Architecture:** Plugin-based strategy framework, CLI orchestration