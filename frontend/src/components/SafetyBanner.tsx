import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

export const SafetyBanner: React.FC = () => {
  return (
    <div style={{
      background: 'linear-gradient(90deg, rgba(20, 27, 45, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%)',
      borderBottom: '1px solid rgba(245, 158, 11, 0.25)',
      padding: '7px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      fontSize: '0.78rem',
      color: 'var(--text-secondary)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <ShieldCheck size={16} color="#10b981" />
        <span>
          <strong style={{ color: '#f8fafc' }}>LexLens Legal Intelligence:</strong> Grounded analysis & preparation assistant. 
          Information provided does not constitute formal legal advice and does not substitute for a qualified legal professional.
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#fcd34d' }}>
        <AlertTriangle size={14} />
        <span>Untrusted Document Isolation Active</span>
      </div>
    </div>
  );
};
