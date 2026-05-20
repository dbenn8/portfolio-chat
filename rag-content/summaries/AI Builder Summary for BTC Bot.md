# AI Builder Summary for BTC Bot

## Part 1: Job Fit

### What This Project Demonstrates

BTC Bot is a solo-built, end-to-end data pipeline and backtesting framework for Bitcoin/crypto trading analysis. It covers the full lifecycle: data ingestion from Binance, indicator calculation, signal detection, strategy execution, and rigorous backtesting with statistical validation. The codebase spans ~3,100 Python files across a modular architecture with 8 strategies, a walk-forward optimization engine, a statistical validation suite, and a market regime classifier.

### AI Building / Super Agent Alignment

**System design and data pipeline architecture.** The core pipeline moves data through five stages: download (Binance Data Vision CSVs + REST API) -> validate (gap detection, timestamp format auto-detection for ms vs us) -> store (SQLite with SQLAlchemy ORM, designed for zero-change PostgreSQL migration) -> compute (15+ technical indicators via the `ta` library) -> act (signal detection, strategy execution, report generation). Each stage is a standalone module with clear interfaces, the same pattern n8n workflows follow: discrete nodes connected by well-defined data contracts.

**Multi-strategy framework with plugin architecture.** `BaseStrategy` defines an abstract interface (`generate_signal()` receives candle + indicators, returns a typed `Signal` with entry/exit/hold/reduce actions, confidence scores, and metadata). Eight concrete strategies implement this interface, from `SimpleRSIStrategy` (40 lines, good for testing) to `MACDRSIStrategy` (290 lines, with trailing ATR stops and MACD crossover history tracking). Adding a new strategy means implementing one method. This is the same composable-node thinking that makes n8n powerful: standardized interfaces, pluggable implementations.

**Automation of complex multi-step workflows.** The CLI (`main.py`) orchestrates download -> calculate -> detect -> report in a single command with flags. Multi-symbol support (BTCUSDT + ETHUSDT) runs in sequence automatically. Range downloads iterate month-by-month with error handling per month so failures don't break the full run. The signal detection pipeline runs 8 independent detector functions, collects results, sorts by timestamp, and persists to database. This is workflow orchestration -- the same discipline needed to build and debug n8n automation flows.

**Builder velocity.** This is a solo project built from scratch: database schema, data loaders, indicator calculators, 8 trading strategies, a full backtesting engine with portfolio management, walk-forward optimization, statistical validation, market regime classification, signal detection across 8 signal categories, HTML report generation with interactive charts, a Slack bot integration, and comprehensive documentation. The breadth-to-person ratio demonstrates the kind of fast, autonomous building the AI Product Builder role requires.

### AI Trust / Evals / Reliability Alignment

**Backtesting as an eval framework.** The backtesting system is structurally identical to an AI eval pipeline. The `BacktestEngine` runs a strategy against historical data (analogous to running an AI agent against test cases), the `PerformanceMetrics` class computes standardized scores (Sharpe ratio, win rate, max drawdown -- analogous to accuracy, precision, recall), and the `WalkForwardEngine` ensures out-of-sample validation by splitting data into train/test windows that roll forward through time. This is the "measure before you trust" discipline that n8n's AI Trust workstream demands.

**Statistical rigor to prevent false confidence.** The `StatisticalValidator` class runs five significance tests on every backtest result: t-test on returns, bootstrap Sharpe ratio confidence intervals, Shapiro-Wilk normality testing, binomial consistency testing across walk-forward windows, and paired strategy comparison. The `SampleSizeValidator` flags results with fewer than 30 trades as "CRITICAL" and fewer than 100 as "WARNING," with color-coded HTML banners in reports. This is the same mindset needed for AI trust: never ship a metric without understanding its confidence interval.

**Overfitting detection built into the framework.** The walk-forward analysis summary explicitly prints "Train vs Test (Overfitting Check)" comparing in-sample and out-of-sample performance. The `WalkForwardAnalyzer` computes parameter stability via coefficient of variation -- if optimal RSI thresholds swing wildly across windows, the system flags them as "Unstable." The `RegimeClassifier` breaks performance down by bull/bear/sideways markets with high/normal/low volatility overlays, so you can see where a strategy actually works versus where it was lucky. This maps directly to AI model evaluation: understanding when your system works, when it fails, and whether it's overfitting to training distribution.

**Assumptions transparency and reproducibility.** The `BacktestAssumptions` dataclass documents every parameter that affects results: trading fees, slippage, execution model, fill assumptions, position sizing, compounding behavior. Reports include a full "Assumptions & Methodology" section with disclaimers about execution reality gaps. This is the same transparency needed for AI system evaluation: documenting what was tested, what was assumed, and what could differ in production.

---

## Part 2: Case Study Draft

### BTC Bot: A Data Pipeline and Backtesting Framework for Crypto Trading Analysis

**The problem.** Evaluating a trading strategy requires the same rigor as evaluating an AI model: you need clean data, a reproducible test harness, out-of-sample validation, statistical significance testing, and clear reporting of assumptions and limitations. Most retail trading tools skip these steps, leading to strategies that look great on historical data but fail in production -- the exact same overfitting problem that plagues AI systems.

**What I built.** A modular Python framework with five layers:

1. **Data layer.** Ingests OHLCV candlestick data from Binance (both historical CSV archives and live REST API), handles timestamp format changes (Binance switched from milliseconds to microseconds in 2025), validates data quality (gap detection, zero-volume checks, OHLC relationship validation), and stores in SQLite with SQLAlchemy ORM designed for zero-change PostgreSQL migration. The database holds ~2 GB of multi-interval, multi-symbol data.

2. **Indicator layer.** Calculates 15+ technical indicators (RSI, MACD, Bollinger Bands, EMAs, ATR, Stochastic, OBV) using a smart calculation method that only computes missing indicators, not the full dataset. Handles NaN values for warm-up periods (first 200 candles for SMA-200) with proper NULL handling in the database.

3. **Signal detection layer.** Eight independent detectors (RSI, MACD, MA crossovers, Bollinger Bands, Stochastic, volume spikes, volatility changes, momentum) scan historical data and persist signals to the database with type, category, direction, strength (1-10 scale), and metadata. Signals are queryable by type, date range, and minimum strength.

4. **Strategy and backtesting layer.** An abstract `BaseStrategy` interface that eight concrete strategies implement. The `BacktestEngine` iterates candle-by-candle, passing each to the strategy and executing the resulting signal through a `Portfolio` manager that tracks cash, BTC holdings, trades, and takes snapshots at every timestep. Strategies range from simple (RSI threshold) to complex (MACD+RSI convergence with ATR trailing stops). The `WalkForwardEngine` adds parameter optimization: grid search over parameter combinations on training windows, then test on out-of-sample windows, rolling forward through time.

5. **Validation and reporting layer.** `PerformanceMetrics` computes Sharpe ratio, max drawdown, win rate, annualized returns, and trade statistics. `StatisticalValidator` runs t-tests, bootstrap confidence intervals, normality checks, and binomial consistency tests. `SampleSizeValidator` prevents false confidence from small trade counts. `RegimeClassifier` labels periods as bull/bear/sideways with volatility overlays. `StrategyReportGenerator` produces standalone HTML reports with interactive charts, trade breakdowns, assumptions documentation, and prominently displayed sample size warnings.

**Technical decisions that reflect builder judgment.**

- *Walk-forward over simple train/test split.* A single train/test split tells you how a strategy performed in one specific out-of-sample period. Walk-forward analysis with rolling windows (e.g., 180-day train, 90-day test, 90-day step) tells you how consistently it performs across different market conditions. I built this because consistency matters more than peak performance -- the same principle that makes AI evals valuable: you want to know the distribution of outcomes, not just the best case.

- *Statistical validation as a first-class concern.* Every backtest result passes through significance testing before being trusted. The framework explicitly calculates whether a Sharpe ratio is significantly positive (bootstrap CI lower bound > 0), whether a win rate is significantly better than a coin flip (binomial test), and whether two strategies are significantly different (paired t-test). This prevents the "looks good on the chart" trap that leads to overconfident deployment -- in AI terms, it prevents shipping a model based on a cherry-picked eval set.

- *Parameter stability as an overfitting signal.* The walk-forward analyzer tracks which parameters the optimizer selects across windows. If the optimal RSI oversold threshold is 25 in one window and 35 in another, the coefficient of variation will be high, and the system flags this as "Unstable." Stable parameters across windows suggest a real market pattern; unstable parameters suggest the optimizer is chasing noise. This is the trading equivalent of hyperparameter sensitivity analysis in ML.

- *Regime-aware evaluation.* Strategies that work in bull markets may fail in bear markets. The `RegimeClassifier` automatically labels each test window by market condition (bull/bear/sideways crossed with high/normal/low volatility), enabling performance breakdown by regime. This reveals whether alpha is real or just correlated with market direction -- the same decomposition needed to evaluate whether an AI agent's "intelligence" is genuine or just pattern matching on easy inputs.

**The n8n connection.** This project is a pipeline system: data flows through typed stages, each stage has a clear contract, errors are handled per-stage without breaking the pipeline, and the output is a structured report that enables decisions. The backtesting infrastructure embodies the "measure before you trust" philosophy that n8n's AI Trust workstream requires: never deploy a strategy (or an AI agent) without out-of-sample validation, statistical significance testing, and transparent documentation of assumptions and limitations.
