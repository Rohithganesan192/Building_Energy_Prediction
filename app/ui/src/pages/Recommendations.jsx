import React, { useEffect, useState } from 'react';
import { Card, GlassPanel } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge, StatusBadge } from '../components/ui/index';
import { usePrediction } from '../store/PredictionContext';
import { apiClient } from '../services/apiClient';
import { useNavigate } from 'react-router-dom';
import { Activity, ArrowRight, AlertTriangle, Lightbulb, GitBranch, ShieldAlert, CheckCircle2 } from 'lucide-react';

export const Recommendations = () => {
  const { currentFeatures } = usePrediction();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    if (!currentFeatures) return;

    const fetchData = async () => {
      setLoading(true);
      setErrorMsg(null);
      try {
        const res = await apiClient.getRecommendations(currentFeatures);
        setData(res);
      } catch (err) {
        console.error(err);
        setErrorMsg("Failed to load recommendations.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [currentFeatures]);

  const renderEmptyState = () => (
    <div style={{ textAlign: 'center', padding: 'var(--space-8) var(--space-6)', background: 'var(--surface-secondary)', borderRadius: 'var(--radius-md)', border: '1px dashed var(--border-strong)' }}>
      <Activity size={24} style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-3)' }} />
      <h3 style={{ fontSize: 'var(--fs-base)', fontWeight: 600, color: 'var(--text-secondary)' }}>No Active Prediction</h3>
      <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-muted)', maxWidth: 400, margin: '0.5rem auto var(--space-5)' }}>
        Generate a prediction to activate evidence-based recommendations.
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
          <h1 className="page-title">Energy Efficiency Recommendations</h1>
          <p className="page-subtitle">Decision-support suggestions derived from model attribution and domain rules.</p>
        </div>
        {!currentFeatures ? (
          <StatusBadge status="neutral" text="Awaiting Prediction" />
        ) : (
          <StatusBadge status="success" text="Engine Active" />
        )}
      </div>

      {errorMsg && (
        <div style={{ padding: 'var(--space-3)', background: 'rgba(220, 38, 38, 0.1)', color: 'var(--accent-danger)', borderRadius: 'var(--radius-sm)', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <AlertTriangle size={16} /> {errorMsg}
        </div>
      )}

      {loading ? (
        <div style={{ padding: 'var(--space-6)', textAlign: 'center', color: 'var(--text-muted)' }}>Analyzing SHAP signals...</div>
      ) : !currentFeatures ? (
        renderEmptyState()
      ) : data ? (
        <>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
            {(data.recommendations || []).length === 0 ? (
              <Card title="Normal Operation Baseline" action={<Badge variant="neutral">Baseline</Badge>}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', marginTop: 'var(--space-4)' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)' }}>
                    <div>
                      <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.2rem' }}>
                        Current Assessment
                      </div>
                      <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-primary)', fontWeight: 500 }}>
                        Current consumption is consistent with the available historical operating baseline.
                      </div>
                    </div>
                  </div>
                  <div style={{ background: 'var(--surface-secondary)', padding: 'var(--space-4)', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <Lightbulb size={14} style={{ color: 'var(--accent-primary)' }}/>
                      Evidence
                    </div>
                    <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-primary)', margin: 0, lineHeight: 'var(--lh-relaxed)' }}>
                      Historical energy-state features are the dominant model-attribution group. No actionable contextual anomalies detected.
                    </p>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', background: 'rgba(217,119,6,0.05)', border: '1px solid rgba(217,119,6,0.15)', padding: 'var(--space-3)', borderRadius: 'var(--radius-xs)' }}>
                     <ShieldAlert size={16} style={{ color: 'var(--accent-warning)', flexShrink: 0, marginTop: '2px' }} />
                     <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', lineHeight: 'var(--lh-relaxed)' }}>
                       <strong>Operational Guidance:</strong> Continue monitoring consumption against the recent historical baseline and investigate substantial deviations.
                     </span>
                  </div>
                </div>
              </Card>
            ) : (
              (data.recommendations || []).map((rec, i) => (
                <Card key={i} title={rec.action || "Suggested Action"} action={<Badge variant="accent">Actionable Anomaly</Badge>}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', marginTop: 'var(--space-4)' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)' }}>
                      <div>
                        <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.2rem' }}>
                          Current Assessment
                        </div>
                        <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>
                          Actionable contextual driver detected for {rec.driver || "Operational variable"}.
                        </div>
                      </div>
                    </div>
                    <div style={{ background: 'var(--surface-secondary)', padding: 'var(--space-4)', borderRadius: 'var(--radius-sm)' }}>
                      <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Lightbulb size={14} style={{ color: 'var(--accent-primary)' }}/>
                        Evidence
                      </div>
                      <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-primary)', margin: 0, lineHeight: 'var(--lh-relaxed)' }}>
                        {rec.signal || "Significant SHAP deviation detected."} {rec.rationale}
                      </p>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', background: 'rgba(217,119,6,0.05)', border: '1px solid rgba(217,119,6,0.15)', padding: 'var(--space-3)', borderRadius: 'var(--radius-xs)' }}>
                       <ShieldAlert size={16} style={{ color: 'var(--accent-warning)', flexShrink: 0, marginTop: '2px' }} />
                       <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', lineHeight: 'var(--lh-relaxed)' }}>
                         <strong>Operational Guidance:</strong> {rec.limitation || "Investigate the underlying causes of this feature's high attribution to optimize operational efficiency. This does not establish causal energy savings."}
                       </span>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
          
          <div style={{ marginTop: 'var(--space-4)', padding: 'var(--space-4)', borderRadius: 'var(--radius-sm)', borderTop: '1px solid var(--border-subtle)', textAlign: 'center' }}>
             <p style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)' }}>
               * Do not interpret SHAP attribution directly as guaranteed energy savings percentages. Recommendations are decision-support logic.
             </p>
          </div>
        </>
      ) : null}

    </div>
  );
};
