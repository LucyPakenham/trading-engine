# Algorithmic Trading Engine with Risk Analytics

A fully functional algorithmic trading system built in Python with a C++ performance core. Built over 8 weeks as a first-year engineering student.

## Live Demo

Run the interactive dashboard locally:

streamlit run week7.py

## Project Structure

trading-engine/

├── week1.py # Data fetching and visualisation

├── week2.py # Financial concepts and returns analysis

├── week3.py # Moving average crossover strategy

├── week4.py # Backtesting engine

├── week5.py # C++ performance core with Python bindings

├── week6.py # Risk metrics (Sharpe, VaR, Max Drawdown)

├── week7.py # Interactive Streamlit dashboard

├── backtest.cpp # C++ simulation loop

└── backtest.dll # Compiled C++ library

## Features

Live market data via Yahoo Finance API
Moving average crossover strategy with configurable MA windows
Backtesting engine with transaction costs and benchmark comparison
C++ performance core — simulation loop written in C++ and wrapped with Python ctypes bindings, achieving 1.4x speedup
Risk analytics — Sharpe ratio, Value at Risk (historical and Monte Carlo), max drawdown
Interactive dashboard built with Streamlit

## Results (AAPL, 2 years)

| Metric | Strategy | Buy & Hold |

|--------|----------|------------|

| Total Return | 31.04% | 38.93% |

| Sharpe Ratio | 0.920 | 1.447 |

| Max Drawdown | -13.80% | -13.80% |

| VaR 95% | -1.83% | -1.94% |

## Tech Stack

Python — pandas, numpy, matplotlib, yfinance, Streamlit
C++ — simulation core compiled as a shared library (.dll)
ctypes — Python bindings to call C++ from Python

## Key Learnings

How moving average crossover strategies work and their limitations
How to build a backtesting engine that avoids look-ahead bias
How to measure risk-adjusted performance using industry-standard metrics
How to write performance-critical code in C++ and integrate it with Python
How to build and deploy an interactive financial dashboard

## Built By

Lucy Pakenham — First Year Engineering Student

github.com/LucyPakenham


