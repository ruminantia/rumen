"""
Configuration models and settings for Rumen LLM API.
"""

import os
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from pathlib import Path
import configparser


class PromptFileConfig(BaseModel):
    """Configuration for prompt file references."""

    system_prompt_file: Optional[Path] = Field(
        default=None, description="Path to system prompt file"
    )
    user_prompt_file: Optional[Path] = Field(
        default=None, description="Path to user prompt template file"
    )

    @validator("system_prompt_file", "user_prompt_file")
    def validate_prompt_file_path(cls, v):
        """Ensure prompt file paths are resolved correctly."""
        if v is not None:
            # Convert to Path if it's a string
            path = Path(v) if isinstance(v, str) else v
            # If it's a relative path, resolve it relative to the current working directory
            if not path.is_absolute():
                return Path.cwd() / path
            return path
        return v


class LLMSettings(BaseModel):
    """Settings for LLM provider configuration."""

    provider: str = Field(
        default="openrouter",
        description="LLM provider (openrouter, openai, gemini, deepseek, zai)",
    )
    model: str = Field(default="google/gemini-2.5-flash-lite", description="Model name")
    base_url: str = Field(
        default="https://openrouter.ai/api/v1", description="API base URL"
    )
    api_key: str = Field(description="API key for the provider")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Temperature for generation"
    )
    max_tokens: int = Field(
        default=2048, ge=1, le=32000, description="Maximum tokens to generate"
    )
    top_p: float = Field(
        default=0.9, ge=0.0, le=1.0, description="Top-p sampling parameter"
    )
    thinking_enabled: bool = Field(
        default=False, description="Enable thinking/chain-of-thought"
    )
    search_enabled: bool = Field(default=False, description="Enable web search")
    retry_attempts: int = Field(
        default=3, ge=1, le=10, description="Number of retry attempts"
    )
    retry_delay: int = Field(
        default=2, ge=1, le=60, description="Delay between retries in seconds"
    )

    # Provider-specific headers
    http_referer: Optional[str] = Field(
        default=None, description="HTTP Referer for OpenRouter"
    )
    x_title: Optional[str] = Field(default=None, description="X-Title for OpenRouter")


class FolderConfig(BaseModel):
    """Configuration for a monitored routine."""

    name: str = Field(description="Routine configuration name")
    input_directory: Path = Field(description="Input directory to monitor for files")
    enabled: bool = Field(default=False, description="Whether this routine is monitored")
    system_prompt: str = Field(description="System prompt for this routine")
    user_prompt_template: str = Field(
        description="User prompt template with {content} placeholder"
    )
    provider: str = Field(
        default="openrouter", description="LLM provider for this routine"
    )
    model: str = Field(
        default="google/gemini-2.5-flash-lite", description="Model for this routine"
    )
    temperature: float = Field(default=0.7, description="Temperature for this routine")
    max_tokens: int = Field(default=2048, description="Max tokens for this routine")
    output_format: str = Field(
        default="markdown", description="Output format (markdown, json)"
    )
    output_directory: Optional[Path] = Field(
        default=None, description="Custom output directory for this routine (optional)"
    )
    prompt_files: PromptFileConfig = Field(
        default_factory=PromptFileConfig, description="Prompt file configuration"
    )
    delete_input_files: Optional[bool] = Field(
        default=None,
        description="Whether to delete input files after processing (None = use global setting)",
    )
    rejection_trigger_words: Optional[List[str]] = Field(
        default=None,
        description="List of words that trigger file rejection if found in output",
    )
    append_input_to_output: Optional[bool] = Field(
        default=None,
        description="Whether to append original input content to output (None = use global setting)",
    )

    @validator("input_directory")
    def validate_input_directory(cls, v):
        """Ensure input directory path is absolute."""
        if not v.is_absolute():
            return Path("/app") / v
        return v

    @validator("output_directory")
    def validate_output_directory(cls, v):
        """Ensure output directory is absolute if provided."""
        if v is not None and not v.is_absolute():
            return Path("/app") / v
        return v

    def load_system_prompt(self) -> str:
        """Load system prompt from file if specified, otherwise use configured prompt."""
        if (
            self.prompt_files.system_prompt_file
            and self.prompt_files.system_prompt_file.exists()
        ):
            try:
                with open(
                    self.prompt_files.system_prompt_file, "r", encoding="utf-8"
                ) as f:
                    return f.read().strip()
            except Exception as e:
                raise ValueError(
                    f"Failed to load system prompt from {self.prompt_files.system_prompt_file}: {e}"
                )
        return self.system_prompt

    def load_user_prompt_template(self) -> str:
        """Load user prompt template from file if specified, otherwise use configured template."""
        if (
            self.prompt_files.user_prompt_file
            and self.prompt_files.user_prompt_file.exists()
        ):
            try:
                with open(
                    self.prompt_files.user_prompt_file, "r", encoding="utf-8"
                ) as f:
                    return f.read().strip()
            except Exception as e:
                raise ValueError(
                    f"Failed to load user prompt template from {self.prompt_files.user_prompt_file}: {e}"
                )
        return self.user_prompt_template


class APISettings(BaseModel):
    """API server settings."""

    host: str = Field(default="0.0.0.0", description="API server host")
    port: int = Field(default=8000, ge=1, le=65535, description="API server port")
    workers: int = Field(
        default=1, ge=1, le=10, description="Number of worker processes"
    )


class FileMonitorSettings(BaseModel):
    """File monitoring settings."""

    monitor_interval: int = Field(
        default=5, ge=1, le=60, description="Monitoring interval in seconds"
    )
    file_timeout: int = Field(
        default=30, ge=10, le=300, description="File processing timeout in seconds"
    )
    delete_input_files: bool = Field(
        default=True,
        description="Whether to delete input files after successful processing",
    )
    process_existing_on_startup: bool = Field(
        default=True,
        description="Process unprocessed existing files when monitor starts",
    )


class OutputSettings(BaseModel):
    """Output settings."""

    output_format: str = Field(default="markdown", description="Default output format")
    output_directory: Path = Field(
        default=Path("/app/bolus"), description="Output directory"
    )

    @validator("output_directory")
    def validate_output_directory(cls, v):
        """Ensure output directory is absolute."""
        if not v.is_absolute():
            return Path("/app") / v
        return v


class Settings(BaseModel):
    """Main application settings."""

    # Default LLM settings
    llm: LLMSettings = Field(default_factory=LLMSettings)

    # API settings
    api: APISettings = Field(default_factory=APISettings)

    # File monitoring settings
    file_monitor: FileMonitorSettings = Field(default_factory=FileMonitorSettings)

    # Output settings
    output: OutputSettings = Field(default_factory=OutputSettings)

    # Folder configurations
    folders: Dict[str, FolderConfig] = Field(default_factory=dict)

    # Provider-specific base URLs
    provider_base_urls: Dict[str, str] = Field(default_factory=dict)


class ConfigManager:
    """Manages configuration loading from config.ini file."""

    def __init__(self, config_path: Path = Path("/app/config/config.ini")):
        self.config_path = config_path
        self.parser = configparser.ConfigParser()

    def load_config(self) -> Settings:
        """Load configuration from config.ini file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        self.parser.read(self.config_path)

        # Load default LLM settings
        llm_settings = self._load_llm_settings()

        # Load API settings
        api_settings = self._load_api_settings()

        # Load file monitor settings
        file_monitor_settings = self._load_file_monitor_settings()

        # Load output settings
        output_settings = self._load_output_settings()

        # Load folder configurations
        folder_configs = self._load_folder_configs()

        # Load provider base URLs
        provider_base_urls = self._load_provider_base_urls()

        return Settings(
            llm=llm_settings,
            api=api_settings,
            file_monitor=file_monitor_settings,
            output=output_settings,
            folders=folder_configs,
            provider_base_urls=provider_base_urls,
        )

    def _load_llm_settings(self) -> LLMSettings:
        """Load LLM settings from config."""
        default_section = self.parser["DEFAULT"]
        provider_name = self.parser["DEFAULT"].get("provider", "openrouter")
        provider_section = (
            self.parser[provider_name] if provider_name in self.parser else {}
        )

        # Get API key from environment
        provider = default_section.get("provider", "openrouter")
        api_key = self._get_api_key_from_env(provider)

        return LLMSettings(
            provider=provider,
            model=default_section.get("model", "google/gemini-2.5-flash-lite"),
            base_url=default_section.get("base_url") or provider_section.get("base_url", "https://openrouter.ai/api/v1"),
            api_key=api_key,
            temperature=float(default_section.get("temperature", "0.7")),
            max_tokens=int(default_section.get("max_tokens", "2048")),
            top_p=float(default_section.get("top_p", "0.9")),
            thinking_enabled=default_section.getboolean("thinking_enabled", False),
            search_enabled=default_section.getboolean("search_enabled", False),
            retry_attempts=int(default_section.get("retry_attempts", "3")),
            retry_delay=int(default_section.get("retry_delay", "2")),
            http_referer=provider_section.get("http_referer"),
            x_title=provider_section.get("x_title"),
        )

    def _get_api_key_from_env(self, provider: str) -> str:
        """Get API key from environment variables."""
        env_var_map = {
            "openrouter": "OPENROUTER_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "zai": "ZAI_API_KEY",
        }

        env_var = env_var_map.get(provider, "OPENROUTER_API_KEY")
        api_key = os.getenv(env_var)

        if not api_key:
            raise ValueError(f"API key not found in environment variable: {env_var}")

        return api_key

    def _load_api_settings(self) -> APISettings:
        """Load API settings from config."""
        default_section = self.parser["DEFAULT"]

        return APISettings(
            host=default_section.get("api_host", "0.0.0.0"),
            port=int(default_section.get("api_port", "8000")),
            workers=int(default_section.get("api_workers", "1")),
        )

    def _load_file_monitor_settings(self) -> FileMonitorSettings:
        """Load file monitoring settings from config."""
        default_section = self.parser["DEFAULT"]

        return FileMonitorSettings(
            monitor_interval=int(default_section.get("monitor_interval", "5")),
            file_timeout=int(default_section.get("file_timeout", "30")),
            delete_input_files=default_section.getboolean("delete_input_files", True),
        )

    def _load_output_settings(self) -> OutputSettings:
        """Load output settings from config."""
        default_section = self.parser["DEFAULT"]

        return OutputSettings(
            output_format=default_section.get("output_format", "markdown"),
            output_directory=Path(
                default_section.get("output_directory", "/app/bolus")
            ),
        )

    def _load_folder_configs(self) -> Dict[str, FolderConfig]:
        """Load folder configurations from config."""
        folder_configs = {}

        for section_name in self.parser.sections():
            # Skip provider-specific sections
            if section_name in ["openrouter", "openai", "gemini", "deepseek", "zai"]:
                continue

            section = self.parser[section_name]

            # Load all folder configurations, both enabled and disabled
            enabled = section.getboolean("enabled", False)

            # Skip sections without input_directory (not routine configs)
            if not section.get("input_directory"):
                continue

            folder_configs[section_name] = FolderConfig(
                name=section_name,
                input_directory=Path(section.get("input_directory", "")),
                enabled=enabled,
                system_prompt=section.get("system_prompt", ""),
                user_prompt_template=section.get("user_prompt_template", ""),
                provider=section.get("provider", "openrouter"),
                model=section.get("model", "google/gemini-2.5-flash-lite"),
                temperature=float(section.get("temperature", "0.7")),
                max_tokens=int(section.get("max_tokens", "2048")),
                output_format=section.get("output_format", "markdown"),
                output_directory=Path(section["output_directory"])
                if section.get("output_directory")
                else None,
                prompt_files=PromptFileConfig(
                    system_prompt_file=Path(section["system_prompt_file"])
                    if section.get("system_prompt_file")
                    else None,
                    user_prompt_file=Path(section["user_prompt_file"])
                    if section.get("user_prompt_file")
                    else None,
                ),
                delete_input_files=section.getboolean("delete_input_files", None)
                if section.get("delete_input_files") is not None
                else None,
                rejection_trigger_words=self._parse_rejection_trigger_words(section.get("rejection_trigger_words")),
                append_input_to_output=section.getboolean("append_input_to_output", None)
                if section.get("append_input_to_output") is not None
                else None,
            )

        return folder_configs

    def _parse_rejection_trigger_words(self, value: Optional[str]) -> Optional[List[str]]:
        """Parse rejection trigger words from config string.

        Args:
            value: Comma-separated string of trigger words

        Returns:
            List of trigger words or None
        """
        if not value:
            return None

        words = [w.strip().lower() for w in value.split(",") if w.strip()]
        return words if words else None

    def _load_provider_base_urls(self) -> Dict[str, str]:
        """Load provider-specific base URLs from config."""
        provider_base_urls = {}

        for section_name in self.parser.sections():
            # Only process provider-specific sections
            if section_name in ["openrouter", "openai", "gemini", "deepseek", "zai"]:
                section = self.parser[section_name]
                base_url = section.get("base_url")
                if base_url:
                    provider_base_urls[section_name] = base_url

        return provider_base_urls


# Global settings instance
settings: Optional[Settings] = None


def get_settings(force_reload: bool = False) -> Settings:
    """Get the global settings instance.

    Args:
        force_reload: If True, reload the config from disk even if cached
    """
    global settings
    if settings is None or force_reload:
        config_manager = ConfigManager()
        settings = config_manager.load_config()
    return settings
