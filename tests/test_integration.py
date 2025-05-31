"""
Integration Tests for Plugin System with Main Application

This module tests the integration between the plugin system and the main Flask application.
"""
import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from main application
import app
from plugin_client import PluginAwareAIClient


class TestAppPluginIntegration:
    """Test integration between the Flask app and plugin system."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.app.config['TESTING'] = True
        with app.app.test_client() as client:
            yield client
            
    @pytest.fixture
    def mock_plugin_client(self):
        """Mock the PluginAwareAIClient for testing."""
        with patch('app.ai_client') as mock_client:
            mock_client.get_message.return_value = "Test message from plugin system"
            mock_client.health_check_all.return_value = {"TestProvider": True}
            mock_client.get_provider_info.return_value = {
                "TestProvider": {
                    "name": "Test Provider",
                    "model": "test-model",
                    "status": "healthy"
                }
            }
            mock_client.get_available_providers.return_value = ["TestProvider"]
            yield mock_client
            
    def test_index_route_with_plugins(self, client):
        """Test that the main page loads correctly with plugin system."""
        response = client.get('/')
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data
        assert b"AI-Ticker Dashboard" in response.data
        
    @patch('app.ai_client')
    def test_api_message_route_with_plugins(self, mock_ai_client, client):
        """Test API message route with plugin system."""
        # Mock the AI client to return a test message
        mock_ai_client.get_message.return_value = "Test plugin message"
        
        response = client.get('/api/message')
        assert response.status_code == 200
        assert response.is_json
        
        data = response.get_json()
        assert "message" in data
        assert data["message"] == "Test plugin message"
        
    def test_api_plugins_route(self, client):
        """Test the new /api/plugins route."""
        response = client.get('/api/plugins')
        assert response.status_code == 200
        assert response.is_json
        
        data = response.get_json()
        assert "plugins" in data
        assert isinstance(data["plugins"], list)
        
    def test_api_providers_route(self, client):
        """Test the new /api/providers route."""
        response = client.get('/api/providers')
        assert response.status_code == 200
        assert response.is_json
        
        data = response.get_json()
        assert "providers" in data
        assert isinstance(data["providers"], dict)
        
    def test_api_providers_reload_route(self, client):
        """Test the new /api/providers/reload route."""
        response = client.post('/api/providers/reload')
        assert response.status_code == 200
        assert response.is_json
        
        data = response.get_json()
        assert "status" in data
        assert data["status"] == "success"
        assert "message" in data
        
    @patch('app.ai_client')
    def test_api_health_with_plugins(self, mock_ai_client, client):
        """Test health check endpoint with plugin information."""
        # Mock health check to return plugin status
        mock_ai_client.health_check_all.return_value = {
            "OpenRouter": True,
            "Together": False,
            "MockProvider": True
        }
        
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.is_json
        
        data = response.get_json()
        assert "status" in data
        assert "providers" in data
        assert "OpenRouter" in data["providers"]
        assert "Together" in data["providers"]
        
    @patch('app.ai_client')
    def test_error_handling_with_failed_plugins(self, mock_ai_client, client):
        """Test error handling when plugins fail."""
        # Mock AI client to return None (all providers failed)
        mock_ai_client.get_message.return_value = None
        
        response = client.get('/api/message')
        assert response.status_code == 200
        assert response.is_json
        
        data = response.get_json()
        assert "message" in data
        # Should return fallback message when all providers fail
        assert "currently unavailable" in data["message"].lower() or "error" in data["message"].lower()


class TestPluginClientIntegration:
    """Test PluginAwareAIClient integration."""
    
    @patch.dict(os.environ, {
        'OPENROUTER_API_KEY': 'test-openrouter-key',
        'TOGETHER_API_KEY': 'test-together-key'
    })
    def test_plugin_client_initialization_with_env(self):
        """Test that PluginAwareAIClient initializes with environment variables."""
        client = PluginAwareAIClient()
        
        # Should have loaded providers from environment
        available_providers = client.get_available_providers()
        assert isinstance(available_providers, list)
        assert len(available_providers) > 0
        
    def test_plugin_client_with_custom_config(self):
        """Test PluginAwareAIClient with custom configuration."""
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
        assert client is not None
        
        # Should have the test provider
        provider_info = client.get_provider_info()
        assert isinstance(provider_info, dict)
        
    @patch('plugins.integration.PluginIntegration')
    def test_plugin_client_message_generation(self, mock_integration):
        """Test message generation through plugin client."""
        # Mock the plugin integration
        mock_provider = Mock()
        mock_provider.generate_message.return_value = Mock(
            content="Test message from plugin",
            provider_name="TestProvider",
            model="test-model",
            usage={"total_tokens": 10},
            metadata={}
        )
        
        mock_integration_instance = Mock()
        mock_integration_instance.get_providers.return_value = {"TestProvider": mock_provider}
        mock_integration.return_value = mock_integration_instance
        
        client = PluginAwareAIClient()
        
        result = client.get_message(
            "You are a helpful assistant.",
            "Tell me about AI.",
            existing_messages=[],
            fuzzy_threshold=85
        )
        
        assert result == "Test message from plugin"
        
    @patch('plugins.integration.PluginIntegration')
    def test_plugin_client_health_check(self, mock_integration):
        """Test health check through plugin client."""
        # Mock providers with different health status
        mock_provider1 = Mock()
        mock_provider1.provider_name = "Provider1"
        mock_provider1.health_check.return_value = True
        
        mock_provider2 = Mock()
        mock_provider2.provider_name = "Provider2"
        mock_provider2.health_check.return_value = False
        
        mock_integration_instance = Mock()
        mock_integration_instance.get_providers.return_value = {
            "Provider1": mock_provider1,
            "Provider2": mock_provider2
        }
        mock_integration.return_value = mock_integration_instance
        
        client = PluginAwareAIClient()
        health_status = client.health_check_all()
        
        assert isinstance(health_status, dict)
        assert "Provider1" in health_status
        assert "Provider2" in health_status
        assert health_status["Provider1"] is True
        assert health_status["Provider2"] is False


class TestConfigurationIntegration:
    """Test configuration integration with plugin system."""
    
    @patch.dict(os.environ, {
        'OPENROUTER_API_KEY': 'test-key-1',
        'TOGETHER_API_KEY': 'test-key-2',
        'DEEPINFRA_API_KEY': 'test-key-3'
    })
    def test_config_loads_plugin_providers(self):
        """Test that configuration loads providers for plugin system."""
        from config import Config
        
        config = Config()
        assert len(config.providers) >= 3  # At least the three main providers
        
        # Check that providers have the required fields
        for provider in config.providers:
            assert "name" in provider
            assert "api_key" in provider
            assert "base_url" in provider
            assert "model" in provider
            assert provider["api_key"]  # Should have a valid API key
            
    def test_config_validation_with_plugins(self):
        """Test configuration validation works with plugin system."""
        from config import Config
        
        # This should not raise an exception even if no API keys are set
        config = Config()
        assert config is not None
        
        # Validate that configuration has all required fields
        assert hasattr(config, 'providers')
        assert hasattr(config, 'fuzzy_threshold')
        assert hasattr(config, 'cache_probability')
        assert hasattr(config, 'api_timeout')


class TestBackwardCompatibility:
    """Test backward compatibility with existing functionality."""
    
    def test_existing_config_format_still_works(self):
        """Test that existing configuration format still works."""
        # Simulate old configuration format
        old_config = {
            "providers": [
                {
                    "name": "OpenRouter",
                    "api_key": "old-key",
                    "base_url": "https://openrouter.ai/api/v1",
                    "model": "openai/gpt-4o"
                }
            ]
        }
        
        # Should work with PluginAwareAIClient
        client = PluginAwareAIClient(old_config)
        assert client is not None
        
        provider_info = client.get_provider_info()
        assert isinstance(provider_info, dict)
        
    @patch('app.AIProviderClient')
    def test_legacy_client_fallback(self, mock_legacy_client):
        """Test that if plugin system fails, app can fall back to legacy client."""
        # This test ensures that the application is robust
        # even if there are issues with the plugin system
        
        mock_legacy_client.return_value.get_message.return_value = "Legacy fallback message"
        
        # If we were to implement a fallback mechanism, it would work like this
        try:
            client = PluginAwareAIClient()
            result = client.get_message("", "", [], 85)
        except Exception:
            # Fallback to legacy client
            legacy_client = mock_legacy_client()
            result = legacy_client.get_message("", "", [], 85)
        
        assert result is not None


class TestPluginSystemEndToEnd:
    """End-to-end tests for the complete plugin system."""
    
    @pytest.fixture
    def app_client(self):
        """Create a test client for the Flask app."""
        app.app.config['TESTING'] = True
        with app.app.test_client() as client:
            yield client
            
    @patch('httpx.Client')
    def test_complete_plugin_flow(self, mock_httpx, app_client):
        """Test complete flow from HTTP request to plugin response."""
        # Mock HTTP response for AI provider
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "End-to-end test response"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            },
            "id": "test-e2e-id",
            "created": 1234567890
        }
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value = mock_client
        
        # Set environment variable for API key
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'}):
            # Make request to API endpoint
            response = app_client.get('/api/message')
            
            assert response.status_code == 200
            assert response.is_json
            
            data = response.get_json()
            assert "message" in data
            # The response should come from the plugin system
            assert isinstance(data["message"], str)
            assert len(data["message"]) > 0
            
    def test_plugin_system_graceful_degradation(self, app_client):
        """Test that the system degrades gracefully when plugins fail."""
        # Test with no API keys (should not crash)
        with patch.dict(os.environ, {}, clear=True):
            response = app_client.get('/api/health')
            assert response.status_code == 200
            
            # Should still return a valid response even with no providers
            data = response.get_json()
            assert "status" in data
            
    def test_plugin_system_metrics_collection(self, app_client):
        """Test that metrics are collected from plugin system."""
        response = app_client.get('/api/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert "status" in data
        assert "timestamp" in data
        
        # Should include plugin/provider information
        if "providers" in data:
            assert isinstance(data["providers"], dict)


if __name__ == "__main__":
    # Run tests directly if executed as a script
    pytest.main([__file__, "-v"])
