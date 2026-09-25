import React, { useState, useEffect } from 'react';
import { X, GitCompare, ArrowRight, CheckCircle2, AlertTriangle, Layers, Loader2, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { DocumentMetadata, ComparisonResponse } from '../types';

interface ContractComparisonModalProps {
  isOpen: boolean;
  onClose: () => void;
  documents: DocumentMetadata[];
  defaultDocAId: string | null;
}

export const ContractComparisonModal: React.FC<ContractComparisonModalProps> = ({
  isOpen,
  onClose,
  documents,
  defaultDocAId
}) => {
  const [docAId, setDocAId] = useState<string>('');
  const [docBId, setDocBId] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && documents.length >= 2) {
      const v1 = documents.find((d) => d.id.includes('v1')) || documents[0];
      const v2 = documents.find((d) => d.id.includes('v2')) || documents[1];
      setDocAId(v1.id);
      setDocBId(v2.id);
      // Auto-run comparison on open if not already compared
      executeCompare(v1.id, v2.id);
    } else if (isOpen && documents.length === 1) {
      setDocAId(documents[0].id);
      setDocBId(documents[0].id);
    }
  }, [isOpen, documents]);

  const executeCompare = async (aId: string, bId: string) => {
    if (!aId || !bId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.compareDocuments(aId, bId);
      setComparison(res);
    } catch (err: any) {
      setError(err.message || 'Comparison failed');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: '24px'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '980px',
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
            <div style={{
              width: '34px',
              height: '34px',
              borderRadius: '8px',
              background: 'rgba(99, 102, 241, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <GitCompare size={18} color="var(--accent-primary)" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Contract Version Comparison</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                Differential clause analysis, modified obligations, and shifting risk allocations.
              </p>
            </div>
          </div>
          <button onClick={onClose} className="btn-ghost" style={{ padding: '6px', borderRadius: '50%' }}>
            <X size={20} />
          </button>
        </div>

        {/* Document Selection Toolbar */}
        <div style={{
          padding: '14px 24px',
          background: 'rgba(11, 15, 26, 0.6)',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
            {/* Version A Selector */}
            <div style={{ flex: 1, minWidth: '240px' }}>
              <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Base Version A
              </label>
              <select
                id="select-version-a"
                value={docAId}
                onChange={(e) => {
                  setDocAId(e.target.value);
                  executeCompare(e.target.value, docBId);
                }}
                style={{
                  width: '100%',
                  background: 'var(--bg-input)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '8px 12px',
                  fontSize: '0.84rem'
                }}
              >
                {documents.map((d) => (
                  <option key={d.id} value={d.id}>{d.title}</option>
                ))}
              </select>
            </div>

            <div style={{ marginTop: '16px', color: 'var(--text-muted)' }}>
              <ArrowRight size={18} />
            </div>

            {/* Version B Selector */}
            <div style={{ flex: 1, minWidth: '240px' }}>
              <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Revised Version B
              </label>
              <select
                id="select-version-b"
                value={docBId}
                onChange={(e) => {
                  setDocBId(e.target.value);
                  executeCompare(docAId, e.target.value);
                }}
                style={{
                  width: '100%',
                  background: 'var(--bg-input)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '8px 12px',
                  fontSize: '0.84rem'
                }}
              >
                {documents.map((d) => (
                  <option key={d.id} value={d.id}>{d.title}</option>
                ))}
              </select>
            </div>

            <div style={{ marginTop: '16px' }}>
              <button
                id="btn-run-comparison"
                onClick={() => executeCompare(docAId, docBId)}
                className="btn btn-primary"
                disabled={loading || !docAId || !docBId}
              >
                {loading ? (
                  <>
                    <Loader2 size={15} className="highlight-pulse" />
                    Comparing...
                  </>
                ) : (
                  'Re-run Comparison'
                )}
              </button>
            </div>
          </div>

          {/* Quick preset pills for 1-click comparison */}
          {documents.length >= 2 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>Presets:</span>
              <button
                onClick={() => {
                  const v1 = documents.find((d) => d.id.includes('v1')) || documents[0];
                  const v2 = documents.find((d) => d.id.includes('v2')) || documents[1];
                  setDocAId(v1.id);
                  setDocBId(v2.id);
                  executeCompare(v1.id, v2.id);
                }}
                className="btn btn-ghost btn-sm"
                style={{
                  background: 'rgba(99, 102, 241, 0.1)',
                  color: '#a5b4fc',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  padding: '3px 8px',
                  fontSize: '0.72rem'
                }}
              >
                <Sparkles size={12} />
                Employment Agreement (v1 Initial vs v2 Revised Counter-Offer)
              </button>
            </div>
          )}
        </div>

        {/* Content Area */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
          {error && (
            <div style={{
              padding: '12px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--accent-rose-soft)',
              color: '#fda4af',
              fontSize: '0.85rem',
              marginBottom: '16px'
            }}>
              {error}
            </div>
          )}

          {loading && (
            <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-secondary)' }}>
              <Loader2 size={28} className="highlight-pulse" style={{ margin: '0 auto 12px auto' }} />
              <p style={{ fontSize: '0.9rem', fontWeight: 600 }}>Analyzing Version Differences...</p>
              <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                Comparing clauses, shifted deadlines, modified obligations, and liability caps.
              </p>
            </div>
          )}

          {comparison && !loading && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Executive Summary */}
              <div className="glass-card" style={{ padding: '16px', borderLeft: '4px solid var(--accent-cyan)' }}>
                <h4 style={{ fontSize: '0.9rem', marginBottom: '8px', color: '#67e8f9' }}>Executive Diff Summary</h4>
                <p style={{ fontSize: '0.85rem', lineHeight: 1.6, color: '#e2e8f0' }}>
                  {comparison.executive_summary}
                </p>
              </div>

              {/* Key Differences Table (Section 22 Requirement) */}
              <div className="glass-card" style={{ padding: '16px', overflowX: 'auto' }}>
                <h4 style={{ fontSize: '0.9rem', marginBottom: '12px' }}>Material Terms Comparison</h4>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-subtle)', textAlign: 'left', color: 'var(--text-muted)' }}>
                      <th style={{ padding: '8px 12px' }}>Topic</th>
                      <th style={{ padding: '8px 12px' }}>Version A (Initial)</th>
                      <th style={{ padding: '8px 12px' }}>Version B (Revised)</th>
                      <th style={{ padding: '8px 12px' }}>Significance</th>
                      <th style={{ padding: '8px 12px' }}>Analysis</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparison.key_differences_table.map((row, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                        <td style={{ padding: '10px 12px', fontWeight: 700, color: '#f8fafc' }}>{row.topic}</td>
                        <td style={{ padding: '10px 12px', color: '#cbd5e1' }}>{row.version_a_value}</td>
                        <td style={{ padding: '10px 12px', color: '#67e8f9', fontWeight: 600 }}>{row.version_b_value}</td>
                        <td style={{ padding: '10px 12px' }}>
                          <span className={`badge ${
                            row.significance === 'Critical' ? 'badge-rose' :
                            row.significance === 'Notable' ? 'badge-amber' : 'badge-muted'
                          }`}>
                            {row.significance}
                          </span>
                        </td>
                        <td style={{ padding: '10px 12px', color: 'var(--text-secondary)' }}>{row.analysis}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Clause-level Diffs */}
              <div className="glass-card" style={{ padding: '16px' }}>
                <h4 style={{ fontSize: '0.9rem', marginBottom: '12px' }}>Clause-by-Clause Modifications</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {comparison.clause_diffs.map((diff, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '10px 14px',
                        background: 'rgba(0, 0, 0, 0.25)',
                        borderRadius: 'var(--radius-sm)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        fontSize: '0.8rem'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span className={`badge ${
                          diff.status === 'Modified' ? 'badge-amber' :
                          diff.status === 'Added' ? 'badge-emerald' :
                          diff.status === 'Removed' ? 'badge-rose' : 'badge-muted'
                        }`}>
                          {diff.status}
                        </span>
                        <div>
                          <strong>{diff.clause_identifier}</strong> • {diff.title}
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>{diff.change_summary}</div>
                        </div>
                      </div>
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
