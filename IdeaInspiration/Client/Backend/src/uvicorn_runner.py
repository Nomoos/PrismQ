"""Uvicorn runner with Windows subprocess support.

This module ensures that the Windows ProactorEventLoop is set before
uvicorn starts, which is required for asyncio subprocess operations on Windows.

Primary Platform: Windows 10/11 with NVIDIA RTX 5090
"""

import asyncio
import sys
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Run uvicorn with proper Windows event loop policy.
    
    On Windows, we need to set the ProactorEventLoopPolicy before
    uvicorn creates its event loop. This is required for subprocess
    operations using asyncio.create_subprocess_exec.
    
    This is the REQUIRED way to run the PrismQ backend on Windows.
    """
    logger.info(f"Starting PrismQ Backend on {sys.platform}")
    logger.info(f"Python version: {sys.version}")
    
    # Set Windows event loop policy BEFORE importing uvicorn
    # This ensures the policy is applied before any event loop is created
    if sys.platform == 'win32':
        logger.info("Detected Windows platform - setting ProactorEventLoopPolicy")
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Verify the policy was set correctly
        policy = asyncio.get_event_loop_policy()
        logger.info(f"Event loop policy set to: {type(policy).__name__}")
        
        if type(policy).__name__ != "WindowsProactorEventLoopPolicy":
            logger.error("Failed to set Windows event loop policy!")
            logger.error("Module execution will fail with NotImplementedError")
            sys.exit(1)
    else:
        logger.info(f"Non-Windows platform detected ({sys.platform})")
        logger.info("Using default event loop policy")
    
    # Now import and run uvicorn
    try:
        import uvicorn
    except ImportError:
        logger.error("uvicorn is not installed!")
        logger.error("Install it with: pip install uvicorn[standard]")
        sys.exit(1)
    
    logger.info("Starting uvicorn server...")
    logger.info("Server will be available at: http://127.0.0.1:8000")
    logger.info("API documentation at: http://127.0.0.1:8000/docs")
    logger.info("Press CTRL+C to stop the server")
    
    # Run the FastAPI application
    try:
        uvicorn.run(
            "src.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
