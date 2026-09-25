import React from 'react';
import {
  FileText,
  Upload,
  Sparkles,
  GitCompare,
  Activity,
  CheckCircle2,
  Scale
} from 'lucide-react';
import { DocumentMetadata } from '../types';

interface NavbarProps {
  documents: DocumentMetadata[];
  selectedDocId: string | null;
  onSelectDoc: (id: string) => void;
  onOpenUpload: () => void;
  onLoadDemo: () => void;
  onOpenCompare: () => void;
  onOpenEvaluation: () => void;
  onOpenMetrics: () => void;
  isDemoLoading: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  documents,
  selectedDocId,
  onSelectDoc,
  onOpenUpload,
  onLoadDemo,
  onOpenCompare,
  onOpenEvaluation,
  onOpenMetrics,
  isDemoLoading
}) => {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 24px',
      background: 'rgba(15, 20, 34, 0.85)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-subtle)',
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      {/* Brand */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 16px rgba(99, 102, 241, 0.4)'
        }}>
          <Scale size={22} color="#ffffff" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{
              fontFamily: 'var(--font-heading)',
              fontSize: '1.25rem',
              fontWeight: 800,
              background: 'linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              letterSpacing: '-0.02em'
            }}>
              LexLens
            </span>
            <span className="badge badge-indigo" style={{ fontSize: '0.65rem' }}>AI Intelligence</span>
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
            Know what you signed. Know what to ask next.
          </div>
        </div>
      </div>

      {/* Document Selector & Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        {documents.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={16} color="var(--accent-primary)" />
            <select
              value={selectedDocId || ''}
              onChange={(e) => onSelectDoc(e.target.value)}
              style={{
                background: 'var(--bg-input)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '6px 12px',
                fontSize: '0.85rem',
                fontFamily: 'var(--font-main)',
                maxWidth: '260px',
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title} ({d.file_type.toUpperCase()})
                </option>
              ))}
            </select>
          </div>
        )}

        <button
          onClick={onOpenUpload}
          className="btn btn-primary btn-sm"
          title="Upload PDF, DOCX or TXT"
        >
          <Upload size={14} />
          Upload Document
        </button>

        <button
          onClick={onLoadDemo}
          className="btn btn-secondary btn-sm"
          disabled={isDemoLoading}
          style={{ borderColor: 'rgba(99, 102, 241, 0.4)' }}
          title="Load pre-analyzed demo documents with contradictions"
        >
          <Sparkles size={14} color="#a5b4fc" />
          {isDemoLoading ? 'Loading Demo...' : 'Try Demo'}
        </button>

        <button
          onClick={onOpenCompare}
          className="btn btn-secondary btn-sm"
          title="Side-by-side contract version comparison"
        >
          <GitCompare size={14} />
          Compare Versions
        </button>

        <button
          onClick={onOpenEvaluation}
          className="btn btn-ghost btn-sm"
          title="Run automated evaluation benchmark"
        >
          <CheckCircle2 size={15} color="var(--accent-emerald)" />
          Benchmark
        </button>

        <button
          onClick={onOpenMetrics}
          className="btn btn-ghost btn-sm"
          title="System Observability & Latency"
        >
          <Activity size={15} color="var(--accent-cyan)" />
          Telemetry
        </button>
      </div>
    </header>
  );
};
