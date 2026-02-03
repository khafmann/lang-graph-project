"""FastAPI application for the product agent."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import ErrorResponse, HealthResponse, QueryRequest, QueryResponse
from ..agent.graph import get_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup: initialize agent
    get_agent()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Product Agent API",
    description="AI Agent with MCP integration for product management",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API health status."""
    return HealthResponse()


@app.post(
    "/api/v1/agent/query",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    tags=["Agent"],
)
async def process_query(request: QueryRequest):
    """Process a natural language query about products.

    Examples:
    - "Покажи все продукты"
    - "Продукты в категории Электроника"
    - "Статистика по товарам"
    - "Скидка 10% на товар ID 1"
    """
    try:
        agent = get_agent()
        result = agent.process_query(request.query)
        return QueryResponse(
            response=result["response"],
            tools_used=result["tools_used"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Product Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
