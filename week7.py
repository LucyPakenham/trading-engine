import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Trading Engine Dashboard", layout="wide")
st.title("Algorithmic Trading Engine")
st.markdown(
    "Built by Lucy Pakenham | Moving Average Crossover Strategy with Risk Analytics"
)

# --- Sidebar Controls ---
st.sidebar.header("Strategy Settings")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL").upper()
period = st.sidebar.selectbox("Time Period", ["1y", "2y", "3y", "5y"], index=1)
ma_short = st.sidebar.slider("Short MA (days)", 10, 100, 50)
ma_long = st.sidebar.slider("Long MA (days)", 50, 300, 200)
initial_capital = st.sidebar.number_input(
    "Starting Capital ($)", value=10000, step=1000
)
transaction_cost = st.sidebar.slider("Transaction Cost (%)", 0.0, 1.0, 0.1) / 100


# --- Download Data ---
@st.cache_data
def load_data(ticker, period):
    raw = yf.download(ticker, period=period)
    data = raw["Close"].squeeze()
    data = pd.DataFrame(data)
    data.columns = ["Close"]
    return data


with st.spinner("Fetching market data..."):
    data = load_data(ticker, period)

if data.empty:
    st.error("Could not fetch data. Check the ticker symbol.")
    st.stop()

# --- Strategy ---
data["MA_Short"] = data["Close"].rolling(window=ma_short).mean()
data["MA_Long"] = data["Close"].rolling(window=ma_long).mean()
data["RawSignal"] = 0
data.loc[data["MA_Short"] > data["MA_Long"], "RawSignal"] = 1
data.loc[data["MA_Short"] < data["MA_Long"], "RawSignal"] = -1
data["Signal"] = data["RawSignal"].diff().fillna(0)
data["Position"] = 0
data.loc[data["Signal"] > 0, "Position"] = 1
data.loc[data["Signal"] < 0, "Position"] = -1
data = data.dropna()

# --- Backtest ---
cash = initial_capital
shares = 0
portfolio_value = []

for i, row in data.iterrows():
    if row["Position"] == 1 and cash > 0:
        shares = (cash * (1 - transaction_cost)) / row["Close"]
        cash = 0
    elif row["Position"] == -1 and shares > 0:
        cash = shares * row["Close"] * (1 - transaction_cost)
        shares = 0
    portfolio_value.append(cash + shares * row["Close"])

data["Portfolio"] = portfolio_value
data["BuyHold"] = initial_capital * (data["Close"] / data["Close"].iloc[0])

# --- Risk Metrics ---
returns = data["Portfolio"].pct_change().dropna()
bh_returns = data["BuyHold"].pct_change().dropna()


def sharpe(returns, rf=0.05):
    excess = returns - rf / 252
    return np.sqrt(252) * excess.mean() / excess.std()


def max_drawdown(portfolio):
    peak = portfolio.cummax()
    return ((portfolio - peak) / peak).min()


def var_95(returns):
    return np.percentile(returns.dropna(), 5)


# --- Metrics Row ---
st.subheader("Performance Summary")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Final Value", f"${data['Portfolio'].iloc[-1]:,.0f}")
col2.metric(
    "Total Return", f"{((data['Portfolio'].iloc[-1] / initial_capital) - 1) * 100:.1f}%"
)
col3.metric("Sharpe Ratio", f"{sharpe(returns):.3f}")
col4.metric("Max Drawdown", f"{max_drawdown(data['Portfolio']):.1%}")
col5.metric("VaR 95%", f"{var_95(returns):.2%}")

# --- Charts ---
st.subheader("Equity Curve")
fig1, ax1 = plt.subplots(figsize=(12, 4))
ax1.plot(data.index, data["Portfolio"], label="Strategy", color="steelblue")
ax1.plot(
    data.index, data["BuyHold"], label="Buy & Hold", color="orange", linestyle="--"
)
ax1.set_ylabel("Portfolio Value ($)")
ax1.legend()
st.pyplot(fig1)

st.subheader("Price & Moving Averages")
fig2, ax2 = plt.subplots(figsize=(12, 4))
ax2.plot(data.index, data["Close"], label=ticker, color="steelblue", alpha=0.7)
ax2.plot(data.index, data["MA_Short"], label=f"{ma_short}-day MA", color="orange")
ax2.plot(data.index, data["MA_Long"], label=f"{ma_long}-day MA", color="red")
buy = data[data["Position"] == 1]
sell = data[data["Position"] == -1]
ax2.scatter(buy.index, buy["Close"], marker="^", color="green", zorder=5, label="Buy")
ax2.scatter(sell.index, sell["Close"], marker="v", color="red", zorder=5, label="Sell")
ax2.set_ylabel("Price (USD)")
ax2.legend()
st.pyplot(fig2)

st.subheader("Drawdown")
fig3, ax3 = plt.subplots(figsize=(12, 3))
dd = (data["Portfolio"] - data["Portfolio"].cummax()) / data["Portfolio"].cummax()
ax3.fill_between(data.index, dd, 0, color="steelblue", alpha=0.5)
ax3.set_ylabel("Drawdown %")
st.pyplot(fig3)
