import re

with open("frontend/index.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. CSS
css_injection = """
    footer a:hover {
      color: var(--accent);
    }

    /* ── Multi-Tab UI ──────────────────────────────────── */
    .workspace-tabs {
      display: flex; gap: 8px; margin-bottom: 24px; overflow-x: auto; padding-bottom: 4px;
    }
    .workspace-tabs::-webkit-scrollbar { height: 4px; }
    .workspace-tabs::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

    .workspace-tab {
      background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-sm);
      padding: 10px 16px; font-size: 0.85rem; font-weight: 600; color: var(--text-muted); cursor: pointer;
      display: flex; align-items: center; gap: 12px; transition: all 0.2s; white-space: nowrap; user-select: none;
    }
    .workspace-tab:hover { border-color: var(--text-primary); }
    .workspace-tab.active {
      background: var(--bg-secondary); border-color: var(--accent); color: var(--accent);
      box-shadow: 0 0 10px rgba(240, 185, 11, 0.1);
    }
    .workspace-tab-close {
      color: var(--text-muted); font-size: 1.1rem; line-height: 1; padding: 0 4px; border-radius: 4px; transition: all 0.2s;
    }
    .workspace-tab-close:hover { background: rgba(246, 70, 93, 0.15); color: var(--short); }

    .workspace-content { display: none; animation: fadeInUp 0.4s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
    .workspace-content.active { display: block; }
  </style>
"""
text = text.replace("    footer a:hover {\n      color: var(--accent);\n    }\n  </style>", css_injection)


# 2. HTML Result Section
html_pattern = re.compile(r'    <!-- Result -->\n    <div id="result-section">.*?    </div><!-- /result-section -->', re.DOTALL)

html_injection = """    <!-- Result Workspace -->
    <div id="result-section">
      <div class="workspace-tabs" id="workspace-tabs"></div>
      <div id="workspace-contents"></div>
    </div><!-- /result-section -->

    <!-- Template -->
    <template id="card-template">
      <div class="signal-card dyn-signal-card" style="margin-bottom: 24px;">
        <div class="signal-header">
          <div>
            <div style="font-size:0.72rem;font-weight:600;color:var(--text-muted);letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px;">Signal for</div>
            <div class="signal-symbol dyn-res-symbol">—</div>
          </div>
          <div class="signal-right">
            <div class="confidence-wrap">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="var(--border)" stroke-width="9" />
                <circle class="dyn-conf-ring" cx="50" cy="50" r="40" fill="none" stroke="var(--accent)" stroke-width="9" stroke-linecap="round" stroke-dasharray="251.33" stroke-dashoffset="251.33" transform="rotate(-90 50 50)" style="transition: stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)" />
                <text class="dyn-conf-text" x="50" y="56" text-anchor="middle" fill="var(--text-primary)" font-family="Inter,sans-serif" font-size="20" font-weight="700">0</text>
              </svg>
              <span class="confidence-label">Confidence</span>
            </div>
            <div class="direction-badge dyn-direction-badge HOLD">● HOLD</div>
          </div>
        </div>

        <div class="metrics-grid">
          <div class="metric"><span class="metric-label">Entry Price</span><span class="metric-value dyn-res-entry">—</span></div>
          <div class="metric"><span class="metric-label">Stop Loss</span><span class="metric-value short-val dyn-res-sl">—</span></div>
          <div class="metric"><span class="metric-label">Take Profit</span><span class="metric-value long-val dyn-res-tp">—</span></div>
          <div class="metric"><span class="metric-label">Leverage</span><span class="metric-value dyn-res-lev">—</span></div>
          <div class="metric"><span class="metric-label">Position Size</span><span class="metric-value dyn-res-pos">—</span></div>
        </div>

        <div class="reasoning-box" style="margin-bottom: 24px;">
          <div class="reasoning-label">📊 AI Reasoning</div>
          <div class="dyn-res-reasoning">—</div>
        </div>

        <div style="background: var(--bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-sm); overflow: hidden; height: 350px;">
          <div class="dyn-chart-container" style="width: 100%; height: 100%;"></div>
        </div>
      </div>

      <details class="market-panel dyn-market-panel">
        <summary>📈 Raw Market Data</summary>
        <div class="global-metrics dyn-global-metrics">
          <div class="gm-item"><span class="gm-label">Funding Rate</span><span class="gm-value dyn-gm-funding">—</span></div>
          <div class="gm-item"><span class="gm-label">Open Interest</span><span class="gm-value dyn-gm-oi">—</span></div>
          <div class="gm-item"><span class="gm-label">Bid/Ask Ratio</span><span class="gm-value dyn-gm-bar">—</span></div>
        </div>
        <div class="tf-tabs dyn-tf-tabs">
          <div class="tf-tab active" data-tf="15m">15m</div><div class="tf-tab" data-tf="1h">1h</div>
          <div class="tf-tab" data-tf="4h">4h</div><div class="tf-tab" data-tf="1d">1d</div>
        </div>
        <div class="ind-table active dyn-tf-15m"></div><div class="ind-table dyn-tf-1h"></div>
        <div class="ind-table dyn-tf-4h"></div><div class="ind-table dyn-tf-1d"></div>
      </details>
    </template>"""
text = html_pattern.sub(html_injection, text)

# 3. JavaScript
js_pattern = re.compile(r'    // ── Render Signal ──────────────────────────────────────.*?    // ── Market Dashboard ───────────────────────────────────', re.DOTALL)

js_injection = """    // ── Multi-Tab Manager ──────────────────────────────────
    const MAX_TABS = 5;
    let tabs = [];
    
    function switchTab(tabId) {
      document.querySelectorAll('.workspace-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.workspace-content').forEach(c => c.classList.remove('active'));
      const tBtn = document.getElementById('tab-btn-' + tabId);
      const cDiv = document.getElementById('tab-content-' + tabId);
      if (tBtn) tBtn.classList.add('active');
      if (cDiv) cDiv.classList.add('active');
    }

    function removeTab(tabId) {
      const idx = tabs.findIndex(t => t.id === tabId);
      if (idx === -1) return;
      if (tabs[idx].ws) {
        tabs[idx].ws.close();
      }
      tabs.splice(idx, 1);
      document.getElementById('tab-btn-' + tabId)?.remove();
      document.getElementById('tab-content-' + tabId)?.remove();

      if (tabs.length > 0) {
        switchTab(tabs[tabs.length - 1].id);
      } else {
        resultEl.classList.remove('active');
      }
    }

    // ── Render Signal (Tab Scoped) ─────────────────────────
    function renderSignal(data, symbol, cardEl) {
      const dir = (data.direction || 'HOLD').toUpperCase();
      cardEl.querySelector('.dyn-res-symbol').textContent = data.asset || symbol;

      const badge = cardEl.querySelector('.dyn-direction-badge');
      badge.className = 'direction-badge dyn-direction-badge ' + dir;
      const icons = { LONG: '▲', SHORT: '▼', HOLD: '◆' };
      badge.textContent = (icons[dir] || '●') + ' ' + dir;

      const colors = { LONG: 'var(--long)', SHORT: 'var(--short)', HOLD: 'var(--hold)' };
      const glows = { LONG: 'rgba(0,200,150,0.35)', SHORT: 'rgba(246,70,93,0.35)', HOLD: 'rgba(94,111,138,0.25)' };
      cardEl.querySelector('.dyn-signal-card').style.setProperty('--direction-color', colors[dir] || colors.HOLD);
      badge.style.setProperty('--badge-glow', glows[dir] || glows.HOLD);

      const score = parseFloat(data.confidence_score) || 0;
      const offset = 251.33 * (1 - score / 100);
      const ringColor = score >= 70 ? 'var(--long)' : score >= 40 ? 'var(--accent)' : 'var(--short)';
      const ring = cardEl.querySelector('.dyn-conf-ring');
      ring.style.stroke = ringColor;
      requestAnimationFrame(() => { setTimeout(() => { ring.style.strokeDashoffset = offset; }, 60); });
      cardEl.querySelector('.dyn-conf-text').textContent = score;

      cardEl.querySelector('.dyn-res-entry').textContent = fmtPrice(data.entry_price);
      cardEl.querySelector('.dyn-res-sl').textContent = fmtPrice(data.stop_loss);
      cardEl.querySelector('.dyn-res-tp').textContent = fmtPrice(data.take_profit);
      cardEl.querySelector('.dyn-res-lev').textContent = (data.leverage || '—') + 'x';
      cardEl.querySelector('.dyn-res-pos').textContent = (data.position_size_percent || '—') + '%';
      cardEl.querySelector('.dyn-res-reasoning').textContent = data.reasoning || '—';
    }

    // ── Render Market Data (Tab Scoped) ────────────────────
    function renderMarketData(md, cardEl) {
      const fr = parseFloat(md.funding_rate) * 100;
      cardEl.querySelector('.dyn-gm-funding').textContent = (fr >= 0 ? '+' : '') + fr.toFixed(4) + '%';
      cardEl.querySelector('.dyn-gm-oi').textContent = fmt(md.open_interest, 0);
      const bar = parseFloat(md.bid_ask_ratio);
      const barEl = cardEl.querySelector('.dyn-gm-bar');
      barEl.textContent = bar.toFixed(3);
      barEl.style.color = bar > 1 ? 'var(--long)' : 'var(--short)';

      const tfs = ['15m', '1h', '4h', '1d'];
      tfs.forEach(tf => {
        const d = md.timeframes[tf];
        const el = cardEl.querySelector('.dyn-tf-' + tf);
        if (!d) { el.innerHTML = '<div style="padding:16px;color:var(--text-muted)">No data</div>'; return; }

        const rsi = parseFloat(d.RSI_14);
        const rsiClass = rsi > 70 ? 'red' : rsi < 30 ? 'green' : '';
        const ema50 = parseFloat(d.EMA50);
        const ema200 = parseFloat(d.EMA200);
        const emaClass = ema50 > ema200 ? 'green' : 'red';
        const emaTrend = ema50 > ema200 ? '↑ Bullish' : '↓ Bearish';
        const hist = parseFloat(d.MACD_histogram);
        const histClass = hist > 0 ? 'green' : 'red';
        const atr = parseFloat(d.ATR_14);
        const buyRat = parseFloat(d.Buy_Vol_Ratio);
        const volStyle = d.Volume > d.Volume_SMA_20 ? 'color: var(--long)' : 'color: var(--text-muted)';
        const buyClass = buyRat > 0.5 ? 'green' : 'red';

        el.innerHTML = `
        <div class="ind-row"><span class="ind-name">Price</span><span class="ind-val">${fmtPrice(d.price)}</span></div>
        <div class="ind-row"><span class="ind-name">24h Change</span><span class="ind-val ${d.change_24h >= 0 ? 'green' : 'red'}">${d.change_24h >= 0 ? '+' : ''}${d.change_24h}%</span></div>
        <div class="ind-row"><span class="ind-name">RSI (14)</span><span class="ind-val ${rsiClass}">${fmt(rsi, 2)}</span></div>
        <div class="ind-row"><span class="ind-name">ATR (14)</span><span class="ind-val">${fmtPrice(atr)}</span></div>
        <div class="ind-row"><span class="ind-name">Volume / SMA(20)</span><span class="ind-val" style="${volStyle}">${fmt(d.Volume, 2)} / ${fmt(d.Volume_SMA_20, 2)}</span></div>
        <div class="ind-row"><span class="ind-name">Buy Vol Ratio</span><span class="ind-val ${buyClass}">${fmt(buyRat * 100, 2)}%</span></div>
        <div class="ind-row"><span class="ind-name">MACD Line</span><span class="ind-val">${fmt(d.MACD_line, 4)}</span></div>
        <div class="ind-row"><span class="ind-name">MACD Signal</span><span class="ind-val">${fmt(d.MACD_signal, 4)}</span></div>
        <div class="ind-row"><span class="ind-name">MACD Histogram</span><span class="ind-val ${histClass}">${fmt(hist, 4)}</span></div>
        <div class="ind-row"><span class="ind-name">EMA 50</span><span class="ind-val">${fmtPrice(d.EMA50)}</span></div>
        <div class="ind-row"><span class="ind-name">EMA 200</span><span class="ind-val">${fmtPrice(d.EMA200)}</span></div>
        <div class="ind-row"><span class="ind-name">EMA Trend</span><span class="ind-val ${emaClass}">${emaTrend}</span></div>
      `;
      });
      
      const tabContainer = cardEl.querySelector('.dyn-tf-tabs');
      tabContainer.addEventListener('click', e => {
        const tab = e.target.closest('.tf-tab');
        if (!tab) return;
        const tf = tab.dataset.tf;
        tabContainer.querySelectorAll('.tf-tab').forEach(t => t.classList.remove('active'));
        cardEl.querySelectorAll('.ind-table').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        cardEl.querySelector('.dyn-tf-' + tf).classList.add('active');
      });
    }

    // ── Main Analyze Function ──────────────────────────────
    async function analyze() {
      const symbol = inputEl.value.trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
      if (!symbol) {
        inputEl.focus(); inputEl.style.borderColor = 'var(--short)';
        setTimeout(() => { inputEl.style.borderColor = ''; }, 900);
        return;
      }
      const style = document.getElementById('style-select').value;
      showLoading();

      try {
        const res = await fetch('/api/analyze', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ symbol, style })
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Server error' }));
          throw new Error(err.detail || `HTTP ${res.status}`);
        }
        const data = await res.json();
        hideLoading();
        errorEl.classList.remove('active');
        resultEl.classList.add('active');
        
        // 1. Tạo Tab Id mới (Check xem coin đã có chưa)
        const existIdx = tabs.findIndex(t => t.symbol === symbol && t.style === style);
        if (existIdx !== -1) {
          removeTab(tabs[existIdx].id);
        }
        if (tabs.length >= MAX_TABS) {
          removeTab(tabs[0].id);
        }
        
        const tabId = Date.now().toString();
        const tabObj = { id: tabId, symbol: symbol, style: style, ws: null };
        tabs.push(tabObj);

        // 2. Add Tab Button
        const tBar = document.getElementById('workspace-tabs');
        const tBtn = document.createElement('div');
        tBtn.className = 'workspace-tab';
        tBtn.id = 'tab-btn-' + tabId;
        tBtn.innerHTML = `<span>${symbol} <span style="color:var(--text-muted); font-size: 0.75rem;">(${style})</span></span><span class="workspace-tab-close">×</span>`;
        tBtn.onclick = (e) => {
          if (e.target.classList.contains('workspace-tab-close')) {
            removeTab(tabId);
          } else {
            switchTab(tabId);
          }
        };
        tBar.appendChild(tBtn);

        // 3. Add Content Area
        const tContent = document.createElement('div');
        tContent.className = 'workspace-content';
        tContent.id = 'tab-content-' + tabId;
        
        const template = document.getElementById('card-template');
        const cardClone = template.content.cloneNode(true);
        tContent.appendChild(cardClone);
        document.getElementById('workspace-contents').appendChild(tContent);

        // 4. Fill Data
        renderSignal(data, symbol, tContent);
        if (data.market_data) renderMarketData(data.market_data, tContent);
        
        // 5. Render Chart & WebSocket (pass the tabObj to store ws)
        renderChart(symbol, data, tContent, tabObj);
        
        // 6. Switch
        switchTab(tabId);
        resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' });

      } catch (err) {
        const msg = err.message.includes('fetch') ? 'Cannot connect to server. Make sure the backend is running.' : err.message;
        showError('⚠️  ' + msg);
      }
    }

    // ── TradingView Chart ──────────────────────────────────
    async function renderChart(symbol, data, cardEl, tabObj) {
      const container = cardEl.querySelector('.dyn-chart-container');
      container.innerHTML = '<div class="chart-debug" style="padding:10px; font-family:var(--mono); font-size:12px; color:var(--text-secondary); height:100%; overflow:auto; background:#111;">[SYSTEM] Chart Engine Initializing...<br></div>';
      const debugDiv = container.querySelector('.chart-debug');
      const log = (msg) => { debugDiv.innerHTML += msg + '<br>'; };

      try {
        await new Promise(r => setTimeout(r, 100)); // reflow
        const chart = LightweightCharts.createChart(container, {
          width: container.clientWidth, height: container.clientHeight,
          layout: { background: { type: 'solid', color: 'transparent' }, textColor: '#9aaabb' },
          grid: { vertLines: { color: 'rgba(46, 56, 71, 0.4)' }, horzLines: { color: 'rgba(46, 56, 71, 0.4)' } },
          timeScale: { timeVisible: true, secondsVisible: false }
        });
        const series = chart.addCandlestickSeries({ upColor: '#00c896', downColor: '#f6465d', borderVisible: false, wickUpColor: '#00c896', wickDownColor: '#f6465d' });

        const res = await fetch(`https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=1h&limit=200`);
        const klines = await res.json();
        const chartData = klines.map(k => ({ time: Math.floor(parseInt(k[0]) / 1000), open: parseFloat(k[1]), high: parseFloat(k[2]), low: parseFloat(k[3]), close: parseFloat(k[4]) }));
        series.setData(chartData);

        if (data.direction && data.direction !== 'HOLD') {
          if (data.entry_price != null) series.createPriceLine({ price: parseFloat(data.entry_price), color: '#f0b90b', lineWidth: 2, lineStyle: 2, axisLabelVisible: true, title: 'ENTRY' });
          if (data.stop_loss != null) series.createPriceLine({ price: parseFloat(data.stop_loss), color: '#f6465d', lineWidth: 2, lineStyle: 2, axisLabelVisible: true, title: 'SL' });
          if (data.take_profit != null) series.createPriceLine({ price: parseFloat(data.take_profit), color: '#00c896', lineWidth: 2, lineStyle: 2, axisLabelVisible: true, title: 'TP' });
        }
        chart.timeScale().fitContent();

        const ws = new WebSocket(`wss://stream.binance.com:9443/ws/${symbol.toLowerCase()}@kline_1h`);
        tabObj.ws = ws;
        ws.onmessage = (event) => {
          const msg = JSON.parse(event.data);
          const k = msg.k;
          series.update({ time: Math.floor(k.t / 1000), open: parseFloat(k.o), high: parseFloat(k.h), low: parseFloat(k.l), close: parseFloat(k.c) });
        };

        debugDiv.style.display = 'none';
      } catch (e) {
        log(`<b style="color:red">[ERROR] ${e.toString()}</b><br><span style="color:#a55">${e.stack || ''}</span>`);
      }
    }

    // ── Market Dashboard ───────────────────────────────────"""

text = js_pattern.sub(js_injection, text)

# Event listeners cleanup if necessary (it's fine)
# Clean up `document.getElementById('tf-tabs').addEventListener` since it's removed and now handled per card.
text = re.sub(r"    // ── Timeframe Tab Switching ────────────────────────────.*?    // ── Main Analyze Function", "    // ── Main Analyze Function", text, flags=re.DOTALL)

with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Refactored successfully")
