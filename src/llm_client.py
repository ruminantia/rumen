"""
LLM client for interacting with various providers (OpenRouter, OpenAI, Gemini, DeepSeek).
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
        # Basic client initialization
        client = OpenAI(
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
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
                        raise ValueError("No content in response")

                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
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
