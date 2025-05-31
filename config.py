"""
Configuration module for AI-Ticker application.
Handles environment variables, validation, and default settings.
"""
import os
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULTS = {
    'FUZZY_THRESHOLD': 85,
    'CACHE_PROBABILITY': 0.6,
    'LAST_LIMIT': 3,
    'MAX_CACHE_SIZE': 200,
    'CACHE_FILE': 'message_cache.json',
    'LAST_FILE': 'last_messages.json',
    'PROMPTS_FILE': 'prompts.json',
    'PROMPT_PROFILE': 'default',
    'DEFAULT_SYSTEM_PROMPT': 'You are an AI assistant. Provide a short, interesting, or thought-provoking statement about AI, technology, or the future.',
    'DEFAULT_USER_PROMPT': 'Tell me something about AI.',
    'COMPRESS_LEVEL': 6,
    'COMPRESS_MIN_SIZE': 500,
    'RATE_LIMIT_DEFAULT': '100 per hour',
    'RATE_LIMIT_API': '10 per minute',
    'API_TIMEOUT': 30,
}

class Config:
    """Configuration class for AI-Ticker application."""
    
    def __init__(self):
        self.providers = self._load_providers()
        self.fuzzy_threshold = self._get_int('FUZZY_THRESHOLD')
        self.cache_probability = self._get_float('CACHE_PROBABILITY')
        self.last_limit = self._get_int('LAST_LIMIT')
        self.max_cache_size = self._get_int('MAX_CACHE_SIZE')
        self.cache_file = self._get_str('CACHE_FILE')
        self.last_file = self._get_str('LAST_FILE')
        self.prompts_file = self._get_str('PROMPTS_FILE')
        self.prompt_profile = self._get_str('PROMPT_PROFILE')
        self.system_prompt = self._get_str('SYSTEM_PROMPT', 'DEFAULT_SYSTEM_PROMPT')
        self.user_prompt = self._get_str('USER_PROMPT', 'DEFAULT_USER_PROMPT')
        self.compress_level = self._get_int('COMPRESS_LEVEL')
        self.compress_min_size = self._get_int('COMPRESS_MIN_SIZE')
        self.rate_limit_default = self._get_str('RATE_LIMIT_DEFAULT')
        self.rate_limit_api = self._get_str('RATE_LIMIT_API')
        self.api_timeout = self._get_int('API_TIMEOUT')
        self.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
        
        self._validate()
    
    def _get_str(self, key: str, default_key: str = None) -> str:
        """Get string value from environment or defaults."""
        default = DEFAULTS.get(default_key or key, '')
        return os.getenv(key, default)
    
    def _get_int(self, key: str) -> int:
        """Get integer value from environment or defaults."""
        value = os.getenv(key, str(DEFAULTS[key]))
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid {key}: {value}, using default: {DEFAULTS[key]}")
            return DEFAULTS[key]
    
    def _get_float(self, key: str) -> float:
        """Get float value from environment or defaults."""
        value = os.getenv(key, str(DEFAULTS[key]))
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Invalid {key}: {value}, using default: {DEFAULTS[key]}")
            return DEFAULTS[key]
    
    def _load_providers(self) -> List[Dict[str, Any]]:
        """Load and validate API providers."""
        all_providers = [
            {
                "name": "OpenRouter",
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "model": "openai/gpt-4o"
            },
            {
                "name": "Together",
                "base_url": "https://api.together.xyz/v1",
                "api_key": os.getenv("TOGETHER_API_KEY"),
                "model": "meta-llama/Llama-3.1-70B-Instruct-Turbo"
            },
            {
                "name": "DeepInfra",
                "base_url": "https://api.deepinfra.com/v1/openai",
                "api_key": os.getenv("DEEPINFRA_API_KEY"),
                "model": "meta-llama/Meta-Llama-3.1-70B-Instruct"
            }
        ]
        
        # Filter providers with valid API keys
        valid_providers = [p for p in all_providers if p["api_key"]]
        
        if not valid_providers:
            logger.warning("⚠️ No API providers configured! Set at least one API key.")
        else:
            provider_names = [p["name"] for p in valid_providers]
            logger.info(f"Configured providers: {', '.join(provider_names)}")
        
        return valid_providers
    
    def _validate(self):
        """Validate configuration values."""
        issues = []
        
        if not (0 <= self.cache_probability <= 1):
            issues.append("CACHE_PROBABILITY must be between 0 and 1")
        
        if not (0 <= self.fuzzy_threshold <= 100):
            issues.append("FUZZY_THRESHOLD must be between 0 and 100")
        
        if self.last_limit < 1:
            issues.append("LAST_LIMIT must be at least 1")
        
        if self.max_cache_size < 1:
            issues.append("MAX_CACHE_SIZE must be at least 1")
        
        if self.compress_level not in range(1, 10):
            issues.append("COMPRESS_LEVEL must be between 1 and 9")
        
        if self.api_timeout < 1:
            issues.append("API_TIMEOUT must be at least 1 second")
        
        if issues:
            for issue in issues:
                logger.error(f"Configuration error: {issue}")
            raise ValueError("Configuration validation failed")
        
        logger.info("Configuration validation passed")

# Create global config instance
config = Config()
