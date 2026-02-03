"""Custom tools for the agent."""

from typing import Union


def calculate_discount(price: float, percent: float) -> dict:
    """Calculate discounted price.

    Args:
        price: Original price
        percent: Discount percentage (0-100)

    Returns:
        Dictionary with original price, discount amount, and final price
    """
    if percent < 0 or percent > 100:
        return {"error": "Discount percentage must be between 0 and 100"}

    discount_amount = price * (percent / 100)
    final_price = price - discount_amount

    return {
        "original_price": price,
        "discount_percent": percent,
        "discount_amount": round(discount_amount, 2),
        "final_price": round(final_price, 2)
    }


def format_price(amount: Union[int, float]) -> str:
    """Format price as string."""
    return f"{amount}"


def format_product_list(products: list[dict]) -> list[dict]:
    """Format a list of products for display.

    Args:
        products: List of product dictionaries

    Returns:
        List of formatted product dictionaries
    """
    if not products:
        return []

    return [
        {
            "id": p["id"],
            "name": p["name"],
            "price": p["price"],
            "category": p["category"],
            "in_stock": p.get("in_stock", False)
        }
        for p in products
    ]


def format_statistics(stats: dict) -> dict:
    """Format statistics for display.

    Args:
        stats: Statistics dictionary

    Returns:
        Formatted statistics dictionary
    """
    return stats
