# API Documentation
Auto-generated API documentation for AI-Ticker plugin system.

## BaseAIProvider

Abstract base class for AI providers.

All custom AI provider plugins must inherit from this class and implement
the required methods.


### Methods:
- **generate_message()**: 
Generate a message using the AI provider.

Args:
    system_prompt: The system/instruction prompt
    user_prompt: The user's prompt/query
    
Returns:
    AIResponse: The response from the AI provider, or None if failed

- **get_info()**: Get information about this provider.
- **health_check()**: 
Check if the provider is healthy and accessible.

Returns:
    bool: True if the provider is healthy, False otherwise.

- **initialize()**: 
Initialize the provider with its configuration.

Returns:
    bool: True if initialization was successful, False otherwise.

- **validate_config()**: 
Validate the provider configuration.

Returns:
    bool: True if configuration is valid, False otherwise.


## AIProviderPlugin

Plugin wrapper for AI providers.

This class wraps BaseAIProvider implementations and provides additional
metadata and lifecycle management.


### Methods:
- **create_provider()**: Create an instance of the provider with the given configuration.
- **get_plugin_info()**: Get plugin information.

## PluginManager

Core plugin manager for AI provider plugins.

Handles plugin discovery, loading, validation, and lifecycle management.


### Methods:
- **create_provider()**: 
Create a provider instance from a registered plugin.

Args:
    plugin_name: Name of the registered plugin
    config: Configuration for the provider
    
Returns:
    Provider instance or None if failed

- **disable_plugin()**: Add plugin to disabled list and remove from enabled list.
- **discover_plugins()**: 
Discover available plugins in the plugin directory.

Returns:
    List of plugin information dictionaries

- **enable_plugin()**: Add plugin to enabled list and remove from disabled list.
- **get_plugin_list()**: Get list of all registered plugins with their information.
- **get_registry()**: Get the plugin registry instance.
- **load_all_plugins()**: 
Load all discovered plugins.

Returns:
    Dictionary of successfully loaded plugins

- **load_plugin()**: 
Load a specific plugin by name.

Args:
    plugin_name: Name of the plugin to load
    
Returns:
    Loaded plugin instance or None if failed

- **load_plugins_from_directory()**: 
Load plugins from a specific directory.

Args:
    directory: Directory to load plugins from. If None, uses default plugin directory.
    
Returns:
    List of successfully loaded plugin names

- **reload_plugin()**: 
Reload a plugin (unload and load again).

Args:
    plugin_name: Name of the plugin to reload
    
Returns:
    Reloaded plugin instance or None if failed

- **unload_plugin()**: 
Unload a plugin and clean up resources.

Args:
    plugin_name: Name of the plugin to unload
    
Returns:
    True if successfully unloaded, False otherwise


## PluginRegistry

Thread-safe registry for AI provider plugins.

Manages the registration, storage, and retrieval of plugins with
thread safety for concurrent access.


### Methods:
- **check_dependencies()**: 
Check if all dependencies for a plugin are satisfied.

Args:
    plugin_name: Name of the plugin to check dependencies for
    
Returns:
    Dictionary mapping dependency names to availability status

- **clear()**: Clear all registered plugins.
- **count()**: 
Get the number of registered plugins.

Returns:
    Number of registered plugins

- **export_registry()**: 
Export registry state for serialization.

Returns:
    Serializable dictionary representation of the registry

- **find_by_provider_class()**: 
Find plugins by provider class name.

Args:
    provider_class_name: Name of the provider class to search for
    
Returns:
    List of plugin names that use the specified provider class

- **get_all_plugins()**: 
Get all registered plugins.

Returns:
    Dictionary of all registered plugins (copy)

- **get_dependent_plugins()**: 
Get list of plugins that depend on the specified plugin.

Args:
    plugin_name: Name of the plugin to check dependents for
    
Returns:
    List of plugin names that depend on the specified plugin

- **get_plugin()**: 
Get a registered plugin by name.

Args:
    name: Name of the plugin to retrieve
    
Returns:
    Plugin instance or None if not found

- **get_plugin_dependencies()**: 
Get dependencies for a specific plugin.

Args:
    plugin_name: Name of the plugin to get dependencies for
    
Returns:
    List of dependency names

- **get_plugin_names()**: 
Get names of all registered plugins.

Returns:
    List of plugin names

- **get_plugins_by_metadata()**: 
Find plugins by metadata key-value pair.

Args:
    key: Metadata key to search for
    value: Expected value for the metadata key
    
Returns:
    List of plugin names that match the metadata criteria

- **get_registry_info()**: 
Get information about the registry state.

Returns:
    Dictionary with registry statistics and information

- **is_registered()**: 
Check if a plugin is registered.

Args:
    name: Name of the plugin to check
    
Returns:
    True if plugin is registered, False otherwise

- **register_plugin()**: 
Register a plugin in the registry.

Args:
    name: Unique name for the plugin
    plugin: Plugin instance to register
    
Returns:
    True if registration was successful, False if name conflicts

- **unregister_plugin()**: 
Unregister a plugin from the registry.

Args:
    name: Name of the plugin to unregister
    
Returns:
    True if unregistration was successful, False if not found

- **validate_plugin()**: 
Validate a single plugin.

Args:
    plugin: Plugin to validate
    
Returns:
    True if plugin is valid, False otherwise

- **validate_registry()**: 
Validate all registered plugins.

Returns:
    Dictionary with validation results (valid/invalid plugin lists)


## PluginAwareAIClient

Enhanced AI provider client that uses the plugin system.

Provides backward compatibility while leveraging the new plugin architecture.


### Methods:
- **add_custom_provider()**: 
Add a custom provider from a plugin.

Args:
    plugin_name: Name of the plugin to use
    config: Provider configuration
    
Returns:
    True if provider was added successfully

- **get_available_providers()**: 
Get list of available provider names.

Returns:
    List of provider names

- **get_message()**: 
Get a unique message from available providers.

Args:
    system_prompt: System/instruction prompt
    user_prompt: User query/prompt
    existing_messages: List of existing messages to avoid duplicates
    fuzzy_threshold: Similarity threshold for duplicate detection (0-100)
    
Returns:
    Generated message content or None if all providers fail

- **get_plugin_manager()**: Get the underlying plugin manager.
- **get_provider_info()**: 
Get information about all providers.

Returns:
    Dictionary with provider information

- **health_check_all()**: 
Check health of all providers.

Returns:
    Dictionary mapping provider names to health status

- **reload_providers()**: Reload all providers.

