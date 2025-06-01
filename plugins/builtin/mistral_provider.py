"""
Mistral AI Provider Plugin

A plugin implementation for Mistral AI API integration.
"""
import os
import logging
from typing import Dict, Any, Optional, List

import httpx  # Added: Import httpx
from mistralai.client import MistralClient
from mistralai.types import ChatMessage  # Changed: Attempt import from mistralai.types

from ..base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse, Message, LLMProviderConfig, LLMProvider  # Added LLMProviderConfig, LLMProvider

logger = logging.getLogger(__name__)

# Plugin metadata
PLUGIN_METADATA = {
    "name": "Mistral AI Provider",
    "version": "1.0.0",
    "author": "AI-Ticker Team",
    "description": "Official Mistral AI API provider plugin",
    "requires": ["mistralai>=1.0.0"],
    "category": "official",
    "api_version": "v1",
    "supported_features": ["chat_completion", "streaming", "function_calling"],
}


class MistralProviderConfig(LLMProviderConfig):  # Ensure this inherits from the imported LLMProviderConfig
    """
    Configuration class for the Mistral provider.
    Inherits from LLMProviderConfig.
    """

    def get_default_config(self) -> dict:
        """Return default configuration for Mistral AI provider."""
        return {
            "model": "mistral-large-latest",
            "max_tokens": 512,
            "temperature": 0.7,
            "timeout": 30,
        }


class MistralProvider(LLMProvider):  # Ensure this inherits from the imported LLMProvider
    """Mistral AI API provider implementation."""

    @property
    def provider_name(self) -> str:
        """Return the name of this provider."""
        return "Mistral"

    @property
    def supported_models(self) -> List[str]:
        """Return a list of models supported by Mistral AI."""
        return [
            "mistral-large-latest",
            "mistral-large-2407",
            "mistral-medium-latest",
            "mistral-small-latest",
            "mistral-small-2409",
            "codestral-latest",
            "codestral-2405",
            "open-mistral-7b",
            "open-mixtral-8x7b",
            "open-mixtral-8x22b",
            "open-codestral-mamba",
        ]

    def initialize(self) -> bool:
        """Initialize the Mistral AI provider."""
        try:
            if not self.validate_config():
                return False

            # Initialize Mistral client
            self._client = MistralClient(
                api_key=self.config.api_key, timeout=self.config.timeout
            )

            self.logger.info(f"Initialized Mistral AI provider with model: {self.config.model}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Mistral AI provider: {e}")
            return False

    def generate_message(self, system_prompt: str, user_prompt: str) -> Optional[AIResponse]:
        """Generate a message using Mistral AI API."""
        if not self._client:
            self.logger.error("Provider not initialized")
            return None

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            response = self._client.chat.complete(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                stream=False,
            )

            content = response.choices[0].message.content if response.choices else ""

            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            }

            metadata = {
                "response_id": response.id,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason if response.choices else None,
                "created": response.created,
            }

            return AIResponse(
                content=content,
                provider_name=self.provider_name,
                model=self.config.model,
                usage=usage_info,
                metadata=metadata,
            )

        except Exception as e:
            self.logger.error(f"Error in Mistral AI provider: {e}")
            return None

    def health_check(self) -> bool:
        """Check if Mistral AI API is accessible."""
        if not self._client:
            return False

        try:
            # Make a minimal request to test connectivity
            messages = [{"role": "user", "content": "Hi"}]
            response = self._client.chat.complete(
                model=self.config.model,
                messages=messages,
                max_tokens=10,
                temperature=0.1,
                stream=False,
            )
            return True
        except Exception as e:
            self.logger.error(f"Mistral AI health check failed: {e}")
            return False

    def validate_config(self) -> bool:
        """Validate Mistral AI-specific configuration."""
        if not super().validate_config():
            return False

        if not self.config.api_key:
            self.logger.error("Mistral AI API key is required")
            return False

        if self.config.model not in self.supported_models:
            self.logger.warning(f"Model {self.config.model} not in supported models list")

        return True

    async def get_response(self, messages: List[Message], max_tokens: Optional[int] = None) -> str:
        """
        Fetches a response from the Mistral API.
        Args:
            messages (List[Message]): A list of message objects (custom Message type from base_provider).
            max_tokens (Optional[int]): The maximum number of tokens for the response.
        Returns:
            str: The AI-generated response.
        """
        if not self.client:
            logger.error("Mistral client not initialized.")
            return "Error: Mistral client not initialized."

        # Convert custom Message objects to Mistral's ChatMessage objects
        formatted_messages = [ChatMessage(role=msg.role, content=msg.content) for msg in messages]

        try:
            # Ensure model_dump is available or use an alternative if not present on ChatMessage
            # For debugging, let's log the type of formatted_messages and its elements
            logger.debug(f"Type of formatted_messages: {type(formatted_messages)}")
            if formatted_messages:
                logger.debug(f"Type of first element in formatted_messages: {type(formatted_messages[0])}")
                # Assuming ChatMessage has 'role' and 'content' attributes for logging
                logger.debug(f"Sending request to Mistral API with model {self.config.model}, messages: {[{'role': msg.role, 'content': msg.content} for msg in formatted_messages]}")
            else:
                logger.debug(f"Sending request to Mistral API with model {self.config.model}, messages: []")
            
            chat_response = await self._run_chat_completion(formatted_messages, max_tokens)

            if chat_response and chat_response.choices:
                response_content = chat_response.choices[0].message.content
                logger.info(f"Received response from Mistral API: {response_content}")
                return response_content
            else:
                logger.warning("No choices found in the response from Mistral API.")
                return "Error: No response from Mistral API."

        except httpx.RequestError as e:
            logger.error(f"HTTP request error while communicating with Mistral API: {e}")
            return f"Error: HTTP request error - {e}"
        except httpx.HTTPStatusError as e:
            logger.error(f"Unexpected HTTP status {e.response.status_code} while communicating with Mistral API.")
            return f"Error: Unexpected HTTP status {e.response.status_code}"
        except Exception as e:
            logger.error(f"An unexpected error occurred while communicating with Mistral API: {e}", exc_info=True)
            return f"Error: An unexpected error occurred with Mistral API."

    async def _run_chat_completion(self, formatted_messages: List[ChatMessage], max_tokens: Optional[int]):
        """Helper to run chat completion, allowing for easier mocking in tests."""
        # Note: Mistral's client might not be async directly.
        # If it's synchronous, this would block. For true async, consider httpx directly
        effective_max_tokens = max_tokens or self.config.max_tokens

        # If MistralClient was imported correctly, this part would be:
        chat_response = self.client.chat(
            model=self.config.model,
            messages=formatted_messages,
            temperature=self.config.temperature,
            max_tokens=effective_max_tokens,
        )
        return chat_response

    def get_config_model(self):
        """
        Get the model configuration.
        Returns:
            dict: The model configuration.
        """
        return {
            "type": "mistral",
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }


# Create the plugin instance
MistralPlugin = AIProviderPlugin(
    provider_class=MistralProvider,
    metadata=PLUGIN_METADATA,
)
