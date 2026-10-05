import React from 'react';
import { useTheme } from '../../store/ThemeContext';
import { CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

/**
 * Theme-aware Recharts component wrappers.
 * All components read from CSS variables at render time,
 * so they automatically adapt when the theme changes.
 */

/** Returns current CSS variable value at runtime */
const cssVar = (name) =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim();

/** Shared grid component using semantic tokens */
export const ThemeGrid = (props) => (
  <CartesianGrid
    strokeDasharray="3 3"
    stroke={cssVar('--border-subtle') || 'rgba(148,163,184,0.2)'}
    vertical={false}
    {...props}
  />
);

/** Shared X-axis using semantic tokens */
export const ThemeXAxis = (props) => (
  <XAxis
    stroke="transparent"
    tick={{ fill: cssVar('--text-secondary') || '#64748b', fontSize: 12, fontFamily: 'Inter, sans-serif' }}
    tickLine={false}
    axisLine={false}
    {...props}
  />
);

/** Shared Y-axis using semantic tokens */
export const ThemeYAxis = (props) => (
  <YAxis
    stroke="transparent"
    tick={{ fill: cssVar('--text-secondary') || '#64748b', fontSize: 12, fontFamily: 'Inter, sans-serif' }}
    tickLine={false}
    axisLine={false}
    width={60}
    {...props}
  />
);

/** Custom tooltip styles using CSS variables */
export const themeTooltipStyle = {
  backgroundColor: 'var(--surface-elevated)',
  borderColor: 'var(--border-strong)',
  borderRadius: 'var(--radius-md)',
  color: 'var(--text-primary)',
  boxShadow: 'var(--shadow-medium)',
  fontFamily: 'Inter, sans-serif',
  fontSize: '0.8125rem',
};

export const ThemeTooltip = (props) => (
  <Tooltip
    contentStyle={themeTooltipStyle}
    itemStyle={{ color: 'var(--text-primary)' }}
    labelStyle={{ color: 'var(--text-secondary)', fontWeight: 500 }}
    {...props}
  />
);

/**
 * Hook returning the four theme-aware chart colors.
 * Re-reads CSS vars on theme change.
 */
export const useChartColors = () => {
  const { theme } = useTheme();
  return React.useMemo(() => ({
    primary:    cssVar('--chart-primary'),
    secondary:  cssVar('--chart-secondary'),
    tertiary:   cssVar('--chart-tertiary'),
    quaternary: cssVar('--chart-quaternary'),
    muted:      cssVar('--text-muted'),
    gridStroke: cssVar('--border-subtle'),
  }), [theme]);
};

/** Standard responsive chart wrapper */
export const ChartContainer = ({ children, height = 240 }) => (
  <ResponsiveContainer width="100%" height={height}>
    {children}
  </ResponsiveContainer>
);