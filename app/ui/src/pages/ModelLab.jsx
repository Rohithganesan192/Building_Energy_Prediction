import React from 'react';
import { Card, GlassPanel } from '../components/ui/Card';
import { Badge, StatusBadge } from '../components/ui/index';
import { Target, Layers, Box, Maximize2, ShieldCheck, Database, Calendar } from 'lucide-react';

export const ModelLab = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: 1200, paddingBottom: 'var(--space-8)' }}>
      <div className="page-header">
        <h1 className="page-title">Model Evaluation Laboratory</h1>
        <p className="page-subtitle">Interactive exploration of the project's experimental research findings.</p>
      </div>

      <GlassPanel style={{ padding: 'var(--space-6)', borderRadius: 'var(--radius-lg)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <Database size={18} style={{ color: 'var(--accent-primary)' }} />
          <h2 style={{ fontSize: 'var(--fs-base)', fontWeight: 600 }}>Section A — Experiment Overview</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div><strong style={{ color: 'var(--text-secondary)' }}>Configurations:</strong> 24</div>
          <div><strong style={{ color: 'var(--text-secondary)' }}>Models Evaluated:</strong> 6</div>
          <div><strong style={{ color: 'var(--text-secondary)' }}>Feature Groups:</strong> 2 (Group A, Group B)</div>
          <div><strong style={{ color: 'var(--text-secondary)' }}>Target Representations:</strong> 2 (raw, log1p)</div>
          <div><strong style={{ color: 'var(--text-secondary)' }}>Buildings Sample:</strong> 157 (10.84% deterministic)</div>
          <div><strong style={{ color: 'var(--text-secondary)' }}>Training Period:</strong> Jan–Sep 2016</div>
          <div><strong style={{ color: 'var(--text-secondary)' }}>Validation Period:</strong> Oct–Nov 2016</div>
          <div><strong style={{ color: 'var(--text-secondary)' }}>Holdout Period:</strong> Dec 2016</div>
        </div>
      </GlassPanel>

      <Card title="Section B — Model Comparison (Raw Target)">
        <div style={{ overflowX: 'auto', marginTop: '1rem' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--fs-sm)', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border-strong)', color: 'var(--text-secondary)' }}>
                <th style={{ padding: '0.75rem' }}>Model</th>
                <th style={{ padding: '0.75rem' }}>Group A MAE</th>
                <th style={{ padding: '0.75rem' }}>Group A RMSE</th>
                <th style={{ padding: '0.75rem' }}>Group A R²</th>
                <th style={{ padding: '0.75rem' }}>Group B MAE</th>
                <th style={{ padding: '0.75rem' }}>Group B RMSE</th>
                <th style={{ padding: '0.75rem' }}>Group B R²</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 500 }}>LinearRegression</td>
                <td style={{ padding: '0.75rem' }}>393.94</td><td style={{ padding: '0.75rem' }}>1154.69</td><td style={{ padding: '0.75rem' }}>0.2503</td>
                <td style={{ padding: '0.75rem' }}>43.69</td><td style={{ padding: '0.75rem' }}>275.54</td><td style={{ padding: '0.75rem' }}>0.9573</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 500 }}>DecisionTree</td>
                <td style={{ padding: '0.75rem' }}>138.46</td><td style={{ padding: '0.75rem' }}>687.90</td><td style={{ padding: '0.75rem' }}>0.7339</td>
                <td style={{ padding: '0.75rem' }}>70.25</td><td style={{ padding: '0.75rem' }}>426.00</td><td style={{ padding: '0.75rem' }}>0.8980</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', background: 'rgba(6,182,212,0.05)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 600, color: 'var(--accent-primary)' }}>RandomForest</td>
                <td style={{ padding: '0.75rem' }}>263.91</td><td style={{ padding: '0.75rem' }}>788.67</td><td style={{ padding: '0.75rem' }}>0.6503</td>
                <td style={{ padding: '0.75rem', fontWeight: 600 }}>60.18</td><td style={{ padding: '0.75rem', fontWeight: 600 }}>286.57</td><td style={{ padding: '0.75rem', fontWeight: 600 }}>0.9538</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 500 }}>XGBoost</td>
                <td style={{ padding: '0.75rem' }}>152.19</td><td style={{ padding: '0.75rem' }}>607.72</td><td style={{ padding: '0.75rem' }}>0.7923</td>
                <td style={{ padding: '0.75rem' }}>54.84</td><td style={{ padding: '0.75rem' }}>409.29</td><td style={{ padding: '0.75rem' }}>0.9058</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 500 }}>LightGBM</td>
                <td style={{ padding: '0.75rem' }}>166.04</td><td style={{ padding: '0.75rem' }}>630.36</td><td style={{ padding: '0.75rem' }}>0.7766</td>
                <td style={{ padding: '0.75rem' }}>51.63</td><td style={{ padding: '0.75rem' }}>378.51</td><td style={{ padding: '0.75rem' }}>0.9194</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 500 }}>CatBoost</td>
                <td style={{ padding: '0.75rem' }}>167.62</td><td style={{ padding: '0.75rem' }}>640.35</td><td style={{ padding: '0.75rem' }}>0.7694</td>
                <td style={{ padding: '0.75rem' }}>58.17</td><td style={{ padding: '0.75rem' }}>411.49</td><td style={{ padding: '0.75rem' }}>0.9048</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Section C — Tuned Model Results (Group B, Raw)">
        <div style={{ overflowX: 'auto', marginTop: '1rem' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--fs-sm)', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border-strong)', color: 'var(--text-secondary)' }}>
                <th style={{ padding: '0.75rem' }}>Model</th>
                <th style={{ padding: '0.75rem' }}>Validation MAE</th>
                <th style={{ padding: '0.75rem' }}>Validation RMSE</th>
                <th style={{ padding: '0.75rem' }}>Validation R²</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 500 }}>DecisionTree</td>
                <td style={{ padding: '0.75rem' }}>44.02</td><td style={{ padding: '0.75rem' }}>284.09</td><td style={{ padding: '0.75rem' }}>0.9546</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', background: 'rgba(6,182,212,0.05)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 600, color: 'var(--accent-primary)' }}>RandomForest (Selected)</td>
                <td style={{ padding: '0.75rem', fontWeight: 600 }}>38.97</td><td style={{ padding: '0.75rem', fontWeight: 600 }}>262.07</td><td style={{ padding: '0.75rem', fontWeight: 600 }}>0.9614</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 500 }}>XGBoost</td>
                <td style={{ padding: '0.75rem' }}>49.37</td><td style={{ padding: '0.75rem' }}>360.84</td><td style={{ padding: '0.75rem' }}>0.9268</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 500 }}>LightGBM</td>
                <td style={{ padding: '0.75rem' }}>50.05</td><td style={{ padding: '0.75rem' }}>343.64</td><td style={{ padding: '0.75rem' }}>0.9336</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 500 }}>CatBoost</td>
                <td style={{ padding: '0.75rem' }}>52.45</td><td style={{ padding: '0.75rem' }}>346.95</td><td style={{ padding: '0.75rem' }}>0.9323</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <GlassPanel style={{ padding: 'var(--space-6)', borderRadius: 'var(--radius-lg)', borderLeft: '4px solid var(--accent-success)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <ShieldCheck size={18} style={{ color: 'var(--accent-success)' }} />
          <h2 style={{ fontSize: 'var(--fs-base)', fontWeight: 600 }}>Section D — Final Holdout (Protected December 2016)</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div style={{ padding: '1rem', background: 'var(--surface-primary)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 600, color: 'var(--text-secondary)' }}>Final Random Forest</div>
            <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Group B (Raw)</div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>MAE:</span> <strong>34.36</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>RMSE:</span> <strong>175.65</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>R²:</span> <strong>0.9876</strong></div>
          </div>
          <div style={{ padding: '1rem', background: 'var(--surface-primary)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 600, color: 'var(--text-secondary)' }}>Linear Regression Baseline</div>
            <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Group B (Raw)</div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>MAE:</span> <strong>40.32</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>RMSE:</span> <strong>190.69</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>R²:</span> <strong>0.9854</strong></div>
          </div>
        </div>
      </GlassPanel>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-6)' }}>
        <Card title="Section E — Final Model Parameters">
          <ul style={{ listStyleType: 'none', padding: 0, margin: '1rem 0 0 0', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}>
            <li><strong>Algorithm:</strong> Random Forest</li>
            <li><strong>Target:</strong> Raw (meter_reading)</li>
            <li><strong>Feature Group:</strong> Group B (includes 7 historical features)</li>
            <li><strong>Explainability:</strong> SHAP TreeExplainer</li>
          </ul>
        </Card>

        <Card title="Section F — Research Interpretation">
          <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
            - <strong>Historical features</strong> (Group B) substantially improve prediction accuracy across all evaluated models.<br/><br/>
            - <strong>Random Forest</strong> was selected based on the comprehensive experimental comparison and subsequent hyperparameter tuning, providing the most robust performance.<br/><br/>
            - The final evaluation was performed strictly on a <strong>protected December 2016 holdout</strong> to ensure unbiased generalization metrics.<br/><br/>
            - <strong>SHAP</strong> is used exclusively for model attribution (explaining how features influence the model's prediction), and does not establish causal inference.
          </p>
        </Card>
      </div>
    </div>
  );
};
