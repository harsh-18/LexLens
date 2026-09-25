import json
import math
import re
from typing import List, Dict, Any, Optional
try:
    import numpy as np
except ImportError:
    np = None

from sqlalchemy.orm import Session
from backend.app.models.legal import Chunk, Clause
from backend.app.services.ai_providers import AIProviderFactory
from backend.app.services.cache import query_cache

# In-memory caches for high-throughput sub-millisecond retrieval
_CHUNK_TOKEN_CACHE: Dict[str, List[str]] = {}
_CHUNK_VEC_CACHE: Dict[str, Any] = {}

class HybridRetriever:
    @staticmethod
    def get_chunk_tokens(chunk_id: str, chunk_text: str) -> List[str]:
        """Memoized tokenization for sub-millisecond BM25 scoring."""
        if chunk_id in _CHUNK_TOKEN_CACHE:
            return _CHUNK_TOKEN_CACHE[chunk_id]
        tokens = re.findall(r"\w+", chunk_text.lower())
        if len(_CHUNK_TOKEN_CACHE) > 5000:
            _CHUNK_TOKEN_CACHE.clear()
        _CHUNK_TOKEN_CACHE[chunk_id] = tokens
        return tokens

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        try:
            a = np.asarray(vec_a, dtype=np.float32)
            b = np.asarray(vec_b, dtype=np.float32)
            denom = (np.linalg.norm(a) * np.linalg.norm(b))
            if denom == 0.0:
                return 0.0
            return float(np.dot(a, b) / denom)
        except Exception:
            dot = sum(x * y for x, y in zip(vec_a, vec_b))
            norm_a = math.sqrt(sum(x * x for x in vec_a))
            norm_b = math.sqrt(sum(y * y for y in vec_b))
            if norm_a == 0.0 or norm_b == 0.0:
                return 0.0
            return dot / (norm_a * norm_b)

    @staticmethod
    def bm25_score(query_tokens: List[str], chunk_text: str, chunk_id: Optional[str] = None) -> float:
        """
        Lightweight BM25 term frequency / inverse document frequency scoring
        with memoized tokenization.
        """
        cid = chunk_id or str(hash(chunk_text))
        text_tokens = HybridRetriever.get_chunk_tokens(cid, chunk_text)
        if not text_tokens:
            return 0.0
        
        score = 0.0
        len_norm = len(text_tokens) / 300.0  # normalize relative to average chunk size
        
        for q in query_tokens:
            tf = text_tokens.count(q)
            if tf > 0:
                # BM25 tf saturation formula with k1=1.5, b=0.75
                k1 = 1.5
                b = 0.75
                denom = tf + k1 * (1 - b + b * len_norm)
                score += (tf * (k1 + 1)) / denom
        return score

    @staticmethod
    def hybrid_search(
        document_id: str,
        query: str,
        db: Session,
        top_k: int = 5,
        clause_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        cache_key = f"{document_id}:{clause_filter}:{query.lower().strip()}:{top_k}"
        cached = query_cache.get(cache_key)
        if cached is not None:
            return cached

        # Fetch all chunks for this document
        query_builder = db.query(Chunk).filter(Chunk.document_id == document_id)
        if clause_filter:
            query_builder = query_builder.filter(Chunk.section.ilike(f"%{clause_filter}%"))
        chunks = query_builder.all()

        if not chunks:
            return []

        # 1. Sparse BM25 Scoring with cached tokenization
        q_tokens = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2]
        bm25_ranked = []
        for c in chunks:
            s = HybridRetriever.bm25_score(q_tokens, c.text, chunk_id=c.id)
            bm25_ranked.append((c, s))
        bm25_ranked.sort(key=lambda x: x[1], reverse=True)

        # 2. Vectorized Dense Vector Scoring via NumPy
        embed_provider = AIProviderFactory.get_embedding_provider()
        dense_ranked = []
        try:
            q_emb = embed_provider.embed_query(query)
            q_vec = np.asarray(q_emb, dtype=np.float32)
            q_norm = np.linalg.norm(q_vec)

            # Check if all chunks have embeddings
            valid_chunks = []
            chunk_vectors = []
            for c in chunks:
                if c.embedding_json:
                    if c.id not in _CHUNK_VEC_CACHE:
                        if len(_CHUNK_VEC_CACHE) > 5000:
                            _CHUNK_VEC_CACHE.clear()
                        _CHUNK_VEC_CACHE[c.id] = np.asarray(json.loads(c.embedding_json), dtype=np.float32)
                    vec = _CHUNK_VEC_CACHE[c.id]
                    valid_chunks.append(c)
                    chunk_vectors.append(vec)
                else:
                    dense_ranked.append((c, 0.0))

            if chunk_vectors and q_norm > 0:
                mat = np.vstack(chunk_vectors)
                norms = np.linalg.norm(mat, axis=1) * q_norm
                norms[norms == 0] = 1e-9
                sims = np.dot(mat, q_vec) / norms
                for c, sim in zip(valid_chunks, sims):
                    dense_ranked.append((c, float(sim)))
            else:
                for c in valid_chunks:
                    dense_ranked.append((c, 0.0))

            dense_ranked.sort(key=lambda x: x[1], reverse=True)
        except Exception:
            # Fallback to BM25 ranks
            dense_ranked = [(c, 0.0) for c in chunks]

        # 3. Reciprocal Rank Fusion (RRF)
        # RRF_Score = 1/(60 + rank_bm25) + 1/(60 + rank_dense)
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Chunk] = {}

        for rank, (c, _) in enumerate(bm25_ranked):
            chunk_map[c.id] = c
            rrf_scores[c.id] = rrf_scores.get(c.id, 0.0) + (1.0 / (60.0 + rank + 1))

        for rank, (c, _) in enumerate(dense_ranked):
            chunk_map[c.id] = c
            rrf_scores[c.id] = rrf_scores.get(c.id, 0.0) + (1.0 / (60.0 + rank + 1))

        # Sort by final RRF score
        sorted_candidates = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for chunk_id, score in sorted_candidates:
            c = chunk_map[chunk_id]
            results.append({
                "chunk_id": c.id,
                "document_id": c.document_id,
                "page_number": c.page_number,
                "section": c.section,
                "clause_id": c.clause_id,
                "text": c.text,
                "score": score
            })

        query_cache.set(cache_key, results)
        return results
