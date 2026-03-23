import { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import StatsCards from './components/StatsCards';
import RiskMeter from './components/RiskMeter';
import GraphView from './components/GraphView';
import ExplanationPanel from './components/ExplanationPanel';
import './index.css';

const API = 'http://localhost:8000';

export default function App() {
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const [clusters, setClusters] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [phones, setPhones] = useState([]);
  const [users, setUsers] = useState([]);
  const [searchResult, setSearchResult] = useState(null);
  const [selectedResult, setSelectedResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch all initial data
  const fetchInitialData = useCallback(async () => {
    try {
      const [healthRes, statsRes, graphRes, clustersRes, phonesRes, usersRes] = await Promise.allSettled([
        fetch(`${API}/health`).then(r => r.json()),
        fetch(`${API}/stats`).then(r => r.json()),
        fetch(`${API}/graph-data`).then(r => r.json()),
        fetch(`${API}/fraud-clusters`).then(r => r.json()),
        fetch(`${API}/phones`).then(r => r.json()),
        fetch(`${API}/users`).then(r => r.json()),
      ]);

      if (healthRes.status === 'fulfilled') setHealth(healthRes.value);
      if (statsRes.status === 'fulfilled') setStats(statsRes.value);
      if (graphRes.status === 'fulfilled') setGraphData(graphRes.value);
      if (clustersRes.status === 'fulfilled') setClusters(clustersRes.value);
      if (phonesRes.status === 'fulfilled') setPhones(phonesRes.value);
      if (usersRes.status === 'fulfilled') setUsers(usersRes.value);
    } catch (err) {
      console.error('Failed to fetch initial data:', err);
      setError('Cannot connect to backend. Make sure the FastAPI server is running on port 8000.');
    } finally {
      setInitialLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  // Search handler
  const handleSearch = async (query, type) => {
    setLoading(true);
    setError(null);
    setSearchResult(null);
    setSelectedResult(null);

    try {
      let res;
      if (type === 'phone') {
        res = await fetch(`${API}/check-number`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone_number: query }),
        });
      } else {
        res = await fetch(`${API}/check-user`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: query }),
        });
      }

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Error ${res.status}`);
      }

      const data = await res.json();

      if (type === 'phone') {
        setSearchResult(data);
        // Auto-select highest risk user
        if (data.results && data.results.length > 0) {
          setSelectedResult(data.results[0]);
        }
      } else {
        // Single user result
        setSearchResult({ results: [data], total_users: 1 });
        setSelectedResult(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Get highlighted nodes for graph
  const highlightNodes = selectedResult
    ? [
        selectedResult.user_id,
        ...(selectedResult.connected_users || []),
      ]
    : [];

  if (initialLoading) {
    return (
      <div className="app">
        <Header health={null} />
        <div className="main-content">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <div className="loading-text">Connecting to GraphGuard AI...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <Header health={health} />

      <div className="main-content">
        {/* Search */}
        <SearchBar
          onSearch={handleSearch}
          phones={phones}
          users={users}
          loading={loading}
        />

        {/* Stats */}
        <StatsCards stats={stats} clusters={clusters} />

        {/* Error display */}
        {error && (
          <div style={{
            padding: '14px 20px',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--risk-critical)',
            fontSize: '0.9rem',
            marginBottom: '20px',
          }}>
            ⚠️ {error}
          </div>
        )}

        {/* Multiple results selector */}
        {searchResult && searchResult.results && searchResult.results.length > 1 && (
          <div style={{
            display: 'flex',
            gap: '10px',
            marginBottom: '20px',
            flexWrap: 'wrap',
          }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-dim)', padding: '8px 0' }}>
              {searchResult.total_users} users found:
            </span>
            {searchResult.results.map((r) => (
              <button
                key={r.user_id}
                onClick={() => setSelectedResult(r)}
                style={{
                  padding: '8px 16px',
                  background: selectedResult?.user_id === r.user_id
                    ? 'var(--cyan-glow-strong)' : 'var(--bg-card)',
                  border: `1px solid ${selectedResult?.user_id === r.user_id
                    ? 'var(--cyan)' : 'var(--border)'}`,
                  borderRadius: 'var(--radius-md)',
                  color: selectedResult?.user_id === r.user_id
                    ? 'var(--cyan)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  fontFamily: 'var(--font-mono)',
                  transition: 'all 0.2s ease',
                }}
              >
                {r.user_name} ({r.user_id}) —{' '}
                <span style={{
                  color: r.risk_level === 'CRITICAL' ? 'var(--risk-critical)'
                    : r.risk_level === 'HIGH' ? 'var(--risk-high)'
                    : r.risk_level === 'MEDIUM' ? 'var(--risk-medium)'
                    : 'var(--risk-low)',
                  fontWeight: 600,
                }}>
                  {r.risk_score}
                </span>
              </button>
            ))}
          </div>
        )}

        {/* Main Dashboard Grid */}
        <div className="dashboard-grid">
          {/* Left: Graph Visualization */}
          <div className="panel">
            <div className="panel-header">
              <h2>🕸️ Fraud Network Graph</h2>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                {graphData ? `${graphData.nodes?.length || 0} nodes · ${graphData.edges?.length || 0} edges` : '—'}
              </span>
            </div>
            <div style={{ position: 'relative', width: '100%', height: '100%' }}>
              <GraphView graphData={graphData} highlightNodes={highlightNodes} />
              {loading && (
                <div style={{ 
                  position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', 
                  background: 'rgba(10, 10, 10, 0.7)', 
                  display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                  zIndex: 10, borderRadius: 'inherit'
                }}>
                  <div className="loading-spinner"></div>
                  <div className="loading-text">Analyzing risk...</div>
                </div>
              )}
            </div>
          </div>

          {/* Right: Risk Analysis */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Risk Meter */}
            <div className="panel">
              <div className="panel-header">
                <h2>⚡ Risk Assessment</h2>
              </div>
              {selectedResult ? (
                <RiskMeter result={selectedResult} />
              ) : (
                <div className="risk-meter-container">
                  <div className="empty-state">
                    <div className="empty-icon">🎯</div>
                    <h3>No Target Selected</h3>
                    <p>Search for a phone number or user ID to assess fraud risk</p>
                  </div>
                </div>
              )}
            </div>

            {/* Explanation */}
            <ExplanationPanel
              explanations={selectedResult?.explanation}
            />
          </div>
        </div>

        {/* Fraud Alerts Section */}
        {clusters && clusters.total_alerts > 0 && (
          <div className="alerts-section">
            <h2 style={{ fontSize: '1.1rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              🚨 Detected Fraud Patterns
              <span style={{
                fontSize: '0.75rem',
                padding: '3px 10px',
                background: 'rgba(239, 68, 68, 0.15)',
                borderRadius: '100px',
                color: 'var(--risk-critical)',
              }}>
                {clusters.total_alerts}
              </span>
            </h2>

            {clusters.shared_devices?.map((sd, i) => (
              <div key={`sd-${i}`} className="alert-card">
                <span className="alert-icon">💻</span>
                <div className="alert-content">
                  <h4>Shared Device Detected</h4>
                  <p>Device {sd.device_id} ({sd.device_type}) is shared by {sd.user_count} users</p>
                </div>
              </div>
            ))}

            {clusters.money_loops?.map((ml, i) => (
              <div key={`ml-${i}`} className="alert-card">
                <span className="alert-icon">🔄</span>
                <div className="alert-content">
                  <h4>Money Loop Detected</h4>
                  <p>Circular transfer: {ml.user_a} → {ml.user_b} → {ml.user_c} → {ml.user_a}</p>
                </div>
              </div>
            ))}

            {clusters.phone_reuse?.map((pr, i) => (
              <div key={`pr-${i}`} className="alert-card">
                <span className="alert-icon">📱</span>
                <div className="alert-content">
                  <h4>Phone Number Reuse</h4>
                  <p>Phone {pr.phone_number} ({pr.carrier}) linked to {pr.user_count} accounts</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
