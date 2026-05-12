/**
 * Redux Store Configuration
 */

import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import tradesReducer from './slices/tradesSlice';
import analyticsReducer from './slices/analyticsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    trades: tradesReducer,
    analytics: analyticsReducer,
  },
});

export default store;
