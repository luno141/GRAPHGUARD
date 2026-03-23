export default function StatsCards({ stats, clusters }) {
  const alertCount = clusters?.total_alerts || 0;

  const cards = [
    { key: 'users', icon: '👤', value: stats?.users || 0, label: 'Users', className: 'users' },
    { key: 'phones', icon: '📱', value: stats?.phones || 0, label: 'Phones', className: 'phones' },
    { key: 'devices', icon: '💻', value: stats?.devices || 0, label: 'Devices', className: 'devices' },
    { key: 'accounts', icon: '🏦', value: stats?.accounts || 0, label: 'Accounts', className: 'accounts' },
    { key: 'alerts', icon: '🚨', value: alertCount, label: 'Alerts', className: 'alerts' },
  ];

  return (
    <div className="stats-grid">
      {cards.map((card) => (
        <div key={card.key} className={`stat-card ${card.className}`}>
          <div className="stat-icon">{card.icon}</div>
          <div className="stat-value">{card.value}</div>
          <div className="stat-label">{card.label}</div>
        </div>
      ))}
    </div>
  );
}
