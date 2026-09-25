import React, { useState, useEffect } from 'react';
import { X, Printer, Download, Scale, AlertCircle, HelpCircle, CheckSquare, Clock, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { ConsultationBriefResponse } from '../types';

interface LawyerBriefModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
  documentTitle: string;
}

export const LawyerBriefModal: React.FC<LawyerBriefModalProps> = ({
  isOpen,
  onClose,
  documentId,
  documentTitle
}) => {
  const [brief, setBrief] = useState<ConsultationBriefResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && documentId) {
      loadBrief();
    }
  }, [isOpen, documentId]);

  const loadBrief = async () => {
    setLoading(true);
    try {
      const res = await api.generateConsultationBrief(documentId);
      setBrief(res);
    } catch (err) {
      console.error('Failed to load consultation brief:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.85)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: '24px'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '880px',
        maxHeight: '92vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(15, 20, 34, 0.9)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Scale size={20} color="var(--accent-primary)" />
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Lawyer Consultation Preparation Brief</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                Structured briefing packet for your attorney meeting.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button onClick={handlePrint} className="btn btn-secondary btn-sm">
              <Printer size={14} /> Print / Export PDF
            </button>
            <button onClick={onClose} className="btn-ghost" style={{ padding: '6px', borderRadius: '50%' }}>
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Brief Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '28px 36px', backgroundColor: '#0c101c' }}>
          {loading && (
            <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-secondary)' }}>
              <Loader2 size={24} className="highlight-pulse" style={{ margin: '0 auto 12px auto' }} />
              <p style={{ fontSize: '0.9rem', fontWeight: 600 }}>Synthesizing Consultation Brief...</p>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Extracting critical facts, attention areas, and strategic questions for counsel.
              </p>
            </div>
          )}

          {brief && !loading && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
              {/* Top Meta Header */}
              <div style={{
                borderBottom: '2px solid rgba(255, 255, 255, 0.08)',
                paddingBottom: '16px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f8fafc', marginBottom: '4px' }}>
                      Client Legal Briefing Memo
                    </h2>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      Regarding: <strong style={{ color: '#f8fafc' }}>{brief.document_title}</strong>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                    <div>Prepared by LexLens Intelligence</div>
                    <div>Date: {brief.prepared_date}</div>
                  </div>
                </div>
              </div>

              {/* Statutory Disclaimer */}
              <div style={{
                padding: '10px 14px',
                background: 'rgba(245, 158, 11, 0.08)',
                border: '1px solid rgba(245, 158, 11, 0.25)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.74rem',
                color: '#fcd34d',
                lineHeight: 1.4
              }}>
                {brief.disclaimer}
              </div>

              {/* 1. Executive Overview */}
              <div>
                <h4 style={{ fontSize: '0.92rem', color: '#a5b4fc', marginBottom: '8px', fontWeight: 700 }}>
                  1. Executive Overview
                </h4>
                <p style={{ fontSize: '0.85rem', lineHeight: 1.6, color: '#cbd5e1' }}>
                  {brief.executive_overview}
                </p>
              </div>

              {/* 2. Relevant Facts */}
              <div>
                <h4 style={{ fontSize: '0.92rem', color: '#a5b4fc', marginBottom: '8px', fontWeight: 700 }}>
                  2. Relevant Commercial & Operational Facts
                </h4>
                <ul style={{ paddingLeft: '20px', fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.6 }}>
                  {brief.relevant_facts.map((f, i) => (
                    <li key={i} style={{ marginBottom: '4px' }}>{f}</li>
                  ))}
                </ul>
              </div>

              {/* 3. Questions to Ask Counsel */}
              <div>
                <h4 style={{ fontSize: '0.92rem', color: '#a5b4fc', marginBottom: '8px', fontWeight: 700 }}>
                  3. Key Questions to Ask Your Lawyer
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {brief.questions_for_counsel.map((q, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '12px 14px',
                        background: 'rgba(255, 255, 255, 0.03)',
                        borderRadius: 'var(--radius-sm)',
                        borderLeft: '3px solid var(--accent-primary)'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span className="badge badge-indigo" style={{ fontSize: '0.65rem' }}>{q.category}</span>
                        {q.context_clause && (
                          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                            Context: {q.context_clause}
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#f8fafc' }}>
                        "{q.question}"
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 4. Potential Issues & Inconsistencies */}
              <div>
                <h4 style={{ fontSize: '0.92rem', color: '#a5b4fc', marginBottom: '8px', fontWeight: 700 }}>
                  4. Potential Issues & Inconsistencies Flagged
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {brief.potential_issues_and_risks.map((issue, i) => (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '0.82rem',
                        color: '#fde68a',
                        background: 'rgba(245, 158, 11, 0.05)',
                        padding: '8px 12px',
                        borderRadius: 'var(--radius-sm)'
                      }}
                    >
                      <AlertCircle size={15} style={{ flexShrink: 0 }} />
                      <span>{issue}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* 5. Documents to Gather */}
              <div>
                <h4 style={{ fontSize: '0.92rem', color: '#a5b4fc', marginBottom: '8px', fontWeight: 700 }}>
                  5. Documents & Evidence to Bring to Consultation
                </h4>
                <ul style={{ paddingLeft: '20px', fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.6 }}>
                  {brief.documents_to_gather.map((doc, i) => (
                    <li key={i} style={{ marginBottom: '4px' }}>{doc}</li>
                  ))}
                </ul>
              </div>

              {/* 6. Action Timeline */}
              <div>
                <h4 style={{ fontSize: '0.92rem', color: '#a5b4fc', marginBottom: '8px', fontWeight: 700 }}>
                  6. Recommended Action Timeline
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {brief.action_timeline.map((item, i) => (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '0.82rem',
                        color: '#cbd5e1',
                        padding: '6px 0'
                      }}
                    >
                      <Clock size={14} color="var(--accent-cyan)" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
