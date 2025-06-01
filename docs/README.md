# AI-Ticker - Comprehensive Documentation

## Table of Contents

1. [Plugin System](#plugin-system)
2. [Configuration](#configuration)
3. [Testing](#testing)
4. [Development](#development)
5. [Deployment](#deployment)
6. [Troubleshooting](#troubleshooting)

## Plugin System

### Overview
The AI-Ticker plugin system enables modular AI providers through dynamic plugin loading.

### Available Providers
- **OpenRouter** - Multi-model platform with access to various AI models
- **Together AI** - Open-source models with competitive pricing
- **DeepInfra** - Serverless GPU inference platform
- **Anthropic** - Claude models for advanced reasoning
- **Groq** - Ultra-fast inference for real-time applications
- **Google Gemini** - Google's advanced language models
- **Mistral** - European AI provider with excellent performance
- **You.com** - Search-enhanced AI responses

### Plugin Development
See [PLUGIN_DEVELOPMENT.md](../PLUGIN_DEVELOPMENT.md) for detailed guide on developing custom plugins.

### Plugin Structure
```
plugins/
├── base_provider.py      # Base interface for all providers
├── registry.py           # Plugin registry (thread-safe)
├── plugin_manager.py     # Plugin lifecycle management
├── integration.py        # Integration with main app
├── builtin/             # Built-in providers
│   ├── openrouter_provider.py
│   ├── together_provider.py
│   └── deepinfra_provider.py
└── custom/              # Custom user plugins
```

## Configuration

### Environment Variables (.env)
```bash
# API keys (configure at least one)
OPENROUTER_API_KEY=your-openrouter-api-key
TOGETHER_API_KEY=your-together-api-key
DEEPINFRA_API_KEY=your-deepinfra-api-key

# Prompt configuration
PROMPT_PROFILE=default
SYSTEM_PROMPT=You are an AI assistant...
USER_PROMPT=Tell me something about AI.

# Cache settings
CACHE_FILE=message_cache.json
FUZZY_THRESHOLD=85
CACHE_PROBABILITY=0.6
MAX_CACHE_SIZE=200

# Performance
COMPRESS_LEVEL=6
API_TIMEOUT=30
RATE_LIMIT_DEFAULT=100 per hour
```

### Plugin Configuration (plugin_config.json)
```json
{
  "enabled": true,
  "auto_discovery": true,
  "builtin_enabled": true,
  "custom_plugins_path": "plugins/custom",
  "timeout": 30
}
```

## Testing

### Running Test Suite
```bash
# All tests
python -m pytest tests/ -v

# Plugin system tests only
python -m pytest tests/test_plugin_system.py -v

# Built-in provider tests only
python -m pytest tests/test_builtin_providers.py -v

# With coverage report
python -m pytest tests/ --cov=. --cov-report=html
```

### Test Structure
- `test_app.py` - Main app tests
- `test_plugin_system.py` - Plugin system core
- `test_builtin_providers.py` - Built-in providers
- `test_integration.py` - Integration tests

### Test Environment
For testing without real API keys:
```bash
cp .env.example .env
# Use test keys
OPENROUTER_API_KEY=test_key_openrouter
```

## Development

### Local Development
```bash
# Clone repository
git clone <repo-url>
cd ai-ticker

# Install dependencies
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Edit .env with real API keys

# Start development server
python app.py
```

### Developing Custom Plugins
1. Create class inheriting from `BaseAIProvider`
2. Implement required methods
3. Place plugin in `plugins/custom/`
4. Automatic discovery by plugin manager

### API Endpoints
- `GET /` - Main dashboard
- `GET /api/message` - Generate new AI message
- `GET /api/health` - System status
- `GET /api/providers` - Provider information
- `POST /api/providers/reload` - Reload providers

## Deployment

### Development
```bash
# Direct with Python
python app.py

# With development script
./run.sh
```

### Production
```bash
# With Gunicorn
./start-production.sh

# With Docker
docker-compose up -d

# With systemd (see SECURITY.md)
```

### Docker Deployment
```bash
# Build image
docker build -t ai-ticker .

# Start container
docker run -d \
  --name ai-ticker \
  -p 8080:8080 \
  -e OPENROUTER_API_KEY=your-key \
  ai-ticker
```

### Environment Requirements
- Python 3.9+
- 512MB RAM (minimum)
- Internet connection for AI APIs
- Optional reverse proxy (nginx/apache)

### Monitoring
- Health-Check: `GET /api/health`
- Logs: Standard Python logging
- Metrics: Provider status via API

### Security
See [SECURITY.md](../SECURITY.md) for detailed security guidelines:
- Use HTTPS in production
- Manage API keys securely
- Configure rate limiting
- Security headers enabled

## Troubleshooting

### Common Issues
1. **No providers available**
   - Check API keys in .env
   - Test network connection

2. **Plugin not loading**
   - Syntax error in plugin file
   - BaseAIProvider not correctly implemented

3. **Tests failing**
   - Use test API keys
   - Check mocks for external APIs

### Debug Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Check logs
```bash
# Current logs
tail -f logs/ai-ticker.log

# Provider status
curl http://localhost:8080/api/health
```
