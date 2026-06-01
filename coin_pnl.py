import pandas as pd

def print_coin_pnl():
    trader_df = pd.read_csv("historical_trader_data.csv")
    
    coin_pnl = trader_df.groupby('Coin')['Closed PnL'].sum().sort_values(ascending=False)
    
    print("=== Coins Ranked by Total PnL (Profitable) ===")
    for coin, pnl in coin_pnl.head(15).items():
        print(f"{coin:10} : {pnl:,.2f} USD")
        
    print("\n=== Coins Ranked by Total PnL (Unprofitable) ===")
    for coin, pnl in coin_pnl.tail(15).items():
        print(f"{coin:10} : {pnl:,.2f} USD")

if __name__ == "__main__":
    print_coin_pnl()
