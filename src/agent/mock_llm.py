"""Mock LLM for parsing user requests using regex and keyword matching."""

import re
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ToolCall:
    """Represents a parsed tool call."""
    tool_name: str
    arguments: dict[str, Any]


@dataclass
class ParseResult:
    """Result of parsing a user query."""
    tool_calls: list[ToolCall]
    response_template: str


class MockLLM:
    """Mock LLM that parses requests using regex patterns."""

    def __init__(self):
        self.patterns = [
            # Add product - MUST be first to catch "добавь" before other patterns
            (
                r"(добав|создай)\w*\s*.*(продукт|товар)",
                self._parse_add_product
            ),
            # Statistics patterns
            (
                r"(статистик|средн\w* цен|сколько товаров|сколько продуктов)",
                self._parse_statistics
            ),
            # Calculate discount - flexible pattern
            (
                r"скидк\w*\s*(\d+)\s*%.*?(?:id|ID|Id)\s*(\d+)",
                self._parse_discount
            ),
            # Get product by ID - specific patterns with ID keyword
            (
                r"(покажи|найди|информаци\w*|дай)\s*(о\s*)?(продукт|товар)\w*\s*(id|ID|Id)\s*[=:]?\s*(\d+)",
                self._parse_get_product_with_id
            ),
            # Get product by ID - "товар ID N" pattern
            (
                r"(продукт|товар)\s+(id|ID|Id)\s*[=:]?\s*(\d+)",
                self._parse_get_product_simple
            ),
            # List products with category
            (
                r"(покажи|список|все)\s*(продукт|товар)\w*\s*(категории|из категории|в категории)\s+[\"']?(\w+)[\"']?",
                self._parse_list_with_category
            ),
            # List products by category (alternative)
            (
                r"(категори\w*)\s+[\"']?(\w+)[\"']?",
                self._parse_category
            ),
            # General list products (fallback)
            (
                r"(покажи|список|все|вывести)\s*(продукт|товар)",
                self._parse_list_all
            ),
        ]

    def parse(self, query: str) -> ParseResult:
        """Parse user query and determine which tools to call.

        Args:
            query: User query string

        Returns:
            ParseResult with tool calls and response template
        """
        query_lower = query.lower()

        for pattern, parser_func in self.patterns:
            match = re.search(pattern, query_lower)
            if match:
                return parser_func(match, query)

        # Default: list all products
        return ParseResult(
            tool_calls=[ToolCall("list_products", {})],
            response_template="Вот список продуктов:\n{result}"
        )

    def _parse_statistics(self, match: re.Match, query: str) -> ParseResult:
        return ParseResult(
            tool_calls=[ToolCall("get_statistics", {})],
            response_template="Статистика по продуктам:\n{result}"
        )

    def _parse_list_with_category(self, match: re.Match, query: str) -> ParseResult:
        groups = match.groups()
        category = groups[3] if len(groups) > 3 and groups[3] else None

        if category:
            return ParseResult(
                tool_calls=[ToolCall("list_products", {"category": category})],
                response_template=f"Продукты в категории '{category}':\n{{result}}"
            )

        return ParseResult(
            tool_calls=[ToolCall("list_products", {})],
            response_template="Список всех продуктов:\n{result}"
        )

    def _parse_category(self, match: re.Match, query: str) -> ParseResult:
        category = match.group(2)
        return ParseResult(
            tool_calls=[ToolCall("list_products", {"category": category})],
            response_template=f"Продукты в категории '{category}':\n{{result}}"
        )

    def _parse_get_product_with_id(self, match: re.Match, query: str) -> ParseResult:
        product_id = int(match.group(5))
        return ParseResult(
            tool_calls=[ToolCall("get_product", {"product_id": product_id})],
            response_template="Информация о продукте:\n{result}"
        )

    def _parse_get_product_simple(self, match: re.Match, query: str) -> ParseResult:
        product_id = int(match.group(3))
        return ParseResult(
            tool_calls=[ToolCall("get_product", {"product_id": product_id})],
            response_template="Информация о продукте:\n{result}"
        )

    def _parse_add_product(self, match: re.Match, query: str) -> ParseResult:
        # Extract product details from query
        # Format: "Добавь продукт: Мышка, цена 1500, категория Электроника"

        name = "Новый продукт"
        price = 0.0
        category = "Без категории"

        # Try to extract name after "продукт:" or "товар:"
        name_match = re.search(r'(?:продукт|товар)[:\s]+([^,]+)', query, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip()

        # Extract price
        price_match = re.search(r'цена\s*[=:]*\s*(\d+)', query, re.IGNORECASE)
        if price_match:
            price = float(price_match.group(1))

        # Extract category
        cat_match = re.search(r'категория\s*[=:]*\s*(\w+)', query, re.IGNORECASE)
        if cat_match:
            category = cat_match.group(1)

        in_stock = "нет в наличии" not in query.lower()

        return ParseResult(
            tool_calls=[ToolCall("add_product", {
                "name": name,
                "price": price,
                "category": category,
                "in_stock": in_stock
            })],
            response_template="Продукт добавлен:\n{result}"
        )

    def _parse_discount(self, match: re.Match, query: str) -> ParseResult:
        percent = float(match.group(1))
        product_id = int(match.group(2))

        return ParseResult(
            tool_calls=[
                ToolCall("get_product", {"product_id": product_id}),
                ToolCall("calculate_discount", {"percent": percent})
            ],
            response_template="Расчёт скидки:\n{result}"
        )

    def _parse_list_all(self, match: re.Match, query: str) -> ParseResult:
        return ParseResult(
            tool_calls=[ToolCall("list_products", {})],
            response_template="Список всех продуктов:\n{result}"
        )

    def _extract_quoted(self, text: str, prefix_pattern: str) -> Optional[str]:
        """Extract quoted value after a prefix pattern."""
        pattern = rf'{prefix_pattern}\s*[=:]*\s*["\']([^"\']+)["\']'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _extract_number(self, text: str, prefix_pattern: str) -> Optional[float]:
        """Extract number value after a prefix pattern."""
        pattern = rf'{prefix_pattern}\s*[=:]*\s*(\d+(?:\.\d+)?)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None

    def format_response(self, template: str, result: str) -> str:
        """Format the response using template and result.

        Args:
            template: Response template with {result} placeholder
            result: Tool execution result

        Returns:
            Formatted response string
        """
        return template.format(result=result)
