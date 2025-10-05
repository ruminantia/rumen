"""
Main application for Rumen LLM API and file monitoring system.
"""

import os
import secrets

import logging
import signal
import sys
from contextlib import asynccontextmanager


from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

from .config import get_settings, Settings
from .llm_client import LLMClientFactory, LLMClient
from .file_monitor import FileMonitor
from .output_handler import OutputHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Global instances
settings: Settings = None
llm_client: LLMClient = None
file_monitor: FileMonitor = None
output_handler: OutputHandler = None

# Security
security = HTTPBearer()
API_KEYS = set()


def initialize_application():
    """Initialize all application components."""
    global settings, llm_client, file_monitor, output_handler, API_KEYS

    # Generate a default API key if none exists in environment
    default_api_key = os.getenv("RUMEN_API_KEY")
    if default_api_key:
        API_KEYS.add(default_api_key)
    else:
        # Generate a secure random API key
        default_api_key = secrets.token_urlsafe(32)
        API_KEYS.add(default_api_key)
        print(f"⚠️  WARNING: No RUMEN_API_KEY set in environment")
        print(f"⚠️  Generated default API key: {default_api_key}")
        print(f"⚠️  Set RUMEN_API_KEY in your .env file to use this key")

    try:
        # Load settings
        settings = get_settings()
        logger.info("Configuration loaded successfully")

        # Initialize LLM client
        llm_client = LLMClientFactory.create_client(settings.llm)
        logger.info(f"LLM client initialized for provider: {settings.llm.provider}")

        # Initialize output handler
        output_handler = OutputHandler(settings.output)
        logger.info(
            f"Output handler initialized for: {settings.output.output_directory}"
        )

        # Initialize file monitor
        file_monitor = FileMonitor(process_file_content, settings)
        logger.info("File monitor initialized")

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise


async def process_file_content(content: str, file_path: str, folder_config) -> bool:
    """
    Process file content using LLM and save results.

    Args:
        content: File content to process
        file_path: Path to the original file
        folder_config: Folder configuration

    Returns:
        True if processing was successful
    """
    try:
        logger.info(
            f"Processing content from {file_path} for folder {folder_config.name}"
        )

        # Process content with LLM
        processed_content = llm_client.process_content(
            content=content,
            system_prompt=folder_config.system_prompt,
            user_prompt_template=folder_config.user_prompt_template,
        )

        # Save the result
        output_handler.save_result(
            content=processed_content,
            original_filename=file_path,
            folder_name=folder_config.name,
            output_format=folder_config.output_format,
            metadata={
                "original_file": file_path,
                "folder": folder_config.name,
                "model": folder_config.model,
                "provider": folder_config.provider,
            },
        )

        logger.info(f"Successfully processed content from {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error processing content from {file_path}: {e}")

        # Save error result
        output_handler.save_error_result(
            error_message=str(e),
            original_filename=file_path,
            folder_name=folder_config.name,
            error_details={
                "folder_config": folder_config.name,
                "file_path": file_path,
            },
        )
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting Rumen application...")
    initialize_application()

    # Start file monitoring in background
    if file_monitor:
        file_monitor.start()
        # Process any existing files
        file_monitor.process_existing_files()

    yield

    # Shutdown
    logger.info("Shutting down Rumen application...")
    if file_monitor:
        file_monitor.stop()


# Authentication dependency
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key from Authorization header."""
    if credentials.credentials not in API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


# Create FastAPI application
app = FastAPI(
    title="Rumen LLM API",
    description="Containerized API for interacting with LLMs via HTTP API and file monitoring",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Rumen LLM API",
        "version": "1.0.0",
        "status": "running",
        "llm_provider": settings.llm.provider if settings else "unknown",
        "authentication_required": True,
    }


@app.get("/health")
async def health_check(_: str = Depends(verify_api_key)):
    """Health check endpoint."""
    try:
        # Check LLM provider health
        llm_healthy = llm_client.health_check() if llm_client else False

        # Check file monitor status
        file_monitor_healthy = file_monitor.running if file_monitor else False

        status = "healthy" if llm_healthy and file_monitor_healthy else "degraded"

        return {
            "status": status,
            "llm_provider": settings.llm.provider if settings else "unknown",
            "llm_healthy": llm_healthy,
            "file_monitor_running": file_monitor_healthy,
            "output_directory": str(settings.output.output_directory)
            if settings
            else "unknown",
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/process")
async def process_text(
    text: str,
    system_prompt: str = "You are a helpful assistant.",
    user_prompt: str = "Process the following text: {content}",
    temperature: float = None,
    max_tokens: int = None,
    output_format: str = "markdown",
    background_tasks: BackgroundTasks = None,
    _: str = Depends(verify_api_key),
):
    """
    Process text using the LLM.

    Args:
        text: Text to process
        system_prompt: System prompt for the LLM
        user_prompt: User prompt template with {content} placeholder
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate
        output_format: Output format (markdown, json)
    """
    try:
        # Process the text
        processed_content = llm_client.process_content(
            content=text,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt,
        )

        # Save the result
        file_path = output_handler.save_result(
            content=processed_content,
            output_format=output_format,
            metadata={
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "model": settings.llm.model,
                "provider": settings.llm.provider,
            },
        )

        return {
            "status": "success",
            "processed_content": processed_content,
            "output_file": str(file_path),
            "content_length": len(processed_content),
        }

    except Exception as e:
        logger.error(f"Error processing text: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")


@app.get("/folders")
async def list_monitored_folders(_: str = Depends(verify_api_key)):
    """List all monitored folders and their status."""
    if not settings or not file_monitor:
        raise HTTPException(status_code=503, detail="Service not initialized")

    folders_info = []
    for folder_name, folder_config in settings.folders.items():
        folder_info = {
            "name": folder_name,
            "enabled": folder_config.enabled,
            "folder_path": str(folder_config.folder_path),
            "system_prompt": folder_config.system_prompt[:100] + "..."
            if len(folder_config.system_prompt) > 100
            else folder_config.system_prompt,
            "model": folder_config.model,
            "provider": folder_config.provider,
        }
        folders_info.append(folder_info)

    return {
        "monitored_folders": folders_info,
        "total_folders": len(folders_info),
        "enabled_folders": len([f for f in folders_info if f["enabled"]]),
    }


@app.get("/results")
async def list_results(limit: int = 10, _: str = Depends(verify_api_key)):
    """List recent processing results."""
    try:
        result_files = output_handler.list_results(limit=limit)
        results = []

        for file_path in result_files:
            results.append(
                {
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                }
            )

        return {
            "results": results,
            "total_results": output_handler.get_result_count(),
            "limit": limit,
        }

    except Exception as e:
        logger.error(f"Error listing results: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing results: {str(e)}")


@app.post("/file-monitor/start")
async def start_file_monitor(_: str = Depends(verify_api_key)):
    """Start the file monitor."""
    try:
        if file_monitor:
            file_monitor.start()
            return {"status": "started", "message": "File monitor started"}
        else:
            raise HTTPException(status_code=503, detail="File monitor not initialized")
    except Exception as e:
        logger.error(f"Error starting file monitor: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error starting file monitor: {str(e)}"
        )


@app.post("/file-monitor/stop")
async def stop_file_monitor(_: str = Depends(verify_api_key)):
    """Stop the file monitor."""
    try:
        if file_monitor:
            file_monitor.stop()
            return {"status": "stopped", "message": "File monitor stopped"}
        else:
            raise HTTPException(status_code=503, detail="File monitor not initialized")
    except Exception as e:
        logger.error(f"Error stopping file monitor: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error stopping file monitor: {str(e)}"
        )


@app.get("/file-monitor/status")
async def get_file_monitor_status(_: str = Depends(verify_api_key)):
    """Get file monitor status."""
    if file_monitor:
        return {
            "running": file_monitor.running,
            "monitored_folders": len(file_monitor.event_handlers),
        }
    else:
        raise HTTPException(status_code=503, detail="File monitor not initialized")


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down...")
    if file_monitor:
        file_monitor.stop()
    sys.exit(0)


def main():
    """Main entry point for the application."""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start the API server
        uvicorn.run(
            "src.main:app",
            host=settings.api.host if settings else "0.0.0.0",
            port=settings.api.port if settings else 8000,
            workers=settings.api.workers if settings else 1,
            log_level="info",
            reload=False,  # Disable reload in production
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
