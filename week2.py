import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# Download 1 year of data for 5 stocks
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
data = yf.download(tickers, period="1y")["Close"]

# Print first few rows
print(data.head())

# --- Daily Returns ---
returns = data.pct_change().dropna()
print("\nDaily Returns (first 5 rows):")
print(returns.head())

# --- Summary Statistics ---
print("\nSummary Statistics:")
print(returns.describe())

# --- Plot 1: Closing Prices ---
plt.figure(figsize=(12, 5))
for ticker in tickers:
    plt.plot(data[ticker], label=ticker)
plt.title("Closing Prices — Last 1 Year")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.tight_layout()
plt.savefig(r"C:\Users\Lucy\Desktop\trading-engine\week2_prices.png")

# --- Plot 2: Cumulative Returns ---
cumulative = (1 + returns).cumprod()
plt.figure(figsize=(12, 5))
for ticker in tickers:
    plt.plot(cumulative[ticker], label=ticker)
plt.title("Cumulative Returns — Last 1 Year")
plt.xlabel("Date")
plt.ylabel("Growth of $1")
plt.legend()
plt.tight_layout()
plt.savefig(r"C:\Users\Lucy\Desktop\trading-engine\week2_cumulative.png")

print("\nCharts saved!")
