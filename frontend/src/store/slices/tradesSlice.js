/**
 * Trades Redux Slice
 */

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  trades: [],
  currentTrade: null,
  statistics: null,
  loading: false,
  error: null,
  filters: {
    symbol: null,
    strategy: null,
    session: null,
  },
};

const tradesSlice = createSlice({
  name: 'trades',
  initialState,
  reducers: {
    setTrades: (state, action) => {
      state.trades = action.payload;
    },
    addTrade: (state, action) => {
      state.trades.unshift(action.payload);
    },
    updateTrade: (state, action) => {
      const index = state.trades.findIndex(t => t.id === action.payload.id);
      if (index !== -1) {
        state.trades[index] = action.payload;
      }
    },
    deleteTrade: (state, action) => {
      state.trades = state.trades.filter(t => t.id !== action.payload);
    },
    setCurrentTrade: (state, action) => {
      state.currentTrade = action.payload;
    },
    setStatistics: (state, action) => {
      state.statistics = action.payload;
    },
    setFilters: (state, action) => {
      state.filters = action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const {
  setTrades,
  addTrade,
  updateTrade,
  deleteTrade,
  setCurrentTrade,
  setStatistics,
  setFilters,
  setLoading,
  setError,
} = tradesSlice.actions;

export default tradesSlice.reducer;
