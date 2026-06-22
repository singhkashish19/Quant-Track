import { useEffect, useMemo, useState } from 'react';

import { LoadingState, StatCard, TradeTable } from '../components';
import { tradesAPI } from '../services/api';

function TradesPage() {
  const defaultTimestamp = useMemo(() => new Date().toISOString().slice(0, 16), []);
  const [trades, setTrades] = useState([]);
  const [stats, setStats] = useState(null);
  const [form, setForm] = useState({
    symbol: 'XAUUSD',
    asset_type: 'COMMODITIES',
    direction: 'BUY',
    entry_price: 2350,
    exit_price: 2362,
    stop_loss: 2344,
    take_profit: 2368,
    lot_size: 1,
    strategy: 'breakout',
    timeframe: '15M',
    market_condition: 'trending',
    session: 'FOREX',
    emotional_state: 'DISCIPLINED',
    confidence_level: 7,
    execution_quality: 'good',
    slippage: 0.1,
    trade_duration: 45,
    entry_timestamp: defaultTimestamp,
    exit_timestamp: defaultTimestamp,
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadTrades = async () => {
    setLoading(true);
    setError('');

    try {
      const [tradesResponse, statsResponse] = await Promise.all([
        tradesAPI.list({ limit: 20 }),
        tradesAPI.getStatistics(),
      ]);
      setTrades(tradesResponse.data.trades || []);
      setStats(statsResponse.data);
    } catch (fetchError) {
      setError(fetchError.response?.data?.detail || 'Unable to load trades.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrades();
  }, []);

  const handleChange = (event) => {
    const { name, value, type } = event.target;
    setForm((previous) => ({ ...previous, [name]: type === 'number' ? Number(value) : value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage('');
    const entryTimestamp = new Date(form.entry_timestamp);
    const exitTimestamp = form.exit_price
      ? new Date(form.exit_timestamp || new Date(entryTimestamp.getTime() + 60_000).toISOString())
      : null;

    const payload = {
      ...form,
      entry_timestamp: entryTimestamp.toISOString(),
      exit_timestamp: exitTimestamp ? exitTimestamp.toISOString() : null,
    };
    try {
      await tradesAPI.create(payload);
      setMessage('Trade recorded and analytics will update automatically.');
      loadTrades();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Could not save trade.');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Trade Management</h1>
        <p className="mt-1 text-sm text-slate-600">Record trades with market, execution, risk, and behavioral context.</p>
      </div>

      {loading ? (
        <LoadingState label="Loading trades and analytics..." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Total trades" value={stats?.total_trades ?? '--'} />
          <StatCard label="Win rate" value={stats ? `${stats.win_rate}%` : '--'} />
          <StatCard label="Total PnL" value={stats ? `$${Number(stats.total_pnl).toFixed(2)}` : '--'} />
          <StatCard label="Profit factor" value={stats?.profit_factor ?? '--'} />
        </div>
      )}
      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="text-sm font-semibold">Add Trade</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Input label="Symbol" name="symbol" value={form.symbol} onChange={handleChange} />
          <Select label="Asset" name="asset_type" value={form.asset_type} onChange={handleChange} options={['FOREX', 'CRYPTO', 'INDICES', 'COMMODITIES', 'EQUITIES']} />
          <Select label="Direction" name="direction" value={form.direction} onChange={handleChange} options={['BUY', 'SELL', 'LONG', 'SHORT']} />
          <Input label="Entry" name="entry_price" type="number" value={form.entry_price} onChange={handleChange} />
          <Input label="Exit" name="exit_price" type="number" value={form.exit_price} onChange={handleChange} />
          <Input label="Stop loss" name="stop_loss" type="number" value={form.stop_loss} onChange={handleChange} />
          <Input label="Take profit" name="take_profit" type="number" value={form.take_profit} onChange={handleChange} />
          <Input label="Lot size" name="lot_size" type="number" value={form.lot_size} onChange={handleChange} />
          <Input label="Strategy" name="strategy" value={form.strategy} onChange={handleChange} />
          <Select label="Timeframe" name="timeframe" value={form.timeframe} onChange={handleChange} options={['5M', '15M', '1H', '4H', '1D']} />
          <Select label="Session" name="session" value={form.session} onChange={handleChange} options={['FOREX', 'NYSE', 'CRYPTO', 'NSE']} />
          <Select label="Emotion" name="emotional_state" value={form.emotional_state} onChange={handleChange} options={['DISCIPLINED', 'FOMO', 'FEARFUL', 'GREEDY', 'IMPULSIVE', 'REVENGE', 'CONFIDENT']} />
          <Input label="Confidence" name="confidence_level" type="number" value={form.confidence_level} onChange={handleChange} />
          <Input label="Slippage" name="slippage" type="number" value={form.slippage} onChange={handleChange} />
          <Input label="Duration min" name="trade_duration" type="number" value={form.trade_duration} onChange={handleChange} />
          <Input label="Entry time" name="entry_timestamp" type="datetime-local" value={form.entry_timestamp} onChange={handleChange} />
          <Input label="Exit time" name="exit_timestamp" type="datetime-local" value={form.exit_timestamp} onChange={handleChange} />
        </div>
        <div className="mt-4 flex items-center gap-3">
          <button className="btn-primary" type="submit">Save trade</button>
          {message && <span className="text-sm text-slate-600">{message}</span>}
        </div>
      </form>

      <TradeTable trades={trades} />
    </div>
  );
}

function Input({ label, ...props }) {
  return (
    <label className="grid gap-1 text-xs font-medium text-slate-600">
      {label}
      <input className="input-field" {...props} />
    </label>
  );
}

function Select({ label, options, ...props }) {
  return (
    <label className="grid gap-1 text-xs font-medium text-slate-600">
      {label}
      <select className="input-field" {...props}>
        {options.map((option) => (
          <option key={option} value={option}>{option}</option>
        ))}
      </select>
    </label>
  );
}

export default TradesPage;
