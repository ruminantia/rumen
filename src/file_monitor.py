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

        # Skip already processed files
        if self._is_file_processed(file_path):
            logger.debug(f"Skipping already processed file: {file_path}")
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

    def _is_file_processed(self, file_path: Path) -> bool:
        """
        Check if a file has already been processed or rejected.

        Args:
            file_path: Path to the file

        Returns:
            True if the file has been processed or rejected
        """
        # Check if filename contains .processed. or .rejected. marker
        return ".processed." in file_path.name or ".rejected." in file_path.name

    def _mark_file_processed(self, file_path: Path) -> bool:
        """
        Mark a file as processed by renaming it with a .processed. marker.

        Args:
            file_path: Path to the file

        Returns:
            Path to the marked file if successful, None otherwise
        """
        try:
            # Insert .processed. before the file extension
            # e.g., "document.md" -> "document.processed.md"
            stem = file_path.stem
            suffix = file_path.suffix
            new_name = f"{stem}.processed{suffix}"
            new_path = file_path.parent / new_name

            # Rename the file
            file_path.rename(new_path)
            logger.debug(f"Marked file as processed: {file_path} -> {new_path}")
            return new_path

        except Exception as e:
            logger.error(f"Failed to mark file as processed {file_path}: {e}")
            return None

    def _mark_file_rejected(self, file_path: Path, reason: str = "") -> bool:
        """
        Mark a file as rejected by renaming it with a .rejected. or .blurb. marker.

        Args:
            file_path: Path to the file
            reason: Optional reason for rejection (used to determine marker type)

        Returns:
            Path to the marked file if successful, None otherwise
        """
        try:
            # Determine marker type based on reason
            # If reason contains "BLURB", use .blurb. marker, otherwise use .rejected.
            marker = "blurb" if "BLURB" in reason.upper() else "rejected"

            # Insert marker before the file extension
            # e.g., "document.md" -> "document.blurb.md" or "document.rejected.md"
            stem = file_path.stem
            suffix = file_path.suffix
            new_name = f"{stem}.{marker}{suffix}"
            new_path = file_path.parent / new_name

            # Rename the file
            file_path.rename(new_path)
            logger.info(f"Marked file as {marker}: {file_path} -> {new_path}. Reason: {reason}")
            return new_path

        except Exception as e:
            logger.error(f"Failed to mark file as rejected/blurb {file_path}: {e}")
            return None

    def _check_for_rejection_triggers(self, content: str, trigger_words: list[str]) -> tuple[bool, str]:
        """
        Check if content contains any rejection trigger words.

        Args:
            content: Content to check
            trigger_words: List of trigger words to look for

        Returns:
            Tuple of (should_reject: bool, matched_word: str)
        """
        if not trigger_words:
            return False, ""

        content_lower = content.lower()
        for word in trigger_words:
            if word.lower() in content_lower:
                return True, word

        return False, ""

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

            # Call the processing callback (returns tuple: success, rejected, rejection_reason)
            result = await self.process_callback(
                content=content, file_path=file_path, folder_config=folder_config
            )

            # Handle both old boolean return and new tuple return
            if isinstance(result, tuple):
                success, rejected, rejection_reason = result
            else:
                success = result
                rejected = False
                rejection_reason = ""

            if success and rejected:
                # File was rejected due to trigger word
                self._mark_file_rejected(file_path, rejection_reason)
                return True
            elif success:
                # Determine whether to delete input files (per-folder setting or global default)
                should_delete = (
                    folder_config.delete_input_files
                    if folder_config.delete_input_files is not None
                    else self.settings.file_monitor.delete_input_files
                )

                if should_delete:
                    # Mark as processed first, then delete
                    marked_path = self._mark_file_processed(file_path)
                    if marked_path:
                        self._cleanup_file(marked_path)
                else:
                    # Just mark as processed without deleting
                    self._mark_file_processed(file_path)
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
        Clean up processed file by deleting it.

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
        """Start monitoring a specific routine."""
        input_path = folder_config.input_directory

        # Create input directory if it doesn't exist
        try:
            input_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured input directory exists: {input_path}")
        except Exception as e:
            logger.error(f"Could not create input directory {input_path}: {e}")
            return

        if not input_path.exists() or not input_path.is_dir():
            logger.error(f"Input path is not a directory: {input_path}")
            return

        # Create event handler
        event_handler = FolderEventHandler(folder_config, self.file_processor)
        self.event_handlers[folder_name] = event_handler

        # Start watching
        try:
            self.observer.schedule(
                event_handler,
                str(input_path),
                recursive=True,  # Watch subdirectories recursively
            )
            logger.info(f"Started monitoring routine: {input_path}")
        except Exception as e:
            logger.error(f"Failed to start monitoring routine {input_path}: {e}")

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
            input_path = folder_config.input_directory

            logger.info(f"Processing existing files in: {input_path}")

            try:
                # Collect all files to process (only unprocessed ones)
                files_to_process = []
                skipped_processed = 0

                for file_path in input_path.rglob("*.md"):
                    if self.file_processor.should_process_file(file_path):
                        # Check if already marked as processed
                        if not self.file_processor._is_file_processed(file_path):
                            files_to_process.append(file_path)
                        else:
                            skipped_processed += 1

                for file_path in input_path.rglob("*.markdown"):
                    if self.file_processor.should_process_file(file_path):
                        if not self.file_processor._is_file_processed(file_path):
                            files_to_process.append(file_path)
                        else:
                            skipped_processed += 1

                for file_path in input_path.rglob("*.txt"):
                    if self.file_processor.should_process_file(file_path):
                        if not self.file_processor._is_file_processed(file_path):
                            files_to_process.append(file_path)
                        else:
                            skipped_processed += 1

                logger.info(f"Found {len(files_to_process)} unprocessed files to process (skipped {skipped_processed} already processed)")

                if not files_to_process:
                    logger.info("No unprocessed files found in this folder")
                    continue

                # Process files with delay to avoid rate limits
                import time as time_module
                for i, file_path in enumerate(files_to_process, 1):
                    # Check if file still exists (may have been processed by another stage)
                    if not file_path.exists():
                        logger.info(f"File {i}/{len(files_to_process)} no longer exists, skipping: {file_path.name}")
                        continue

                    logger.info(f"Processing file {i}/{len(files_to_process)}: {file_path.name}")
                    self._process_file_sync(file_path, folder_config)

                    # Add delay between files to avoid rate limits (10 seconds for free models)
                    if i < len(files_to_process):
                        logger.debug("Waiting 10 seconds to avoid rate limits...")
                        time_module.sleep(10)

            except Exception as e:
                logger.error(f"Error processing existing files in {input_path}: {e}")

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
            from .main import output_handler
            from .config import LLMSettings
            from .llm_client import LLMClient

            # Create folder-specific LLM settings
            folder_llm_settings = LLMSettings(
                provider=folder_config.provider,
                model=folder_config.model,
                base_url=self.settings.llm.base_url,  # Will be overridden
                api_key=self.settings.llm.api_key,
                temperature=folder_config.temperature,
                max_tokens=folder_config.max_tokens,
                top_p=self.settings.llm.top_p,
                retry_attempts=self.settings.llm.retry_attempts,
                retry_delay=self.settings.llm.retry_delay,
            )

            # Get provider-specific base_url
            provider_name = folder_config.provider
            if provider_name in self.settings.provider_base_urls:
                folder_llm_settings.base_url = self.settings.provider_base_urls[provider_name]

            # Create folder-specific LLM client
            folder_llm_client = LLMClient(folder_llm_settings)

            logger.info(f"Using provider: {folder_config.provider}, model: {folder_config.model}")

            # Process content with LLM
            processed_content = folder_llm_client.process_content(
                content=content,
                system_prompt=folder_config.load_system_prompt(),
                user_prompt_template=folder_config.load_user_prompt_template(),
            )

            # Check for rejection trigger words
            should_reject, matched_word = self.file_processor._check_for_rejection_triggers(
                processed_content,
                folder_config.rejection_trigger_words
            )

            # Save the result (whether accepted or rejected)
            output_handler.save_result(
                content=processed_content,
                original_filename=file_path.name,
                folder_name=folder_config.name,
                output_format=folder_config.output_format,
                metadata={
                    "original_file": str(file_path),
                    "folder": folder_config.name,
                    "model": folder_config.model,
                    "provider": folder_config.provider,
                },
                folder_config=folder_config,
                original_filepath=str(file_path),
                rejected=should_reject,
                original_input_content=content,
                append_input=folder_config.append_input_to_output,
            )

            if should_reject:
                logger.warning(f"File {file_path} rejected due to trigger word: {matched_word}")
                self.file_processor._mark_file_rejected(file_path, f"Trigger word found: {matched_word}")
                return

            # Clean up the processed file if configured to do so
            should_delete = (
                folder_config.delete_input_files
                if folder_config.delete_input_files is not None
                else self.settings.file_monitor.delete_input_files
            )

            if should_delete:
                # Mark as processed first, then delete
                marked_path = self.file_processor._mark_file_processed(file_path)
                if marked_path:
                    self.file_processor._cleanup_file(marked_path)
            else:
                # Just mark as processed without deleting
                self.file_processor._mark_file_processed(file_path)

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
