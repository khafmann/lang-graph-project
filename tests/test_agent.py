"""Tests for LangGraph agent."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.graph import ProductAgent, get_agent
from src.agent.mock_llm import MockLLM
from src.agent.tools import calculate_discount, format_product_list
from src.mcp_server.server import reset_products


@pytest.fixture(autouse=True)
def reset_data():
    """Reset products data before each test."""
    reset_products()
    yield
    reset_products()


class TestMockLLM:
    """Tests for Mock LLM parser."""

    def test_parse_list_products(self):
        """Test parsing list products query."""
        llm = MockLLM()
        result = llm.parse("Покажи все продукты")

        assert len(result.tool_calls) >= 1
        assert result.tool_calls[0].tool_name == "list_products"

    def test_parse_statistics(self):
        """Test parsing statistics query."""
        llm = MockLLM()
        result = llm.parse("Какая средняя цена?")

        assert len(result.tool_calls) >= 1
        assert result.tool_calls[0].tool_name == "get_statistics"

    def test_parse_get_product(self):
        """Test parsing get product query."""
        llm = MockLLM()
        result = llm.parse("Покажи товар ID 1")

        assert len(result.tool_calls) >= 1
        assert result.tool_calls[0].tool_name == "get_product"
        assert result.tool_calls[0].arguments.get("product_id") == 1

    def test_parse_discount(self):
        """Test parsing discount query."""
        llm = MockLLM()
        result = llm.parse("Скидка 15% на товар ID 1")

        tool_names = [tc.tool_name for tc in result.tool_calls]
        assert "get_product" in tool_names
        assert "calculate_discount" in tool_names


class TestCustomTools:
    """Tests for custom agent tools."""

    def test_calculate_discount(self):
        """Test discount calculation."""
        result = calculate_discount(price=1000, percent=15)

        assert result["original_price"] == 1000
        assert result["discount_percent"] == 15
        assert result["discount_amount"] == 150
        assert result["final_price"] == 850

    def test_calculate_discount_invalid_percent(self):
        """Test discount with invalid percentage."""
        result = calculate_discount(price=1000, percent=150)
        assert "error" in result

    def test_format_product_list_empty(self):
        """Test formatting empty product list."""
        result = format_product_list([])
        assert result == []

    def test_format_product_list(self):
        """Test formatting product list."""
        products = [
            {"id": 1, "name": "Тест", "price": 1000, "category": "Кат", "in_stock": True}
        ]
        result = format_product_list(products)

        assert len(result) == 1
        assert result[0]["name"] == "Тест"
        assert result[0]["id"] == 1
        assert result[0]["price"] == 1000


class TestProductAgent:
    """Tests for ProductAgent."""

    def test_agent_singleton(self):
        """Test that get_agent returns singleton."""
        agent1 = get_agent()
        agent2 = get_agent()
        assert agent1 is agent2

    def test_process_list_query(self):
        """Test processing list products query."""
        agent = ProductAgent()
        result = agent.process_query("Покажи все продукты")

        assert "response" in result
        assert "tools_used" in result
        assert "list_products" in result["tools_used"]
        assert "products" in result["response"]

    def test_process_statistics_query(self):
        """Test processing statistics query."""
        agent = ProductAgent()
        result = agent.process_query("Статистика по товарам")

        assert "response" in result
        assert "get_statistics" in result["tools_used"]
        assert "statistics" in result["response"]

    def test_process_category_query(self):
        """Test processing category filter query."""
        agent = ProductAgent()
        result = agent.process_query("Продукты категории Электроника")

        assert "response" in result
        assert "list_products" in result["tools_used"]
