"""
Plugin Registry for AI-Ticker Plugin System

This module provides the plugin registry functionality for storing and
managing registered AI provider plugins.
"""
import logging
from typing import Dict, Optional, List, Any
from threading import RLock

from .base_provider import AIProviderPlugin

logger = logging.getLogger(__name__)


class PluginRegistry:
    """
    Thread-safe registry for AI provider plugins.
    
    Manages the registration, storage, and retrieval of plugins with
    thread safety for concurrent access.
    """
    
    def __init__(self):
        """Initialize the plugin registry."""
        self._plugins: Dict[str, AIProviderPlugin] = {}
        self._lock = RLock()  # Reentrant lock for thread safety
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def register_plugin(self, name: str, plugin: AIProviderPlugin) -> bool:
        """
        Register a plugin in the registry.
        
        Args:
            name: Unique name for the plugin
            plugin: Plugin instance to register
            
        Returns:
            True if registration was successful, False if name conflicts
        """
        with self._lock:
            if name in self._plugins:
                self.logger.warning(f"Plugin {name} is already registered")
                return False
                
            self._plugins[name] = plugin
            self.logger.info(f"Registered plugin: {name}")
            return True
            
    def unregister_plugin(self, name: str) -> bool:
        """
        Unregister a plugin from the registry.
        
        Args:
            name: Name of the plugin to unregister
            
        Returns:
            True if unregistration was successful, False if not found
        """
        with self._lock:
            if name not in self._plugins:
                self.logger.warning(f"Plugin {name} is not registered")
                return False
                
            del self._plugins[name]
            self.logger.info(f"Unregistered plugin: {name}")
            return True
            
    def get_plugin(self, name: str) -> Optional[AIProviderPlugin]:
        """
        Get a registered plugin by name.
        
        Args:
            name: Name of the plugin to retrieve
            
        Returns:
            Plugin instance or None if not found
        """
        with self._lock:
            return self._plugins.get(name)
            
    def is_registered(self, name: str) -> bool:
        """
        Check if a plugin is registered.
        
        Args:
            name: Name of the plugin to check
            
        Returns:
            True if plugin is registered, False otherwise
        """
        with self._lock:
            return name in self._plugins
            
    def get_all_plugins(self) -> Dict[str, AIProviderPlugin]:
        """
        Get all registered plugins.
        
        Returns:
            Dictionary of all registered plugins (copy)
        """
        with self._lock:
            return self._plugins.copy()
            
    def get_plugin_names(self) -> List[str]:
        """
        Get names of all registered plugins.
        
        Returns:
            List of plugin names
        """
        with self._lock:
            return list(self._plugins.keys())
            
    def count(self) -> int:
        """
        Get the number of registered plugins.
        
        Returns:
            Number of registered plugins
        """
        with self._lock:
            return len(self._plugins)
            
    def clear(self) -> None:
        """Clear all registered plugins."""
        with self._lock:
            count = len(self._plugins)
            self._plugins.clear()
            self.logger.info(f"Cleared {count} plugins from registry")
            
    def find_by_provider_class(self, provider_class_name: str) -> List[str]:
        """
        Find plugins by provider class name.
        
        Args:
            provider_class_name: Name of the provider class to search for
            
        Returns:
            List of plugin names that use the specified provider class
        """
        with self._lock:
            matches = []
            for name, plugin in self._plugins.items():
                if plugin.provider_class.__name__ == provider_class_name:
                    matches.append(name)
            return matches
            
    def get_plugins_by_metadata(self, key: str, value: Any) -> List[str]:
        """
        Find plugins by metadata key-value pair.
        
        Args:
            key: Metadata key to search for
            value: Expected value for the metadata key
            
        Returns:
            List of plugin names that match the metadata criteria
        """
        with self._lock:
            matches = []
            for name, plugin in self._plugins.items():
                if plugin.metadata.get(key) == value:
                    matches.append(name)
            return matches
            
    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get information about the registry state.
        
        Returns:
            Dictionary with registry statistics and information
        """
        with self._lock:
            plugin_info = {}
            for name, plugin in self._plugins.items():
                plugin_info[name] = {
                    "provider_class": plugin.provider_class.__name__,
                    "version": plugin.version,
                    "author": plugin.author,
                    "description": plugin.description
                }
                
            return {
                "total_plugins": len(self._plugins),
                "plugin_names": list(self._plugins.keys()),
                "plugins": plugin_info
            }
            
    def validate_registry(self) -> Dict[str, List[str]]:
        """
        Validate all registered plugins.
        
        Returns:
            Dictionary with validation results (valid/invalid plugin lists)
        """
        valid_plugins = []
        invalid_plugins = []
        
        with self._lock:
            for name, plugin in self._plugins.items():
                try:
                    # Basic validation checks
                    if not plugin.provider_class:
                        invalid_plugins.append(f"{name}: No provider class")
                        continue
                        
                    if not hasattr(plugin.provider_class, 'provider_name'):
                        invalid_plugins.append(f"{name}: Missing provider_name property")
                        continue
                        
                    if not hasattr(plugin.provider_class, 'supported_models'):
                        invalid_plugins.append(f"{name}: Missing supported_models property")
                        continue
                        
                    # Check required methods
                    required_methods = ['initialize', 'generate_message', 'health_check']
                    for method in required_methods:
                        if not hasattr(plugin.provider_class, method):
                            invalid_plugins.append(f"{name}: Missing {method} method")
                            break
                    else:
                        valid_plugins.append(name)
                        
                except Exception as e:
                    invalid_plugins.append(f"{name}: Validation error: {e}")
                    
        return {
            "valid": valid_plugins,
            "invalid": invalid_plugins
        }
        
    def export_registry(self) -> Dict[str, Any]:
        """
        Export registry state for serialization.
        
        Returns:
            Serializable dictionary representation of the registry
        """
        with self._lock:
            export_data = {
                "version": "1.0.0",
                "plugins": {}
            }
            
            for name, plugin in self._plugins.items():
                export_data["plugins"][name] = {
                    "provider_class_name": plugin.provider_class.__name__,
                    "version": plugin.version,
                    "author": plugin.author,
                    "description": plugin.description,
                    "metadata": plugin.metadata,
                    "requires": plugin.requires
                }
                
            return export_data
            
    def get_plugin_dependencies(self, plugin_name: str) -> List[str]:
        """
        Get dependencies for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to get dependencies for
            
        Returns:
            List of dependency names
        """
        with self._lock:
            plugin = self._plugins.get(plugin_name)
            if not plugin:
                return []
            return plugin.requires.copy() if plugin.requires else []
            
    def check_dependencies(self, plugin_name: str) -> Dict[str, bool]:
        """
        Check if all dependencies for a plugin are satisfied.
        
        Args:
            plugin_name: Name of the plugin to check dependencies for
            
        Returns:
            Dictionary mapping dependency names to availability status
        """
        dependencies = self.get_plugin_dependencies(plugin_name)
        
        with self._lock:
            dependency_status = {}
            for dep in dependencies:
                dependency_status[dep] = dep in self._plugins
                
            return dependency_status
            
    def get_dependent_plugins(self, plugin_name: str) -> List[str]:
        """
        Get list of plugins that depend on the specified plugin.
        
        Args:
            plugin_name: Name of the plugin to check dependents for
            
        Returns:
            List of plugin names that depend on the specified plugin
        """
        with self._lock:
            dependents = []
            for name, plugin in self._plugins.items():
                if plugin.requires and plugin_name in plugin.requires:
                    dependents.append(name)
            return dependents
        
    def validate_plugin(self, plugin: AIProviderPlugin) -> bool:
        """
        Validate a single plugin.
        
        Args:
            plugin: Plugin to validate
            
        Returns:
            True if plugin is valid, False otherwise
        """
        try:
            # Check if plugin has required attributes
            if not plugin.provider_class:
                self.logger.error("Plugin missing provider_class")
                return False
                
            if not plugin.metadata:
                self.logger.error("Plugin missing metadata")
                return False
                
            # Check required metadata fields
            required_metadata = ['name', 'version', 'author', 'description']
            for field in required_metadata:
                if field not in plugin.metadata:
                    self.logger.error(f"Plugin missing required metadata field: {field}")
                    return False
                    
            # Check if provider class has required attributes
            if not hasattr(plugin.provider_class, 'provider_name'):
                self.logger.error("Provider class missing provider_name property")
                return False
                
            if not hasattr(plugin.provider_class, 'supported_models'):
                self.logger.error("Provider class missing supported_models property")
                return False
                
            # Check required methods
            required_methods = ['initialize', 'generate_message', 'health_check']
            for method in required_methods:
                if not hasattr(plugin.provider_class, method):
                    self.logger.error(f"Provider class missing required method: {method}")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Plugin validation error: {e}")
            return False
