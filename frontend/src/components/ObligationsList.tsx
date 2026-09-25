import React, { useState } from 'react';
import { CheckSquare, AlertCircle, Clock, ArrowRight, UserCheck, Shield } from 'lucide-react';
import { Obligation, RightItem } from '../types';

interface ObligationsListProps {
  obligations: Obligation[];
  rights: RightItem[];
  onFocusClause: (clauseNumber: string, pageNumber: number, textSnippet: string) => void;
}

export const ObligationsList: React.FC<ObligationsListProps> = ({
  obligations,
  rights,
  onFocusClause
}) => {
  const [viewMode, setViewMode] = useState<'obligations' | 'rights'>('obligations');
  const [actorFilter, setActorFilter] = useState<string>('ALL');

  const actors = ['ALL', ...Array.from(new Set(obligations.map((o) => o.actor))).filter(Boolean)];

  const filteredObligations = obligations.filter((o) => {
    return actorFilter === 'ALL' || o.actor.toLowerCase() === actorFilter.toLowerCase();
  });

  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
      {/* View Switcher: Obligations vs Rights */}
      <div style={{
        display: 'flex',
        background: 'var(--bg-input)',
        padding: '3px',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)'
      }}>
        <button
          onClick={() => setViewMode('obligations')}
          style={{
            flex: 1,
            padding: '6px',
            fontSize: '0.78rem',
            fontWeight: 600,
            background: viewMode === 'obligations' ? 'var(--accent-primary)' : 'transparent',
            color: viewMode === 'obligations' ? '#ffffff' : 'var(--text-secondary)',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer'
          }}
        >
          Obligations ({obligations.length})
        </button>
        <button
          onClick={() => setViewMode('rights')}
          style={{
            flex: 1,
            padding: '6px',
            fontSize: '0.78rem',
            fontWeight: 600,
            background: viewMode === 'rights' ? 'var(--accent-primary)' : 'transparent',
            color: viewMode === 'rights' ? '#ffffff' : 'var(--text-secondary)',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer'
          }}
        >
          Rights & Privileges ({rights.length})
        </button>
      </div>

      {viewMode === 'obligations' ? (
        <>
          {/* Actor filter buttons */}
          {actors.length > 2 && (
            <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px' }}>
              {actors.map((act) => (
                <button
                  key={act}
                  onClick={() => setActorFilter(act)}
                  style={{
                    background: actorFilter === act ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.04)',
                    color: actorFilter === act ? '#a5b4fc' : 'var(--text-secondary)',
                    border: `1px solid ${actorFilter === act ? 'rgba(99, 102, 241, 0.5)' : 'var(--border-subtle)'}`,
                    borderRadius: 'var(--radius-full)',
                    padding: '2px 8px',
                    fontSize: '0.7rem',
                    cursor: 'pointer'
                  }}
                >
                  {act}
                </button>
              ))}
            </div>
          )}

          {/* Obligations Cards */}
          {filteredObligations.map((ob, idx) => (
            <div
              key={ob.id || idx}
              className="glass-card"
              style={{
                padding: '14px',
                borderLeft: ob.is_ambiguous ? '4px solid #f59e0b' : '4px solid var(--accent-primary)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span className="badge badge-indigo">
                  <UserCheck size={11} /> {ob.actor}
                </span>
                <span className="badge badge-muted" style={{ fontSize: '0.65rem' }}>
                  Clause {ob.source_clause_number || '§'} • P. {ob.source_page}
                </span>
              </div>

              <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#f8fafc', marginBottom: '8px' }}>
                {ob.action}
              </div>

              {/* Deadline & Trigger badges */}
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '10px' }}>
                {ob.deadline && (
                  <span className="badge badge-amber" style={{ fontSize: '0.68rem' }}>
                    <Clock size={11} /> Deadline: {ob.deadline}
                  </span>
                )}
                {ob.trigger && (
                  <span className="badge badge-muted" style={{ fontSize: '0.68rem' }}>
                    Trigger: {ob.trigger}
                  </span>
                )}
              </div>

              {/* Ambiguity representation (Section 10 Requirement) */}
              {ob.is_ambiguous && (
                <div style={{
                  padding: '8px 10px',
                  background: 'rgba(245, 158, 11, 0.1)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.72rem',
                  color: '#fde68a',
                  marginBottom: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  <AlertCircle size={14} style={{ flexShrink: 0 }} />
                  <span>Ambiguity: {ob.ambiguity_reason || 'Unspecified conditional timing.'}</span>
                </div>
              )}

              <button
                onClick={() => onFocusClause(ob.source_clause_number || '', ob.source_page, ob.excerpt || ob.action)}
                className="btn btn-ghost btn-sm"
                style={{ fontSize: '0.7rem', padding: '2px 4px', color: 'var(--accent-primary)' }}
              >
                View supporting clause →
              </button>
            </div>
          ))}
        </>
      ) : (
        /* Rights View */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {rights.map((r, idx) => (
            <div
              key={r.id || idx}
              className="glass-card"
              style={{
                padding: '14px',
                borderLeft: '4px solid #10b981'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span className="badge badge-emerald">
                  <Shield size={11} /> {r.holder}
                </span>
                <span className="badge badge-muted" style={{ fontSize: '0.65rem' }}>
                  Clause {r.source_clause_number || '§'} • P. {r.source_page}
                </span>
              </div>

              <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#f8fafc', marginBottom: '8px' }}>
                {r.right_text}
              </div>

              {r.condition && (
                <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  Condition: {r.condition}
                </div>
              )}

              <button
                onClick={() => onFocusClause(r.source_clause_number || '', r.source_page, r.excerpt || r.right_text)}
                className="btn btn-ghost btn-sm"
                style={{ fontSize: '0.7rem', padding: '2px 4px', color: 'var(--accent-emerald)' }}
              >
                View supporting clause →
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
