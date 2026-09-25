import {
  DocumentMetadata,
  DocumentDetail,
  FullAnalysis,
  QAResponse,
  ComparisonResponse,
  ConsultationBriefResponse,
  EvaluationReportResponse
} from '../types';

const BASE_URL = '/api/v1';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('lexlens_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
}

export const api = {
  // Auth
  async createDemoSession(): Promise<{ access_token: string; user: any }> {
    const res = await fetch(`${BASE_URL}/auth/demo-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to create demo session');
    const data = await res.json();
    localStorage.setItem('lexlens_token', data.access_token);
    return data;
  },

  // Documents
  async listDocuments(): Promise<DocumentMetadata[]> {
    const res = await fetch(`${BASE_URL}/documents`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  async getDocument(id: string): Promise<DocumentDetail> {
    const res = await fetch(`${BASE_URL}/documents/${id}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`Failed to fetch document ${id}`);
    return res.json();
  },

  async uploadDocument(file: File): Promise<DocumentMetadata> {
    const token = localStorage.getItem('lexlens_token');
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${BASE_URL}/documents/upload`, {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to upload document');
    }
    return res.json();
  },

  async deleteDocument(id: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/documents/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`Failed to delete document ${id}`);
  },

  // Analysis
  async triggerAnalysis(id: string): Promise<FullAnalysis> {
    const res = await fetch(`${BASE_URL}/documents/${id}/analyze`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to analyze document');
    }
    return res.json();
  },

  // Grounded Q&A
  async askQuestion(documentId: string, question: string, clauseFilter?: string): Promise<QAResponse> {
    const res = await fetch(`${BASE_URL}/documents/${documentId}/ask`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ question, clause_filter: clauseFilter })
    });
    if (!res.ok) throw new Error('Failed to query document');
    return res.json();
  },

  // Comparison
  async compareDocuments(docAId: string, docBId: string): Promise<ComparisonResponse> {
    const res = await fetch(`${BASE_URL}/comparisons`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ document_a_id: docAId, document_b_id: docBId })
    });
    if (!res.ok) throw new Error('Failed to compare documents');
    return res.json();
  },

  // Consultation Brief
  async generateConsultationBrief(documentId: string): Promise<ConsultationBriefResponse> {
    const res = await fetch(`${BASE_URL}/documents/${documentId}/consultation-brief`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to generate consultation brief');
    return res.json();
  },

  // Evaluation
  async runEvaluation(): Promise<EvaluationReportResponse> {
    const res = await fetch(`${BASE_URL}/evaluation/run`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to run evaluation benchmark');
    return res.json();
  },

  // Metrics
  async getMetrics(): Promise<any> {
    const res = await fetch(`${BASE_URL}/metrics`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch system metrics');
    return res.json();
  }
};
