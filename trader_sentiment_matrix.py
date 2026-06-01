import pandas as pd
import numpy as np

def analyze_trader_behavior():
    trader_df = pd.read_csv("historical_trader_data.csv")
    fg_df = pd.read_csv("fear_greed_index.csv")
    
    # Parse dates
    trader_df['parsed_time'] = pd.to_datetime(trader_df['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
    trader_df['trade_date'] = trader_df['parsed_time'].dt.date
    fg_df['trade_date'] = pd.to_datetime(fg_df['date']).dt.date
    
    # Merge
    merged_df = pd.merge(trader_df, fg_df, on='trade_date', how='inner')
    
    # Let's get the top 5 profitable and top 5 unprofitable traders
    pnl_by_account = merged_df.groupby('Account')['Closed PnL'].sum().sort_values(ascending=False)
    top_profitable = pnl_by_account.head(5).index.tolist()
    top_unprofitable = pnl_by_account.tail(5).index.tolist()
    key_accounts = top_profitable + top_unprofitable
    
    print("=== Top Traders Performance across Sentiments ===")
    for acc in key_accounts:
        acc_short = acc[:8] + "..." + acc[-4:]
        acc_df = merged_df[merged_df['Account'] == acc]
        print(f"\nTrader: {acc_short} (Total PnL: {acc_df['Closed PnL'].sum():,.2f} USD)")
        
        # Group by sentiment
        sent_perf = acc_df.groupby('classification').agg(
            pnl=('Closed PnL', 'sum'),
            trades=('Closed PnL', 'count'),
            win_rate=('Closed PnL', lambda x: (x > 0).sum() / (x != 0).sum() if (x != 0).sum() > 0 else 0)
        ).reindex(['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'])
        print(sent_perf)
        
    print("\n=== Long/Short Directional Preference by Market Sentiment ===")
    # Let's see if there is a preference for Long vs Short based on sentiment
    # We will filter for 'Open Long' and 'Open Short' directions
    open_trades = merged_df[merged_df['Direction'].isin(['Open Long', 'Open Short'])]
    direction_by_sentiment = open_trades.groupby(['classification', 'Direction']).size().unstack().reindex(['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'])
    direction_by_sentiment['Long_Ratio'] = direction_by_sentiment['Open Long'] / (direction_by_sentiment['Open Long'] + direction_by_sentiment['Open Short'])
    print(direction_by_sentiment)
    
    print("\n=== Coin Preferences by Market Sentiment ===")
    # Let's see what coins are traded in Extreme Fear vs Extreme Greed
    for sent in ['Extreme Fear', 'Extreme Greed']:
        sent_df = merged_df[merged_df['classification'] == sent]
        print(f"\nTop 5 Coins traded in {sent} (by Trade Count):")
        print(sent_df['Coin'].value_counts().head(5))
        
        print(f"Top 5 Coins traded in {sent} (by Total Size USD):")
        print(sent_df.groupby('Coin')['Size USD'].sum().sort_values(ascending=False).head(5))

if __name__ == "__main__":
    analyze_trader_behavior()
