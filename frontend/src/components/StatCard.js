function StatCard({ label, value, detail }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-slate-950">{value}</div>
      {detail && <div className="mt-1 text-sm text-slate-500">{detail}</div>}
    </div>
  );
}

export default StatCard;
