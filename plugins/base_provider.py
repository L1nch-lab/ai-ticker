"""
Base Provider Interface for AI-Ticker Plugin System

This module defines the abstract base class that all AI provider plugins must implement.
"""
import abc
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for an AI provider."""
    name: str
    api_key: str
    base_url: str
    model: str
    timeout: int = 30
    max_tokens: int = 512
    temperature: float = 0.7
    extra_params: Dict[str, Any] = None
    extra_headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}
        if self.extra_headers is None:
            self.extra_headers = {}


@dataclass
class AIResponse:
    """Standardized response from an AI provider."""
    content: str
    provider_name: str
    model: str
    usage: Dict[str, int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.usage is None:
            self.usage = {}
        if self.metadata is None:
            self.metadata = {}


class BaseAIProvider(abc.ABC):
    """
    Abstract base class for AI providers.
    
    All custom AI provider plugins must inherit from this class and implement
    the required methods.
    """
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._client = None
        
    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider."""
        pass
    
    @property
    @abc.abstractmethod
    def supported_models(self) -> List[str]:
        """Return a list of models supported by this provider."""
        pass
    
    @abc.abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the provider with its configuration.
        
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        pass
    
    @abc.abstractmethod
    def generate_message(self, system_prompt: str, user_prompt: str) -> Optional[AIResponse]:
        """
        Generate a message using the AI provider.
        
        Args:
            system_prompt: The system/instruction prompt
            user_prompt: The user's prompt/query
            
        Returns:
            AIResponse: The response from the AI provider, or None if failed
        """
        pass
    
    @abc.abstractmethod
    def health_check(self) -> bool:
        """
        Check if the provider is healthy and accessible.
        
        Returns:
            bool: True if the provider is healthy, False otherwise.
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Validate the provider configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        if not self.config.name:
            self.logger.error("Provider name is required")
            return False
            
        if not self.config.api_key:
            self.logger.error("API key is required")
            return False
            
        if not self.config.model:
            self.logger.error("Model is required")
            return False
            
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": self.provider_name,
            "config_name": self.config.name,
            "model": self.config.model,
            "supported_models": self.supported_models,
            "base_url": self.config.base_url,
            "timeout": self.config.timeout,
            "max_tokens": self.config.max_tokens
        }


class AIProviderPlugin:
    """
    Plugin wrapper for AI providers.
    
    This class wraps BaseAIProvider implementations and provides additional
    metadata and lifecycle management.
    """
    
    def __init__(self, provider_class: type, metadata: Dict[str, Any] = None):
        self.provider_class = provider_class
        self.metadata = metadata or {}
        self.version = self.metadata.get('version', '1.0.0')
        self.author = self.metadata.get('author', 'Unknown')
        self.description = self.metadata.get('description', 'Custom AI Provider')
        self.requires = self.metadata.get('requires', [])
        
    def create_provider(self, config: ProviderConfig) -> BaseAIProvider:
        """Create an instance of the provider with the given configuration."""
        return self.provider_class(config)
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "provider_class": self.provider_class.__name__,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "requires": self.requires,
            "metadata": self.metadata
        }
