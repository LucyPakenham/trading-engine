import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# --- Download Data ---
ticker = "AAPL"
raw = yf.download(ticker, period="2y")
data = raw["Close"].squeeze()
data = pd.DataFrame(data)
data.columns = ["Close"]

# --- Moving Averages + Signals ---
data["MA50"] = data["Close"].rolling(window=50).mean()
data["MA200"] = data["Close"].rolling(window=200).mean()
data["RawSignal"] = 0
data.loc[data["MA50"] > data["MA200"], "RawSignal"] = 1
data.loc[data["MA50"] < data["MA200"], "RawSignal"] = -1
data["Signal"] = data["RawSignal"].diff().fillna(0)
data["Position"] = 0
data.loc[data["Signal"] > 0, "Position"] = 1
data.loc[data["Signal"] < 0, "Position"] = -1
data = data.dropna()

# --- Simulate Portfolio ---
initial_capital = 10000
cash = initial_capital
shares = 0
portfolio_value = []

for i, row in data.iterrows():
    if row["Position"] == 1 and cash > 0:
        shares = (cash * 0.999) / row["Close"]
        cash = 0
    elif row["Position"] == -1 and shares > 0:
        cash = shares * row["Close"] * 0.999
        shares = 0
    portfolio_value.append(cash + shares * row["Close"])

data["Portfolio"] = portfolio_value
data["BuyHold"] = initial_capital * (data["Close"] / data["Close"].iloc[0])

# --- Daily Returns ---
data["StrategyReturns"] = data["Portfolio"].pct_change().dropna()
data["BuyHoldReturns"] = data["BuyHold"].pct_change().dropna()


# --- Sharpe Ratio ---
def sharpe_ratio(returns, risk_free_rate=0.05):
    excess_returns = returns - risk_free_rate / 252
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()


strategy_sharpe = sharpe_ratio(data["StrategyReturns"].dropna())
buyhold_sharpe = sharpe_ratio(data["BuyHoldReturns"].dropna())


# --- Max Drawdown ---
def max_drawdown(portfolio):
    peak = portfolio.cummax()
    drawdown = (portfolio - peak) / peak
    return drawdown.min()


strategy_mdd = max_drawdown(data["Portfolio"])
buyhold_mdd = max_drawdown(data["BuyHold"])


# --- Value at Risk (Historical) ---
def var_historical(returns, confidence=0.95):
    return np.percentile(returns.dropna(), (1 - confidence) * 100)


strategy_var = var_historical(data["StrategyReturns"])
buyhold_var = var_historical(data["BuyHoldReturns"])


# --- Value at Risk (Monte Carlo) ---
def var_monte_carlo(returns, confidence=0.95, simulations=10000):
    mu = returns.mean()
    sigma = returns.std()
    simulated = np.random.normal(mu, sigma, simulations)
    return np.percentile(simulated, (1 - confidence) * 100)


strategy_var_mc = var_monte_carlo(data["StrategyReturns"].dropna())
buyhold_var_mc = var_monte_carlo(data["BuyHoldReturns"].dropna())

# --- Print Results ---
print("=" * 50)
print(f"{'Metric':<25} {'Strategy':>10} {'Buy & Hold':>10}")
print("=" * 50)
print(f"{'Sharpe Ratio':<25} {strategy_sharpe:>10.3f} {buyhold_sharpe:>10.3f}")
print(f"{'Max Drawdown':<25} {strategy_mdd:>10.2%} {buyhold_mdd:>10.2%}")
print(f"{'VaR 95% (Historical)':<25} {strategy_var:>10.2%} {buyhold_var:>10.2%}")
print(f"{'VaR 95% (Monte Carlo)':<25} {strategy_var_mc:>10.2%} {buyhold_var_mc:>10.2%}")
print("=" * 50)

# --- Plot Drawdown ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Equity curve
ax1.plot(data.index, data["Portfolio"], label="Strategy", color="steelblue")
ax1.plot(
    data.index, data["BuyHold"], label="Buy & Hold", color="orange", linestyle="--"
)
ax1.set_title("Equity Curve")
ax1.set_ylabel("Portfolio Value (USD)")
ax1.legend()

# Drawdown
strategy_dd = (data["Portfolio"] - data["Portfolio"].cummax()) / data[
    "Portfolio"
].cummax()
buyhold_dd = (data["BuyHold"] - data["BuyHold"].cummax()) / data["BuyHold"].cummax()
ax2.fill_between(
    data.index, strategy_dd, 0, alpha=0.4, color="steelblue", label="Strategy Drawdown"
)
ax2.fill_between(
    data.index, buyhold_dd, 0, alpha=0.4, color="orange", label="Buy & Hold Drawdown"
)
ax2.set_title("Drawdown")
ax2.set_ylabel("Drawdown %")
ax2.legend()

plt.tight_layout()
plt.savefig(r"C:\Users\Lucy\Desktop\trading-engine\week6_risk.png")
print("Chart saved!")
