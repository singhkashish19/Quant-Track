import { NavLink, Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';

import { AnalyticsPage, Dashboard, InsightsPage, JournalPage, LoginPage, ProfilePage, RegisterPage, TradesPage } from './pages';
import { logout } from './store/slices/authSlice';

function ProtectedRoute({ children }) {
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppShell({ children }) {
  const dispatch = useDispatch();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white px-5 py-6 md:block">
        <div className="text-xl font-semibold tracking-tight">QuantTrack</div>
        <nav className="mt-8 grid gap-1 text-sm font-medium">
          <NavItem to="/dashboard">Dashboard</NavItem>
          <NavItem to="/trades">Trades</NavItem>
          <NavItem to="/analytics">Analytics</NavItem>
          <NavItem to="/journal">Journal</NavItem>
          <NavItem to="/insights">AI Insights</NavItem>
          <NavItem to="/profile">Profile</NavItem>
        </nav>
        <button className="mt-8 rounded-md border border-slate-200 px-3 py-2 text-sm" onClick={() => dispatch(logout())}>
          Sign out
        </button>
      </aside>
      <main className="md:pl-64">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</div>
      </main>
    </div>
  );
}

function NavItem({ to, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `rounded-md px-3 py-2 ${isActive ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-100'}`
      }
    >
      {children}
    </NavLink>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={<Navigate to="/dashboard" replace />}
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AppShell>
                <Dashboard />
              </AppShell>
            </ProtectedRoute>
          }
        />
        <Route
          path="/trades"
          element={
            <ProtectedRoute>
              <AppShell>
                <TradesPage />
              </AppShell>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <AppShell>
                <AnalyticsPage />
              </AppShell>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <AppShell>
                <ProfilePage />
              </AppShell>
            </ProtectedRoute>
          }
        />
        <Route
          path="/journal"
          element={
            <ProtectedRoute>
              <AppShell>
                <JournalPage />
              </AppShell>
            </ProtectedRoute>
          }
        />
        <Route
          path="/insights"
          element={
            <ProtectedRoute>
              <AppShell>
                <InsightsPage />
              </AppShell>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
