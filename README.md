# AI-Ticker

🤖 A modern Flask dashboard for dynamic AI-generated messages with plugin system.

## ✨ Features

- **Modular AI Providers** - OpenRouter, Together AI, DeepInfra
- **Plugin System** - Easy extension with custom providers
- **Smart Caching** - Intelligent duplicate detection
- **Rate Limiting** - Protection against API abuse
- **Docker Ready** - Production-ready containers

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
OPENROUTER_API_KEY=your-openrouter-api-key
TOGETHER_API_KEY=your-together-api-key
DEEPINFRA_API_KEY=your-deepinfra-api-key
```

## 🔧 API Endpoints

- `GET /` - Dashboard
- `GET /api/message` - New AI message
- `GET /api/health` - System status
- `GET /api/providers` - Provider info

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
2. Place in `plugins/custom/`
3. Automatic discovery on restart

## 📚 Documentation

Detailed documentation: [docs/README.md](docs/README.md)

## 📋 Requirements

- Python 3.9+
- At least one AI provider API key
- Internet connection

## 📄 License

MIT License - see [LICENSE](LICENSE)
