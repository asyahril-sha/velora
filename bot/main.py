"""
VELORA - Main Entry Point
Telegram bot + aiohttp web server (Railway webhook support)
- Bot initialization with all handlers
- Webhook setup for Railway deployment
- Background worker integration
- Graceful shutdown
"""

import os
import sys
import asyncio
import signal
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from aiohttp import web
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, MessageHandler, filters
from telegram.request import HTTPXRequest

from config import get_settings
from bot.handlers import register_handlers
from bot.messages import message_handler, error_handler
from core.orchestrator import get_orchestrator
from core.memory import get_memory_manager
from core.world import get_world_state
from memory.persistent import get_persistent
from roles.manager import get_role_manager
from worker.background import get_worker

logger = logging.getLogger(__name__)


# =============================================================================
# GLOBALS
# =============================================================================

_application: Optional[Application] = None
_shutdown_flag = False


# =============================================================================
# WEBHOOK HANDLERS
# =============================================================================

async def webhook_handler(request: web.Request):
    """Handle incoming webhook requests from Telegram"""
    global _application
    
    if request.method != "POST":
        return web.Response(text="Use POST", status=405)
    
    if not _application:
        return web.Response(status=503, text="Bot not ready")
    
    settings = get_settings()
    
    # Verify secret token if set
    secret = settings.webhook.secret_token
    if secret:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if header_secret != secret:
            return web.Response(status=401, text="Invalid secret token")
    
    try:
        update_data = await request.json()
        upd = Update.de_json(update_data, _application.bot)
        await _application.process_update(upd)
        return web.Response(text="OK", status=200)
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return web.Response(status=500, text="Error")


async def health_handler(request: web.Request):
    """Health check endpoint for Railway"""
    settings = get_settings()
    worker = get_worker()
    
    return web.json_response({
        "status": "healthy",
        "bot": "VELORA",
        "version": "1.0.0",
        "worker_running": worker.is_running,
        "timestamp": datetime.now().isoformat()
    })


async def root_handler(request: web.Request):
    """Root endpoint"""
    return web.json_response({
        "name": "VELORA",
        "status": "running",
        "message": "AI Drama Engine / Relationship Simulator"
    })


# =============================================================================
# VELORA BOT
# =============================================================================

class VeloraBot:
    """
    Main bot class for VELORA.
    Manages Telegram bot, webhook server, and background tasks.
    """
    
    def __init__(self):
        self.application: Optional[Application] = None
        self._runner: Optional[web.AppRunner] = None
        self._save_task: Optional[asyncio.Task] = None
        self._worker_task: Optional[asyncio.Task] = None
        
        logger.info("💜 VeloraBot initialized")
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    async def init_systems(self) -> bool:
        """Initialize all VELORA systems"""
        logger.info("🚀 Initializing VELORA systems...")
        
        try:
            # Initialize database first
            persistent = await get_persistent()
            logger.info("✅ Database initialized")
            
            # Initialize memory manager
            memory = get_memory_manager()
            world = get_world_state()
            memory.initialize(None, world)  # Tracker will be set later
            logger.info("✅ Memory Manager initialized")
            
            # Load all states from database
            await self._load_all_states(persistent, memory, world)
            
            # Initialize role manager
            role_manager = get_role_manager()
            await role_manager.initialize(memory, world)
            logger.info(f"✅ Role Manager initialized with {len(role_manager.roles)} roles")
            
            # Initialize orchestrator
            orchestrator = await get_orchestrator()
            await orchestrator.initialize(memory, world, role_manager)
            logger.info("✅ Orchestrator initialized")
            
            # Initialize worker
            worker = get_worker()
            logger.info("✅ Worker initialized")
            
            logger.info("🎉 All VELORA systems initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize systems: {e}", exc_info=True)
            return False
    
    async def _load_all_states(self, persistent, memory, world):
        """Load all states from database"""
        try:
            # Load world state
            await persistent.load_world_state(world)
            
            # Load role states
            role_manager = get_role_manager()
            await role_manager.load_all(persistent)
            
            # Load memory
            memory_data = await persistent.get_state("memory_manager")
            if memory_data:
                import json
                memory.from_dict(json.loads(memory_data), None, world)
            
            logger.info("📀 All states loaded from database")
            
        except Exception as e:
            logger.error(f"Error loading states: {e}", exc_info=True)
    
    async def _save_all_states(self):
        """Save all states to database"""
        try:
            persistent = await get_persistent()
            memory = get_memory_manager()
            world = get_world_state()
            role_manager = get_role_manager()
            
            # Save world state
            await persistent.save_world_state(world)
            
            # Save role states
            await role_manager.save_all(persistent)
            
            # Save memory
            await persistent.set_state("memory_manager", json.dumps(memory.to_dict()))
            
            logger.debug("💾 All states saved to database")
            
        except Exception as e:
            logger.error(f"Error saving states: {e}", exc_info=True)
    
    # =========================================================================
    # BOT SETUP
    # =========================================================================
    
    async def init_application(self) -> Application:
        """Initialize Telegram application with handlers"""
        settings = get_settings()
        logger.info("🔧 Initializing Telegram application...")
        
        # Create application with custom request
        request = HTTPXRequest(
            connection_pool_size=50,
            connect_timeout=60,
            read_timeout=60
        )
        
        app = ApplicationBuilder() \
            .token(settings.telegram_token) \
            .request(request) \
            .build()
        
        # Register all command handlers
        register_handlers(app)
        
        # Register message handler (for non-command messages)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        
        # Register error handler
        app.add_error_handler(error_handler)
        
        handler_count = sum(len(h) for h in app.handlers.values())
        logger.info(f"✅ Handlers registered: {handler_count}")
        
        return app
    
    async def setup_webhook(self) -> bool:
        """Setup webhook for Railway deployment"""
        settings = get_settings()
        webhook_url = settings.webhook.url
        
        if not webhook_url:
            logger.warning("🌐 No webhook URL found, using polling mode")
            return False
        
        logger.info(f"🔗 Setting webhook to: {webhook_url}")
        
        try:
            await self.application.bot.delete_webhook(drop_pending_updates=True)
            await self.application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True,
                secret_token=settings.webhook.secret_token
            )
            info = await self.application.bot.get_webhook_info()
            logger.info(f"📡 Webhook info: {info.url}")
            return info.url == webhook_url
        except Exception as e:
            logger.error(f"Webhook setup error: {e}", exc_info=True)
            return False
    
    async def start_web_server(self):
        """Start aiohttp web server for webhook"""
        settings = get_settings()
        port = int(os.environ.get("PORT", settings.webhook.port))
        
        app = web.Application()
        app.router.add_get("/", root_handler)
        app.router.add_get("/health", health_handler)
        app.router.add_post(settings.webhook.path, webhook_handler)
        
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        
        site = web.TCPSite(self._runner, "0.0.0.0", port)
        await site.start()
        
        logger.info(f"🌐 Web server running on port {port}")
        logger.info(f"   Health check: http://localhost:{port}/health")
        logger.info(f"   Webhook endpoint: POST http://localhost:{port}{settings.webhook.path}")
        if settings.webhook.url:
            logger.info(f"   Public webhook: {settings.webhook.url}")
    
    # =========================================================================
    # BACKGROUND TASKS
    # =========================================================================
    
    async def _save_loop(self):
        """Periodic save loop"""
        while not _shutdown_flag:
            await asyncio.sleep(60)  # Save every minute
            await self._save_all_states()
    
    async def _worker_loop(self):
        """Start background worker"""
        worker = get_worker()
        
        # Set up user IDs from settings
        settings = get_settings()
        if settings.admin_id:
            worker.add_user(settings.admin_id)
        
        # Start worker
        await worker.start()
        
        # Keep running
        while not _shutdown_flag:
            await asyncio.sleep(1)
        
        # Stop worker on shutdown
        await worker.stop()
    
    # =========================================================================
    # START & SHUTDOWN
    # =========================================================================
    
    async def start(self):
        """Start the bot"""
        global _application
        
        logger.info("=" * 70)
        logger.info("💜 VELORA - AI Drama Engine / Relationship Simulator")
        logger.info("=" * 70)
        
        # Initialize systems
        if not await self.init_systems():
            logger.error("Failed to initialize systems. Exiting.")
            return
        
        # Initialize Telegram application
        self.application = await self.init_application()
        await self.application.initialize()
        await self.application.start()
        
        _application = self.application
        logger.info("✅ Telegram Application started")
        
        # Setup webhook or polling
        settings = get_settings()
        if settings.webhook.url:
            webhook_ok = await self.setup_webhook()
            if webhook_ok:
                await self.start_web_server()
            else:
                logger.warning("Webhook setup failed, falling back to polling")
                await self.application.bot.delete_webhook()
                await self.application.updater.start_polling()
        else:
            logger.info("Using polling mode")
            await self.application.updater.start_polling()
        
        # Start background tasks
        self._save_task = asyncio.create_task(self._save_loop())
        self._worker_task = asyncio.create_task(self._worker_loop())
        
        logger.info("=" * 70)
        logger.info("✨ VELORA is ready!")
        logger.info(f"👑 Admin ID: {settings.admin_id}")
        logger.info(f"🌍 Railway Mode: {settings.webhook.is_railway}")
        logger.info("=" * 70)
        
        # Keep running
        while not _shutdown_flag:
            await asyncio.sleep(1)
    
    async def shutdown(self):
        """Graceful shutdown"""
        global _shutdown_flag
        
        logger.info("🛑 Shutting down VELORA...")
        _shutdown_flag = True
        
        # Cancel background tasks
        for task in [self._save_task, self._worker_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Save final state
        await self._save_all_states()
        logger.info("💾 Final state saved")
        
        # Stop web server
        if self._runner:
            await self._runner.cleanup()
            logger.info("✅ Web server stopped")
        
        # Stop Telegram application
        if self.application:
            try:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("✅ Telegram application stopped")
            except Exception as e:
                logger.error(f"Error stopping application: {e}")
        
        # Close database connection
        try:
            persistent = await get_persistent()
            await persistent.close()
            logger.info("✅ Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
        
        logger.info("👋 Goodbye from VELORA!")


# =============================================================================
# ENTRY POINT
# =============================================================================

async def main():
    """Main entry point"""
    bot = VeloraBot()
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    
    def signal_handler():
        asyncio.create_task(bot.shutdown())
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass
    
    try:
        await bot.start()
    except asyncio.CancelledError:
        logger.info("Bot cancelled")
    except Exception as e:
        logger.error(f"Main error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
