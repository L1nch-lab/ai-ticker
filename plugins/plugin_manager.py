"""
Plugin Manager for AI-Ticker Plugin System

This module provides the core plugin management functionality including
plugin discovery, loading, registration, and lifecycle management.
"""
import os
import sys
import json
import logging
import importlib
import importlib.util
from typing import Dict, List, Optional, Any, Type
from pathlib import Path

from .base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig
from .registry import PluginRegistry

logger = logging.getLogger(__name__)


class PluginLoadError(Exception):
    """Raised when a plugin fails to load."""
    pass


class PluginManager:
    """
    Core plugin manager for AI provider plugins.
    
    Handles plugin discovery, loading, validation, and lifecycle management.
    """
    
    def __init__(self, plugin_directory: str = None, config_file: str = None):
        """
        Initialize the plugin manager.
        
        Args:
            plugin_directory: Directory to search for plugins
            config_file: Configuration file for plugin settings
        """
        self.plugin_directory = plugin_directory or os.path.join(os.getcwd(), "plugins", "custom")
        self.config_file = config_file or os.path.join(os.getcwd(), "plugin_config.json")
        self.registry = PluginRegistry()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Ensure plugin directory exists
        os.makedirs(self.plugin_directory, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Track loaded modules for cleanup
        self._loaded_modules = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load plugin configuration from file."""
        if not os.path.exists(self.config_file):
            default_config = {
                "enabled_plugins": [],
                "disabled_plugins": [],
                "plugin_settings": {},
                "auto_discovery": True,
                "validate_on_load": True
            }
            self._save_config(default_config)
            return default_config
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Failed to load plugin config: {e}")
            return {"enabled_plugins": [], "disabled_plugins": [], "plugin_settings": {}}
            
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save plugin configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            self.logger.error(f"Failed to save plugin config: {e}")
            
    def discover_plugins(self) -> List[Dict[str, Any]]:
        """
        Discover available plugins in the plugin directory.
        
        Returns:
            List of plugin information dictionaries
        """
        discovered = []
        
        if not os.path.exists(self.plugin_directory):
            self.logger.warning(f"Plugin directory does not exist: {self.plugin_directory}")
            return discovered
            
        for item in os.listdir(self.plugin_directory):
            plugin_path = os.path.join(self.plugin_directory, item)
            
            # Check for Python files
            if item.endswith('.py') and not item.startswith('_'):
                plugin_info = self._analyze_plugin_file(plugin_path)
                if plugin_info:
                    discovered.append(plugin_info)
                    
            # Check for plugin directories
            elif os.path.isdir(plugin_path) and not item.startswith('_'):
                plugin_info = self._analyze_plugin_directory(plugin_path)
                if plugin_info:
                    discovered.append(plugin_info)
                    
        self.logger.info(f"Discovered {len(discovered)} plugins")
        return discovered
        
    def _analyze_plugin_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a single Python file for plugin information."""
        try:
            spec = importlib.util.spec_from_file_location("temp_plugin", file_path)
            if not spec or not spec.loader:
                return None
                
            # Check for plugin metadata without fully loading
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for plugin metadata
            plugin_info = {
                "type": "file",
                "path": file_path,
                "name": os.path.splitext(os.path.basename(file_path))[0],
                "has_provider_class": "BaseAIProvider" in content,
                "has_plugin_metadata": "PLUGIN_METADATA" in content,
                "estimated_version": "1.0.0"
            }
            
            return plugin_info
            
        except Exception as e:
            self.logger.error(f"Error analyzing plugin file {file_path}: {e}")
            return None
            
    def _analyze_plugin_directory(self, dir_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a plugin directory for plugin information."""
        init_file = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_file):
            return None
            
        try:
            plugin_info = {
                "type": "directory",
                "path": dir_path,
                "name": os.path.basename(dir_path),
                "has_init": True,
                "files": os.listdir(dir_path)
            }
            
            # Check for metadata file
            metadata_file = os.path.join(dir_path, "plugin.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    plugin_info.update(metadata)
                    
            return plugin_info
            
        except Exception as e:
            self.logger.error(f"Error analyzing plugin directory {dir_path}: {e}")
            return None
            
    def load_plugin(self, plugin_name: str) -> Optional[AIProviderPlugin]:
        """
        Load a specific plugin by name.
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            Loaded plugin instance or None if failed
        """
        # Check if plugin is disabled
        if plugin_name in self.config.get("disabled_plugins", []):
            self.logger.info(f"Plugin {plugin_name} is disabled")
            return None
            
        # Check if already loaded
        if self.registry.is_registered(plugin_name):
            self.logger.info(f"Plugin {plugin_name} already loaded")
            return self.registry.get_plugin(plugin_name)
            
        try:
            plugin = self._load_plugin_from_file(plugin_name)
            if plugin:
                self.registry.register_plugin(plugin_name, plugin)
                self.logger.info(f"Successfully loaded plugin: {plugin_name}")
                return plugin
                
        except Exception as e:
            raise PluginLoadError(f"Failed to load plugin {plugin_name}: {e}")
            
        return None
        
    def _load_plugin_from_file(self, plugin_name: str) -> Optional[AIProviderPlugin]:
        """Load plugin from Python file or directory."""
        # Try loading from file
        plugin_file = os.path.join(self.plugin_directory, f"{plugin_name}.py")
        if os.path.exists(plugin_file):
            return self._load_from_python_file(plugin_file, plugin_name)
            
        # Try loading from directory
        plugin_dir = os.path.join(self.plugin_directory, plugin_name)
        if os.path.isdir(plugin_dir):
            return self._load_from_directory(plugin_dir, plugin_name)
            
        self.logger.error(f"Plugin {plugin_name} not found")
        return None
        
    def _load_from_python_file(self, file_path: str, plugin_name: str) -> Optional[AIProviderPlugin]:
        """Load plugin from a single Python file."""
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, file_path)
            if not spec or not spec.loader:
                raise PluginLoadError(f"Cannot create spec for {file_path}")
                
            module = importlib.util.module_from_spec(spec)
            self._loaded_modules[plugin_name] = module
            
            # Add to sys.modules temporarily
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            
            # Look for provider class and metadata
            provider_class = self._find_provider_class(module)
            metadata = getattr(module, 'PLUGIN_METADATA', {})
            
            if not provider_class:
                raise PluginLoadError(f"No BaseAIProvider subclass found in {file_path}")
                
            plugin = AIProviderPlugin(provider_class, metadata)
            
            # Validate if required
            if self.config.get("validate_on_load", True):
                self._validate_plugin(plugin)
                
            return plugin
            
        except Exception as e:
            # Cleanup on failure
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]
            if plugin_name in self._loaded_modules:
                del self._loaded_modules[plugin_name]
            raise PluginLoadError(f"Failed to load plugin from {file_path}: {e}")
            
    def _load_from_directory(self, dir_path: str, plugin_name: str) -> Optional[AIProviderPlugin]:
        """Load plugin from a directory with __init__.py."""
        try:
            # Add directory to Python path temporarily
            if dir_path not in sys.path:
                sys.path.insert(0, os.path.dirname(dir_path))
                
            module = importlib.import_module(os.path.basename(dir_path))
            self._loaded_modules[plugin_name] = module
            
            # Look for provider class and metadata
            provider_class = self._find_provider_class(module)
            
            # Load metadata from plugin.json if available
            metadata_file = os.path.join(dir_path, "plugin.json")
            metadata = {}
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
            # Also check for module-level metadata
            module_metadata = getattr(module, 'PLUGIN_METADATA', {})
            metadata.update(module_metadata)
            
            if not provider_class:
                raise PluginLoadError(f"No BaseAIProvider subclass found in {dir_path}")
                
            plugin = AIProviderPlugin(provider_class, metadata)
            
            # Validate if required
            if self.config.get("validate_on_load", True):
                self._validate_plugin(plugin)
                
            return plugin
            
        except Exception as e:
            raise PluginLoadError(f"Failed to load plugin from {dir_path}: {e}")
            
    def _find_provider_class(self, module) -> Optional[Type[BaseAIProvider]]:
        """Find BaseAIProvider subclass in a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, BaseAIProvider) and 
                attr is not BaseAIProvider):
                return attr
        return None
        
    def _validate_plugin(self, plugin: AIProviderPlugin) -> None:
        """Validate a plugin before registration."""
        # Check required metadata
        info = plugin.get_plugin_info()
        
        # Basic validation
        if not hasattr(plugin.provider_class, 'provider_name'):
            raise PluginLoadError("Plugin class must have provider_name property")
            
        if not hasattr(plugin.provider_class, 'supported_models'):
            raise PluginLoadError("Plugin class must have supported_models property")
            
        # Check required methods
        required_methods = ['initialize', 'generate_message', 'health_check']
        for method in required_methods:
            if not hasattr(plugin.provider_class, method):
                raise PluginLoadError(f"Plugin class must implement {method} method")
                
        self.logger.debug(f"Plugin validation passed for {info['provider_class']}")
        
    def load_all_plugins(self) -> Dict[str, AIProviderPlugin]:
        """
        Load all discovered plugins.
        
        Returns:
            Dictionary of successfully loaded plugins
        """
        loaded = {}
        
        if self.config.get("auto_discovery", True):
            discovered = self.discover_plugins()
            
            for plugin_info in discovered:
                plugin_name = plugin_info["name"]
                
                # Skip if explicitly disabled
                if plugin_name in self.config.get("disabled_plugins", []):
                    self.logger.info(f"Skipping disabled plugin: {plugin_name}")
                    continue
                    
                try:
                    plugin = self.load_plugin(plugin_name)
                    if plugin:
                        loaded[plugin_name] = plugin
                except PluginLoadError as e:
                    self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
                    
        # Also load explicitly enabled plugins
        for plugin_name in self.config.get("enabled_plugins", []):
            if plugin_name not in loaded:
                try:
                    plugin = self.load_plugin(plugin_name)
                    if plugin:
                        loaded[plugin_name] = plugin
                except PluginLoadError as e:
                    self.logger.error(f"Failed to load enabled plugin {plugin_name}: {e}")
                    
        self.logger.info(f"Loaded {len(loaded)} plugins successfully")
        return loaded
        
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin and clean up resources.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            True if successfully unloaded, False otherwise
        """
        try:
            # Remove from registry
            if self.registry.is_registered(plugin_name):
                self.registry.unregister_plugin(plugin_name)
                
            # Clean up module
            if plugin_name in self._loaded_modules:
                del self._loaded_modules[plugin_name]
                
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]
                
            self.logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
            
    def reload_plugin(self, plugin_name: str) -> Optional[AIProviderPlugin]:
        """
        Reload a plugin (unload and load again).
        
        Args:
            plugin_name: Name of the plugin to reload
            
        Returns:
            Reloaded plugin instance or None if failed
        """
        self.logger.info(f"Reloading plugin: {plugin_name}")
        
        # Unload first
        self.unload_plugin(plugin_name)
        
        # Load again
        return self.load_plugin(plugin_name)
        
    def get_plugin_list(self) -> List[Dict[str, Any]]:
        """Get list of all registered plugins with their information."""
        return [
            {
                "name": name,
                "plugin_info": plugin.get_plugin_info(),
                "provider_info": plugin.provider_class.__name__ if plugin.provider_class else None
            }
            for name, plugin in self.registry.get_all_plugins().items()
        ]
        
    def create_provider(self, plugin_name: str, config: ProviderConfig) -> Optional[BaseAIProvider]:
        """
        Create a provider instance from a registered plugin.
        
        Args:
            plugin_name: Name of the registered plugin
            config: Configuration for the provider
            
        Returns:
            Provider instance or None if failed
        """
        plugin = self.registry.get_plugin(plugin_name)
        if not plugin:
            self.logger.error(f"Plugin {plugin_name} not found")
            return None
            
        try:
            provider = plugin.create_provider(config)
            
            # Apply plugin-specific settings if available
            plugin_settings = self.config.get("plugin_settings", {}).get(plugin_name, {})
            for key, value in plugin_settings.items():
                if hasattr(provider.config, key):
                    setattr(provider.config, key, value)
                    
            return provider
            
        except Exception as e:
            self.logger.error(f"Failed to create provider from plugin {plugin_name}: {e}")
            return None
            
    def get_registry(self) -> PluginRegistry:
        """Get the plugin registry instance."""
        return self.registry
        
    def enable_plugin(self, plugin_name: str) -> None:
        """Add plugin to enabled list and remove from disabled list."""
        enabled = self.config.get("enabled_plugins", [])
        disabled = self.config.get("disabled_plugins", [])
        
        if plugin_name not in enabled:
            enabled.append(plugin_name)
            
        if plugin_name in disabled:
            disabled.remove(plugin_name)
            
        self.config["enabled_plugins"] = enabled
        self.config["disabled_plugins"] = disabled
        self._save_config(self.config)
        
    def disable_plugin(self, plugin_name: str) -> None:
        """Add plugin to disabled list and remove from enabled list."""
        enabled = self.config.get("enabled_plugins", [])
        disabled = self.config.get("disabled_plugins", [])
        
        if plugin_name not in disabled:
            disabled.append(plugin_name)
            
        if plugin_name in enabled:
            enabled.remove(plugin_name)
            
        self.config["enabled_plugins"] = enabled
        self.config["disabled_plugins"] = disabled
        self._save_config(self.config)
        
        # Unload if currently loaded
        if self.registry.is_registered(plugin_name):
            self.unload_plugin(plugin_name)
            
    def load_plugins_from_directory(self, directory: str = None) -> List[str]:
        """
        Load plugins from a specific directory.
        
        Args:
            directory: Directory to load plugins from. If None, uses default plugin directory.
            
        Returns:
            List of successfully loaded plugin names
        """
        if directory is None:
            directory = self.plugin_directory
            
        loaded_plugins = []
        
        if not os.path.exists(directory):
            self.logger.warning(f"Plugin directory does not exist: {directory}")
            return loaded_plugins
            
        self.logger.info(f"Loading plugins from directory: {directory}")
        
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                
                # Handle Python files
                if item.endswith('.py') and not item.startswith('_'):
                    plugin_name = item[:-3]  # Remove .py extension
                    try:
                        plugin = self._load_plugin_from_file(plugin_name, item_path)
                        if plugin:
                            self.registry.register_plugin(plugin_name, plugin)
                            loaded_plugins.append(plugin_name)
                            self.logger.info(f"Loaded plugin from file: {plugin_name}")
                    except Exception as e:
                        self.logger.error(f"Failed to load plugin from {item}: {e}")
                        
                # Handle subdirectories
                elif os.path.isdir(item_path) and not item.startswith('_'):
                    try:
                        # Check if it's a Python package (has __init__.py)
                        init_file = os.path.join(item_path, '__init__.py')
                        if os.path.exists(init_file):
                            # Try to load plugins from the package
                            sub_plugins = self._load_plugins_from_package(item, item_path)
                            loaded_plugins.extend(sub_plugins)
                    except Exception as e:
                        self.logger.error(f"Failed to load plugins from directory {item}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error scanning plugin directory {directory}: {e}")
            
        self.logger.info(f"Loaded {len(loaded_plugins)} plugins from directory: {', '.join(loaded_plugins)}")
        return loaded_plugins

    def _load_plugins_from_package(self, package_name: str, package_path: str) -> List[str]:
        """Helper method to load plugins from a Python package."""
        loaded_plugins = []
        
        try:
            # Scan for Python files in the package
            for item in os.listdir(package_path):
                if item.endswith('.py') and not item.startswith('_'):
                    module_name = item[:-3]
                    full_module_name = f"{package_name}.{module_name}"
                    
                    try:
                        plugin = self._load_plugin_from_module(full_module_name, package_path)
                        if plugin:
                            self.registry.register_plugin(full_module_name, plugin)
                            loaded_plugins.append(full_module_name)
                            
                    except Exception as e:
                        self.logger.error(f"Failed to load plugin {full_module_name}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error loading plugins from package {package_name}: {e}")
            
        return loaded_plugins
