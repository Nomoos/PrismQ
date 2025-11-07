"""FastAPI application entry point for PrismQ Web Client Backend."""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.logger import setup_logging
from .core.exceptions import WebClientException
from .core.resource_pool import initialize_resource_pool, cleanup_resource_pool
from .api import runs, system, queue

# Import modular endpoints (new pattern - modules are self-contained at Backend/ level)
# Add Backend directory to path to import modules
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
from API.endpoints import task_types_router, task_list_router
from Modules.endpoints import router as modules_router

# Configure event loop policy for Windows
# On Windows, the default SelectorEventLoop doesn't support subprocess operations
# We need to use ProactorEventLoop instead
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Set up logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting PrismQ Web Client Backend...")
    logger.info(f"Version: {app.version}")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    # Validate Windows event loop policy
    if sys.platform == 'win32':
        policy = asyncio.get_event_loop_policy()
        if not isinstance(policy, asyncio.WindowsProactorEventLoopPolicy):
            logger.error("=" * 70)
            logger.error("SERVER STARTED WITH WRONG EVENT LOOP POLICY!")
            logger.error("Module execution will fail with NotImplementedError")
            logger.error("=" * 70)
            logger.error("Please restart using: python -m src.uvicorn_runner")
            logger.error("=" * 70)
    
    # Initialize global resource pool
    initialize_resource_pool(max_workers=settings.MAX_CONCURRENT_RUNS)
    logger.info("Resource pool initialized")
    
    # Note: Periodic maintenance tasks are now disabled in favor of on-demand execution
    # All background operations are triggered via API endpoints based on UI requests
    logger.info("Background operations configured for on-demand execution only")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PrismQ Web Client Backend...")
    
    # Cleanup global resource pool
    cleanup_resource_pool()
    logger.info("Resource pool cleaned up")


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
app.include_router(modules_router, prefix="/api", tags=["Modules"])
app.include_router(runs.router, prefix="/api", tags=["Runs"])
app.include_router(system.router, prefix="/api", tags=["System"])
app.include_router(queue.router, prefix="/api", tags=["Queue"])

# Include new API module routers
app.include_router(task_types_router, prefix="/api", tags=["TaskTypes"])
app.include_router(task_list_router, prefix="/api", tags=["TaskList"])


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
