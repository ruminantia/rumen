"""
File monitoring system for watching input folders and triggering LLM processing.
"""

import time
import logging
from pathlib import Path
from typing import Dict, Set, Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .config import FolderConfig, FileMonitorSettings

logger = logging.getLogger(__name__)


class FileProcessor:
    """Handles file processing logic."""

    def __init__(self, process_callback: Callable, settings):
        self.process_callback = process_callback
        self.processing_files: Set[Path] = set()
        self.settings = settings

    def should_process_file(self, file_path: Path) -> bool:
        """
        Check if a file should be processed.

        Args:
            file_path: Path to the file

        Returns:
            True if the file should be processed
        """
        # Skip if file is already being processed
        if file_path in self.processing_files:
            return False

        # Skip hidden files and temporary files
        if file_path.name.startswith(".") or file_path.name.endswith("~"):
            return False

        # Only process markdown files by default
        if file_path.suffix.lower() not in [".md", ".markdown", ".txt"]:
            logger.debug(f"Skipping non-markdown file: {file_path}")
            return False

        # Check if file is complete (not being written)
        try:
            initial_size = file_path.stat().st_size
            time.sleep(0.1)  # Small delay
            final_size = file_path.stat().st_size
            if initial_size != final_size:
                logger.debug(f"File still being written: {file_path}")
                return False
        except (OSError, IOError) as e:
            logger.warning(f"Error checking file size for {file_path}: {e}")
            return False

        return True

    async def process_file(self, file_path: Path, folder_config: FolderConfig) -> bool:
        """
        Process a single file.

        Args:
            file_path: Path to the file
            folder_config: Configuration for the folder

        Returns:
            True if processing was successful
        """
        if not self.should_process_file(file_path):
            return False

        try:
            self.processing_files.add(file_path)

            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                logger.warning(f"Empty file: {file_path}")
                return False

            # Call the processing callback
            success = await self.process_callback(
                content=content, file_path=file_path, folder_config=folder_config
            )

            if success:
                # Clean up the processed file
                self._cleanup_file(file_path)
            else:
                logger.error(f"Failed to process file: {file_path}")

            return success

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return False
        finally:
            self.processing_files.discard(file_path)

    def _cleanup_file(self, file_path: Path):
        """
        Clean up processed file by deleting it (no longer moving to processed directory).

        Args:
            file_path: Path to the processed file
        """
        try:
            # Simply delete the processed file since results are now saved to output directory
            file_path.unlink()
            logger.debug(f"Deleted processed file: {file_path}")

        except Exception as e:
            logger.warning(f"Could not delete processed file {file_path}: {e}")


class FolderEventHandler(FileSystemEventHandler):
    """Event handler for folder monitoring."""

    def __init__(self, folder_config: FolderConfig, file_processor: FileProcessor):
        self.folder_config = folder_config
        self.file_processor = file_processor
        self.pending_files: Dict[Path, float] = {}
        self.settings = file_processor.settings

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        logger.debug(f"File created: {file_path}")

        # Add to pending files with timestamp
        self.pending_files[file_path] = time.time()

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        logger.debug(f"File modified: {file_path}")

        # Update timestamp for pending files
        if file_path in self.pending_files:
            self.pending_files[file_path] = time.time()

    def process_pending_files(self):
        """Process files that have been stable for the required timeout."""
        current_time = time.time()
        files_to_process = []

        # Check which files are ready to process
        for file_path, timestamp in list(self.pending_files.items()):
            if current_time - timestamp >= self.settings.file_monitor.file_timeout:
                files_to_process.append(file_path)
                del self.pending_files[file_path]

        # Process ready files
        for file_path in files_to_process:
            if file_path.exists():
                # Run the async processing function
                import asyncio

                asyncio.run(
                    self.file_processor.process_file(file_path, self.folder_config)
                )


class FileMonitor:
    """Main file monitoring system."""

    def __init__(self, process_callback: Callable, settings):
        self.settings = settings
        self.process_callback = process_callback
        self.file_processor = FileProcessor(process_callback, settings)
        self.observer = Observer()
        self.event_handlers: Dict[str, FolderEventHandler] = {}
        self.running = False

    def start(self):
        """Start monitoring all enabled folders."""
        if self.running:
            logger.warning("File monitor is already running")
            return

        enabled_folders = {
            name: config
            for name, config in self.settings.folders.items()
            if config.enabled
        }

        if not enabled_folders:
            logger.info("No folders enabled for monitoring")
            return

        logger.info(f"Starting file monitor for {len(enabled_folders)} folders")

        for folder_name, folder_config in enabled_folders.items():
            self._start_folder_monitoring(folder_name, folder_config)

        if hasattr(self.observer, "_watchers") and self.observer._watchers:
            self.observer.start()
            self.running = True
            logger.info("File monitor started successfully")
        elif self.observer._handlers:
            self.observer.start()
            self.running = True
            logger.info("File monitor started successfully")
        else:
            logger.warning("No folders to monitor")

    def _start_folder_monitoring(self, folder_name: str, folder_config: FolderConfig):
        """Start monitoring a specific folder."""
        folder_path = folder_config.folder_path

        # Create folder if it doesn't exist
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured folder exists: {folder_path}")
        except Exception as e:
            logger.error(f"Could not create folder {folder_path}: {e}")
            return

        if not folder_path.exists() or not folder_path.is_dir():
            logger.error(f"Folder path is not a directory: {folder_path}")
            return

        # Create event handler
        event_handler = FolderEventHandler(folder_config, self.file_processor)
        self.event_handlers[folder_name] = event_handler

        # Start watching
        try:
            self.observer.schedule(
                event_handler,
                str(folder_path),
                recursive=True,  # Watch subdirectories recursively
            )
            logger.info(f"Started monitoring folder: {folder_path}")
        except Exception as e:
            logger.error(f"Failed to start monitoring folder {folder_path}: {e}")

    def stop(self):
        """Stop the file monitor."""
        if not self.running:
            return

        logger.info("Stopping file monitor")
        self.observer.stop()
        self.observer.join()
        self.running = False
        logger.info("File monitor stopped")

    def process_existing_files(self):
        """Process any existing files in monitored folders."""
        if not self.running:
            logger.warning("File monitor not running, cannot process existing files")
            return

        for folder_name, event_handler in self.event_handlers.items():
            folder_config = self.settings.folders[folder_name]
            folder_path = folder_config.folder_path

            logger.info(f"Processing existing files in: {folder_path}")

            try:
                # Process all markdown files recursively
                for file_path in folder_path.rglob("*.md"):
                    if self.file_processor.should_process_file(file_path):
                        self._process_file_sync(file_path, folder_config)

                for file_path in folder_path.rglob("*.markdown"):
                    if self.file_processor.should_process_file(file_path):
                        self._process_file_sync(file_path, folder_config)

                for file_path in folder_path.rglob("*.txt"):
                    if self.file_processor.should_process_file(file_path):
                        self._process_file_sync(file_path, folder_config)

            except Exception as e:
                logger.error(f"Error processing existing files in {folder_path}: {e}")

    def _process_file_sync(self, file_path: Path, folder_config: FolderConfig):
        """Process a file synchronously for existing files at startup."""
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                logger.warning(f"Empty file: {file_path}")
                return

            # Import here to avoid circular imports
            from .main import llm_client, output_handler

            # Process content with LLM
            processed_content = llm_client.process_content(
                content=content,
                system_prompt=folder_config.load_system_prompt(),
                user_prompt_template=folder_config.load_user_prompt_template(),
            )

            # Save the result
            output_handler.save_result(
                content=processed_content,
                original_filename=str(file_path),
                folder_name=folder_config.name,
                output_format=folder_config.output_format,
                metadata={
                    "original_file": str(file_path),
                    "folder": folder_config.name,
                    "model": folder_config.model,
                    "provider": folder_config.provider,
                },
                folder_config=folder_config,
            )

            # Clean up the processed file
            self.file_processor._cleanup_file(file_path)

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

    def run_monitoring_loop(self):
        """Run the main monitoring loop."""
        if not self.running:
            self.start()

        logger.info("Starting file monitoring loop")

        try:
            while self.running:
                # Process pending files for all handlers
                for event_handler in self.event_handlers.values():
                    event_handler.process_pending_files()

                # Sleep for the monitoring interval
                time.sleep(self.settings.file_monitor.monitor_interval)

        except KeyboardInterrupt:
            logger.info("File monitoring interrupted by user")
        except Exception as e:
            logger.error(f"File monitoring loop error: {e}")
        finally:
            self.stop()
