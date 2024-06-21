def backtesting(df, directions, threshold, atr_mode, chart_type):
    balance = 100000
    signals = [0] * len(df)  
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
        if directions[i] == 'up' and directions[i-1] == 'down':
            signals[i] = 1
            buy_signals[i] = 1
            entry_price = df.at[i, 'close']
            entry_prices[i] = entry_price
            buy_position[i] = 'long'
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

        if buy_position[i] == 'long':
            # take profit
            if df.at[i, 'high'] >= entry_price + 3 * df.at[i, 'atr']:
                take_profit = 3 * df.at[i, 'atr'] * lot
                balance += take_profit
                buy_position[i] = None
                exit_price = entry_price + 3 * df.at[i, 'atr']
                exit_prices[i] = exit_price
                pnl[i] = take_profit
            elif directions[i+1] != 'up' and entry_price <= df.at[i, 'close']:
                take_profit = (df.at[i, 'close'] - entry_price) * lot
                balance += take_profit
                buy_position[i+1] = None
                exit_price = df.at[i, 'close']
                exit_prices[i] = exit_price
                pnl[i] = take_profit
                signals[i+1] = -1
                sell_signals[i+1] = 1
                entry_price = df.at[i+1, 'close']
                entry_prices[i+1] = entry_price
                sell_position[i+1] = 'short'
            elif df.at[i, 'low'] < entry_price - df.at[i, 'atr']:
                stop_loss = df.at[i, 'atr'] * lot
                balance -= stop_loss
                buy_position[i] = None
                exit_price = df.at[i, 'close']
                exit_prices[i] = exit_price
                pnl[i] = - stop_loss
            elif directions[i+1] != 'up' and entry_price >= df.at[i, 'close']:
                stop_loss = (entry_price - df.at[i, 'close']) * lot
                balance -= stop_loss
                buy_position[i+1] = None
                exit_price = df.at[i, 'close']
                exit_prices[i] = exit_price
                pnl[i] = - stop_loss
                signals[i+1] = -1
                sell_signals[i+1] = 1
                entry_price = df.at[i+1, 'close']
                entry_prices[i+1] = entry_price
                sell_position[i+1] = 'short'
            else:
                continue
        if sell_position[i] == 'short':
            # take profit
            if df.at[i, 'low'] <= entry_price - 3 * df.at[i, 'atr']:
                take_profit = 3 * df.at[i, 'atr'] * lot
                balance += take_profit
                sell_position[i] = None
                exit_price = entry_price - 3 * df.at[i, 'atr']
                exit_prices[i] = exit_price
                pnl[i] = take_profit
            elif directions[i+1] != 'down' and entry_price >= df.at[i, 'close']:
                take_profit = (entry_price - df.at[i, 'close']) * lot
                balance += take_profit
                sell_position[i+1] = None
                exit_price = df.at[i, 'close']
                exit_prices[i] = exit_price
                pnl[i] = take_profit
                signals[i+1] = 1
                buy_signals[i+1] = 1
                entry_price = df.at[i+1, 'close']
                entry_prices[i+1] = entry_price
                buy_position[i+1] = 'long'
            elif df.at[i, 'high'] >= entry_price + df.at[i, 'atr']:
                stop_loss = df.at[i, 'atr'] * lot
                balance -= stop_loss
                sell_position[i] = None
                exit_price = df.at[i, 'close']
                exit_prices[i] = exit_price
                pnl[i] = - stop_loss
            elif directions[i+1] != 'down' and entry_price <= df.at[i, 'close']:
                stop_loss = (df.at[i, 'close'] - entry_price) * lot
                balance -= stop_loss
                sell_position[i+1] = None
                exit_price = df.at[i, 'close']
                exit_prices[i] = exit_price
                pnl[i] = - stop_loss
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

