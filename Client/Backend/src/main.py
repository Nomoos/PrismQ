"""FastAPI application entry point for PrismQ Web Client Backend."""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.logger import setup_logging
from .core.exceptions import WebClientException
from .core.resource_pool import initialize_resource_pool, cleanup_resource_pool
from .core.periodic_tasks import PeriodicTaskManager
from .core.maintenance import MAINTENANCE_TASKS
from .api import modules, runs, system, queue

# Configure event loop policy for Windows
# On Windows, the default SelectorEventLoop doesn't support subprocess operations
# We need to use ProactorEventLoop instead
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Set up logging
logger = setup_logging()

# Initialize periodic task manager (global instance)
periodic_task_manager = PeriodicTaskManager()


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
    # Register and start periodic maintenance tasks
    logger.info("Registering periodic maintenance tasks...")
    for task_config in MAINTENANCE_TASKS:
        try:
            periodic_task_manager.register_task(
                name=task_config["name"],
                interval=task_config["interval"],
                task_func=task_config["func"],
                **task_config.get("kwargs", {})
            )
            logger.info(f"  - {task_config['name']}: {task_config['description']}")
        except Exception as e:
            logger.error(f"Failed to register task {task_config['name']}: {e}")
    
    # Start all periodic tasks
    periodic_task_manager.start_all()
    logger.info("Periodic tasks started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PrismQ Web Client Backend...")
    
    # Cleanup global resource pool
    cleanup_resource_pool()
    logger.info("Resource pool cleaned up")
    # Stop all periodic tasks
    logger.info("Stopping periodic tasks...")
    await periodic_task_manager.stop_all(timeout=10.0)
    logger.info("Periodic tasks stopped")


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
app.include_router(queue.router, prefix="/api", tags=["Queue"])


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
