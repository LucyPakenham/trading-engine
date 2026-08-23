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

# --- Moving Averages ---
data["MA50"] = data["Close"].rolling(window=50).mean()
data["MA200"] = data["Close"].rolling(window=200).mean()

# --- Generate Signals (only on crossover days) ---
data["RawSignal"] = 0
data.loc[data["MA50"] > data["MA200"], "RawSignal"] = 1
data.loc[data["MA50"] < data["MA200"], "RawSignal"] = -1

# Only trade on the day the signal CHANGES (fixes overtrading)
data["Signal"] = data["RawSignal"].diff().fillna(0)
data.loc[data["Signal"] > 0, "Position"] = 1  # Buy
data.loc[data["Signal"] < 0, "Position"] = -1  # Sell
data["Position"] = data["Position"].fillna(0)

# --- Simulate Portfolio ---
TRANSACTION_COST = 0.001  # 0.1% per trade
initial_capital = 10000
cash = initial_capital
shares = 0
portfolio_value = []

for i, row in data.iterrows():
    if row["Position"] == 1 and cash > 0:
        # Buy as many shares as we can afford
        shares = (cash * (1 - TRANSACTION_COST)) / row["Close"]
        cash = 0
    elif row["Position"] == -1 and shares > 0:
        # Sell all shares
        cash = shares * row["Close"] * (1 - TRANSACTION_COST)
        shares = 0
    # Record portfolio value today
    total = cash + shares * row["Close"]
    portfolio_value.append(total)

data["Portfolio"] = portfolio_value

# --- Buy and Hold Benchmark ---
first_price = data["Close"].dropna().iloc[0]
data["BuyHold"] = initial_capital * (data["Close"] / first_price)

# --- Results ---
final_strategy = data["Portfolio"].iloc[-1]
final_buyhold = data["BuyHold"].iloc[-1]
print(f"Starting capital:        ${initial_capital:,.2f}")
print(f"Strategy final value:    ${final_strategy:,.2f}")
print(f"Buy & Hold final value:  ${final_buyhold:,.2f}")
print(f"Strategy return:         {((final_strategy / initial_capital) - 1) * 100:.2f}%")
print(f"Buy & Hold return:       {((final_buyhold / initial_capital) - 1) * 100:.2f}%")

# --- Plot Equity Curve ---
plt.figure(figsize=(14, 6))
plt.plot(
    data.index, data["Portfolio"], label="MA Crossover Strategy", color="steelblue"
)
plt.plot(
    data.index, data["BuyHold"], label="Buy & Hold", color="orange", linestyle="--"
)
plt.title("Strategy vs Buy & Hold — Equity Curve")
plt.xlabel("Date")
plt.ylabel("Portfolio Value (USD)")
plt.legend()
plt.tight_layout()
plt.savefig(r"C:\Users\Lucy\Desktop\trading-engine\week4_backtest.png")
print("Chart saved!")
