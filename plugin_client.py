"""
Plugin-Aware AI Provider Client

This module provides an enhanced AI provider client that works with the plugin system
while maintaining backward compatibility with the existing application.
"""
import logging
import secrets
from typing import List, Dict, Any, Optional

from plugins.integration import PluginIntegration, load_providers_from_env
from plugins.base_provider import BaseAIProvider, AIResponse
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)


class PluginAwareAIClient:
    """
    Enhanced AI provider client that uses the plugin system.
    
    Provides backward compatibility while leveraging the new plugin architecture.
    """
    
    def __init__(self, config_dict: Dict[str, Any] = None, timeout: int = 30):
        """
        Initialize the plugin-aware AI client.
        
        Args:
            config_dict: Configuration dictionary (legacy format supported)
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize plugin integration
        try:
            if config_dict is None:
                config_dict = load_providers_from_env()
                
            self.plugin_integration = PluginIntegration(config_dict)
            self.providers = self.plugin_integration.get_providers()
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin integration: {e}")
            self.plugin_integration = None
            self.providers = {}
        
        if not self.providers:
            self.logger.warning("No AI providers available")
        else:
            provider_names = list(self.providers.keys())
            self.logger.info(f"Initialized with providers: {', '.join(provider_names)}")
    
    def get_message(self, system_prompt: str, user_prompt: str,
                    existing_messages: List[str],
                    fuzzy_threshold: int) -> Optional[str]:
        """
        Get a unique message from available providers.
        
        Args:
            system_prompt: System/instruction prompt
            user_prompt: User query/prompt
            existing_messages: List of existing messages to avoid duplicates
            fuzzy_threshold: Similarity threshold for duplicate detection (0-100)
            
        Returns:
            Generated message content or None if all providers fail
        """
        if not self.providers:
            self.logger.warning("No AI providers configured")
            return None
            
        # Try each provider until we get a unique message
        provider_list = list(self.providers.items())
        
        # Randomize provider order to distribute load
        for i in range(len(provider_list)):
            j = secrets.randbelow(len(provider_list))
            provider_list[i], provider_list[j] = provider_list[j], provider_list[i]
            
        for provider_name, provider in provider_list:
            try:
                self.logger.info(f"🔍 Trying provider: {provider_name}")
                
                # Generate message using the provider
                response = provider.generate_message(system_prompt, user_prompt)
                
                if response and response.content:
                    # Check for similarity with existing messages
                    if not self._is_similar(response.content, existing_messages, fuzzy_threshold):
                        self.logger.info(f"✅ Got unique message from {provider_name}")
                        return response.content
                    else:
                        self.logger.info(f"Similar message from {provider_name}, trying next")
                else:
                    self.logger.warning(f"Empty response from {provider_name}")
                    
            except Exception as e:
                self.logger.error(f"❌ Provider {provider_name} failed: {type(e).__name__}: {e}")
                continue
                
        self.logger.warning("All providers failed or returned similar messages")
        return None
    
    def _is_similar(self, new_message: str, existing_messages: List[str], threshold: int) -> bool:
        """
        Check if message is too similar to existing ones.
        
        Args:
            new_message: New message to check
            existing_messages: List of existing messages
            threshold: Similarity threshold (0-100)
            
        Returns:
            True if message is too similar, False otherwise
        """
        for existing in existing_messages:
            similarity = fuzz.ratio(new_message, existing)
            if similarity >= threshold:
                self.logger.debug(f"Similarity {similarity}% >= threshold {threshold}%")
                return True
        return False
    
    def health_check_all(self) -> Dict[str, bool]:
        """
        Check health of all providers.
        
        Returns:
            Dictionary mapping provider names to health status
        """
        health_status = {}
        
        if not self.providers:
            return health_status
            
        for provider_name, provider in self.providers.items():
            try:
                health_status[provider_name] = provider.health_check()
            except Exception as e:
                self.logger.error(f"Health check failed for {provider_name}: {e}")
                health_status[provider_name] = False
                
        return health_status

    def get_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all providers.
        
        Returns:
            Dictionary with provider information
        """
        if not self.plugin_integration:
            # Fallback info if plugin integration failed
            return {name: {"status": "mock", "model": getattr(provider, 'config', {}).get('model', 'unknown')} 
                   for name, provider in self.providers.items()}
        return self.plugin_integration.get_provider_info()
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available provider names.
        
        Returns:
            List of provider names
        """
        if not self.plugin_integration:
            return list(self.providers.keys())
        return self.plugin_integration.get_available_providers()
    
    def add_custom_provider(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """
        Add a custom provider from a plugin.
        
        Args:
            plugin_name: Name of the plugin to use
            config: Provider configuration
            
        Returns:
            True if provider was added successfully
        """
        if not self.plugin_integration:
            self.logger.warning("Cannot add custom provider: plugin integration not available")
            return False
            
        success = self.plugin_integration.add_custom_provider(plugin_name, config)
        if success:
            # Refresh provider list
            self.providers = self.plugin_integration.get_providers()
        return success
    
    def reload_providers(self) -> None:
        """Reload all providers."""
        if not self.plugin_integration:
            self.logger.warning("Cannot reload providers: plugin integration not available")
            return
            
        self.plugin_integration.reload_providers()
        self.providers = self.plugin_integration.get_providers()
        
        provider_names = list(self.providers.keys())
        self.logger.info(f"Reloaded providers: {', '.join(provider_names)}")
    
    def get_plugin_manager(self):
        """Get the underlying plugin manager."""
        if not self.plugin_integration:
            return None
        return self.plugin_integration.get_plugin_manager()


def create_legacy_compatible_client(providers: List[Dict[str, Any]], timeout: int = 30) -> PluginAwareAIClient:
    """
    Create a plugin-aware client from legacy provider configuration.
    
    Args:
        providers: List of provider configurations (legacy format)
        timeout: Request timeout
        
    Returns:
        Configured PluginAwareAIClient instance
    """
    config_dict = {"providers": providers}
    return PluginAwareAIClient(config_dict, timeout)
