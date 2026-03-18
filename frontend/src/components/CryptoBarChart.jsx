import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Cell,
} from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <div className="tt-name">{d.name} <span className="tt-sym">({d.symbol})</span></div>
      <div className={`tt-val ${d.change_30d >= 0 ? 'up' : 'down'}`}>
        30d: {d.change_30d > 0 ? '+' : ''}{d.change_30d}%
      </div>
      {d.change_7d != null && (
        <div className={`tt-val ${d.change_7d >= 0 ? 'up' : 'down'}`}>
          7d: {d.change_7d > 0 ? '+' : ''}{d.change_7d}%
        </div>
      )}
      {d.change_24h != null && (
        <div className={`tt-val ${d.change_24h >= 0 ? 'up' : 'down'}`}>
          24h: {d.change_24h > 0 ? '+' : ''}{d.change_24h}%
        </div>
      )}
    </div>
  );
};

export default function CryptoBarChart({ data, loading }) {
  if (loading) {
    return (
      <div className="chart-placeholder">
        <div className="spinner" />
        <p>Loading chart data…</p>
      </div>
    );
  }
  if (!data.length) return null;

  return (
    <div className="chart-wrap">
      <div className="chart-title">
        <span className="chart-icon">▦</span>
        30-DAY PERCENTAGE CHANGE — ALL TRACKED COINS
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 20 }} barCategoryGap="25%">
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
          <XAxis
            dataKey="symbol"
            tick={{ fill: '#8892a4', fontSize: 11, fontFamily: 'inherit' }}
            axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
            tickLine={false}
          />
          <YAxis
            tickFormatter={v => `${v > 0 ? '+' : ''}${v}%`}
            tick={{ fill: '#8892a4', fontSize: 11, fontFamily: 'inherit' }}
            axisLine={false}
            tickLine={false}
            width={58}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
          <ReferenceLine y={0} stroke="rgba(255,255,255,0.2)" strokeWidth={1} />
          <Bar dataKey="change_30d" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.change_30d >= 0 ? '#00e5a0' : '#ff4560'}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
