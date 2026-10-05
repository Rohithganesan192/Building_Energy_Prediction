import React, { useEffect, useState } from 'react';
import { Card, GlassPanel } from '../components/ui/Card';
import { Badge, StatusBadge } from '../components/ui/index';
import { Button } from '../components/ui/Button';
import { usePrediction } from '../store/PredictionContext';
import { apiClient } from '../services/apiClient';
import { useNavigate } from 'react-router-dom';
import { Lightbulb, Info, AlertTriangle, ArrowRight, Activity, Database, Clock, CloudRain, Building2, Zap } from 'lucide-react';

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

const HBar = ({ value, max, color, isNegative }) => {
  const pct = Math.min(100, (Math.abs(value) / max) * 100);
  return (
    <div style={{ flex: 1, display: 'flex', alignItems: 'center', height: 16 }}>
      {isNegative ? (
        <div style={{ flex: 1, display: 'flex', justifyContent: 'flex-end', paddingRight: '0.5rem' }}>
          <div style={{ height: 6, width: `${pct}%`, background: color, borderRadius: 'var(--radius-pill)', opacity: 0.8 }} />
        </div>
      ) : (
        <div style={{ flex: 1, borderRight: '1px solid var(--border-subtle)' }} />
      )}
      
      {!isNegative ? (
        <div style={{ flex: 1, display: 'flex', justifyContent: 'flex-start', paddingLeft: '0.5rem' }}>
          <div style={{ height: 6, width: `${pct}%`, background: color, borderRadius: 'var(--radius-pill)', opacity: 0.8 }} />
        </div>
      ) : (
        <div style={{ flex: 1, borderLeft: '1px solid var(--border-subtle)' }} />
      )}
    </div>
  );
};

export const Explain = () => {
  const { currentFeatures, predictionResult } = usePrediction();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(false);
  const [explainData, setExplainData] = useState(null);
  const [globalData, setGlobalData] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setErrorMsg(null);
      try {
        const [drv, exp] = await Promise.all([
          apiClient.getEnergyDrivers(),
          currentFeatures ? apiClient.explain(currentFeatures) : Promise.resolve(null)
        ]);
        setGlobalData(drv);
        if (exp?.explanation) {
          setExplainData(exp);
        }
      } catch (err) {
        console.error(err);
        setErrorMsg("Failed to load explanation data.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [currentFeatures]);

  const renderEmptyState = () => (
    <div style={{ textAlign: 'center', padding: 'var(--space-8) var(--space-6)', background: 'var(--surface-secondary)', borderRadius: 'var(--radius-md)', border: '1px dashed var(--border-strong)' }}>
      <Activity size={24} style={{ color: 'var(--accent-primary)', marginBottom: 'var(--space-3)' }} />
      <h3 style={{ fontSize: 'var(--fs-base)', fontWeight: 600, color: 'var(--text-secondary)' }}>No Active Prediction</h3>
      <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-muted)', maxWidth: 400, margin: '0.5rem auto var(--space-5)' }}>
        Generate a prediction first to see its local SHAP explanation.
      </p>
      <Button variant="primary" onClick={() => navigate('/predict')}>
        Create Prediction <ArrowRight size={14} />
      </Button>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: 1200, paddingBottom: 'var(--space-8)' }}>
      
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">Explainable Model Intelligence</h1>
          <p className="page-subtitle">Understand why the model made its prediction using SHAP local explanations.</p>
        </div>
        <StatusBadge status="success" text="SHAP Ready" />
      </div>

      {errorMsg && (
        <div style={{ padding: 'var(--space-3)', background: 'rgba(220, 38, 38, 0.1)', color: 'var(--accent-danger)', borderRadius: 'var(--radius-sm)', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <AlertTriangle size={16} /> {errorMsg}
        </div>
      )}

      {loading ? (
        <div style={{ padding: 'var(--space-6)', textAlign: 'center', color: 'var(--text-muted)' }}>Loading explanation data...</div>
      ) : (
        <>
          {!currentFeatures || !explainData ? renderEmptyState() : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-5)' }}>
              
              <Card title="Prediction Summary" action={<Lightbulb size={16} style={{color:'var(--text-muted)'}}/>}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', marginTop: 'var(--space-4)' }}>
                  <div>
                     <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Predicted Consumption</div>
                     <div style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700, color: 'var(--accent-primary)', lineHeight: 1, marginTop: '0.2rem' }}>
                       {explainData.prediction.predicted_energy?.toFixed(2)} <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>kWh</span>
                     </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)', borderTop: '1px solid var(--border-subtle)', paddingTop: 'var(--space-3)' }}>
                    <div>
                      <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Model</div>
                      <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>Random Forest</div>
                    </div>
                    <div>
                      <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Feature Group</div>
                      <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>Group B / Historical</div>
                    </div>
                    <div>
                      <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Target</div>
                      <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>meter_reading (raw)</div>
                    </div>
                    <div>
                      <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Observation</div>
                      <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>
                        {predictionResult?.is_demo ? 'Verified ASHRAE Observation' : 'Manual Testing Input'}
                      </div>
                    </div>
                  </div>
                </div>
              </Card>

              <Card title="Local Explanation" action={<Badge variant="accent">SHAP</Badge>}>
                <div style={{ marginTop: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', paddingBottom: '0.2rem', borderBottom: '1px solid var(--border-subtle)' }}>
                    <span style={{ flex: 1.5 }}>Feature Contributor</span>
                    <span style={{ flex: 1, textAlign: 'center' }}>Negative ← → Positive</span>
                    <span style={{ width: 60, textAlign: 'right' }}>Value</span>
                  </div>
                  
                  {(() => {
                    const pos = explainData.explanation.positive_contributors || [];
                    const neg = explainData.explanation.negative_contributors || [];
                    const all = [...pos, ...neg].sort((a, b) => Math.abs(b.value) - Math.abs(a.value)).slice(0, 10);
                    const maxAbs = Math.max(...all.map(d => Math.abs(d.value)), 1);

                    return all.map((d) => (
                      <div key={d.feature} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-2)', padding: '0.25rem 0' }}>
                        <div style={{ flex: 1.5, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
                          <span style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-primary)', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {FRIENDLY_NAMES[d.feature] || d.feature}
                          </span>
                          <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', fontFamily: 'var(--font-mono, monospace)', marginTop: '2px' }}>
                            {d.feature}
                          </span>
                        </div>
                        
                        <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
                          <HBar value={d.value} max={maxAbs} color={d.value > 0 ? 'var(--accent-danger)' : 'var(--accent-success)'} isNegative={d.value < 0} />
                        </div>
                        
                        <span style={{ width: 60, fontSize: 'var(--fs-sm)', color: 'var(--text-primary)', textAlign: 'right', fontWeight: 600 }}>
                          {d.value > 0 ? '+' : ''}{d.value.toFixed(2)}
                        </span>
                      </div>
                    ));
                  })()}
                </div>
              </Card>
            </div>
          )}

          <GlassPanel style={{ padding: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-3)', borderLeft: '3px solid var(--accent-warning)', borderRadius: 'var(--radius-sm)' }}>
            <AlertTriangle size={20} style={{ color: 'var(--accent-warning)', flexShrink: 0 }} />
            <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', margin: 0, lineHeight: 'var(--lh-relaxed)' }}>
              <strong>Important Disclaimer:</strong> SHAP values describe mathematical model attribution for this specific prediction. They do not establish real-world causality or guarantee engineering outcomes.
            </p>
          </GlassPanel>

          {globalData && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-5)' }}>
              
              <Card title="Global Model Intelligence" action={<Badge variant="neutral">Top Global Drivers</Badge>}>
                <div style={{ marginTop: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                  <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                    This section represents model-level feature importance across the entire dataset, rather than for a single prediction.
                  </p>
                  <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Mean |SHAP| (Overall)</div>
                  {(globalData.global_importance || []).map((d, i) => (
                    <div key={d.feature || i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <span style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>
                          {FRIENDLY_NAMES[d.feature] || d.feature}
                        </span>
                        <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', fontFamily: 'var(--font-mono, monospace)' }}>
                          {d.feature}
                        </span>
                      </div>
                      <span style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-primary)', fontWeight: 600 }}>
                        {d.mean_abs_shap ? d.mean_abs_shap.toFixed(2) : '0.00'}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>

              <Card title="Feature Group Attribution" action={<Badge variant="neutral">Global Model Level</Badge>}>
                 <div style={{ marginTop: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                   {(globalData.groups || []).map((g) => (
                     <div key={g.name}>
                       <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                         <span style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-primary)', fontWeight: 600 }}>{g.name}</span>
                         <span style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}>{g.pct.toFixed(2)}%</span>
                       </div>
                       <div style={{ height: 6, background: 'var(--surface-secondary)', borderRadius: 'var(--radius-pill)', overflow: 'hidden', marginBottom: '0.3rem' }}>
                         <div style={{ height: '100%', width: `${g.pct}%`, background: 'var(--chart-1)', borderRadius: 'var(--radius-pill)' }} />
                       </div>
                       <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)' }}>
                         {GROUP_EXPLANATIONS[g.name] || ""}
                       </div>
                     </div>
                   ))}
                 </div>
              </Card>

            </div>
          )}
        </>
      )}
    </div>
  );
};
