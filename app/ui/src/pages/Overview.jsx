import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { useTheme } from '../store/ThemeContext';
import { GlassPanel } from '../components/ui/Card';
import { Badge, StatusBadge } from '../components/ui/index';
import { Button } from '../components/ui/Button';
import {
  Zap, ArrowRight, Database, GitBranch,
  BarChart2, CheckCircle2, Clock, ChevronRight,
  Shield,
} from 'lucide-react';

/* ─────────────────────────────────────────────
   STATIC RESEARCH DATA (verified Phase 8 / 9)
   ───────────────────────────────────────────── */
const MODEL_METRICS = [
  { label: 'Final Model R²',       value: '0.9876', sub: 'December 2016 holdout' },
  { label: 'Holdout MAE',          value: '34.36',  sub: 'Mean absolute error' },
  { label: 'Holdout RMSE',         value: '175.65', sub: 'Root mean square error' },
  { label: 'Model',                value: 'Random Forest', sub: 'Group B · Raw target', large: false },
  { label: 'Evaluation',           value: 'Dec 2016', sub: 'Protected holdout', large: false },
];

const SHAP_GROUPS = [
  { name: 'Historical', pct: 95.14, color: '--chart-1' },
  { name: 'Temporal',   pct: 2.31,  color: '--chart-2' },
  { name: 'Weather',    pct: 1.22,  color: '--chart-3' },
  { name: 'Building',   pct: 0.84,  color: '--chart-4' },
  { name: 'Meter',      pct: 0.46,  color: '--chart-5' },
];

const SHAP_DRIVERS = [
  { feature: 'lag_1',           value: 373.60, group: 'Historical' },
  { feature: 'lag_24',          value: 61.42,  group: 'Historical' },
  { feature: 'rolling_mean_24', value: 23.17,  group: 'Historical' },
  { feature: 'lag_168',         value: 8.59,   group: 'Historical' },
  { feature: 'hour_cos',        value: 4.13,   group: 'Temporal'   },
];

const WORKFLOW_STEPS = [
  { label: 'Building Input',  sub: 'Context + history' },
  { label: 'ML Prediction',   sub: 'Random Forest'     },
  { label: 'SHAP Explain',    sub: 'Feature attribution' },
  { label: 'Recommendations', sub: 'Domain rules'      },
];

const RESEARCH_ROWS = [
  { label: 'Dataset',       value: 'ASHRAE Great Energy Predictor III' },
  { label: 'Model family',  value: 'Tree-based ensemble (Random Forest)' },
  { label: 'Primary XAI',   value: 'SHAP (TreeExplainer, exact values)' },
  { label: 'Features',      value: 'Temporal · Building · Weather · Historical' },
  { label: 'Evaluation',    value: 'Chronological split · Protected Dec. holdout' },
];

/* ─────────────────────────────────────────────
   ANIMATED BAR — mounts width transition
   ───────────────────────────────────────────── */
const AnimBar = ({ pct, color, height = 7, delay = 0 }) => {
  const [width, setWidth] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setWidth(pct), 120 + delay);
    return () => clearTimeout(t);
  }, [pct, delay]);
  return (
    <div style={{ flex: 1, height, background: 'var(--surface-secondary)', borderRadius: 'var(--radius-pill)', overflow: 'hidden' }}>
      <div style={{
        height: '100%',
        width: `${width}%`,
        background: `var(${color})`,
        borderRadius: 'var(--radius-pill)',
        transition: 'width 0.8s cubic-bezier(0.4,0,0.2,1)',
      }} />
    </div>
  );
};

/* ─────────────────────────────────────────────
   DRIVER BAR — horizontal, normalized to max
   ───────────────────────────────────────────── */
const DriverBar = ({ value, maxVal, color, delay }) => {
  const [width, setWidth] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setWidth((value / maxVal) * 100), 200 + delay);
    return () => clearTimeout(t);
  }, [value, maxVal, delay]);
  return (
    <div style={{ flex: 1, height: 6, background: 'var(--surface-secondary)', borderRadius: 'var(--radius-pill)', overflow: 'hidden' }}>
      <div style={{
        height: '100%',
        width: `${width}%`,
        background: `var(${color})`,
        borderRadius: 'var(--radius-pill)',
        transition: 'width 0.9s cubic-bezier(0.4,0,0.2,1)',
      }} />
    </div>
  );
};

/* ─────────────────────────────────────────────
   CUSTOM DONUT TOOLTIP
   ───────────────────────────────────────────── */
const DonutTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{
      background: 'var(--surface-elevated)',
      border: '1px solid var(--border-strong)',
      borderRadius: 'var(--radius-sm)',
      padding: '6px 12px',
      boxShadow: 'var(--shadow-medium)',
      fontSize: 'var(--fs-xs)',
      color: 'var(--text-primary)',
      fontFamily: 'var(--font-primary)',
    }}>
      <strong>{d.name}</strong>: {d.pct}%
    </div>
  );
};

/* ─────────────────────────────────────────────
   PANEL WRAPPER — consistent card surface
   ───────────────────────────────────────────── */
const Panel = ({ children, style }) => (
  <div style={{
    background: 'var(--surface-primary)',
    border: '1px solid var(--border-subtle)',
    borderRadius: 'var(--radius-md)',
    boxShadow: 'var(--shadow-soft)',
    padding: 'var(--space-5)',
    transition: 'border-color 0.2s, box-shadow 0.2s',
    ...style,
  }}>
    {children}
  </div>
);

const PanelLabel = ({ text, badge }) => (
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-4)' }}>
    <span style={{
      fontSize: 'var(--fs-xs)',
      fontWeight: 600,
      color: 'var(--text-muted)',
      textTransform: 'uppercase',
      letterSpacing: '0.08em',
    }}>{text}</span>
    {badge}
  </div>
);

/* ═════════════════════════════════════════════
   OVERVIEW PAGE
   ═════════════════════════════════════════════ */
export const Overview = () => {
  const navigate = useNavigate();
  const { theme } = useTheme();

  /* Read chart colors from CSS vars after each theme change */
  const [chartColors, setChartColors] = useState([]);
  useEffect(() => {
    const el = document.documentElement;
    const style = getComputedStyle(el);
    setChartColors(
      ['--chart-1', '--chart-2', '--chart-3', '--chart-4', '--chart-5']
        .map((v) => style.getPropertyValue(v).trim())
    );
  }, [theme]);

  const pieData = SHAP_GROUPS.map((g, i) => ({
    name: g.name,
    value: g.pct,
    pct: g.pct,
    fill: chartColors[i] || '#888',
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)', maxWidth: 1400 }}>

      {/* ── 1. PAGE HEADER ── */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
        <div>
          <h1 className="page-title">Intelligence Overview</h1>
          <p className="page-subtitle">Building energy prediction, model intelligence, and operational context.</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexShrink: 0 }}>
          <StatusBadge status="success" text="Model Ready" />
          <Button variant="primary" onClick={() => navigate('/predict')}>
            <Zap size={14} aria-hidden="true" />
            New Prediction
          </Button>
        </div>
      </div>

      {/* ── 2. MODEL PERFORMANCE STRIP ── */}
      <GlassPanel style={{ padding: 'var(--space-5)', borderRadius: 'var(--radius-lg)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
          <Shield size={13} style={{ color: 'var(--accent-success)' }} aria-hidden="true" />
          <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--accent-success)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.07em' }}>
            Protected Evaluation — December 2016 Holdout
          </span>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-8)', alignItems: 'flex-end' }}>
          {MODEL_METRICS.map((m) => (
            <div key={m.label} style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.07em' }}>
                {m.label}
              </span>
              <span style={{
                fontFamily: 'var(--font-display)',
                fontSize: m.large === false ? 'var(--fs-lg)' : 'var(--fs-2xl)',
                fontWeight: 700,
                color: 'var(--text-primary)',
                lineHeight: 1,
                letterSpacing: '-0.01em',
              }}>
                {m.value}
              </span>
              <span style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)' }}>{m.sub}</span>
            </div>
          ))}
        </div>
      </GlassPanel>

      {/* ── 3 + 6. ASYMMETRIC ROW: Intelligence State + Research Context ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 'var(--space-4)', alignItems: 'stretch' }}>

        {/* 3. CURRENT INTELLIGENCE */}
        <Panel>
          <PanelLabel text="Current Intelligence" badge={<Badge variant="neutral">Awaiting Input</Badge>} />

          {/* Workflow diagram */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 0,
            marginBottom: 'var(--space-5)',
            overflowX: 'auto',
          }}>
            {WORKFLOW_STEPS.map((step, i) => (
              <React.Fragment key={step.label}>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  padding: 'var(--space-3) var(--space-4)',
                  background: 'var(--surface-secondary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  minWidth: 110,
                  flexShrink: 0,
                  transition: 'border-color 0.2s',
                }}>
                  <span style={{
                    fontSize: 'var(--fs-xs)',
                    fontWeight: 700,
                    color: 'var(--text-secondary)',
                    textAlign: 'center',
                    letterSpacing: '0.02em',
                  }}>{step.label}</span>
                  <span style={{
                    fontSize: 'var(--fs-2xs)',
                    color: 'var(--text-muted)',
                    marginTop: 3,
                    textAlign: 'center',
                  }}>{step.sub}</span>
                </div>
                {i < WORKFLOW_STEPS.length - 1 && (
                  <ArrowRight
                    size={14}
                    style={{ color: 'var(--text-muted)', flexShrink: 0, margin: '0 4px' }}
                    aria-hidden="true"
                  />
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Empty / ready state */}
          <div style={{
            textAlign: 'center',
            padding: 'var(--space-8) var(--space-6)',
            borderRadius: 'var(--radius-sm)',
            border: '1px dashed var(--border-strong)',
            background: 'var(--surface-secondary)',
          }}>
            <div style={{
              width: 40, height: 40, borderRadius: '50%',
              background: 'var(--glow-primary)',
              border: '1.5px solid var(--border-accent)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto var(--space-3)',
            }}>
              <BarChart2 size={18} style={{ color: 'var(--accent-primary)' }} aria-hidden="true" />
            </div>
            <h3 style={{ fontSize: 'var(--fs-base)', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 'var(--space-2)' }}>
              No active prediction
            </h3>
            <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-muted)', maxWidth: 380, margin: '0 auto var(--space-5)', lineHeight: 'var(--lh-relaxed)' }}>
              Enter building context and historical energy state on the Predict page to generate a prediction and explanation.
            </p>
            <Button variant="primary" onClick={() => navigate('/predict')}>
              Create Prediction
              <ChevronRight size={14} aria-hidden="true" />
            </Button>
          </div>
        </Panel>

        {/* 6. RESEARCH CONTEXT */}
        <Panel style={{ display: 'flex', flexDirection: 'column' }}>
          <PanelLabel text="Research Context" badge={<Database size={14} style={{ color: 'var(--text-muted)' }} />} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', flex: 1 }}>
            {RESEARCH_ROWS.map((row) => (
              <div key={row.label} style={{
                padding: 'var(--space-3)',
                background: 'var(--surface-secondary)',
                borderRadius: 'var(--radius-xs)',
                border: '1px solid var(--border-subtle)',
              }}>
                <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 3 }}>
                  {row.label}
                </div>
                <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', lineHeight: 'var(--lh-normal)', fontWeight: 500 }}>
                  {row.value}
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      {/* ── 4 + 5. ASYMMETRIC ROW: SHAP Groups + SHAP Drivers ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>

        {/* 4. GLOBAL MODEL INTELLIGENCE */}
        <Panel>
          <PanelLabel text="Global Model Intelligence" badge={<Badge variant="accent">SHAP</Badge>} />

          <div style={{ display: 'flex', gap: 'var(--space-5)', alignItems: 'center', flexWrap: 'wrap' }}>
            {/* Donut chart */}
            <div style={{ flexShrink: 0 }}>
              <ResponsiveContainer width={160} height={160}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={48}
                    outerRadius={72}
                    paddingAngle={2}
                    dataKey="value"
                    startAngle={90}
                    endAngle={-270}
                    animationBegin={200}
                    animationDuration={1000}
                  >
                    {pieData.map((entry, i) => (
                      <Cell key={entry.name} fill={entry.fill} stroke="none" />
                    ))}
                  </Pie>
                  <Tooltip content={<DonutTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Group breakdown */}
            <div style={{ flex: 1, minWidth: 160, display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              {SHAP_GROUPS.map((g, i) => (
                <div key={g.name} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <div style={{ width: 8, height: 8, borderRadius: 2, background: chartColors[i] || 'var(--text-muted)', flexShrink: 0 }} />
                  <span style={{ width: 68, fontSize: 'var(--fs-xs)', color: 'var(--text-secondary)', fontWeight: 500, flexShrink: 0 }}>
                    {g.name}
                  </span>
                  <AnimBar pct={g.pct} color={g.color} delay={i * 100} />
                  <span style={{ width: 44, fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', textAlign: 'right', flexShrink: 0, fontVariantNumeric: 'tabular-nums' }}>
                    {g.pct}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div style={{
            marginTop: 'var(--space-4)',
            padding: 'var(--space-3)',
            background: 'var(--surface-secondary)',
            borderRadius: 'var(--radius-xs)',
            borderLeft: '2.5px solid var(--accent-warning)',
          }}>
            <p style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', lineHeight: 'var(--lh-relaxed)' }}>
              Historical features dominate model attribution in the evaluated sample.{' '}
              <strong style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>
                SHAP attribution indicates model contribution, not causal influence.
              </strong>
            </p>
          </div>
        </Panel>

        {/* 5. TOP SHAP DRIVERS */}
        <Panel>
          <PanelLabel
            text="Top SHAP Drivers"
            badge={
              <Button variant="ghost" size="sm" onClick={() => navigate('/explain')} style={{ fontSize: 'var(--fs-xs)' }}>
                View Explanation <ChevronRight size={12} />
              </Button>
            }
          />

          <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', marginBottom: 'var(--space-3)', textTransform: 'uppercase', letterSpacing: '0.07em', fontWeight: 600 }}>
            Mean |SHAP| — Global analysis (Phase 9, 1,000 validation rows)
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            {SHAP_DRIVERS.map((d, i) => (
              <div key={d.feature}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-1)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                    <span style={{
                      fontFamily: 'var(--font-mono, monospace)',
                      fontSize: 'var(--fs-sm)',
                      color: 'var(--text-primary)',
                      fontWeight: 500,
                    }}>
                      {d.feature}
                    </span>
                    <span style={{
                      fontSize: 'var(--fs-2xs)',
                      color: 'var(--text-muted)',
                      background: 'var(--surface-secondary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-pill)',
                      padding: '1px 6px',
                    }}>
                      {d.group}
                    </span>
                  </div>
                  <span style={{
                    fontSize: 'var(--fs-sm)',
                    color: 'var(--accent-primary)',
                    fontWeight: 700,
                    fontVariantNumeric: 'tabular-nums',
                    letterSpacing: '-0.01em',
                  }}>
                    {d.value.toFixed(2)}
                  </span>
                </div>
                <DriverBar
                  value={d.value}
                  maxVal={373.60}
                  color={i === 0 ? '--chart-1' : i === SHAP_DRIVERS.length - 1 ? '--chart-2' : '--chart-1'}
                  delay={i * 80}
                />
              </div>
            ))}
          </div>

          <div style={{ marginTop: 'var(--space-4)' }}>
            <Button variant="outline" onClick={() => navigate('/explain')} style={{ width: '100%', justifyContent: 'center' }}>
              View Full SHAP Explanation
              <ArrowRight size={13} />
            </Button>
          </div>
        </Panel>
      </div>

      {/* ── 7. RECOMMENDATION ENGINE STATUS ── */}
      <Panel style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-6)', flexWrap: 'wrap' }}>
        <div style={{ flex: '0 0 auto' }}>
          <div style={{
            width: 44, height: 44,
            borderRadius: 'var(--radius-sm)',
            background: 'var(--surface-secondary)',
            border: '1px solid var(--border-subtle)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <GitBranch size={20} style={{ color: 'var(--text-muted)' }} aria-hidden="true" />
          </div>
        </div>

        <div style={{ flex: 1, minWidth: 220 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-2)' }}>
            <span style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--fs-base)', fontWeight: 600, color: 'var(--text-primary)' }}>
              Recommendation Engine
            </span>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 5,
              fontSize: 'var(--fs-xs)', color: 'var(--accent-warning)',
              background: 'rgba(217,119,6,0.1)',
              border: '1px solid rgba(217,119,6,0.25)',
              borderRadius: 'var(--radius-pill)',
              padding: '2px 8px',
              fontWeight: 500,
            }}>
              <Clock size={11} aria-hidden="true" />
              Awaiting prediction
            </div>
          </div>
          <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-muted)', lineHeight: 'var(--lh-relaxed)', marginBottom: 'var(--space-2)' }}>
            Generate a prediction with SHAP output to activate evidence-based recommendation rules.
          </p>
          <p style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', fontStyle: 'italic', lineHeight: 'var(--lh-relaxed)' }}>
            Recommendations are decision-support suggestions based on model attribution and domain rules; they do not establish causal energy savings.
          </p>
        </div>

        <div style={{ flexShrink: 0, alignSelf: 'center' }}>
          <Button variant="secondary" onClick={() => navigate('/recommendations')}>
            Go to Recommendations
            <ChevronRight size={14} />
          </Button>
        </div>
      </Panel>

      {/* ── RESPONSIVE STYLE ── */}
      <style>{`
        @media (max-width: 1100px) {
          .ov-split-a { grid-template-columns: 1fr !important; }
          .ov-split-b { grid-template-columns: 1fr !important; }
        }
        @media (max-width: 768px) {
          .ov-metrics-wrap { flex-direction: column; gap: 1rem; }
        }
      `}</style>
    </div>
  );
};