
"""
Main entry point for the Food Delivery System backend.

This module initializes the FastAPI application, configures
CORS for the React frontend, and registers the API routers.

Run the backend from the backend/ directory using:

    python -m uvicorn app.main:app --reload

FastAPI automatically provides interactive API documentation
at /docs and an OpenAPI specification at /openapi.json.
"""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.menu import router as menu_router
from app.api.routes.restaurants import router as restaurant_router


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Food Delivery System API",
    description=(
        "REST API for restaurant discovery and menu management. "
        "Supports restaurant browsing, filtering, creation, "
        "and editing, along with menu-item management. "
        "Authentication is not implemented for Milestone 1; "
        "restaurant creation and editing use a demonstration owner."
    ),
    version="1.0.0",
)


# ============================================================
# Cross-Origin Resource Sharing (CORS)
# ============================================================

# CORS controls which browser-based applications may make
# cross-origin requests to this backend.
#
# During local development:
#     React/Vite frontend: http://localhost:5173
#     FastAPI backend:     http://localhost:8000
#
# Since these use different ports, the browser treats them
# as different origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API Router Registration
# ============================================================

# Each router defines endpoints for a specific responsibility.
# include_router() adds those endpoints to the application.
app.include_router(health_router)
app.include_router(restaurant_router)
app.include_router(menu_router)
