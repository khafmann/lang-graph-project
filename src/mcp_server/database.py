"""SQLite database module for product management."""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

# Database file path
DB_PATH = Path(__file__).parent / "products.db"

# Initial seed data
INITIAL_PRODUCTS = [
    (1, "Ноутбук", 50000, "Электроника", True),
    (2, "Смартфон", 30000, "Электроника", True),
    (3, "Стол", 15000, "Мебель", False),
]


@contextmanager
def get_connection():
    """Get database connection with context manager."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database with schema and seed data."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL,
                in_stock BOOLEAN NOT NULL DEFAULT 1
            )
        """)

        # Check if table is empty, seed initial data
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO products (id, name, price, category, in_stock) VALUES (?, ?, ?, ?, ?)",
                INITIAL_PRODUCTS
            )

        conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert sqlite3.Row to dictionary."""
    return {
        "id": row["id"],
        "name": row["name"],
        "price": row["price"],
        "category": row["category"],
        "in_stock": bool(row["in_stock"])
    }


# CRUD Operations

def get_all_products(category: Optional[str] = None) -> list[dict]:
    """Get all products, optionally filtered by category.

    Args:
        category: Optional category name to filter products

    Returns:
        List of products as dictionaries
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        if category:
            # Use case-insensitive comparison for Cyrillic support
            cursor.execute("SELECT * FROM products")
            all_products = cursor.fetchall()
            return [
                row_to_dict(row) for row in all_products
                if row["category"].lower() == category.lower()
            ]
        else:
            cursor.execute("SELECT * FROM products")
            return [row_to_dict(row) for row in cursor.fetchall()]


def get_product_by_id(product_id: int) -> Optional[dict]:
    """Get a product by ID.

    Args:
        product_id: The product ID

    Returns:
        Product dict or None if not found
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()

        if row:
            return row_to_dict(row)
        return None


def create_product(name: str, price: float, category: str, in_stock: bool = True) -> dict:
    """Create a new product.

    Args:
        name: Product name
        price: Product price
        category: Product category
        in_stock: Whether product is in stock

    Returns:
        The created product with its ID
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, category, in_stock) VALUES (?, ?, ?, ?)",
            (name, price, category, in_stock)
        )
        conn.commit()

        return {
            "id": cursor.lastrowid,
            "name": name,
            "price": price,
            "category": category,
            "in_stock": in_stock
        }


def update_product(product_id: int, **kwargs) -> Optional[dict]:
    """Update a product by ID.

    Args:
        product_id: The product ID
        **kwargs: Fields to update (name, price, category, in_stock)

    Returns:
        Updated product or None if not found
    """
    allowed_fields = {"name", "price", "category", "in_stock"}
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not updates:
        return get_product_by_id(product_id)

    with get_connection() as conn:
        cursor = conn.cursor()

        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [product_id]

        cursor.execute(
            f"UPDATE products SET {set_clause} WHERE id = ?",
            values
        )
        conn.commit()

        if cursor.rowcount == 0:
            return None

        return get_product_by_id(product_id)


def delete_product(product_id: int) -> bool:
    """Delete a product by ID.

    Args:
        product_id: The product ID

    Returns:
        True if deleted, False if not found
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()

        return cursor.rowcount > 0


def get_statistics() -> dict:
    """Get product statistics.

    Returns:
        Statistics dict with counts and averages
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Total count and average price
        cursor.execute("""
            SELECT
                COUNT(*) as total_count,
                COALESCE(AVG(price), 0) as average_price,
                SUM(CASE WHEN in_stock THEN 1 ELSE 0 END) as in_stock_count
            FROM products
        """)
        row = cursor.fetchone()

        # Category breakdown
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM products
            GROUP BY category
        """)
        categories = {r["category"]: r["count"] for r in cursor.fetchall()}

        return {
            "total_count": row["total_count"],
            "average_price": round(row["average_price"], 2),
            "in_stock_count": row["in_stock_count"] or 0,
            "categories": categories
        }


def reset_db() -> None:
    """Reset database to initial state (for testing)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products")
        cursor.executemany(
            "INSERT INTO products (id, name, price, category, in_stock) VALUES (?, ?, ?, ?, ?)",
            INITIAL_PRODUCTS
        )
        # Reset autoincrement
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='products'")
        cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('products', 3)")
        conn.commit()


# Initialize database on module import
init_db()
