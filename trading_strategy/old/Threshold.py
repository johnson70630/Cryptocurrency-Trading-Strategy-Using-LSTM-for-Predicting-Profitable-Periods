import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import requests
import json
import time
from mplfinance.original_flavor import candlestick_ohlc

# 设置pandas显示选项，显示最大行列数，数据不会被中断
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

plt.style.use('dark_background')

def get_direction(df, threshold, atr_mode, chart_type):
    up_trend = True
    last_high_i = 0
    last_low_i = 0
    last_high = df.at[0, 'high']
    last_low = df.at[0, 'low']
    tops = []
    bottoms = []
    directions = []

    for i in range(len(df)):
        if atr_mode: threshold = df.at[i, 'atr']
        if up_trend:
            if df.at[i, 'high'] > last_high:
                last_high_i = i
                last_high = df.at[i, 'high']
            elif (not atr_mode and (df.at[i, 'close'] < last_high * (1 - threshold))) or \
                    (atr_mode and (df.at[i, 'close'] < last_high - threshold)):
                if chart_type == 'OHLC':
                    tops.append([i, last_high_i, last_high])
                if chart_type == 'line':
                    tops.append([i, i, df.at[i, 'high']])
                up_trend = False
                last_low_i = i
                last_low = df.at[i, 'low']
        else:
            if df.at[i, 'low'] < last_low:
                last_low_i = i
                last_low = df.at[i, 'low']
            elif (not atr_mode and (df.at[i, 'close'] > last_low * (1 + threshold))) or \
                    (atr_mode and (df.at[i, 'close'] > last_low + threshold)):
                if chart_type == 'OHLC':
                    bottoms.append([i, last_low_i, last_low])
                if chart_type == 'line':
                    bottoms.append([i, i, df.at[i, 'low']])
                up_trend = True
                last_high_i = i
                last_high = df.at[i, 'high']

        if up_trend:
            directions.append('up')
        else:
            directions.append('down')

    df['direction'] = directions

    return df, tops, bottoms

def backtesting(df, directions, threshold, atr_mode, chart_type):
    balance = 100000
    signals = [0] * len(df)  # 初始为长度为 len(df) 的列表，最终值为 0
    buy_signals = [0] * len(df)
    sell_signals = [0] * len(df)
    buy_position = [None] * len(df)
    sell_position = [None] * len(df)
    entry_price = None
    exit_price = None
    entry_prices = [None] * len(df)
    exit_prices = [None] * len(df)
    stop_loss = None
    take_profit = None
    lot = 1
    pnl = [None] * len(df)

    for i in range(1, len(df)-1):
        # 做多
        if directions[i] == 'up' and directions[i-1] == 'down':
            signals[i] = 1
            buy_signals[i] = 1
            entry_price = df.at[i, 'close']
            entry_prices[i] = entry_price
            buy_position[i] = 'long'
        # 做空
        elif directions[i] == 'down' and directions[i-1] == 'up':
            signals[i] = -1
            sell_signals[i] = 1
            entry_price = df.at[i, 'close']
            entry_prices[i] = entry_price
            sell_position[i] = 'short'
        else:
            signals[i] = 0
            buy_signals[i] = 0
            sell_signals[i] = 0
            buy_position[i] = buy_position[i-1]
            sell_position[i] = sell_position[i-1]

        # 多单停利&止损的条件
        if buy_position[i] == 'long':
            # take profit
            if df.at[i, 'high'] >= entry_price + 3 * df.at[i, 'atr']:
                take_profit = 3 * df.at[i, 'atr'] * lot
                balance += take_profit
                buy_position[i] = None
                exit_price = entry_price + 3 * df.at[i, 'atr']
                exit_prices[i] = exit_price
                pnl[i] = take_profit
            # take profit 保利润(出现trend转角)
            elif directions[i+1] != 'up' and entry_price <= df.at[i, 'close']:
                take_profit = (df.at[i, 'close'] - entry_price) * lot
                balance += take_profit
                buy_position[i+1] = None
                exit_price = df.at[i, 'close']
                exit_prices[i] = exit_price
                pnl[i] = take_profit
                # 出现trend 轉空单
                signals[i+1] = -1
                sell_signals[i+1] = 1
                entry_price = df.at[i+1, 'close']
                entry_prices[i+1] = entry_price
                sell_position[i+1] = 'short'
            # stop loss 完整
            elif df.at[i, 'low'] < entry_price - df.at[i, 'atr']:
                stop_loss = df.at[i, 'atr'] * lot
                balance -= stop_loss
                buy_position[i] = None
                exit_price = df.at[i, 'close']
                exit_prices[i] = exit_price
                pnl[i] = - stop_loss
            # stop loss 出现 up 轉 down
            elif directions[i+1] != 'up' and entry_price >= df.at[i, 'close']:
                stop_loss = (entry_price - df.at[i, 'close']) * lot
                balance -= stop_loss
                buy_position[i+1] = None
                exit_price = df.at[i, 'close']
                exit_prices[i] = exit_price
                pnl[i] = - stop_loss
                # 出现trend 轉空单
                signals[i+1] = -1
                sell_signals[i+1] = 1
                entry_price = df.at[i+1, 'close']
                entry_prices[i+1] = entry_price
                sell_position[i+1] = 'short'
            else:
                continue
        # 空单停利&止损的条件
        if sell_position[i] == 'short':
            # take profit
            if df.at[i, 'low'] <= entry_price - 3 * df.at[i, 'atr']:
                take_profit = 3 * df.at[i, 'atr'] * lot
                balance += take_profit
                sell_position[i] = None
                exit_price = entry_price - 3 * df.at[i, 'atr']
                exit_prices[i] = exit_price
                pnl[i] = take_profit
            # take profit 保利润 出现转角down 轉 up
            elif directions[i+1] != 'down' and entry_price >= df.at[i, 'close']:
                take_profit = (entry_price - df.at[i, 'close']) * lot
                balance += take_profit
                sell_position[i+1] = None
                exit_price = df.at[i, 'close']
                exit_prices[i] = exit_price
                pnl[i] = take_profit
                # 出现trend 轉多单
                signals[i+1] = 1
                buy_signals[i+1] = 1
                entry_price = df.at[i+1, 'close']
                entry_prices[i+1] = entry_price
                buy_position[i+1] = 'long'
            # stop loss 完整
            elif df.at[i, 'high'] >= entry_price + df.at[i, 'atr']:
                stop_loss = df.at[i, 'atr'] * lot
                balance -= stop_loss
                sell_position[i] = None
                exit_price = df.at[i, 'close']
                exit_prices[i] = exit_price
                pnl[i] = - stop_loss
            # stop loss 出现down 轉 up
            elif directions[i+1] != 'down' and entry_price <= df.at[i, 'close']:
                stop_loss = (df.at[i, 'close'] - entry_price) * lot
                balance -= stop_loss
                sell_position[i+1] = None
                exit_price = df.at[i, 'close']
                exit_prices[i] = exit_price
                pnl[i] = - stop_loss
                # 出现trend 轉多单
                signals[i+1] = 1
                buy_signals[i+1] = 1
                entry_price = df.at[i+1, 'close']
                entry_prices[i+1] = entry_price
                buy_position[i+1] = 'long'
            else:
                continue

    df['signal'] = signals
    df['buy signal'] = buy_signals
    df['buy position'] = buy_position
    df['sell signals'] = sell_signals
    df['sell position'] = sell_position
    df['entry price'] = entry_prices
    df['exit price'] = exit_prices
    df['PnL'] = pnl

    return df, balance

def plot_chart(df, tops, bottoms, chart_type='OHLC'):
    items = tops + bottoms

    if chart_type == 'OHLC':
        # OHLC
        ohlc = []
        for i in range(len(df)):
            ohlc_ohlc = i, \
                        df.at[i, 'open'], \
                        df.at[i, 'high'], \
                        df.at[i, 'low'], \
                        df.at[i, 'close'],
            ohlc.append(ohlc_ohlc)

        fig = plt.figure(figsize=(16, 12))
        ax = plt.subplot2grid((1, 1), (0, 0))

        candlestick_ohlc(ax, ohlc, width=1.0, colorup='green', colordown='red')

        sorted_items = sorted(items, key=lambda x: x[1])
        items = sorted_items

        x_values = [item[1] for item in items]
        y_values = [item[2] for item in items]

        ax.plot(x_values, y_values, linestyle='-', linewidth=1, color='yellow')

        plt.show()

    elif chart_type == 'line':
        # Line
        pd.Series(df['close'].tolist()).plot()
        for top in tops:
            plt.plot(top[1], top[2], marker='o', color='white', markersize=7)
        for bottom in bottoms:
            plt.plot(bottom[1], bottom[2], marker='o', color='yellow', markersize=7)
        plt.show()

if __name__ == '__main__':
    turning_pct = 0.05
    atr_mode = True

    chart_type = 'OHLC'
    # chart_type = 'line'

    start_date = '2023-12-31 16:00:00'
    end_date = '2024-06-09 10:15:00'

    df = pd.read_csv('BTCUSDT_historical_data2.csv')
    # df['date'] = pd.to_datetime(df['Open time'], format='%Y-%m-%d %H:%M:%S')
    df['date'] = pd.to_datetime(df['Open time'], infer_datetime_format=True)

    df = df[df['date'] >= start_date]
    df = df[df['date'] < end_date]
    # df 重新命名column名称
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume','atr']

    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    df = df[df['atr'].notna()]
    df['atr'] = df['atr'] * 3
    df = df.reset_index(drop=True)

    df, tops, bottoms = get_direction(df, turning_pct, atr_mode, chart_type)
    directions = df['direction']
    df, balance = backtesting(df, directions, turning_pct, atr_mode, chart_type)

    print("Final Balance:", balance)
    print(df.head(500))
    # print(df.tail(1000))
    df.to_csv('price_turning_BTCUSDT.csv', index=True)


    # 提取entry price和exit price不为NaN的数据，并重置索引
    # the number of the 'entry price' rows: 604 (0~603)
    entry_price_clean = df[['entry price']].dropna()
    entry_price_clean = entry_price_clean.reset_index(drop=True)

    # the number of the 'exit price' rows: 603 (0~602)
    exit_price_clean = df[['exit price']].dropna()
    # 新增一个值为0的行
    exit_price_clean.loc[len(exit_price_clean)] = 0
    exit_price_clean = exit_price_clean.reset_index(drop=True)

    # 提取非NaN的'entry price'值对应的'date'并重置索引
    entry_date_clean = df[['date', 'entry price']].dropna().reset_index(drop=True)['date']
    entry_date_clean.loc[len(entry_date_clean)] = pd.NaT

    # 提取非NaN的'exit price'值对应的'date'并重置索引
    exit_date_clean = df[['date', 'exit price']].dropna().reset_index(drop=True)['date']
    exit_date_clean.loc[len(exit_date_clean)] = pd.NaT

    # 提取 PnL 不为NaN的数据，并重置索引
    extracted_df_pnl = df[['PnL']].dropna().reset_index(drop=True)

    # Create extracted_df of Dataframe
    extracted_df = pd.DataFrame()
    extracted_df['entry date'] = entry_date_clean
    extracted_df['entry price'] = entry_price_clean['entry price']

    extracted_df['exit date'] = exit_date_clean
    extracted_df['exit price'] = exit_price_clean['exit price']

    # extracted_df['PnL'] = extracted_df_pnl
    #
    # extracted_df['Balance'] = [0]*len(extracted_df)
    # extracted_df['Balance'][0] = 100_000
    # for i in range(len(extracted_df)):
    #     extracted_df['Balance'][i+1] = extracted_df['Balance'][i] + extracted_df['Pnl'][i+1]


    # extracted_df = df[['date', 'entry price', 'exit price']].dropna()

    # 重置索引，并删除旧索引
    # extracted_df = extracted_df.reset_index(drop=True)

    # 重命名列
    # extracted_df = extracted_df.rename(columns={'date': 'entry date'})

    print(entry_price_clean)
    print(exit_price_clean)
    print(extracted_df)