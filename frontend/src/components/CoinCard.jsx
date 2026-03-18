import { useState } from 'react';

function fmt(n) {
  if (n === null || n === undefined) return '—';
  if (n >= 1e9) return '$' + (n / 1e9).toFixed(2) + 'B';
  if (n >= 1e6) return '$' + (n / 1e6).toFixed(2) + 'M';
  if (n >= 1000) return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  return '$' + n.toFixed(n < 0.01 ? 6 : 4);
}

function pct(n) {
  if (n === null || n === undefined) return '—';
  const sign = n > 0 ? '+' : '';
  return sign + n.toFixed(2) + '%';
}

export default function CoinCard({ coin, index }) {
  const [imgError, setImgError] = useState(false);
  const popping = coin.is_popping;

  return (
    <div
      className={`coin-card ${popping ? 'popping' : 'dropping'}`}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      {/* Glow accent */}
      <div className="card-glow" />

      {/* Header */}
      <div className="card-header">
        <div className="coin-identity">
          {!imgError ? (
            <img
              src={coin.logo_url}
              alt={coin.symbol}
              className="coin-logo"
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="coin-logo-fallback">{coin.symbol[0]}</div>
          )}
          <div>
            <div className="coin-symbol">{coin.symbol}</div>
            <div className="coin-name">{coin.name}</div>
          </div>
        </div>
        <div className={`status-badge ${popping ? 'badge-pop' : 'badge-drop'}`}>
          {popping ? (
            <><span className="badge-icon">▲</span> POPPING</>
          ) : (
            <><span className="badge-icon">▼</span> BET AGAINST</>
          )}
        </div>
      </div>

      {/* Price */}
      <div className="price-section">
        <div className="current-price">{fmt(coin.current_price)}</div>
        <div className={`change-pill ${popping ? 'change-up' : 'change-down'}`}>
          {pct(coin.change_30d)} <span className="change-label">30d</span>
        </div>
      </div>

      {/* Stats row */}
      <div className="stats-row">
        <div className="stat">
          <span className="stat-label">30d ago</span>
          <span className="stat-value">{fmt(coin.old_price)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">24h</span>
          <span className={`stat-value ${coin.change_24h > 0 ? 'up' : 'down'}`}>
            {pct(coin.change_24h)}
          </span>
        </div>
        <div className="stat">
          <span className="stat-label">7d</span>
          <span className={`stat-value ${coin.change_7d > 0 ? 'up' : 'down'}`}>
            {pct(coin.change_7d)}
          </span>
        </div>
      </div>

      {/* Market cap */}
      {coin.market_cap && (
        <div className="mktcap">
          <span className="stat-label">Mkt Cap</span>
          <span className="stat-value">{fmt(coin.market_cap)}</span>
        </div>
      )}

      {/* Trend line decoration */}
      <div className={`card-footer-line ${popping ? 'line-up' : 'line-down'}`} />
    </div>
  );
}
