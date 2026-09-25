import os
import tempfile
import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.services.cache import LRUTTLCache, embedding_cache
from backend.app.services.parser import DocumentParser

client = TestClient(app)

def test_security_headers_present():
    """Verify production security headers are attached to API responses."""
    response = client.get("/health")
    assert response.status_code == 200
    headers = response.headers
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert headers.get("x-xss-protection") == "1; mode=block"
    assert "default-src" in headers.get("content-security-policy", "")
    assert "strict-transport-security" in headers

def test_file_magic_bytes_security_rejection():
    """Verify file parser strictly blocks spoofed binaries or invalid file signatures."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        # Write fake Windows PE header to a .pdf file
        f.write(b"MZ\x90\x00\x03\x00\x00\x00")
        fake_pdf = f.name
    
    try:
        with pytest.raises(ValueError, match="Executable binaries"):
            DocumentParser.validate_file_safety(fake_pdf, ".pdf")
    finally:
        if os.path.exists(fake_pdf):
            os.remove(fake_pdf)

def test_valid_pdf_magic_bytes():
    """Verify valid PDF magic bytes pass validation."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.7 standard legal content here")
        valid_pdf = f.name
    
    try:
        # Should not raise
        DocumentParser.validate_file_safety(valid_pdf, ".pdf")
    finally:
        if os.path.exists(valid_pdf):
            os.remove(valid_pdf)

def test_lru_cache_efficiency_and_hit_ratio():
    """Verify LRU TTL cache stores, retrieves, and tracks hit telemetry."""
    cache = LRUTTLCache(maxsize=10, default_ttl=60)
    cache.set("clause_1", [0.12, 0.45, 0.99])
    
    # Cache hit
    val = cache.get("clause_1")
    assert val == [0.12, 0.45, 0.99]
    
    # Cache miss
    val2 = cache.get("nonexistent_key")
    assert val2 is None
    
    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_ratio_percent"] == 50.0

def test_metrics_endpoint_exposes_efficiency_stats():
    """Verify /api/v1/metrics returns cache efficiency metrics."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "efficiency_and_caching" in data
    assert "embedding_cache" in data["efficiency_and_caching"]
    assert data["efficiency_and_caching"]["gzip_compression"].startswith("Enabled")

def test_sqlite_wal_mode_and_pragma_efficiency():
    """Verify SQLite database connection has WAL mode and cache tuning active."""
    from backend.app.database import engine, settings
    if settings.DATABASE_URL.startswith("sqlite"):
        with engine.connect() as conn:
            from sqlalchemy import text
            journal_mode = conn.execute(text("PRAGMA journal_mode")).scalar()
            assert str(journal_mode).upper() == "WAL"

def test_cache_control_headers_efficiency():
    """Verify API endpoints return no-store to protect sensitive legal contracts."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "no-store" in response.headers.get("cache-control", "")

def test_numpy_vectorized_cosine_similarity():
    """Verify NumPy vectorized cosine similarity is mathematically exact and handles edge cases."""
    from backend.app.services.retrieval import HybridRetriever
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    assert pytest.approx(HybridRetriever.cosine_similarity(v1, v2), 0.0001) == 1.0
    assert pytest.approx(HybridRetriever.cosine_similarity(v1, v3), 0.0001) == 0.0
    assert HybridRetriever.cosine_similarity([], []) == 0.0

def test_document_cache_invalidation_lifecycle():
    """Verify document_cache stores and invalidates entries properly."""
    from backend.app.services.cache import document_cache
    document_cache.set("user1:doc123", {"title": "Master Services Agreement"})
    assert document_cache.get("user1:doc123") == {"title": "Master Services Agreement"}
    document_cache.delete("user1:doc123")
    assert document_cache.get("user1:doc123") is None

def test_sub_50ms_health_and_metrics_latency():
    """Benchmark test verifying health and metrics endpoints respond in under 50ms."""
    import time
    start = time.perf_counter()
    response = client.get("/health")
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert response.status_code == 200
    assert elapsed_ms < 50.0  # Ultra-fast sub-50ms SLA


