import React from 'react';
import { Calendar, Clock, ArrowDown, AlertCircle } from 'lucide-react';
import { DeadlineItem } from '../types';

interface DeadlinesTimelineProps {
  deadlines: DeadlineItem[];
  onFocusClause: (clauseNumber: string, pageNumber: number, textSnippet: string) => void;
}

export const DeadlinesTimeline: React.FC<DeadlinesTimelineProps> = ({
  deadlines,
  onFocusClause
}) => {
  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{
        padding: '12px 14px',
        borderRadius: 'var(--radius-md)',
        background: 'rgba(99, 102, 241, 0.08)',
        border: '1px solid rgba(99, 102, 241, 0.25)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
      }}>
        <Clock size={18} color="var(--accent-primary)" />
        <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
          Relative durations, notice periods, and milestones mapped directly from contractual triggers.
        </div>
      </div>

      {deadlines.length === 0 ? (
        <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
          No specific deadlines or notice periods detected in this document.
        </div>
      ) : (
        <div style={{ position: 'relative', paddingLeft: '24px' }}>
          {/* Vertical timeline line */}
          <div style={{
            position: 'absolute',
            left: '7px',
            top: '12px',
            bottom: '12px',
            width: '2px',
            background: 'linear-gradient(to bottom, #6366f1, #06b6d4, #10b981)'
          }} />

          {deadlines.map((dl, idx) => (
            <div
              key={dl.id || idx}
              style={{
                position: 'relative',
                marginBottom: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px'
              }}
            >
              {/* Timeline circle node */}
              <div style={{
                position: 'absolute',
                left: '-24px',
                top: '4px',
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                background: 'var(--bg-card)',
                border: '2px solid var(--accent-primary)',
                boxShadow: '0 0 8px rgba(99, 102, 241, 0.5)'
              }} />

              {/* Card */}
              <div className="glass-card" style={{ padding: '12px 14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.86rem', color: '#f8fafc' }}>
                    {dl.event}
                  </span>
                  <span className="badge badge-amber" style={{ fontSize: '0.7rem' }}>
                    {dl.duration_or_date}
                  </span>
                </div>

                {dl.triggering_condition && (
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    Trigger: <span style={{ color: '#cbd5e1' }}>{dl.triggering_condition}</span>
                  </div>
                )}

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span className="badge badge-muted" style={{ fontSize: '0.62rem' }}>
                    Clause {dl.source_clause_number || 'General'} • P. {dl.source_page}
                  </span>
                  <button
                    onClick={() => onFocusClause(dl.source_clause_number || '', dl.source_page, dl.duration_or_date)}
                    className="btn btn-ghost btn-sm"
                    style={{ fontSize: '0.7rem', padding: '2px 4px', color: 'var(--accent-primary)' }}
                  >
                    View in text →
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
