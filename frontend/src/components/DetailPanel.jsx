import React from 'react';

function DetailPanel({ selectedNode, complexity, blastRadius, onBlastRadius }) {
  if (!selectedNode) {
    return <div className="card">Select a node from graph to see details.</div>;
  }

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div style={{ fontSize: '20px', fontWeight: '700' }}>{selectedNode.label}</div>
      <div style={{ color: '#94a3b8' }}>{selectedNode.type} • {selectedNode.file}</div>
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        <span style={{ padding: '4px 8px', borderRadius: '999px', background: '#1f2937' }}>Complexity: {complexity}</span>
        <span style={{ padding: '4px 8px', borderRadius: '999px', background: '#1f2937' }}>{selectedNode.risk || 'low'}</span>
      </div>
      <pre style={{ background: '#020617', padding: '10px', borderRadius: '8px', overflow: 'auto', whiteSpace: 'pre-wrap' }}>{selectedNode.code || 'no code'}</pre>
      <button onClick={onBlastRadius} style={{ padding: '10px', borderRadius: '8px', background: '#dc2626', border: 'none', color: 'white', cursor: 'pointer' }}>
        Calculate Blast Radius
      </button>
      <div style={{ color: '#fca5a5' }}>{blastRadius.length > 0 ? blastRadius.join(' → ') : 'No blast radius yet'}</div>
    </div>
  );
}

export default DetailPanel;
