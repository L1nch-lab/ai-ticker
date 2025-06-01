"""
Mistral AI Provider Plugin

A plugin implementation for Mistral AI API integration.
"""
import logging
from typing import Optional, List
from mistralai import MistralClient

from ..base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse

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
    "supported_features": ["chat_completion", "streaming", "function_calling"]
}


class MistralProvider(BaseAIProvider):
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
            "open-codestral-mamba"
        ]
    
    def initialize(self) -> bool:
        """Initialize the Mistral AI provider."""
        try:
            if not self.validate_config():
                return False
                
            # Initialize Mistral client
            self._client = MistralClient(
                api_key=self.config.api_key,
                timeout=self.config.timeout
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
                {"role": "user", "content": user_prompt}
            ]
            
            response = self._client.chat.complete(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                stream=False
            )
            
            content = response.choices[0].message.content if response.choices else ""
            
            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
            
            metadata = {
                "response_id": response.id,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason if response.choices else None,
                "created": response.created
            }
            
            return AIResponse(
                content=content,
                provider_name=self.provider_name,
                model=self.config.model,
                usage=usage_info,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Error in Mistral AI provider: {e}")
            return None
    
    def get_default_config(self) -> dict:
        """Return default configuration for Mistral AI provider."""
        return {
            "model": "mistral-large-latest",
            "max_tokens": 512,
            "temperature": 0.7,
            "timeout": 30
        }
    
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
                stream=False
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


# Create the plugin instance
MistralPlugin = AIProviderPlugin(
    provider_class=MistralProvider,
    metadata=PLUGIN_METADATA
)
