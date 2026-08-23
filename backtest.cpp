#include <vector>
#include <iostream>

// This function simulates the trading portfolio day by day
// It takes prices and signals as input and returns the portfolio value each day
extern "C" {
    void run_backtest(
        double* prices,    // array of closing prices
        int* signals,      // array of signals: 1=buy, -1=sell, 0=hold
        int n,             // number of days
        double* portfolio, // output: portfolio value each day
        double initial_capital,
        double transaction_cost
    ) {
        double cash = initial_capital;
        double shares = 0.0;

        for (int i = 0; i < n; i++) {
            if (signals[i] == 1 && cash > 0) {
                // Buy
                shares = (cash * (1.0 - transaction_cost)) / prices[i];
                cash = 0.0;
            } else if (signals[i] == -1 && shares > 0) {
                // Sell
                cash = shares * prices[i] * (1.0 - transaction_cost);
                shares = 0.0;
            }
            portfolio[i] = cash + shares * prices[i];
        }
    }
}