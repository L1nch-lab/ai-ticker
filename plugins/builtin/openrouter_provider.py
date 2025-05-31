"""
OpenRouter AI Provider Plugin

A plugin implementation for OpenRouter API integration.
"""
import logging
from typing import Optional, List
from openai import OpenAI

from ..base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse

logger = logging.getLogger(__name__)

# Plugin metadata
PLUGIN_METADATA = {
    "name": "OpenRouter Provider",
    "version": "1.0.0",
    "author": "AI-Ticker Team",
    "description": "Official OpenRouter API provider plugin",
    "requires": ["openai>=1.14.3"],
    "category": "official",
    "api_version": "v1",
    "supported_features": ["chat_completion", "streaming", "function_calling"]
}


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter API provider implementation."""
    
    @property
    def provider_name(self) -> str:
        """Return the name of this provider."""
        return "OpenRouter"
    
    @property
    def supported_models(self) -> List[str]:
        """Return a list of popular models supported by OpenRouter."""
        return [
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "openai/gpt-4-turbo",
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-haiku",
            "meta-llama/llama-3.1-405b-instruct",
            "meta-llama/llama-3.1-70b-instruct",
            "meta-llama/llama-3.1-8b-instruct",
            "google/gemini-pro-1.5",
            "cohere/command-r-plus",
            "mistralai/mistral-large",
            "qwen/qwen-2-72b-instruct"
        ]
    
    def initialize(self) -> bool:
        """Initialize the OpenRouter provider."""
        try:
            if not self.validate_config():
                return False
                
            # Initialize OpenAI client with OpenRouter endpoint
            self._client = OpenAI(
                base_url=self.config.base_url or "https://openrouter.ai/api/v1",
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            
            self.logger.info(f"Initialized OpenRouter provider with model: {self.config.model}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenRouter provider: {e}")
            return False
    
    def generate_message(self, system_prompt: str, user_prompt: str) -> Optional[AIResponse]:
        """Generate a message using OpenRouter API."""
        if not self._client:
            self.logger.error("Provider not initialized")
            return None
            
        try:
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout,
                **self.config.extra_params
            )
            
            if not response.choices:
                self.logger.warning("No choices in OpenRouter response")
                return None
                
            content = response.choices[0].message.content
            if not content:
                self.logger.warning("Empty content in OpenRouter response")
                return None
                
            # Extract usage information
            usage = {}
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
                    "completion_tokens": getattr(response.usage, 'completion_tokens', 0),
                    "total_tokens": getattr(response.usage, 'total_tokens', 0)
                }
            
            # Extract metadata
            metadata = {
                "response_id": getattr(response, 'id', None),
                "created": getattr(response, 'created', None),
                "finish_reason": response.choices[0].finish_reason if response.choices else None
            }
            
            return AIResponse(
                content=content.strip(),
                provider_name=self.provider_name,
                model=self.config.model,
                usage=usage,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"OpenRouter API error: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check if OpenRouter API is accessible."""
        if not self._client:
            return False
            
        try:
            # Make a minimal request to test connectivity
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1,
                timeout=10
            )
            return bool(response.choices)
            
        except Exception as e:
            self.logger.error(f"OpenRouter health check failed: {e}")
            return False
    
    def validate_config(self) -> bool:
        """Validate OpenRouter-specific configuration."""
        if not super().validate_config():
            return False
            
        # Check if model is in supported list (warning only)
        if self.config.model not in self.supported_models:
            self.logger.warning(
                f"Model {self.config.model} not in known supported models list. "
                f"This may still work if it's available on OpenRouter."
            )
            
        # Validate base URL
        if self.config.base_url and not self.config.base_url.startswith(('http://', 'https://')):
            self.logger.error("OpenRouter base_url must start with http:// or https://")
            return False
            
        return True


# Create the plugin instance
OpenRouterPlugin = AIProviderPlugin(
    provider_class=OpenRouterProvider,
    metadata=PLUGIN_METADATA
)
