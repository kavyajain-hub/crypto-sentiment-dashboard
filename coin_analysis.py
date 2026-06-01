import pandas as pd

def analyze_coins():
    trader_df = pd.read_csv("historical_trader_data.csv")
    
    # Group by Coin and aggregate
    coin_summary = trader_df.groupby('Coin').agg(
        trade_count=('Closed PnL', 'count'),
        total_size_usd=('Size USD', 'sum'),
        total_pnl=('Closed PnL', 'sum'),
        avg_execution_price=('Execution Price', 'mean'),
        total_fees=('Fee', 'sum')
    ).sort_values(by='total_size_usd', ascending=False)
    
    print("=== Top 15 Coins by Total Size USD ===")
    print(coin_summary.head(15))
    
    print("\n=== Most Profitable Coins overall ===")
    print(coin_summary.sort_values(by='total_pnl', ascending=False).head(10))
    
    print("\n=== Least Profitable Coins overall ===")
    print(coin_summary.sort_values(by='total_pnl', ascending=True).head(10))

if __name__ == "__main__":
    analyze_coins()
