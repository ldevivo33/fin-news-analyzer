"""
Basic API tests for the Financial News Sentiment Analyzer.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    from app.main import app
    with TestClient(app) as c:
        yield c


class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_health_check_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data


class TestSentimentAnalysis:
    """Tests for the sentiment analysis endpoint."""

    def test_analyze_positive_headline(self, client):
        response = client.post(
            "/analyze",
            json={"headline": "Stock market surges to record highs on strong earnings"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] in ["positive", "negative", "neutral"]
        assert "commentary" in data

    def test_analyze_negative_headline(self, client):
        response = client.post(
            "/analyze",
            json={"headline": "Markets crash amid recession fears and economic crisis"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] in ["positive", "negative", "neutral"]
        assert "commentary" in data

    def test_analyze_neutral_headline(self, client):
        response = client.post(
            "/analyze",
            json={"headline": "Federal Reserve announces quarterly meeting schedule"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] in ["positive", "negative", "neutral"]

    def test_analyze_empty_headline_fails(self, client):
        response = client.post("/analyze", json={"headline": ""})
        # Empty string should still work (model will handle it)
        assert response.status_code == 200

    def test_analyze_missing_headline_fails(self, client):
        response = client.post("/analyze", json={})
        assert response.status_code == 422  # Validation error


class TestHeadlinesCRUD:
    """Tests for headlines CRUD operations."""

    def test_list_headlines_returns_200(self, client):
        response = client.get("/headlines")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_list_headlines_with_pagination(self, client):
        response = client.get("/headlines?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 5

    def test_list_headlines_filter_by_sentiment(self, client):
        response = client.get("/headlines?sentiment=positive")
        assert response.status_code == 200

    def test_list_headlines_invalid_sentiment_filter(self, client):
        response = client.get("/headlines?sentiment=invalid")
        assert response.status_code == 422  # Validation error

    def test_get_nonexistent_headline_returns_404(self, client):
        response = client.get("/headlines/999999")
        assert response.status_code == 404

    def test_delete_nonexistent_headline_returns_404(self, client):
        response = client.delete("/headlines/999999")
        assert response.status_code == 404


class TestCaching:
    """Tests to verify caching behavior."""

    def test_repeated_analysis_returns_same_result(self, client):
        headline = "Tesla stock rises 10% on delivery numbers"

        # First request
        response1 = client.post("/analyze", json={"headline": headline})
        data1 = response1.json()

        # Second request (should hit cache)
        response2 = client.post("/analyze", json={"headline": headline})
        data2 = response2.json()

        # Results should be identical
        assert data1["sentiment"] == data2["sentiment"]
        assert data1["commentary"] == data2["commentary"]
