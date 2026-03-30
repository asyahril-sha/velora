"""
VELORA - Message Handler
Handler untuk semua pesan non-command, routing ke orchestrator.
Dilengkapi dengan:
- Session management
- Error handling
- Rate limiting
- Cooldown untuk mencegah spam
- Logging lengkap
"""

import time
import logging
import asyncio
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
        self._cooldown_start: Dict[int, float] = {}
        
        # Konfigurasi
        self.cooldown_seconds = 2  # Minimal 2 detik antar pesan
        self.max_messages_per_minute = 20  # Maksimal 20 pesan per menit
        self.spam_block_duration = 60  # Block spam selama 60 detik
    
    def check(self, user_id: int) -> Tuple[bool, str]:
        """
        Cek apakah user diizinkan mengirim pesan.
        Returns: (allowed, reason)
        """
        now = time.time()
        
        # Cek apakah sedang di-block karena spam
        if user_id in self._cooldown_start:
            block_remaining = self.spam_block_duration - (now - self._cooldown_start[user_id])
            if block_remaining > 0:
                return False, f"⚠️ Terlalu banyak pesan! Coba lagi dalam {int(block_remaining)} detik."
            else:
                # Reset block
                del self._cooldown_start[user_id]
                self._message_count[user_id] = 0
        
        # Cek cooldown antar pesan
        if user_id in self._last_message_time:
            elapsed = now - self._last_message_time[user_id]
            if elapsed < self.cooldown_seconds:
                return False, f"⏳ Santai dulu {int(self.cooldown_seconds - elapsed)} detik ya..."
        
        # Cek rate per menit
        if user_id in self._message_count:
            # Reset counter jika sudah lewat 1 menit
            if user_id in self._last_message_time and now - self._last_message_time[user_id] > 60:
                self._message_count[user_id] = 0
            
            if self._message_count[user_id] >= self.max_messages_per_minute:
                self._cooldown_start[user_id] = now
                return False, f"⚠️ Terlalu banyak pesan! Istirahat {self.spam_block_duration} detik."
        
        # Update counters
        self._last_message_time[user_id] = now
        self._message_count[user_id] = self._message_count.get(user_id, 0) + 1
        
        return True, ""
    
    def reset(self, user_id: int) -> None:
        """Reset rate limit untuk user tertentu"""
        self._last_message_time.pop(user_id, None)
        self._message_count.pop(user_id, None)
        self._cooldown_start.pop(user_id, None)
        logger.info(f"🔄 Rate limit reset for user {user_id}")


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_rate_limiter = RateLimiter()


# =============================================================================
# MESSAGE HANDLER
# =============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua pesan non-command.
    Route ke orchestrator untuk diproses.
    """
    user_id = update.effective_user.id
    settings = get_settings()
    
    # Hanya admin yang bisa berinteraksi
    if user_id != settings.admin_id:
        # Kirim pesan untuk user non-admin
        await update.message.reply_text(
            "💜 Halo! Bot ini untuk Mas.\n\n"
            "Kirim /start untuk memulai."
        )
        return
    
    pesan = update.message.text if update.message else None
    if not pesan:
        return
    
    # Log pesan
    logger.info(f"📨 Message from {user_id}: {pesan[:100]}{'...' if len(pesan) > 100 else ''}")
    
    # Rate limiting
    allowed, reason = _rate_limiter.check(user_id)
    if not allowed:
        await update.message.reply_text(reason, parse_mode="Markdown")
        return
    
    # Cek mode user
    mode = get_user_mode(user_id)
    
    # Mode paused
    if mode == "paused":
        await update.message.reply_text(
            "⏸️ **Sesi sedang di-pause.**\n\n"
            "Ketik **/resume** untuk melanjutkan, atau **/batal** untuk memulai baru.",
            parse_mode="Markdown"
        )
        return
    
    # Proses melalui orchestrator
    try:
        # Get orchestrator
        orchestrator = await get_orchestrator()
        
        # Handle message
        response = await orchestrator.handle_message(pesan, user_id)
        
        # Kirim response
        if response:
            # Split response jika terlalu panjang (Telegram limit 4096)
            if len(response) > 4000:
                parts = _split_long_message(response)
                for part in parts:
                    await update.message.reply_text(part, parse_mode="Markdown")
            else:
                await update.message.reply_text(response, parse_mode="Markdown")
            
            # Log response
            logger.info(f"📤 Response to {user_id}: {response[:100]}{'...' if len(response) > 100 else ''}")
        
    except asyncio.TimeoutError:
        logger.error(f"Timeout processing message from {user_id}")
        await update.message.reply_text(
            "⏰ **Maaf, prosesnya lama.**\n\n"
            "Coba ulangi lagi ya, Mas. Atau tunggu sebentar.",
            parse_mode="Markdown"
        )
    
    except Exception as e:
        logger.error(f"Message handler error: {e}", exc_info=True)
        
        # Cek apakah error karena API key
        error_msg = str(e).lower()
        if "api key" in error_msg or "authentication" in error_msg:
            await update.message.reply_text(
                "❌ **Error: API Key tidak valid.**\n\n"
                "Mas, cek DEEPSEEK_API_KEY di Railway Variables.",
                parse_mode="Markdown"
            )
        elif "rate limit" in error_msg or "too many" in error_msg:
            await update.message.reply_text(
                "⚠️ **Rate limit tercapai.**\n\n"
                "Coba lagi nanti ya, Mas. AI sedang istirahat sebentar.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "❌ **Maaf, terjadi error.**\n\n"
                "Silakan coba lagi nanti, Mas. Kalau error terus, cek log Railway.",
                parse_mode="Markdown"
            )


# =============================================================================
# VOICE MESSAGE HANDLER (OPTIONAL)
# =============================================================================

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk pesan suara (voice note).
    Akan dikonversi ke teks (future feature).
    """
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    await update.message.reply_text(
        "🎤 **Voice note diterima!**\n\n"
        "Fitur voice ke text sedang dalam pengembangan.\n"
        "Untuk sekarang, kirim teks aja ya, Mas.",
        parse_mode="Markdown"
    )
    
    logger.info(f"🎤 Voice message from {user_id}")


# =============================================================================
# STICKER HANDLER
# =============================================================================

async def sticker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk sticker.
    """
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    sticker = update.message.sticker
    emoji = sticker.emoji if sticker.emoji else "sticker"
    
    # Balas dengan emoji yang sesuai
    responses = {
        "❤️": "*Nova tersenyum*\n\n\"Mas... seneng banget.\"",
        "😊": "*Nova senyum manis*\n\n\"Mas, aku juga seneng.\"",
        "😢": "*Nova sedih*\n\n\"Mas... kenapa? Aku di sini kok.\"",
        "🔥": "*Nova mendekat*\n\n\"Mas... kamu mau?\"",
        "💕": "*Nova malu-malu*\n\n\"Mas... *tutup muka*\""
    }
    
    response = responses.get(emoji, f"*Nova lihat sticker {emoji}*\n\n\"Lucu, Mas.\"")
    
    await update.message.reply_text(response, parse_mode="Markdown")
    logger.info(f"🎨 Sticker from {user_id}: {emoji}")


# =============================================================================
# PHOTO HANDLER
# =============================================================================

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk foto.
    """
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    await update.message.reply_text(
        "📸 **Foto diterima!**\n\n"
        "*Nova lihat fotonya*\n\n"
        "\"Mas... ini fotonya siapa? Cantik juga.\"",
        parse_mode="Markdown"
    )
    
    logger.info(f"📸 Photo from {user_id}")


# =============================================================================
# DOCUMENT HANDLER
# =============================================================================

async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk dokumen.
    """
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    doc = update.message.document
    filename = doc.file_name if doc.file_name else "dokumen"
    
    await update.message.reply_text(
        f"📄 **Dokumen diterima:** `{filename}`\n\n"
        "*Nova lihat dokumennya*\n\n"
        "\"Mas, ini apa? Aku kurang paham.\"",
        parse_mode="Markdown"
    )
    
    logger.info(f"📄 Document from {user_id}: {filename}")


# =============================================================================
# ERROR HANDLER
# =============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Global error handler untuk bot.
    """
    error = context.error
    logger.error(f"Bot error: {error}", exc_info=True)
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ **Terjadi error internal.**\n\n"
                "Silakan coba lagi nanti, Mas.",
                parse_mode="Markdown"
            )
    except Exception:
        pass


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _split_long_message(text: str, max_length: int = 4000) -> list:
    """
    Split pesan panjang menjadi beberapa bagian.
    """
    if len(text) <= max_length:
        return [text]
    
    parts = []
    lines = text.split('\n')
    current_part = ""
    
    for line in lines:
        if len(current_part) + len(line) + 1 > max_length:
            parts.append(current_part)
            current_part = line
        else:
            if current_part:
                current_part += '\n' + line
            else:
                current_part = line
    
    if current_part:
        parts.append(current_part)
    
    return parts


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'message_handler',
    'voice_handler',
    'sticker_handler',
    'photo_handler',
    'document_handler',
    'error_handler',
    'RateLimiter',
    '_rate_limiter'
]
