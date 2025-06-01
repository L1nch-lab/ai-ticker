"""
You.com Provider Plugin

A plugin implementation for You.com Smart API integration.
"""
import logging
import httpx
from typing import Optional, List

from ..base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse

logger = logging.getLogger(__name__)

# Plugin metadata
PLUGIN_METADATA = {
    "name": "You.com Provider",
    "version": "1.0.0",
    "author": "AI-Ticker Team",
    "description": "Official You.com Smart API provider plugin",
    "requires": ["httpx>=0.27.0"],
    "category": "official",
    "api_version": "v1",
    "supported_features": ["chat_completion", "search_augmented", "citations"]
}


class YouComProvider(BaseAIProvider):
    """You.com Smart API provider implementation."""
    
    @property
    def provider_name(self) -> str:
        """Return the name of this provider."""
        return "You.com"
    
    @property
    def supported_models(self) -> List[str]:
        """Return a list of models supported by You.com."""
        return [
            "smart",  # You.com Smart API model
            "research",  # You.com Research API model
            "default"  # Default You.com model
        ]
    
    def initialize(self) -> bool:
        """Initialize the You.com provider."""
        try:
            if not self.validate_config():
                return False
                
            # Initialize HTTP client with You.com endpoint
            headers = {
                "X-API-Key": self.config.api_key,
                "Content-Type": "application/json",
                "User-Agent": "AI-Ticker/1.1.0"
            }
            
            # Add any extra headers from config
            if self.config.extra_headers:
                headers.update(self.config.extra_headers)
            
            self._client = httpx.Client(
                base_url=self.config.base_url or "https://chat-api.you.com",
                headers=headers,
                timeout=self.config.timeout
            )
            
            self.logger.info(f"Initialized You.com provider with model: {self.config.model}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize You.com provider: {e}")
            return False
    
    def generate_message(self, system_prompt: str, user_prompt: str) -> Optional[AIResponse]:
        """Generate a message using You.com Smart API."""
        if not self._client:
            self.logger.error("Provider not initialized")
            return None
            
        try:
            # Combine system and user prompts for You.com
            combined_query = f"{system_prompt}\n\nQuery: {user_prompt}"
            
            # Prepare the request payload for You.com Smart API
            payload = {
                "query": combined_query,
                "instructions": system_prompt if system_prompt != user_prompt else "Provide a helpful and informative response."
            }
            
            # Add any extra parameters from config
            if self.config.extra_params:
                payload.update(self.config.extra_params)
            
            # Make API request to You.com Smart API
            response = self._client.post("/smart", json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("answer"):
                self.logger.warning("No answer in You.com response")
                return None
                
            content = data["answer"]
            if not content:
                self.logger.warning("Empty content in You.com response")
                return None
            
            # Extract search results and citations if available
            search_results = data.get("search_results", [])
            citations = []
            if search_results:
                citations = [
                    {
                        "url": result.get("url", ""),
                        "title": result.get("name", ""),
                        "snippet": result.get("snippet", "")[:200] + "..." if result.get("snippet", "") else ""
                    }
                    for result in search_results[:3]  # Limit to top 3 citations
                ]
            
            # You.com doesn't provide token usage, so we estimate
            estimated_tokens = len(combined_query.split()) + len(content.split())
            usage = {
                "prompt_tokens": len(combined_query.split()),
                "completion_tokens": len(content.split()),
                "total_tokens": estimated_tokens
            }
            
            # Extract metadata
            metadata = {
                "search_results_count": len(search_results),
                "has_citations": len(citations) > 0,
                "citations": citations,
                "provider_specific": {
                    "youcom_model": self.config.model,
                    "api_endpoint": "smart"
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
            self.logger.error(f"You.com API error: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check if You.com API is accessible."""
        if not self._client:
            return False
            
        try:
            # Make a minimal request to test connectivity
            payload = {
                "query": "Hello",
                "instructions": "Respond with a simple greeting."
            }
            
            response = self._client.post("/smart", json=payload, timeout=10)
            return response.status_code == 200 and bool(response.json().get("answer"))
            
        except Exception as e:
            self.logger.error(f"You.com health check failed: {e}")
            return False
    
    def validate_config(self) -> bool:
        """Validate You.com-specific configuration."""
        if not super().validate_config():
            return False
            
        # Check if model is in supported list (warning only)
        if self.config.model not in self.supported_models:
            self.logger.warning(
                f"Model {self.config.model} not in known supported models list. "
                f"This may still work if it's available on You.com."
            )
            
        # Validate base URL
        if self.config.base_url and not self.config.base_url.startswith(('http://', 'https://')):
            self.logger.error("You.com base_url must start with http:// or https://")
            return False
            
        # Check API key format (You.com uses X-API-Key header)
        if not self.config.api_key or len(self.config.api_key) < 10:
            self.logger.error("You.com API key appears to be invalid or too short")
            return False
            
        return True


# Create the plugin instance
YouComPlugin = AIProviderPlugin(
    provider_class=YouComProvider,
    metadata=PLUGIN_METADATA
)
