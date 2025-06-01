#!/bin/bash
# Development helper script for AI-Ticker
# Usage: ./dev.sh [command]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "app.py" ]]; then
    log_error "Please run this script from the AI-Ticker root directory"
    exit 1
fi

# Commands
case "${1:-help}" in
    "setup")
        log_info "Setting up development environment..."
        
        # Install pre-commit
        pip install pre-commit
        pre-commit install
        
        # Install development dependencies
        pip install black isort autoflake flake8 mypy pylint pytest-cov bandit safety
        
        # Copy example config if .env doesn't exist
        if [[ ! -f ".env" ]]; then
            cp .env.example .env
            log_warning "Created .env file from example - please configure your API keys"
        fi
        
        log_success "Development environment setup complete!"
        ;;
        
    "test")
        log_info "Running test suite..."
        pytest tests/ -v --cov=. --cov-report=term-missing
        log_success "Tests completed!"
        ;;
        
    "test-plugins")
        log_info "Testing plugin system specifically..."
        pytest tests/test_plugin_system.py tests/test_builtin_providers.py tests/test_integration.py -v
        log_success "Plugin tests completed!"
        ;;
        
    "format")
        log_info "Formatting code..."
        autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive .
        isort .
        black .
        log_success "Code formatting complete!"
        ;;
        
    "lint")
        log_info "Running linters..."
        flake8 . --count --statistics
        mypy . --ignore-missing-imports || log_warning "Type checking completed with warnings"
        log_success "Linting complete!"
        ;;
        
    "security")
        log_info "Running security checks..."
        bandit -r . -c .bandit
        safety check
        log_success "Security checks complete!"
        ;;
        
    "quality")
        log_info "Running full quality checks..."
        ./dev.sh format
        ./dev.sh lint
        ./dev.sh security
        ./dev.sh test
        log_success "All quality checks passed!"
        ;;
        
    "clean")
        log_info "Cleaning up temporary files..."
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        find . -name "*.pyo" -delete 2>/dev/null || true
        find . -name ".coverage" -delete 2>/dev/null || true
        rm -rf htmlcov/ .pytest_cache/ .mypy_cache/ 2>/dev/null || true
        log_success "Cleanup complete!"
        ;;
        
    "docs")
        log_info "Generating documentation..."
        
        # Create API docs directory if it doesn't exist
        mkdir -p docs/api
        
        # Generate plugin documentation
        python -c "
import sys
sys.path.append('.')

# Import plugin modules
from plugins.base_provider import BaseAIProvider, AIProviderPlugin
from plugins.plugin_manager import PluginManager
from plugins.registry import PluginRegistry
from plugin_client import PluginAwareAIClient

# Generate documentation
docs_content = []
docs_content.append('# Plugin System API Documentation\n\n')
docs_content.append('Auto-generated documentation for the AI-Ticker plugin system.\n\n')

classes = [BaseAIProvider, AIProviderPlugin, PluginManager, PluginRegistry, PluginAwareAIClient]

for cls in classes:
    docs_content.append(f'## {cls.__name__}\n\n')
    docs_content.append(f'{cls.__doc__ or \"No description available.\"}\n\n')
    
    # Get public methods
    methods = [method for method in dir(cls) if not method.startswith('_') and callable(getattr(cls, method, None))]
    if methods:
        docs_content.append('### Public Methods:\n\n')
        for method in methods:
            try:
                method_obj = getattr(cls, method)
                docs_content.append(f'- **{method}()**: {method_obj.__doc__ or \"No description\"}\n')
            except:
                pass
        docs_content.append('\n')

with open('docs/api/plugin-system.md', 'w') as f:
    f.write(''.join(docs_content))

print('✅ Plugin system documentation generated')
"
        
        log_success "Documentation generation complete!"
        ;;
        
    "run")
        log_info "Starting development server..."
        ./run.sh
        ;;
        
    "docker")
        log_info "Building and running Docker container..."
        docker build -t ai-ticker:dev .
        docker run -d --name ai-ticker-dev -p 5000:5000 ai-ticker:dev
        log_success "Docker container running on http://localhost:5000"
        ;;
        
    "docker-stop")
        log_info "Stopping Docker container..."
        docker stop ai-ticker-dev 2>/dev/null || true
        docker rm ai-ticker-dev 2>/dev/null || true
        log_success "Docker container stopped"
        ;;
        
    "plugin-validate")
        log_info "Validating plugin system..."
        python -c "
import sys
sys.path.append('.')

try:
    # Test core plugin system
    from plugins.plugin_manager import PluginManager
    from plugins.registry import PluginRegistry
    from plugin_client import PluginAwareAIClient
    
    # Test built-in providers
    from plugins.builtin.openrouter_provider import OpenRouterProvider, OpenRouterPlugin
    from plugins.builtin.together_provider import TogetherProvider, TogetherPlugin
    from plugins.builtin.deepinfra_provider import DeepInfraProvider, DeepInfraPlugin
    
    # Initialize components
    manager = PluginManager()
    registry = PluginRegistry()
    client = PluginAwareAIClient()
    
    print('✅ All plugin system components validated successfully')
    print(f'📦 Found {len([OpenRouterPlugin, TogetherPlugin, DeepInfraPlugin])} built-in providers')
    
except Exception as e:
    print(f'❌ Plugin validation failed: {e}')
    sys.exit(1)
"
        log_success "Plugin validation complete!"
        ;;
        
    "help"|*)
        echo "AI-Ticker Development Helper"
        echo ""
        echo "Usage: ./dev.sh [command]"
        echo ""
        echo "Available commands:"
        echo "  setup          - Set up development environment"
        echo "  test           - Run full test suite"
        echo "  test-plugins   - Test plugin system only"
        echo "  format         - Format code with black/isort"
        echo "  lint           - Run linters (flake8, mypy)"
        echo "  security       - Run security checks (bandit, safety)"
        echo "  quality        - Run all quality checks"
        echo "  clean          - Clean temporary files"
        echo "  docs           - Generate documentation"
        echo "  run            - Start development server"
        echo "  docker         - Build and run Docker container"
        echo "  docker-stop    - Stop Docker container"
        echo "  plugin-validate - Validate plugin system"
        echo "  help           - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./dev.sh setup    # First time setup"
        echo "  ./dev.sh quality  # Run all checks before commit"
        echo "  ./dev.sh test     # Run tests"
        ;;
esac
