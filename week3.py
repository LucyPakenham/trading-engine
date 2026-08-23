import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# Download 2 years of Apple data
ticker = "AAPL"
raw = yf.download(ticker, period="2y")
data = raw["Close"].squeeze()
data = pd.DataFrame(data)
data.columns = ["Close"]

# --- Calculate Moving Averages ---
data["MA50"] = data["Close"].rolling(window=50).mean()
data["MA200"] = data["Close"].rolling(window=200).mean()

# --- Generate Buy/Sell Signals ---
data["Signal"] = 0
data.loc[data["MA50"] > data["MA200"], "Signal"] = 1
data.loc[data["MA50"] < data["MA200"], "Signal"] = -1

print(data.tail(10))

# --- Plot ---
plt.figure(figsize=(14, 6))
plt.plot(data["Close"], label="AAPL Close", color="steelblue", alpha=0.7)
plt.plot(data["MA50"], label="50-day MA", color="orange")
plt.plot(data["MA200"], label="200-day MA", color="red")

buy_signals = data[data["Signal"] == 1]
plt.scatter(
    buy_signals.index,
    buy_signals["Close"],
    marker="^",
    color="green",
    label="Buy Signal",
    alpha=0.7,
    zorder=5,
)

sell_signals = data[data["Signal"] == -1]
plt.scatter(
    sell_signals.index,
    sell_signals["Close"],
    marker="v",
    color="red",
    label="Sell Signal",
    alpha=0.7,
    zorder=5,
)

plt.title("AAPL — Moving Average Crossover Strategy")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.tight_layout()
plt.savefig(r"C:\Users\Lucy\Desktop\trading-engine\week3_strategy.png")
print("Chart saved!")
