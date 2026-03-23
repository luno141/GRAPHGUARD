import { useEffect, useState } from 'react';

const RISK_COLORS = {
  LOW: '#10b981',
  MEDIUM: '#f59e0b',
  HIGH: '#f97316',
  CRITICAL: '#ef4444',
};

const BAND_LEGEND = [
  { label: '0-30 Safe', className: 'safe' },
  { label: '31-70 Suspicious', className: 'watch' },
  { label: '71-100 Critical', className: 'critical' },
];

function formatCurrency(amount) {
  return `$${Number(amount || 0).toLocaleString()}`;
}

export default function RiskMeter({ result }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  const score = result?.risk_score || 0;
  const level = result?.risk_level || 'LOW';
  const color = RISK_COLORS[level] || RISK_COLORS.LOW;
  const flaggedLinks = result?.signals?.connected_flagged_users?.length || 0;

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 100);
    return () => clearTimeout(timer);
  }, [score]);

  const radius = 80;
  const strokeWidth = 12;
  const cx = 100;
  const cy = 100;
  const arcLength = Math.PI * radius;
  const filledLength = (animatedScore / 100) * arcLength;

  const describeArc = (startAngle, endAngle) => {
    const startX = cx + radius * Math.cos(startAngle);
    const startY = cy - radius * Math.sin(startAngle);
    const endX = cx + radius * Math.cos(endAngle);
    const endY = cy - radius * Math.sin(endAngle);
    const largeArc = endAngle - startAngle > Math.PI ? 1 : 0;

    return `M ${startX} ${startY} A ${radius} ${radius} 0 ${largeArc} 0 ${endX} ${endY}`;
  };

  const bgPath = describeArc(Math.PI, 0);

  return (
    <div className={`risk-meter-container risk-level-${level}`}>
      <div className="risk-gauge">
        <svg viewBox="0 0 200 115" width="200" height="115">
          <path
            d={bgPath}
            fill="none"
            stroke="rgba(148, 163, 184, 0.1)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          <path
            d={bgPath}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={arcLength}
            strokeDashoffset={arcLength - filledLength}
            style={{
              transition: 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.5s ease',
              filter: `drop-shadow(0 0 8px ${color}50)`,
            }}
          />
          {[0, 25, 50, 75, 100].map((tick) => {
            const angle = Math.PI - (tick / 100) * Math.PI;
            const innerRadius = radius - 20;
            const outerRadius = radius - 14;
            const x1 = cx + innerRadius * Math.cos(angle);
            const y1 = cy - innerRadius * Math.sin(angle);
            const x2 = cx + outerRadius * Math.cos(angle);
            const y2 = cy - outerRadius * Math.sin(angle);

            return (
              <line
                key={tick}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke="rgba(148, 163, 184, 0.3)"
                strokeWidth="1.5"
              />
            );
          })}
        </svg>
      </div>

      <div className="risk-score-display">
        <div className="risk-score-number">{animatedScore}</div>
        <div className="risk-score-label">{level} Risk</div>
        <p className="risk-meter-caption">Live graph signals from TigerGraph GSQL queries</p>
      </div>

      <div className="risk-band-legend">
        {BAND_LEGEND.map((band) => (
          <span key={band.label} className={`risk-band ${band.className}`}>
            {band.label}
          </span>
        ))}
      </div>

      {result && (
        <>
          <div className="risk-user-name">{result.user_name}</div>
          <div className="risk-user-id">{result.user_id}</div>

          <div className="signal-grid">
            <div className="signal-badge">
              <span className="signal-value">{result.signals?.shared_device_count || 0}</span>
              <span className="signal-label">Shared Devices</span>
            </div>
            <div className="signal-badge">
              <span className="signal-value">{result.signals?.shared_phone_count || 0}</span>
              <span className="signal-label">Shared Phones</span>
            </div>
            <div className="signal-badge">
              <span className="signal-value">{flaggedLinks}</span>
              <span className="signal-label">Flagged Neighbors</span>
            </div>
            <div className="signal-badge">
              <span className="signal-value">
                {result.signals?.is_in_money_loop ? 'Yes' : 'No'}
              </span>
              <span className="signal-label">Money Loop</span>
            </div>
            <div className="signal-badge">
              <span className="signal-value">{result.signals?.sent_to_count || 0}</span>
              <span className="signal-label">Outgoing Transfers</span>
            </div>
            <div className="signal-badge">
              <span className="signal-value">{formatCurrency(result.signals?.total_sent)}</span>
              <span className="signal-label">Total Sent</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
