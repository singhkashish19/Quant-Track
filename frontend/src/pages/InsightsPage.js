import { useEffect, useState } from 'react';

import { StatCard } from '../components';
import { mlAPI } from '../services/api';

function InsightsPage() {
  const [performance, setPerformance] = useState(null);
  const [features, setFeatures] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [message, setMessage] = useState('');

  const load = () => {
    Promise.allSettled([mlAPI.getModelPerformance(), mlAPI.getFeatures()]).then((results) => {
      if (results[0].status === 'fulfilled') setPerformance(results[0].value.data);
      if (results[1].status === 'fulfilled') setFeatures(results[1].value.data.top_features || []);
    });
  };

  useEffect(() => {
    load();
  }, []);

  const handlePredict = async () => {
    const response = await mlAPI.getPredictions({});
    setPrediction(response.data);
  };

  const handleRetrain = async () => {
    setMessage('Retraining models...');
    const response = await mlAPI.retrain();
    setPerformance(response.data.performance);
    setMessage(response.data.message);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">AI Insights</h1>
          <p className="mt-1 text-sm text-slate-600">Profitability prediction, behavioral risk detection, and setup clustering.</p>
        </div>
        <div className="flex gap-2">
          <button type="button" className="btn-secondary" onClick={handleRetrain}>Retrain</button>
          <button type="button" className="btn-primary" onClick={handlePredict}>Predict latest trade</button>
        </div>
      </div>

      {message && <div className="rounded-md border border-slate-200 bg-white p-3 text-sm text-slate-600">{message}</div>}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Profit model F1" value={performance?.profitability_model?.f1_score ?? '--'} />
        <StatCard label="Risk model F1" value={performance?.risk_model?.f1_score ?? '--'} />
        <StatCard label="Training rows" value={performance?.training_rows ?? '--'} />
        <StatCard label="Data source" value={performance?.data_source || '--'} />
      </div>

      {prediction && (
        <section className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="text-sm font-semibold">Latest Prediction</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Profit probability" value={`${Math.round(prediction.profitability_probability * 100)}%`} />
            <StatCard label="Risk score" value={`${Math.round(prediction.risk_score * 100)}%`} />
            <StatCard label="Pattern cluster" value={prediction.pattern_cluster} />
            <StatCard label="Confidence" value={`${Math.round(prediction.confidence_score * 100)}%`} />
          </div>
          <div className="mt-4 space-y-2">
            {prediction.recommendations.map((item) => (
              <div key={item} className="rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-700">{item}</div>
            ))}
          </div>
        </section>
      )}

      <section className="rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="text-sm font-semibold">Top Risk Features</h2>
        <div className="mt-4 grid gap-2">
          {features.map((item) => (
            <div key={item.feature} className="grid grid-cols-[1fr_auto] items-center gap-3 text-sm">
              <span className="truncate text-slate-600">{item.feature}</span>
              <span className="font-medium">{item.importance}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default InsightsPage;
