"""
Anthropic Claude Provider Plugin

A plugin implementation for Anthropic Claude API integration.
"""
import logging
from typing import Optional, List
import anthropic

from ..base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse

logger = logging.getLogger(__name__)

# Plugin metadata
PLUGIN_METADATA = {
    "name": "Anthropic Claude Provider",
    "version": "1.0.0",
    "author": "AI-Ticker Team",
    "description": "Official Anthropic Claude API provider plugin",
    "requires": ["anthropic>=0.34.0"],
    "category": "official",
    "api_version": "v1",
    "supported_features": ["chat_completion", "streaming", "vision"]
}


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude API provider implementation."""
    
    @property
    def provider_name(self) -> str:
        """Return the name of this provider."""
        return "Anthropic"
    
    @property
    def supported_models(self) -> List[str]:
        """Return a list of models supported by Anthropic."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    def initialize(self) -> bool:
        """Initialize the Anthropic provider."""
        try:
            if not self.validate_config():
                return False
                
            # Initialize Anthropic client
            self._client = anthropic.Anthropic(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            
            self.logger.info(f"Initialized Anthropic provider with model: {self.config.model}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Anthropic provider: {e}")
            return False
    
    def generate_message(self, system_prompt: str, user_prompt: str) -> Optional[AIResponse]:
        """Generate a message using Anthropic Claude API."""
        if not self._client:
            self.logger.error("Provider not initialized")
            return None
            
        try:
            response = self._client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            content = response.content[0].text if response.content else ""
            
            usage_info = {
                "prompt_tokens": response.usage.input_tokens if response.usage else 0,
                "completion_tokens": response.usage.output_tokens if response.usage else 0,
                "total_tokens": (response.usage.input_tokens + response.usage.output_tokens) if response.usage else 0
            }
            
            metadata = {
                "response_id": response.id,
                "model": response.model,
                "stop_reason": response.stop_reason,
                "stop_sequence": response.stop_sequence
            }
            
            return AIResponse(
                content=content,
                provider_name=self.provider_name,
                model=self.config.model,
                usage=usage_info,
                metadata=metadata
            )
            
        except anthropic.APIError as e:
            self.logger.error(f"Anthropic API error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in Anthropic provider: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check if Anthropic API is accessible."""
        if not self._client:
            return False
            
        try:
            # Make a minimal request to test connectivity
            response = self._client.messages.create(
                model=self.config.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception as e:
            self.logger.error(f"Anthropic health check failed: {e}")
            return False
    
    def validate_config(self) -> bool:
        """Validate Anthropic-specific configuration."""
        if not super().validate_config():
            return False
            
        if not self.config.api_key:
            self.logger.error("Anthropic API key is required")
            return False
            
        if self.config.model not in self.supported_models:
            self.logger.warning(f"Model {self.config.model} not in supported models list")
            
        return True


# Create the plugin instance
AnthropicPlugin = AIProviderPlugin(
    provider_class=AnthropicProvider,
    metadata=PLUGIN_METADATA
)
