"""FastMCP server for product management."""

import json
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("products-server")

# Load initial data
DATA_FILE = Path(__file__).parent / "products.json"


def load_products() -> list[dict]:
    """Load products from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_products(products: list[dict]) -> None:
    """Save products to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


# In-memory storage
_products: list[dict] = load_products()


@mcp.tool()
def list_products(category: Optional[str] = None) -> list[dict]:
    """List all products, optionally filtered by category.

    Args:
        category: Optional category name to filter products

    Returns:
        List of products matching the criteria
    """
    if category:
        return [p for p in _products if p["category"].lower() == category.lower()]
    return _products


@mcp.tool()
def get_product(product_id: int) -> dict:
    """Get a product by its ID.

    Args:
        product_id: The unique identifier of the product

    Returns:
        Product data or error message
    """
    for product in _products:
        if product["id"] == product_id:
            return product
    return {"error": f"Product with ID {product_id} not found"}


@mcp.tool()
def add_product(name: str, price: float, category: str, in_stock: bool = True) -> dict:
    """Add a new product.

    Args:
        name: Product name
        price: Product price
        category: Product category
        in_stock: Whether the product is in stock

    Returns:
        The newly created product
    """
    # Generate new ID
    new_id = max((p["id"] for p in _products), default=0) + 1

    new_product = {
        "id": new_id,
        "name": name,
        "price": price,
        "category": category,
        "in_stock": in_stock
    }

    _products.append(new_product)
    save_products(_products)

    return new_product


@mcp.tool()
def get_statistics() -> dict:
    """Get product statistics.

    Returns:
        Statistics including total count, average price, and category breakdown
    """
    if not _products:
        return {
            "total_count": 0,
            "average_price": 0,
            "in_stock_count": 0,
            "categories": {}
        }

    total_count = len(_products)
    average_price = sum(p["price"] for p in _products) / total_count
    in_stock_count = sum(1 for p in _products if p["in_stock"])

    # Category breakdown
    categories: dict[str, int] = {}
    for product in _products:
        cat = product["category"]
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_count": total_count,
        "average_price": round(average_price, 2),
        "in_stock_count": in_stock_count,
        "categories": categories
    }


def reset_products() -> None:
    """Reset products to initial data (for testing)."""
    global _products
    _products = load_products()


def get_products_storage() -> list[dict]:
    """Get direct access to products storage (for testing)."""
    return _products


if __name__ == "__main__":
    mcp.run()
