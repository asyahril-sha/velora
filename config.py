"""
VELORA - Configuration Management
Semua konfigurasi dari environment variable dengan duk penuh Railway.
- Database settings
- AI settings (DeepSeek)
- Webhook settings (Railway deployment)
- Logging settings
- Feature toggles
- World settings
- Validation
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


# =============================================================================
# DATABASE SETTINGS
# =============================================================================

class DatabaseSettings(BaseSettings):
    """Konfigurasi database"""
    model_config = ConfigDict(env_prefix="DB_", extra="ignore")
    
    type: str = Field("sqlite", alias="DB_TYPE")
    path: Path = Field(Path("data/velora.db"), alias="DB_PATH")
    
    @property
    def url(self) -> str:
        return f"sqlite+aiosqlite:///{self.path}"
    
    @field_validator('path', mode='before')
    @classmethod
    def validate_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v


# =============================================================================
# AI SETTINGS
# =============================================================================

class AISettings(BaseSettings):
    """Konfigurasi AI DeepSeek"""
    model_config = ConfigDict(env_prefix="AI_", extra="ignore")
    
    temperature: float = Field(0.85, alias="AI_TEMPERATURE")
    max_tokens: int = Field(1200, alias="AI_MAX_TOKENS")
    timeout: int = Field(45, alias="AI_TIMEOUT")
    model: str = Field("deepseek-chat", alias="AI_MODEL")
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError(f'Temperature must be between 0 and 2, got {v}')
        return v


# =============================================================================
# WEBHOOK SETTINGS (RAILWAY DEPLOYMENT)
# =============================================================================

class WebhookSettings(BaseSettings):
    """Konfigurasi webhook untuk Railway deployment"""
    model_config = ConfigDict(env_prefix="", extra="ignore")
    
    port: int = Field(8080, alias="PORT")
    path: str = Field("/webhook", alias="WEBHOOK_PATH")
    secret_token: Optional[str] = Field(None, alias="WEBHOOK_SECRET")
    railway_domain: Optional[str] = Field(None, alias="RAILWAY_PUBLIC_DOMAIN")
    railway_static_url: Optional[str] = Field(None, alias="RAILWAY_STATIC_URL")
    
    @property
    def url(self) -> Optional[str]:
        if self.railway_domain:
            return f"https://{self.railway_domain}{self.path}"
        if self.railway_static_url:
            return f"https://{self.railway_static_url}{self.path}"
        return None
    
    @property
    def is_railway(self) -> bool:
        return bool(self.railway_domain or self.railway_static_url)


# =============================================================================
# LOGGING SETTINGS
# =============================================================================

class LoggingSettings(BaseSettings):
    """Konfigurasi logging untuk Railway"""
    model_config = ConfigDict(env_prefix="LOG_", extra="ignore")
    
    level: str = Field("INFO", alias="LOG_LEVEL")
    json_format: bool = Field(True, alias="LOG_JSON_FORMAT")
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}, got {v}')
        return v.upper()


# =============================================================================
# FEATURE SETTINGS
# =============================================================================

class FeatureSettings(BaseSettings):
    """Feature toggles untuk VELORA"""
    model_config = ConfigDict(env_prefix="", extra="ignore")
    
    vulgar_mode_enabled: bool = Field(True, alias="VULGAR_MODE_ENABLED")
    aftercare_enabled: bool = Field(True, alias="AFTERCARE_ENABLED")
    flashback_enabled: bool = Field(True, alias="FLASHBACK_ENABLED")
    proactive_chat_enabled: bool = Field(True, alias="PROACTIVE_CHAT_ENABLED")
    auto_backup_enabled: bool = Field(True, alias="AUTO_BACKUP_ENABLED")


# =============================================================================
# WORLD SETTINGS
# =============================================================================

class WorldSettings(BaseSettings):
    """World system configuration"""
    model_config = ConfigDict(env_prefix="WORLD_", extra="ignore")
    
    default_drama_level: int = Field(0, alias="DEFAULT_DRAMA_LEVEL")
    max_drama_level: int = Field(100, alias="MAX_DRAMA_LEVEL")
    drama_decay_per_hour: float = Field(2.0, alias="DRAMA_DECAY_PER_HOUR")
    cross_role_effect_enabled: bool = Field(True, alias="CROSS_ROLE_EFFECT_ENABLED")


# =============================================================================
# REALITY ENGINE SETTINGS
# =============================================================================

class RealitySettings(BaseSettings):
    """Reality engine configuration (realism 9.9)"""
    model_config = ConfigDict(env_prefix="REALITY_", extra="ignore")
    
    emotion_delay_enabled: bool = Field(True, alias="EMOTION_DELAY_ENABLED")
    memory_priority_enabled: bool = Field(True, alias="MEMORY_PRIORITY_ENABLED")
    imperfection_enabled: bool = Field(True, alias="IMPERFECTION_ENABLED")
    personality_drift_enabled: bool = Field(True, alias="PERSONALITY_DRIFT_ENABLED")
    
    # Delay settings
    base_emotion_delay: int = Field(1, alias="BASE_EMOTION_DELAY")  # detik
    max_emotion_delay: int = Field(5, alias="MAX_EMOTION_DELAY")  # detik
    
    # Memory priority
    memory_importance_decay: float = Field(0.1, alias="MEMORY_IMPORTANCE_DECAY")  # per hari
    
    # Imperfection
    imperfection_probability: float = Field(0.3, alias="IMPERFECTION_PROBABILITY")
    
    # Personality drift
    personality_drift_rate: float = Field(0.5, alias="PERSONALITY_DRIFT_RATE")  # per 10 interaksi


# =============================================================================
# MAIN SETTINGS CLASS
# =============================================================================

class Settings(BaseSettings):
    """
    VELORA - AI Drama Engine / Relationship Simulator
    Main Settings with Railway Support
    """
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ===== API KEYS (REQUIRED) =====
    deepseek_api_key: str = Field(..., alias="DEEPSEEK_API_KEY")
    telegram_token: str = Field(..., alias="TELEGRAM_TOKEN")
    admin_id: int = Field(..., alias="ADMIN_ID")
    
    # ===== COMPONENT SETTINGS =====
    database: DatabaseSettings = DatabaseSettings()
    ai: AISettings = AISettings()
    webhook: WebhookSettings = WebhookSettings()
    logging: LoggingSettings = LoggingSettings()
    features: FeatureSettings = FeatureSettings()
    world: WorldSettings = WorldSettings()
    reality: RealitySettings = RealitySettings()
    
    # ===== BASE DIRECTORY =====
    base_dir: Path = Path(__file__).parent
    
    # ===== VALIDATORS =====
    @field_validator('deepseek_api_key')
    @classmethod
    def validate_deepseek_key(cls, v):
        if not v or v == "your_deepseek_api_key_here":
            raise ValueError("DEEPSEEK_API_KEY is required. Set in Railway Variables or .env")
        if len(v) < 10:
            raise ValueError("DEEPSEEK_API_KEY seems invalid (too short)")
        return v
    
    @field_validator('telegram_token')
    @classmethod
    def validate_telegram_token(cls, v):
        if not v or v == "your_telegram_bot_token_here":
            raise ValueError("TELEGRAM_TOKEN is required. Set in Railway Variables or .env")
        return v
    
    @field_validator('admin_id')
    @classmethod
    def validate_admin_id(cls, v):
        if v == 0:
            logger.warning("⚠️ ADMIN_ID = 0. Admin commands won't work. Set from @userinfobot")
        return v
    
    # ===== HELPER METHODS =====
    def create_directories(self) -> "Settings":
        """Create all necessary directories"""
        dirs = [
            Path("data"),
            Path("data/backups"),
            Path("data/memory"),
            Path("logs"),
        ]
        for dir_path in dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Directory created/verified: {dir_path}")
            except Exception as e:
                logger.warning(f"Could not create directory {dir_path}: {e}")
        return self
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate all settings and return status"""
        status = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'railway_mode': self.webhook.is_railway
        }
        
        if not self.deepseek_api_key or self.deepseek_api_key == "your_deepseek_api_key_here":
            status['valid'] = False
            status['errors'].append("DeepSeek API Key missing or invalid")
        
        if not self.telegram_token or self.telegram_token == "your_telegram_bot_token_here":
            status['valid'] = False
            status['errors'].append("Telegram Token missing or invalid")
        
        if self.admin_id == 0:
            status['warnings'].append("Admin ID not set (default 0)")
        
        # Check database path is writable
        try:
            self.database.path.parent.mkdir(parents=True, exist_ok=True)
            # Test write
            test_file = self.database.path.parent / ".write_test"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            status['warnings'].append(f"Database directory may not be writable: {e}")
        
        return status
    
    def log_configuration(self) -> None:
        """Log configuration to console"""
        logger.info("=" * 70)
        logger.info("💜 VELORA - Configuration Loaded")
        logger.info("=" * 70)
        logger.info(f"🗄️  Database: {self.database.type} @ {self.database.path}")
        logger.info(f"🤖 AI Model: {self.ai.model} | Temperature: {self.ai.temperature} | Max Tokens: {self.ai.max_tokens}")
        logger.info(f"👑 Admin ID: {self.admin_id}")
        logger.info(f"🌍 Railway Mode: {self.webhook.is_railway}")
        if self.webhook.railway_domain:
            logger.info(f"🌐 Webhook URL: https://{self.webhook.railway_domain}{self.webhook.path}")
        logger.info(f"🌍 World: Drama Max: {self.world.max_drama_level} | Decay: {self.world.drama_decay_per_hour}/h")
        logger.info(f"✨ Reality Engine: Delay={self.reality.emotion_delay_enabled} | Imperfection={self.reality.imperfection_enabled} | Drift={self.reality.personality_drift_enabled}")
        logger.info(f"💋 Vulgar Mode: {'ON' if self.features.vulgar_mode_enabled else 'OFF'}")
        logger.info(f"💕 Aftercare Mode: {'ON' if self.features.aftercare_enabled else 'OFF'}")
        logger.info(f"💬 Proactive Chat: {'ON' if self.features.proactive_chat_enabled else 'OFF'}")
        logger.info(f"💾 Auto Backup: {'ON' if self.features.auto_backup_enabled else 'OFF'}")
        logger.info("=" * 70)
    
    def get_status_text(self) -> str:
        """Get status text for display"""
        status = self.validate_all()
        
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║                    ⚙️ VELORA CONFIGURATION                   ║",
            "╠══════════════════════════════════════════════════════════════╣",
            f"║ Valid: {'✅' if status['valid'] else '❌'}                                        ║",
            f"║ Railway Mode: {'✅' if status['railway_mode'] else '❌'}                                    ║",
            "╠══════════════════════════════════════════════════════════════╣",
            f"║ Admin ID: {self.admin_id}                                             ║",
            f"║ AI Model: {self.ai.model}                                         ║",
            f"║ Database: {self.database.path}                               ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║ FEATURES:                                                  ║",
            f"║   Vulgar Mode: {'✅' if self.features.vulgar_mode_enabled else '❌'}                                            ║",
            f"║   Proactive Chat: {'✅' if self.features.proactive_chat_enabled else '❌'}                                        ║",
            f"║   Auto Backup: {'✅' if self.features.auto_backup_enabled else '❌'}                                          ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║ REALITY ENGINE:                                            ║",
            f"║   Emotion Delay: {'✅' if self.reality.emotion_delay_enabled else '❌'}                                    ║",
            f"║   Imperfection: {'✅' if self.reality.imperfection_enabled else '❌'}                                     ║",
            f"║   Personality Drift: {'✅' if self.reality.personality_drift_enabled else '❌'}                               ║",
            "╚══════════════════════════════════════════════════════════════╝"
        ]
        
        if status['errors']:
            lines.append("\n❌ ERRORS:")
            for err in status['errors']:
                lines.append(f"   • {err}")
        
        if status['warnings']:
            lines.append("\n⚠️ WARNINGS:")
            for warn in status['warnings']:
                lines.append(f"   • {warn}")
        
        return "\n".join(lines)


# =============================================================================
# GLOBAL SETTINGS INSTANCE
# =============================================================================

_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance with caching"""
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
            _settings.create_directories()
            _settings.log_configuration()
            
            status = _settings.validate_all()
            if not status['valid']:
                for err in status['errors']:
                    logger.error(f"❌ Configuration error: {err}")
                raise ValueError("Invalid configuration")
            
            for warn in status['warnings']:
                logger.warning(f"⚠️ {warn}")
                
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            raise
    
    return _settings


def reset_settings() -> None:
    """Reset settings instance (for testing)"""
    global _settings
    _settings = None
    logger.info("🔄 Settings reset")


settings = get_settings()


__all__ = [
    'DatabaseSettings',
    'AISettings',
    'WebhookSettings',
    'LoggingSettings',
    'FeatureSettings',
    'WorldSettings',
    'RealitySettings',
    'Settings',
    'get_settings',
    'reset_settings',
    'settings'
]
