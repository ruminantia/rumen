"""
Output handler for saving processed LLM results to files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from .config import OutputSettings, FolderConfig

logger = logging.getLogger(__name__)


class OutputHandler:
    """Handles saving processed results to files."""

    def __init__(self, settings: OutputSettings):
        self.settings = settings
        self._ensure_output_directory()

    def _get_output_directory(
        self, folder_config: Optional[FolderConfig] = None, original_filepath: Optional[str] = None
    ) -> Path:
        """Get the appropriate output directory for a folder configuration with date-based subdirectories."""
        base_dir = None
        if folder_config and folder_config.output_directory:
            base_dir = folder_config.output_directory
        else:
            base_dir = self.settings.output_directory

        # Extract date from original filepath if available (format: .../YYYY/MM/DD/file.md)
        date_path = self._extract_date_path(original_filepath)

        # Append date-based subdirectory
        if date_path:
            return base_dir / date_path
        else:
            # Use current date if no date in input path
            now = datetime.now()
            date_dir = now.strftime("%Y/%m/%d")
            return base_dir / date_dir

    def _extract_date_path(self, filepath: Optional[str]) -> Optional[str]:
        """Extract date path (YYYY/MM/DD) from a file path if present."""
        if not filepath:
            return None

        path = Path(filepath)
        parts = path.parts

        # Look for date pattern in path parts: YYYY/MM/DD
        for i in range(len(parts) - 2):
            if (
                parts[i].isdigit() and len(parts[i]) == 4 and  # Year
                parts[i + 1].isdigit() and len(parts[i + 1]) == 2 and  # Month
                parts[i + 2].isdigit() and len(parts[i + 2]) == 2  # Day
            ):
                return f"{parts[i]}/{parts[i+1]}/{parts[i+2]}"

        return None

    def _ensure_output_directory_for_folder(self, output_dir: Path):
        """Ensure the output directory exists."""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured output directory exists: {output_dir}")
        except Exception as e:
            logger.error(f"Could not create output directory {output_dir}: {e}")
            raise

    def _ensure_output_directory(self):
        """Ensure the default output directory exists."""
        try:
            self.settings.output_directory.mkdir(parents=True, exist_ok=True)
            logger.debug(
                f"Ensured output directory exists: {self.settings.output_directory}"
            )
        except Exception as e:
            logger.error(
                f"Could not create output directory {self.settings.output_directory}: {e}"
            )
            raise

    def save_result(
        self,
        content: str,
        original_filename: Optional[str] = None,
        folder_name: Optional[str] = None,
        output_format: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        folder_config: Optional[FolderConfig] = None,
        original_filepath: Optional[str] = None,
        skip_metadata: bool = False,
        rejected: bool = False,
        original_input_content: Optional[str] = None,
        append_input: Optional[bool] = None,
    ) -> Path:
        """
        Save processed result to a file.

        Args:
            content: The processed content to save
            original_filename: Original filename (for naming)
            folder_name: Name of the folder that triggered processing
            output_format: Output format (markdown, json)
            metadata: Additional metadata to include
            folder_config: Folder configuration for custom output directory
            original_filepath: Full path to original file (for date extraction)
            skip_metadata: If True, skip adding metadata frontmatter (for publication-ready output)
            rejected: If True, mark the file as rejected in the filename
            original_input_content: Original input content to append if append_input is True
            append_input: If True, append original input content to output

        Returns:
            Path to the saved file
        """
        if output_format is None:
            output_format = self.settings.output_format

        # Append original input content if requested
        if append_input and original_input_content:
            content = self._append_input_content(content, original_input_content)

        # Generate filename
        filename = self._generate_filename(
            original_filename=original_filename,
            folder_name=folder_name,
            output_format=output_format,
            rejected=rejected,
        )

        # Get output directory with date-based subdirectory
        output_dir = self._get_output_directory(folder_config, original_filepath)
        self._ensure_output_directory_for_folder(output_dir)
        file_path = output_dir / filename

        try:
            if output_format.lower() == "json":
                self._save_as_json(file_path, content, metadata)
            else:
                self._save_as_markdown(file_path, content, metadata, skip_metadata)

            logger.info(f"Saved result to: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Error saving result to {file_path}: {e}")
            raise

    def _generate_filename(
        self,
        original_filename: Optional[str] = None,
        folder_name: Optional[str] = None,
        output_format: str = "markdown",
        rejected: bool = False,
    ) -> str:
        """
        Generate a filename for the output file.

        Args:
            original_filename: Original filename (for naming)
            folder_name: Name of the folder that triggered processing
            output_format: Output format (markdown, json)
            rejected: If True, mark file as rejected in filename

        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]

        # Build filename components
        components = []

        if folder_name:
            components.append(folder_name)

        if original_filename:
            # Remove extension from original filename
            original_stem = Path(original_filename).stem
            components.append(original_stem)

        components.append(timestamp)
        components.append(unique_id)

        # Join components with underscores
        base_name = "_".join(components)

        # Add rejection marker if needed
        if rejected:
            base_name = f"{base_name}.rejected"

        # Add appropriate extension
        if output_format.lower() == "json":
            extension = "json"
        else:
            extension = "md"

        return f"{base_name}.{extension}"

    def _append_input_content(self, processed_content: str, original_input: str) -> str:
        """
        Append original input content to processed output.

        Args:
            processed_content: The processed LLM output
            original_input: The original input content

        Returns:
            Combined content with original input appended
        """
        separator = "\n\n" + "=" * 80 + "\n\n"
        combined = (
            processed_content
            + separator
            + "## Original Input Content\n\n"
            + original_input
        )
        return combined

    def _save_as_markdown(
        self, file_path: Path, content: str, metadata: Optional[Dict[str, Any]] = None, skip_metadata: bool = False
    ):
        """
        Save content as markdown file with optional metadata header.

        Args:
            file_path: Path to save the file
            content: Content to save
            metadata: Optional metadata to include as YAML frontmatter
            skip_metadata: If True, skip adding metadata frontmatter (for publication-ready output)
        """
        with open(file_path, "w", encoding="utf-8") as f:
            # Add YAML frontmatter if metadata is provided and skip_metadata is False
            if metadata and not skip_metadata:
                f.write("---\n")
                for key, value in metadata.items():
                    f.write(f"{key}: {value}\n")
                f.write("---\n\n")

            # Write the main content
            f.write(content)

            # Ensure file ends with newline
            if not content.endswith("\n"):
                f.write("\n")

    def _save_as_json(
        self, file_path: Path, content: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Save content as JSON file with metadata.

        Args:
            file_path: Path to save the file
            content: Content to save
            metadata: Optional metadata to include
        """
        result_data = {
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        # Add metadata if provided
        if metadata:
            result_data["metadata"] = metadata

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)

    def save_error_result(
        self,
        error_message: str,
        original_filename: Optional[str] = None,
        folder_name: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
        folder_config: Optional[FolderConfig] = None,
        original_filepath: Optional[str] = None,
    ) -> Path:
        """
        Save error information to a file.

        Args:
            error_message: Error message
            original_filename: Original filename (for naming)
            folder_name: Name of the folder that triggered processing
            error_details: Additional error details
            folder_config: Folder configuration for custom output directory
            original_filepath: Full path to original file (for date extraction)

        Returns:
            Path to the saved error file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]

        # Build filename
        components = ["error"]
        if folder_name:
            components.append(folder_name)
        if original_filename:
            original_stem = Path(original_filename).stem
            components.append(original_stem)
        components.extend([timestamp, unique_id])

        base_name = "_".join(components)
        filename = f"{base_name}.json"

        # Get output directory with date-based subdirectory
        output_dir = self._get_output_directory(folder_config, original_filepath)
        self._ensure_output_directory_for_folder(output_dir)
        file_path = output_dir / filename

        error_data = {
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "original_filename": original_filename,
            "folder_name": folder_name,
        }

        if error_details:
            error_data["details"] = error_details

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(error_data, f, indent=2, ensure_ascii=False)

            logger.warning(f"Saved error result to: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Error saving error result to {file_path}: {e}")
            raise

    def list_results(
        self, limit: Optional[int] = None, folder_config: Optional[FolderConfig] = None
    ) -> list[Path]:
        """
        List all result files in the output directory.

        Args:
            limit: Maximum number of files to return
            folder_config: Folder configuration for custom output directory

        Returns:
            List of file paths
        """
        try:
            output_dir = self._get_output_directory(folder_config)
            files = list(output_dir.glob("*"))
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            if limit:
                files = files[:limit]

            return files

        except Exception as e:
            logger.error(f"Error listing results: {e}")
            return []

    def get_result_count(self, folder_config: Optional[FolderConfig] = None) -> int:
        """
        Get the number of result files in the output directory.

        Args:
            folder_config: Folder configuration for custom output directory

        Returns:
            Number of result files
        """
        try:
            output_dir = self._get_output_directory(folder_config)
            files = list(output_dir.glob("*"))
            return len(files)
        except Exception as e:
            logger.error(f"Error counting results: {e}")
            return 0

    def cleanup_old_results(
        self, max_age_days: int = 30, folder_config: Optional[FolderConfig] = None
    ):
        """
        Remove result files older than the specified number of days.

        Args:
            max_age_days: Maximum age in days to keep files
            folder_config: Folder configuration for custom output directory
        """
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
            deleted_count = 0

            output_dir = self._get_output_directory(folder_config)

            for file_path in output_dir.glob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old result files")

        except Exception as e:
            logger.error(f"Error cleaning up old results: {e}")
