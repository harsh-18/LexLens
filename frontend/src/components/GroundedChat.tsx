import React, { useState } from 'react';
import { Send, Sparkles, ShieldCheck, AlertCircle, Bookmark, ArrowRight, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { QAResponse, Citation } from '../types';

interface GroundedChatProps {
  documentId: string;
  onFocusCitation: (citation: Citation) => void;
}

interface ChatMessage {
  sender: 'user' | 'assistant';
  text: string;
  citations?: Citation[];
  unsupported_claims?: string[];
  is_grounded?: boolean;
  groundedness_score?: number;
  latency_ms?: number;
}

const SUGGESTED_QUERIES = [
  'How many days notice are required to resign?',
  'What are the payment and reimbursement deadlines?',
  'What is the scope and duration of the non-compete?',
  'Can the company terminate me without cause?',
  'Are my pre-existing personal coding projects owned by the company?'
];

export const GroundedChat: React.FC<GroundedChatProps> = ({ documentId, onFocusCitation }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: 'assistant',
      text: "Hello! I am your LexLens legal intelligence assistant. Ask any question about this document and I will provide answers grounded strictly in its text with verified citations to exact clauses and pages."
    }
  ]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (questionText?: string) => {
    const q = (questionText || query).trim();
    if (!q || loading) return;

    setMessages((prev) => [...prev, { sender: 'user', text: q }]);
    setQuery('');
    setLoading(true);

    try {
      const res: QAResponse = await api.askQuestion(documentId, q);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: res.answer,
          citations: res.citations,
          unsupported_claims: res.unsupported_claims,
          is_grounded: res.is_grounded,
          groundedness_score: res.groundedness_score,
          latency_ms: res.latency_ms
        }
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: `Error processing question: ${err.message || 'Please check your connection and try again.'}`
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      overflow: 'hidden'
    }}>
      {/* Messages Scroll Area */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px'
      }}>
        {messages.map((m, idx) => (
          <div
            key={idx}
            style={{
              alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '92%',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px'
            }}
          >
            <div style={{
              background: m.sender === 'user'
                ? 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)'
                : 'var(--bg-card)',
              color: '#ffffff',
              padding: '12px 16px',
              borderRadius: m.sender === 'user'
                ? '16px 16px 4px 16px'
                : '16px 16px 16px 4px',
              border: m.sender === 'user' ? 'none' : '1px solid var(--border-subtle)',
              fontSize: '0.84rem',
              lineHeight: 1.55,
              boxShadow: var_shadow(m.sender)
            }}>
              {m.text}

              {/* Citations Block */}
              {m.citations && m.citations.length > 0 && (
                <div style={{
                  marginTop: '12px',
                  paddingTop: '10px',
                  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px'
                }}>
                  <div style={{
                    fontSize: '0.72rem',
                    textTransform: 'uppercase',
                    color: '#a5b4fc',
                    fontWeight: 700,
                    letterSpacing: '0.04em'
                  }}>
                    Document Citations & Evidence
                  </div>
                  {m.citations.map((c, cIdx) => (
                    <div
                      key={cIdx}
                      onClick={() => onFocusCitation(c)}
                      style={{
                        padding: '6px 10px',
                        background: 'rgba(0, 0, 0, 0.3)',
                        borderRadius: 'var(--radius-sm)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        fontSize: '0.74rem',
                        transition: 'var(--transition)'
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(99, 102, 241, 0.25)')}
                      onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(0, 0, 0, 0.3)')}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Bookmark size={12} color="var(--accent-primary)" />
                        <span style={{ fontWeight: 600, color: '#f8fafc' }}>
                          Clause {c.clause_number}
                        </span>
                        <span style={{ color: 'var(--text-muted)' }}>• Page {c.page_number}</span>
                      </div>
                      <span style={{ color: '#60a5fa', fontSize: '0.68rem', display: 'flex', alignItems: 'center', gap: '2px' }}>
                        Jump <ArrowRight size={10} />
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Groundedness Verification Badge & Latency */}
              {m.sender === 'assistant' && m.groundedness_score !== undefined && (
                <div style={{
                  marginTop: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontSize: '0.68rem',
                  color: 'var(--text-muted)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <ShieldCheck size={13} color="#10b981" />
                    <span>Groundedness: <strong>{Math.round((m.groundedness_score || 1) * 100)}%</strong></span>
                  </div>
                  {m.latency_ms && <span>{m.latency_ms} ms</span>}
                </div>
              )}

              {/* Unsupported Claims Alert (Section 21) */}
              {m.unsupported_claims && m.unsupported_claims.length > 0 && (
                <div style={{
                  marginTop: '8px',
                  padding: '6px 10px',
                  background: 'var(--accent-amber-soft)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.72rem',
                  color: '#fcd34d',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  <AlertCircle size={14} style={{ flexShrink: 0 }} />
                  <span>Validation Warning: {m.unsupported_claims.join(' ')}</span>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            <Loader2 size={16} className="highlight-pulse" />
            <span>Retrieving chunks & verifying evidence...</span>
          </div>
        )}
      </div>

      {/* Suggested Prompt Chips */}
      <div style={{
        padding: '8px 16px',
        borderTop: '1px solid var(--border-subtle)',
        display: 'flex',
        gap: '6px',
        overflowX: 'auto',
        whiteSpace: 'nowrap',
        background: 'rgba(11, 15, 26, 0.4)'
      }}>
        {SUGGESTED_QUERIES.map((qText, i) => (
          <button
            key={i}
            onClick={() => handleSend(qText)}
            style={{
              padding: '4px 10px',
              fontSize: '0.7rem',
              borderRadius: 'var(--radius-full)',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <Sparkles size={11} color="var(--accent-primary)" />
            {qText}
          </button>
        ))}
      </div>

      {/* Chat Input Bar */}
      <div style={{
        padding: '12px 16px',
        borderTop: '1px solid var(--border-subtle)',
        background: 'rgba(15, 20, 34, 0.85)',
        display: 'flex',
        gap: '8px'
      }}>
        <input
          type="text"
          placeholder="Ask a question about this document..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          style={{
            flex: 1,
            background: 'var(--bg-input)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '8px 14px',
            fontSize: '0.84rem',
            color: 'var(--text-primary)',
            outline: 'none'
          }}
        />
        <button
          onClick={() => handleSend()}
          className="btn btn-primary"
          disabled={!query.trim() || loading}
          style={{ padding: '8px 14px' }}
        >
          <Send size={15} />
        </button>
      </div>
    </div>
  );
};

function var_shadow(sender: 'user' | 'assistant') {
  return sender === 'user' ? '0 4px 12px rgba(99, 102, 241, 0.3)' : '0 2px 6px rgba(0, 0, 0, 0.3)';
}
