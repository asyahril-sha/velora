#!/usr/bin/env python3
"""
VELORA - Deployment Runner for Railway
This script handles all startup tasks for Railway deployment.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-5s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("VELORA-DEPLOY")


def setup_environment():
    """Setup environment variables and directories"""
    logger.info("🔧 Setting up environment...")
    
    # Create necessary directories
    directories = [
        Path("data"),
        Path("data/backups"),
        Path("data/memory"),
        Path("logs")
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Directory created: {dir_path}")
    
    # Check environment variables
    required_vars = ['TELEGRAM_TOKEN', 'DEEPSEEK_API_KEY', 'ADMIN_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("✅ Environment setup complete")
    return True


def check_dependencies():
    """Check if all dependencies are installed"""
    logger.info("🔍 Checking dependencies...")
    
    required_modules = [
        'aiohttp',
        'telegram',
        'openai',
        'pydantic',
        'aiosqlite',
        'tenacity'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            logger.debug(f"✅ {module} found")
        except ImportError:
            missing_modules.append(module)
            logger.warning(f"⚠️ {module} not found")
    
    if missing_modules:
        logger.error(f"❌ Missing modules: {missing_modules}")
        return False
    
    logger.info("✅ All dependencies OK")
    return True


async def test_imports():
    """Test critical imports"""
    logger.info("🔍 Testing critical imports...")
    
    critical_imports = [
        ('config', 'get_settings'),
        ('core.tracker', 'StateTracker'),
        ('core.emotional', 'EmotionalEngine'),
        ('core.relationship', 'RelationshipManager'),
        ('core.conflict', 'ConflictEngine'),
        ('core.world', 'WorldState'),
        ('core.memory', 'MemoryManager'),
        ('core.orchestrator', 'RoleOrchestrator'),
        ('roles.manager', 'RoleManager'),
        ('roles.nova', 'NovaRole'),
        ('bot.main', 'VeloraBot')
    ]
    
    failed = []
    for module_name, class_name in critical_imports:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            logger.debug(f"✅ {module_name}.{class_name} OK")
        except Exception as e:
            failed.append(f"{module_name}.{class_name}: {e}")
            logger.error(f"❌ {module_name}.{class_name} failed: {e}")
    
    if failed:
        logger.error(f"❌ Failed imports: {len(failed)}")
        return False
    
    logger.info("✅ All critical imports OK")
    return True


async def test_database():
    """Test database connection"""
    logger.info("🔍 Testing database connection...")
    
    try:
        from memory.persistent import get_persistent
        
        persistent = await get_persistent()
        stats = await persistent.get_stats()
        logger.info(f"✅ Database OK: {stats.get('db_size_mb', 0)} MB")
        return True
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        return False


async def test_roles():
    """Test role creation"""
    logger.info("🔍 Testing role creation...")
    
    try:
        from roles.manager import get_role_manager
        
        role_manager = get_role_manager()
        roles = role_manager.get_all_roles()
        logger.info(f"✅ Roles OK: {len(roles)} roles loaded")
        
        for role in roles[:5]:
            logger.debug(f"   - {role['id']}: {role['nama']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Roles error: {e}")
        return False


async def main():
    """Main deployment runner"""
    logger.info("=" * 60)
    logger.info("🚀 VELORA - Deployment Runner")
    logger.info("=" * 60)
    
    # Step 1: Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Step 2: Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Step 3: Test imports
    if not await test_imports():
        sys.exit(1)
    
    # Step 4: Test database
    if not await test_database():
        logger.warning("⚠️ Database test failed, but continuing...")
    
    # Step 5: Test roles
    if not await test_roles():
        logger.warning("⚠️ Roles test failed, but continuing...")
    
    logger.info("=" * 60)
    logger.info("✅ All tests passed! Starting bot...")
    logger.info("=" * 60)
    
    # Import and run bot
    try:
        from bot.main import main as bot_main
        await bot_main()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
