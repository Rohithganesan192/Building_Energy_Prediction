import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const themes = [
  {
    id: 'solar-glass',
    name: 'Solar Glass',
    description: 'Premium light energy-tech interface',
    tone: 'light',
    accent: '#0ea5e9',
    accentMuted: '#0ea5e920',
    bg: '#f0f5fa',
    bgGradient: 'linear-gradient(135deg, #e8f4ff 0%, #f0f5fa 100%)',
    surface: 'rgba(255,255,255,0.82)',
    border: 'rgba(186,210,235,0.4)',
    textPrimary: '#0c1a2e',
    textSecondary: '#3d5a80',
    chartBars: ['#0ea5e9', '#059669', '#d97706', '#0891b2'],
  },
  {
    id: 'carbon-cyan',
    name: 'Carbon Cyan',
    description: 'AI control-centre dark mode',
    tone: 'dark',
    accent: '#06b6d4',
    accentMuted: '#06b6d420',
    bg: '#0b0f18',
    bgGradient: 'linear-gradient(135deg, #0d1320 0%, #0b0f18 100%)',
    surface: 'rgba(18,26,42,0.82)',
    border: 'rgba(6,182,212,0.2)',
    textPrimary: '#dde8f2',
    textSecondary: '#7da4c0',
    chartBars: ['#06b6d4', '#14b8a6', '#38bdf8', '#10b981'],
  },
  {
    id: 'ember-grid',
    name: 'Ember Grid',
    description: 'Dark industrial energy platform',
    tone: 'dark',
    accent: '#c8192e',
    accentMuted: '#c8192e20',
    bg: '#150c0e',
    bgGradient: 'linear-gradient(135deg, #1e0e11 0%, #150c0e 100%)',
    surface: 'rgba(42,16,22,0.82)',
    border: 'rgba(200,25,46,0.25)',
    textPrimary: '#f5e8e8',
    textSecondary: '#b89090',
    chartBars: ['#c8192e', '#d97706', '#f04455', '#fb923c'],
  },
  {
    id: 'frosted-air',
    name: 'Frosted Air',
    description: 'Futuristic translucent light theme',
    tone: 'light',
    accent: '#0ea5e9',
    accentMuted: '#0ea5e918',
    bg: '#e8f2f9',
    bgGradient: 'linear-gradient(135deg, #e0f0ff 0%, #d6eaf6 100%)',
    surface: 'rgba(255,255,255,0.45)',
    border: 'rgba(255,255,255,0.65)',
    textPrimary: '#0a1628',
    textSecondary: '#2c4a6e',
    chartBars: ['#0ea5e9', '#14b8a6', '#38bdf8', '#059669'],
  },
  {
    id: 'deep-ocean',
    name: 'Deep Ocean',
    description: 'Navy engineering analytics platform',
    tone: 'dark',
    accent: '#38dcbe',
    accentMuted: '#38dcbe1a',
    bg: '#060e1c',
    bgGradient: 'linear-gradient(135deg, #081220 0%, #060e1c 100%)',
    surface: 'rgba(10,22,42,0.8)',
    border: 'rgba(56,220,190,0.14)',
    textPrimary: '#b8d4e8',
    textSecondary: '#6898b8',
    chartBars: ['#38dcbe', '#3b82f6', '#06b6d4', '#f5b942'],
  },
  {
    id: 'industrial-ember',
    name: 'Industrial Ember',
    description: 'Copper-toned engineering dashboard',
    tone: 'dark',
    accent: '#c97a28',
    accentMuted: '#c97a2820',
    bg: '#131210',
    bgGradient: 'linear-gradient(135deg, #1a1714 0%, #131210 100%)',
    surface: 'rgba(35,30,25,0.82)',
    border: 'rgba(201,122,40,0.22)',
    textPrimary: '#f0ebe4',
    textSecondary: '#a89880',
    chartBars: ['#c97a28', '#0891b2', '#e8a84a', '#10b981'],
  },
];

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('bei-theme') || 'solar-glass';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('bei-theme', theme);
  }, [theme]);

  const currentTheme = themes.find((t) => t.id === theme) || themes[0];

  return (
    <ThemeContext.Provider value={{ theme, setTheme, themes, currentTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used inside ThemeProvider');
  return ctx;
};