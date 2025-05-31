"""
AI-Ticker Plugin System

This package provides a plugin architecture for custom AI providers.
Plugins can be loaded dynamically and integrated seamlessly with the core system.
"""

from .base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse
from .registry import PluginRegistry
from .plugin_manager import PluginManager

__all__ = [
    'BaseAIProvider', 
    'AIProviderPlugin', 
    'ProviderConfig', 
    'AIResponse',
    'PluginRegistry',
    'PluginManager'
]
__version__ = "1.1.0"
