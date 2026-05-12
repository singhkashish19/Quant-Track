function LoadingState({ label = 'Loading data...' }) {
  return <div className="rounded-md border border-slate-200 bg-white p-4 text-sm text-slate-600">{label}</div>;
}

export default LoadingState;
