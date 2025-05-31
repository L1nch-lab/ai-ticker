# AI-Ticker Dashboard 🤖

A modern Flask-based dashboard that displays AI-generated messages with pathfinding visualization. Features multiple AI provider support, intelligent caching, and security-focused architecture.

## ✨ Features

- **Multi-Provider AI Integration**: OpenRouter, Together AI, DeepInfra
- **Smart Caching**: Fuzzy matching to avoid repetitive messages
- **Security First**: CSP nonces, rate limiting, input validation
- **Modern UI**: Responsive design with speech bubble animations
- **Pathfinding Visualizer**: Interactive A* algorithm demonstration
- **Production Ready**: Comprehensive logging, error handling, and monitoring
- **Security Hardened**: Passes security scans, secure defaults, and best practices

## 🔒 Security Features

- **Cryptographically Secure**: Uses `secrets` module for random operations
- **Configurable Host Binding**: Secure localhost default, production-ready options
- **Content Security Policy**: XSS protection with nonce-based CSP
- **Rate Limiting**: Protection against abuse and DoS attacks
- **Input Validation**: Comprehensive request validation and sanitization
- **Security Headers**: Full security header implementation with Talisman

See [SECURITY.md](SECURITY.md) for detailed security documentation.

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Virtual environment (recommended)
- At least one AI provider API key

### Installation

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd ai-ticker
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example-new .env
   # Edit .env with your API keys and preferences
   ```

4. **Run the application**:
   ```bash
   ./run.sh
   # Or directly: python app-cleaned.py
   ```

5. **Open your browser**:
   Navigate to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `dev-key-change-in-production` |
| `OPENROUTER_API_KEY` | OpenRouter API key | - |
| `TOGETHER_API_KEY` | Together AI API key | - |
| `DEEPINFRA_API_KEY` | DeepInfra API key | - |
| `PROMPT_PROFILE` | Active prompt profile | `default` |
| `FUZZY_THRESHOLD` | Similarity threshold (0-100) | `85` |
| `CACHE_PROBABILITY` | Probability of using cache | `0.6` |
| `RATE_LIMIT_API` | API endpoint rate limit | `10 per minute` |

### Prompt Profiles

Configure different AI personalities in `prompts.json`:

```json
{
  "default": {
    "system": "You are an AI assistant...",
    "user": "Tell me something about AI."
  },
  "creative_writer": {
    "system": "You are a creative writer...",
    "user": "Write a short story about technology."
  }
}
```

## 🏗️ Architecture

### Key Components

- **`app-cleaned.py`**: Main application with clean, modular structure
- **`config.py`**: Centralized configuration management
- **`templates/index-cleaned.html`**: Improved template with security features
- **`static/style-expanded.css`**: Comprehensive, maintainable CSS

### Security Features

- **Content Security Policy**: Nonce-based CSP for scripts and styles
- **Rate Limiting**: Configurable limits per endpoint
- **Input Validation**: Comprehensive validation and sanitization
- **Error Handling**: Graceful degradation and logging

### Caching Strategy

1. **Message Cache**: Stores successful AI responses
2. **Recent Tracking**: Prevents immediate repetition
3. **Fuzzy Matching**: Avoids similar content using RapidFuzz
4. **Fallback Logic**: Graceful degradation when APIs fail

## 🔌 API Endpoints

### `GET /`
Main dashboard interface

### `GET /api/message`
Get an AI-generated message
- **Rate Limited**: 10 requests per minute
- **Response**: `{"message": "AI-generated content"}`

### `GET /api/health`
Health check endpoint
- **Response**: `{"status": "healthy", "providers": 2, "cache_size": 150}`

### `GET /api/docs`
Interactive API documentation (Swagger UI)

## 🎨 UI Components

### Speech Bubble
- Positioned above robot image
- Smooth animations and transitions
- Responsive design for mobile devices
- Loading states with visual feedback

### Pathfinding Visualizer
- Interactive A* algorithm demonstration
- Clickable canvas for manual restart
- Auto-refresh every 20 seconds
- Color-coded visualization states

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Test categories:
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end functionality
- **Security Tests**: CSP and rate limiting validation

## 🚀 Deployment

### Development
```bash
./run.sh
```

### Production (Docker)
```bash
docker build -t ai-ticker .
docker run -p 5000:5000 --env-file .env ai-ticker
```

### Production (Manual)
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 app-cleaned:app
```

## 📊 Monitoring

### Logging
- Structured logging with correlation IDs
- Configurable log levels
- File and console output options

### Health Checks
- Provider availability monitoring
- Cache size tracking
- Error rate monitoring

### Metrics
- API request rates
- Cache hit ratios
- Provider response times

## 🛠️ Development

### Code Structure
```
ai-ticker/
├── app-cleaned.py          # Main application (improved)
├── config.py              # Configuration management
├── prompts.json           # AI prompt profiles
├── requirements.txt       # Dependencies
├── static/
│   ├── style-expanded.css # Improved styles
│   └── ...
├── templates/
│   └── index-cleaned.html # Improved template
└── tests/
    └── test_cleaned.py    # Test suite
```

### Best Practices
- **Type Hints**: Full type annotation support
- **Error Handling**: Comprehensive exception management
- **Security**: OWASP recommendations followed
- **Performance**: Optimized caching and compression
- **Maintainability**: Modular, documented code

## 🔄 Migration from Original

The cleaned version includes:

1. **Improved Security**: CSP nonces instead of `unsafe-inline`
2. **Better Error Handling**: Graceful degradation and logging
3. **Modular Architecture**: Separated concerns and classes
4. **Enhanced UI**: Better accessibility and animations
5. **Configuration Management**: Centralized config with validation
6. **Production Features**: Health checks, metrics, proper logging

## 📝 License

[Your License Here]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🆘 Troubleshooting

### Common Issues

**No messages loading**:
- Check API keys in `.env`
- Verify network connectivity
- Check logs for API errors

**CSS not loading**:
- Ensure `cssmin` is installed
- Check Flask-Assets configuration
- Verify static file permissions

**Rate limiting errors**:
- Adjust rate limits in configuration
- Check if multiple instances are running

### Support

- Check the logs: `tail -f ai-ticker.log`
- Health check: `curl http://localhost:5000/api/health`
- API docs: `http://localhost:5000/api/docs`

---

*Built with ❤️ and modern Python practices*
