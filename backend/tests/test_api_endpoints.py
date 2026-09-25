import pytest
from starlette.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    assert "LexLens" in res.json()["service"]

def test_demo_session_and_listing():
    res = client.post("/api/v1/auth/demo-session")
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    docs_res = client.get("/api/v1/documents", headers=headers)
    assert docs_res.status_code == 200
    docs = docs_res.json()
    assert len(docs) >= 1
    doc_id = docs[0]["id"]

    # Get analysis
    detail_res = client.get(f"/api/v1/documents/{doc_id}", headers=headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["status"] == "analyzed"
    assert len(detail["pages"]) >= 1

def test_evaluation_benchmark_endpoint():
    res = client.post("/api/v1/evaluation/run")
    assert res.status_code == 200
    data = res.json()
    assert data["total_tests"] >= 5
    assert data["passed_tests"] >= 4
    assert data["groundedness_score"] >= 0.8
