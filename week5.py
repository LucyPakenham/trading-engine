import ctypes
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time

# --- Load the C++ DLL ---
lib = ctypes.CDLL(r"C:\Users\Lucy\Desktop\trading-engine\backtest.dll")

# Tell Python what types the C++ function expects
lib.run_backtest.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # prices
    ctypes.POINTER(ctypes.c_int),  # signals
    ctypes.c_int,  # n (number of days)
    ctypes.POINTER(ctypes.c_double),  # portfolio output
    ctypes.c_double,  # initial capital
    ctypes.c_double,  # transaction cost
]
lib.run_backtest.restype = None

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

# --- Prepare arrays for C++ ---
prices = data["Close"].values.astype(np.float64)
signals = data["Position"].values.astype(np.int32)
n = len(prices)
portfolio = np.zeros(n, dtype=np.float64)

# --- Run C++ backtest and time it ---
start_cpp = time.perf_counter()
lib.run_backtest(
    prices.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
    signals.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    ctypes.c_int(n),
    portfolio.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
    ctypes.c_double(10000.0),
    ctypes.c_double(0.001),
)
end_cpp = time.perf_counter()


# --- Run Python backtest and time it ---
def python_backtest(prices, signals, initial_capital=10000, tc=0.001):
    cash = initial_capital
    shares = 0
    portfolio = []
    for i in range(len(prices)):
        if signals[i] == 1 and cash > 0:
            shares = (cash * (1 - tc)) / prices[i]
            cash = 0
        elif signals[i] == -1 and shares > 0:
            cash = shares * prices[i] * (1 - tc)
            shares = 0
        portfolio.append(cash + shares * prices[i])
    return portfolio


start_py = time.perf_counter()
py_portfolio = python_backtest(prices, signals)
end_py = time.perf_counter()

# --- Print Results ---
cpp_time = (end_cpp - start_cpp) * 1000
py_time = (end_py - start_py) * 1000
print(f"C++ execution time:    {cpp_time:.4f} ms")
print(f"Python execution time: {py_time:.4f} ms")
print(f"Speedup:               {py_time / cpp_time:.1f}x faster")
print(f"Final portfolio value: ${portfolio[-1]:,.2f}")

# --- Plot ---
plt.figure(figsize=(14, 6))
plt.plot(data.index, portfolio, label="C++ Backtest", color="steelblue")
plt.plot(
    data.index, py_portfolio, label="Python Backtest", color="orange", linestyle="--"
)
plt.title("C++ vs Python Backtest — Results should be identical")
plt.xlabel("Date")
plt.ylabel("Portfolio Value (USD)")
plt.legend()
plt.tight_layout()
plt.savefig(r"C:\Users\Lucy\Desktop\trading-engine\week5_cpp.png")
print("Chart saved!")
