const QUERY_CARDS = [
  {
    key: 'money_loops',
    icon: '->',
    title: 'Circular Money Loops',
    query: 'detect_money_loops()',
    description: 'Flags 3-hop transfer rings that look like laundering behavior.',
  },
  {
    key: 'shared_devices',
    icon: '[]',
    title: 'Shared Device Hubs',
    query: 'detect_shared_devices()',
    description: 'Surfaces device fingerprints reused across multiple identities.',
  },
  {
    key: 'phone_reuse',
    icon: '##',
    title: 'Phone Reuse',
    query: 'detect_phone_reuse()',
    description: 'Finds numbers linked to multiple accounts inside the graph.',
  },
];

export default function PatternSummary({ clusters }) {
  const items = QUERY_CARDS.map((card) => ({
    ...card,
    count: clusters?.[card.key]?.length || 0,
  }));

  return (
    <section className="pattern-summary">
      <div className="section-heading">
        <div>
          <p className="section-kicker">TigerGraph Pattern Queries</p>
          <h2>In-database GSQL signals driving the demo</h2>
        </div>
        <p className="section-copy">
          These counts come directly from TigerGraph pattern-matching queries, not Python post-processing.
        </p>
      </div>

      <div className="pattern-grid">
        {items.map((item) => (
          <div key={item.key} className="pattern-card">
            <div className="pattern-icon">{item.icon}</div>
            <div className="pattern-count">{item.count}</div>
            <h3>{item.title}</h3>
            <code>{item.query}</code>
            <p>{item.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
