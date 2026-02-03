"""Pydantic schemas for API."""

from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request schema for agent query."""
    query: str = Field(
        ...,
        description="User query in natural language",
        min_length=1,
        max_length=1000,
        examples=["Покажи все продукты", "Статистика по товарам"]
    )


class QueryResponse(BaseModel):
    """Response schema for agent query."""
    response: Any = Field(
        ...,
        description="Structured response data (products, statistics, etc.)"
    )
    tools_used: list[str] = Field(
        default_factory=list,
        description="List of tools that were used to process the query"
    )


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str = Field(default="ok")
    version: str = Field(default="1.0.0")


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    error: str = Field(..., description="Error message")
    detail: str | None = Field(default=None, description="Additional error details")
