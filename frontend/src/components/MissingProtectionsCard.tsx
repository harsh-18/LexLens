import React from 'react';
import { ShieldAlert, HelpCircle, ArrowRight } from 'lucide-react';
import { MissingProtection } from '../types';

interface MissingProtectionsCardProps {
  missingProtections: MissingProtection[];
  onOpenConsultation: () => void;
}

export const MissingProtectionsCard: React.FC<MissingProtectionsCardProps> = ({
  missingProtections,
  onOpenConsultation
}) => {
  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
      <div style={{
        padding: '12px 14px',
        borderRadius: 'var(--radius-md)',
        background: 'rgba(244, 63, 94, 0.08)',
        border: '1px solid rgba(244, 63, 94, 0.25)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
      }}>
        <ShieldAlert size={20} color="var(--accent-rose)" style={{ flexShrink: 0 }} />
        <div>
          <h5 style={{ fontSize: '0.86rem', fontWeight: 700, color: '#fda4af', marginBottom: '2px' }}>
            Protective Provisions Not Identified
          </h5>
          <p style={{ fontSize: '0.74rem', color: 'var(--text-secondary)' }}>
            Provisions commonly included in standard industry templates that were not clearly identified in the analyzed text.
          </p>
        </div>
      </div>

      {missingProtections.map((m, idx) => (
        <div
          key={m.id || idx}
          className="glass-card"
          style={{
            padding: '14px',
            borderLeft: '4px solid var(--accent-rose)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#f8fafc' }}>
              {m.protection_type}
            </span>
            <span className="badge badge-rose" style={{ fontSize: '0.65rem' }}>
              {m.severity}
            </span>
          </div>

          <p style={{ fontSize: '0.8rem', color: '#cbd5e1', lineHeight: 1.5, marginBottom: '10px' }}>
            {m.description}
          </p>

          <div style={{
            background: 'rgba(0, 0, 0, 0.3)',
            padding: '10px 12px',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.76rem',
            color: '#a5b4fc',
            lineHeight: 1.4
          }}>
            <strong>Recommendation:</strong> {m.recommendation}
          </div>
        </div>
      ))}

      {missingProtections.length > 0 && (
        <button
          onClick={onOpenConsultation}
          className="btn btn-secondary btn-sm"
          style={{ width: '100%', borderColor: 'rgba(244, 63, 94, 0.3)' }}
        >
          Include in Lawyer Consultation Brief →
        </button>
      )}
    </div>
  );
};
