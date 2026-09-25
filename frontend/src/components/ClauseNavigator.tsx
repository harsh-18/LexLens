import React, { useState } from 'react';
import { Search, ChevronRight, Layers, Tag } from 'lucide-react';
import { Clause } from '../types';

interface ClauseNavigatorProps {
  clauses: Clause[];
  selectedClauseId: string | null;
  onSelectClause: (clause: Clause) => void;
}

export const ClauseNavigator: React.FC<ClauseNavigatorProps> = ({
  clauses,
  selectedClauseId,
  onSelectClause
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  // Extract unique categories
  const categories = ['ALL', ...Array.from(new Set(clauses.map((c) => c.category))).filter(Boolean)];

  const filteredClauses = clauses.filter((c) => {
    const matchesSearch =
      (c.clause_number?.toLowerCase().includes(searchTerm.toLowerCase()) || false) ||
      (c.title?.toLowerCase().includes(searchTerm.toLowerCase()) || false) ||
      c.text.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesCategory = selectedCategory === 'ALL' || c.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <aside className="glass-panel" style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={16} color="var(--accent-primary)" />
            <h4 style={{ fontSize: '0.92rem', fontWeight: 700 }}>Clauses & Structure</h4>
          </div>
          <span className="badge badge-muted" style={{ fontSize: '0.7rem' }}>
            {filteredClauses.length} / {clauses.length}
          </span>
        </div>

        {/* Search */}
        <div style={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          marginBottom: '8px'
        }}>
          <Search size={14} color="var(--text-muted)" style={{ position: 'absolute', left: '10px' }} />
          <input
            type="text"
            placeholder="Search clause or text..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              background: 'var(--bg-input)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '6px 10px 6px 30px',
              fontSize: '0.78rem',
              color: 'var(--text-primary)',
              outline: 'none'
            }}
          />
        </div>

        {/* Category Pills */}
        <div style={{
          display: 'flex',
          gap: '6px',
          overflowX: 'auto',
          paddingBottom: '4px',
          whiteSpace: 'nowrap'
        }}>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              style={{
                background: selectedCategory === cat ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.04)',
                color: selectedCategory === cat ? '#a5b4fc' : 'var(--text-secondary)',
                border: `1px solid ${selectedCategory === cat ? 'rgba(99, 102, 241, 0.5)' : 'var(--border-subtle)'}`,
                borderRadius: 'var(--radius-full)',
                padding: '2px 8px',
                fontSize: '0.68rem',
                cursor: 'pointer',
                fontWeight: selectedCategory === cat ? 600 : 400
              }}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Clause List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
        {filteredClauses.length === 0 ? (
          <div style={{ padding: '24px 12px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            No matching clauses found.
          </div>
        ) : (
          filteredClauses.map((clause, idx) => {
            const isSelected = selectedClauseId === clause.id;
            return (
              <div
                key={clause.id || idx}
                onClick={() => onSelectClause(clause)}
                style={{
                  padding: '10px 12px',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: '6px',
                  cursor: 'pointer',
                  background: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                  border: `1px solid ${isSelected ? 'rgba(99, 102, 241, 0.4)' : 'transparent'}`,
                  transition: 'var(--transition)'
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) e.currentTarget.style.background = 'transparent';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{
                    fontSize: '0.82rem',
                    fontWeight: 700,
                    color: isSelected ? '#a5b4fc' : 'var(--text-primary)'
                  }}>
                    {clause.clause_number ? `§ ${clause.clause_number}` : `Clause ${idx + 1}`}
                  </span>
                  <span className="badge badge-muted" style={{ fontSize: '0.62rem' }}>
                    P. {clause.page_start}
                  </span>
                </div>

                <div style={{
                  fontSize: '0.78rem',
                  color: 'var(--text-secondary)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  marginBottom: '6px'
                }}>
                  {clause.title || clause.text.slice(0, 45)}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{
                    fontSize: '0.68rem',
                    color: 'var(--text-muted)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    <Tag size={10} />
                    {clause.category}
                  </span>
                  <ChevronRight size={14} color="var(--text-muted)" />
                </div>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
};
