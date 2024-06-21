import requests
import json
from datetime import datetime, timedelta
import pandas as pd

# 设置pandas显示选项，显示最大行列数，数据不会被中断
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def fetch_kline_price_data():
    API_Library = 'v1/klines'
    ticker = 'BTCUSDT'
    time_interval = '15m'  #1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    start_time = datetime(2024, 1, 1)
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
        # start_time = start_time + timedelta(minutes=1500)

        # Get the last end time
        last_entry = data[-1]
        last_close_time = last_entry[6]  # 'Close time' is the 7th element in each entry

        # Set the new start time to be the close time of the last entry in the current batch
        start_time = datetime.fromtimestamp(last_close_time / 1000.0)


    # 建立DataFrame並指定列名
    price_data = pd.DataFrame(price_data, columns=[
        'Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
        'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
        'Taker buy quote asset volume', 'Ignore'
    ])

    # 檢查並清理數據中的非數字值
    price_data = price_data.apply(pd.to_numeric, errors='coerce')

    # 刪除包含任何NaN值的行
    price_data = price_data.dropna()

    # 將時間轉換為可讀格式
    price_data['Open time'] = pd.to_datetime(price_data['Open time'], unit='ms')
    price_data['Close time'] = pd.to_datetime(price_data['Close time'], unit='ms')

    # 將 'Open time' 設為索引
    # price_data = price_data.set_index('Open time')

    # 提取OHLC格列
    extracted_df = price_data[['Open time','Open', 'High', 'Low', 'Close', 'Volume']]
    return extracted_df

price_request = fetch_kline_price_data()

price_df = pd.DataFrame(price_request)

# 保存為CSV文件
price_df.to_csv('BTCUSDT_historical_data2.csv', index=False)

print(price_df.head(1000))
print(price_df.tail(1000))

