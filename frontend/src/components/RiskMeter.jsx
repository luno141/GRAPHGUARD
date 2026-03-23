import { useEffect, useState } from 'react';

const RISK_COLORS = {
  LOW: '#10b981',
  MEDIUM: '#f59e0b',
  HIGH: '#f97316',
  CRITICAL: '#ef4444',
};

export default function RiskMeter({ result }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  const score = result?.risk_score || 0;
  const level = result?.risk_level || 'LOW';
  const color = RISK_COLORS[level] || RISK_COLORS.LOW;

  useEffect(() => {
    setAnimatedScore(0);
    const timer = setTimeout(() => setAnimatedScore(score), 100);
    return () => clearTimeout(timer);
  }, [score]);

  // SVG arc calculation
  const radius = 80;
  const strokeWidth = 12;
  const cx = 100;
  const cy = 100;
  const startAngle = Math.PI;
  const endAngle = 0;
  const totalAngle = Math.PI;

  const arcLength = totalAngle * radius;
  const filledLength = (animatedScore / 100) * arcLength;

  const describeArc = (startA, endA) => {
    const startX = cx + radius * Math.cos(startA);
    const startY = cy - radius * Math.sin(startA);
    const endX = cx + radius * Math.cos(endA);
    const endY = cy - radius * Math.sin(endA);
    const largeArc = endA - startA > Math.PI ? 1 : 0;
    return `M ${startX} ${startY} A ${radius} ${radius} 0 ${largeArc} 0 ${endX} ${endY}`;
  };

  const bgPath = describeArc(Math.PI, 0);

  return (
    <div className={`risk-meter-container risk-level-${level}`}>
      <div className="risk-gauge">
        <svg viewBox="0 0 200 115" width="200" height="115">
          {/* Background arc */}
          <path
            d={bgPath}
            fill="none"
            stroke="rgba(148, 163, 184, 0.1)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          {/* Filled arc */}
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
          {/* Tick marks */}
          {[0, 25, 50, 75, 100].map((tick) => {
            const angle = Math.PI - (tick / 100) * Math.PI;
            const innerR = radius - 20;
            const outerR = radius - 14;
            const x1 = cx + innerR * Math.cos(angle);
            const y1 = cy - innerR * Math.sin(angle);
            const x2 = cx + outerR * Math.cos(angle);
            const y2 = cy - outerR * Math.sin(angle);
            return (
              <line key={tick} x1={x1} y1={y1} x2={x2} y2={y2}
                stroke="rgba(148, 163, 184, 0.3)" strokeWidth="1.5" />
            );
          })}
        </svg>
      </div>

      <div className="risk-score-display">
        <div className="risk-score-number">{animatedScore}</div>
        <div className="risk-score-label">{level} RISK</div>
      </div>

      {result && (
        <>
          <div className="risk-user-name">{result.user_name}</div>
          <div className="risk-user-id">{result.user_id}</div>

          <div className="signal-grid" style={{ width: '100%', marginTop: '20px' }}>
            <div className="signal-badge">
              <span className="signal-value">{result.signals?.shared_device_count || 0}</span>
              <span className="signal-label">Shared Devices</span>
            </div>
            <div className="signal-badge">
              <span className="signal-value">{result.signals?.shared_phone_count || 0}</span>
              <span className="signal-label">Shared Phones</span>
            </div>
            <div className="signal-badge">
              <span className="signal-value">{result.signals?.sent_to_count || 0}</span>
              <span className="signal-label">Outgoing Txns</span>
            </div>
            <div className="signal-badge">
              <span className="signal-value">${(result.signals?.total_sent || 0).toLocaleString()}</span>
              <span className="signal-label">Total Sent</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
