import { useRef, useEffect } from 'react';
import cytoscape from 'cytoscape';

const NODE_COLORS = {
  User: '#00d4ff',
  'User-flagged': '#ef4444',
  Phone: '#a78bfa',
  Device: '#f59e0b',
  BankAccount: '#10b981',
  Transaction: '#f472b6',
};

const NODE_SHAPES = {
  User: 'ellipse',
  Phone: 'diamond',
  Device: 'hexagon',
  BankAccount: 'round-rectangle',
  Transaction: 'star',
};

export default function GraphView({ graphData, highlightNodes }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !graphData) return;

    const elements = [];
    const addedNodes = new Set();

    // Add nodes
    if (graphData.nodes) {
      for (const node of graphData.nodes) {
        if (addedNodes.has(node.id)) continue;
        addedNodes.add(node.id);

        const isFlagged = node.flagged;
        const isHighlighted = highlightNodes?.includes(node.id);
        const colorKey = isFlagged ? 'User-flagged' : node.node_type;

        elements.push({
          data: {
            id: node.id,
            label: node.label || node.id,
            nodeType: node.node_type,
            flagged: isFlagged,
            highlighted: isHighlighted,
          },
          classes: [
            node.node_type.toLowerCase(),
            isFlagged ? 'flagged' : '',
            isHighlighted ? 'highlighted' : '',
          ].filter(Boolean).join(' '),
        });
      }
    }

    // Add edges
    if (graphData.edges) {
      for (let i = 0; i < graphData.edges.length; i++) {
        const edge = graphData.edges[i];
        if (addedNodes.has(edge.source) && addedNodes.has(edge.target)) {
          elements.push({
            data: {
              id: `e-${i}`,
              source: edge.source,
              target: edge.target,
              label: edge.label || edge.edge_type,
              edgeType: edge.edge_type,
            },
          });
        }
      }
    }

    // Destroy previous instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'text-margin-y': 8,
            'font-size': '9px',
            'font-family': 'Inter, sans-serif',
            'color': '#94a3b8',
            'text-outline-color': '#050810',
            'text-outline-width': 2,
            'width': 30,
            'height': 30,
            'border-width': 2,
            'border-opacity': 0.8,
          },
        },
        // User nodes
        {
          selector: 'node.user',
          style: {
            'background-color': NODE_COLORS.User,
            'border-color': NODE_COLORS.User,
            'shape': 'ellipse',
            'width': 35,
            'height': 35,
          },
        },
        // Flagged users - red and larger
        {
          selector: 'node.flagged',
          style: {
            'background-color': NODE_COLORS['User-flagged'],
            'border-color': '#ff6b6b',
            'border-width': 3,
            'width': 42,
            'height': 42,
            'color': '#ef4444',
            'font-weight': 'bold',
          },
        },
        // Highlighted nodes
        {
          selector: 'node.highlighted',
          style: {
            'border-width': 4,
            'border-color': '#00d4ff',
            'width': 45,
            'height': 45,
            'overlay-color': '#00d4ff',
            'overlay-opacity': 0.15,
          },
        },
        // Phone nodes
        {
          selector: 'node.phone',
          style: {
            'background-color': NODE_COLORS.Phone,
            'border-color': NODE_COLORS.Phone,
            'shape': 'diamond',
          },
        },
        // Device nodes
        {
          selector: 'node.device',
          style: {
            'background-color': NODE_COLORS.Device,
            'border-color': NODE_COLORS.Device,
            'shape': 'hexagon',
          },
        },
        // Bank account nodes
        {
          selector: 'node.bankaccount',
          style: {
            'background-color': NODE_COLORS.BankAccount,
            'border-color': NODE_COLORS.BankAccount,
            'shape': 'round-rectangle',
          },
        },
        // Edges
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': 'rgba(148, 163, 184, 0.2)',
            'target-arrow-color': 'rgba(148, 163, 184, 0.3)',
            'target-arrow-shape': 'triangle',
            'arrow-scale': 0.8,
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '7px',
            'color': '#64748b',
            'text-rotation': 'autorotate',
            'text-outline-color': '#050810',
            'text-outline-width': 1.5,
          },
        },
        // SENT_TO edges - highlight money flow
        {
          selector: 'edge[edgeType="SENT_TO"]',
          style: {
            'line-color': 'rgba(239, 68, 68, 0.4)',
            'target-arrow-color': 'rgba(239, 68, 68, 0.5)',
            'width': 2,
            'color': '#ef4444',
          },
        },
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 1000,
        nodeRepulsion: 8000,
        idealEdgeLength: 120,
        edgeElasticity: 100,
        gravity: 0.3,
        padding: 40,
      },
      minZoom: 0.3,
      maxZoom: 3,
      wheelSensitivity: 0.3,
    });

    cyRef.current = cy;

    // Add hover interactions
    cy.on('mouseover', 'node', (evt) => {
      const node = evt.target;
      node.style({
        'overlay-opacity': 0.1,
        'overlay-color': '#00d4ff',
      });
      // Highlight connected edges
      node.connectedEdges().style({
        'width': 3,
        'line-color': 'rgba(0, 212, 255, 0.5)',
        'target-arrow-color': 'rgba(0, 212, 255, 0.6)',
      });
    });

    cy.on('mouseout', 'node', (evt) => {
      const node = evt.target;
      node.style({ 'overlay-opacity': 0 });
      node.connectedEdges().forEach((edge) => {
        const isSentTo = edge.data('edgeType') === 'SENT_TO';
        edge.style({
          'width': isSentTo ? 2 : 1.5,
          'line-color': isSentTo ? 'rgba(239, 68, 68, 0.4)' : 'rgba(148, 163, 184, 0.2)',
          'target-arrow-color': isSentTo ? 'rgba(239, 68, 68, 0.5)' : 'rgba(148, 163, 184, 0.3)',
        });
      });
    });

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [graphData, highlightNodes]);

  if (!graphData) {
    return (
      <div className="graph-container">
        <div className="empty-state">
          <div className="empty-icon">🕸️</div>
          <h3>No Graph Data</h3>
          <p>Load data to visualize the fraud network</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: 'relative' }}>
      <div ref={containerRef} className="graph-container" />
      <div className="graph-legend">
        <div className="legend-item">
          <span className="legend-dot" style={{ background: NODE_COLORS.User }}></span>
          User
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: NODE_COLORS['User-flagged'] }}></span>
          Flagged
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: NODE_COLORS.Phone }}></span>
          Phone
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: NODE_COLORS.Device }}></span>
          Device
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: NODE_COLORS.BankAccount }}></span>
          Account
        </div>
      </div>
    </div>
  );
}
