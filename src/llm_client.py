"""
LLM client for interacting with various providers (OpenRouter, OpenAI, Gemini, DeepSeek, ZAI/GLM).
"""

import os
import time
from typing import List, Dict, Optional
from openai import OpenAI
import logging

from .config import LLMSettings

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with various LLM providers."""

    def __init__(self, settings: LLMSettings):
        self.settings = settings
        self.client = self._initialize_client()

    def _initialize_client(self) -> OpenAI:
        """Initialize the OpenAI client with provider-specific configuration."""
        # Basic client initialization with retries disabled (we handle retries ourselves)
        client = OpenAI(
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
            max_retries=0,  # Disable built-in retries, we handle them ourselves
        )

        return client

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate a completion using the configured LLM.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt to prepend
            **kwargs: Additional parameters to override default settings

        Returns:
            Generated text content
        """
        try:
            # Prepare messages
            final_messages = []
            if system_prompt:
                final_messages.append({"role": "system", "content": system_prompt})
            final_messages.extend(messages)

            # Prepare completion parameters
            completion_kwargs = {
                "model": self.settings.model,
                "messages": final_messages,
                "temperature": kwargs.get("temperature", self.settings.temperature),
                "max_tokens": kwargs.get("max_tokens", self.settings.max_tokens),
                "top_p": kwargs.get("top_p", self.settings.top_p),
            }

            # Remove None values
            completion_kwargs = {
                k: v for k, v in completion_kwargs.items() if v is not None
            }

            logger.info(f"Generating completion with model: {self.settings.model}")

            # Make the API call with retry logic
            max_retries = self.settings.retry_attempts
            retrying_empty_response = False  # Track if we're retrying after empty response

            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(**completion_kwargs)

                    # Extract the content
                    if response.choices and response.choices[0].message.content:
                        content = response.choices[0].message.content.strip()
                        logger.info(
                            f"Successfully generated completion ({len(content)} characters)"
                        )
                        return content
                    else:
                        # If we got an empty response with an :online model, retry without :online
                        # The search already happened, so we don't need to search again
                        if ":online" in self.settings.model and not retrying_empty_response:
                            logger.warning(
                                "Got empty response from :online model after successful search. "
                                "Retrying without :online to avoid redundant search costs."
                            )
                            completion_kwargs["model"] = self.settings.model.replace(":online", "")
                            retrying_empty_response = True
                            continue  # Retry immediately without delay
                        else:
                            raise ValueError("No content in response")

                except Exception as e:
                    error_str = str(e)
                    logger.warning(f"Attempt {attempt + 1} failed: {error_str}")

                    # Check if it's a rate limit error (429)
                    if "429" in error_str and attempt < max_retries - 1:
                        # Try to extract rate limit reset time from error
                        import re
                        import time as time_module

                        reset_match = re.search(r"'X-RateLimit-Reset':\s*'(\d+)'", error_str)
                        if reset_match:
                            reset_timestamp = int(reset_match.group(1))
                            current_time = time_module.time() * 1000  # Convert to milliseconds
                            wait_seconds = max(1, (reset_timestamp - current_time) / 1000)
                            logger.info(f"Rate limited. Waiting {wait_seconds:.1f} seconds until reset")
                            time.sleep(wait_seconds)
                        else:
                            # Fallback to exponential backoff if we can't parse reset time
                            backoff = self.settings.retry_delay * (2 ** attempt)
                            logger.info(f"Using exponential backoff: waiting {backoff} seconds")
                            time.sleep(backoff)
                    elif attempt < max_retries - 1:
                        # Non-rate-limit errors: use standard retry delay
                        time.sleep(self.settings.retry_delay)
                    else:
                        raise

            raise Exception("All retry attempts failed")

        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise

    def process_content(
        self,
        content: str,
        system_prompt: str,
        user_prompt_template: str = "Process the following content: {content}",
    ) -> str:
        """
        Process content with a specific system prompt and user prompt template.

        Args:
            content: The content to process
            system_prompt: System prompt for the LLM
            user_prompt_template: Template for user prompt with {content} placeholder

        Returns:
            Processed content
        """
        user_prompt = user_prompt_template.format(content=content)

        messages = [
            {
                "role": "user",
                "content": user_prompt,
            }
        ]

        return self.generate_completion(messages, system_prompt)

    def health_check(self) -> bool:
        """
        Perform a health check on the LLM provider.

        Returns:
            True if the provider is healthy, False otherwise
        """
        try:
            # Check if API key is configured
            if not self.settings.api_key:
                return False

            # For health check, just verify the API key is present and base URL looks valid
            # Don't make actual API calls to avoid unnecessary requests and 404 errors
            if self.settings.base_url and self.settings.api_key:
                return True
            return False
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False


class LLMClientFactory:
    """Factory for creating LLM clients based on provider."""

    @staticmethod
    def create_client(settings: LLMSettings) -> LLMClient:
        """
        Create an LLM client for the specified provider.

        Args:
            settings: LLM settings including provider configuration

        Returns:
            Configured LLM client
        """
        return LLMClient(settings)
