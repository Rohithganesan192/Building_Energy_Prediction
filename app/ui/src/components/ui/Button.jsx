import React from 'react';
import './ui.css';

export const Button = ({
  children,
  variant = 'primary',
  size = '',
  className = '',
  ...props
}) => {
  const sizeClass = size ? `btn-${size}` : '';
  return (
    <button className={`btn btn-${variant} ${sizeClass} ${className}`.trim()} {...props}>
      {children}
    </button>
  );
};

export const IconButton = ({
  icon: Icon,
  label,
  active = false,
  className = '',
  size = 18,
  ...props
}) => {
  return (
    <button
      className={`btn-icon ${active ? 'active' : ''} ${className}`.trim()}
      aria-label={label}
      title={label}
      {...props}
    >
      <Icon size={size} />
    </button>
  );
};