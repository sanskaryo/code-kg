import React from 'react';

function SearchBar({ query, setQuery, onSearch }) {
  return (
    <div style={{ display: 'flex', gap: '8px' }}>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="search code semantically"
        style={{ flex: 1, padding: '10px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: 'white' }}
      />
      <button onClick={onSearch} style={{ padding: '10px 14px', borderRadius: '8px', background: '#f59e0b', border: 'none', color: 'black', cursor: 'pointer' }}>
        Search
      </button>
    </div>
  );
}

export default SearchBar;
