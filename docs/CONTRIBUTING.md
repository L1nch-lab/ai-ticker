# Contributing to AI-Ticker

Thank you for your interest in contributing to AI-Ticker! This guide will help you get started with development and ensure your contributions align with our project standards.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (Python 3.13 recommended)
- Git
- Basic understanding of Flask and plugin architectures

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/ai-ticker.git
   cd ai-ticker
   ```

2. **Set up development environment:**
   ```bash
   ./dev.sh setup
   ```
   This will:
   - Install all dependencies
   - Set up pre-commit hooks
   - Configure development tools

3. **Verify setup:**
   ```bash
   ./dev.sh test
   ```

## 🛠️ Development Workflow

### Code Quality Standards

We maintain high code quality through automated checks:

- **Formatting**: Black (line length: 88)
- **Import sorting**: isort
- **Linting**: flake8, mypy
- **Security**: bandit, safety
- **Testing**: pytest with coverage

### Pre-commit Hooks

Pre-commit hooks automatically run quality checks:

```bash
# Install hooks (done automatically in setup)
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Development Commands

Use the development helper script for common tasks:

```bash
# Run full validation suite
./dev.sh full-check

# Format code
./dev.sh format

# Run tests with coverage
./dev.sh test-coverage

# Test plugin system specifically
./dev.sh plugin-test

# Security checks
./dev.sh security

# Performance benchmarks
./dev.sh performance
```

## 🔌 Plugin Development

AI-Ticker uses a robust plugin system. Here's how to create plugins:

### Plugin Structure

```
plugins/
├── your_plugin/
│   ├── __init__.py
│   ├── plugin.py          # Main plugin logic
│   ├── config.yaml        # Plugin configuration
│   └── requirements.txt   # Plugin dependencies
└── tests/
    └── test_your_plugin.py
```

### Plugin Template

```python
# plugins/your_plugin/plugin.py
from typing import Dict, Any, Optional
from plugins.base_plugin import BasePlugin

class YourPlugin(BasePlugin):
    """Your custom AI provider plugin."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        
    def get_stock_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Analyze stock using your AI service."""
        # Implementation here
        pass
        
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        return 'api_key' in config
```

### Plugin Configuration

```yaml
# plugins/your_plugin/config.yaml
name: "Your Plugin"
version: "1.0.0"
description: "Description of your plugin"
author: "Your Name"
website: "https://your-website.com"
enabled: true
priority: 10

settings:
  api_key:
    type: "string"
    required: true
    description: "Your API key"
  
  model:
    type: "string"
    default: "default-model"
    description: "AI model to use"
```

### Testing Plugins

```python
# tests/test_your_plugin.py
import pytest
from plugins.your_plugin.plugin import YourPlugin

def test_plugin_initialization():
    config = {'api_key': 'test-key'}
    plugin = YourPlugin(config)
    assert plugin.api_key == 'test-key'

def test_stock_analysis():
    config = {'api_key': 'test-key'}
    plugin = YourPlugin(config)
    result = plugin.get_stock_analysis('AAPL')
    assert result is not None
```

## 📝 Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks
- `plugin`: Plugin-related changes

**Examples:**
```
feat(plugins): add OpenAI GPT-4 plugin
fix(api): resolve rate limiting issue
docs(readme): update installation instructions
plugin(anthropic): improve error handling
```

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `plugin/name` - Plugin development

## 🧪 Testing

### Test Organization

```
tests/
├── unit/                  # Unit tests
├── integration/           # Integration tests
├── plugins/              # Plugin-specific tests
├── performance/          # Performance benchmarks
└── fixtures/             # Test data
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch
from your_module import YourClass

class TestYourClass:
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {'key': 'value'}
        self.instance = YourClass(self.config)
    
    def test_method_success(self):
        """Test successful method execution."""
        result = self.instance.method()
        assert result == expected_value
    
    @patch('your_module.external_service')
    def test_method_with_mock(self, mock_service):
        """Test with mocked external service."""
        mock_service.return_value = {'data': 'test'}
        result = self.instance.method()
        assert result['data'] == 'test'
```

### Coverage Requirements

- Minimum 80% code coverage
- 100% coverage for critical paths
- All new features must include tests

## 📚 Documentation

### Code Documentation

```python
def analyze_stock(symbol: str, timeframe: str = "1d") -> Dict[str, Any]:
    """
    Analyze stock performance using AI insights.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        timeframe: Analysis timeframe ('1d', '1w', '1m', '1y')
        
    Returns:
        Dictionary containing analysis results:
        - sentiment: Market sentiment score
        - prediction: Price prediction
        - confidence: Confidence level (0-1)
        - reasoning: AI reasoning for the analysis
        
    Raises:
        ValueError: If symbol is invalid
        APIError: If external API call fails
        
    Example:
        >>> result = analyze_stock("AAPL", "1w")
        >>> print(result['sentiment'])
        0.75
    """
```

### API Documentation

Update API documentation for new endpoints:

```python
@app.route('/api/v1/analyze/<symbol>', methods=['GET'])
def analyze_endpoint(symbol: str):
    """
    Analyze stock symbol.
    
    ---
    parameters:
      - name: symbol
        in: path
        type: string
        required: true
        description: Stock ticker symbol
      - name: timeframe
        in: query
        type: string
        default: "1d"
        description: Analysis timeframe
    responses:
      200:
        description: Analysis results
        schema:
          type: object
          properties:
            sentiment:
              type: number
            prediction:
              type: object
    """
```

## 🚀 Pull Request Process

### Before Submitting

1. **Run full validation:**
   ```bash
   ./dev.sh full-check
   ```

2. **Update documentation** if needed

3. **Add tests** for new functionality

4. **Update CHANGELOG.md** with your changes

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Plugin compatibility verified (if applicable)
- [ ] Security considerations addressed

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Plugin addition/modification

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Plugin Impact
- [ ] No plugin impact
- [ ] Plugin API changes documented
- [ ] Backward compatibility maintained

## Additional Notes
Any additional context or considerations
```

## 🔄 CI/CD Pipeline

Our automated workflows ensure code quality:

### Workflows

1. **Test Coverage** - Multi-Python version testing
2. **Code Quality** - Linting and formatting checks
3. **Security** - Vulnerability scanning
4. **Plugin Validation** - Plugin system testing
5. **Performance** - Benchmark testing
6. **Dependency Updates** - Automated dependency management

### Workflow Triggers

- **Push to main/develop**: Full validation
- **Pull requests**: Comprehensive testing
- **Weekly**: Dependency updates
- **Tags**: Release automation

## 📋 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes

### Release Steps

1. **Update version** in relevant files
2. **Update CHANGELOG.md**
3. **Create release tag**
4. **Automated workflows** handle the rest

## 🤝 Community

### Getting Help

- **Issues**: Report bugs or request features
- **Discussions**: Ask questions or share ideas
- **Discord**: Join our community chat (if available)

### Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's license.

---

Thank you for contributing to AI-Ticker! 🎉
