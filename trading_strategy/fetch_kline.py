import requests
import json
from datetime import datetime, timedelta
import pandas as pd

def fetch_kline_price_data(ticker, time_interval, start_date, filename):
    API_Library = 'v1/klines'
    start_time = datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.now()
    price_data = []

    while start_time < end_time:
        start_time_2 = int(start_time.timestamp() * 1000)
        url = f'https://fapi.binance.com/fapi/{API_Library}?symbol={ticker}&interval={time_interval}&limit=1500&startTime={start_time_2}'
        print(start_time)
        resp = requests.get(url)
        data = resp.json()
        if not data:
            break
        price_data.extend(data)

        # Get the last end time
        last_entry = data[-1]
        last_close_time = last_entry[6]

        # Set the new start time to be the close time of the last entry in the current batch
        start_time = datetime.fromtimestamp(last_close_time / 1000.0)

    price_data_df = pd.DataFrame(price_data, columns=[
        'Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
        'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
        'Taker buy quote asset volume', 'Ignore'
    ])

    price_data_df = price_data_df.apply(pd.to_numeric, errors='coerce')
    price_data_df = price_data_df.dropna()
    price_data_df['Open time'] = pd.to_datetime(price_data_df['Open time'], unit='ms')
    price_data_df['Close time'] = pd.to_datetime(price_data_df['Close time'], unit='ms')

    extracted_df = price_data_df[['Open time', 'Open', 'High', 'Low', 'Close', 'Volume']]
    extracted_df.to_csv(filename, index=False)
    return extracted_df
