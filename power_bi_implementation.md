# Power BI Dashboard Implementation Guide

This guide details how to reconstruct the **SENTIX // HYPERLIQUID** Sentiment & Trader Performance Dashboard in **Microsoft Power BI Desktop**. 

If you do not have `pandas` and `numpy` installed on your machine, you have two choices:
*   **Choice 1**: Quickly install them in your system Python environment using a single command.
*   **Choice 2 (Recommended)**: Use the **100% Native Power BI Import path** detailed below. This path loads data natively via CSV and calculates archetypes using pure DAX code, bypassing Python completely!

---

## Quick Fix: Installing Pandas and NumPy (Choice 1)

If you want to use the automated Python data connector (Option A), you can install the required packages in your system's Command Prompt (cmd) or PowerShell:

```bash
pip install pandas numpy
```

> [!NOTE]
> If you are using a specific Python environment or Anaconda, make sure Power BI is pointed to the correct Python directory. Go to **File** -> **Options and settings** -> **Options** -> **Python scripting** to verify your Python home directory location.

---

## 100% Native Power BI Import Path (Choice 2 - No Python Required)

This method uses Power BI's native ETL engine (Power Query) and DAX engine to handle the entire dashboard setup.

### Step 1: Load the CSV Files Natively
1.  Open **Power BI Desktop**.
2.  Click on **Get Data** (Home Tab) -> select **Text/CSV**.
3.  Select and open:
    *   `C:\Users\Kavya Jain\.gemini\antigravity\scratch\crypto_sentiment_analysis\fear_greed_index.csv`
4.  In the preview window, click **Load**.
5.  Repeat the process to load:
    *   `C:\Users\Kavya Jain\.gemini\antigravity\scratch\crypto_sentiment_analysis\historical_trader_data.csv`

---

### Step 2: Establish the Date Relationship (Power Query)
We need to format the trader timestamps to match the Daily Fear & Greed Index dates.

1.  Click on **Transform Data** in the Home Ribbon to open the **Power Query Editor**.
2.  In the left pane, click on **historical_trader_data**.
3.  Click on **Add Column** tab -> select **Custom Column**.
    *   Name the new column: `trade_date`
    *   Enter this M formula exactly:
        ```powerquery
        Date.FromText(Text.Start([Timestamp IST], 10), "en-GB")
        ```
    *   *Note: This extracts the first 10 characters (DD-MM-YYYY) and converts them to a standard date using British date format conventions.*
4.  Click **OK**.
5.  Click on the data type icon next to the column header `trade_date` and select **Date**.
6.  Go to the **Home** tab -> click **Close & Apply**.
7.  Go to **Model View** (left-sidebar icon of three small boxes) and establish a relationship:
    *   Drag `trade_date` from **historical_trader_data** to `date` in **fear_greed_index**.
    *   *This will automatically create a Many-to-One (*:1) relationship, allowing sentiment categories to filter trader performance in real-time.*

---

### Step 3: Create calculated columns (Archetypes & Sorting)
Go to the **Data View** (or Table View) and select the `historical_trader_data` table.

#### 1. Sentiment Sorting Column (Select fear_greed_index table)
To prevent Power BI from sorting sentiment categories alphabetically:
1.  Click **New Column** in the Table Tools tab and paste this DAX:
    ```dax
    SentimentSort = 
    SWITCH(
        'fear_greed_index'[classification],
        "Extreme Fear", 1,
        "Fear", 2,
        "Neutral", 3,
        "Greed", 4,
        "Extreme Greed", 5,
        6
    )
    ```
2.  Select the `classification` column, click **Sort by column** in the ribbon, and select **SentimentSort**.

#### 2. Native DAX Trader Archetypes (Select historical_trader_data table)
This calculated column analyzes each trade and assigns the trader's strategic archetype on the fly.
1.  Click **New Column** in the Table Tools tab and paste this DAX:
    ```dax
    Trader_Archetype = 
    VAR CurrentAccount = 'historical_trader_data'[Account]
    
    // Calculate total net profit for this specific trader
    VAR TotalPnL = CALCULATE(
        SUM('historical_trader_data'[Closed PnL]), 
        ALL('historical_trader_data'), 
        'historical_trader_data'[Account] = CurrentAccount
    )
    
    // Calculate performance under Fearful conditions
    VAR FearPnL = CALCULATE(
        SUM('historical_trader_data'[Closed PnL]), 
        ALL('historical_trader_data'), 
        'historical_trader_data'[Account] = CurrentAccount, 
        RELATED('fear_greed_index'[classification]) IN {"Extreme Fear", "Fear"}
    )
    
    // Calculate performance under Greedy conditions
    VAR GreedPnL = CALCULATE(
        SUM('historical_trader_data'[Closed PnL]), 
        ALL('historical_trader_data'), 
        'historical_trader_data'[Account] = CurrentAccount, 
        RELATED('fear_greed_index'[classification]) IN {"Extreme Greed", "Greed"}
    )

    RETURN
    IF(
        TotalPnL > 10000,
        IF(FearPnL > 0 && (GreedPnL <= 0 || FearPnL > 3.0 * GreedPnL), "Fear Harvester",
        IF(GreedPnL > 0 && (FearPnL <= 0 || GreedPnL > 3.0 * FearPnL), "Greed Rider",
        IF(FearPnL > 0 && GreedPnL > 0, "Hedged Market Maker", "Opportunistic Scalper"))),
        IF(GreedPnL < -10000 && (FearPnL >= 0 || GreedPnL < 2.0 * FearPnL), "Bleeding Shorter",
        IF(FearPnL < -10000 && (GreedPnL >= 0 || FearPnL < 2.0 * GreedPnL), "Liquidation Victim", "Speculative Scalper"))
    )
    ```

---

### Step 4: Create Calculated Measures
Create these DAX measures in `historical_trader_data` to drive your visual indicators and charts:

```dax
// 1. Net Realized Profits
Total_PnL = SUM('historical_trader_data'[Closed PnL])

// 2. Aggregate Trading Volume
Total_Volume_USD = SUM('historical_trader_data'[Size USD])

// 3. Execution Count
Total_Trades = COUNTROWS('historical_trader_data')

// 4. Win Rate % (profitable trades vs non-zero trades)
Win_Rate_Pct = 
VAR NonZeroTrades = CALCULATE(COUNTROWS('historical_trader_data'), 'historical_trader_data'[Closed PnL] <> 0)
VAR ProfitableTrades = CALCULATE(COUNTROWS('historical_trader_data'), 'historical_trader_data'[Closed PnL] > 0)
RETURN
DIVIDE(ProfitableTrades, NonZeroTrades, 0)

// 5. Open Long Ratio % (Positioning for the contrarian signal)
Open_Long_Ratio_Pct = 
VAR OpenLongs = CALCULATE(COUNTROWS('historical_trader_data'), 'historical_trader_data'[Direction] = "Open Long")
VAR OpenShorts = CALCULATE(COUNTROWS('historical_trader_data'), 'historical_trader_data'[Direction] = "Open Short")
VAR TotalOpens = OpenLongs + OpenShorts
RETURN
DIVIDE(OpenLongs, TotalOpens, 0)

// 6. Aggregate Trading Fees Paid
Total_Fees = SUM('historical_trader_data'[Fee])

// 7. Dynamic Profitability Color Coding (For text color glows)
PnL_Color = IF([Total_PnL] >= 0, "#10B981", "#EF4444")
```

---

### Step 5: Visualizations Grid Construction

1.  **KPI Cards (Top Ribbon)**: Create 4 Card visuals using measures `[Total_PnL]`, `[Total_Volume_USD]`, `[Total_Trades]`, and `[Win_Rate_Pct]`.
2.  **Contrarian Signal Line & Clustered Column Chart**:
    *   **X-axis**: `classification` (from `fear_greed_index` table).
    *   **Column y-axis**: `[Open_Long_Ratio_Pct]` (formatted as percentage).
    *   **Line y-axis**: `[Total_Trades]`.
3.  **Regime Profitability Clustered Column Chart**:
    *   **X-axis**: `classification`.
    *   **Y-axis**: `[Total_PnL]`.
    *   *Conditional Formatting*: Set the bar colors dynamically using the rules option -> select column `[Total_PnL]` -> set Green for positive values and Red for negative values.
4.  **Trader Profile Directory (Table visual on left side)**:
    *   **Fields**: `Account`, `Trader_Archetype`, `[Total_PnL]`, `[Win_Rate_Pct]`.
    *   *Formatting*: Set background/text colors dynamically for PnL column based on profitability. Turning on **single-select slicing** allows the user to click any trader in this list and instantly filter all charts and metrics on the page specifically for them!
5.  **Token Rotation Table (Matrix visual)**:
    *   **Rows**: `Coin`.
    *   **Columns**: `classification` (optional).
    *   **Values**: `[Total_Volume_USD]`, `[Total_PnL]`, `[Total_Fees]`.
