import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates

plt.style.use('dark_background')

def plot_chart(df, max_points=2500):
    df['exit_date'] = pd.to_datetime(df['exit_date'])
    
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.plot(df['exit_date'][:max_points], df['Balance'][:max_points], label='Balance')
    
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.legend()
    return fig, ax
