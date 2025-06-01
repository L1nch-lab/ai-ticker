"""
Google Gemini Provider Plugin

A plugin implementation for Google Gemini API integration.
"""
import logging
from typing import Optional, List
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from ..base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse

logger = logging.getLogger(__name__)

# Plugin metadata
PLUGIN_METADATA = {
    "name": "Google Gemini Provider",
    "version": "1.0.0",
    "author": "AI-Ticker Team",
    "description": "Official Google Gemini API provider plugin",
    "requires": ["google-generativeai>=0.8.0"],
    "category": "official",
    "api_version": "v1",
    "supported_features": ["chat_completion", "streaming", "vision", "multimodal"]
}


class GeminiProvider(BaseAIProvider):
    """Google Gemini API provider implementation."""
    
    @property
    def provider_name(self) -> str:
        """Return the name of this provider."""
        return "Google"
    
    @property
    def supported_models(self) -> List[str]:
        """Return a list of models supported by Google Gemini."""
        return [
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.0-pro",
            "gemini-1.0-pro-latest"
        ]
    
    def initialize(self) -> bool:
        """Initialize the Google Gemini provider."""
        try:
            if not self.validate_config():
                return False
                
            # Configure Gemini API
            genai.configure(api_key=self.config.api_key)
            
            # Initialize the model
            self._model = genai.GenerativeModel(
                model_name=self.config.model,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                ),
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )
            
            self.logger.info(f"Initialized Google Gemini provider with model: {self.config.model}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Gemini provider: {e}")
            return False
    
    def generate_message(self, system_prompt: str, user_prompt: str) -> Optional[AIResponse]:
        """Generate a message using Google Gemini API."""
        if not self._model:
            self.logger.error("Provider not initialized")
            return None
            
        try:
            # Combine system and user prompts for Gemini
            full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
            
            response = self._model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                )
            )
            
            content = response.text if response.text else ""
            
            # Extract usage information if available
            usage_info = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage_info = {
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "completion_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count
                }
            
            metadata = {
                "model": self.config.model,
                "finish_reason": response.candidates[0].finish_reason.name if response.candidates and response.candidates[0].finish_reason else None,
                "safety_ratings": [
                    {
                        "category": rating.category.name,
                        "probability": rating.probability.name
                    } for rating in response.candidates[0].safety_ratings
                ] if response.candidates and response.candidates[0].safety_ratings else []
            }
            
            return AIResponse(
                content=content,
                provider_name=self.provider_name,
                model=self.config.model,
                usage=usage_info,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Error in Google Gemini provider: {e}")
            return None
    
    def get_default_config(self) -> dict:
        """Return default configuration for Google Gemini provider."""
        return {
            "model": "gemini-1.5-flash",
            "max_tokens": 512,
            "temperature": 0.7,
            "timeout": 30
        }
    
    def health_check(self) -> bool:
        """Check if Google Gemini API is accessible."""
        if not self._model:
            return False
            
        try:
            # Make a minimal request to test connectivity
            response = self._model.generate_content(
                "Hi",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=10,
                    temperature=0.1,
                )
            )
            return True
        except Exception as e:
            self.logger.error(f"Google Gemini health check failed: {e}")
            return False
    
    def validate_config(self) -> bool:
        """Validate Google Gemini-specific configuration."""
        if not super().validate_config():
            return False
            
        if not self.config.api_key:
            self.logger.error("Google API key is required")
            return False
            
        if self.config.model not in self.supported_models:
            self.logger.warning(f"Model {self.config.model} not in supported models list")
            
        return True


# Create the plugin instance
GeminiPlugin = AIProviderPlugin(
    provider_class=GeminiProvider,
    metadata=PLUGIN_METADATA
)
