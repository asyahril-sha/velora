"""
VELORA Bot Package

Telegram bot components:
- ai_client: DeepSeek API client
- prompt: Prompt builder (brutal mode level 11-12)
- handlers: Command handlers (14 commands)
- messages: Message handler (routing)
- main: Main entry point
"""

from .ai_client import (
    AIErrorType,
    AIClient,
    get_ai_client,
    reset_ai_client
)

from .prompt import (
    PromptBuilder,
    get_prompt_builder,
    reset_prompt_builder
)

from .handlers import (
    get_user_mode,
    set_user_mode,
    get_active_role,
    clear_user_mode,
    register_handlers
)

from .messages import (
    message_handler,
    voice_handler,
    sticker_handler,
    photo_handler,
    document_handler,
    error_handler,
    RateLimiter,
    _rate_limiter
)

__all__ = [
    # AI Client
    "AIErrorType",
    "AIClient",
    "get_ai_client",
    "reset_ai_client",
    
    # Prompt Builder
    "PromptBuilder",
    "get_prompt_builder",
    "reset_prompt_builder",
    
    # Handlers
    "get_user_mode",
    "set_user_mode",
    "get_active_role",
    "clear_user_mode",
    "register_handlers",
    
    # Messages
    "message_handler",
    "voice_handler",
    "sticker_handler",
    "photo_handler",
    "document_handler",
    "error_handler",
    "RateLimiter",
    "_rate_limiter"
]
