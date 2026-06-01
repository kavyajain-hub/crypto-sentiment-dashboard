import pandas as pd
import numpy as np

def explore():
    print("=== Exploring Fear & Greed Dataset ===")
    fg_df = pd.read_csv("fear_greed_index.csv")
    fg_df['date'] = pd.to_datetime(fg_df['date'])
    print(f"Fear & Greed Date Range: {fg_df['date'].min()} to {fg_df['date'].max()}")
    print("Classifications count:")
    print(fg_df['classification'].value_counts())
    
    print("\n=== Exploring Historical Trader Dataset ===")
    trader_df = pd.read_csv("historical_trader_data.csv")
    
    # Let's inspect unique accounts, coins, and sides
    print(f"Total Trades: {len(trader_df)}")
    print(f"Unique Accounts: {trader_df['Account'].nunique()}")
    print("Top 10 Accounts by trade count:")
    print(trader_df['Account'].value_counts().head(10))
    print(f"Unique Coins: {trader_df['Coin'].nunique()}")
    print("Top 10 Coins by trade count:")
    print(trader_df['Coin'].value_counts().head(10))
    print("Sides count:")
    print(trader_df['Side'].value_counts())
    print("Direction count:")
    print(trader_df['Direction'].value_counts())
    
    # Parse timestamps
    # Let's see some exact values of Timestamp
    pd.set_option('display.float_format', lambda x: '%.3f' % x)
    print("\nSample raw timestamps:")
    print(trader_df[['Timestamp IST', 'Timestamp', 'Closed PnL']].head(10))
    
    # Let's convert 'Timestamp IST' which is in format DD-MM-YYYY HH:MM
    trader_df['parsed_time'] = pd.to_datetime(trader_df['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
    print(f"\nParsed Time Range: {trader_df['parsed_time'].min()} to {trader_df['parsed_time'].max()}")
    print(f"Null parsed times: {trader_df['parsed_time'].isnull().sum()}")
    
    # PnL Analysis
    print("\n=== PnL Summary ===")
    print(f"Total PnL across all trades: {trader_df['Closed PnL'].sum():,.2f} USD")
    print(f"Average PnL per trade: {trader_df['Closed PnL'].mean():,.4f} USD")
    print(f"Number of profitable trades (PnL > 0): {(trader_df['Closed PnL'] > 0).sum()} ({((trader_df['Closed PnL'] > 0).sum() / len(trader_df)) * 100:.2f}%)")
    print(f"Number of unprofitable trades (PnL < 0): {(trader_df['Closed PnL'] < 0).sum()} ({((trader_df['Closed PnL'] < 0).sum() / len(trader_df)) * 100:.2f}%)")
    print(f"Number of zero PnL trades (PnL == 0): {(trader_df['Closed PnL'] == 0).sum()} ({((trader_df['Closed PnL'] == 0).sum() / len(trader_df)) * 100:.2f}%)")
    
    # Let's see the sum of PnL for top 10 accounts
    pnl_by_account = trader_df.groupby('Account')['Closed PnL'].sum().sort_values(ascending=False)
    print("\nTop 5 Most Profitable Accounts:")
    print(pnl_by_account.head(5))
    print("\nTop 5 Least Profitable Accounts:")
    print(pnl_by_account.tail(5))
    
    # Merge and correlate with Fear & Greed
    # We want to extract 'date' from 'parsed_time' in YYYY-MM-DD
    trader_df['trade_date'] = trader_df['parsed_time'].dt.date
    fg_df['trade_date'] = fg_df['date'].dt.date
    
    merged_df = pd.merge(trader_df, fg_df, on='trade_date', how='inner')
    print(f"\nMerged dataset size: {len(merged_df)}")
    
    # Analyze PnL by Fear & Greed classification
    print("\n=== PnL and Activity by Fear & Greed Sentiment ===")
    pnl_by_sentiment = merged_df.groupby('classification').agg(
        total_pnl=('Closed PnL', 'sum'),
        mean_pnl=('Closed PnL', 'mean'),
        trade_count=('Closed PnL', 'count'),
        avg_trade_size_usd=('Size USD', 'mean'),
        win_rate=('Closed PnL', lambda x: (x > 0).sum() / (x != 0).sum() if (x != 0).sum() > 0 else 0)
    ).reindex(['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'])
    
    print(pnl_by_sentiment)

if __name__ == "__main__":
    explore()
