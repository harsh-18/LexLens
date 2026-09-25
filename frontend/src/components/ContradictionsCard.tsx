import React from 'react';
import { AlertTriangle, ArrowRight, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { Contradiction } from '../types';

interface ContradictionsCardProps {
  contradictions: Contradiction[];
  onFocusClause: (clauseNumber: string, pageNumber: number, textSnippet: string) => void;
}

export const ContradictionsCard: React.FC<ContradictionsCardProps> = ({
  contradictions,
  onFocusClause
}) => {
  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{
        padding: '12px 16px',
        borderRadius: 'var(--radius-md)',
        background: contradictions.length > 0 ? 'rgba(245, 158, 11, 0.1)' : 'rgba(16, 185, 129, 0.1)',
        border: `1px solid ${contradictions.length > 0 ? 'rgba(245, 158, 11, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        {contradictions.length > 0 ? (
          <ShieldAlert size={22} color="#f59e0b" style={{ flexShrink: 0 }} />
        ) : (
          <CheckCircle2 size={22} color="#10b981" style={{ flexShrink: 0 }} />
        )}
        <div>
          <div style={{
            fontSize: '0.86rem',
            fontWeight: 700,
            color: contradictions.length > 0 ? '#fcd34d' : '#6ee7b7'
          }}>
            {contradictions.length > 0
              ? `${contradictions.length} Potential Inconsistencies Detected`
              : 'No Internal Contradictions Detected'}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            {contradictions.length > 0
              ? 'Provisions appear to specify conflicting obligations or terms. Document should be clarified with counsel.'
              : 'Clauses analyzed demonstrate internal consistency across payment, notice, and operational covenants.'}
          </p>
        </div>
      </div>

      {contradictions.map((item, idx) => (
        <div
          key={item.id || idx}
          className="glass-card"
          style={{
            padding: '16px',
            borderLeft: '4px solid #f59e0b'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#f8fafc' }}>
              {item.title}
            </span>
            <span className="badge badge-amber">{item.severity}</span>
          </div>

          {/* Side by side comparison */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '10px',
            marginBottom: '12px'
          }}>
            {/* Provision A */}
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              padding: '10px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.78rem'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '6px',
                color: '#93c5fd',
                fontWeight: 600
              }}>
                <span>{item.clause_a}</span>
                <span className="badge badge-muted" style={{ fontSize: '0.62rem' }}>P. {item.page_a}</span>
              </div>
              <p style={{ color: '#cbd5e1', lineHeight: 1.4, fontSize: '0.75rem', marginBottom: '8px' }}>
                "{item.text_a.slice(0, 160)}..."
              </p>
              <button
                onClick={() => onFocusClause(item.clause_a, item.page_a, item.text_a)}
                className="btn btn-ghost btn-sm"
                style={{ fontSize: '0.68rem', padding: '2px 6px', color: '#60a5fa' }}
              >
                Inspect in Document →
              </button>
            </div>

            {/* Provision B */}
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              padding: '10px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.78rem'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '6px',
                color: '#fca5a5',
                fontWeight: 600
              }}>
                <span>{item.clause_b}</span>
                <span className="badge badge-muted" style={{ fontSize: '0.62rem' }}>P. {item.page_b}</span>
              </div>
              <p style={{ color: '#cbd5e1', lineHeight: 1.4, fontSize: '0.75rem', marginBottom: '8px' }}>
                "{item.text_b.slice(0, 160)}..."
              </p>
              <button
                onClick={() => onFocusClause(item.clause_b, item.page_b, item.text_b)}
                className="btn btn-ghost btn-sm"
                style={{ fontSize: '0.68rem', padding: '2px 6px', color: '#f87171' }}
              >
                Inspect in Document →
              </button>
            </div>
          </div>

          {/* Explanation */}
          <div style={{
            background: 'rgba(245, 158, 11, 0.08)',
            padding: '10px 12px',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.78rem',
            color: '#fde68a',
            lineHeight: 1.5
          }}>
            <strong>LexLens Analysis: </strong> {item.explanation}
          </div>
        </div>
      ))}
    </div>
  );
};
