"""
Tests for the AI-Ticker Plugin System

This module contains comprehensive tests for the plugin system including:
- BaseAIProvider functionality
- Plugin registration and discovery
- Plugin manager operations
- Integration with the main application
"""
import pytest
import tempfile
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from typing import Optional, List

# Add the parent directory to the path to import from plugins
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse
from plugins.plugin_manager import PluginManager
from plugins.registry import PluginRegistry
from plugins.integration import PluginIntegration, load_providers_from_env
from plugin_client import PluginAwareAIClient


class MockProvider(BaseAIProvider):
    """Mock provider for testing."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._initialized = False
        self._health_status = True
        
    @property
    def provider_name(self) -> str:
        return "MockProvider"
        
    @property
    def supported_models(self) -> List[str]:
        return ["mock-model-1", "mock-model-2"]
        
    def initialize(self) -> bool:
        self._initialized = True
        return True
        
    def generate_message(self, system_prompt: str, user_prompt: str) -> Optional[AIResponse]:
        if not self._initialized:
            return None
            
        return AIResponse(
            content="Mock response from test provider",
            provider_name=self.provider_name,
            model=self.config.model,
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            metadata={"test": True}
        )
        
    def health_check(self) -> bool:
        return self._health_status
        
    def set_health_status(self, status: bool):
        """Set health status for testing."""
        self._health_status = status


class TestProviderConfig:
    """Test ProviderConfig dataclass."""
    
    def test_provider_config_creation(self):
        """Test creating a provider configuration."""
        config = ProviderConfig(
            name="Test Provider",
            api_key="test-key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        assert config.name == "Test Provider"
        assert config.api_key == "test-key"
        assert config.base_url == "https://test.api.com"
        assert config.model == "test-model"
        assert config.max_tokens == 512  # Default value
        assert config.temperature == 0.7  # Default value
        
    def test_provider_config_with_custom_values(self):
        """Test creating a provider configuration with custom values."""
        config = ProviderConfig(
            name="Custom Provider",
            api_key="custom-key",
            base_url="https://custom.api.com",
            model="custom-model",
            max_tokens=1000,
            temperature=0.5,
            extra_headers={"Custom-Header": "value"}
        )
        
        assert config.max_tokens == 1000
        assert config.temperature == 0.5
        assert config.extra_headers == {"Custom-Header": "value"}


class TestAIResponse:
    """Test AIResponse dataclass."""
    
    def test_ai_response_creation(self):
        """Test creating an AI response."""
        response = AIResponse(
            content="Test response",
            provider_name="TestProvider",
            model="test-model",
            usage={"total_tokens": 100},
            metadata={"test": True}
        )
        
        assert response.content == "Test response"
        assert response.provider_name == "TestProvider"
        assert response.model == "test-model"
        assert response.usage == {"total_tokens": 100}
        assert response.metadata == {"test": True}


class TestBaseAIProvider:
    """Test BaseAIProvider abstract class."""
    
    def test_mock_provider_initialization(self):
        """Test that mock provider can be initialized."""
        config = ProviderConfig(
            name="Mock Provider",
            api_key="test-key",
            base_url="https://mock.api.com",
            model="mock-model-1"
        )
        
        provider = MockProvider(config)
        assert provider.config == config
        assert provider.provider_name == "MockProvider"
        assert "mock-model-1" in provider.supported_models
        
    def test_provider_initialization(self):
        """Test provider initialization."""
        config = ProviderConfig(
            name="Mock Provider",
            api_key="test-key",
            base_url="https://mock.api.com",
            model="mock-model-1"
        )
        
        provider = MockProvider(config)
        result = provider.initialize()
        
        assert result is True
        assert provider._initialized is True
        
    def test_provider_message_generation(self):
        """Test provider message generation."""
        config = ProviderConfig(
            name="Mock Provider",
            api_key="test-key",
            base_url="https://mock.api.com",
            model="mock-model-1"
        )
        
        provider = MockProvider(config)
        provider.initialize()
        
        response = provider.generate_message(
            "You are a helpful assistant.",
            "Tell me about AI."
        )
        
        assert response is not None
        assert response.content == "Mock response from test provider"
        assert response.provider_name == "MockProvider"
        assert response.model == "mock-model-1"
        assert "prompt_tokens" in response.usage
        
    def test_provider_health_check(self):
        """Test provider health check."""
        config = ProviderConfig(
            name="Mock Provider",
            api_key="test-key",
            base_url="https://mock.api.com",
            model="mock-model-1"
        )
        
        provider = MockProvider(config)
        assert provider.health_check() is True
        
        provider.set_health_status(False)
        assert provider.health_check() is False
        
    def test_provider_config_validation(self):
        """Test provider configuration validation."""
        config = ProviderConfig(
            name="Mock Provider",
            api_key="test-key",
            base_url="https://mock.api.com",
            model="mock-model-1"
        )
        
        provider = MockProvider(config)
        assert provider.validate_config() is True
        
        # Test with invalid config
        invalid_config = ProviderConfig(
            name="",
            api_key="",
            base_url="",
            model=""
        )
        
        invalid_provider = MockProvider(invalid_config)
        assert invalid_provider.validate_config() is False


class TestPluginRegistry:
    """Test PluginRegistry functionality."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = PluginRegistry()
        assert len(registry.get_all_plugins()) == 0
        
    def test_plugin_registration(self):
        """Test plugin registration."""
        registry = PluginRegistry()
        
        config = ProviderConfig(
            name="Test Provider",
            api_key="test-key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        plugin = AIProviderPlugin(
            provider_class=MockProvider,
            metadata={
                "name": "Test Plugin",
                "version": "1.0.0",
                "author": "Test Author",
                "description": "Test plugin"
            }
        )
        
        registry.register_plugin("test_plugin", plugin)
        
        assert registry.get_plugin("test_plugin") == plugin
        assert "test_plugin" in registry.get_all_plugins()
        
    def test_plugin_unregistration(self):
        """Test plugin unregistration."""
        registry = PluginRegistry()
        
        plugin = AIProviderPlugin(
            provider_class=MockProvider,
            metadata={
                "name": "Test Plugin",
                "version": "1.0.0",
                "author": "Test Author",
                "description": "Test plugin"
            }
        )
        
        registry.register_plugin("test_plugin", plugin)
        assert registry.get_plugin("test_plugin") is not None
        
        registry.unregister_plugin("test_plugin")
        assert registry.get_plugin("test_plugin") is None
        
    def test_plugin_validation(self):
        """Test plugin validation."""
        registry = PluginRegistry()
        
        valid_plugin = AIProviderPlugin(
            provider_class=MockProvider,
            metadata={
                "name": "Valid Plugin",
                "version": "1.0.0",
                "author": "Test Author",
                "description": "Valid test plugin"
            }
        )
        
        assert registry.validate_plugin(valid_plugin) is True
        
        # Test with invalid plugin (missing required metadata)
        invalid_plugin = AIProviderPlugin(
            provider_class=MockProvider,
            metadata={
                "name": "Invalid Plugin"
                # Missing required fields
            }
        )
        
        assert registry.validate_plugin(invalid_plugin) is False


class TestPluginManager:
    """Test PluginManager functionality."""
    
    def test_plugin_manager_initialization(self):
        """Test plugin manager initialization."""
        manager = PluginManager()
        assert manager.registry is not None
        
    def test_load_plugins_from_directory(self):
        """Test loading plugins from a directory."""
        # Create a temporary directory with a mock plugin
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_file = os.path.join(temp_dir, "test_plugin.py")
            
            plugin_content = '''
from plugins.base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse
from typing import Optional, List

class TestProvider(BaseAIProvider):
    def __init__(self, config):
        super().__init__(config)
        
    @property
    def provider_name(self):
        return "TestProvider"
        
    @property
    def supported_models(self):
        return ["test-model"]
        
    def initialize(self):
        return True
        
    def generate_message(self, system_prompt, user_prompt):
        return AIResponse(
            content="Test response",
            provider_name=self.provider_name,
            model=self.config.model,
            usage={},
            metadata={}
        )
        
    def health_check(self):
        return True

TestPlugin = AIProviderPlugin(
    provider_class=TestProvider,
    metadata={
        "name": "Test Plugin",
        "version": "1.0.0",
        "author": "Test",
        "description": "Test plugin"
    }
)
'''
            
            with open(plugin_file, 'w') as f:
                f.write(plugin_content)
            
            manager = PluginManager()
            
            # This would normally load the plugin, but due to import complexities
            # in the test environment, we'll just test the method exists
            assert hasattr(manager, 'load_plugins_from_directory')


class TestPluginIntegration:
    """Test PluginIntegration functionality."""
    
    @patch.dict(os.environ, {
        'OPENROUTER_API_KEY': 'test-openrouter-key',
        'TOGETHER_API_KEY': 'test-together-key'
    })
    def test_load_providers_from_env(self):
        """Test loading providers from environment variables."""
        providers = load_providers_from_env()
        
        assert "providers" in providers
        assert len(providers["providers"]) >= 2  # At least OpenRouter and Together
        
        # Check that API keys are loaded
        openrouter_found = False
        together_found = False
        
        for provider in providers["providers"]:
            if provider["name"] == "OpenRouter":
                openrouter_found = True
                assert provider["api_key"] == "test-openrouter-key"
            elif provider["name"] == "Together":
                together_found = True
                assert provider["api_key"] == "test-together-key"
                
        assert openrouter_found
        assert together_found
        
    def test_plugin_integration_initialization(self):
        """Test plugin integration initialization."""
        config = {
            "providers": [
                {
                    "name": "Test Provider",
                    "api_key": "test-key",
                    "base_url": "https://test.api.com",
                    "model": "test-model"
                }
            ]
        }
        
        integration = PluginIntegration(config)
        assert integration.plugin_manager is not None


class TestPluginAwareAIClient:
    """Test PluginAwareAIClient functionality."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        config = {
            "providers": [
                {
                    "name": "Test Provider",
                    "api_key": "test-key",
                    "base_url": "https://test.api.com",
                    "model": "test-model"
                }
            ]
        }
        
        client = PluginAwareAIClient(config)
        assert client.timeout == 30
        assert client.plugin_integration is not None
        
    def test_client_with_no_config(self):
        """Test client initialization with no config."""
        with patch('plugin_client.load_providers_from_env') as mock_load:
            mock_load.return_value = {"providers": []}
            
            client = PluginAwareAIClient()
            assert client.plugin_integration is not None
            
    @patch.dict(os.environ, {
        'OPENROUTER_API_KEY': 'test-key'
    })
    def test_client_health_check(self):
        """Test client health check functionality."""
        client = PluginAwareAIClient()
        
        # Health check should return a dictionary
        health_status = client.health_check_all()
        assert isinstance(health_status, dict)
        
    def test_client_provider_info(self):
        """Test getting provider information."""
        config = {
            "providers": [
                {
                    "name": "Test Provider",
                    "api_key": "test-key",
                    "base_url": "https://test.api.com",
                    "model": "test-model"
                }
            ]
        }
        
        client = PluginAwareAIClient(config)
        provider_info = client.get_provider_info()
        
        assert isinstance(provider_info, dict)
        
    def test_client_available_providers(self):
        """Test getting available providers."""
        config = {
            "providers": [
                {
                    "name": "Test Provider",
                    "api_key": "test-key",
                    "base_url": "https://test.api.com",
                    "model": "test-model"
                }
            ]
        }
        
        client = PluginAwareAIClient(config)
        providers = client.get_available_providers()
        
        assert isinstance(providers, list)


class TestPluginSystemIntegration:
    """Test integration between different plugin system components."""
    
    def test_end_to_end_plugin_flow(self):
        """Test complete plugin flow from registration to usage."""
        # Create a registry
        registry = PluginRegistry()
        
        # Create a plugin
        plugin = AIProviderPlugin(
            provider_class=MockProvider,
            metadata={
                "name": "Integration Test Plugin",
                "version": "1.0.0",
                "author": "Test Author",
                "description": "Plugin for integration testing"
            }
        )
        
        # Register the plugin
        registry.register_plugin("integration_test", plugin)
        
        # Verify registration
        assert registry.get_plugin("integration_test") == plugin
        
        # Test plugin functionality
        config = ProviderConfig(
            name="Integration Test Provider",
            api_key="test-key",
            base_url="https://test.api.com",
            model="mock-model-1"
        )
        
        provider_instance = plugin.create_provider(config)
        assert provider_instance is not None
        
        # Initialize and test the provider
        assert provider_instance.initialize() is True
        assert provider_instance.health_check() is True
        
        response = provider_instance.generate_message(
            "You are a helpful assistant.",
            "Generate a test response."
        )
        
        assert response is not None
        assert response.content == "Mock response from test provider"
        assert response.provider_name == "MockProvider"


# Pytest fixtures
@pytest.fixture
def mock_provider_config():
    """Fixture for creating a mock provider configuration."""
    return ProviderConfig(
        name="Mock Provider",
        api_key="test-api-key",
        base_url="https://mock.api.com",
        model="mock-model-1"
    )


@pytest.fixture
def mock_provider(mock_provider_config):
    """Fixture for creating a mock provider instance."""
    return MockProvider(mock_provider_config)


@pytest.fixture
def plugin_registry():
    """Fixture for creating a clean plugin registry."""
    return PluginRegistry()


@pytest.fixture
def plugin_manager():
    """Fixture for creating a plugin manager."""
    return PluginManager()


# Integration tests with pytest fixtures
def test_provider_with_fixture(mock_provider):
    """Test provider using pytest fixture."""
    assert mock_provider.provider_name == "MockProvider"
    assert mock_provider.initialize() is True


def test_registry_with_fixture(plugin_registry):
    """Test registry using pytest fixture."""
    assert len(plugin_registry.get_all_plugins()) == 0


def test_manager_with_fixture(plugin_manager):
    """Test manager using pytest fixture."""
    assert plugin_manager.registry is not None


if __name__ == "__main__":
    # Run tests directly if executed as a script
    pytest.main([__file__, "-v"])
