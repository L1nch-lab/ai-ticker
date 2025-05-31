# Plugin Development Guide

This guide explains how to create custom AI provider plugins for the AI-Ticker system.

## Overview

The AI-Ticker plugin system allows you to add custom AI providers without modifying the core application code. This makes the system extensible and maintainable.

## Plugin Architecture

### Core Components

1. **BaseAIProvider**: Abstract base class that all providers must inherit from
2. **AIProviderPlugin**: Plugin wrapper that contains metadata and provider class
3. **ProviderConfig**: Configuration dataclass for provider settings
4. **AIResponse**: Standardized response format

### Plugin Structure

```python
from plugins.base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse
from typing import Optional, List

class MyCustomProvider(BaseAIProvider):
    """Your custom AI provider implementation."""
    
    @property
    def provider_name(self) -> str:
        return "MyCustomProvider"
    
    @property 
    def supported_models(self) -> List[str]:
        return ["my-model-1", "my-model-2"]
    
    def initialize(self) -> bool:
        # Initialize your provider (API connections, auth, etc.)
        return True
    
    def generate_message(self, system_prompt: str, user_prompt: str) -> Optional[AIResponse]:
        # Generate AI response using your provider
        pass
    
    def health_check(self) -> bool:
        # Check if your provider is healthy
        return True

# Create plugin instance
MyPlugin = AIProviderPlugin(
    provider_class=MyCustomProvider,
    metadata={
        "name": "My Custom AI Provider",
        "version": "1.0.0",
        "author": "Your Name",
        "description": "Description of your provider",
        "requires": ["httpx>=0.27.0"],  # Dependencies
        "category": "custom",
        "api_version": "v1",
        "supported_features": ["chat_completion"]
    }
)
```

## Step-by-Step Guide

### 1. Create Your Provider Class

Create a new Python file in `plugins/custom/` directory:

```python
# plugins/custom/my_provider.py
import logging
import httpx
from typing import Optional, List

from plugins.base_provider import BaseAIProvider, AIProviderPlugin, ProviderConfig, AIResponse

logger = logging.getLogger(__name__)

class MyCustomProvider(BaseAIProvider):
    """Custom AI provider implementation."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
        
    @property
    def provider_name(self) -> str:
        return "MyCustomProvider"
    
    @property
    def supported_models(self) -> List[str]:
        return [
            "my-gpt-model",
            "my-claude-model",
            "my-custom-model"
        ]
    
    def initialize(self) -> bool:
        """Initialize the provider."""
        try:
            if not self.validate_config():
                return False
            
            # Create HTTP client with headers
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            # Add any extra headers from config
            if self.config.extra_headers:
                headers.update(self.config.extra_headers)
            
            self.client = httpx.Client(
                base_url=self.config.base_url,
                headers=headers,
                timeout=30.0
            )
            
            self.logger.info(f"Initialized {self.provider_name} with model: {self.config.model}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.provider_name}: {e}")
            return False
    
    def generate_message(self, system_prompt: str, user_prompt: str) -> Optional[AIResponse]:
        """Generate a message using your AI API."""
        try:
            if not self.client:
                self.logger.error("Provider not initialized")
                return None
            
            # Prepare the request payload (adjust for your API)
            payload = {
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
            
            # Make API request
            response = self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract response content (adjust for your API format)
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            # Create standardized response
            return AIResponse(
                content=content,
                provider_name=self.provider_name,
                model=self.config.model,
                usage=usage,
                metadata={
                    "response_id": data.get("id"),
                    "created": data.get("created"),
                    "finish_reason": data["choices"][0].get("finish_reason")
                }
            )
            
        except Exception as e:
            self.logger.error(f"{self.provider_name} generation error: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check if the provider is healthy."""
        try:
            if not self.client:
                return False
            
            # Make a simple health check request
            response = self.client.get("/health")  # Adjust endpoint
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"{self.provider_name} health check failed: {e}")
            return False
    
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        if not super().validate_config():
            return False
        
        # Add custom validation
        if self.config.model not in self.supported_models:
            self.logger.error(f"Unsupported model: {self.config.model}")
            return False
        
        return True

# Plugin metadata
PLUGIN_METADATA = {
    "name": "My Custom AI Provider",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "A custom AI provider for demonstration",
    "requires": ["httpx>=0.27.0"],
    "category": "custom",
    "api_version": "v1",
    "supported_features": ["chat_completion", "health_check"]
}

# Create plugin instance
MyCustomPlugin = AIProviderPlugin(
    provider_class=MyCustomProvider,
    metadata=PLUGIN_METADATA
)
```

### 2. Test Your Plugin

Create a test script to verify your plugin works:

```python
# test_my_plugin.py
from plugins.custom.my_provider import MyCustomProvider, MyCustomPlugin
from plugins.base_provider import ProviderConfig

# Test configuration
config = ProviderConfig(
    name="My Custom Provider",
    api_key="your-api-key-here",
    base_url="https://your-api.com/v1",
    model="my-gpt-model",
    max_tokens=512,
    temperature=0.7
)

# Test provider
provider = MyCustomProvider(config)

if provider.initialize():
    print("✅ Provider initialized successfully")
    
    # Test health check
    if provider.health_check():
        print("✅ Health check passed")
    else:
        print("❌ Health check failed")
    
    # Test message generation
    response = provider.generate_message(
        "You are a helpful assistant.",
        "Tell me about AI."
    )
    
    if response:
        print(f"✅ Generated response: {response.content}")
    else:
        print("❌ Failed to generate response")
else:
    print("❌ Failed to initialize provider")
```

### 3. Plugin Configuration

Add your plugin configuration to `plugin_config.json`:

```json
{
  "plugins": {
    "my_custom_provider": {
      "enabled": true,
      "config": {
        "name": "My Custom Provider",
        "api_key": "${MY_CUSTOM_API_KEY}",
        "base_url": "https://your-api.com/v1",
        "model": "my-gpt-model",
        "max_tokens": 512,
        "temperature": 0.7
      }
    }
  }
}
```

### 4. Environment Variables

Add necessary environment variables to your `.env` file:

```bash
# My Custom Provider
MY_CUSTOM_API_KEY=your_actual_api_key_here
```

## Best Practices

### Error Handling

Always handle errors gracefully:

```python
def generate_message(self, system_prompt: str, user_prompt: str) -> Optional[AIResponse]:
    try:
        # Your implementation
        pass
    except httpx.HTTPError as e:
        self.logger.error(f"HTTP error: {e}")
        return None
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        return None
```

### Logging

Use proper logging throughout your plugin:

```python
import logging

class MyProvider(BaseAIProvider):
    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def some_method(self):
        self.logger.info("Starting operation")
        self.logger.debug("Debug information")
        self.logger.warning("Warning message")
        self.logger.error("Error occurred")
```

### Configuration Validation

Validate configuration thoroughly:

```python
def validate_config(self) -> bool:
    if not super().validate_config():
        return False
    
    # Check required fields
    if not self.config.api_key:
        self.logger.error("API key is required")
        return False
    
    if not self.config.base_url:
        self.logger.error("Base URL is required")
        return False
    
    # Validate model
    if self.config.model not in self.supported_models:
        self.logger.error(f"Unsupported model: {self.config.model}")
        return False
    
    return True
```

### Resource Management

Properly manage resources:

```python
def __del__(self):
    """Cleanup when provider is destroyed."""
    if hasattr(self, 'client') and self.client:
        self.client.close()

def initialize(self) -> bool:
    try:
        # Initialize resources
        self.client = httpx.Client()
        return True
    except Exception as e:
        # Clean up on failure
        if hasattr(self, 'client') and self.client:
            self.client.close()
        return False
```

## Plugin Metadata

### Required Fields

- `name`: Human-readable plugin name
- `version`: Plugin version (semantic versioning)
- `author`: Plugin author/maintainer
- `description`: Brief description of the plugin

### Optional Fields

- `requires`: List of required dependencies
- `category`: Plugin category (e.g., "official", "community", "custom")
- `api_version`: API version compatibility
- `supported_features`: List of supported features
- `homepage`: Plugin homepage URL
- `documentation`: Documentation URL
- `license`: Plugin license

## Integration with AI-Ticker

### Plugin Discovery

The system automatically discovers plugins in:
- `plugins/builtin/`: Built-in providers
- `plugins/custom/`: Custom providers
- External plugin directories (if configured)

### Plugin Loading

Plugins are loaded during application startup:

1. Plugin discovery scans directories
2. Plugin validation checks metadata and structure
3. Plugin registration adds valid plugins to registry
4. Provider initialization creates provider instances

### Configuration Priority

Configuration is loaded in this order (later overrides earlier):
1. Default configuration
2. Plugin configuration file
3. Environment variables
4. Runtime configuration

## Debugging

### Enable Debug Logging

Set environment variable:
```bash
export LOG_LEVEL=DEBUG
```

### Check Plugin Status

Use the API endpoints to check plugin status:

```bash
# List all plugins
curl http://localhost:5000/api/plugins

# List all providers
curl http://localhost:5000/api/providers

# Reload providers
curl -X POST http://localhost:5000/api/providers/reload
```

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Configuration Errors**: Validate your configuration format
3. **API Errors**: Check API keys and endpoints
4. **Permission Errors**: Ensure proper file permissions

## Examples

See the following examples in the codebase:

- `plugins/custom/mock_provider.py`: Simple mock provider
- `plugins/builtin/openrouter_provider.py`: OpenRouter implementation
- `plugins/builtin/together_provider.py`: Together AI implementation
- `plugins/builtin/deepinfra_provider.py`: DeepInfra implementation

## Support

For questions or issues:

1. Check the logs for error messages
2. Review the plugin validation results
3. Test your plugin with the mock provider example
4. Consult the API documentation

## Contributing

To contribute your plugin to the main repository:

1. Follow the coding standards
2. Include comprehensive tests
3. Add documentation
4. Submit a pull request

---

Happy plugin development! 🚀
