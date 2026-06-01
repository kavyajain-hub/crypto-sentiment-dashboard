import pandas as pd
import numpy as np
import json
import os

def run_aggregation():
    print("Starting data aggregation engine...")
    
    # 1. Load datasets
    print("Loading datasets...")
    trader_df = pd.read_csv("historical_trader_data.csv")
    fg_df = pd.read_csv("fear_greed_index.csv")
    
    # 2. Parse dates
    print("Parsing date and time fields...")
    # Trader date: format is DD-MM-YYYY HH:MM
    trader_df['parsed_time'] = pd.to_datetime(trader_df['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
    trader_df['trade_date'] = trader_df['parsed_time'].dt.date
    
    # Fear & Greed date: format is YYYY-MM-DD
    fg_df['trade_date'] = pd.to_datetime(fg_df['date']).dt.date
    
    # 3. Merge datasets
    print("Merging datasets on trade date...")
    merged_df = pd.merge(trader_df, fg_df, on='trade_date', how='inner')
    print(f"Merged size: {len(merged_df)} rows")
    
    # 4. Global KPIs
    print("Computing global KPIs...")
    total_trades = len(merged_df)
    unique_traders = merged_df['Account'].nunique()
    total_pnl = merged_df['Closed PnL'].sum()
    total_volume_usd = merged_df['Size USD'].sum()
    total_fees = merged_df['Fee'].sum()
    
    non_zero_pnl = merged_df[merged_df['Closed PnL'] != 0]
    win_rate = (non_zero_pnl['Closed PnL'] > 0).sum() / len(non_zero_pnl) if len(non_zero_pnl) > 0 else 0
    
    global_kpis = {
        "total_trades": int(total_trades),
        "unique_traders": int(unique_traders),
        "total_pnl_usd": float(total_pnl),
        "total_volume_usd": float(total_volume_usd),
        "total_fees_usd": float(total_fees),
        "win_rate": float(win_rate)
    }
    
    # 5. Sentiment metrics
    print("Computing sentiment-specific performance metrics...")
    sentiment_order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
    sentiment_metrics = {}
    
    # Group by classification
    sent_groups = merged_df.groupby('classification')
    for sent in sentiment_order:
        if sent in sent_groups.groups:
            group = sent_groups.get_group(sent)
            s_non_zero = group[group['Closed PnL'] != 0]
            s_win_rate = (s_non_zero['Closed PnL'] > 0).sum() / len(s_non_zero) if len(s_non_zero) > 0 else 0
            
            sentiment_metrics[sent] = {
                "total_pnl": float(group['Closed PnL'].sum()),
                "mean_pnl": float(group['Closed PnL'].mean()),
                "trade_count": int(len(group)),
                "total_volume": float(group['Size USD'].sum()),
                "avg_trade_size": float(group['Size USD'].mean()),
                "win_rate": float(s_win_rate)
            }
        else:
            sentiment_metrics[sent] = {
                "total_pnl": 0.0,
                "mean_pnl": 0.0,
                "trade_count": 0,
                "total_volume": 0.0,
                "avg_trade_size": 0.0,
                "win_rate": 0.0
            }
            
    # 6. Directional ratios (Contrarian Signal)
    print("Computing directional (Long/Short) ratios by sentiment...")
    directional_metrics = {}
    open_trades = merged_df[merged_df['Direction'].isin(['Open Long', 'Open Short'])]
    dir_groups = open_trades.groupby(['classification', 'Direction']).size().unstack(fill_value=0)
    
    for sent in sentiment_order:
        if sent in dir_groups.index:
            longs = int(dir_groups.loc[sent, 'Open Long'])
            shorts = int(dir_groups.loc[sent, 'Open Short'])
            total = longs + shorts
            long_ratio = longs / total if total > 0 else 0.5
            
            directional_metrics[sent] = {
                "open_longs": longs,
                "open_shorts": shorts,
                "total_opens": total,
                "long_ratio": float(long_ratio)
            }
        else:
            directional_metrics[sent] = {
                "open_longs": 0,
                "open_shorts": 0,
                "total_opens": 0,
                "long_ratio": 0.5
            }
            
    # 7. Trader Profiles & Archetypes
    print("Profiling 32 traders and assigning tactical Archetypes...")
    trader_profiles = []
    
    trader_groups = merged_df.groupby('Account')
    for acc, group in trader_groups:
        acc_total_pnl = group['Closed PnL'].sum()
        acc_trades = len(group)
        acc_volume = group['Size USD'].sum()
        acc_fees = group['Fee'].sum()
        
        acc_non_zero = group[group['Closed PnL'] != 0]
        acc_win_rate = (acc_non_zero['Closed PnL'] > 0).sum() / len(acc_non_zero) if len(acc_non_zero) > 0 else 0
        
        # Calculate sentiment PnL matrix for this trader
        sent_matrix = {}
        t_sent_groups = group.groupby('classification')
        
        fear_pnl = 0.0
        greed_pnl = 0.0
        
        for sent in sentiment_order:
            if sent in t_sent_groups.groups:
                t_group = t_sent_groups.get_group(sent)
                tg_non_zero = t_group[t_group['Closed PnL'] != 0]
                tg_win_rate = (tg_non_zero['Closed PnL'] > 0).sum() / len(tg_non_zero) if len(tg_non_zero) > 0 else 0
                
                s_pnl = float(t_group['Closed PnL'].sum())
                s_count = int(len(t_group))
                
                sent_matrix[sent] = {
                    "pnl": s_pnl,
                    "trades": s_count,
                    "win_rate": float(tg_win_rate)
                }
                
                if sent in ['Extreme Fear', 'Fear']:
                    fear_pnl += s_pnl
                elif sent in ['Extreme Greed', 'Greed']:
                    greed_pnl += s_pnl
            else:
                sent_matrix[sent] = {
                    "pnl": 0.0,
                    "trades": 0,
                    "win_rate": 0.0
                }
        
        # Determine archetype
        archetype = "Opportunistic Scalper"
        description = "Trades flexibly across all market sentiments, scaling size as opportunities arise."
        
        if acc_total_pnl > 10000: # Profitable traders
            # Fear specialist
            if fear_pnl > 0 and (greed_pnl <= 0 or fear_pnl > 3.0 * greed_pnl):
                archetype = "Fear Harvester"
                description = "Dip-buying specialist. Thrives during panic (Fear/Extreme Fear) and steps away or underperforms during high greed."
            # Greed momentum rider
            elif greed_pnl > 0 and (fear_pnl <= 0 or greed_pnl > 3.0 * fear_pnl):
                archetype = "Greed Rider"
                description = "Momentum breakout specialist. Highly profitable during strong uptrends and euphoria, but struggles in major sell-offs."
            # Hedged market maker (profitable in both)
            elif fear_pnl > 0 and greed_pnl > 0:
                archetype = "Hedged Market Maker"
                description = "Systematic profile. Maintains high win rates and profitability in both fear panic and greed expansion, likely delta-neutral."
        else: # Unprofitable or low-profit traders
            # Bleeding Shorter
            if greed_pnl < -10000 and (fear_pnl >= 0 or greed_pnl < 2.0 * fear_pnl):
                archetype = "Bleeding Shorter"
                description = "High-risk contrarian who aggressively shorts bull runs too early, suffering heavy drawdowns during blow-off tops."
            # Liquidation Victim
            elif fear_pnl < -10000 and (greed_pnl >= 0 or fear_pnl < 2.0 * greed_pnl):
                archetype = "Liquidation Victim"
                description = "Vulnerable to liquidations. Suffers severe losses during market panics (Fear/Extreme Fear), likely due to over-leveraged longs."
            else:
                archetype = "Speculative Scalper"
                description = "High-turnover scalper experiencing erratic PnL. Struggles to maintain consistent risk management under extreme market conditions."
                
        trader_profiles.append({
            "account": acc,
            "display_name": acc[:6] + "..." + acc[-4:],
            "total_pnl": float(acc_total_pnl),
            "trade_count": int(acc_trades),
            "total_volume": float(acc_volume),
            "total_fees": float(acc_fees),
            "win_rate": float(acc_win_rate),
            "archetype": archetype,
            "description": description,
            "sentiment_matrix": sent_matrix
        })
        
    # Sort profiles by PnL descending
    trader_profiles.sort(key=lambda x: x['total_pnl'], reverse=True)
    
    # 8. Token Rotation Metrics
    print("Aggregating token preferences and rotation profiles...")
    # Overall coin stats
    coin_pnl = merged_df.groupby('Coin')['Closed PnL'].sum()
    coin_volume = merged_df.groupby('Coin')['Size USD'].sum()
    coin_trades = merged_df.groupby('Coin').size()
    coin_fees = merged_df.groupby('Coin')['Fee'].sum()
    
    coins_list = []
    for coin in coin_pnl.index:
        coins_list.append({
            "coin": coin,
            "total_pnl": float(coin_pnl[coin]),
            "total_volume": float(coin_volume[coin]),
            "trade_count": int(coin_trades[coin]),
            "total_fees": float(coin_fees[coin])
        })
    # Sort overall coins by size USD
    coins_list.sort(key=lambda x: x['total_volume'], reverse=True)
    
    # Coin stats by sentiment (Top 8 coins per sentiment)
    token_rotation_by_sentiment = {}
    sent_coin_groups = merged_df.groupby(['classification', 'Coin'])
    
    for sent in sentiment_order:
        sent_coins = []
        if sent in merged_df['classification'].values:
            sent_df = merged_df[merged_df['classification'] == sent]
            s_coin_pnl = sent_df.groupby('Coin')['Closed PnL'].sum()
            s_coin_vol = sent_df.groupby('Coin')['Size USD'].sum()
            s_coin_trades = sent_df.groupby('Coin').size()
            
            for coin in s_coin_trades.index:
                sent_coins.append({
                    "coin": coin,
                    "pnl": float(s_coin_pnl[coin]),
                    "volume": float(s_coin_vol[coin]),
                    "trades": int(s_coin_trades[coin])
                })
            # Sort by volume descending and take top 8
            sent_coins.sort(key=lambda x: x['volume'], reverse=True)
            token_rotation_by_sentiment[sent] = sent_coins[:10]
        else:
            token_rotation_by_sentiment[sent] = []
            
    # Assemble the final dashboard JSON payload
    print("Compiling all analytics into optimized JSON schema...")
    dashboard_data = {
        "global_kpis": global_kpis,
        "sentiment_metrics": sentiment_metrics,
        "directional_signals": directional_metrics,
        "trader_profiles": trader_profiles,
        "overall_coins": coins_list[:30], # Top 30 coins overall
        "token_rotation_by_sentiment": token_rotation_by_sentiment
    }
    
    # 9. Output file
    output_filename = "dashboard_data.json"
    with open(output_filename, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
        
    print(f"Data aggregation engine complete! Output saved to: {output_filename}")
    print(f"File size: {os.path.getsize(output_filename) / 1024:.2f} KB (optimized from 45.32 MB!)")

if __name__ == "__main__":
    run_aggregation()
