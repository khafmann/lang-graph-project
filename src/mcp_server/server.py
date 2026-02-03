"""FastMCP server for product management with SQLite persistence."""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from . import database as db

# Initialize FastMCP server
mcp = FastMCP("products-server")


@mcp.tool()
def list_products(category: Optional[str] = None) -> list[dict]:
    """List all products, optionally filtered by category.

    Args:
        category: Optional category name to filter products

    Returns:
        List of products matching the criteria
    """
    return db.get_all_products(category)


@mcp.tool()
def get_product(product_id: int) -> dict:
    """Get a product by its ID.

    Args:
        product_id: The unique identifier of the product

    Returns:
        Product data or error message
    """
    product = db.get_product_by_id(product_id)
    if product:
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
    return db.create_product(name, price, category, in_stock)


@mcp.tool()
def update_product(product_id: int, name: Optional[str] = None,
                   price: Optional[float] = None, category: Optional[str] = None,
                   in_stock: Optional[bool] = None) -> dict:
    """Update an existing product.

    Args:
        product_id: The unique identifier of the product
        name: New product name (optional)
        price: New product price (optional)
        category: New product category (optional)
        in_stock: New stock status (optional)

    Returns:
        Updated product data or error message
    """
    updates = {}
    if name is not None:
        updates["name"] = name
    if price is not None:
        updates["price"] = price
    if category is not None:
        updates["category"] = category
    if in_stock is not None:
        updates["in_stock"] = in_stock

    product = db.update_product(product_id, **updates)
    if product:
        return product
    return {"error": f"Product with ID {product_id} not found"}


@mcp.tool()
def delete_product(product_id: int) -> dict:
    """Delete a product by its ID.

    Args:
        product_id: The unique identifier of the product

    Returns:
        Success or error message
    """
    if db.delete_product(product_id):
        return {"success": True, "message": f"Product {product_id} deleted"}
    return {"error": f"Product with ID {product_id} not found"}


@mcp.tool()
def get_statistics() -> dict:
    """Get product statistics.

    Returns:
        Statistics including total count, average price, and category breakdown
    """
    return db.get_statistics()


# Testing helpers
def reset_products() -> None:
    """Reset products to initial data (for testing)."""
    db.reset_db()


def get_products_storage() -> list[dict]:
    """Get all products (for testing)."""
    return db.get_all_products()


if __name__ == "__main__":
    mcp.run()
