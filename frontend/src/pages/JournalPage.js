import { useEffect, useState } from 'react';

import { StatCard } from '../components';
import { journalsAPI } from '../services/api';

function JournalPage() {
  const [notes, setNotes] = useState('Entered too early because price moved aggressively.');
  const [emotionalState, setEmotionalState] = useState('FOMO');
  const [journals, setJournals] = useState([]);
  const [summary, setSummary] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [message, setMessage] = useState('');

  const load = () => {
    Promise.allSettled([journalsAPI.list(), journalsAPI.getSummary()]).then((results) => {
      if (results[0].status === 'fulfilled') setJournals(results[0].value.data || []);
      if (results[1].status === 'fulfilled') setSummary(results[1].value.data);
    });
  };

  useEffect(load, []);

  const handleAnalyze = async () => {
    const response = await journalsAPI.create({ notes, emotional_state: emotionalState });
    setAnalysis(response.data.analysis);
    setMessage('Journal saved and analyzed.');
    load();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Behavioral Journal</h1>
        <p className="mt-1 text-sm text-slate-600">Turn trading notes into sentiment, emotion, and behavioral tags.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Journal entries" value={summary?.total_journals ?? 0} />
        <StatCard label="Avg sentiment" value={summary?.average_sentiment ?? 0} />
        <StatCard label="FOMO events" value={summary?.fomo_events ?? 0} />
        <StatCard label="Revenge events" value={summary?.revenge_events ?? 0} />
      </div>

      <section className="rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="text-sm font-semibold">New Journal Entry</h2>
        <div className="mt-4 grid gap-3">
          <textarea
            className="input-field min-h-32"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
          />
          <select className="input-field max-w-xs" value={emotionalState} onChange={(event) => setEmotionalState(event.target.value)}>
            {['DISCIPLINED', 'FOMO', 'FEARFUL', 'GREEDY', 'IMPULSIVE', 'REVENGE', 'CONFIDENT'].map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          <div className="flex items-center gap-3">
            <button type="button" className="btn-primary" onClick={handleAnalyze}>Save and analyze</button>
            {message && <span className="text-sm text-slate-600">{message}</span>}
          </div>
        </div>
      </section>

      {analysis && (
        <section className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="text-sm font-semibold">Latest NLP Analysis</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Sentiment" value={analysis.sentiment_score} />
            <StatCard label="FOMO score" value={analysis.fomo_score} />
            <StatCard label="Revenge score" value={analysis.revenge_trade_score} />
            <StatCard label="Impulsive score" value={analysis.impulsive_score} />
          </div>
          <div className="mt-4 text-sm text-slate-600">Tags: {(analysis.behavior_tags || []).join(', ') || 'None'}</div>
        </section>
      )}

      <section className="rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="text-sm font-semibold">Recent Entries</h2>
        <div className="mt-4 space-y-3">
          {journals.length === 0 && <div className="text-sm text-slate-600">No journal entries yet.</div>}
          {journals.slice(0, 8).map((journal) => (
            <div key={journal.id} className="rounded-md bg-slate-50 p-3">
              <div className="text-sm text-slate-800">{journal.notes}</div>
              <div className="mt-1 text-xs uppercase text-slate-500">{journal.emotional_state || 'UNLABELED'}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default JournalPage;
