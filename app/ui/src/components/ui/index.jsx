import React from 'react';
import './ui.css';

export const Badge = ({ children, variant = 'neutral', className = '' }) => (
  <span className={`badge badge-${variant} ${className}`.trim()}>{children}</span>
);

export const StatusBadge = ({ status = 'neutral', text }) => (
  <div className={`status-badge ${status}`}>
    <span className="status-dot" />
    {text}
  </div>
);

export const MetricDisplay = ({ label, value, unit }) => (
  <div className="metric-display">
    <span className="metric-label">{label}</span>
    <span className="metric-value">
      {value}
      {unit && <span className="metric-unit"> {unit}</span>}
    </span>
  </div>
);

export const ProgressBar = ({ value = 0, max = 100, className = '' }) => (
  <div className={`progress-bar ${className}`.trim()}>
    <div className="progress-fill" style={{ width: `${Math.min(100, (value / max) * 100)}%` }} />
  </div>
);

export const Divider = ({ className = '' }) => (
  <div className={`divider ${className}`.trim()} />
);

export const SectionHeader = ({ title, subtitle, action }) => (
  <div className="section-header">
    <div>
      <div className="section-title">{title}</div>
      {subtitle && <div className="section-subtitle">{subtitle}</div>}
    </div>
    {action && <div>{action}</div>}
  </div>
);

export const EmptyState = ({ icon: Icon, title, description }) => (
  <div className="state-container">
    {Icon && <Icon size={40} className="state-icon" />}
    <div className="state-title">{title}</div>
    {description && <div className="state-desc">{description}</div>}
  </div>
);

export const LoadingState = ({ message = 'Loading...' }) => (
  <div className="state-container">
    <div className="state-title">{message}</div>
  </div>
);

export const ErrorState = ({ message }) => (
  <div className="state-container">
    <div className="state-title" style={{ color: 'var(--accent-danger)' }}>Error</div>
    {message && <div className="state-desc">{message}</div>}
  </div>
);

export const Tabs = ({ tabs = [], activeTab, onChange }) => (
  <div className="tabs" role="tablist">
    {tabs.map((tab) => (
      <button
        key={tab.id}
        role="tab"
        aria-selected={activeTab === tab.id}
        className={`tab ${activeTab === tab.id ? 'active' : ''}`}
        onClick={() => onChange(tab.id)}
      >
        {tab.label}
      </button>
    ))}
  </div>
);
