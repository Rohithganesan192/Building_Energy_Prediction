import React, { useState, useEffect } from 'react';
import { Card, GlassPanel } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge, StatusBadge } from '../components/ui/index';
import { apiClient } from '../services/apiClient';
import { useTheme } from '../store/ThemeContext';
import { Settings as SettingsIcon, Server, Database, BrainCircuit, Activity, Palette, CheckCircle2, XCircle } from 'lucide-react';

export const Settings = () => {
  const { theme, themes, setTheme, currentTheme } = useTheme();
  const [sysInfo, setSysInfo] = useState({ backend: null, model: null });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const [health, modelInfo] = await Promise.all([
          apiClient.getHealth().catch(() => ({ status: 'error' })),
          apiClient.getModelInfo().catch(() => null)
        ]);
        setSysInfo({ backend: health?.status === 'ok', model: modelInfo });
      } finally {
        setLoading(false);
      }
    };
    fetchInfo();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: 1000, paddingBottom: 'var(--space-8)' }}>
      <div className="page-header">
        <h1 className="page-title">Settings & Configuration</h1>
        <p className="page-subtitle">Application preferences and system information.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-6)' }}>
        
        {/* System Status */}
        <Card title="System Status" action={<Activity size={16} style={{ color: 'var(--text-muted)' }} />}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                <Server size={16} /> Backend API
              </div>
              {loading ? <Badge variant="neutral">Checking...</Badge> : 
                sysInfo.backend ? <StatusBadge status="success" text="Connected" /> : <StatusBadge status="error" text="Disconnected" />}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                <BrainCircuit size={16} /> Prediction Engine
              </div>
              {loading ? <Badge variant="neutral">Checking...</Badge> : 
                sysInfo.model ? <StatusBadge status="success" text="Operational" /> : <StatusBadge status="error" text="Unavailable" />}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                <SettingsIcon size={16} /> Application Version
              </div>
              <span style={{ fontSize: 'var(--fs-sm)', fontWeight: 500, color: 'var(--text-primary)' }}>v1.0.0 (Research Release)</span>
            </div>
          </div>
        </Card>

        {/* Display Settings */}
        <Card title="Display Preferences" action={<Palette size={16} style={{ color: 'var(--text-muted)' }} />}>
          <div style={{ marginTop: '1rem' }}>
            <label style={{ fontSize: 'var(--fs-sm)', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.5rem' }}>Active Theme</label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {themes.map(t => (
                <button
                  key={t.id}
                  onClick={() => setTheme(t.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem 1rem',
                    background: theme === t.id ? 'var(--surface-secondary)' : 'transparent',
                    border: `1px solid ${theme === t.id ? 'var(--accent-primary)' : 'var(--border-subtle)'}`,
                    borderRadius: 'var(--radius-sm)',
                    cursor: 'pointer',
                    color: 'var(--text-primary)',
                    fontWeight: theme === t.id ? 600 : 400
                  }}
                >
                  {t.name}
                  {theme === t.id && <CheckCircle2 size={16} style={{ color: 'var(--accent-primary)' }} />}
                </button>
              ))}
            </div>
          </div>
        </Card>

        {/* Model & Dataset Config */}
        <GlassPanel style={{ gridColumn: '1 / -1', padding: 'var(--space-6)', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
            <Database size={20} style={{ color: 'var(--accent-primary)' }} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, margin: 0 }}>Research Configuration</h2>
          </div>
          <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
            This application is running in a strictly controlled research environment. Core model and dataset parameters are locked to preserve the integrity of the experimental results.
          </p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
            <div>
              <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Target Dataset</div>
              <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 500, color: 'var(--text-secondary)' }}>ASHRAE Great Energy Predictor III</div>
            </div>
            <div>
              <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Selected Model</div>
              <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 500, color: 'var(--text-secondary)' }}>{sysInfo.model?.model_name || 'Random Forest'}</div>
            </div>
            <div>
              <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Feature Group</div>
              <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 500, color: 'var(--text-secondary)' }}>{sysInfo.model?.feature_group || 'Group B (Historical included)'}</div>
            </div>
            <div>
              <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Target Transform</div>
              <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 500, color: 'var(--text-secondary)' }}>{sysInfo.model?.target || 'meter_reading (raw)'}</div>
            </div>
            <div>
              <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>XAI Method</div>
              <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 500, color: 'var(--text-secondary)' }}>{sysInfo.model?.xai_method || 'SHAP TreeExplainer'}</div>
            </div>
            <div>
              <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Decision Support</div>
              <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 500, color: 'var(--text-secondary)' }}>Phase 10 Recommendation Rules</div>
            </div>
          </div>
        </GlassPanel>

      </div>
    </div>
  );
};
