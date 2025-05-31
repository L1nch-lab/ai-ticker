"""
Together AI Provider Plugin

A plugin implementation for Together AI API integration.
"""
import logging
from typing import Optional, List
from openai import OpenAI

from ..base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse

logger = logging.getLogger(__name__)

# Plugin metadata
PLUGIN_METADATA = {
    "name": "Together AI Provider",
    "version": "1.0.0",
    "author": "AI-Ticker Team",
    "description": "Official Together AI API provider plugin",
    "requires": ["openai>=1.14.3"],
    "category": "official",
    "api_version": "v1",
    "supported_features": ["chat_completion", "streaming"]
}


class TogetherProvider(BaseAIProvider):
    """Together AI API provider implementation."""
    
    @property
    def provider_name(self) -> str:
        """Return the name of this provider."""
        return "Together"
    
    @property
    def supported_models(self) -> List[str]:
        """Return a list of popular models supported by Together AI."""
        return [
            "meta-llama/Llama-3.1-405B-Instruct-Turbo",
            "meta-llama/Llama-3.1-70B-Instruct-Turbo",
            "meta-llama/Llama-3.1-8B-Instruct-Turbo",
            "meta-llama/Llama-3-70b-chat-hf",
            "meta-llama/Llama-3-8b-chat-hf",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "mistralai/Mixtral-8x22B-Instruct-v0.1",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
            "Qwen/Qwen2-72B-Instruct",
            "togethercomputer/RedPajama-INCITE-Chat-3B-v1",
            "zero-one-ai/Yi-34B-Chat"
        ]
    
    def initialize(self) -> bool:
        """Initialize the Together AI provider."""
        try:
            if not self.validate_config():
                return False
                
            # Initialize OpenAI client with Together AI endpoint
            self._client = OpenAI(
                base_url=self.config.base_url or "https://api.together.xyz/v1",
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            
            self.logger.info(f"Initialized Together AI provider with model: {self.config.model}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Together AI provider: {e}")
            return False
    
    def generate_message(self, system_prompt: str, user_prompt: str) -> Optional[AIResponse]:
        """Generate a message using Together AI API."""
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
                self.logger.warning("No choices in Together AI response")
                return None
                
            content = response.choices[0].message.content
            if not content:
                self.logger.warning("Empty content in Together AI response")
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
                "finish_reason": response.choices[0].finish_reason if response.choices else None,
                "provider_specific": {
                    "together_model": self.config.model
                }
            }
            
            return AIResponse(
                content=content.strip(),
                provider_name=self.provider_name,
                model=self.config.model,
                usage=usage,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Together AI API error: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check if Together AI API is accessible."""
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
            self.logger.error(f"Together AI health check failed: {e}")
            return False
    
    def validate_config(self) -> bool:
        """Validate Together AI-specific configuration."""
        if not super().validate_config():
            return False
            
        # Check if model is in supported list (warning only)
        if self.config.model not in self.supported_models:
            self.logger.warning(
                f"Model {self.config.model} not in known supported models list. "
                f"This may still work if it's available on Together AI."
            )
            
        # Validate base URL
        if self.config.base_url and not self.config.base_url.startswith(('http://', 'https://')):
            self.logger.error("Together AI base_url must start with http:// or https://")
            return False
            
        return True


# Create the plugin instance
TogetherPlugin = AIProviderPlugin(
    provider_class=TogetherProvider,
    metadata=PLUGIN_METADATA
)
