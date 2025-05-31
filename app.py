"""
AI-Ticker - A Flask dashboard displaying AI-generated messages in a speech bubble.
Enhanced with security, caching, and multiple API providers.
"""
import os
import json
import logging
import secrets
import time
from typing import Optional, List, Dict, Any

from flask import Flask, render_template, jsonify, g
from openai import OpenAI
from rapidfuzz import fuzz
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_assets import Environment, Bundle
from flasgger import Swagger

from config import config
from plugin_client import PluginAwareAIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        # Uncomment for file logging:
        # logging.FileHandler("ai-ticker.log"),
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.secret_key


# Security headers with CSP nonces
@app.before_request
def generate_nonce():
    """Generate a unique nonce for each request for CSP."""
    g.nonce = secrets.token_urlsafe(16)


# Configure Talisman security headers
talisman = Talisman(
    app,
    force_https=False,  # Set to True in production
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",  # Temporarily allow inline scripts
        'style-src': "'self' 'unsafe-inline'",   # Temporarily allow inline styles
        'img-src': "'self' data:",
        'object-src': "'none'",
        'base-uri': "'self'",
        'form-action': "'self'"
    }
)

# Configure compression
app.config.update({
    'COMPRESS_MIMETYPES': ['text/html', 'text/css', 'application/json', 'application/javascript'],
    'COMPRESS_LEVEL': config.compress_level,
    'COMPRESS_MIN_SIZE': config.compress_min_size
})
Compress(app)

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[config.rate_limit_default]
)

# Asset bundling
assets = Environment(app)
css_bundle = Bundle(
    'style-expanded.css',
    filters='cssmin',
    output='style.min.css'
)
assets.register('css_all', css_bundle)

# API documentation
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}
Swagger(app, config=swagger_config)


class MessageCache:
    """Handles message caching and persistence."""

    def __init__(self, cache_file: str, max_size: int):
        self.cache_file = cache_file
        self.max_size = max_size

    def load(self) -> List[str]:
        """Load messages from cache file."""
        if not os.path.exists(self.cache_file):
            return []

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load cache: {e}")
            return []

    def save(self, messages: List[str]) -> None:
        """Save messages to cache file with size limiting."""
        # Prune if necessary
        if len(messages) > self.max_size:
            messages = messages[-self.max_size:]
            logger.info(f"Cache pruned to {self.max_size} messages")

        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.error(f"Failed to save cache: {e}")

    def add_message(self, message: str) -> None:
        """Add a new message to cache."""
        messages = self.load()
        messages.append(message)
        self.save(messages)


class RecentMessagesTracker:
    """Tracks recently used messages to avoid repetition."""

    def __init__(self, file_path: str, limit: int):
        self.file_path = file_path
        self.limit = limit

    def load(self) -> List[str]:
        """Load recent messages from file."""
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('last', [])
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load recent messages: {e}")
            return []

    def save(self, messages: List[str]) -> None:
        """Save recent messages to file."""
        # Keep only the most recent messages
        recent = messages[-self.limit:] if len(messages) > self.limit else messages

        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({'last': recent}, f, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Failed to save recent messages: {e}")

    def add_message(self, message: str) -> None:
        """Add a message to recent list."""
        messages = self.load()
        messages.append(message)
        self.save(messages)


class PromptManager:
    """Manages system and user prompts from files and environment."""

    def __init__(self, prompts_file: str, profile: str):
        self.prompts_file = prompts_file
        self.profile = profile
        self.system_prompt, self.user_prompt = self._load_prompts()

    def _load_prompts(self) -> tuple[str, str]:
        """Load prompts from file and environment variables."""
        # Default prompts
        default_system = config.system_prompt
        default_user = config.user_prompt

        # Try to load from file
        if os.path.exists(self.prompts_file):
            try:
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    all_profiles = json.load(f)

                if self.profile in all_profiles:
                    profile_prompts = all_profiles[self.profile]
                    system = profile_prompts.get('system', default_system)
                    user = profile_prompts.get('user', default_user)
                    logger.info(f"Loaded prompts for profile '{self.profile}'")

                    # Environment variables override file
                    system = os.getenv('SYSTEM_PROMPT', system)
                    user = os.getenv('USER_PROMPT', user)

                    return system, user
                else:
                    logger.warning(f"Profile '{self.profile}' not found, using defaults")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load prompts file: {e}")

        # Use environment variables or defaults
        system = os.getenv('SYSTEM_PROMPT', default_system)
        user = os.getenv('USER_PROMPT', default_user)

        return system, user


class AIProviderClient:
    """Handles communication with AI providers."""

    def __init__(self, providers: List[Dict[str, Any]], timeout: int):
        self.providers = providers
        self.timeout = timeout

    def get_message(self, system_prompt: str, user_prompt: str,
                    existing_messages: List[str],
                    fuzzy_threshold: int) -> Optional[str]:
        """Try to get a unique message from configured providers."""
        if not self.providers:
            logger.warning("No AI providers configured")
            return None

        for provider in self.providers:
            try:
                message = self._try_provider(provider, system_prompt, user_prompt)
                if message and not self._is_similar(message, existing_messages, fuzzy_threshold):
                    logger.info(f"✅ Got unique message from {provider['name']}")
                    return message
                elif message:
                    logger.info(f"Similar message from {provider['name']}, trying next")
            except Exception as e:
                logger.error(f"❌ Provider {provider['name']} failed: {type(e).__name__}: {e}")
                continue

        return None

    def _try_provider(self, provider: Dict[str, Any], system_prompt: str, user_prompt: str) -> Optional[str]:
        """Try to get a message from a single provider."""
        logger.info(f"🔍 Trying provider: {provider['name']}")

        client = OpenAI(
            base_url=provider['base_url'],
            api_key=provider['api_key']
        )

        response = client.chat.completions.create(
            model=provider['model'],
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            max_tokens=512,
            timeout=self.timeout
        )

        if not response.choices:
            logger.warning(f"No choices in response from {provider['name']}")
            return None

        message = response.choices[0].message.content.strip()
        logger.debug(f"Message from {provider['name']}: '{message[:100]}...'")

        return message

    def _is_similar(self, new_message: str, existing_messages: List[str], threshold: int) -> bool:
        """Check if message is too similar to existing ones."""
        for existing in existing_messages:
            similarity = fuzz.ratio(new_message, existing)
            if similarity >= threshold:
                logger.debug(f"Similarity {similarity}% >= threshold {threshold}%")
                return True
        return False


# Initialize components
cache = MessageCache(config.cache_file, config.max_cache_size)
recent_tracker = RecentMessagesTracker(config.last_file, config.last_limit)
prompt_manager = PromptManager(config.prompts_file, config.prompt_profile)
# Use the new plugin-aware AI client
ai_client = PluginAwareAIClient({"providers": config.providers}, config.api_timeout)

logger.info(f"System prompt: '{prompt_manager.system_prompt[:70]}...'")
logger.info(f"User prompt: '{prompt_manager.user_prompt[:70]}...'")


def get_ai_message() -> str:
    """
    Main function to get an AI message using cache and provider fallback.

    Returns:
        str: The selected or generated message.
    """
    cached_messages = cache.load()
    recent_messages = recent_tracker.load()

    # Try cached message first (based on probability)
    if cached_messages and secrets.randbelow(100) < int(config.cache_probability * 100):
        # Prefer messages not recently used
        available = [msg for msg in cached_messages if msg not in recent_messages]

        if not available:
            logger.info("All cached messages recently used, using any cached message")
            available = cached_messages

        if available:
            selected = available[secrets.randbelow(len(available))]
            logger.info("🔁 Using cached message")
            recent_tracker.add_message(selected)
            return selected

    # Try to get new message from AI providers
    logger.info("Fetching new message from AI providers")
    new_message = ai_client.get_message(
        prompt_manager.system_prompt,
        prompt_manager.user_prompt,
        cached_messages,
        config.fuzzy_threshold
    )

    if new_message:
        cache.add_message(new_message)
        recent_tracker.add_message(new_message)
        return new_message

    # Fallback to cached message
    if cached_messages:
        fallback = cached_messages[secrets.randbelow(len(cached_messages))]
        logger.info("🕑 Using fallback from cache")
        recent_tracker.add_message(fallback)
        return fallback + " (from archive)"

    # Last resort
    error_msg = "[No response available - please check configuration]"
    logger.error("No messages available from any source")
    return error_msg


@app.route("/")
def index():
    """Serve the main dashboard page."""
    return render_template("index.html", nonce=g.nonce)


@app.route("/api/message")
@limiter.limit(config.rate_limit_api)
def api_message():
    """
    Get an AI-generated message.
    ---
    responses:
      200:
        description: AI-generated message
        schema:
          type: object
          properties:
            message:
              type: string
              description: The AI-generated message
    """
    client_ip = get_remote_address()
    logger.info(f"API request from {client_ip}")

    try:
        message = get_ai_message()
        return jsonify({"message": message})
    except Exception as e:
        logger.error(f"Error generating message: {e}")
        return jsonify({
            "message": "[Error generating message - please try again later]"
        }), 500


@app.route("/api/health")
def health_check():
    """
    Health check endpoint.
    ---
    responses:
      200:
        description: Service health status
        schema:
          type: object
          properties:
            status:
              type: string
            providers:
              type: integer
            cache_size:
              type: integer
    """
    cached_messages = cache.load()
    
    # Get provider health status
    try:
        provider_health = ai_client.health_check_all() if hasattr(ai_client, 'health_check_all') else {}
    except Exception as e:
        logger.warning(f"Failed to get provider health: {e}")
        provider_health = {}
    
    import time
    
    return jsonify({
        "status": "healthy",
        "providers": provider_health,
        "cache_size": len(cached_messages),
        "timestamp": cached_messages.get('last_updated') if isinstance(cached_messages, dict) and cached_messages.get('last_updated') else time.time()
    })


@app.route("/api/plugins")
def api_plugins():
    """
    Get information about available plugins.
    ---
    responses:
      200:
        description: Plugin information
        schema:
          type: object
          properties:
            plugins:
              type: array
              description: List of available plugins
            total:
              type: integer
              description: Total number of plugins
    """
    try:
        plugin_manager = ai_client.get_plugin_manager()
        plugins = plugin_manager.get_plugin_list()
        
        return jsonify({
            "plugins": plugins,
            "total": len(plugins)
        })
    except Exception as e:
        logger.error(f"Error getting plugin information: {e}")
        return jsonify({
            "error": "Failed to get plugin information",
            "message": "An internal error occurred."
        }), 500


@app.route("/api/providers")
def api_providers():
    """
    Get information about configured providers.
    ---
    responses:
      200:
        description: Provider information and health status
        schema:
          type: object
          properties:
            providers:
              type: object
              description: Provider information
            health_status:
              type: object
              description: Health check results
            available_providers:
              type: array
              description: List of available provider names
    """
    try:
        provider_info = ai_client.get_provider_info()
        health_status = ai_client.health_check_all()
        available_providers = ai_client.get_available_providers()
        
        return jsonify({
            "providers": provider_info,
            "health_status": health_status,
            "available_providers": available_providers
        })
    except Exception as e:
        logger.error(f"Error getting provider information: {e}")
        return jsonify({
            "error": "Failed to get provider information",
            "message": "An internal error occurred."
        }), 500


@app.route("/api/providers/reload", methods=["POST"])
def api_reload_providers():
    """
    Reload all providers.
    ---
    responses:
      200:
        description: Providers reloaded successfully
        schema:
          type: object
          properties:
            message:
              type: string
            providers:
              type: array
    """
    try:
        ai_client.reload_providers()
        available_providers = ai_client.get_available_providers()
        
        return jsonify({
            "status": "success",
            "message": "Providers reloaded successfully",
            "providers": available_providers
        })
    except Exception as e:
        logger.error(f"Error reloading providers: {e}")
        return jsonify({
            "error": "Failed to reload providers",
            "message": "An internal error occurred."
        }), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded."""
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later."
    }), 429


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {e}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == "__main__":
    logger.info("Starting AI-Ticker dashboard...")
    # Use localhost for development, 0.0.0.0 only when explicitly configured
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Security warning for binding to all interfaces
    all_interfaces = "0.0.0.0"  # nosec B104 - intentional check for security warning
    if host == all_interfaces:
        logger.warning("⚠️  Binding to all interfaces (0.0.0.0) - ensure this is intended for production")

    app.run(
        host=host,
        port=port,
        debug=debug,
        ssl_context=None
    )
