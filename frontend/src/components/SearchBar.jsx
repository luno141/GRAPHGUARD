import { useState } from 'react';

export default function SearchBar({
  onSearch,
  phones,
  users,
  loading,
  onLoadSampleData,
  loadingData,
}) {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('phone');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (query.trim()) {
      onSearch(query.trim(), searchType);
    }
  };

  const handleQuickTag = (value, type) => {
    setQuery(value);
    setSearchType(type);
    onSearch(value, type);
  };

  const fraudPhones = phones?.filter((phone) =>
    ['+1-555-0101', '+1-555-0102', '+1-555-0103'].includes(phone.number),
  ) || [];
  const legitPhones = phones?.filter((phone) =>
    ['+1-555-1001', '+1-555-1002'].includes(phone.number),
  ) || [];
  const fraudUsers = users?.filter((user) => user.is_flagged) || [];
  const legitUsers = users?.filter((user) => !user.is_flagged).slice(0, 2) || [];
  const listId = searchType === 'phone' ? 'phone-suggestions' : 'user-suggestions';

  return (
    <section className="search-section">
      <div className="search-intro">
        <div>
          <p className="section-kicker">Finale Demo Flow</p>
          <h2>Load sample data, inspect a suspicious phone, then show the graph story.</h2>
        </div>
        <p className="section-copy">
          Search suggestions are pulled from TigerGraph so judges can move from data load to explainable graph evidence in one pass.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="search-container">
        <div className="search-type-toggle">
          <button
            type="button"
            className={`search-type-btn ${searchType === 'phone' ? 'active' : ''}`}
            onClick={() => setSearchType('phone')}
          >
            Phone
          </button>
          <button
            type="button"
            className={`search-type-btn ${searchType === 'user' ? 'active' : ''}`}
            onClick={() => setSearchType('user')}
          >
            User ID
          </button>
        </div>

        <div className="search-input-wrapper">
          <span className="search-icon">/</span>
          <input
            type="text"
            className="search-input"
            list={listId}
            placeholder={searchType === 'phone'
              ? 'Enter phone number (for example +1-555-0101)'
              : 'Enter user ID (for example F001)'}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <datalist id="phone-suggestions">
            {phones.map((phone) => (
              <option key={phone.number} value={phone.number}>
                {phone.carrier}
              </option>
            ))}
          </datalist>
          <datalist id="user-suggestions">
            {users.map((user) => (
              <option key={user.uid} value={user.uid}>
                {user.name}
              </option>
            ))}
          </datalist>
        </div>

        <button type="submit" className="search-btn" disabled={loading || !query.trim()}>
          {loading ? 'Analyzing...' : 'Analyze Risk'}
        </button>

        <button
          type="button"
          className="secondary-btn"
          onClick={onLoadSampleData}
          disabled={loading || loadingData}
        >
          {loadingData ? 'Loading Demo Data...' : 'Load Sample Data'}
        </button>
      </form>

      <div className="search-helper">
        Demo script: click <strong>Load Sample Data</strong>, search <code>+1-555-0101</code>, open the risk explanation, then point to the highlighted fraud ring in the graph.
      </div>

      <div className="quick-tags">
        <span className="quick-tags-label">Quick test:</span>
        {fraudPhones.map((phone) => (
          <button
            key={phone.number}
            className="quick-tag flagged"
            onClick={() => handleQuickTag(phone.number, 'phone')}
          >
            High Risk {phone.number}
          </button>
        ))}
        {legitPhones.map((phone) => (
          <button
            key={phone.number}
            className="quick-tag"
            onClick={() => handleQuickTag(phone.number, 'phone')}
          >
            Safe {phone.number}
          </button>
        ))}
        {fraudUsers.slice(0, 3).map((user) => (
          <button
            key={user.uid}
            className="quick-tag flagged"
            onClick={() => handleQuickTag(user.uid, 'user')}
          >
            Flagged {user.uid}
          </button>
        ))}
        {legitUsers.map((user) => (
          <button
            key={user.uid}
            className="quick-tag"
            onClick={() => handleQuickTag(user.uid, 'user')}
          >
            Legit {user.uid}
          </button>
        ))}
      </div>
    </section>
  );
}
