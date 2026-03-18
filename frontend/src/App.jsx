import { useState } from 'react';
import CoinCard from './components/CoinCard';
import CryptoBarChart from './components/CryptoBarChart';
import { useCoins } from './hooks/useCoins';
import './index.css';

const FILTERS = [
  { value: 'all', label: 'All Currencies (Randomised)', icon: '⬡' },
  { value: 'increasing', label: 'Popping Only ▲', icon: '▲' },
  { value: 'decreasing', label: 'Going Down Only ▼', icon: '▼' },
];

export default function App() {
  const {
    coins, chartData, filter, loading, chartLoading,
    error, lastUpdated, changeFilter, refresh, loadChart,
  } = useCoins();

  const [showChart, setShowChart] = useState(false);

  const handleChartToggle = () => {
    if (!showChart && chartData.length === 0) loadChart();
    setShowChart(v => !v);
  };

  return (
    <div className="app">
      {/* ── Noise texture overlay ── */}
      <div className="noise-overlay" />

      {/* ── Header ── */}
      <header className="header">
        <div className="logo">
          <div className="logo-mark">
            <span className="logo-pulse" />
            CP
          </div>
          <div className="logo-text">
            <span className="logo-main">CRYPTO</span>
            <span className="logo-sub">POINT</span>
          </div>
        </div>

        <nav className="nav">
          <span className="nav-item active">Dashboard</span>
          <span className="nav-item">Markets</span>
          <span className="nav-item">Portfolio</span>
        </nav>

        <div className="header-right">
          <div className="status-dot">
            <span className={`dot ${loading ? 'dot-loading' : 'dot-live'}`} />
            <span className="status-text">{loading ? 'Fetching…' : 'Live'}</span>
          </div>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="main">
        {/* ── Toolbar ── */}
        <div className="toolbar">
          <div className="toolbar-left">
            <h1 className="page-title">
              <span className="title-accent">CRYPTO PULSE</span>
              <span className="title-divider">|</span>
              REAL-TIME TRACKER
            </h1>
            {lastUpdated && (
              <p className="last-updated">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </p>
            )}
          </div>

          <div className="toolbar-right">
            <div className="filter-wrap">
              <label className="filter-label">Filter:</label>
              <select
                className="filter-select"
                value={filter}
                onChange={e => changeFilter(e.target.value)}
              >
                {FILTERS.map(f => (
                  <option key={f.value} value={f.value}>{f.label}</option>
                ))}
              </select>
            </div>

            <button className="btn-refresh" onClick={refresh} disabled={loading}>
              <span className={loading ? 'spin' : ''}>⟳</span>
              {loading ? 'Loading' : 'Refresh'}
            </button>
          </div>
        </div>

        {/* ── Error banner ── */}
        {error && (
          <div className="error-banner">
            <span>⚠</span> {error}
          </div>
        )}

        {/* ── Coin grid ── */}
        {loading && coins.length === 0 ? (
          <div className="loading-grid">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="coin-card-skeleton" style={{ animationDelay: `${i * 80}ms` }} />
            ))}
          </div>
        ) : coins.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">◎</div>
            <p>No coins matched the current filter.</p>
          </div>
        ) : (
          <div className="coin-grid">
            {coins.map((coin, i) => (
              <CoinCard key={coin.id || coin.symbol} coin={coin} index={i} />
            ))}
          </div>
        )}

        {/* ── Chart toggle ── */}
        <div className="chart-section">
          <button className="btn-chart" onClick={handleChartToggle}>
            <span className="chart-btn-icon">▦</span>
            {showChart ? 'HIDE' : 'VIEW'} PERCENTAGE CHANGE DATA VISUALISATION
          </button>

          {showChart && (
            <CryptoBarChart data={chartData} loading={chartLoading} />
          )}
        </div>
      </main>

      {/* ── Footer ── */}
      <footer className="footer">
        <span className="footer-dot" />
        Powered by CoinMarketCap API
        <span className="footer-sep">·</span>
        Data refreshes every 5 minutes
        <span className="footer-sep">·</span>
        Crypto Point © 2025
      </footer>
    </div>
  );
}
