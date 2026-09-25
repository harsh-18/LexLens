import os
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from backend.app.config import settings
from backend.app.services.cache import embedding_cache

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        pass

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        pass

# =====================================================================
# Google Gemini Provider Implementation
# =====================================================================
class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Google GenAI Client: {e}")

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        if not self.client:
            raise RuntimeError("Gemini Client is not configured. Check GOOGLE_API_KEY.")
        
        contents = prompt
        if system_instruction:
            contents = f"SYSTEM INSTRUCTIONS:\n{system_instruction}\n\nUSER PROMPT:\n{prompt}"
            
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini generate_text error: {e}")
            raise

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        enhanced_prompt = (
            f"{prompt}\n\n"
            "CRITICAL: Return ONLY valid, parseable JSON matching the requested structure. "
            "Do NOT include markdown fences, backticks, or preamble text."
        )
        raw = self.generate_text(enhanced_prompt, system_instruction)
        
        # Clean backticks if model wrapped in ```json ... ```
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
            
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as err:
            logger.warning(f"JSON parsing error: {err}. Raw output was:\n{raw[:300]}")
            # Attempt to extract outermost JSON object or list
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(cleaned[start:end+1])
                except Exception:
                    pass
            raise ValueError(f"Model failed to produce valid JSON: {err}")

class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.model = model or settings.GEMINI_EMBEDDING_MODEL
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Google GenAI Embedding Client: {e}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.client:
            return [FallbackEmbeddingProvider().embed_query(t) for t in texts]
        
        embeddings = []
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            for text in batch:
                cache_key = f"{self.model}:{text}"
                cached = embedding_cache.get(cache_key)
                if cached is not None:
                    embeddings.append(cached)
                    continue

                try:
                    res = self.client.models.embed_content(
                        model=self.model,
                        contents=text[:8000]
                    )
                    vec = res.embeddings[0].values
                    embedding_cache.set(cache_key, vec)
                    embeddings.append(vec)
                except Exception as e:
                    logger.warning(f"Gemini embedding fallback for item: {e}")
                    embeddings.append(FallbackEmbeddingProvider().embed_query(text))
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        if not self.client:
            return FallbackEmbeddingProvider().embed_query(query)

        cache_key = f"{self.model}:{query}"
        cached = embedding_cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            res = self.client.models.embed_content(
                model=self.model,
                contents=query[:4000]
            )
            vec = res.embeddings[0].values
            embedding_cache.set(cache_key, vec)
            return vec
        except Exception as e:
            logger.warning(f"Gemini embedding fallback for query: {e}")
            return FallbackEmbeddingProvider().embed_query(query)

# =====================================================================
# Deterministic Fallback Embedding Provider (for offline tests)
# =====================================================================
class FallbackEmbeddingProvider(BaseEmbeddingProvider):
    """Zero-dependency hash-based pseudo-embedding (dim=384) for fast offline testing."""
    def __init__(self, dim: int = 384):
        self.dim = dim

    def embed_query(self, query: str) -> List[float]:
        import math
        vec = [0.0] * self.dim
        tokens = query.lower().split()
        if not tokens:
            return vec
        for token in tokens:
            idx = abs(hash(token)) % self.dim
            vec[idx] += 1.0
        # Normalize
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]

# =====================================================================
# AI Provider Factory
# =====================================================================
class AIProviderFactory:
    _llm_instance: Optional[BaseLLMProvider] = None
    _embed_instance: Optional[BaseEmbeddingProvider] = None

    @classmethod
    def get_llm_provider(cls) -> BaseLLMProvider:
        if cls._llm_instance is None:
            if settings.GOOGLE_API_KEY:
                cls._llm_instance = GeminiLLMProvider()
            else:
                logger.warning("No GOOGLE_API_KEY found; AI operations will require configuration.")
                cls._llm_instance = GeminiLLMProvider()
        return cls._llm_instance

    @classmethod
    def get_embedding_provider(cls) -> BaseEmbeddingProvider:
        if cls._embed_instance is None:
            if settings.GOOGLE_API_KEY:
                cls._embed_instance = GeminiEmbeddingProvider()
            else:
                cls._embed_instance = FallbackEmbeddingProvider()
        return cls._embed_instance
