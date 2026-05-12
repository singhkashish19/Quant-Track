import { useEffect, useState } from 'react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { LoadingState, StatCard, TradeTable } from '../components';
import { analyticsAPI, mlAPI, tradesAPI } from '../services/api';

function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [trades, setTrades] = useState([]);
  const [model, setModel] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      analyticsAPI.getDashboard(),
      tradesAPI.list({ limit: 5 }),
      mlAPI.getModelPerformance(),
    ]).then((results) => {
      if (results[0].status === 'fulfilled') setDashboard(results[0].value.data);
      if (results[1].status === 'fulfilled') setTrades(results[1].value.data.trades || []);
      if (results[2].status === 'fulfilled') setModel(results[2].value.data);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingState label="Preparing your trading dashboard..." />;

  const summary = dashboard?.summary || {};

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Trading Command Center</h1>
        <p className="mt-1 text-sm text-slate-600">A compact view of performance, behavior, and AI model readiness.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Win rate" value={`${summary.win_rate || 0}%`} detail={`${summary.closed_trades || 0} closed trades`} />
        <StatCard label="Profit factor" value={summary.profit_factor || 0} detail="Gross profit vs gross loss" />
        <StatCard label="Expectancy" value={`$${summary.expectancy || 0}`} detail="Average expected trade outcome" />
        <StatCard label="AI training rows" value={model?.training_rows || '--'} detail={model?.data_source || 'Model pending'} />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <section className="rounded-lg border border-slate-200 bg-white p-4 xl:col-span-2">
          <h2 className="text-sm font-semibold">Equity Curve</h2>
          <div className="mt-4 h-72">
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
          <h2 className="text-sm font-semibold">Behavior Flags</h2>
          <div className="mt-4 space-y-3 text-sm">
            <Flag label="Overtrading" value={summary.behavioral_flags?.overtrading || 0} />
            <Flag label="Revenge trades" value={summary.behavioral_flags?.revenge_trading || 0} />
            <Flag label="Emotional trades" value={summary.behavioral_flags?.emotional_trades || 0} />
          </div>
        </section>
      </div>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold">Recent Trades</h2>
        </div>
        <TradeTable trades={trades} />
      </section>
    </div>
  );
}

function Flag({ label, value }) {
  return (
    <div className="flex items-center justify-between rounded-md bg-slate-50 px-3 py-2">
      <span className="text-slate-600">{label}</span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}

export default Dashboard;
