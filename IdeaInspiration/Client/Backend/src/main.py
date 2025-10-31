"""FastAPI application entry point for PrismQ Web Client Backend."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.logger import setup_logging
from .api import modules, runs, system

# Set up logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting PrismQ Web Client Backend...")
    logger.info(f"Version: {app.version}")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PrismQ Web Client Backend...")


# Create FastAPI application
app = FastAPI(
    title="PrismQ Web Client API",
    description="Control panel API for discovering, configuring, and running PrismQ modules",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(modules.router, prefix="/api", tags=["Modules"])
app.include_router(runs.router, prefix="/api", tags=["Runs"])
app.include_router(system.router, prefix="/api", tags=["System"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.
    
    Returns:
        dict: Welcome message and API information
    """
    return {
        "message": "PrismQ Web Client API",
        "version": app.version,
        "docs_url": "/docs",
        "health_url": "/api/health",
    }
