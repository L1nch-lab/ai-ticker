"""
Groq Provider Plugin

A plugin implementation for Groq API integration.
"""
import logging
from typing import Optional, List
from groq import Groq

from ..base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse

logger = logging.getLogger(__name__)

# Plugin metadata
PLUGIN_METADATA = {
    "name": "Groq Provider",
    "version": "1.0.0",
    "author": "AI-Ticker Team",
    "description": "Official Groq API provider plugin",
    "requires": ["groq>=0.9.0"],
    "category": "official",
    "api_version": "v1",
    "supported_features": ["chat_completion", "streaming", "fast_inference"]
}


class GroqProvider(BaseAIProvider):
    """Groq API provider implementation."""
    
    @property
    def provider_name(self) -> str:
        """Return the name of this provider."""
        return "Groq"
    
    @property
    def supported_models(self) -> List[str]:
        """Return a list of models supported by Groq."""
        return [
            "llama-3.1-405b-reasoning",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "llama3-groq-70b-8192-tool-use-preview",
            "llama3-groq-8b-8192-tool-use-preview",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
            "gemma-7b-it"
        ]
    
    def initialize(self) -> bool:
        """Initialize the Groq provider."""
        try:
            if not self.validate_config():
                return False
                
            # Initialize Groq client
            self._client = Groq(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            
            self.logger.info(f"Initialized Groq provider with model: {self.config.model}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Groq provider: {e}")
            return False
    
    def generate_message(self, system_prompt: str, user_prompt: str) -> Optional[AIResponse]:
        """Generate a message using Groq API."""
        if not self._client:
            self.logger.error("Provider not initialized")
            return None
            
        try:
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
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
            self.logger.error(f"Error in Groq provider: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check if Groq API is accessible."""
        if not self._client:
            return False
            
        try:
            # Make a minimal request to test connectivity
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            self.logger.error(f"Groq health check failed: {e}")
            return False
    
    def validate_config(self) -> bool:
        """Validate Groq-specific configuration."""
        if not super().validate_config():
            return False
            
        if self.config.model not in self.supported_models:
            self.logger.warning(f"Model {self.config.model} not in supported models list")
            
        return True


# Create the plugin instance
GroqPlugin = AIProviderPlugin(
    provider_class=GroqProvider,
    metadata=PLUGIN_METADATA
)
