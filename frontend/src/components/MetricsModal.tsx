import React, { useState, useEffect } from 'react';
import { X, Activity, Server, Cpu, Database, ShieldCheck, Zap } from 'lucide-react';
import { api } from '../services/api';

interface MetricsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MetricsModal: React.FC<MetricsModalProps> = ({ isOpen, onClose }) => {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadMetrics();
    }
  }, [isOpen]);

  const loadMetrics = async () => {
    setLoading(true);
    try {
      const data = await api.getMetrics();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load metrics:', err);
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
        maxWidth: '740px',
        maxHeight: '88vh',
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
            <Activity size={20} color="var(--accent-cyan)" />
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>System Telemetry & Observability</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                Live pipeline latency, token consumption, and model provider telemetry.
              </p>
            </div>
          </div>
          <button onClick={onClose} className="btn-ghost" style={{ padding: '6px', borderRadius: '50%' }}>
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
          {metrics && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              {/* Active AI Stack Card */}
              <div className="glass-card" style={{ padding: '16px', borderLeft: '4px solid var(--accent-cyan)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Cpu size={16} color="var(--accent-cyan)" />
                  <h4 style={{ fontSize: '0.9rem', fontWeight: 700 }}>AI Engine & Provider Architecture</h4>
                </div>
                <div style={{ fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.6 }}>
                  <div>Primary LLM: <strong>{metrics.active_ai_provider?.primary_llm}</strong></div>
                  <div>Dense Embeddings: <strong>{metrics.active_ai_provider?.embedding_model}</strong></div>
                  <div>Retrieval Strategy: <strong>{metrics.active_ai_provider?.vector_search}</strong></div>
                </div>
              </div>

              {/* Grid Metrics */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                {/* Documents Stats */}
                <div className="glass-card" style={{ padding: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <Database size={16} color="var(--accent-primary)" />
                    <h5 style={{ fontSize: '0.85rem' }}>Ingested Documents</h5>
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f8fafc' }}>
                    {metrics.documents?.successfully_analyzed} / {metrics.documents?.total_ingested}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Success Rate: {metrics.documents?.success_rate_percentage}%
                  </div>
                </div>

                {/* Grounded Queries */}
                <div className="glass-card" style={{ padding: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <Zap size={16} color="#f59e0b" />
                    <h5 style={{ fontSize: '0.85rem' }}>Grounded Q&A Queries</h5>
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fcd34d' }}>
                    {metrics.grounded_qa?.total_queries}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Avg Latency: {metrics.grounded_qa?.avg_latency_ms} ms • Tokens: {metrics.grounded_qa?.estimated_token_usage}
                  </div>
                </div>
              </div>

              {/* Guardrails Status */}
              <div className="glass-card" style={{ padding: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <ShieldCheck size={16} color="var(--accent-emerald)" />
                  <h5 style={{ fontSize: '0.85rem' }}>AI Safety & Guardrail Controls</h5>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#6ee7b7' }}>
                  ✓ Prompt Injection Defense Shield active (&lt;untrusted_document_data&gt; delimiter enforcement)
                </div>
                <div style={{ fontSize: '0.8rem', color: '#6ee7b7', marginTop: '4px' }}>
                  ✓ Post-generation Claim Validation layer active (verifies numerical & statutory assertions)
                </div>
                <div style={{ fontSize: '0.8rem', color: '#6ee7b7', marginTop: '4px' }}>
                  ✓ Per-tenant document vault isolation enforced
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
