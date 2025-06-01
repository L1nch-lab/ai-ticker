# AI-Ticker

🤖 A modern Flask dashboard for dynamic AI-generated messages with comprehensive plugin system.

## ✨ Features

- **🔌 Modular AI Providers** - OpenRouter, Together AI, DeepInfra, Anthropic, Groq, Gemini, Mistral
- **🧩 Plugin System** - Easy extension with custom providers
- **🧠 Smart Caching** - Intelligent duplicate detection and message optimization
- **⚡ Rate Limiting** - Built-in protection against API abuse
- **🐳 Docker Ready** - Production-ready containerized deployment
- **🔒 Security First** - CSP, CSRF protection, secure headers
- **📊 Health Monitoring** - Comprehensive health checks and status reporting

## 🚀 Quick Start

```bash
# Clone repository
git clone <repository-url>
cd ai-ticker

# Install dependencies
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Add API keys to .env

# Start application
python app.py
# → http://localhost:8080
```

## ⚙️ Configuration

Configure at least one API key in `.env`:

```bash
# AI Provider API Keys (configure at least one)
OPENROUTER_API_KEY=your-openrouter-api-key
TOGETHER_API_KEY=your-together-api-key
DEEPINFRA_API_KEY=your-deepinfra-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key
MISTRAL_API_KEY=your-mistral-api-key

# Optional Configuration
FLASK_HOST=127.0.0.1
FLASK_PORT=8080
FLASK_ENV=production
CACHE_SIZE=100
REQUEST_TIMEOUT=30
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | Main dashboard interface |
| `/api/message` | GET | Generate new AI message |
| `/api/health` | GET | System health status |
| `/api/providers` | GET | Available AI providers info |
| `/api/plugins` | GET | Loaded plugin information |

## 🏗️ Development

```bash
# Run tests
python -m pytest tests/ -v

# Development server
export FLASK_ENV=development
python app.py

# Docker
docker-compose up -d
```

## 🔌 Plugin Development

1. Create class inheriting from `BaseAIProvider`
2. Place in `plugins/custom/` directory
3. Automatic discovery on application restart

See [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md) for detailed instructions.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details on:

- Development setup and workflow
- Code style and quality standards
- Testing requirements
- Submitting pull requests

## 📚 Documentation

- **[Complete Documentation](docs/README.md)** - Detailed setup and usage guide
- **[Plugin Development](docs/PLUGIN_DEVELOPMENT.md)** - Create custom AI providers
- **[Contributing Guide](docs/CONTRIBUTING.md)** - Development workflow and standards
- **[Security Documentation](docs/SECURITY.md)** - Security features and best practices

## 📋 Requirements

- **Python**: 3.9+ (Python 3.11+ recommended)
- **API Keys**: At least one AI provider API key
- **Network**: Internet connection for AI APIs
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB free space

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
