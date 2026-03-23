export default function ExplanationPanel({ explanations }) {
  if (!explanations || explanations.length === 0) {
    return (
      <div className="panel">
        <div className="panel-header">
          <h2>🔍 AI Analysis</h2>
        </div>
        <div className="panel-body">
          <div className="empty-state">
            <div className="empty-icon">🤖</div>
            <h3>Awaiting Analysis</h3>
            <p>Search for a phone number or user ID to see the AI-powered risk assessment</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>🔍 AI Analysis</h2>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
          {explanations.length} signal{explanations.length !== 1 ? 's' : ''} detected
        </span>
      </div>
      <div className="panel-body">
        <ul className="explanation-list">
          {explanations.map((exp, i) => (
            <li key={i} className="explanation-item">
              {exp}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
