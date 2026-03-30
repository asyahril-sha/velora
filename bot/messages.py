"""
VELORA - Message Handler
Handler untuk pesan non-command, routing ke orchestrator.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import get_settings
from core.orchestrator import get_orchestrator
from bot.handlers import get_user_mode, get_active_role, clear_user_mode

logger = logging.getLogger(__name__)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua pesan non-command.
    Route ke orchestrator untuk diproses.
    """
    user_id = update.effective_user.id
    settings = get_settings()
    
    # Hanya admin yang bisa berinteraksi
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text if update.message else None
    if not pesan:
        return
    
    logger.info(f"📨 Message from {user_id}: {pesan[:100]}")
    
    # Cek mode user
    mode = get_user_mode(user_id)
    
    if mode == "paused":
        await update.message.reply_text(
            "⏸️ Sesi sedang di-pause.\n\n"
            "Ketik **/resume** untuk melanjutkan, atau **/batal** untuk memulai baru.",
            parse_mode="Markdown"
        )
        return
    
    # Proses melalui orchestrator
    try:
        orchestrator = await get_orchestrator()
        response = await orchestrator.handle_message(pesan, user_id)
        
        # Kirim response
        if response:
            await update.message.reply_text(response, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Message handler error: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Maaf, terjadi error. Silakan coba lagi nanti.",
            parse_mode="Markdown"
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler untuk bot"""
    logger.error(f"Bot error: {context.error}", exc_info=True)
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Terjadi error internal. Silakan coba lagi nanti, Mas.",
                parse_mode="Markdown"
            )
    except Exception:
        pass


__all__ = [
    'message_handler',
    'error_handler'
]
