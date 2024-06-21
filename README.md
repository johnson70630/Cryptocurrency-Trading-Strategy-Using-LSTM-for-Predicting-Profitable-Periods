# Trading-Strategy-with-LSTM

## Why?
Quantitative strategies inevitably incur losses. If AI can predict the periods when a quantitative strategy will incur losses, can it reduce losses and increase the win rate?
## LSTM
An LSTM (Long Short-Term Memory) model is a type of recurrent neural network (RNN) designed to effectively learn and remember long-term dependencies in sequential data.
## Fetching Data
In [fetching data](https://github.com/johnson70630/Trading-Strategy-with-LSTM/blob/main/LSTM_15min/fetching_data.ipynb), we fetched BTC-USDT price both from spot market and futures market (15 minutes interval) from Binance API (2021-01-01 ~ 2024-06-15)
## Add Indicators
There are multiple trading indicators added in the [adding data](https://github.com/johnson70630/Trading-Strategy-with-LSTM/blob/main/LSTM_15min/adding_indicators.ipynb)
- MA, EMA (96 K-lines, 1 day)
- Historical Volatility (96 K-lines, 1 day)
- Relative Strength Index (RSI)
- Moving Average Convergence Divergence (MACD)
- and so on ....
**The purpose of adding indicators is to increase the number of features in the data.**
## Labeling
The original trading backtesting result is in [this file](https://github.com/johnson70630/Trading-Strategy-with-LSTM/blob/main/LSTM_15min/data/processed_price_turning_BTCUSDT.csv)
We add label in [true label](https://github.com/johnson70630/Trading-Strategy-with-LSTM/blob/main/LSTM_15min/true_label.ipynb).

**Adding True Label by the Entry date of the original trading backtesting**
- PnL > 0  ->  label = 1
- PnL < 0  ->  label = 0 
- data -> 4,800+
  
**Adding Ture label by the period from entry time to exit time of the original trading backtesting**
- PnL > 0  ->  label = 1
- PnL < 0  ->  label = 0
- data -> 120,000+ 
We ultimately use the dataset with more data points to train the model.
(model prediction ->  1 or 0  ->  PnL > 0  or  PnL  < 0)
## Modeling
Input:   recent data + previous 16 data points (4hr) 

predict:    the label of next K line

Split data on 2023-06-30

- training data:  80,000+  
- testing data:  30,000+
## Training Result
