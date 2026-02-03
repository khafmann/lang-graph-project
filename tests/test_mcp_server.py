"""Tests for MCP server tools."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server.server import (
    list_products,
    get_product,
    add_product,
    get_statistics,
    reset_products,
    get_products_storage,
)


@pytest.fixture(autouse=True)
def reset_data():
    """Reset products data before each test."""
    reset_products()
    yield
    reset_products()


class TestListProducts:
    """Tests for list_products tool."""

    def test_list_all_products(self):
        """Test listing all products."""
        products = list_products()
        assert isinstance(products, list)
        assert len(products) >= 3

    def test_list_products_by_category(self):
        """Test filtering products by category."""
        products = list_products(category="Электроника")
        assert isinstance(products, list)
        assert len(products) >= 2
        for product in products:
            assert product["category"].lower() == "электроника"

    def test_list_products_nonexistent_category(self):
        """Test filtering by nonexistent category returns empty list."""
        products = list_products(category="НесуществующаяКатегория")
        assert products == []


class TestGetProduct:
    """Tests for get_product tool."""

    def test_get_existing_product(self):
        """Test getting a product that exists."""
        product = get_product(product_id=1)
        assert isinstance(product, dict)
        assert product["id"] == 1
        assert "name" in product
        assert "price" in product

    def test_get_nonexistent_product(self):
        """Test getting a product that doesn't exist."""
        result = get_product(product_id=9999)
        assert "error" in result


class TestAddProduct:
    """Tests for add_product tool."""

    def test_add_new_product(self):
        """Test adding a new product."""
        initial_count = len(get_products_storage())

        new_product = add_product(
            name="Тестовый товар",
            price=1000,
            category="Тест",
            in_stock=True
        )

        assert isinstance(new_product, dict)
        assert new_product["name"] == "Тестовый товар"
        assert new_product["price"] == 1000
        assert new_product["category"] == "Тест"
        assert new_product["in_stock"] is True
        assert "id" in new_product

        # Verify product was added
        assert len(get_products_storage()) == initial_count + 1


class TestGetStatistics:
    """Tests for get_statistics tool."""

    def test_get_statistics(self):
        """Test getting product statistics."""
        stats = get_statistics()

        assert isinstance(stats, dict)
        assert "total_count" in stats
        assert "average_price" in stats
        assert "in_stock_count" in stats
        assert "categories" in stats

        assert stats["total_count"] >= 3
        assert stats["average_price"] > 0
        assert isinstance(stats["categories"], dict)
