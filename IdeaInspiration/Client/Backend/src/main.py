"""FastAPI application entry point for PrismQ Web Client Backend."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.logger import setup_logging
from .core.exceptions import WebClientException
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


# Exception handlers
@app.exception_handler(WebClientException)
async def web_client_exception_handler(request: Request, exc: WebClientException):
    """
    Handle custom WebClient exceptions.
    
    Args:
        request: HTTP request
        exc: WebClient exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"WebClient error: {exc.message}", exc_info=True)
    
    # Determine appropriate HTTP status code based on exception type
    from .core.exceptions import (
        ModuleNotFoundException,
        RunNotFoundException,
        ResourceLimitException,
        ValidationException,
    )
    
    if isinstance(exc, (ModuleNotFoundException, RunNotFoundException)):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ResourceLimitException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, ValidationException):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    else:
        status_code = status.HTTP_400_BAD_REQUEST
    
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.
    
    Args:
        request: HTTP request
        exc: Exception
        
    Returns:
        JSON response with generic error message
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
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
