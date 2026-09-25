import React, { useState, useEffect } from 'react';
import {
  FileText,
  AlertTriangle,
  CheckSquare,
  Clock,
  ShieldAlert,
  MessageSquare,
  Layers,
  Sparkles,
  Loader2
} from 'lucide-react';
import { api } from './services/api';
import { DocumentMetadata, DocumentDetail, Clause, Citation } from './types';

import { Navbar } from './components/Navbar';
import { SafetyBanner } from './components/SafetyBanner';
import { LandingHero } from './components/LandingHero';
import { ClauseNavigator } from './components/ClauseNavigator';
import { DocumentViewer } from './components/DocumentViewer';
import { AnalysisOverview } from './components/AnalysisOverview';
import { ContradictionsCard } from './components/ContradictionsCard';
import { ObligationsList } from './components/ObligationsList';
import { DeadlinesTimeline } from './components/DeadlinesTimeline';
import { MissingProtectionsCard } from './components/MissingProtectionsCard';
import { GroundedChat } from './components/GroundedChat';

import { UploadModal } from './components/UploadModal';
import { ContractComparisonModal } from './components/ContractComparisonModal';
import { LawyerBriefModal } from './components/LawyerBriefModal';
import { EvaluationModal } from './components/EvaluationModal';
import { MetricsModal } from './components/MetricsModal';

export const App: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [currentDoc, setCurrentDoc] = useState<DocumentDetail | null>(null);
  const [loadingDoc, setLoadingDoc] = useState<boolean>(false);
  const [isDemoLoading, setIsDemoLoading] = useState<boolean>(false);

  // Highlighting & Focus State
  const [highlightedText, setHighlightedText] = useState<string | null>(null);
  const [targetPage, setTargetPage] = useState<number | null>(null);
  const [selectedClause, setSelectedClause] = useState<Clause | null>(null);

  // Right Panel Tab
  const [rightPanelTab, setRightPanelTab] = useState<
    'overview' | 'contradictions' | 'obligations' | 'timeline' | 'missing' | 'chat'
  >('contradictions');

  // Modals
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isCompareOpen, setIsCompareOpen] = useState(false);
  const [isBriefOpen, setIsBriefOpen] = useState(false);
  const [isEvalOpen, setIsEvalOpen] = useState(false);
  const [isMetricsOpen, setIsMetricsOpen] = useState(false);

  // Initial load
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await api.listDocuments();
      setDocuments(docs);
      if (docs.length > 0 && !selectedDocId) {
        setSelectedDocId(docs[0].id);
      }
    } catch {
      // If unauthorized or empty, initialize demo session
      handleLoadDemo();
    }
  };

  // Load document detail when selection changes
  useEffect(() => {
    if (selectedDocId) {
      loadDocumentDetail(selectedDocId);
    }
  }, [selectedDocId]);

  const loadDocumentDetail = async (id: string) => {
    setLoadingDoc(true);
    try {
      const detail = await api.getDocument(id);
      setCurrentDoc(detail);
      // If doc has contradictions, default tab to contradictions for high impact
      if (detail.analysis?.contradictions && detail.analysis.contradictions.length > 0) {
        setRightPanelTab('contradictions');
      } else {
        setRightPanelTab('overview');
      }
    } catch (err) {
      console.error('Failed to load document detail:', err);
    } finally {
      setLoadingDoc(false);
    }
  };

  const handleLoadDemo = async () => {
    setIsDemoLoading(true);
    try {
      await api.createDemoSession();
      const docs = await api.listDocuments();
      setDocuments(docs);
      if (docs.length > 0) {
        setSelectedDocId(docs[0].id);
      }
    } catch (err) {
      console.error('Failed to load demo session:', err);
    } finally {
      setIsDemoLoading(false);
    }
  };

  const handleSelectClause = (clause: Clause) => {
    setSelectedClause(clause);
    setHighlightedText(clause.text.slice(0, 50));
    setTargetPage(clause.page_start);
  };

  const handleFocusCitation = (citation: Citation) => {
    setHighlightedText(citation.excerpt);
    setTargetPage(citation.page_number);
  };

  const handleFocusFromCard = (clauseNum: string, pageNum: number, textSnippet: string) => {
    setHighlightedText(textSnippet.slice(0, 50));
    setTargetPage(pageNum);
  };

  const handleClearHighlight = () => {
    setHighlightedText(null);
    setTargetPage(null);
    setSelectedClause(null);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navbar */}
      <Navbar
        documents={documents}
        selectedDocId={selectedDocId}
        onSelectDoc={(id) => setSelectedDocId(id)}
        onOpenUpload={() => setIsUploadOpen(true)}
        onLoadDemo={handleLoadDemo}
        onOpenCompare={() => setIsCompareOpen(true)}
        onOpenEvaluation={() => setIsEvalOpen(true)}
        onOpenMetrics={() => setIsMetricsOpen(true)}
        isDemoLoading={isDemoLoading}
      />

      {/* Statutory Disclaimer & Guardrails */}
      <SafetyBanner />

      {/* Main Workspace or Landing View */}
      {documents.length === 0 && !loadingDoc ? (
        <LandingHero
          onTryDemo={handleLoadDemo}
          onUpload={() => setIsUploadOpen(true)}
          isLoadingDemo={isDemoLoading}
        />
      ) : loadingDoc ? (
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px',
          color: 'var(--text-secondary)'
        }}>
          <Loader2 size={32} className="highlight-pulse" color="var(--accent-primary)" />
          <div style={{ fontSize: '0.95rem', fontWeight: 600 }}>Loading Legal Intelligence...</div>
        </div>
      ) : currentDoc ? (
        <main
          id="main-workspace"
          role="main"
          aria-label="Legal Document Intelligence Workspace"
          className="workspace-grid"
          style={{ marginTop: '16px' }}
        >
          {/* Left Panel: Clause Navigator */}
          <ClauseNavigator
            clauses={currentDoc.analysis?.clauses || []}
            selectedClauseId={selectedClause?.id || null}
            onSelectClause={handleSelectClause}
          />

          {/* Center Panel: Document Viewer */}
          <DocumentViewer
            document={currentDoc}
            highlightedText={highlightedText}
            targetPage={targetPage}
            selectedClause={selectedClause}
            onClearHighlight={handleClearHighlight}
          />

          {/* Right Panel: Intelligence Suite */}
          <aside
            role="region"
            aria-label="Contract Intelligence Analysis"
            className="glass-panel"
            style={{
              display: 'flex',
              flexDirection: 'column',
              height: '100%',
              overflow: 'hidden'
            }}
          >
            {/* Intelligence Tabs Header */}
            <div
              role="tablist"
              aria-label="Intelligence Navigation Tabs"
              style={{
                display: 'flex',
                borderBottom: '1px solid var(--border-subtle)',
                background: 'rgba(11, 15, 26, 0.6)',
                overflowX: 'auto',
                whiteSpace: 'nowrap'
              }}
            >
              <button
                id="tab-btn-contradictions"
                role="tab"
                aria-selected={rightPanelTab === 'contradictions'}
                aria-controls="panel-contradictions"
                onClick={() => setRightPanelTab('contradictions')}
                style={{
                  padding: '10px 11px',
                  fontSize: '0.74rem',
                  fontWeight: rightPanelTab === 'contradictions' ? 700 : 500,
                  color: rightPanelTab === 'contradictions' ? '#fcd34d' : 'var(--text-secondary)',
                  borderBottom: `2px solid ${rightPanelTab === 'contradictions' ? '#f59e0b' : 'transparent'}`,
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}
              >
                <AlertTriangle size={13} color="#f59e0b" aria-hidden="true" />
                Conflicts ({currentDoc.analysis?.contradictions?.length || 0})
              </button>

              <button
                id="tab-btn-obligations"
                role="tab"
                aria-selected={rightPanelTab === 'obligations'}
                aria-controls="panel-obligations"
                onClick={() => setRightPanelTab('obligations')}
                style={{
                  padding: '10px 11px',
                  fontSize: '0.74rem',
                  fontWeight: rightPanelTab === 'obligations' ? 700 : 500,
                  color: rightPanelTab === 'obligations' ? '#a5b4fc' : 'var(--text-secondary)',
                  borderBottom: `2px solid ${rightPanelTab === 'obligations' ? 'var(--accent-primary)' : 'transparent'}`,
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}
              >
                <CheckSquare size={13} aria-hidden="true" />
                Obligations ({currentDoc.analysis?.obligations?.length || 0})
              </button>

              <button
                id="tab-btn-timeline"
                role="tab"
                aria-selected={rightPanelTab === 'timeline'}
                aria-controls="panel-timeline"
                onClick={() => setRightPanelTab('timeline')}
                style={{
                  padding: '10px 11px',
                  fontSize: '0.74rem',
                  fontWeight: rightPanelTab === 'timeline' ? 700 : 500,
                  color: rightPanelTab === 'timeline' ? '#a5b4fc' : 'var(--text-secondary)',
                  borderBottom: `2px solid ${rightPanelTab === 'timeline' ? 'var(--accent-primary)' : 'transparent'}`,
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}
              >
                <Clock size={13} aria-hidden="true" />
                Timeline ({currentDoc.analysis?.deadlines?.length || 0})
              </button>

              <button
                id="tab-btn-missing"
                role="tab"
                aria-selected={rightPanelTab === 'missing'}
                aria-controls="panel-missing"
                onClick={() => setRightPanelTab('missing')}
                style={{
                  padding: '10px 11px',
                  fontSize: '0.74rem',
                  fontWeight: rightPanelTab === 'missing' ? 700 : 500,
                  color: rightPanelTab === 'missing' ? '#fda4af' : 'var(--text-secondary)',
                  borderBottom: `2px solid ${rightPanelTab === 'missing' ? 'var(--accent-rose)' : 'transparent'}`,
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}
              >
                <ShieldAlert size={13} color="var(--accent-rose)" aria-hidden="true" />
                Missing ({currentDoc.analysis?.missing_protections?.length || 0})
              </button>

              <button
                id="tab-btn-chat"
                role="tab"
                aria-selected={rightPanelTab === 'chat'}
                aria-controls="panel-chat"
                onClick={() => setRightPanelTab('chat')}
                style={{
                  padding: '10px 11px',
                  fontSize: '0.74rem',
                  fontWeight: rightPanelTab === 'chat' ? 700 : 500,
                  color: rightPanelTab === 'chat' ? '#38bdf8' : 'var(--text-secondary)',
                  borderBottom: `2px solid ${rightPanelTab === 'chat' ? '#06b6d4' : 'transparent'}`,
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}
              >
                <MessageSquare size={13} color="var(--accent-cyan)" aria-hidden="true" />
                Q&A
              </button>

              <button
                id="tab-btn-overview"
                role="tab"
                aria-selected={rightPanelTab === 'overview'}
                aria-controls="panel-overview"
                onClick={() => setRightPanelTab('overview')}
                style={{
                  padding: '10px 11px',
                  fontSize: '0.74rem',
                  fontWeight: rightPanelTab === 'overview' ? 700 : 500,
                  color: rightPanelTab === 'overview' ? '#a5b4fc' : 'var(--text-secondary)',
                  borderBottom: `2px solid ${rightPanelTab === 'overview' ? 'var(--accent-primary)' : 'transparent'}`,
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer'
                }}
              >
                Overview
              </button>
            </div>

            {/* Tab Contents */}
            <div
              role="tabpanel"
              id={`panel-${rightPanelTab}`}
              aria-labelledby={`tab-btn-${rightPanelTab}`}
              tabIndex={0}
              style={{ flex: 1, overflowY: 'auto' }}
            >
              {rightPanelTab === 'overview' && currentDoc.analysis && (
                <AnalysisOverview
                  analysis={currentDoc.analysis}
                  onGenerateBrief={() => setIsBriefOpen(true)}
                />
              )}

              {rightPanelTab === 'contradictions' && (
                <ContradictionsCard
                  contradictions={currentDoc.analysis?.contradictions || []}
                  onFocusClause={handleFocusFromCard}
                />
              )}

              {rightPanelTab === 'obligations' && (
                <ObligationsList
                  obligations={currentDoc.analysis?.obligations || []}
                  rights={currentDoc.analysis?.rights || []}
                  onFocusClause={handleFocusFromCard}
                />
              )}

              {rightPanelTab === 'timeline' && (
                <DeadlinesTimeline
                  deadlines={currentDoc.analysis?.deadlines || []}
                  onFocusClause={handleFocusFromCard}
                />
              )}

              {rightPanelTab === 'missing' && (
                <MissingProtectionsCard
                  missingProtections={currentDoc.analysis?.missing_protections || []}
                  onOpenConsultation={() => setIsBriefOpen(true)}
                />
              )}

              {rightPanelTab === 'chat' && (
                <GroundedChat
                  documentId={currentDoc.id}
                  onFocusCitation={handleFocusCitation}
                />
              )}
            </div>
          </aside>
        </main>
      ) : null}

      {/* Modals */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={(doc) => {
          loadDocuments();
          setSelectedDocId(doc.id);
        }}
      />

      <ContractComparisonModal
        isOpen={isCompareOpen}
        onClose={() => setIsCompareOpen(false)}
        documents={documents}
        defaultDocAId={selectedDocId}
      />

      {currentDoc && (
        <LawyerBriefModal
          isOpen={isBriefOpen}
          onClose={() => setIsBriefOpen(false)}
          documentId={currentDoc.id}
          documentTitle={currentDoc.title}
        />
      )}

      <EvaluationModal
        isOpen={isEvalOpen}
        onClose={() => setIsEvalOpen(false)}
      />

      <MetricsModal
        isOpen={isMetricsOpen}
        onClose={() => setIsMetricsOpen(false)}
      />
    </div>
  );
};
