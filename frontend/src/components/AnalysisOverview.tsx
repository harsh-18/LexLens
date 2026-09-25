import React from 'react';
import { Users, DollarSign, Globe, Calendar, FileText, CheckCircle2 } from 'lucide-react';
import { FullAnalysis } from '../types';

interface AnalysisOverviewProps {
  analysis: FullAnalysis;
  onGenerateBrief: () => void;
}

export const AnalysisOverview: React.FC<AnalysisOverviewProps> = ({ analysis, onGenerateBrief }) => {
  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Executive Summary Card */}
      <div className="glass-card" style={{ padding: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
            Executive Summary
          </span>
          <span className="badge badge-emerald">Verified Grounded</span>
        </div>
        <p style={{ fontSize: '0.84rem', lineHeight: 1.6, color: '#e2e8f0' }}>
          {analysis.summary || 'Document intelligence extracted and parsed.'}
        </p>

        <div style={{ marginTop: '14px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.04)',
            padding: '6px 12px',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <Globe size={13} color="var(--accent-cyan)" />
            <span>Jurisdiction: <strong>{analysis.jurisdiction}</strong></span>
          </div>

          <div style={{
            background: 'rgba(255, 255, 255, 0.04)',
            padding: '6px 12px',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <FileText size={13} color="var(--accent-primary)" />
            <span>Type: <strong>{analysis.document_type.replace('_', ' ').toUpperCase()}</strong></span>
          </div>
        </div>
      </div>

      {/* Identified Parties */}
      <div className="glass-card" style={{ padding: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
          <Users size={16} color="var(--accent-primary)" />
          <h5 style={{ fontSize: '0.85rem', fontWeight: 700 }}>Identified Parties</h5>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {analysis.parties.map((p, idx) => (
            <div
              key={p.id || idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '8px 12px',
                background: 'rgba(0, 0, 0, 0.25)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.82rem'
              }}
            >
              <div>
                <strong style={{ color: '#f8fafc' }}>{p.name}</strong>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Role: {p.role}</div>
              </div>
              <span className="badge badge-muted" style={{ fontSize: '0.65rem' }}>{p.party_type}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Financial Terms */}
      {analysis.financial_terms && analysis.financial_terms.length > 0 && (
        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
            <DollarSign size={16} color="#10b981" />
            <h5 style={{ fontSize: '0.85rem', fontWeight: 700 }}>Financial Provisions & Amounts</h5>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {analysis.financial_terms.map((f, idx) => (
              <div
                key={f.id || idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 12px',
                  background: 'rgba(16, 185, 129, 0.05)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.82rem'
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, color: '#f8fafc' }}>{f.item}</div>
                  {f.condition && (
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{f.condition}</div>
                  )}
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontWeight: 800, color: '#34d399', fontSize: '0.9rem' }}>{f.amount}</span>
                  {f.frequency && (
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>{f.frequency}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fast CTA to Lawyer Consultation Brief */}
      <div style={{
        padding: '16px',
        borderRadius: 'var(--radius-md)',
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(6, 182, 212, 0.15) 100%)',
        border: '1px solid rgba(99, 102, 241, 0.35)',
        textAlign: 'center'
      }}>
        <h5 style={{ fontSize: '0.9rem', marginBottom: '6px', color: '#e0e7ff' }}>
          Consulting Legal Counsel?
        </h5>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
          Generate a tailored briefing document with key facts, critical clauses, and high-impact questions for your lawyer.
        </p>
        <button onClick={onGenerateBrief} className="btn btn-primary btn-sm" style={{ width: '100%' }}>
          Prepare Lawyer Consultation Brief
        </button>
      </div>
    </div>
  );
};
