import { useState } from 'react';

export default function SearchBar({ onSearch, phones, users, loading }) {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('phone');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim(), searchType);
    }
  };

  const handleQuickTag = (value, type) => {
    setQuery(value);
    setSearchType(type);
    onSearch(value, type);
  };

  // Get sample fraud and legit items for quick tags
  const fraudPhones = phones?.filter(p => 
    ['+1-555-0101', '+1-555-0102', '+1-555-0103'].includes(p.number)
  ) || [];
  const legitPhones = phones?.filter(p => 
    ['+1-555-1001', '+1-555-1002'].includes(p.number)
  ) || [];
  const fraudUsers = users?.filter(u => u.is_flagged) || [];
  const legitUsers = users?.filter(u => !u.is_flagged).slice(0, 2) || [];

  return (
    <div className="search-section">
      <form onSubmit={handleSubmit} className="search-container">
        <div className="search-type-toggle">
          <button
            type="button"
            className={`search-type-btn ${searchType === 'phone' ? 'active' : ''}`}
            onClick={() => setSearchType('phone')}
          >
            📱 Phone
          </button>
          <button
            type="button"
            className={`search-type-btn ${searchType === 'user' ? 'active' : ''}`}
            onClick={() => setSearchType('user')}
          >
            👤 User ID
          </button>
        </div>
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="search-input"
            placeholder={searchType === 'phone' 
              ? 'Enter phone number (e.g. +1-555-0101)...' 
              : 'Enter user ID (e.g. F001)...'}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <button type="submit" className="search-btn" disabled={loading || !query.trim()}>
          {loading ? '⏳ Analyzing...' : '⚡ Analyze Risk'}
        </button>
      </form>

      <div className="quick-tags">
        <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', padding: '6px 0' }}>Quick test:</span>
        {fraudPhones.map(p => (
          <button key={p.number} className="quick-tag flagged" onClick={() => handleQuickTag(p.number, 'phone')}>
            🔴 {p.number}
          </button>
        ))}
        {legitPhones.map(p => (
          <button key={p.number} className="quick-tag" onClick={() => handleQuickTag(p.number, 'phone')}>
            🟢 {p.number}
          </button>
        ))}
        {fraudUsers.slice(0, 3).map(u => (
          <button key={u.uid} className="quick-tag flagged" onClick={() => handleQuickTag(u.uid, 'user')}>
            🔴 {u.uid}
          </button>
        ))}
        {legitUsers.map(u => (
          <button key={u.uid} className="quick-tag" onClick={() => handleQuickTag(u.uid, 'user')}>
            🟢 {u.uid}
          </button>
        ))}
      </div>
    </div>
  );
}
