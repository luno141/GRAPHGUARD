const GROUP_TITLES = {
  identity: 'Identity Reuse Signals',
  transactions: 'Transaction Pattern Signals',
  network: 'Risky Network Exposure',
  review: 'Analyst Review Notes',
  clean: 'Clearance Signal',
};

function normalizeExplanation(explanation) {
  return explanation.replace(/^[^\w]+/, '').trim();
}

function classifyExplanation(explanation) {
  const text = normalizeExplanation(explanation);
  const lower = text.toLowerCase();

  if (lower.includes('no suspicious')) {
    return {
      group: 'clean',
      severity: 'LOW',
      title: 'No suspicious behavior detected',
      detail: text,
    };
  }

  if (lower.includes('shares device')) {
    return {
      group: 'identity',
      severity: 'HIGH',
      title: 'Shared device footprint',
      detail: text,
    };
  }

  if (lower.includes('phone number shared')) {
    return {
      group: 'identity',
      severity: 'HIGH',
      title: 'Phone reused across accounts',
      detail: text,
    };
  }

  if (lower.includes('circular money transfer')) {
    return {
      group: 'transactions',
      severity: 'HIGH',
      title: 'Circular transfer loop',
      detail: text,
    };
  }

  if (lower.includes('send/receive ratio')) {
    return {
      group: 'transactions',
      severity: 'MEDIUM',
      title: 'Suspicious fund flow ratio',
      detail: text,
    };
  }

  if (lower.includes('sent money to')) {
    return {
      group: 'transactions',
      severity: 'MEDIUM',
      title: 'High outgoing transfer fan-out',
      detail: text,
    };
  }

  if (lower.includes('connected to') && lower.includes('flagged')) {
    return {
      group: 'network',
      severity: 'HIGH',
      title: 'Connected to flagged users',
      detail: text,
    };
  }

  if (lower.includes('already flagged')) {
    return {
      group: 'review',
      severity: 'HIGH',
      title: 'Previously flagged entity',
      detail: text,
    };
  }

  return {
    group: 'review',
    severity: 'MEDIUM',
    title: 'Additional risk context',
    detail: text,
  };
}

function groupExplanations(explanations) {
  return explanations.reduce((groups, explanation) => {
    const classified = classifyExplanation(explanation);
    const existingGroup = groups.find((group) => group.key === classified.group);

    if (existingGroup) {
      existingGroup.items.push(classified);
      return groups;
    }

    groups.push({
      key: classified.group,
      title: GROUP_TITLES[classified.group],
      items: [classified],
    });
    return groups;
  }, []);
}

export default function ExplanationPanel({ explanations }) {
  if (!explanations || explanations.length === 0) {
    return (
      <div className="panel">
        <div className="panel-header">
          <h2>AI Analysis</h2>
        </div>
        <div className="panel-body">
          <div className="empty-state">
            <div className="empty-icon">[ ]</div>
            <h3>Awaiting Analysis</h3>
            <p>Search for a phone number or user ID to see the explainable TigerGraph risk assessment.</p>
          </div>
        </div>
      </div>
    );
  }

  const groupedExplanations = groupExplanations(explanations);

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Explainable Risk Breakdown</h2>
        <span className="panel-meta">
          {explanations.length} signal{explanations.length !== 1 ? 's' : ''} detected
        </span>
      </div>
      <div className="panel-body explanation-groups">
        {groupedExplanations.map((group) => (
          <section key={group.key} className="explanation-group">
            <div className="explanation-group-header">
              <h3>{group.title}</h3>
              <span className="group-count">{group.items.length}</span>
            </div>
            <ul className="explanation-list">
              {group.items.map((item, index) => (
                <li key={`${item.title}-${index}`} className="explanation-item">
                  <div className="explanation-topline">
                    <span className={`severity-pill ${item.severity.toLowerCase()}`}>
                      {item.severity}
                    </span>
                    <strong>{item.title}</strong>
                  </div>
                  <p>{item.detail}</p>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
