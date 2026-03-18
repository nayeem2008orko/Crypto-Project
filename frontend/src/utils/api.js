const BASE = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchCoins(filter = 'all') {
  const res = await fetch(`${BASE}/api/coins?filter=${filter}`);
  if (res.status === 429) {
    const data = await res.json();
    throw new Error(data.message || 'Rate limit exceeded. Please wait a moment.');
  }
  if (!res.ok) throw new Error('Failed to fetch coins');
  return res.json();
}

export async function fetchChartData() {
  const res = await fetch(`${BASE}/api/coins/chart`);
  if (res.status === 429) {
    const data = await res.json();
    throw new Error(data.message || 'Rate limit exceeded. Please wait a moment.');
  }
  if (!res.ok) throw new Error('Failed to fetch chart data');
  return res.json();
}
