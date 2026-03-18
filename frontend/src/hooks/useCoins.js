import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchCoins, fetchChartData } from '../utils/api';

// Minimum ms between user-triggered refreshes (guards against button-spam)
const MANUAL_REFRESH_COOLDOWN = 8000;

export function useCoins() {
  const [coins, setCoins] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [chartLoading, setChartLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const lastRefreshRef = useRef(0);

  const loadCoins = useCallback(async (f = filter, isManual = false) => {
    if (isManual) {
      const now = Date.now();
      if (now - lastRefreshRef.current < MANUAL_REFRESH_COOLDOWN) {
        setError(`Please wait ${Math.ceil((MANUAL_REFRESH_COOLDOWN - (now - lastRefreshRef.current)) / 1000)}s before refreshing again.`);
        return;
      }
      lastRefreshRef.current = now;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCoins(f);
      setCoins(data.coins);
      setLastUpdated(new Date());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  const loadChart = useCallback(async () => {
    setChartLoading(true);
    try {
      const data = await fetchChartData();
      setChartData(data.chart);
    } catch (e) {
      setError(e.message);
    } finally {
      setChartLoading(false);
    }
  }, []);

  const changeFilter = useCallback((f) => {
    setFilter(f);
    loadCoins(f);
  }, [loadCoins]);

  // Initial load + auto-refresh every 5 minutes
  useEffect(() => {
    loadCoins(filter);
    const interval = setInterval(() => loadCoins(filter), 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return {
    coins, chartData, filter, loading, chartLoading,
    error, lastUpdated,
    changeFilter,
    refresh: () => loadCoins(filter, true),
    loadChart,
  };
}
