import React from 'react';

function GraphView({ nodes, edges, onSelectNode, highlightIds }) {
  return (
    <div className="card" style={{ minHeight: '360px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div style={{ fontWeight: '600' }}>Graph view</div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        {nodes.map((node) => {
          const isHigh = highlightIds.includes(node.id);
          let color = '#3b82f6';
          if (node.type === 'Function') color = '#f59e0b';
          if (node.type === 'Class') color = '#10b981';
          if (isHigh) color = '#ef4444';

          return (
            <div
              key={node.id}
              onClick={() => onSelectNode(node)}
              style={{
                padding: '8px 10px',
                borderRadius: '999px',
                background: color,
                color: 'white',
                cursor: 'pointer',
                border: isHigh ? '2px solid white' : '1px solid transparent',
              }}
            >
              {node.label}
            </div>
          );
        })}
      </div>
      <div style={{ color: '#94a3b8', fontSize: '13px' }}>Edges: {edges.length}</div>
    </div>
  );
}

export default GraphView;
