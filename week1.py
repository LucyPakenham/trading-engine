import yfinance as yf
import matplotlib.pyplot as plt

# Download 1 year of Apple stock data
ticker = "AAPL"
data = yf.download(ticker, period="1y")

# Print the first few rows
print(data.head())

# Plot the closing price
plt.figure(figsize=(12, 5))
plt.plot(data["Close"], label="AAPL Close Price", color="steelblue")
plt.title("Apple (AAPL) — Closing Price (Last 1 Year)")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.tight_layout()
plt.savefig(r"C:\Users\Lucy\Desktop\trading-engine\week1_chart.png")
plt.show()
print("Chart saved as week1_chart.png")
