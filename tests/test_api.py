"""Tests for FastAPI endpoints."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

from src.api.main import app
from src.mcp_server.server import reset_products


@pytest.fixture
def client():
    """Create test client."""
    reset_products()
    with TestClient(app) as c:
        yield c
    reset_products()


class TestHealthEndpoint:
    """Tests for health endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns OK."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


class TestAgentQueryEndpoint:
    """Tests for agent query endpoint."""

    def test_query_list_products(self, client):
        """Test querying for product list."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "Покажи все продукты"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "tools_used" in data
        assert "list_products" in data["tools_used"]
        assert "products" in data["response"]

    def test_query_statistics(self, client):
        """Test querying for statistics."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "Статистика"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "get_statistics" in data["tools_used"]
        assert "statistics" in data["response"]

    def test_query_empty(self, client):
        """Test empty query returns error."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": ""}
        )
        assert response.status_code == 422  # Validation error

    def test_query_get_product(self, client):
        """Test querying for specific product."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "Покажи товар ID 1"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "product" in data["response"]
        assert data["response"]["product"]["name"] == "Ноутбук"

    def test_query_category_filter(self, client):
        """Test querying with category filter."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "Продукты в категории Электроника"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "products" in data["response"]
        # Should contain electronics products
        products = data["response"]["products"]
        assert len(products) >= 2
