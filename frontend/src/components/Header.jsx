import { useState, useEffect } from 'react';

export default function Header({ health }) {
  const connected = health?.tigergraph_connected || false;

  return (
    <header className="header">
      <div className="header-logo">
        <div className="logo-icon">🛡️</div>
        <div>
          <h1>GraphGuard AI</h1>
          <div className="subtitle">Fraud Intelligence System</div>
        </div>
      </div>
      <div className="header-status">
        <div className={`status-badge ${connected ? 'connected' : 'disconnected'}`}>
          <span className={`status-dot ${connected ? 'online' : 'offline'}`}></span>
          TigerGraph {connected ? 'Connected' : 'Disconnected'}
        </div>
        <div className="status-badge connected" style={{ background: 'rgba(0, 212, 255, 0.08)', borderColor: 'rgba(0, 212, 255, 0.25)', color: 'var(--cyan)' }}>
          ⚡ Real-time Analysis
        </div>
      </div>
    </header>
  );
}
