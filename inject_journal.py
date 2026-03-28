import re

with open("frontend/index.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. CSS
css_injection = """
    /* ── Journal Modal Styles ── */
    .modal-overlay {
      position: fixed; top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(11, 14, 20, 0.85); backdrop-filter: blur(4px);
      display: none; justify-content: center; align-items: center; z-index: 1000;
      opacity: 0; transition: opacity 0.2s;
    }
    .modal-overlay.active { display: flex; opacity: 1; }
    .modal-overlay.active .modal-content { transform: scale(1); opacity: 1; }
    
    .modal-content {
      background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
      width: 95%; max-width: 900px; max-height: 85vh; display: flex; flex-direction: column; overflow: hidden;
      box-shadow: 0 10px 40px rgba(0,0,0,0.5); transform: scale(0.95); opacity: 0; transition: all 0.2s;
    }
    .modal-header { padding: 16px 24px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
    .modal-header h2 { font-size: 1.2rem; font-weight: 700; color: var(--text-primary); margin: 0; }
    .close-modal { font-size: 1.5rem; color: var(--text-muted); cursor: pointer; line-height: 1; }
    .close-modal:hover { color: var(--short); }
    .modal-body { padding: 24px; overflow-y: auto; flex: 1; }
    
    .journal-stats { display: flex; gap: 16px; margin-bottom: 24px; }
    .stat-box { flex: 1; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 16px; text-align: center; }
    .stat-label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
    .stat-value { font-size: 1.8rem; font-weight: 800; color: var(--accent); font-family: var(--mono); }
    
    .journal-table { width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: 0.85rem; }
    .journal-table th, .journal-table td { padding: 12px; border-bottom: 1px solid var(--border-light); text-align: left; }
    .journal-table th { color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; font-family: Inter, sans-serif; font-size: 0.75rem; border-bottom-color: var(--border); position: sticky; top: -24px; background: var(--bg-card); }
    .journal-table tr:hover { background: rgba(255,255,255,0.02); }
    
    .status-badge { padding: 4px 8px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; }
    .status-PENDING { background: rgba(240, 185, 11, 0.15); color: var(--hold); border: 1px solid rgba(240, 185, 11, 0.3); }
    .status-WIN { background: rgba(0, 200, 150, 0.15); color: var(--long); border: 1px solid rgba(0, 200, 150, 0.3); }
    .status-LOSS { background: rgba(246, 70, 93, 0.15); color: var(--short); border: 1px solid rgba(246, 70, 93, 0.3); }
  </style>
"""
text = text.replace("  </style>", css_injection, 1)


# 2. Header and Modal Body 
header_pattern = re.compile(r'    <span class="header-badge">AI-Powered · Binance Futures</span>\n  </header>')
header_injection = """    <div style="display:flex; gap:12px; align-items:center;">
      <button id="journal-btn" class="header-badge" style="cursor: pointer; background: var(--bg-card); border-color: var(--border); color: var(--text-secondary); transition: all 0.2s;">📚 Trade Journal</button>
      <span class="header-badge">AI-Powered · Binance Futures</span>
    </div>
  </header>

  <!-- Trade Journal Modal -->
  <div id="journal-modal" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h2>📚 Trade Journal</h2>
        <span class="close-modal" id="close-journal">&times;</span>
      </div>
      <div class="modal-body">
        <div class="journal-stats">
          <div class="stat-box"><div class="stat-label">Win Rate</div><div class="stat-value" id="journal-winrate">--%</div></div>
          <div class="stat-box"><div class="stat-label">Closed Trades</div><div class="stat-value" id="journal-total" style="color:var(--text-primary)">--</div></div>
        </div>
        <table class="journal-table">
          <thead>
            <tr>
              <th>Date</th><th>Pair</th><th>Dir</th><th>Entry</th><th>Strategy</th><th>Score</th><th>Status</th>
            </tr>
          </thead>
          <tbody id="journal-tbody">
            <tr><td colspan="7" style="text-align:center;">Loading...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>"""
text = header_pattern.sub(header_injection, text)


# 3. Request Notification at JS DOM Init, and handle journal logic
js_additions = """
    // ── Phase 3: Push Notifications & Trade Journal ────
    if (Notification && Notification.permission !== "granted" && Notification.permission !== "denied") {
      Notification.requestPermission();
    }

    const modal = document.getElementById('journal-modal');
    const closeBtn = document.getElementById('close-journal');
    
    document.getElementById('journal-btn').addEventListener('click', async () => {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
      
      const tbody = document.getElementById('journal-tbody');
      tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 40px; color:var(--text-muted)">Loading historical signals...</td></tr>';
      
      try {
        const r = await fetch('/api/journal');
        const d = await r.json();
        
        document.getElementById('journal-winrate').textContent = d.win_rate + '%';
        if (d.win_rate >= 50) document.getElementById('journal-winrate').style.color = 'var(--long)';
        else document.getElementById('journal-winrate').style.color = 'var(--short)';
        
        document.getElementById('journal-total').textContent = d.total_closed;
        
        if (d.signals.length === 0) {
          tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No trades recorded yet.</td></tr>';
          return;
        }
        
        tbody.innerHTML = d.signals.map(s => {
          const date = new Date(s.timestamp).toLocaleString();
          const dirColor = s.direction === 'LONG' ? 'var(--long)' : s.direction === 'SHORT' ? 'var(--short)' : 'var(--hold)';
          return `<tr>
            <td style="color:var(--text-muted); font-size:0.75rem">${date}</td>
            <td style="font-weight:700; color:var(--text-primary)">${s.symbol}</td>
            <td style="color:${dirColor}; font-weight:700">${s.direction}</td>
            <td>${fmtPrice(s.entry_price)}</td>
            <td>${s.strategy}</td>
            <td style="color:${s.confidence_score >= 70 ? 'var(--accent)' : 'var(--text-muted)'}">${s.confidence_score}%</td>
            <td><span class="status-badge status-${s.status}">${s.status}</span></td>
          </tr>`;
        }).join('');
      } catch(e) {
         tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--short)">Error fetching history</td></tr>';
      }
    });

    closeBtn.addEventListener('click', () => {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    });
    modal.addEventListener('click', e => {
      if (e.target === modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
      }
    });

    // ── Elements ───────────────────────────────────────────"""
text = text.replace("    // ── Elements ───────────────────────────────────────────", js_additions)


# 4. Show Notification at end of analyze
notification_call = """
        // 7. Show Push Notification for High Conviction Signals
        if (Notification && Notification.permission === 'granted' && data.direction !== 'HOLD' && data.confidence_score >= 70) {
          new Notification(`A.I ALERT: ${symbol} ${data.direction}`, {
            body: `[${style}] Entry: ${fmtPrice(data.entry_price)} | SL: ${fmtPrice(data.stop_loss)} | TP: ${fmtPrice(data.take_profit)}\\n⚡ Confidence: ${data.confidence_score}%`,
          });
        }
        
        // 8. Wait for chart drawing..."""
text = text.replace("        // 6. Switch", notification_call + "\n        // 6. Switch")

with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Injected Trade Journal & Push Notifications.")
