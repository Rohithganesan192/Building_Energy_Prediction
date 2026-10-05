import React from 'react';
import './ui.css';

export const Input = ({ className = '', ...props }) => (
  <input className={`input ${className}`.trim()} {...props} />
);

export const Select = ({ className = '', children, ...props }) => (
  <select className={`input ${className}`.trim()} {...props}>
    {children}
  </select>
);