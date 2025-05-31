"""
Tests for Built-in AI Provider Plugins

This module tests the built-in provider plugins to ensure they work correctly
with the plugin system and maintain their original functionality.
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from typing import Optional

# Add the parent directory to the path to import from plugins
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.base_provider import ProviderConfig, AIResponse
from plugins.builtin.openrouter_provider import OpenRouterProvider, OpenRouterPlugin
from plugins.builtin.together_provider import TogetherProvider, TogetherPlugin
from plugins.builtin.deepinfra_provider import DeepInfraProvider, DeepInfraPlugin


class TestOpenRouterProvider:
    """Test OpenRouter provider plugin."""
    
    def test_openrouter_provider_initialization(self):
        """Test OpenRouter provider initialization."""
        config = ProviderConfig(
            name="OpenRouter",
            api_key="test-openrouter-key",
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o"
        )
        
        provider = OpenRouterProvider(config)
        assert provider.provider_name == "OpenRouter"
        assert provider.config == config
        
    def test_openrouter_supported_models(self):
        """Test OpenRouter supported models."""
        config = ProviderConfig(
            name="OpenRouter",
            api_key="test-key",
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o"
        )
        
        provider = OpenRouterProvider(config)
        models = provider.supported_models
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert "openai/gpt-4o" in models
        assert "anthropic/claude-3.5-sonnet" in models
        
    def test_openrouter_config_validation(self):
        """Test OpenRouter configuration validation."""
        # Valid config
        valid_config = ProviderConfig(
            name="OpenRouter",
            api_key="test-key",
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o"
        )
        
        provider = OpenRouterProvider(valid_config)
        assert provider.validate_config() is True
        
        # Invalid config (no API key)
        invalid_config = ProviderConfig(
            name="OpenRouter",
            api_key="",
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o"
        )
        
        invalid_provider = OpenRouterProvider(invalid_config)
        assert invalid_provider.validate_config() is False
        
    @patch('httpx.Client')
    def test_openrouter_message_generation(self, mock_httpx):
        """Test OpenRouter message generation."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "This is a test response from OpenRouter"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 8,
                "total_tokens": 18
            },
            "id": "test-response-id",
            "created": 1234567890
        }
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value = mock_client
        
        config = ProviderConfig(
            name="OpenRouter",
            api_key="test-key",
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o"
        )
        
        provider = OpenRouterProvider(config)
        provider.initialize()
        
        response = provider.generate_message(
            "You are a helpful assistant.",
            "Tell me about AI."
        )
        
        assert response is not None
        assert isinstance(response, AIResponse)
        assert response.content == "This is a test response from OpenRouter"
        assert response.provider_name == "OpenRouter"
        assert response.model == "openai/gpt-4o"
        assert response.usage["total_tokens"] == 18
        
    @patch('httpx.Client')
    def test_openrouter_health_check(self, mock_httpx):
        """Test OpenRouter health check."""
        # Mock successful health check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_httpx.return_value = mock_client
        
        config = ProviderConfig(
            name="OpenRouter",
            api_key="test-key",
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o"
        )
        
        provider = OpenRouterProvider(config)
        provider.initialize()
        
        assert provider.health_check() is True
        
    def test_openrouter_plugin_metadata(self):
        """Test OpenRouter plugin metadata."""
        assert OpenRouterPlugin.metadata["name"] == "OpenRouter Provider"
        assert OpenRouterPlugin.metadata["version"] == "1.0.0"
        assert "openrouter" in OpenRouterPlugin.metadata["description"].lower()
        assert "chat_completion" in OpenRouterPlugin.metadata["supported_features"]


class TestTogetherProvider:
    """Test Together AI provider plugin."""
    
    def test_together_provider_initialization(self):
        """Test Together provider initialization."""
        config = ProviderConfig(
            name="Together",
            api_key="test-together-key",
            base_url="https://api.together.xyz/v1",
            model="meta-llama/Llama-3.1-70B-Instruct-Turbo"
        )
        
        provider = TogetherProvider(config)
        assert provider.provider_name == "Together"
        assert provider.config == config
        
    def test_together_supported_models(self):
        """Test Together supported models."""
        config = ProviderConfig(
            name="Together",
            api_key="test-key",
            base_url="https://api.together.xyz/v1",
            model="meta-llama/Llama-3.1-70B-Instruct-Turbo"
        )
        
        provider = TogetherProvider(config)
        models = provider.supported_models
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert "meta-llama/Llama-3.1-70B-Instruct-Turbo" in models
        assert any("llama" in model.lower() for model in models)
        
    @patch('httpx.Client')
    def test_together_message_generation(self, mock_httpx):
        """Test Together message generation."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "This is a test response from Together AI"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 9,
                "total_tokens": 21
            },
            "id": "test-together-id",
            "created": 1234567890
        }
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value = mock_client
        
        config = ProviderConfig(
            name="Together",
            api_key="test-key",
            base_url="https://api.together.xyz/v1",
            model="meta-llama/Llama-3.1-70B-Instruct-Turbo"
        )
        
        provider = TogetherProvider(config)
        provider.initialize()
        
        response = provider.generate_message(
            "You are a helpful assistant.",
            "Tell me about machine learning."
        )
        
        assert response is not None
        assert isinstance(response, AIResponse)
        assert response.content == "This is a test response from Together AI"
        assert response.provider_name == "Together"
        assert response.model == "meta-llama/Llama-3.1-70B-Instruct-Turbo"
        assert response.usage["total_tokens"] == 21
        
    def test_together_plugin_metadata(self):
        """Test Together plugin metadata."""
        assert TogetherPlugin.metadata["name"] == "Together AI Provider"
        assert TogetherPlugin.metadata["version"] == "1.0.0"
        assert "together" in TogetherPlugin.metadata["description"].lower()
        assert "chat_completion" in TogetherPlugin.metadata["supported_features"]


class TestDeepInfraProvider:
    """Test DeepInfra provider plugin."""
    
    def test_deepinfra_provider_initialization(self):
        """Test DeepInfra provider initialization."""
        config = ProviderConfig(
            name="DeepInfra",
            api_key="test-deepinfra-key",
            base_url="https://api.deepinfra.com/v1/openai",
            model="meta-llama/Meta-Llama-3.1-70B-Instruct"
        )
        
        provider = DeepInfraProvider(config)
        assert provider.provider_name == "DeepInfra"
        assert provider.config == config
        
    def test_deepinfra_supported_models(self):
        """Test DeepInfra supported models."""
        config = ProviderConfig(
            name="DeepInfra",
            api_key="test-key",
            base_url="https://api.deepinfra.com/v1/openai",
            model="meta-llama/Meta-Llama-3.1-70B-Instruct"
        )
        
        provider = DeepInfraProvider(config)
        models = provider.supported_models
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert "meta-llama/Meta-Llama-3.1-70B-Instruct" in models
        assert any("llama" in model.lower() for model in models)
        
    @patch('httpx.Client')
    def test_deepinfra_message_generation(self, mock_httpx):
        """Test DeepInfra message generation."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "This is a test response from DeepInfra"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 8,
                "total_tokens": 23
            },
            "id": "test-deepinfra-id",
            "created": 1234567890
        }
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value = mock_client
        
        config = ProviderConfig(
            name="DeepInfra",
            api_key="test-key",
            base_url="https://api.deepinfra.com/v1/openai",
            model="meta-llama/Meta-Llama-3.1-70B-Instruct"
        )
        
        provider = DeepInfraProvider(config)
        provider.initialize()
        
        response = provider.generate_message(
            "You are a helpful assistant.",
            "Explain neural networks."
        )
        
        assert response is not None
        assert isinstance(response, AIResponse)
        assert response.content == "This is a test response from DeepInfra"
        assert response.provider_name == "DeepInfra"
        assert response.model == "meta-llama/Meta-Llama-3.1-70B-Instruct"
        assert response.usage["total_tokens"] == 23
        
    def test_deepinfra_plugin_metadata(self):
        """Test DeepInfra plugin metadata."""
        assert DeepInfraPlugin.metadata["name"] == "DeepInfra Provider"
        assert DeepInfraPlugin.metadata["version"] == "1.0.0"
        assert "deepinfra" in DeepInfraPlugin.metadata["description"].lower()
        assert "chat_completion" in DeepInfraPlugin.metadata["supported_features"]


class TestBuiltinProvidersIntegration:
    """Test integration of all built-in providers."""
    
    def test_all_builtin_providers_have_plugins(self):
        """Test that all built-in providers have plugin instances."""
        assert OpenRouterPlugin is not None
        assert TogetherPlugin is not None
        assert DeepInfraPlugin is not None
        
    def test_all_builtin_providers_can_create_instances(self):
        """Test that all built-in providers can create instances."""
        providers = [
            (OpenRouterPlugin, ProviderConfig(
                name="OpenRouter",
                api_key="test-key",
                base_url="https://openrouter.ai/api/v1",
                model="openai/gpt-4o"
            )),
            (TogetherPlugin, ProviderConfig(
                name="Together",
                api_key="test-key",
                base_url="https://api.together.xyz/v1",
                model="meta-llama/Llama-3.1-70B-Instruct-Turbo"
            )),
            (DeepInfraPlugin, ProviderConfig(
                name="DeepInfra",
                api_key="test-key",
                base_url="https://api.deepinfra.com/v1/openai",
                model="meta-llama/Meta-Llama-3.1-70B-Instruct"
            ))
        ]
        
        for plugin, config in providers:
            provider_instance = plugin.create_provider(config)
            assert provider_instance is not None
            assert hasattr(provider_instance, 'provider_name')
            assert hasattr(provider_instance, 'supported_models')
            assert hasattr(provider_instance, 'initialize')
            assert hasattr(provider_instance, 'generate_message')
            assert hasattr(provider_instance, 'health_check')
            
    def test_builtin_providers_validation(self):
        """Test that all built-in providers pass validation."""
        providers = [OpenRouterPlugin, TogetherPlugin, DeepInfraPlugin]
        
        for plugin in providers:
            # Check required metadata fields
            assert "name" in plugin.metadata
            assert "version" in plugin.metadata
            assert "description" in plugin.metadata
            assert "author" in plugin.metadata
            
            # Check provider class is valid
            assert plugin.provider_class is not None
            assert hasattr(plugin.provider_class, '__init__')
            
    def test_builtin_providers_unique_names(self):
        """Test that all built-in providers have unique names."""
        provider_names = [
            OpenRouterPlugin.metadata["name"],
            TogetherPlugin.metadata["name"],
            DeepInfraPlugin.metadata["name"]
        ]
        
        assert len(provider_names) == len(set(provider_names))
        
    @patch('httpx.Client')
    def test_builtin_providers_error_handling(self, mock_httpx):
        """Test error handling in built-in providers."""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API Error")
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value = mock_client
        
        config = ProviderConfig(
            name="OpenRouter",
            api_key="test-key",
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o"
        )
        
        provider = OpenRouterProvider(config)
        provider.initialize()
        
        # Should handle errors gracefully and return None
        response = provider.generate_message(
            "You are a helpful assistant.",
            "This should fail."
        )
        
        assert response is None


# Test fixtures for built-in providers
@pytest.fixture
def openrouter_config():
    """Fixture for OpenRouter configuration."""
    return ProviderConfig(
        name="OpenRouter",
        api_key="test-openrouter-key",
        base_url="https://openrouter.ai/api/v1",
        model="openai/gpt-4o"
    )


@pytest.fixture
def together_config():
    """Fixture for Together configuration."""
    return ProviderConfig(
        name="Together",
        api_key="test-together-key",
        base_url="https://api.together.xyz/v1",
        model="meta-llama/Llama-3.1-70B-Instruct-Turbo"
    )


@pytest.fixture
def deepinfra_config():
    """Fixture for DeepInfra configuration."""
    return ProviderConfig(
        name="DeepInfra",
        api_key="test-deepinfra-key",
        base_url="https://api.deepinfra.com/v1/openai",
        model="meta-llama/Meta-Llama-3.1-70B-Instruct"
    )


# Tests using fixtures
def test_openrouter_with_fixture(openrouter_config):
    """Test OpenRouter provider with fixture."""
    provider = OpenRouterProvider(openrouter_config)
    assert provider.provider_name == "OpenRouter"
    assert provider.validate_config() is True


def test_together_with_fixture(together_config):
    """Test Together provider with fixture."""
    provider = TogetherProvider(together_config)
    assert provider.provider_name == "Together"
    assert provider.validate_config() is True


def test_deepinfra_with_fixture(deepinfra_config):
    """Test DeepInfra provider with fixture."""
    provider = DeepInfraProvider(deepinfra_config)
    assert provider.provider_name == "DeepInfra"
    assert provider.validate_config() is True


if __name__ == "__main__":
    # Run tests directly if executed as a script
    pytest.main([__file__, "-v"])
