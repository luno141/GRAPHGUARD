import { useCallback, useEffect, useState } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import StatsCards from './components/StatsCards';
import RiskMeter from './components/RiskMeter';
import GraphView from './components/GraphView';
import ExplanationPanel from './components/ExplanationPanel';
import PatternSummary from './components/PatternSummary';
import './index.css';

const API = 'http://localhost:8000';

async function parseJsonResponse(response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Error ${response.status}`);
  }

  return response.json();
}

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
  const [loadingData, setLoadingData] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);

  const fetchInitialData = useCallback(async () => {
    const responses = await Promise.allSettled([
      fetch(`${API}/health`).then(parseJsonResponse),
      fetch(`${API}/stats`).then(parseJsonResponse),
      fetch(`${API}/graph-data`).then(parseJsonResponse),
      fetch(`${API}/fraud-clusters`).then(parseJsonResponse),
      fetch(`${API}/phones`).then(parseJsonResponse),
      fetch(`${API}/users`).then(parseJsonResponse),
    ]);

    const [healthRes, statsRes, graphRes, clustersRes, phonesRes, usersRes] = responses;

    if (healthRes.status === 'fulfilled') {
      setHealth(healthRes.value);
    }
    if (statsRes.status === 'fulfilled') {
      setStats(statsRes.value);
    }
    if (graphRes.status === 'fulfilled') {
      setGraphData(graphRes.value);
    }
    if (clustersRes.status === 'fulfilled') {
      setClusters(clustersRes.value);
    }
    if (phonesRes.status === 'fulfilled') {
      setPhones(phonesRes.value);
    }
    if (usersRes.status === 'fulfilled') {
      setUsers(usersRes.value);
    }

    const failedCalls = responses.filter((response) => response.status === 'rejected');
    if (failedCalls.length === responses.length) {
      setError('Cannot connect to backend. Make sure FastAPI is running on port 8000 and TigerGraph is available.');
    } else {
      setError(null);
    }

    setInitialLoading(false);
  }, []);

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  const handleSearch = async (query, type) => {
    setLoading(true);
    setError(null);
    setNotice(null);
    setSearchResult(null);
    setSelectedResult(null);

    try {
      const endpoint = type === 'phone' ? '/check-number' : '/check-user';
      const payload = type === 'phone'
        ? { phone_number: query }
        : { user_id: query };

      const data = await fetch(`${API}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }).then(parseJsonResponse);

      if (type === 'phone') {
        setSearchResult(data);
        if (data.results && data.results.length > 0) {
          setSelectedResult(data.results[0]);
        }
      } else {
        setSearchResult({ results: [data], total_users: 1 });
        setSelectedResult(data);
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSampleData = async () => {
    setLoadingData(true);
    setError(null);
    setNotice(null);

    try {
      await fetch(`${API}/load-data`, {
        method: 'POST',
      }).then(parseJsonResponse);

      await fetchInitialData();
      setNotice('Sample data loaded successfully. The dashboard has been refreshed with the full fraud-ring demo scenario.');
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoadingData(false);
    }
  };

  const highlightNodes = selectedResult
    ? [...new Set([
        selectedResult.user_id,
        ...(selectedResult.connected_users || []),
        ...(selectedResult.connected_phones || []),
        ...(selectedResult.connected_devices || []),
        ...(selectedResult.connected_accounts || []),
      ])]
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
        <section className="hero-banner">
          <div>
            <p className="section-kicker">TigerGraph-Native Fraud Intelligence</p>
            <h2>See multi-hop fraud rings, shared devices, and phone reuse in one live demo.</h2>
            <p className="section-copy">
              Powered by TigerGraph: graph insights are computed in-database via GSQL queries, not stitched together afterward in Python.
            </p>
            <div className="hero-chips">
              <span className="hero-chip">3-hop link analysis</span>
              <span className="hero-chip">Pattern queries in GSQL</span>
              <span className="hero-chip">Explainable risk scoring</span>
            </div>
          </div>
          <div className="hero-proof">
            <span className="hero-proof-label">Judge-ready value</span>
            <ul>
              <li>Search a suspicious phone and instantly reveal linked users, devices, and accounts.</li>
              <li>Show exactly why a user is risky with grouped graph-derived signals.</li>
              <li>Pivot into the network view and point at the cluster TigerGraph found.</li>
            </ul>
          </div>
        </section>

        <SearchBar
          onSearch={handleSearch}
          phones={phones}
          users={users}
          loading={loading}
          onLoadSampleData={handleLoadSampleData}
          loadingData={loadingData}
        />

        {notice && <div className="inline-banner success">{notice}</div>}
        {error && <div className="inline-banner error">{error}</div>}

        <StatsCards stats={stats} clusters={clusters} />
        {clusters && <PatternSummary clusters={clusters} />}

        {searchResult && searchResult.results && searchResult.results.length > 1 && (
          <div
            style={{
              display: 'flex',
              gap: '10px',
              marginBottom: '20px',
              flexWrap: 'wrap',
            }}
          >
            <span style={{ fontSize: '0.85rem', color: 'var(--text-dim)', padding: '8px 0' }}>
              {searchResult.total_users} users found:
            </span>
            {searchResult.results.map((result) => (
              <button
                key={result.user_id}
                onClick={() => setSelectedResult(result)}
                style={{
                  padding: '8px 16px',
                  background: selectedResult?.user_id === result.user_id
                    ? 'var(--cyan-glow-strong)'
                    : 'var(--bg-card)',
                  border: `1px solid ${selectedResult?.user_id === result.user_id
                    ? 'var(--cyan)'
                    : 'var(--border)'}`,
                  borderRadius: 'var(--radius-md)',
                  color: selectedResult?.user_id === result.user_id
                    ? 'var(--cyan)'
                    : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  fontFamily: 'var(--font-mono)',
                  transition: 'all 0.2s ease',
                }}
              >
                {result.user_name} ({result.user_id}){' '}
                <span
                  style={{
                    color: result.risk_level === 'CRITICAL'
                      ? 'var(--risk-critical)'
                      : result.risk_level === 'HIGH'
                        ? 'var(--risk-high)'
                        : result.risk_level === 'MEDIUM'
                          ? 'var(--risk-medium)'
                          : 'var(--risk-low)',
                    fontWeight: 600,
                  }}
                >
                  {result.risk_score}
                </span>
              </button>
            ))}
          </div>
        )}

        <div className="dashboard-grid">
          <div className="panel">
            <div className="panel-header">
              <h2>Fraud Network Graph</h2>
              <span className="panel-meta">
                {graphData ? `${graphData.nodes?.length || 0} nodes · ${graphData.edges?.length || 0} edges` : '-'}
              </span>
            </div>
            {selectedResult && (
              <div className="graph-focus-strip">
                Focused neighborhood: {highlightNodes.length} related entities highlighted for {selectedResult.user_id}.
              </div>
            )}
            <div style={{ position: 'relative', width: '100%', height: '100%' }}>
              <GraphView graphData={graphData} highlightNodes={highlightNodes} />
              {loading && (
                <div
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    background: 'rgba(10, 10, 10, 0.7)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 10,
                    borderRadius: 'inherit',
                  }}
                >
                  <div className="loading-spinner"></div>
                  <div className="loading-text">Analyzing risk...</div>
                </div>
              )}
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="panel">
              <div className="panel-header">
                <h2>Risk Assessment</h2>
                <span className="panel-meta">Graph-driven score</span>
              </div>
              {selectedResult ? (
                <RiskMeter
                  key={`${selectedResult.user_id}-${selectedResult.risk_score}`}
                  result={selectedResult}
                />
              ) : (
                <div className="risk-meter-container">
                  <div className="empty-state">
                    <div className="empty-icon">[]</div>
                    <h3>No Target Selected</h3>
                    <p>Search for a phone number or user ID to assess fraud risk.</p>
                  </div>
                </div>
              )}
            </div>

            <ExplanationPanel explanations={selectedResult?.explanation} />
          </div>
        </div>

        {clusters && clusters.total_alerts > 0 && (
          <div className="alerts-section">
            <h2
              style={{
                fontSize: '1.1rem',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              Detected Fraud Patterns
              <span
                style={{
                  fontSize: '0.75rem',
                  padding: '3px 10px',
                  background: 'rgba(239, 68, 68, 0.15)',
                  borderRadius: '100px',
                  color: 'var(--risk-critical)',
                }}
              >
                {clusters.total_alerts}
              </span>
            </h2>

            {clusters.shared_devices?.map((sharedDevice, index) => (
              <div key={`sd-${index}`} className="alert-card">
                <span className="alert-icon">[D]</span>
                <div className="alert-content">
                  <h4>Shared Device Detected</h4>
                  <p>
                    Device {sharedDevice.device_id} ({sharedDevice.device_type}) is shared by {sharedDevice.user_count} users.
                  </p>
                </div>
              </div>
            ))}

            {clusters.money_loops?.map((moneyLoop, index) => (
              <div key={`ml-${index}`} className="alert-card">
                <span className="alert-icon">[L]</span>
                <div className="alert-content">
                  <h4>Money Loop Detected</h4>
                  <p>
                    Circular transfer: {moneyLoop.user_a} to {moneyLoop.user_b} to {moneyLoop.user_c} to {moneyLoop.user_a}.
                  </p>
                </div>
              </div>
            ))}

            {clusters.phone_reuse?.map((phoneReuse, index) => (
              <div key={`pr-${index}`} className="alert-card">
                <span className="alert-icon">[P]</span>
                <div className="alert-content">
                  <h4>Phone Number Reuse</h4>
                  <p>
                    Phone {phoneReuse.phone_number} ({phoneReuse.carrier}) is linked to {phoneReuse.user_count} accounts.
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
