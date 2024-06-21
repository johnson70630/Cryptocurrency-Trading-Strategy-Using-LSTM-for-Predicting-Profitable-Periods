import pandas as pd

def process_results(df):
    entry_price_clean = df[['date', 'entry price']].dropna().reset_index(drop=True)
    exit_price_clean = df[['date', 'exit price']].dropna().reset_index(drop=True)
    pnl_clean = df[['PnL']].dropna().reset_index(drop=True)

    processed_df = pd.DataFrame()
    processed_df['entry_date'] = entry_price_clean['date']
    processed_df['entry_price'] = entry_price_clean['entry price']
    processed_df['exit_date'] = exit_price_clean['date']
    processed_df['exit_price'] = exit_price_clean['exit price']
    processed_df['PnL'] = pnl_clean['PnL']
    
    initial_balance = 100000
    processed_df['Balance'] = initial_balance + processed_df['PnL'].cumsum()
    processed_df['Cum_PnL'] = processed_df['PnL'].cumsum()

    processed_df.to_csv('processed_price_turning_BTCUSDT.csv', index=False)
    return processed_df
