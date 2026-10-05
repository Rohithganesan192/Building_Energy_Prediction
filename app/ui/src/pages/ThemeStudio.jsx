import React, { useState } from 'react';
import { useTheme } from '../store/ThemeContext';
import { CheckCircle2 } from 'lucide-react';

/* ---- Inline mini-preview component ---- */
const MiniPreview = ({ t }) => {
  const barData = [65, 90, 45, 78, 55, 82];
  const isDark = t.tone === 'dark';

  return (
    <div
      style={{
        height: 180,
        borderRadius: 6,
        overflow: 'hidden',
        background: t.bgGradient,
        display: 'flex',
        gap: 0,
        fontFamily: "'Inter', sans-serif",
        position: 'relative',
      }}
      aria-hidden="true"
    >
      {/* Mini sidebar */}
      <div style={{
        width: 46,
        background: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(255,255,255,0.7)',
        borderRight: `1px solid ${t.border}`,
        display: 'flex',
        flexDirection: 'column',
        padding: '8px 5px',
        gap: 4,
        flexShrink: 0,
      }}>
        <div style={{ width: 22, height: 6, borderRadius: 3, background: t.accent, marginBottom: 8, boxShadow: `0 0 6px ${t.accent}60` }} />
        {[1, 0.6, 0.6, 0.6, 1, 0.6, 0.6].map((op, i) => (
          <div key={i} style={{
            height: 5,
            borderRadius: 2,
            background: op === 1 ? `${t.accent}cc` : (isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.1)'),
            width: op === 1 ? '90%' : `${55 + i * 5}%`,
          }} />
        ))}
      </div>

      {/* Mini content */}
      <div style={{ flex: 1, padding: '8px 10px', display: 'flex', flexDirection: 'column', gap: 6, minWidth: 0 }}>
        {/* Mini topbar */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingBottom: 5,
          borderBottom: `1px solid ${t.border}`,
        }}>
          <div style={{ width: 60, height: 5, borderRadius: 2, background: isDark ? 'rgba(255,255,255,0.25)' : 'rgba(0,0,0,0.2)' }} />
          <div style={{
            width: 24, height: 5, borderRadius: 10,
            background: t.accent, opacity: 0.85,
            boxShadow: `0 0 5px ${t.accent}50`,
          }} />
        </div>

        {/* Mini stat row */}
        <div style={{ display: 'flex', gap: 4 }}>
          {[{ v: '0.9876', l: 'R²' }, { v: '34.4', l: 'MAE' }, { v: '175.6', l: 'RMSE' }].map((s, i) => (
            <div key={i} style={{
              flex: 1,
              background: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.75)',
              border: `1px solid ${t.border}`,
              borderRadius: 3,
              padding: '3px 4px',
            }}>
              <div style={{ fontSize: 7, color: isDark ? 'rgba(255,255,255,0.35)' : 'rgba(0,0,0,0.35)', lineHeight: 1, marginBottom: 1 }}>{s.l}</div>
              <div style={{ fontSize: 9, fontWeight: 700, color: i === 0 ? t.accent : (isDark ? 'rgba(255,255,255,0.75)' : 'rgba(0,0,0,0.7)'), lineHeight: 1 }}>{s.v}</div>
            </div>
          ))}
        </div>

        {/* Mini chart */}
        <div style={{
          flex: 1,
          background: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(255,255,255,0.6)',
          border: `1px solid ${t.border}`,
          borderRadius: 3,
          padding: '5px 6px',
          display: 'flex',
          flexDirection: 'column',
          gap: 3,
        }}>
          <div style={{ fontSize: 6, color: isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>SHAP Group Attribution</div>
          <div style={{ flex: 1, display: 'flex', alignItems: 'flex-end', gap: 3, paddingTop: 4 }}>
            {barData.map((v, i) => (
              <div key={i} style={{
                flex: 1,
                height: `${v}%`,
                borderRadius: '2px 2px 0 0',
                background: i === 0 ? t.accent : `${t.chartBars[i % t.chartBars.length]}99`,
                transition: 'height 0.3s ease',
              }} />
            ))}
          </div>
        </div>

        {/* Mini button row */}
        <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
          <div style={{
            flex: 1, height: 14, borderRadius: 2,
            background: t.accent,
            boxShadow: `0 0 6px ${t.accent}50`,
          }} />
          <div style={{
            width: 14, height: 14, borderRadius: '50%',
            background: t.accent,
            opacity: 0.8,
            boxShadow: `0 0 5px ${t.accent}50`,
          }} />
          <div style={{
            fontSize: 6, fontWeight: 600,
            color: t.accent,
            letterSpacing: '0.03em',
            display: 'flex', alignItems: 'center', gap: 2,
          }}>
            <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#10b981', display: 'inline-block', boxShadow: '0 0 4px #10b981' }} />
            Active
          </div>
        </div>
      </div>
    </div>
  );
};

export const ThemeStudio = () => {
  const { theme, setTheme, themes } = useTheme();
  const [hovered, setHovered] = useState(null);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: 1200 }}>
      <div className="page-header">
        <h1 className="page-title">Theme Studio</h1>
        <p className="page-subtitle">
          Six distinct visual identities for the Building Energy Intelligence platform.
          Each theme is applied instantly and persisted across sessions.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(310px, 1fr))',
        gap: 'var(--space-5)',
      }}>
        {themes.map((t) => {
          const isActive = theme === t.id;
          const isHov = hovered === t.id;

          return (
            <div
              key={t.id}
              role="button"
              tabIndex={0}
              aria-pressed={isActive}
              aria-label={`Select ${t.name} theme`}
              onClick={() => setTheme(t.id)}
              onKeyDown={(e) => e.key === 'Enter' && setTheme(t.id)}
              onMouseEnter={() => setHovered(t.id)}
              onMouseLeave={() => setHovered(null)}
              style={{
                borderRadius: 'var(--radius-md)',
                border: `1.5px solid ${isActive ? t.accent : (isHov ? `${t.accent}60` : 'var(--border-subtle)')}`,
                boxShadow: isActive
                  ? `0 0 0 1px ${t.accent}40, 0 8px 32px ${t.accent}25, var(--shadow-medium)`
                  : isHov ? 'var(--shadow-medium)' : 'var(--shadow-soft)',
                cursor: 'pointer',
                overflow: 'hidden',
                transition: 'all 0.2s ease',
                background: 'var(--surface-primary)',
                backdropFilter: 'blur(var(--surface-glass-blur, 16px))',
                WebkitBackdropFilter: 'blur(var(--surface-glass-blur, 16px))',
                transform: isHov && !isActive ? 'translateY(-2px)' : 'none',
              }}
            >
              {/* Preview */}
              <div style={{ margin: 12, borderRadius: 4, overflow: 'hidden', boxShadow: `0 2px 12px ${t.accent}30` }}>
                <MiniPreview t={t} />
              </div>

              {/* Info footer */}
              <div style={{ padding: '0 16px 16px' }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: 6,
                }}>
                  <div>
                    <div style={{
                      fontFamily: "'Manrope', sans-serif",
                      fontWeight: 700,
                      fontSize: '1rem',
                      color: 'var(--text-primary)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                    }}>
                      <span style={{
                        display: 'inline-block',
                        width: 9,
                        height: 9,
                        borderRadius: '50%',
                        background: t.accent,
                        boxShadow: `0 0 6px ${t.accent}80`,
                        flexShrink: 0,
                      }} />
                      {t.name}
                    </div>
                    <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', marginTop: 2 }}>
                      {t.description}
                    </div>
                  </div>
                  {isActive && (
                    <CheckCircle2
                      size={18}
                      style={{ color: t.accent, flexShrink: 0 }}
                      aria-label="Active theme"
                    />
                  )}
                </div>

                <div style={{ display: 'flex', gap: 6, marginTop: 10 }}>
                  {t.chartBars.map((c, i) => (
                    <div
                      key={i}
                      title={c}
                      style={{
                        flex: 1,
                        height: 4,
                        borderRadius: 2,
                        background: c,
                        opacity: 0.8,
                      }}
                    />
                  ))}
                </div>

                <button
                  style={{
                    marginTop: 12,
                    width: '100%',
                    padding: '0.45rem 0',
                    borderRadius: 'var(--radius-sm)',
                    border: `1.5px solid ${isActive ? t.accent : 'var(--border-strong)'}`,
                    background: isActive ? t.accent : 'transparent',
                    color: isActive ? '#fff' : 'var(--text-secondary)',
                    fontFamily: "'Inter', sans-serif",
                    fontWeight: 600,
                    fontSize: '0.8125rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    letterSpacing: '0.01em',
                  }}
                  onClick={(e) => { e.stopPropagation(); setTheme(t.id); }}
                >
                  {isActive ? '✓ Active Theme' : 'Apply Theme'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer note */}
      <div style={{
        padding: 'var(--space-4) var(--space-5)',
        background: 'var(--surface-secondary)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        fontSize: 'var(--fs-sm)',
        color: 'var(--text-muted)',
        lineHeight: 'var(--lh-relaxed)',
        display: 'flex',
        alignItems: 'flex-start',
        gap: 'var(--space-3)',
      }}>
        <div style={{ flexShrink: 0, marginTop: 2 }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--accent-primary)', boxShadow: '0 0 6px var(--glow-primary)' }} />
        </div>
        <div>
          <strong style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>Theme System</strong>
          {' — '}Theme selection is persisted in local storage and applied instantly via CSS custom properties (no page reload).
          All six themes share the same information architecture and component behavior.
          No purple or violet is used in any theme.
          Chart colors, borders, shadows, and glow effects are fully theme-aware.
        </div>
      </div>
    </div>
  );
};