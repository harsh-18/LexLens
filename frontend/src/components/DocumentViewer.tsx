import React, { useState, useEffect, useRef } from 'react';
import { FileText, Search, ZoomIn, ZoomOut, BookOpen, AlertCircle, HelpCircle } from 'lucide-react';
import { DocumentDetail, Clause } from '../types';

interface DocumentViewerProps {
  document: DocumentDetail;
  highlightedText: string | null;
  targetPage: number | null;
  selectedClause: Clause | null;
  onClearHighlight: () => void;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  document,
  highlightedText,
  targetPage,
  selectedClause,
  onClearHighlight
}) => {
  const [fontSize, setFontSize] = useState<number>(14);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'verbatim' | 'plain'>('verbatim');
  const pageRefs = useRef<{ [key: number]: HTMLDivElement | null }>({});

  // Scroll to target page when citation or clause is clicked
  useEffect(() => {
    if (targetPage && pageRefs.current[targetPage]) {
      pageRefs.current[targetPage]?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [targetPage, highlightedText]);

  // Render text with search or citation highlights
  const renderHighlightedContent = (text: string) => {
    if (!text) return null;

    let targetToHighlight = searchTerm.trim();
    if (!targetToHighlight && highlightedText) {
      targetToHighlight = highlightedText.trim().slice(0, 40);
    }

    if (!targetToHighlight) {
      return <span>{text}</span>;
    }

    try {
      const escaped = targetToHighlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const parts = text.split(new RegExp(`(${escaped})`, 'gi'));
      return (
        <span>
          {parts.map((part, i) =>
            part.toLowerCase() === targetToHighlight.toLowerCase() ? (
              <mark key={i} className="highlight-source highlight-pulse">
                {part}
              </mark>
            ) : (
              part
            )
          )}
        </span>
      );
    } catch {
      return <span>{text}</span>;
    }
  };

  return (
    <section
      role="region"
      aria-label="Document Reader and Verbatim Clause Viewer"
      className="glass-panel"
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden'
      }}
    >
      {/* Top Controls Toolbar */}
      <div style={{
        padding: '12px 18px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(11, 15, 26, 0.6)'
      }}>
        {/* Document Title & Pages Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <FileText size={17} color="var(--accent-primary)" aria-hidden="true" />
          <div>
            <div style={{ fontSize: '0.9rem', fontWeight: 700 }}>{document.title}</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              {document.page_count} Pages • {document.file_type.toUpperCase()} • {document.jurisdiction}
            </div>
          </div>
        </div>

        {/* View Mode Toggle: Verbatim Document vs Plain Explanation */}
        <div
          role="tablist"
          aria-label="Document reading mode"
          style={{
            display: 'flex',
            background: 'var(--bg-input)',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)',
            padding: '2px'
          }}
        >
          <button
            role="tab"
            aria-selected={activeTab === 'verbatim'}
            aria-label="Switch to Verbatim Contract Text View"
            onClick={() => setActiveTab('verbatim')}
            style={{
              padding: '4px 12px',
              fontSize: '0.75rem',
              fontWeight: 600,
              background: activeTab === 'verbatim' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'verbatim' ? '#ffffff' : 'var(--text-secondary)',
              border: 'none',
              borderRadius: 'var(--radius-sm)',
              cursor: 'pointer'
            }}
          >
            Verbatim Text
          </button>
          <button
            role="tab"
            aria-selected={activeTab === 'plain'}
            aria-label="Switch to Plain English Explanation View"
            onClick={() => setActiveTab('plain')}
            style={{
              padding: '4px 12px',
              fontSize: '0.75rem',
              fontWeight: 600,
              background: activeTab === 'plain' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'plain' ? '#ffffff' : 'var(--text-secondary)',
              border: 'none',
              borderRadius: 'var(--radius-sm)',
              cursor: 'pointer'
            }}
          >
            Explain Simply
          </button>
        </div>

        {/* Search & Zoom Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Search size={13} color="var(--text-muted)" style={{ position: 'absolute', left: '8px' }} aria-hidden="true" />
            <input
              type="text"
              id="doc-viewer-search-input"
              aria-label="Find text in document pages"
              placeholder="Find in page..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '140px',
                background: 'var(--bg-input)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '4px 8px 4px 26px',
                fontSize: '0.75rem',
                color: 'var(--text-primary)',
                outline: 'none'
              }}
            />
          </div>

          <button
            onClick={() => setFontSize((s) => Math.max(12, s - 1))}
            className="btn-ghost"
            style={{ padding: '4px', borderRadius: '4px' }}
            title="Decrease font size"
            aria-label="Decrease reading font size"
          >
            <ZoomOut size={16} aria-hidden="true" />
          </button>
          <span
            aria-label={`Current font size ${fontSize} pixels`}
            style={{ fontSize: '0.75rem', color: 'var(--text-muted)', minWidth: '24px', textAlign: 'center' }}
          >
            {fontSize}px
          </span>
          <button
            onClick={() => setFontSize((s) => Math.min(20, s + 1))}
            className="btn-ghost"
            style={{ padding: '4px', borderRadius: '4px' }}
            title="Increase font size"
            aria-label="Increase reading font size"
          >
            <ZoomIn size={16} aria-hidden="true" />
          </button>
        </div>
      </div>

      {/* Selected Clause Focus Banner (if active) */}
      {selectedClause && (
        <div style={{
          padding: '10px 18px',
          background: 'rgba(99, 102, 241, 0.1)',
          borderBottom: '1px solid rgba(99, 102, 241, 0.25)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.8rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BookOpen size={16} color="var(--accent-primary)" />
            <span>
              <strong>Focused:</strong> {selectedClause.clause_number ? `§ ${selectedClause.clause_number} ` : ''}
              {selectedClause.title} ({selectedClause.category})
            </span>
          </div>
          <button
            onClick={onClearHighlight}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: '0.75rem',
              textDecoration: 'underline'
            }}
          >
            Reset focus
          </button>
        </div>
      )}

      {/* Main Content Area */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '24px 32px',
        backgroundColor: '#0a0d17'
      }}>
        {activeTab === 'plain' ? (
          /* Plain-Language Explanations Mode (Progressive Disclosure) */
          <div style={{ maxWidth: '780px', margin: '0 auto' }}>
            <div style={{
              padding: '16px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(6, 182, 212, 0.08)',
              border: '1px solid rgba(6, 182, 212, 0.25)',
              marginBottom: '24px',
              display: 'flex',
              gap: '12px'
            }}>
              <HelpCircle size={20} color="var(--accent-cyan)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <h4 style={{ fontSize: '0.9rem', color: '#67e8f9', marginBottom: '4px' }}>
                  Plain-Language Explanations (Non-Lawyer Translation)
                </h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  LexLens simplifies complex legal legalese into accessible terms without changing the underlying legal meaning.
                  This explanation is for informational guidance and does not substitute for a professional legal opinion.
                </p>
              </div>
            </div>

            {document.analysis?.clauses && document.analysis.clauses.length > 0 ? (
              document.analysis.clauses.map((clause, idx) => (
                <div
                  key={clause.id || idx}
                  className="glass-card"
                  style={{
                    padding: '20px',
                    marginBottom: '16px',
                    borderLeft: '4px solid var(--accent-primary)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>
                        {clause.clause_number ? `§ ${clause.clause_number}` : `Clause ${idx + 1}`}
                      </span>
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>• {clause.title}</span>
                    </div>
                    <span className="badge badge-indigo">{clause.category}</span>
                  </div>

                  {/* Plain Language Box */}
                  <div style={{
                    padding: '12px 14px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'rgba(255, 255, 255, 0.03)',
                    marginBottom: '12px',
                    fontSize: '0.86rem',
                    lineHeight: 1.6
                  }}>
                    <strong style={{ color: '#a5b4fc' }}>Plain Meaning: </strong>
                    {clause.plain_explanation || 'Specifies contractual terms and operational rights between the parties.'}
                  </div>

                  {/* Why it Matters / Attention Area */}
                  {clause.risk_note && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '8px',
                      fontSize: '0.8rem',
                      color: '#fcd34d',
                      marginBottom: '10px'
                    }}>
                      <AlertCircle size={15} style={{ flexShrink: 0, marginTop: '2px' }} />
                      <span><strong>Why this matters:</strong> {clause.risk_note}</span>
                    </div>
                  )}

                  {/* Verbatim Source Drawer */}
                  <details style={{ marginTop: '8px' }}>
                    <summary style={{
                      cursor: 'pointer',
                      fontSize: '0.75rem',
                      color: 'var(--text-muted)',
                      userSelect: 'none'
                    }}>
                      View original legal text (Page {clause.page_start})
                    </summary>
                    <div style={{
                      marginTop: '8px',
                      padding: '10px 12px',
                      background: 'rgba(0, 0, 0, 0.4)',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.78rem',
                      fontFamily: 'var(--font-mono)',
                      color: '#94a3b8',
                      lineHeight: 1.5,
                      whiteSpace: 'pre-wrap'
                    }}>
                      {clause.text}
                    </div>
                  </details>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                No analyzed clauses available. Please click 'Analyze Document' to generate plain explanations.
              </div>
            )}
          </div>
        ) : (
          /* Verbatim Document Pages Layout */
          <div style={{ maxWidth: '820px', margin: '0 auto' }}>
            {document.pages && document.pages.length > 0 ? (
              document.pages.map((p) => (
                <div
                  key={p.id}
                  ref={(el) => { pageRefs.current[p.page_number] = el; }}
                  style={{
                    backgroundColor: '#121727',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: 'var(--radius-md)',
                    padding: '36px 44px',
                    marginBottom: '28px',
                    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4)',
                    position: 'relative'
                  }}
                >
                  {/* Page header marker */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
                    paddingBottom: '10px',
                    marginBottom: '20px',
                    fontSize: '0.72rem',
                    color: 'var(--text-muted)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.06em'
                  }}>
                    <span>{document.title}</span>
                    <span className="badge badge-muted">Page {p.page_number} of {document.page_count}</span>
                  </div>

                  {/* Page Text */}
                  <div style={{
                    fontSize: `${fontSize}px`,
                    lineHeight: 1.7,
                    whiteSpace: 'pre-wrap',
                    color: '#e2e8f0',
                    fontFamily: 'var(--font-main)'
                  }}>
                    {renderHighlightedContent(p.text)}
                  </div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>
                No page text extracted.
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
};
