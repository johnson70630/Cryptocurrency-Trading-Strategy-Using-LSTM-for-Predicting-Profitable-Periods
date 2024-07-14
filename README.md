# Cryptocurrency Trading Strategy Using LSTM for Predicting Profitable Periods

## Why?
In quantitative trading strategies, there are range-bound strategies and breakout strategies. This time, we developed a price trend reversal strategy. However, in unsuitable market conditions, the strategy continuously incurs losses, leading to self-doubt and the desire to shut down the strategy. Can we avoid this situation?

We are attempting to use LSTM models that handle time-series data to predict the periods when the strategy will be profitable or non profitable. By determining when to activate or deactivate the strategy based on these predictions, can we reduce the instances of losses and further improve the performance of the breakout strategy?
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
[Modeling file](https://github.com/johnson70630/Trading-Strategy-with-LSTM/blob/main/LSTM_15min/LSTM_prediction_15min_period.ipynb) has all precoss of data processing, model training, and output.

**Input:**   recent data + previous 24 data points (6hr) 

**predict:**    the label of next K line

Split data on 2023-06-30

- training data:  80,000+  
- testing data:  30,000+
## Training Result
- Train 50 epochs (1~2 hr)
- Training Accuracy: 69.47%
- Testing Accuracy:  64.95%
## Strategy ﻿Result
[Compare Profit file](https://github.com/johnson70630/Trading-Strategy-with-LSTM/blob/main/LSTM_15min/comparing_profit.ipynb) demonstrated the result of the trading strategy overall profit from 2023-06-30 ~ 2024-06-09, and the result after LSTM prediction.

Date:  2023-06-30 ~ 2024-06-09

**Strategy Before Model Prediction**
- Total PnL:  164621.37
- Win Rate:  46.45%

**Strategy After Model Prediction**
- Total PnL:  100063.53
- Win Rate: 45.84%

## Ways to Improve 
- **Multi-Timeframe Analysis**

  We found that the short-term market may be hard to predict. As a result, we could add data from different time frame to confirm signal.
- **Add different types data (IV, Funding Rate, Option data)**

  Many of the technical indicators we use are related to price and have high homogeneity. Therefore, we could consider using different
  indicators, such as implied volatility, funding rates, and options prices.
- **Different way of labeling**

  Perhaps the labeled data for the periods cannot provide the model with sufficient discriminatory power. We could try different labeling
  methods, such as labeling market trends instead of adjusting the labels based on the strategy. Alternatively, we could label the periods of significant losses and gains separately. Binary classification might not be sufficient.
- **Use Transformer in model**

  We all know that transformers are very powerful models. Perhaps we can apply their positional encoding method to help the model assign more
  appropriate weights to each feature.
