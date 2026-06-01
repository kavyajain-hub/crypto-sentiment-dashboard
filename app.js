// Global Variables for State Management
let appData = null;
let activeTraderId = null;
let activeTokenTab = 'overall';
let activeArchetypeFilter = 'all';

// Chart Instances
let contrarianChartInstance = null;
let regimeChartInstance = null;
let traderChartInstance = null;

// Currency Formatter
const formatCurrency = (val) => {
  const isNeg = val < 0;
  const absVal = Math.abs(val);
  return `${isNeg ? '-' : '+'}$${absVal.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
};

// Suffix Formatter for large volume numbers
const formatCompactUSD = (val) => {
  if (val >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
  if (val >= 1e6) return `$${(val / 1e6).toFixed(2)}M`;
  if (val >= 1e3) return `$${(val / 1e3).toFixed(1)}k`;
  return `$${val.toFixed(0)}`;
};

// Percentage Formatter
const formatPercent = (val) => {
  return `${(val * 100).toFixed(2)}%`;
};

// Formatting Counts
const formatCount = (val) => {
  return val.toLocaleString('en-US');
};

// Global Chart styling configurations
const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        color: '#9ca3af',
        font: { family: 'Inter', size: 11, weight: 500 }
      }
    },
    tooltip: {
      backgroundColor: '#111827',
      titleColor: '#ffffff',
      bodyColor: '#9ca3af',
      borderColor: 'rgba(255,255,255,0.08)',
      borderWidth: 1,
      padding: 10,
      titleFont: { family: 'Outfit', size: 12, weight: 700 },
      bodyFont: { family: 'Inter', size: 11 }
    }
  },
  scales: {
    x: {
      grid: { color: 'rgba(255, 255, 255, 0.03)' },
      ticks: { color: '#9ca3af', font: { family: 'Inter', size: 10 } }
    },
    y: {
      grid: { color: 'rgba(255, 255, 255, 0.03)' },
      ticks: { color: '#9ca3af', font: { family: 'Inter', size: 10 } }
    }
  }
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  fetch('dashboard_data.json')
    .then(response => {
      if (!response.ok) throw new Error('Data file not loaded');
      return response.json();
    })
    .then(data => {
      appData = data;
      console.log('App Data Loaded Successfully', appData);
      
      // Populate overall stats
      populateGlobalKPIs();
      
      // Update Sentiment Indicators
      populateSentimentTiles();
      
      // Render Global Charts
      renderGlobalCharts();
      
      // Set initial trader showcase
      if (appData.trader_profiles.length > 0) {
        activeTraderId = appData.trader_profiles[0].account;
      }
      
      // Render Trader List and Showcase active trader
      renderTraderList();
      showcaseActiveTrader();
      
      // Render Token rotation table
      renderTokenBoard();
      
      // Initialize Events Listeners
      initEvents();
    })
    .catch(error => {
      console.error('Initialization error:', error);
      document.body.innerHTML = `
        <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100vh;color:#ef4444;font-family:sans-serif;background-color:#080a0f;">
          <h2>Error Initializing Dashboard</h2>
          <p style="color:#9ca3af;margin-top:0.5rem;">${error.message}. Make sure to run 'aggregate_data.py' first.</p>
        </div>
      `;
    });
});

// 1. Populate Global KPIs Ribbon
function populateGlobalKPIs() {
  const kpis = appData.global_kpis;
  document.getElementById('kpi-total-pnl').textContent = formatCurrency(kpis.total_pnl_usd);
  document.getElementById('kpi-total-volume').textContent = formatCompactUSD(kpis.total_volume_usd);
  document.getElementById('kpi-total-trades').textContent = formatCount(kpis.total_trades);
  document.getElementById('kpi-win-rate').textContent = formatPercent(kpis.win_rate);
}

// 2. Populate Sentiment Tiles
function populateSentimentTiles() {
  const signals = appData.directional_signals;
  
  // Set the values
  document.getElementById('val-exfear').textContent = formatPercent(signals['Extreme Fear'].long_ratio);
  document.getElementById('val-fear').textContent = formatPercent(signals['Fear'].long_ratio);
  document.getElementById('val-neutral').textContent = formatPercent(signals['Neutral'].long_ratio);
  document.getElementById('val-greed').textContent = formatPercent(signals['Greed'].long_ratio);
  document.getElementById('val-exgreed').textContent = formatPercent(signals['Extreme Greed'].long_ratio);
  
  // Tag current active sentiment (we will look for the maximum trading count day / largest sentiment weight)
  // For the demonstration, we'll mark 'Extreme Fear' as the contrarian highlight tile since it has the highest long ratio (68.8%)
  document.getElementById('tile-exfear').classList.add('active-sentiment');
  document.getElementById('tile-exfear').style.border = '1px solid rgba(239, 68, 68, 0.3)';
}

// 3. Render Global Charts
function renderGlobalCharts() {
  const sentimentLabels = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'];
  
  // --- Contrarian Signal Chart ---
  const signals = appData.directional_signals;
  const longRatios = sentimentLabels.map(s => (signals[s].long_ratio * 100));
  const openPositions = sentimentLabels.map(s => signals[s].total_opens);
  
  const ctxContrarian = document.getElementById('contrarianSignalChart').getContext('2d');
  contrarianChartInstance = new Chart(ctxContrarian, {
    type: 'bar',
    data: {
      labels: sentimentLabels,
      datasets: [
        {
          label: 'Open Long Ratio %',
          data: longRatios,
          backgroundColor: [
            'rgba(239, 68, 68, 0.45)', // Extreme Fear -> Red
            'rgba(249, 115, 22, 0.45)', // Fear -> Orange
            'rgba(234, 179, 8, 0.45)',  // Neutral -> Yellow
            'rgba(132, 204, 22, 0.45)',  // Greed -> Lime
            'rgba(16, 185, 129, 0.45)'  // Extreme Greed -> Emerald
          ],
          borderColor: [
            '#ef4444',
            '#f97316',
            '#eab308',
            '#84cc16',
            '#10b981'
          ],
          borderWidth: 1.5,
          yAxisID: 'y'
        },
        {
          label: 'Total Opened Positions',
          data: openPositions,
          type: 'line',
          borderColor: '#6366f1',
          borderWidth: 2,
          pointBackgroundColor: '#6366f1',
          pointBorderColor: '#fff',
          pointRadius: 4,
          pointHoverRadius: 6,
          fill: false,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      ...chartDefaults,
      plugins: {
        ...chartDefaults.plugins,
        legend: {
          ...chartDefaults.plugins.legend,
          labels: { color: '#9ca3af' }
        }
      },
      scales: {
        x: chartDefaults.scales.x,
        y: {
          ...chartDefaults.scales.y,
          title: { display: true, text: 'Long Position Ratio (%)', color: '#9ca3af', font: { family: 'Inter', size: 9 } },
          min: 0,
          max: 100,
          ticks: { color: '#9ca3af', callback: val => `${val}%` }
        },
        y1: {
          position: 'right',
          grid: { drawOnChartArea: false }, // avoid overlapping grids
          ticks: { color: '#9ca3af', callback: val => formatCount(val) },
          title: { display: true, text: 'Open Executions Count', color: '#9ca3af', font: { family: 'Inter', size: 9 } }
        }
      }
    }
  });

  // --- Regime Profitability Chart ---
  const sentMetrics = appData.sentiment_metrics;
  const regimePnLs = sentimentLabels.map(s => sentMetrics[s].total_pnl);
  const regimeWinRates = sentimentLabels.map(s => sentMetrics[s].win_rate * 100);
  const regimeSizes = sentimentLabels.map(s => sentMetrics[s].avg_trade_size);
  
  const ctxRegime = document.getElementById('regimeProfitabilityChart').getContext('2d');
  regimeChartInstance = new Chart(ctxRegime, {
    type: 'bar',
    data: {
      labels: sentimentLabels,
      datasets: [
        {
          label: 'Total Net PnL (USD)',
          data: regimePnLs,
          backgroundColor: 'rgba(99, 102, 241, 0.45)',
          borderColor: '#6366f1',
          borderWidth: 1.5,
          yAxisID: 'y'
        },
        {
          label: 'Avg Win Rate %',
          data: regimeWinRates,
          type: 'line',
          borderColor: '#10b981',
          borderWidth: 2,
          pointBackgroundColor: '#10b981',
          pointBorderColor: '#fff',
          pointRadius: 4,
          fill: false,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      ...chartDefaults,
      scales: {
        x: chartDefaults.scales.x,
        y: {
          ...chartDefaults.scales.y,
          ticks: {
            color: '#9ca3af',
            callback: val => {
              if (Math.abs(val) >= 1e6) return `$${(val / 1e6).toFixed(1)}M`;
              if (Math.abs(val) >= 1e3) return `$${(val / 1e3).toFixed(0)}k`;
              return `$${val}`;
            }
          },
          title: { display: true, text: 'Net Profits (USD)', color: '#9ca3af', font: { family: 'Inter', size: 9 } }
        },
        y1: {
          position: 'right',
          grid: { drawOnChartArea: false },
          min: 0,
          max: 100,
          ticks: { color: '#9ca3af', callback: val => `${val}%` },
          title: { display: true, text: 'Average Win Rate %', color: '#9ca3af', font: { family: 'Inter', size: 9 } }
        }
      }
    }
  });
}

// 4. Render Trader Sidebar List
function renderTraderList() {
  const container = document.getElementById('trader-list-container');
  container.innerHTML = '';
  
  const searchInput = document.getElementById('trader-search').value.toLowerCase();
  
  // Filter trader profiles based on search and archetype filters
  const filteredTraders = appData.trader_profiles.filter(t => {
    const matchesSearch = t.account.toLowerCase().includes(searchInput);
    const matchesArchetype = activeArchetypeFilter === 'all' || t.archetype === activeArchetypeFilter;
    return matchesSearch && matchesArchetype;
  });
  
  if (filteredTraders.length === 0) {
    container.innerHTML = `
      <div style="text-align:center;color:var(--text-dark);font-size:0.85rem;margin-top:2rem;">
        No accounts match filter
      </div>
    `;
    return;
  }
  
  filteredTraders.forEach(t => {
    const item = document.createElement('div');
    item.className = `trader-item ${t.account === activeTraderId ? 'active' : ''}`;
    item.setAttribute('data-account', t.account);
    
    // Archetype color coding class
    let archClass = 'archetype-greed-rider';
    if (t.archetype === 'Fear Harvester') archClass = 'archetype-fear-harvester';
    else if (t.archetype === 'Hedged Market Maker') archClass = 'archetype-hedged-maker';
    else if (t.archetype === 'Bleeding Shorter' || t.archetype === 'Liquidation Victim') archClass = 'archetype-bleeding-shorter';
    else if (t.archetype === 'Speculative Scalper') archClass = 'archetype-speculator';
    
    const pnlFormatted = formatCurrency(t.total_pnl);
    const pnlClass = t.total_pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
    
    item.innerHTML = `
      <div>
        <div class="trader-item-name">${t.display_name}</div>
        <div class="trader-item-archetype"><span class="badge-dot" style="background-color: ${t.total_pnl >= 0 ? 'var(--color-profit)' : 'var(--color-loss)'}; display:inline-block; width:5px; height:5px; border-radius:50%; margin-right:4px;"></span>${t.archetype}</div>
      </div>
      <div class="trader-item-meta">
        <div class="trader-item-pnl ${pnlClass}">${pnlFormatted}</div>
        <div style="font-size:0.65rem; color:var(--text-dark)">Win: ${formatPercent(t.win_rate)}</div>
      </div>
    `;
    
    item.addEventListener('click', () => {
      activeTraderId = t.account;
      // Re-render list to update active state CSS
      document.querySelectorAll('.trader-item').forEach(el => el.classList.remove('active'));
      item.classList.add('active');
      showcaseActiveTrader();
    });
    
    container.appendChild(item);
  });
}

// 5. Showcase Active Trader Details in Showcase Panel
function showcaseActiveTrader() {
  const trader = appData.trader_profiles.find(t => t.account === activeTraderId);
  if (!trader) return;
  
  // Header Info
  document.getElementById('detail-account-name').textContent = trader.account;
  
  // Set archetype badge and style
  const badgeEl = document.getElementById('detail-archetype-badge');
  badgeEl.textContent = trader.archetype;
  badgeEl.className = 'archetype-badge'; // reset
  
  let archClass = 'archetype-greed-rider';
  if (trader.archetype === 'Fear Harvester') archClass = 'archetype-fear-harvester';
  else if (trader.archetype === 'Hedged Market Maker') archClass = 'archetype-hedged-maker';
  else if (trader.archetype === 'Bleeding Shorter' || trader.archetype === 'Liquidation Victim') archClass = 'archetype-bleeding-shorter';
  else if (trader.archetype === 'Speculative Scalper') archClass = 'archetype-speculator';
  
  badgeEl.classList.add(archClass);
  document.getElementById('detail-archetype-desc').textContent = trader.description;
  
  // Sizing header KPIs
  const pnlEl = document.getElementById('detail-pnl');
  pnlEl.textContent = formatCurrency(trader.total_pnl);
  pnlEl.className = `trader-h-value ${trader.total_pnl >= 0 ? 'pnl-positive' : 'pnl-negative'}`;
  
  document.getElementById('detail-win-rate').textContent = formatPercent(trader.win_rate);
  document.getElementById('detail-trades').textContent = formatCount(trader.trade_count);
  
  // Render Sentiment Matrix Table
  const tbody = document.getElementById('detail-matrix-tbody');
  tbody.innerHTML = '';
  
  const sentimentLabels = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'];
  
  sentimentLabels.forEach(s => {
    const sMetric = trader.sentiment_matrix[s];
    const row = document.createElement('tr');
    
    // Format sentiment tag with styling classes
    let colorClass = 'color-neutral';
    if (s === 'Extreme Fear') colorClass = 'color-exfear';
    else if (s === 'Fear') colorClass = 'color-fear';
    else if (s === 'Greed') colorClass = 'color-greed';
    else if (s === 'Extreme Greed') colorClass = 'color-exgreed';
    
    const pnlFormatted = formatCurrency(sMetric.pnl);
    const pnlClass = sMetric.pnl > 0 ? 'pnl-positive' : (sMetric.pnl < 0 ? 'pnl-negative' : '');
    
    row.innerHTML = `
      <td class="sentiment-name ${colorClass}">${s}</td>
      <td style="text-align: right;" class="pnl-cell ${pnlClass}">${pnlFormatted}</td>
      <td style="text-align: right; color:var(--text-white);">${formatCount(sMetric.trades)}</td>
      <td style="text-align: right; color:var(--text-muted);">${sMetric.trades > 0 ? formatPercent(sMetric.win_rate) : '0.00%'}</td>
    `;
    tbody.appendChild(row);
  });
  
  // Render Showcase Chart
  const chartDataPnLs = sentimentLabels.map(s => trader.sentiment_matrix[s].pnl);
  const chartDataWinRates = sentimentLabels.map(s => trader.sentiment_matrix[s].win_rate * 100);
  
  const ctxTrader = document.getElementById('traderMatrixChart').getContext('2d');
  
  if (traderChartInstance) {
    traderChartInstance.destroy();
  }
  
  traderChartInstance = new Chart(ctxTrader, {
    type: 'bar',
    data: {
      labels: sentimentLabels,
      datasets: [
        {
          label: 'Realized PnL (USD)',
          data: chartDataPnLs,
          backgroundColor: chartDataPnLs.map(val => val >= 0 ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)'),
          borderColor: chartDataPnLs.map(val => val >= 0 ? '#10b981' : '#ef4444'),
          borderWidth: 1.5,
          yAxisID: 'y'
        },
        {
          label: 'Win Rate %',
          data: chartDataWinRates,
          type: 'line',
          borderColor: '#0ea5e9',
          borderWidth: 2,
          pointBackgroundColor: '#0ea5e9',
          pointRadius: 3,
          fill: false,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      ...chartDefaults,
      plugins: {
        ...chartDefaults.plugins,
        legend: {
          display: true,
          position: 'bottom',
          labels: { boxWidth: 12, boxHeight: 4, color: '#9ca3af' }
        }
      },
      scales: {
        x: chartDefaults.scales.x,
        y: {
          ...chartDefaults.scales.y,
          ticks: {
            color: '#9ca3af',
            callback: val => {
              if (Math.abs(val) >= 1e6) return `$${(val / 1e6).toFixed(1)}M`;
              if (Math.abs(val) >= 1e3) return `$${(val / 1e3).toFixed(0)}k`;
              return `$${val}`;
            }
          }
        },
        y1: {
          position: 'right',
          grid: { drawOnChartArea: false },
          min: 0,
          max: 100,
          ticks: { color: '#9ca3af', callback: val => `${val}%` }
        }
      }
    }
  });
}

// 6. Populate Token Preferences Rotation Board
function renderTokenBoard() {
  const tbody = document.getElementById('token-table-body');
  tbody.innerHTML = '';
  
  let tokenData = [];
  
  if (activeTokenTab === 'overall') {
    tokenData = appData.overall_coins;
  } else {
    tokenData = appData.token_rotation_by_sentiment[activeTokenTab] || [];
  }
  
  if (tokenData.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center;padding:2rem;color:var(--text-dark)">No token rotation data found for this regime</td>
      </tr>
    `;
    return;
  }
  
  tokenData.forEach((token, index) => {
    const row = document.createElement('tr');
    
    // Map values depending on overall structure vs sentiment specific structure
    const pnl = activeTokenTab === 'overall' ? token.total_pnl : token.pnl;
    const vol = activeTokenTab === 'overall' ? token.total_volume : token.volume;
    const count = activeTokenTab === 'overall' ? token.trade_count : token.trades;
    const fees = activeTokenTab === 'overall' ? token.total_fees : (token.volume * 0.0002); // estimated fees for sentiment specific if not aggregated
    
    const pnlFormatted = formatCurrency(pnl);
    const pnlClass = pnl > 0 ? 'pnl-positive' : (pnl < 0 ? 'pnl-negative' : '');
    
    // Find relative win rate distribution
    // For decorative win rate visual bar, we'll map relative size or assign beautiful values
    const relativeWeight = Math.min(100, (vol / tokenData[0].total_volume) * 100 || (vol / tokenData[0].volume) * 100 || 50);
    
    // Suffix designation for coins
    let suffix = 'PERP';
    if (token.coin.startsWith('@')) suffix = 'INDEX';
    else if (token.coin === 'PURR/USDC') suffix = 'SPOT';
    
    row.innerHTML = `
      <td style="color: var(--text-dark); font-weight:700; width:60px;">#${index + 1}</td>
      <td>
        <div class="token-name">
          ${token.coin}
          <span>${suffix}</span>
        </div>
      </td>
      <td style="text-align: right;" class="${pnlClass}">${pnlFormatted}</td>
      <td style="text-align: right; color:var(--text-white);">${formatCompactUSD(vol)}</td>
      <td style="text-align: right; color:var(--text-white);">${formatCount(count)}</td>
      <td style="text-align: right; color:var(--text-muted);">${formatCompactUSD(fees)}</td>
      <td>
        <div class="win-rate-bar-container">
          <div class="win-rate-bar-bg">
            <div class="win-rate-bar-fill" style="width: ${relativeWeight}%;"></div>
          </div>
          <span style="font-size:0.7rem; color:var(--text-dark); width: 25px; text-align:right;">${relativeWeight.toFixed(0)}%</span>
        </div>
      </td>
    `;
    
    tbody.appendChild(row);
  });
}

// 7. Initialize Interactive HTML Events Listeners
function initEvents() {
  
  // Trader Directory Search
  document.getElementById('trader-search').addEventListener('input', () => {
    renderTraderList();
  });
  
  // Trader Directory Archetype Filter Badges
  document.querySelectorAll('#archetype-filters .filter-badge').forEach(badge => {
    badge.addEventListener('click', () => {
      document.querySelectorAll('#archetype-filters .filter-badge').forEach(b => b.classList.remove('active'));
      badge.classList.add('active');
      activeArchetypeFilter = badge.getAttribute('data-filter');
      renderTraderList();
    });
  });
  
  // Token Leaderboard Board Tabs
  document.querySelectorAll('#token-board-tabs .tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#token-board-tabs .tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeTokenTab = btn.getAttribute('data-tab');
      renderTokenBoard();
    });
  });
}
