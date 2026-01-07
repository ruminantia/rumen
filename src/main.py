"""
Main application for Rumen LLM API and file monitoring system.
"""

import os
import secrets
from pathlib import Path
from typing import Optional

import logging
import signal
import sys
from contextlib import asynccontextmanager


from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

from .config import get_settings, Settings, LLMSettings
from .llm_client import LLMClientFactory, LLMClient
from .file_monitor import FileMonitor
from .output_handler import OutputHandler
from .web_viewer import create_web_viewer

# Configure logging
log_dir = Path("/app/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / "rumen.log")
    ],
)
logger = logging.getLogger(__name__)

# Global instances
settings: Settings = None
llm_client: LLMClient = None
file_monitor: FileMonitor = None
output_handler: OutputHandler = None
monitoring_thread = None

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


def reload_application_settings():
    """Reload application settings from config file."""
    global settings, llm_client, file_monitor, output_handler, monitoring_thread

    try:
        logger.info("Reloading application settings...")

        # Stop the old file monitor if it's running
        old_monitor_running = file_monitor and file_monitor.running
        if old_monitor_running:
            logger.info("Stopping old file monitor...")
            file_monitor.stop()

        # Reload settings from disk (force reload to bypass cache)
        new_settings = get_settings(force_reload=True)
        settings = new_settings

        # Reinitialize LLM client
        llm_client = LLMClientFactory.create_client(settings.llm)
        logger.info(f"LLM client reinitialized for provider: {settings.llm.provider}")

        # Reinitialize output handler
        output_handler = OutputHandler(settings.output)
        logger.info(f"Output handler reinitialized for: {settings.output.output_directory}")

        # Reinitialize file monitor
        file_monitor = FileMonitor(process_file_content, settings)
        logger.info("File monitor reinitialized")

        # Start the new file monitor
        file_monitor.start()
        logger.info("File monitor started")

        # Process any existing files
        file_monitor.process_existing_files()

        # Create a new monitoring thread
        import threading
        monitoring_thread = threading.Thread(
            target=file_monitor.run_monitoring_loop, daemon=True
        )
        monitoring_thread.start()
        logger.info("File monitoring thread started")

        logger.info("Application settings reloaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to reload application settings: {e}")
        return False


async def process_file_content(content: str, file_path: str, folder_config) -> tuple[bool, bool, str]:
    """
    Process file content using LLM and save results.

    Args:
        content: File content to process
        file_path: Path to the original file
        folder_config: Folder configuration

    Returns:
        Tuple of (success: bool, rejected: bool, rejection_reason: str)
    """
    # Store original input content for potential appending
    original_input_content = content

    try:
        logger.info(
            f"Processing content from {file_path} for folder {folder_config.name}"
        )

        # Create folder-specific LLM settings
        folder_llm_settings = LLMSettings(
            provider=folder_config.provider,
            model=folder_config.model,
            base_url=settings.llm.base_url,  # Will be overridden by provider-specific config
            api_key=settings.llm.api_key,
            temperature=folder_config.temperature,
            max_tokens=folder_config.max_tokens,
            top_p=settings.llm.top_p,
            retry_attempts=settings.llm.retry_attempts,
            retry_delay=settings.llm.retry_delay,
        )

        # Get provider-specific base_url
        provider_name = folder_config.provider
        if provider_name in settings.provider_base_urls:
            folder_llm_settings.base_url = settings.provider_base_urls[provider_name]

        # Create folder-specific LLM client
        folder_llm_client = LLMClient(folder_llm_settings)

        logger.info(f"Using provider: {folder_config.provider}, model: {folder_config.model}")

        # Load prompts (from files or inline)
        system_prompt = folder_config.load_system_prompt()
        user_prompt_template = folder_config.load_user_prompt_template()

        logger.info(f"Loaded system prompt ({len(system_prompt)} chars) and user template ({len(user_prompt_template)} chars)")

        # Process content with LLM
        processed_content = folder_llm_client.process_content(
            content=content,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
        )

        # Check for rejection trigger words
        rejected = False
        rejection_reason = ""
        if folder_config.rejection_trigger_words:
            processed_content_lower = processed_content.lower()
            for trigger_word in folder_config.rejection_trigger_words:
                if trigger_word.lower() in processed_content_lower:
                    logger.warning(f"Content from {file_path} rejected due to trigger word: {trigger_word}")
                    rejected = True
                    rejection_reason = f"Trigger word found: {trigger_word}"
                    break

        # Save the result (whether accepted or rejected)
        output_handler.save_result(
            content=processed_content,
            original_filename=file_path,
            folder_name=folder_config.name,
            output_format=folder_config.output_format,
            metadata={
                "original_file": str(file_path),
                "folder": folder_config.name,
                "model": folder_config.model,
                "provider": folder_config.provider,
            },
            folder_config=folder_config,
            skip_metadata=(folder_config.name == "digest"),  # Skip metadata for publication-ready digest output
            rejected=rejected,
            original_input_content=original_input_content,
            append_input=folder_config.append_input_to_output,
        )

        if rejected:
            logger.info(f"Saved rejected content from {file_path}: {rejection_reason}")
            return (True, True, rejection_reason)

        logger.info(f"Successfully processed content from {file_path}")
        return (True, False, "")

    except Exception as e:
        logger.error(f"Error processing content from {file_path}: {e}")

        # Save error result
        output_handler.save_error_result(
            error_message=str(e),
            original_filename=str(file_path),
            folder_name=folder_config.name,
            error_details={
                "folder_config": folder_config.name,
                "file_path": str(file_path),
            },
            folder_config=folder_config,
        )
        return (False, False, str(e))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global monitoring_thread

    # Startup
    logger.info("Starting Rumen application...")
    initialize_application()

    # Start file monitoring in background
    if file_monitor:
        file_monitor.start()

        # Start the monitoring loop in a background thread
        import threading

        monitoring_thread = threading.Thread(
            target=file_monitor.run_monitoring_loop, daemon=True
        )
        monitoring_thread.start()

        # Process existing files in background if enabled
        if settings.file_monitor.process_existing_on_startup:
            processing_thread = threading.Thread(
                target=file_monitor.process_existing_files, daemon=True
            )
            processing_thread.start()
            logger.info("File processing started in background")
        else:
            logger.info("Processing existing files on startup is disabled")

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


# Generate web viewer before starting the app
try:
    logger.info("Generating web viewer...")
    create_web_viewer("/app/viewer")
    logger.info("Web viewer created successfully")
except Exception as e:
    logger.warning(f"Failed to generate web viewer: {e}")


# Cache control middleware to prevent caching of API responses and viewer files
class CacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Add cache-control headers to API responses and viewer files
        if request.url.path.startswith('/api/') or request.url.path.startswith('/viewer/'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response


# Create FastAPI application
app = FastAPI(
    title="Rumen LLM API",
    description="Containerized API for interacting with LLMs via HTTP API and file monitoring",
    version="1.0.0",
    lifespan=lifespan,
)

# Add cache control middleware
app.add_middleware(CacheControlMiddleware)

# Mount static files for web viewer
try:
    app.mount("/viewer", StaticFiles(directory="/app/viewer"), name="viewer")
    logger.info("Web viewer mounted at /viewer/")
except Exception as e:
    logger.warning(f"Failed to mount web viewer: {e}")


@app.get("/")
async def root():
    """Root endpoint - redirect to web viewer."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/viewer/index.html")


@app.get("/health")
async def health_check():
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
            "input_directory": str(folder_config.input_directory),
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
async def start_file_monitor():
    """Start the file monitor (no auth required for web UI)."""
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
async def stop_file_monitor():
    """Stop the file monitor (no auth required for web UI)."""
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


# ===== Web Viewer API Endpoints =====

@app.get("/api/web/status")
async def get_web_status():
    """Get system status for web viewer (no auth required for web UI)."""
    total_input_files = 0
    total_output_files = 0

    for folder_config in settings.folders.values():
        input_path = folder_config.input_directory
        if input_path.exists():
            # Count input files
            total_input_files += len(list(input_path.rglob("*.md")))
            total_input_files += len(list(input_path.rglob("*.txt")))

    # Count output files
    output_path = settings.output.output_directory
    if output_path.exists():
        total_output_files = len(list(output_path.rglob("*.md")))

    return {
        "file_monitor_running": file_monitor.running if file_monitor else False,
        "enabled_folders": len([f for f in settings.folders.values() if f.enabled]),
        "total_input_files": total_input_files,
        "total_output_files": total_output_files,
    }


@app.get("/api/web/folders")
async def get_web_folders():
    """Get folder configurations for web viewer (no auth required for web UI)."""
    folders = []
    for name, folder_config in settings.folders.items():
        input_path = folder_config.input_directory
        input_files = 0
        if input_path.exists():
            input_files = len(list(input_path.rglob("*.md"))) + len(list(input_path.rglob("*.txt")))

        folders.append({
            "name": name,
            "path": str(folder_config.input_directory),
            "enabled": folder_config.enabled,
            "provider": folder_config.provider,
            "model": folder_config.model,
            "input_files": input_files,
            "delete_input_files": folder_config.delete_input_files if folder_config.delete_input_files is not None else settings.file_monitor.delete_input_files,
        })
    return folders


@app.get("/api/web/folders/{folder_name}")
async def get_web_folder_details(folder_name: str, date: Optional[str] = None):
    """Get detailed configuration for a specific folder (no auth required for web UI)."""
    if folder_name not in settings.folders:
        return {"success": False, "error": "Folder not found"}

    folder_config = settings.folders[folder_name]

    # Get file counts (with optional date filter)
    input_path = folder_config.input_directory
    input_files = 0

    if date:
        # Count files for specific date
        date_parts = date.split("/")
        if len(date_parts) == 3:
            # First check the direct date path (e.g., /app/bolus/pastures/2026/01/06/)
            date_path = input_path / date_parts[0] / date_parts[1] / date_parts[2]
            if date_path.exists() and date_path.is_dir():
                input_files = len(list(date_path.glob("*.md"))) + len(list(date_path.glob("*.txt")))
            else:
                # If not found, search subdirectories (e.g., /app/pastures/{subdir}/2026/01/06/)
                search_paths = []
                if input_path.exists() and input_path.is_dir():
                    for subdir in input_path.iterdir():
                        if subdir.is_dir():
                            date_path = subdir / date_parts[0] / date_parts[1] / date_parts[2]
                            if date_path.exists() and date_path.is_dir():
                                search_paths.append(date_path)

                for search_path in search_paths:
                    if search_path.exists():
                        input_files += len(list(search_path.glob("*.md")))
                        input_files += len(list(search_path.glob("*.txt")))
        else:
            # Invalid date format, count all files
            if input_path.exists():
                input_files = len(list(input_path.rglob("*.md"))) + len(list(input_path.rglob("*.txt")))
    else:
        # Count all files
        if input_path.exists():
            input_files = len(list(input_path.rglob("*.md"))) + len(list(input_path.rglob("*.txt")))

    # Get output directory
    if folder_config.output_directory:
        output_base = folder_config.output_directory
    else:
        output_base = settings.output.output_directory

    output_files = 0
    if date:
        # Count output files for specific date
        date_parts = date.split("/")
        if len(date_parts) == 3:
            output_path = output_base / date_parts[0] / date_parts[1] / date_parts[2]
            if output_path.exists():
                output_files = len(list(output_path.glob("*.md"))) + len(list(output_path.glob("*.json")))
        else:
            # Invalid date format, count all files
            if output_base.exists():
                output_files = len(list(output_base.rglob("*.md"))) + len(list(output_base.rglob("*.json")))
    else:
        # Count all output files
        if output_base.exists():
            output_files = len(list(output_base.rglob("*.md"))) + len(list(output_base.rglob("*.json")))

    # Load prompts (from files if specified, otherwise use inline values)
    try:
        system_prompt = folder_config.load_system_prompt()
    except Exception as e:
        system_prompt = f"Error loading system prompt: {e}"

    try:
        user_prompt_template = folder_config.load_user_prompt_template()
    except Exception as e:
        user_prompt_template = f"Error loading user prompt template: {e}"

    # Add prompt file info if using files
    prompt_source_info = {}
    if folder_config.prompt_files.system_prompt_file:
        prompt_source_info["system_prompt_file"] = str(folder_config.prompt_files.system_prompt_file)
    if folder_config.prompt_files.user_prompt_file:
        prompt_source_info["user_prompt_file"] = str(folder_config.prompt_files.user_prompt_file)

    return {
        "success": True,
        "name": folder_config.name,
        "input_directory": str(folder_config.input_directory),
        "enabled": folder_config.enabled,
        "provider": folder_config.provider,
        "model": folder_config.model,
        "temperature": folder_config.temperature,
        "max_tokens": folder_config.max_tokens,
        "output_format": folder_config.output_format,
        "output_directory": str(folder_config.output_directory) if folder_config.output_directory else str(settings.output.output_directory),
        "delete_input_files": folder_config.delete_input_files if folder_config.delete_input_files is not None else settings.file_monitor.delete_input_files,
        "system_prompt": system_prompt,
        "user_prompt_template": user_prompt_template,
        "prompt_source_info": prompt_source_info,
        "input_files": input_files,
        "output_files": output_files,
    }


@app.get("/api/web/config")
async def get_web_config():
    """Get config.ini content for web viewer (no auth required for web UI)."""
    try:
        config_path = Path("/app/config/config.ini")
        if config_path.exists():
            with open(config_path, "r") as f:
                return {"success": True, "content": f.read()}
        else:
            return {"success": False, "error": "Config file not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/web/config")
async def save_web_config(request: dict):
    """Save config.ini content from web viewer (no auth required for web UI)."""
    try:
        content = request.get("content")
        if not content:
            return {"success": False, "error": "No content provided"}

        config_path = Path("/app/config/config.ini")
        with open(config_path, "w") as f:
            f.write(content)

        # Reload application settings
        reload_success = reload_application_settings()
        if not reload_success:
            return {"success": False, "error": "Configuration saved but failed to reload settings"}

        return {"success": True, "message": "Configuration saved and reloaded"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/web/logs")
async def get_web_logs():
    """Get system logs for web viewer (no auth required for web UI)."""
    import io
    from contextlib import redirect_stderr

    # Capture recent logs
    log_buffer = io.StringIO()
    handler = logging.StreamHandler(log_buffer)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    # Generate some logs
    logs = log_buffer.getvalue()

    # Return actual log content if available
    log_file = Path("/app/logs/rumen.log")
    if log_file.exists():
        with open(log_file, "r") as f:
            # Return last 1000 lines
            lines = f.readlines()
            logs = "".join(lines[-1000:])
    else:
        logs = f"No log file found. System status: {'Running' if file_monitor and file_monitor.running else 'Stopped'}"

    root_logger.removeHandler(handler)
    return Response(content=logs, media_type="text/plain")


@app.get("/api/web/files/input/{folder_name}")
async def get_input_files(folder_name: str, date: Optional[str] = None):
    """Get input files for a specific folder, optionally filtered by date (YYYY/MM/DD)."""
    try:
        if folder_name not in settings.folders:
            return []

        folder_config = settings.folders[folder_name]
        input_path = folder_config.input_directory

        if not input_path.exists():
            return []

        files = []

        # If date filter is provided, search for that date pattern
        search_paths = [input_path]
        if date:
            date_parts = date.split("/")
            if len(date_parts) == 3:
                date_path = input_path / date_parts[0] / date_parts[1] / date_parts[2]
                logger.info(f"Looking for input files in: {date_path}, exists: {date_path.exists()}")
                if date_path.exists():
                    search_paths = [date_path]
                else:
                    # Also check if the input directory has date subdirectories (for cases like /app/pastures/{year}/{month}/{day}/)
                    search_paths = []
                    for subdir in input_path.rglob("*"):
                        if subdir.is_dir():
                            potential_date_path = subdir / date_parts[0] / date_parts[1] / date_parts[2]
                            if potential_date_path.exists() and potential_date_path.is_dir():
                                search_paths.append(potential_date_path)
                                logger.info(f"Found date path: {potential_date_path}")

        logger.info(f"Input file search paths: {search_paths}")

        for search_path in search_paths:
            if not search_path.exists():
                continue

            found_count = 0
            for file_path in search_path.rglob("*.md"):
                if file_path.is_file():
                    found_count += 1
                    stat = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    })

            logger.info(f"Found {found_count} .md files in {search_path}")

            for file_path in search_path.rglob("*.txt"):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    })

        logger.info(f"Returning {len(files)} input files for folder {folder_name}")
        return files
    except Exception as e:
        logger.error(f"Error listing input files: {e}")
        return []


@app.get("/api/web/files/output/{folder_name}")
async def get_output_files(folder_name: str, date: Optional[str] = None):
    """Get output files for a specific folder, optionally filtered by date (YYYY/MM/DD)."""
    try:
        output_path = settings.output.output_directory

        if not output_path.exists():
            return []

        files = []

        if folder_name == "all":
            # Get all output files
            search_path = output_path
            if date:
                # Filter by specific date
                date_parts = date.split("/")
                if len(date_parts) == 3:
                    search_path = output_path / date_parts[0] / date_parts[1] / date_parts[2]

            if search_path.exists():
                for file_path in search_path.rglob("*.md"):
                    if file_path.is_file():
                        stat = file_path.stat()
                        files.append({
                            "name": file_path.name,
                            "path": str(file_path),
                            "size": stat.st_size,
                            "modified": stat.st_mtime
                        })
        else:
            # Get files for specific folder (if it has a custom output directory)
            if folder_name in settings.folders:
                folder_config = settings.folders[folder_name]
                logger.info(f"Getting output files for folder: {folder_name}")
                logger.info(f"Folder config output_directory: {folder_config.output_directory}")

                if folder_config.output_directory:
                    folder_output = folder_config.output_directory
                else:
                    folder_output = output_path

                logger.info(f"Base folder output path: {folder_output}")

                # Apply date filter if provided
                if date:
                    date_parts = date.split("/")
                    if len(date_parts) == 3:
                        folder_output = folder_output / date_parts[0] / date_parts[1] / date_parts[2]
                        logger.info(f"With date filter: {folder_output}")

                logger.info(f"Final search path: {folder_output}, exists: {folder_output.exists()}")

                if folder_output.exists():
                    found_files = list(folder_output.rglob("*.md"))
                    logger.info(f"Found {len(found_files)} files with rglob")
                    for file_path in found_files:
                        if file_path.is_file():
                            stat = file_path.stat()
                            file_info = {
                                "name": file_path.name,
                                "path": str(file_path),
                                "size": stat.st_size,
                                "modified": stat.st_mtime
                            }
                            files.append(file_info)
                            logger.info(f"Adding file: {file_info['name']}")

        logger.info(f"Returning {len(files)} files for folder {folder_name}")
        return files
    except Exception as e:
        logger.error(f"Error listing output files: {e}")
        return []


@app.get("/api/web/file/content")
async def get_file_content(path: str):
    """Get content of a specific file."""
    try:
        file_path = Path(path)

        # Security check - only allow files from /app directory
        if not str(file_path).startswith("/app"):
            return {"success": False, "error": "Access denied"}

        if not file_path.exists():
            return {"success": False, "error": "File not found"}

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {"success": True, "content": content}
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/web/prompts")
async def get_web_prompts():
    """Get all prompts from the prompts directory (no auth required for web UI)."""
    try:
        prompts_dir = Path("/app/prompts")
        if not prompts_dir.exists():
            return {"success": False, "error": "Prompts directory not found"}

        prompts = []
        for prompt_file in prompts_dir.rglob("*.md"):
            if prompt_file.is_file() and prompt_file.name != "README.md":
                # Read first part for preview
                preview = ""
                try:
                    with open(prompt_file, "r", encoding="utf-8") as f:
                        preview = f.read(200)
                except:
                    pass

                prompts.append({
                    "name": prompt_file.stem,
                    "path": str(prompt_file.relative_to("/app")),
                    "preview": preview
                })

        return {"success": True, "prompts": prompts}
    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/web/prompt")
async def get_web_prompt(path: str):
    """Get content of a specific prompt file (no auth required for web UI)."""
    try:
        prompt_path = Path("/app") / path

        # Security check - only allow files from /app/prompts directory
        if not str(prompt_path).startswith("/app/prompts"):
            return {"success": False, "error": "Access denied"}

        if not prompt_path.exists():
            return {"success": False, "error": "Prompt file not found"}

        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {"success": True, "content": content}
    except Exception as e:
        logger.error(f"Error reading prompt: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/web/prompt")
async def save_web_prompt(request: dict):
    """Save a prompt file (no auth required for web UI)."""
    try:
        path = request.get("path")
        content = request.get("content")

        if not path or not content:
            return {"success": False, "error": "Path and content are required"}

        prompt_path = Path("/app") / path

        # Security check - only allow files from /app/prompts directory
        if not str(prompt_path).startswith("/app/prompts"):
            return {"success": False, "error": "Access denied"}

        # Create parent directories if they don't exist
        prompt_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the prompt content
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Prompt saved: {prompt_path}")

        # Reload application settings to pick up prompt changes
        reload_success = reload_application_settings()
        if not reload_success:
            logger.warning("Application settings reload failed after prompt save")

        return {"success": True, "message": "Prompt saved and application reloaded"}
    except Exception as e:
        logger.error(f"Error saving prompt: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/web/dates")
async def get_web_dates():
    """Get all dates that have processed content (no auth required for web UI)."""
    try:
        dates = set()

        # Scan all enabled folders' output directories for date-based subdirectories
        for folder_config in settings.folders.values():
            if not folder_config.enabled:
                continue

            # Get the output directory for this folder
            if folder_config.output_directory:
                output_base = folder_config.output_directory
            else:
                output_base = settings.output.output_directory

            if not output_base.exists():
                continue

            # Scan for YYYY/MM/DD subdirectories
            for year_dir in output_base.iterdir():
                if not year_dir.is_dir() or not year_dir.name.isdigit():
                    continue

                for month_dir in year_dir.iterdir():
                    if not month_dir.is_dir() or not month_dir.name.isdigit():
                        continue

                    for day_dir in month_dir.iterdir():
                        if not day_dir.is_dir() or not day_dir.name.isdigit():
                            continue

                        # Check if this day directory has any markdown or json files
                        has_content = any(
                            f.suffix in ['.md', '.json'] and f.is_file()
                            for f in day_dir.iterdir()
                        )

                        if has_content:
                            date_str = f"{year_dir.name}/{month_dir.name}/{day_dir.name}"
                            dates.add(date_str)

        # Sort dates descending (newest first)
        sorted_dates = sorted(list(dates), reverse=True)

        return {"success": True, "dates": sorted_dates}
    except Exception as e:
        logger.error(f"Error getting dates: {e}")
        return {"success": False, "error": str(e)}


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
