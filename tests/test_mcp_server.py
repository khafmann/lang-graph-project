"""Tests for MCP server tools with SQLite persistence."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server.server import (
    list_products,
    get_product,
    add_product,
    update_product,
    delete_product,
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
        assert len(products) == 3

    def test_list_products_by_category(self):
        """Test filtering products by category."""
        products = list_products(category="Электроника")
        assert isinstance(products, list)
        assert len(products) == 2
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
        assert product["name"] == "Ноутбук"
        assert product["price"] == 50000
        assert product["category"] == "Электроника"
        assert product["in_stock"] is True

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

    def test_add_product_default_in_stock(self):
        """Test adding a product with default in_stock=True."""
        new_product = add_product(
            name="Товар без указания наличия",
            price=500,
            category="Тест"
        )
        assert new_product["in_stock"] is True


class TestUpdateProduct:
    """Tests for update_product tool."""

    def test_update_product_name(self):
        """Test updating product name."""
        result = update_product(product_id=1, name="Игровой ноутбук")
        assert result["name"] == "Игровой ноутбук"
        assert result["price"] == 50000  # unchanged

    def test_update_product_price(self):
        """Test updating product price."""
        result = update_product(product_id=1, price=45000)
        assert result["price"] == 45000
        assert result["name"] == "Ноутбук"  # unchanged

    def test_update_product_multiple_fields(self):
        """Test updating multiple fields at once."""
        result = update_product(
            product_id=2,
            name="iPhone 15",
            price=80000,
            in_stock=False
        )
        assert result["name"] == "iPhone 15"
        assert result["price"] == 80000
        assert result["in_stock"] is False

    def test_update_nonexistent_product(self):
        """Test updating a product that doesn't exist."""
        result = update_product(product_id=9999, name="Не существует")
        assert "error" in result


class TestDeleteProduct:
    """Tests for delete_product tool."""

    def test_delete_existing_product(self):
        """Test deleting a product that exists."""
        initial_count = len(get_products_storage())
        result = delete_product(product_id=3)

        assert result["success"] is True
        assert len(get_products_storage()) == initial_count - 1

        # Verify product is gone
        check = get_product(product_id=3)
        assert "error" in check

    def test_delete_nonexistent_product(self):
        """Test deleting a product that doesn't exist."""
        result = delete_product(product_id=9999)
        assert "error" in result


class TestGetStatistics:
    """Tests for get_statistics tool."""

    def test_get_statistics(self):
        """Test getting product statistics."""
        stats = get_statistics()

        assert isinstance(stats, dict)
        assert stats["total_count"] == 3
        assert stats["average_price"] == round((50000 + 30000 + 15000) / 3, 2)
        assert stats["in_stock_count"] == 2
        assert isinstance(stats["categories"], dict)
        assert stats["categories"]["Электроника"] == 2
        assert stats["categories"]["Мебель"] == 1

    def test_statistics_after_adding_product(self):
        """Test statistics update after adding a product."""
        add_product(name="Новый товар", price=10000, category="Электроника")
        stats = get_statistics()

        assert stats["total_count"] == 4
        assert stats["categories"]["Электроника"] == 3
