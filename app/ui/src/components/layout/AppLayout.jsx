import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import './layout.css';

export const AppLayout = () => {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-container">
        <TopBar />
        <main className="content-area" id="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};