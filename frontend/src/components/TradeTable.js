function TradeTable({ trades = [] }) {
  if (!trades.length) {
    return (
      <div className="rounded-md border border-slate-200 bg-white p-4 text-sm text-slate-600">
        No trades recorded yet. Add your first trade to see performance, PnL, and behavior summaries.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">Symbol</th>
              <th className="px-4 py-3">Direction</th>
              <th className="px-4 py-3">Strategy</th>
              <th className="px-4 py-3">Emotion</th>
              <th className="px-4 py-3">PnL</th>
              <th className="px-4 py-3">Result</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {trades.map((trade) => (
              <tr key={trade.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-medium whitespace-nowrap">{trade.symbol}</td>
                <td className="px-4 py-3 whitespace-nowrap">{trade.direction}</td>
                <td className="px-4 py-3 whitespace-nowrap">{trade.strategy || 'Unspecified'}</td>
                <td className="px-4 py-3 whitespace-nowrap">{trade.emotional_state || 'None'}</td>
                <td className={`px-4 py-3 font-medium whitespace-nowrap ${(trade.pnl || 0) >= 0 ? 'text-emerald-700' : 'text-rose-700'}`}>
                  {trade.pnl == null ? 'Open' : `$${Number(trade.pnl).toFixed(2)}`}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">{trade.result || (trade.is_open ? 'OPEN' : 'BREAKEVEN')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TradeTable;
