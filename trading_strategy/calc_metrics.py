import pandas as pd
import numpy as np

def calc_metrics(processed_df):
    # Win Rate
    total_trades = len(processed_df)
    winning_trades = len(processed_df[processed_df['PnL'] > 0])
    win_rate = winning_trades / total_trades if total_trades > 0 else np.nan

    # Profit Factor
    gross_profit = processed_df[processed_df['PnL'] > 0]['PnL'].sum()
    gross_loss = abs(processed_df[processed_df['PnL'] < 0]['PnL'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss != 0 else np.inf

    # Average RRR
    average_rrr = gross_profit / winning_trades / (gross_loss / (total_trades - winning_trades)) if winning_trades > 0 and total_trades - winning_trades > 0 else np.inf

    # Expectancy
    expectancy = processed_df['PnL'].mean()

    # Sharpe Ratio
    pnl_mean = processed_df['PnL'].mean()
    pnl_std = processed_df['PnL'].std()
    annual_factor = np.sqrt(365)
    sharpe_ratio = pnl_mean / pnl_std * annual_factor if pnl_std > 0 else np.nan

    # Final Balance
    final_balance = processed_df['Balance'].iloc[-2] if len(processed_df) > 1 else np.nan

    # MDD (Maximum Drawdown)
    cumulative_max = processed_df['Balance'].cummax()
    drawdown = (cumulative_max - processed_df['Balance']) / cumulative_max
    max_drawdown = drawdown.max()

    metrics = {
        'Sharpe Ratio': sharpe_ratio,
        'Win Rate': win_rate,
        'Profit Factor': profit_factor,
        'Average RRR': average_rrr,
        'Expectancy': expectancy,
        'Final Balance': final_balance,
        'Total Trades Number': total_trades,
        'Maximum Drawdown': max_drawdown
    }

    metrics_df = pd.DataFrame(metrics, index=[0])
    return metrics_df
