/**
 * Analytics Redux Slice
 */

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  summary: null,
  metrics: null,
  charts: {
    equityCurve: null,
    drawdown: null,
    pnl: null,
  },
  loading: false,
  error: null,
};

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    setSummary: (state, action) => {
      state.summary = action.payload;
    },
    setMetrics: (state, action) => {
      state.metrics = action.payload;
    },
    setCharts: (state, action) => {
      state.charts = action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const { setSummary, setMetrics, setCharts, setLoading, setError } = analyticsSlice.actions;
export default analyticsSlice.reducer;
