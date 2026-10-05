import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './store/ThemeContext';
import { PredictionProvider } from './store/PredictionContext';
import { AppLayout } from './components/layout/AppLayout';
import { Overview } from './pages/Overview';
import { ThemeStudio } from './pages/ThemeStudio';
import { Predict } from './pages/Predict';
import { Explain } from './pages/Explain';
import { EnergyDrivers } from './pages/EnergyDrivers';
import { Recommendations } from './pages/Recommendations';
import { ModelLab } from './pages/ModelLab';
import { Buildings } from './pages/Buildings';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';
import { AuthProvider, useAuth } from './store/AuthContext';
import { Login } from './pages/Login';

const AppRoutes = () => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  if (!isAuthenticated) return <Login />;

  return (
    <Router>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Overview />} />
          <Route path="predict"         element={<Predict />} />
          <Route path="explain"         element={<Explain />} />
          <Route path="drivers"         element={<EnergyDrivers />} />
          <Route path="recommendations" element={<Recommendations />} />
          <Route path="model-lab"       element={<ModelLab />} />
          <Route path="buildings"       element={<Buildings />} />
          <Route path="reports"         element={<Reports />} />
          <Route path="settings"        element={<Settings />} />
          <Route path="theme-studio"    element={<ThemeStudio />} />
        </Route>
      </Routes>
    </Router>
  );
};

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <PredictionProvider>
          <AppRoutes />
        </PredictionProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;