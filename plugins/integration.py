"""
Plugin Integration Utilities

This module provides utilities to integrate the plugin system with the
existing AI-Ticker application.
"""
import os
import logging
from typing import Dict, List, Optional, Any

from .plugin_manager import PluginManager
from .base_provider import ProviderConfig, BaseAIProvider
from .builtin import OpenRouterPlugin, TogetherPlugin, DeepInfraPlugin

logger = logging.getLogger(__name__)


class PluginIntegration:
    """
    Integration layer between the plugin system and the main application.
    
    Provides backward compatibility and seamless integration with existing
    provider configuration.
    """
    
    def __init__(self, config_dict: Dict[str, Any]):
        """
        Initialize plugin integration.
        
        Args:
            config_dict: Configuration dictionary from the main app
        """
        self.config = config_dict
        self.plugin_manager = PluginManager()
        self.providers = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Register built-in plugins
        self._register_builtin_plugins()
        
        # Load and create providers from config
        self._initialize_providers()
        
    def _register_builtin_plugins(self) -> None:
        """Register the built-in provider plugins."""
        builtin_plugins = {
            "openrouter": OpenRouterPlugin,
            "together": TogetherPlugin,
            "deepinfra": DeepInfraPlugin
        }
        
        for name, plugin in builtin_plugins.items():
            try:
                self.plugin_manager.get_registry().register_plugin(name, plugin)
                self.logger.info(f"Registered built-in plugin: {name}")
            except Exception as e:
                self.logger.error(f"Failed to register built-in plugin {name}: {e}")
                
    def _initialize_providers(self) -> None:
        """Initialize providers based on existing configuration."""
        # Convert legacy provider config to plugin-based providers
        legacy_providers = self.config.get('providers', [])
        
        for provider_config in legacy_providers:
            provider_name = provider_config.get('name', '').lower()
            
            # Map legacy provider names to plugin names
            plugin_name = self._map_legacy_to_plugin(provider_name)
            
            if plugin_name:
                try:
                    provider = self._create_provider_from_config(plugin_name, provider_config)
                    if provider:
                        self.providers[provider_name] = provider
                        self.logger.info(f"Initialized provider: {provider_name}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize provider {provider_name}: {e}")
                    
    def _map_legacy_to_plugin(self, provider_name: str) -> Optional[str]:
        """Map legacy provider names to plugin names."""
        mapping = {
            "openrouter": "openrouter",
            "together": "together",
            "deepinfra": "deepinfra"
        }
        return mapping.get(provider_name)
        
    def _create_provider_from_config(self, plugin_name: str, config_dict: Dict[str, Any]) -> Optional[BaseAIProvider]:
        """Create a provider instance from configuration."""
        try:
            # Create provider config
            provider_config = ProviderConfig(
                name=config_dict.get('name', plugin_name),
                api_key=config_dict.get('api_key', ''),
                base_url=config_dict.get('base_url', ''),
                model=config_dict.get('model', ''),
                timeout=config_dict.get('timeout', 30),
                max_tokens=config_dict.get('max_tokens', 512),
                extra_params=config_dict.get('extra_params', {})
            )
            
            # Create provider using plugin manager
            provider = self.plugin_manager.create_provider(plugin_name, provider_config)
            
            if provider and provider.initialize():
                return provider
            else:
                self.logger.error(f"Failed to initialize provider from plugin {plugin_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating provider from plugin {plugin_name}: {e}")
            return None
            
    def get_providers(self) -> Dict[str, BaseAIProvider]:
        """Get all initialized providers."""
        return self.providers.copy()
        
    def get_provider(self, name: str) -> Optional[BaseAIProvider]:
        """Get a specific provider by name."""
        return self.providers.get(name.lower())
        
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return list(self.providers.keys())
        
    def add_custom_provider(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """
        Add a custom provider from a loaded plugin.
        
        Args:
            plugin_name: Name of the plugin to use
            config: Configuration for the provider
            
        Returns:
            True if provider was added successfully
        """
        try:
            provider_config = ProviderConfig(
                name=config.get('name', plugin_name),
                api_key=config.get('api_key', ''),
                base_url=config.get('base_url', ''),
                model=config.get('model', ''),
                timeout=config.get('timeout', 30),
                max_tokens=config.get('max_tokens', 512),
                extra_params=config.get('extra_params', {})
            )
            
            provider = self.plugin_manager.create_provider(plugin_name, provider_config)
            
            if provider and provider.initialize():
                self.providers[config['name']] = provider
                self.logger.info(f"Added custom provider: {config['name']}")
                return True
            else:
                self.logger.error(f"Failed to initialize custom provider {config['name']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error adding custom provider: {e}")
            return False
            
    def reload_providers(self) -> None:
        """Reload all providers."""
        self.providers.clear()
        self._initialize_providers()
        
    def get_plugin_manager(self) -> PluginManager:
        """Get the plugin manager instance."""
        return self.plugin_manager
        
    def health_check_all(self) -> Dict[str, bool]:
        """Perform health check on all providers."""
        results = {}
        for name, provider in self.providers.items():
            try:
                results[name] = provider.health_check()
            except Exception as e:
                self.logger.error(f"Health check failed for {name}: {e}")
                results[name] = False
        return results
        
    def get_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all providers."""
        info = {}
        for name, provider in self.providers.items():
            try:
                info[name] = provider.get_info()
            except Exception as e:
                self.logger.error(f"Failed to get info for provider {name}: {e}")
                info[name] = {"error": str(e)}
        return info


def create_plugin_integration(config_dict: Dict[str, Any]) -> PluginIntegration:
    """
    Factory function to create plugin integration.
    
    Args:
        config_dict: Configuration dictionary from main app
        
    Returns:
        Initialized PluginIntegration instance
    """
    return PluginIntegration(config_dict)


def load_providers_from_env() -> Dict[str, Any]:
    """
    Load provider configuration from environment variables.
    
    Returns:
        Configuration dictionary compatible with PluginIntegration
    """
    providers = []
    
    # OpenRouter
    if os.getenv("OPENROUTER_API_KEY"):
        providers.append({
            "name": "OpenRouter",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "base_url": "https://openrouter.ai/api/v1",
            "model": "openai/gpt-4o"
        })
    
    # Together AI
    if os.getenv("TOGETHER_API_KEY"):
        providers.append({
            "name": "Together",
            "api_key": os.getenv("TOGETHER_API_KEY"),
            "base_url": "https://api.together.xyz/v1",
            "model": "meta-llama/Llama-3.1-70B-Instruct-Turbo"
        })
    
    # DeepInfra
    if os.getenv("DEEPINFRA_API_KEY"):
        providers.append({
            "name": "DeepInfra",
            "api_key": os.getenv("DEEPINFRA_API_KEY"),
            "base_url": "https://api.deepinfra.com/v1/openai",
            "model": "meta-llama/Meta-Llama-3.1-70B-Instruct"
        })
    
    # Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append({
            "name": "Anthropic",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "base_url": "https://api.anthropic.com",
            "model": "claude-3-5-sonnet-20241022"
        })
    
    # Groq
    if os.getenv("GROQ_API_KEY"):
        providers.append({
            "name": "Groq",
            "api_key": os.getenv("GROQ_API_KEY"),
            "base_url": "https://api.groq.com/openai/v1",
            "model": "llama-3.1-70b-versatile"
        })
    
    # Google Gemini
    if os.getenv("GOOGLE_AI_API_KEY"):
        providers.append({
            "name": "Gemini",
            "api_key": os.getenv("GOOGLE_AI_API_KEY"),
            "base_url": "https://generativelanguage.googleapis.com",
            "model": "gemini-1.5-pro"
        })
    
    # Mistral AI
    if os.getenv("MISTRAL_API_KEY"):
        providers.append({
            "name": "Mistral",
            "api_key": os.getenv("MISTRAL_API_KEY"),
            "base_url": "https://api.mistral.ai",
            "model": "mistral-large-latest"
        })
    
    # You.com
    if os.getenv("YOUCOM_API_KEY"):
        providers.append({
            "name": "You.com",
            "api_key": os.getenv("YOUCOM_API_KEY"),
            "base_url": "https://chat-api.you.com",
            "model": "smart"
        })
    
    return {"providers": providers}
