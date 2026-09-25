import React from 'react';
import { Sparkles, Upload, Scale, Search, ShieldCheck, GitCompare, FileText, ArrowRight } from 'lucide-react';

interface LandingHeroProps {
  onTryDemo: () => void;
  onUpload: () => void;
  isLoadingDemo: boolean;
}

export const LandingHero: React.FC<LandingHeroProps> = ({ onTryDemo, onUpload, isLoadingDemo }) => {
  return (
    <div style={{
      maxWidth: '1100px',
      margin: '40px auto',
      padding: '0 24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '36px'
    }}>
      {/* Hero Banner */}
      <div style={{
        textAlign: 'center',
        padding: '50px 30px',
        borderRadius: 'var(--radius-lg)',
        background: 'linear-gradient(180deg, rgba(20, 27, 45, 0.8) 0%, rgba(11, 15, 26, 0.95) 100%)',
        border: '1px solid var(--border-subtle)',
        boxShadow: 'var(--shadow-lg)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Glow backdrop */}
        <div style={{
          position: 'absolute',
          top: '-10%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '400px',
          height: '200px',
          background: 'radial-gradient(ellipse at center, rgba(99, 102, 241, 0.25), transparent 70%)',
          pointerEvents: 'none'
        }} />

        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 14px',
          borderRadius: 'var(--radius-full)',
          background: 'rgba(99, 102, 241, 0.12)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          marginBottom: '20px'
        }}>
          <Sparkles size={14} color="#a5b4fc" />
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#c7d2fe' }}>
            Production-Grade AI Legal Document Intelligence
          </span>
        </div>

        <h1 style={{
          fontSize: '3rem',
          lineHeight: 1.15,
          marginBottom: '16px',
          background: 'linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          Know what you signed.<br />
          Know what it means.<br />
          <span style={{
            background: 'linear-gradient(135deg, #818cf8 0%, #38bdf8 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Know what to ask next.
          </span>
        </h1>

        <p style={{
          fontSize: '1.05rem',
          color: 'var(--text-secondary)',
          maxWidth: '680px',
          margin: '0 auto 30px auto',
          lineHeight: 1.6
        }}>
          LexLens transforms unstructured contracts into structured knowledge graphs—extracting obligations,
          cross-clause contradictions, absent protections, and verifiable citations without pretending to be your lawyer.
        </p>

        {/* CTA Buttons */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '14px', flexWrap: 'wrap' }}>
          <button
            onClick={onTryDemo}
            className="btn btn-primary btn-lg pulse-glow"
            disabled={isLoadingDemo}
          >
            <Sparkles size={18} />
            {isLoadingDemo ? 'Loading Demo Agreement...' : 'Try Demo (Instant Sample)'}
          </button>

          <button onClick={onUpload} className="btn btn-secondary btn-lg">
            <Upload size={18} />
            Upload Your Agreement
          </button>
        </div>

        <div style={{
          marginTop: '20px',
          fontSize: '0.78rem',
          color: 'var(--text-muted)'
        }}>
          Includes sample Senior Software Architect employment contract with real-world payment & notice contradictions.
        </div>
      </div>

      {/* 4 Pillars Grid (Section 54) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '16px'
      }}>
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            background: 'rgba(99, 102, 241, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '12px'
          }}>
            <Search size={18} color="var(--accent-primary)" />
          </div>
          <h4 style={{ fontSize: '0.95rem', marginBottom: '6px' }}>1. Understand</h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Plain-language explanations for complex clauses with progressive disclosure and zero legalese obfuscation.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            background: 'rgba(16, 185, 129, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '12px'
          }}>
            <ShieldCheck size={18} color="var(--accent-emerald)" />
          </div>
          <h4 style={{ fontSize: '0.95rem', marginBottom: '6px' }}>2. Verify</h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Flag internal contradictions (e.g. 30 vs 60 day payment terms) and audit absent protections with exact evidence links.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            background: 'rgba(6, 182, 212, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '12px'
          }}>
            <GitCompare size={18} color="var(--accent-cyan)" />
          </div>
          <h4 style={{ fontSize: '0.95rem', marginBottom: '6px' }}>3. Compare</h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Side-by-side contract diffing tracking shifting deadlines, modified notice windows, and revised restrictive covenants.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            background: 'rgba(245, 158, 11, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '12px'
          }}>
            <Scale size={18} color="var(--accent-amber)" />
          </div>
          <h4 style={{ fontSize: '0.95rem', marginBottom: '6px' }}>4. Prepare</h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Synthesize an attorney-ready consultation memo with critical facts, issues, and targeted questions for counsel.
          </p>
        </div>
      </div>
    </div>
  );
};
