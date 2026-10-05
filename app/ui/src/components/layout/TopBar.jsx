import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Search, Bell, Palette, Info, CheckCircle2, Server, Database, Activity, LayoutDashboard, BrainCircuit, Box, ShieldAlert, XCircle } from 'lucide-react';
import { useTheme } from '../../store/ThemeContext';
import { IconButton } from '../ui/Button';
import './layout.css';

const pageLabels = {
  '/':               'Overview',
  '/predict':        'Predict',
  '/explain':        'Explain',
  '/drivers':        'Energy Drivers',
  '/recommendations':'Recommendations',
  '/model-lab':      'Model Lab',
  '/buildings':      'Buildings',
  '/reports':        'Reports',
  '/settings':       'Settings',
  '/theme-studio':   'Theme Studio',
};

const SEARCH_ROUTES = [
  { path: '/', label: 'Overview', icon: <LayoutDashboard size={14}/> },
  { path: '/predict', label: 'Predict', icon: <BrainCircuit size={14}/> },
  { path: '/explain', label: 'Explain', icon: <Box size={14}/> },
  { path: '/drivers', label: 'Energy Drivers', icon: <Activity size={14}/> },
  { path: '/recommendations', label: 'Recommendations', icon: <ShieldAlert size={14}/> },
  { path: '/model-lab', label: 'Model Lab', icon: <Server size={14}/> },
  { path: '/buildings', label: 'Buildings', icon: <Database size={14}/> },
  { path: '/reports', label: 'Reports', icon: <Box size={14}/> },
  { path: '/settings', label: 'Settings', icon: <Info size={14}/> }
];

export const TopBar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, themes, setTheme, currentTheme } = useTheme();
  const label = pageLabels[location.pathname] ?? 'Building Energy Intelligence';

  const [searchQuery, setSearchQuery] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  
  const [showNotifications, setShowNotifications] = useState(false);
  const [showAppInfo, setShowAppInfo] = useState(false);

  const searchRef = useRef(null);
  const notifRef = useRef(null);
  const infoRef = useRef(null);

  const cycleTheme = () => {
    const idx = themes.findIndex((t) => t.id === theme);
    setTheme(themes[(idx + 1) % themes.length].id);
  };

  const [sysStatus, setSysStatus] = useState({ backend: null, model: null });
  const [loadingStatus, setLoadingStatus] = useState(false);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) setShowSearch(false);
      if (notifRef.current && !notifRef.current.contains(event.target)) setShowNotifications(false);
      if (infoRef.current && !infoRef.current.contains(event.target)) setShowAppInfo(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleStatusClick = async () => {
    setShowNotifications(!showNotifications);
    if (!showNotifications) {
      setLoadingStatus(true);
      try {
        const { apiClient } = await import('../../services/apiClient');
        const [health, modelInfo] = await Promise.all([
          apiClient.getHealth().catch(() => null),
          apiClient.getModelInfo().catch(() => null)
        ]);
        setSysStatus({ backend: !!health, model: !!modelInfo });
      } finally {
        setLoadingStatus(false);
      }
    }
  };

  const filteredRoutes = SEARCH_ROUTES.filter(r => r.label.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <header className="top-bar" role="banner">
      <div className="top-bar-left">
        <nav className="breadcrumb" aria-label="Breadcrumb">
          <span>BEI</span>
          <span className="breadcrumb-sep">/</span>
          <span className="breadcrumb-current">{label}</span>
        </nav>
      </div>

      <div className="top-bar-right">
        
        {/* Search */}
        <div className="search-wrapper" ref={searchRef} style={{ position: 'relative' }}>
          <Search size={13} className="search-icon-pos" aria-hidden="true" />
          <input
            type="search"
            className="search-input"
            placeholder="Search application..."
            aria-label="Search"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setShowSearch(true);
            }}
            onFocus={() => setShowSearch(true)}
          />
          {showSearch && searchQuery && (
            <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, marginTop: '0.5rem', background: 'var(--surface-primary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)', zIndex: 50, maxHeight: 300, overflowY: 'auto' }}>
              {filteredRoutes.length > 0 ? (
                filteredRoutes.map(route => (
                  <div 
                    key={route.path} 
                    onClick={() => {
                      navigate(route.path);
                      setShowSearch(false);
                      setSearchQuery('');
                    }}
                    style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'var(--surface-secondary)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    {route.icon}
                    {route.label}
                  </div>
                ))
              ) : (
                <div style={{ padding: '0.5rem 1rem', fontSize: 'var(--fs-sm)', color: 'var(--text-muted)' }}>No results found</div>
              )}
            </div>
          )}
        </div>

        <button
          className="theme-cycle-btn"
          onClick={cycleTheme}
          title={`Theme: ${currentTheme?.name}. Click to cycle.`}
        >
          <span className="theme-dot" aria-hidden="true" />
          <span>{currentTheme?.name}</span>
          <Palette size={12} aria-hidden="true" />
        </button>

        {/* Notifications / System Status */}
        <div ref={notifRef} style={{ position: 'relative' }}>
          <div onClick={handleStatusClick}>
            <IconButton icon={Bell} label="System Status" />
          </div>
          {showNotifications && (
            <div style={{ position: 'absolute', top: '100%', right: 0, marginTop: '0.5rem', width: 250, background: 'var(--surface-primary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)', zIndex: 50, padding: '1rem' }}>
              <h4 style={{ margin: '0 0 1rem 0', fontSize: 'var(--fs-sm)', color: 'var(--text-primary)' }}>System Status</h4>
              {loadingStatus ? <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-muted)' }}>Checking...</div> : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}>Backend API</span>
                  {sysStatus.backend ? 
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--accent-success)', fontSize: 'var(--fs-xs)' }}><CheckCircle2 size={12}/> Connected</div> :
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--accent-danger)', fontSize: 'var(--fs-xs)' }}><XCircle size={12}/> Unavailable</div>
                  }
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}>Model Engine</span>
                  {sysStatus.model ? 
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--accent-success)', fontSize: 'var(--fs-xs)' }}><CheckCircle2 size={12}/> Ready</div> :
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--accent-danger)', fontSize: 'var(--fs-xs)' }}><XCircle size={12}/> Unavailable</div>
                  }
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}>SHAP</span>
                  {sysStatus.model ?
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--accent-success)', fontSize: 'var(--fs-xs)' }}><CheckCircle2 size={12}/> Available</div> :
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--accent-danger)', fontSize: 'var(--fs-xs)' }}><XCircle size={12}/> Unavailable</div>
                  }
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}>Application</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--accent-success)', fontSize: 'var(--fs-xs)' }}><CheckCircle2 size={12}/> Operational</div>
                </div>
              </div>
              )}
            </div>
          )}
        </div>

        {/* App Info Avatar */}
        <div ref={infoRef} style={{ position: 'relative' }}>
          <div 
            className="user-avatar" 
            aria-label="Application Info" 
            title="Application Info"
            onClick={() => setShowAppInfo(!showAppInfo)}
            style={{ cursor: 'pointer' }}
          >
            BEI
          </div>
          {showAppInfo && (
            <div style={{ position: 'absolute', top: '100%', right: 0, marginTop: '0.5rem', width: 300, background: 'var(--surface-primary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)', zIndex: 50, padding: '1rem' }}>
              <h4 style={{ margin: '0 0 0.25rem 0', fontSize: 'var(--fs-base)', color: 'var(--text-primary)' }}>Explainable Machine Learning for Building Energy Consumption Prediction</h4>
              <p style={{ margin: '0 0 1rem 0', fontSize: 'var(--fs-xs)', color: 'var(--text-muted)' }}>Version 1.0.0 (Research Release)</p>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.75rem' }}>
                <div>
                  <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Dataset</div>
                  <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}>ASHRAE Great Energy Predictor III</div>
                </div>
                <div>
                  <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Final Model</div>
                  <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}>RandomForestRegressor (Group B)</div>
                </div>
                <div>
                  <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>XAI Method</div>
                  <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}>SHAP TreeExplainer</div>
                </div>
                <div>
                  <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Decision Support</div>
                  <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}>Rule-based (Phase 10)</div>
                </div>
              </div>
              <div style={{ borderTop: '1px solid var(--border-subtle)', marginTop: '0.75rem', paddingTop: '0.75rem' }}>
                <button 
                  onClick={() => {
                    localStorage.removeItem('bei_admin_token');
                    window.location.reload();
                  }}
                  style={{ width: '100%', padding: '0.5rem', background: 'var(--surface-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', cursor: 'pointer', color: 'var(--text-primary)', fontSize: 'var(--fs-sm)' }}
                >
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>

      </div>
    </header>
  );
};