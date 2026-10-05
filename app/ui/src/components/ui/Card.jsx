import React from 'react';
import './ui.css';

export const Card = ({ children, className = '', title, action }) => {
  return (
    <div className={`card ${className}`.trim()}>
      {title && (
        <div className="card-header">
          <h3 className="card-title">{title}</h3>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="card-body">{children}</div>
    </div>
  );
};

export const GlassPanel = ({ children, className = '', style }) => {
  return (
    <div className={`glass-panel ${className}`.trim()} style={style}>
      {children}
    </div>
  );
};