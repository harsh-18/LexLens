import React, { useState } from 'react';
import { X, Play, CheckCircle2, XCircle, ShieldCheck, Activity, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { EvaluationReportResponse } from '../types';

interface EvaluationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const EvaluationModal: React.FC<EvaluationModalProps> = ({ isOpen, onClose }) => {
  const [report, setReport] = useState<EvaluationReportResponse | null>(null);
  const [running, setRunning] = useState(false);

  if (!isOpen) return null;

  const handleRunBenchmark = async () => {
    setRunning(true);
    try {
      const res = await api.runEvaluation();
      setReport(res);
    } catch (err) {
      console.error('Failed to run benchmark:', err);
    } finally {
      setRunning(false);
    }
  };

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
        maxWidth: '900px',
        maxHeight: '90vh',
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
            <CheckCircle2 size={20} color="var(--accent-emerald)" />
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>AI Evaluation & Groundedness Benchmark</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                Rigorous automated verification of retrieval recall, citation precision, prompt injection defense, and claim faithfulness.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              onClick={handleRunBenchmark}
              className="btn btn-primary btn-sm"
              disabled={running}
            >
              {running ? (
                <>
                  <Loader2 size={14} className="highlight-pulse" />
                  Running Benchmarks...
                </>
              ) : (
                <>
                  <Play size={14} /> Run Live Benchmark
                </>
              )}
            </button>
            <button onClick={onClose} className="btn-ghost" style={{ padding: '6px', borderRadius: '50%' }}>
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
          {!report && !running && (
            <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
              <Activity size={36} color="var(--border-subtle)" style={{ margin: '0 auto 12px auto' }} />
              <p style={{ fontSize: '0.95rem', fontWeight: 600 }}>No evaluation run in current session.</p>
              <p style={{ fontSize: '0.8rem', marginTop: '4px' }}>
                Click "Run Live Benchmark" to execute the test suite against the legal documents.
              </p>
            </div>
          )}

          {report && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Scorecards */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '12px'
              }}>
                <div className="glass-card" style={{ padding: '14px', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                    Overall Pass Rate
                  </div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#34d399', marginTop: '4px' }}>
                    {report.overall_score}%
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                    {report.passed_tests} / {report.total_tests} Tests Passed
                  </div>
                </div>

                <div className="glass-card" style={{ padding: '14px', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                    Groundedness Score
                  </div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#60a5fa', marginTop: '4px' }}>
                    {Math.round(report.groundedness_score * 100)}%
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                    Grounded in text
                  </div>
                </div>

                <div className="glass-card" style={{ padding: '14px', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                    Citation Precision
                  </div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#a78bfa', marginTop: '4px' }}>
                    {Math.round(report.citation_coverage * 100)}%
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                    Exact clause attribution
                  </div>
                </div>

                <div className="glass-card" style={{ padding: '14px', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                    Avg Latency
                  </div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#38bdf8', marginTop: '4px' }}>
                    {Math.round(report.avg_latency_ms)}ms
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                    RAG retrieval & reasoning
                  </div>
                </div>
              </div>

              {/* Detailed Test Cases Table */}
              <div className="glass-card" style={{ padding: '16px' }}>
                <h4 style={{ fontSize: '0.9rem', marginBottom: '12px' }}>Benchmark Test Cases</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {report.results.map((tc) => (
                    <div
                      key={tc.test_id}
                      style={{
                        padding: '12px 14px',
                        background: 'rgba(0, 0, 0, 0.25)',
                        borderRadius: 'var(--radius-sm)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        borderLeft: tc.passed ? '3px solid #10b981' : '3px solid #f43f5e'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        {tc.passed ? (
                          <CheckCircle2 size={18} color="#10b981" />
                        ) : (
                          <XCircle size={18} color="#f43f5e" />
                        )}
                        <div>
                          <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#f8fafc' }}>
                            {tc.name}
                          </div>
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                            Category: {tc.category} • {tc.notes}
                          </div>
                        </div>
                      </div>

                      <div style={{ textAlign: 'right', display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span className="badge badge-muted" style={{ fontSize: '0.68rem' }}>
                          {tc.latency_ms} ms
                        </span>
                        <span className={`badge ${tc.passed ? 'badge-emerald' : 'badge-rose'}`}>
                          {tc.passed ? 'PASSED' : 'FAILED'}
                        </span>
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
