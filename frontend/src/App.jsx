import React, { useEffect, useState } from 'react';
import SearchBar from './components/SearchBar';
import GraphView from './components/GraphView';
import DetailPanel from './components/DetailPanel';

function App() {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [blastRadius, setBlastRadius] = useState([]);
  const [activeTab, setActiveTab] = useState('graph');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_path: 'test_repo' }),
    })
      .then((res) => res.json())
      .then(() => fetch('http://127.0.0.1:8000/api/graph'))
      .then((res) => res.json())
      .then((data) => setGraphData(data))
      .catch(() => {});
  }, []);

  const handleSearch = async () => {
    const res = await fetch('http://127.0.0.1:8000/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();
    setSearchResults(data);
    if (data.length > 0) {
      const matchNode = graphData.nodes.find((node) => node.id === data[0].node_id);
      if (matchNode) {
        setSelectedNode(matchNode);
      }
    }
  };

  const handleBlastRadius = async () => {
    if (!selectedNode) return;
    const res = await fetch(`http://127.0.0.1:8000/api/blast-radius?node_id=${selectedNode.id}`);
    const data = await res.json();
    setBlastRadius(data);
  };

  return (
    <div style={{ minHeight: '100vh', background: '#020617', padding: '24px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '28px', fontWeight: '700' }}>CodeKG Dashboard</div>
            <div style={{ color: '#94a3b8' }}>A simple student-made code knowledge graph view</div>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button onClick={() => setActiveTab('graph')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #334155', background: activeTab === 'graph' ? '#1d4ed8' : '#111827', color: 'white' }}>Graph</button>
            <button onClick={() => setActiveTab('search')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #334155', background: activeTab === 'search' ? '#1d4ed8' : '#111827', color: 'white' }}>Search</button>
          </div>
        </div>

        <SearchBar query={query} setQuery={setQuery} onSearch={handleSearch} />

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px' }}>
          <GraphView nodes={graphData.nodes} edges={graphData.edges} onSelectNode={setSelectedNode} highlightIds={blastRadius} />
          <DetailPanel selectedNode={selectedNode} complexity={selectedNode?.complexity || 1} blastRadius={blastRadius} onBlastRadius={handleBlastRadius} />
        </div>

        {searchResults.length > 0 && (
          <div className="card">
            <div style={{ fontWeight: '600', marginBottom: '8px' }}>Search results</div>
            {searchResults.map((item) => (
              <div key={item.node_id} style={{ padding: '6px 0', color: '#cbd5e1' }}>{item.node_id} • score {item.score.toFixed(2)}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
