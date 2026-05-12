import { useEffect, useState } from 'react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { analyticsAPI } from '../services/api';

function AnalyticsPage() {
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    analyticsAPI
      .getDashboard()
      .then((response) => setDashboard(response.data))
      .catch(() => setError('Analytics will appear after the backend is running and trades are recorded.'));
  }, []);

  const summary = dashboard?.summary;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Behavioral Analytics</h1>
        <p className="mt-1 text-sm text-slate-600">Performance, drawdown, setup quality, and emotional trading patterns.</p>
      </div>

      {error && <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">{error}</div>}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric label="Win rate" value={summary ? `${summary.win_rate}%` : '--'} />
        <Metric label="Profit factor" value={summary?.profit_factor ?? '--'} />
        <Metric label="Expectancy" value={summary ? `$${summary.expectancy}` : '--'} />
        <Metric label="Max drawdown" value={summary ? `$${summary.max_drawdown}` : '--'} />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <section className="rounded-lg border border-slate-200 bg-white p-4 xl:col-span-2">
          <h2 className="text-sm font-semibold">Equity Curve</h2>
          <div className="mt-4 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={dashboard?.equity_curve || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="trade_id" />
                <YAxis />
                <Tooltip />
                <Area dataKey="cumulative_pnl" stroke="#0f172a" fill="#99f6e4" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="text-sm font-semibold">Strategy PnL</h2>
          <div className="mt-4 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dashboard?.strategy_breakdown || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="key" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="total_pnl" fill="#2563eb" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="text-xs font-medium uppercase text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </div>
  );
}

export default AnalyticsPage;
