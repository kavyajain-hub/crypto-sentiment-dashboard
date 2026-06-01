import pandas as pd
import numpy as np

def inspect_file(filepath):
    print("=" * 60)
    print(f"Inspecting: {filepath}")
    print("=" * 60)
    try:
        # Read the first few lines to detect delimiter and check structure
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i in range(5):
                print(f"Line {i+1}: {f.readline().strip()}")
        
        # Load with pandas
        df = pd.read_csv(filepath)
        print(f"\nShape: {df.shape}")
        print("\nColumns and Data Types:")
        print(df.dtypes)
        print("\nMissing values count:")
        print(df.isnull().sum())
        print("\nFirst 3 rows:")
        print(df.head(3))
        
        # Date column inspection
        date_cols = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()]
        for col in date_cols:
            print(f"\nSample date/time values for '{col}':")
            print(df[col].head(5))
            try:
                if df[col].dtype == object:
                    # Let's try converting a sample
                    parsed = pd.to_datetime(df[col].head(100), errors='coerce')
                    print(f"Successfully parsed sample date range: {parsed.min()} to {parsed.max()}")
                else:
                    # Check if it's timestamp (e.g. ms or seconds)
                    sample_vals = df[col].dropna().head(5).values
                    if len(sample_vals) > 0 and sample_vals[0] > 1e9: # looks like unix timestamp
                        unit = 'ms' if sample_vals[0] > 1e11 else 's'
                        parsed = pd.to_datetime(df[col].head(100), unit=unit, errors='coerce')
                        print(f"Numeric timestamp parsed as '{unit}' range: {parsed.min()} to {parsed.max()}")
            except Exception as e:
                print(f"Could not parse date column: {e}")
                
        return df
    except Exception as e:
        print(f"Error inspecting file: {e}")
        return None

if __name__ == "__main__":
    inspect_file("fear_greed_index.csv")
    inspect_file("historical_trader_data.csv")
