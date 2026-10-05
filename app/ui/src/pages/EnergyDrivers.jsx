import React, { useEffect, useState } from 'react';
import { Card, GlassPanel } from '../components/ui/Card';
import { Badge, StatusBadge } from '../components/ui/index';
import { Button } from '../components/ui/Button';
import { apiClient } from '../services/apiClient';
import { useNavigate } from 'react-router-dom';
import { GitMerge, Info, AlertTriangle, ArrowRight, BarChart2 } from 'lucide-react';

const FRIENDLY_NAMES = {
  lag_1: "Previous-hour energy consumption",
  lag_24: "Previous-day same-hour consumption",
  lag_168: "Previous-week same-hour consumption",
  rolling_mean_24: "24-hour historical average consumption",
  rolling_mean_168: "168-hour historical average consumption",
  rolling_std_24: "24-hour historical consumption variability",
  rolling_std_168: "168-hour historical consumption variability",
  hour: "Hour of day",
  day_of_week: "Day of week",
  day_of_year: "Position within the year",
  hour_sin: "Cyclic representation of daily time pattern",
  hour_cos: "Cyclic representation of daily time pattern",
  air_temperature: "Outdoor air temperature",
  dew_temperature: "Outdoor dew temperature",
  cloud_coverage: "Cloud coverage",
  precip_depth_1_hr: "Hourly precipitation depth",
  sea_level_pressure: "Sea-level atmospheric pressure",
  wind_direction: "Wind direction",
  wind_speed: "Wind speed",
  square_feet: "Building floor area",
  year_built: "Building construction year",
  floor_count: "Number of floors",
  primary_use: "Building primary-use category",
  site_id: "ASHRAE site identifier",
  meter: "Energy meter category"
};

const GROUP_EXPLANATIONS = {
  "Historical": "Previous energy consumption and recent operating state.",
  "Temporal": "Time-related patterns such as hour, weekday and seasonal position.",
  "Weather": "Environmental conditions such as temperature, pressure and wind.",
  "Building": "Physical and usage characteristics of the building.",
  "Meter": "Energy meter category."
};

export const EnergyDrivers = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await apiClient.getEnergyDrivers();
        setData(res);
      } catch (err) {
        console.error(err);
        setErrorMsg("Failed to load energy drivers.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: 1200, paddingBottom: 'var(--space-8)' }}>
      
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">Energy Drivers</h1>
          <p className="page-subtitle">Model-derived drivers of building energy consumption.</p>
        </div>
        <StatusBadge status="success" text="Drivers Analyzed" />
      </div>

      {errorMsg && (
        <div style={{ padding: 'var(--space-3)', background: 'rgba(220, 38, 38, 0.1)', color: 'var(--accent-danger)', borderRadius: 'var(--radius-sm)', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <AlertTriangle size={16} /> {errorMsg}
        </div>
      )}

      {loading ? (
        <div style={{ padding: 'var(--space-6)', textAlign: 'center', color: 'var(--text-muted)' }}>Loading drivers...</div>
      ) : data ? (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-5)' }}>
            
            <Card title="Driver Overview" action={<BarChart2 size={16} style={{color: 'var(--text-muted)'}}/>}>
               <div style={{ marginTop: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                 {(data.groups || []).map((g, i) => (
                   <div key={g.name}>
                     <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: '0.3rem' }}>
                       <span style={{ width: 80, fontSize: 'var(--fs-sm)', color: 'var(--text-primary)', fontWeight: 600, flexShrink: 0 }}>{g.name}</span>
                       <div style={{ flex: 1, height: 8, background: 'var(--surface-secondary)', borderRadius: 'var(--radius-pill)', overflow: 'hidden' }}>
                         <div style={{ height: '100%', width: `${g.pct}%`, background: `var(--chart-${(i % 5) + 1})`, borderRadius: 'var(--radius-pill)' }} />
                       </div>
                       <span style={{ width: 48, fontSize: 'var(--fs-sm)', color: 'var(--text-muted)', textAlign: 'right', flexShrink: 0 }}>
                         {g.pct.toFixed(2)}%
                       </span>
                     </div>
                     <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)' }}>
                       {GROUP_EXPLANATIONS[g.name] || ""}
                     </div>
                   </div>
                 ))}
               </div>
            </Card>

            <Card title="Top Global Features" action={<Badge variant="accent">Global SHAP</Badge>}>
              <div style={{ marginTop: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                 <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.2rem', display: 'flex', justifyContent: 'space-between' }}>
                   <span>Feature</span>
                   <span>Mean |SHAP|</span>
                 </div>
                 {(data.global_importance || []).map((d, i) => {
                   const featName = d.feature;
                   const featValue = d.mean_abs_shap;
                   const pct = Math.min(100, (featValue / 373.60) * 100); 
                   return (
                     <div key={featName} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', padding: '0.25rem 0' }}>
                       <div style={{ display: 'flex', flexDirection: 'column', minWidth: 120 }}>
                         <span style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-primary)', fontWeight: 500 }}>
                           {FRIENDLY_NAMES[featName] || featName}
                         </span>
                         <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', fontFamily: 'var(--font-mono, monospace)' }}>
                           {featName}
                         </span>
                       </div>
                       <div style={{ flex: 1, height: 6, background: 'var(--surface-secondary)', borderRadius: 'var(--radius-pill)' }}>
                         <div style={{ height: '100%', width: `${pct}%`, background: 'var(--chart-1)', borderRadius: 'var(--radius-pill)' }} />
                       </div>
                       <span style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-primary)', fontWeight: 600, width: 50, textAlign: 'right' }}>
                         {featValue?.toFixed(2)}
                       </span>
                     </div>
                   );
                 })}
              </div>
            </Card>

          </div>

          <GlassPanel style={{ padding: 'var(--space-5)', borderLeft: '3px solid var(--accent-warning)', borderRadius: 'var(--radius-sm)' }}>
             <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)' }}>
               <Info size={20} style={{ color: 'var(--accent-warning)', flexShrink: 0, marginTop: '2px' }} />
               <div>
                 <h4 style={{ margin: '0 0 var(--space-2) 0', fontSize: 'var(--fs-base)', color: 'var(--text-primary)', fontWeight: 600 }}>Important Disclaimer</h4>
                 <p style={{ margin: 0, fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', lineHeight: 'var(--lh-relaxed)' }}>
                   These values represent model attribution, not causal influence. In the evaluated sample, historical features represent prior consumption states and absorb substantial temporal and operational information. 
                   <br/><br/>
                   <strong>Note:</strong> <span style={{ fontFamily: 'var(--font-mono, monospace)' }}>lag_1</span> has the strongest model attribution. This does <em>not</em> mean <span style={{ fontFamily: 'var(--font-mono, monospace)' }}>lag_1</span> causes energy consumption. It is a powerful predictor that captures building inertia and recent state.
                 </p>
               </div>
             </div>
          </GlassPanel>

          <Card title="Actionability Categorization" action={<GitMerge size={16} style={{color: 'var(--text-muted)'}} />}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--space-4)', marginTop: 'var(--space-4)' }}>
              
              <div style={{ padding: 'var(--space-4)', background: 'var(--surface-secondary)', borderRadius: 'var(--radius-sm)' }}>
                <h5 style={{ margin: '0 0 var(--space-2) 0', fontSize: 'var(--fs-sm)', color: 'var(--text-primary)' }}>Historical (Non-Actionable)</h5>
                <p style={{ margin: 0, fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', lineHeight: 'var(--lh-relaxed)' }}>
                  Lags and rolling averages (e.g. lag_1, rolling_mean_24). These are highly predictive state variables but cannot be directly tuned.
                </p>
              </div>

              <div style={{ padding: 'var(--space-4)', background: 'var(--surface-secondary)', borderRadius: 'var(--radius-sm)' }}>
                <h5 style={{ margin: '0 0 var(--space-2) 0', fontSize: 'var(--fs-sm)', color: 'var(--text-primary)' }}>Contextual (Non-Actionable)</h5>
                <p style={{ margin: 0, fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', lineHeight: 'var(--lh-relaxed)' }}>
                  Weather and temporal cycles (e.g. air_temperature, hour_cos). These form the environmental baseline against which the building operates.
                </p>
              </div>

              <div style={{ padding: 'var(--space-4)', background: 'rgba(6,182,212,0.1)', border: '1px solid rgba(6,182,212,0.2)', borderRadius: 'var(--radius-sm)' }}>
                <h5 style={{ margin: '0 0 var(--space-2) 0', fontSize: 'var(--fs-sm)', color: 'var(--accent-primary)' }}>Potentially Actionable</h5>
                <p style={{ margin: 0, fontSize: 'var(--fs-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--lh-relaxed)' }}>
                  Operational anomalies derived from deviations in the expected energy profile given the contextual baseline.
                </p>
                <div style={{ marginTop: 'var(--space-3)' }}>
                  <Button variant="primary" size="sm" onClick={() => navigate('/recommendations')} style={{ width: '100%', justifyContent: 'center' }}>
                    View Recommendations <ArrowRight size={14}/>
                  </Button>
                </div>
              </div>

            </div>
          </Card>
        </>
      ) : null}

    </div>
  );
};
