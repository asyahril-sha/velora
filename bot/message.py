"""
VELORA - Message Handler
Handler untuk semua pesan non-command, routing ke orchestrator.
Dilengkapi dengan:
- Session management
- Error handling
- Rate limiting
- Cooldown untuk mencegah spam
- Logging lengkap
- Safe Markdown handling untuk format response baru (gesture + inner thought)
"""

import time
import logging
import asyncio
import re
from typing import Dict, Optional, Tuple
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from config import get_settings
from core.orchestrator import get_orchestrator
from bot.handlers import get_user_mode, get_active_role, clear_user_mode, set_user_mode

logger = logging.getLogger(__name__)


# =============================================================================
# RATE LIMITING
# =============================================================================

class RateLimiter:
    """
    Rate limiter untuk mencegah spam.
    Setiap user memiliki cooldown setelah mengirim pesan.
    """
    
    def __init__(self):
        self._last_message_time: Dict[int, float] = {}
        self._message_count: Dict[int, int] = {}
        self
