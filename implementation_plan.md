# Crypto Sentiment & Trader Performance Analysis Plan

Explore the relationship between Bitcoin market sentiment (Fear & Greed Index) and professional trader performance on the Hyperliquid platform. By linking 211,224 rows of historical trade data with daily sentiment classifications, we will uncover hidden trading behaviors, classify traders into tactical archetypes, and build a premium interactive dashboard to visualize these actionable insights.

---

## Key Research Findings (Data Insights)

Our preliminary data research of the datasets revealed high-value, non-obvious patterns:

1. **The Contrarian Signal (Top Traders vs. Retail Index)**:
   - When the market is in **Extreme Fear**, professional traders are highly bullish, opening **68.8% Longs** (7,005 Longs vs 3,174 Shorts).
   - In **Extreme Greed**, they turn highly bearish, opening **54.9% Shorts** (7,663 Shorts vs 6,300 Longs).
   - *Conclusion*: Elite traders trade contrarian to retail sentiment, accumulating during panic and shorting during euphoria.

2. **Trader Sentiment Archetypes (Out of 32 Unique Accounts)**:
   - **The Greed Rider** (e.g. `0xb1231a...ed23`, +$2.14M PnL): Thrives in high-sentiment momentum, generating +$1.10M of profits in *Extreme Greed* alone with a 93.8% win rate, but barely breaks even in *Extreme Fear*.
   - **The Fear Harvester** (e.g. `0xbaaaf6...7864`, +$940k PnL): A pure dip-buying specialist. Thrives in *Fear* (+$620k, 98.6% win rate) and *Extreme Fear* (+$261k, 100% win rate), but completely shuts off trading in *Extreme Greed*.
   - **The Hedged Market Maker** (e.g. `0x083384...9012`, +$1.60M PnL): Consistent across Fear, Neutral, and Greed, but gets run over (-$40k loss, 25.6% win rate) during blow-off tops (*Extreme Greed*).
   - **The Bleeding Shorter** (e.g. `0x817071...a63b`, -$167k PnL): Profitable in fearful and neutral markets, but wiped out by shorting too early during *Greed* (-$360k loss).

3. **Token Rotation Patterns**:
   - In **Extreme Fear**, volume concentrates in major assets: **BTC** ($36.75M), **HYPE** ($29.25M), and **SOL** ($26.24M) representing a "flight to quality" and dip-buying blue-chips.
   - In **Extreme Greed**, speculative rotation triggers. High-beta tokens rise: **@107** becomes the most active asset with 10,403 trades and $20.45M in volume, indicating traders pivot to riskier perps during retail euphoria.
   - **Highest Profit Driver**: Token `@107` has generated the highest total PnL (**+$2.78M**), followed by `HYPE` (**+$1.95M**) and `SOL` (**+$1.64M**).
   - **Worst Performing Token**: `TRUMP` (**-$364.8k**), followed by `FARTCOIN` (**-$100.6k**).

---

## User Review Required

> [!IMPORTANT]
> **Data Processing Optimization**: The historical trader dataset is large (**45.32 MB, 211,224 rows**). Loading and processing this dataset directly in a web browser can cause severe lag, high RAM usage, or browser crashes. 
> To ensure a blazing-fast, buttery-smooth user experience, I propose pre-aggregating the data using a Python backend script into compact, structured JSON files (totaling <100 KB). The interactive dashboard will load these pre-processed JSON structures, rendering instantly and allowing real-time interactions with zero latency.

---

## Open Questions

None at this time. The data exploration is complete, and the findings are highly cohesive and ready to be compiled into a premium UI dashboard!

---

## Proposed Changes

We will create a new project directory at `C:\Users\Kavya Jain\.gemini\antigravity\scratch\crypto_sentiment_analysis`.

### [Component 1] Data Aggregation Engine (Python)

This component will read the raw 45.32 MB `historical_trader_data.csv` and `fear_greed_index.csv`, merge them, classify traders into archetypes, analyze coin rotations, and compile optimized JSON files for the web app.

#### [NEW] [aggregate_data.py](file:///C:/Users/Kavya%20Jain/.gemini/antigravity/scratch/crypto_sentiment_analysis/aggregate_data.py)
A Python script that will:
1. Merge the trader data with sentiment indices on the exact date.
2. Group and aggregate metrics per trader (Total PnL, average size, win rate, and classification-specific PnL).
3. Assign a trader "Archetype" label based on their sentiment-performance ratios.
4. Calculate contrarian open long/short ratios per sentiment.
5. Aggregate token preferences (PnL, volume, count) grouped by sentiment.
6. Output `dashboard_data.json` (<100 KB) containing all preprocessed analytics.

---

### [Component 2] Premium Interactive Dashboard (Web UI)

This component will render the dashboard utilizing rich aesthetics: HSL tailored color schemes, glassmorphism, responsive flex layouts, glowing visual hierarchy, and smooth CSS transitions. It will use Chart.js via CDN for responsive, high-performance charting.

#### [NEW] [index.html](file:///C:/Users/Kavya%20Jain/.gemini/antigravity/scratch/crypto_sentiment_analysis/index.html)
Main HTML5 entry point containing:
- Glassmorphic navigation header with overall metrics.
- Sentiment Correlation Panel: Showing average trade PnL, win rates, and size across the 5 sentiments.
- Interactive Chart Grid:
  - **Contrarian Signal Chart**: Interactive bar/line chart displaying Open Long Ratio % vs. Market Sentiment.
  - **PnL Distribution Chart**: Total profits generated under different market regimes.
- **Trader Profiles Directory**: Interactive card directory listing the 32 traders. Users can filter by profitability or archetype badge, click a trader, and view their individual radar/bar chart of sentiment performance.
- **Token Rotation Matrix**: Interactive leaderboard table showing which tokens generated the most profits, losses, and volumes under each sentiment.

#### [NEW] [style.css](file:///C:/Users/Kavya%20Jain/.gemini/antigravity/scratch/crypto_sentiment_analysis/style.css)
Vanilla CSS stylesheet embodying elite modern web design:
- Harmonious dark-mode color scheme using curated deep space slate, emerald neon green (+PnL), ruby neon red (-PnL), and specific hues for Fear (orange/red) and Greed (lime/green).
- Custom variables, modern typography (Google Fonts Inter and Outfit).
- Micro-animations: Hover expansions, border glows, smooth card fades.
- Fully responsive flexbox/grid layout designed to wow at first glance.

#### [NEW] [app.js](file:///C:/Users/Kavya%20Jain/.gemini/antigravity/scratch/crypto_sentiment_analysis/app.js)
Frontend logic that:
- Fetches `dashboard_data.json`.
- Dynamically populates KPI cards.
- Configures and renders all Chart.js charts (using customized neon glow colors, font configurations, and responsive tooltip styling).
- Manages interactive states: Trader selection, archetype filtering, and coin list sorting.

---

## Verification Plan

### Automated & Manual Verification
1. **Python Aggregation Validation**: Run `aggregate_data.py` and verify it successfully parses all 211,224 rows and correctly outputs a single `dashboard_data.json` without errors.
2. **Dashboard Visual Test**: Open `index.html` in a web browser using the dev server or local file. Verify:
   - Layout is fully responsive and glassmorphism styling renders beautifully.
   - All charts load and interactive tooltips are fully styled.
   - Clicking on different traders dynamically switches the personal performance card and updates their specific performance chart.
   - Filtering traders by archetype (e.g. clicking "Fear Harvester") works instantly.
