import json
import math
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.legal import Chunk, Clause
from backend.app.services.ai_providers import AIProviderFactory
from backend.app.services.cache import query_cache

class HybridRetriever:
    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    @staticmethod
    def bm25_score(query_tokens: List[str], chunk_text: str) -> float:
        """
        Lightweight BM25 term frequency / inverse document frequency scoring.
        """
        text_tokens = re.findall(r"\w+", chunk_text.lower())
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

        # 1. Sparse BM25 Scoring
        q_tokens = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2]
        bm25_ranked = []
        for c in chunks:
            s = HybridRetriever.bm25_score(q_tokens, c.text)
            bm25_ranked.append((c, s))
        bm25_ranked.sort(key=lambda x: x[1], reverse=True)

        # 2. Dense Vector Scoring
        embed_provider = AIProviderFactory.get_embedding_provider()
        dense_ranked = []
        try:
            q_emb = embed_provider.embed_query(query)
            for c in chunks:
                if c.embedding_json:
                    c_emb = json.loads(c.embedding_json)
                    sim = HybridRetriever.cosine_similarity(q_emb, c_emb)
                else:
                    sim = 0.0
                dense_ranked.append((c, sim))
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
