import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Activity, Lightbulb, GitMerge,
  CheckCircle, FlaskConical, Building2, FileText,
  Settings, Palette,
} from 'lucide-react';
import './layout.css';

const primaryNav = [
  { name: 'Overview',        path: '/',               icon: LayoutDashboard },
  { name: 'Predict',         path: '/predict',         icon: Activity },
  { name: 'Explain',         path: '/explain',         icon: Lightbulb },
  { name: 'Energy Drivers',  path: '/drivers',         icon: GitMerge },
  { name: 'Recommendations', path: '/recommendations', icon: CheckCircle },
  { name: 'Model Lab',       path: '/model-lab',       icon: FlaskConical },
  { name: 'Buildings',       path: '/buildings',       icon: Building2 },
  { name: 'Reports',         path: '/reports',         icon: FileText },
];

const secondaryNav = [
  { name: 'Settings',     path: '/settings',     icon: Settings },
  { name: 'Theme Studio', path: '/theme-studio', icon: Palette },
];

export const Sidebar = () => (
  <aside className="sidebar" role="navigation" aria-label="Main navigation">
    <div className="sidebar-logo">
      <div className="logo-mark" aria-hidden="true">
        <div className="logo-mark-inner" />
      </div>
      <div>
        <div className="logo-text">BEI Platform</div>
        <div className="logo-sub">Energy Intelligence</div>
      </div>
    </div>

    <nav className="sidebar-nav">
      <div className="nav-section">
        <div className="nav-section-label">Analytics</div>
        {primaryNav.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <item.icon size={16} aria-hidden="true" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </div>

      <div className="nav-divider" />

      <div className="nav-secondary">
        {secondaryNav.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <item.icon size={16} aria-hidden="true" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  </aside>
);