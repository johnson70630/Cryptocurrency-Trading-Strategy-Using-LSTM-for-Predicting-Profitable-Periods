import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import requests
import json
import time
from mplfinance.original_flavor import candlestick_ohlc

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
