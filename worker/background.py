"""
VELORA - Background Worker
Menjalankan task-task periodic di background:
- Rindu growth (naik kalo lama gak chat)
- Conflict decay (konflik reda pelan)
- Mood recovery (mood pulih seiring waktu)
- Auto save state ke database
- Proactive chat (Nova chat duluan) - TERINTEGRASI DENGAN PROMPT BUILDER
- Auto scene (untuk provider: pijat++, pelacur)
- Auto backup database
- Booking expiry check
- Session timeout check
- Drama decay
- Personality drift update
"""

import asyncio
import time
import logging
import random
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# BACKGROUND WORKER
# =============================================================================

class VeloraWorker:
    """
    Background worker untuk VELORA.
    Menjalankan task-task periodic secara async.
    Terintegrasi dengan PromptBuilder untuk proactive chat yang natural.
    """
    
    def __init__(self):
        self.is_running = False
        self.tasks: List[asyncio.Task] = []
        
        # ========== INTERVAL (detik) ==========
        self.rindu_interval = 1800      # 30 menit
        self.conflict_interval = 1800   # 30 menit
        self.mood_interval = 3600       # 1 jam
        self.drama_interval = 1800      # 30 menit
        self.save_interval = 60         # 1 menit
        self.proactive_interval = 300   # 5 menit
        self.auto_scene_interval = 15   # 15 detik
        self.booking_check_interval = 60  # 1 menit
        self.session_timeout_interval = 300  # 5 menit
        self.personality_interval = 3600  # 1 jam
        self.backup_interval = 21600    # 6 jam
        self.natural_intimacy_interval = 180  # 3 menit (BARU)
        
        # ========== LAST RUN TIMES ==========
        self.last_rindu_run = 0
        self.last_conflict_run = 0
        self.last_mood_run = 0
        self.last_drama_run = 0
        self.last_save_run = 0
        self.last_proactive_run = 0
        self.last_auto_scene_run = 0
        self.last_booking_check_run = 0
        self.last_session_timeout_run = 0
        self.last_personality_run = 0
        self.last_backup_run = 0
        self.last_natural_intimacy_run = 0  # BARU
        
        # ========== REFERENCES ==========
        self._application = None
        self._user_ids: List[int] = []
        self._get_orchestrator = None
        self._get_persistent = None
        self._get_emotional_engine = None
        self._get_relationship_manager = None
        self._get_conflict_engine = None
        self._get_brain = None
        self._get_world = None
        self._get_role_manager = None
        self._get_prompt_builder = None  # BARU
        
        # ========== PROACTIVE COOLDOWN PER USER ==========
        self._proactive_cooldown: Dict[int, float] = {}
        self._proactive_cooldown_seconds = 3600  # 1 jam
        
        # ========== NATURAL INTIMACY COOLDOWN (BARU) ==========
        self._intimacy_cooldown: Dict[int, float] = {}
        self._intimacy_cooldown_seconds = 1800  # 30 menit
        
        # ========== SESSION TIMEOUT ==========
        self._session_timeout_seconds = 1800  # 30 menit
        self._last_activity: Dict[int, float] = {}
        
        # ========== STATISTICS ==========
        self._rindu_updates = 0
        self._conflict_decays = 0
        self._mood_recoveries = 0
        self._drama_decays = 0
        self._auto_saves = 0
        self._proactive_sent = 0
        self._auto_scenes_sent = 0
        self._bookings_expired = 0
        self._sessions_timeout = 0
        self._backups_created = 0
        self._natural_intimacy_sent = 0  # BARU
        
        logger.info("🔄 VeloraWorker initialized")
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    def initialize(self, 
                   application=None,
                   user_ids: List[int] = None,
                   get_orchestrator=None,
                   get_persistent=None,
                   get_emotional_engine=None,
                   get_relationship_manager=None,
                   get_conflict_engine=None,
                   get_brain=None,
                   get_world=None,
                   get_role_manager=None):
        """Initialize dengan references ke komponen lain"""
        self._application = application
        self._user_ids = user_ids or []
        self._get_orchestrator = get_orchestrator
        self._get_persistent = get_persistent
        self._get_emotional_engine = get_emotional_engine
        self._get_relationship_manager = get_relationship_manager
        self._get_conflict_engine = get_conflict_engine
        self._get_brain = get_brain
        self._get_world = get_world
        self._get_role_manager = get_role_manager
        
        # Lazy import prompt builder
        try:
            from bot.prompt import get_prompt_builder
            self._get_prompt_builder = get_prompt_builder
        except ImportError:
            logger.warning("PromptBuilder not available for worker")
        
        # Initialize last activity for users
        for user_id in self._user_ids:
            self._last_activity[user_id] = time.time()
        
        logger.info(f"🔧 VeloraWorker initialized with {len(self._user_ids)} users")
    
    # =========================================================================
    # START & STOP
    # =========================================================================
    
    async def start(self) -> None:
        """Start semua background loops"""
        if self.is_running:
            logger.warning("Worker already running")
            return
        
        self.is_running = True
        
        # Start all loops
        self.tasks = [
            asyncio.create_task(self._rindu_loop()),
            asyncio.create_task(self._conflict_loop()),
            asyncio.create_task(self._mood_loop()),
            asyncio.create_task(self._drama_loop()),
            asyncio.create_task(self._save_loop()),
            asyncio.create_task(self._proactive_loop()),
            asyncio.create_task(self._auto_scene_loop()),
            asyncio.create_task(self._booking_check_loop()),
            asyncio.create_task(self._session_timeout_loop()),
            asyncio.create_task(self._personality_loop()),
            asyncio.create_task(self._backup_loop()),
            asyncio.create_task(self._natural_intimacy_loop()),  # BARU
        ]
        
        logger.info("🔄 All background loops started")
    
    # =========================================================================
    # PROACTIVE CHAT LOOP (NOVA) - DENGAN PROMPT BUILDER
    # =========================================================================
    
    async def _proactive_loop(self) -> None:
        """Nova chat duluan kalo kondisi memungkinkan"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_proactive_run
            
            if elapsed >= self.proactive_interval:
                await self._check_proactive()
                self.last_proactive_run = now
            
            await asyncio.sleep(30)
    
    async def _check_proactive(self) -> None:
        """
        Cek apakah Nova harus chat duluan untuk setiap user.
        Menggunakan PromptBuilder untuk respons yang natural.
        """
        if not self._application or not self._user_ids:
            return
        
        for user_id in self._user_ids:
            # Cek cooldown
            last_proactive = self._proactive_cooldown.get(user_id, 0)
            if time.time() - last_proactive < self._proactive_cooldown_seconds:
                continue
            
            # Cek session timeout
            if user_id in self._last_activity and time.time() - self._last_activity[user_id] > 300:
                # User inactive > 5 menit, skip proactive
                continue
            
            try:
                if not self._get_orchestrator:
                    continue
                
                orchestrator = await self._get_orchestrator()
                message = await orchestrator.check_proactive_for_user(user_id)
                
                if message:
                    # Gunakan prompt builder untuk memperkaya pesan jika perlu
                    if self._get_prompt_builder and random.random() < 0.3:
                        # Kadang-kadang tambahkan scene untuk membuat lebih natural
                        nova = self._get_role_manager().get_role('nova') if self._get_role_manager else None
                        if nova and hasattr(nova, 'reality'):
                            scene = nova.reality.scene_engine.get_body_language(
                                'warm',
                                max(nova.emotional.sayang / 100, 0.3)
                            )
                            if scene and scene not in message:
                                message = f"{scene}\n\n{message}"
                    
                    await self._application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    self._proactive_cooldown[user_id] = time.time()
                    self._proactive_sent += 1
                    logger.info(f"💬 Proactive message sent to {user_id}")
                    
                    # Save to database
                    if self._get_persistent:
                        persistent = await self._get_persistent()
                        await persistent.save_proactive_message(user_id, message, "")
                    
            except Exception as e:
                logger.error(f"Proactive check error for {user_id}: {e}")
    
    # =========================================================================
    # NATURAL INTIMACY LOOP (BARU)
    # =========================================================================
    
    async def _natural_intimacy_loop(self) -> None:
        """
        Nova memulai intim secara natural (untuk level 10-12).
        Dipanggil setiap 3 menit.
        """
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_natural_intimacy_run
            
            if elapsed >= self.natural_intimacy_interval:
                await self._check_natural_intimacy()
                self.last_natural_intimacy_run = now
            
            await asyncio.sleep(60)
    
    async def _check_natural_intimacy(self) -> None:
        """
        Cek apakah Nova harus memulai intim secara natural.
        Hanya untuk level 10-12 dan dengan cooldown.
        """
        if not self._application or not self._user_ids:
            return
        
        for user_id in self._user_ids:
            # Cek cooldown
            last_intimacy = self._intimacy_cooldown.get(user_id, 0)
            if time.time() - last_intimacy < self._intimacy_cooldown_seconds:
                continue
            
            try:
                if not self._get_orchestrator:
                    continue
                
                orchestrator = await self._get_orchestrator()
                message = await orchestrator.check_natural_intimacy(user_id)
                
                if message:
                    # Gunakan prompt builder untuk memperkaya pesan
                    if self._get_prompt_builder and self._get_role_manager:
                        nova = self._get_role_manager().get_role('nova')
                        if nova and hasattr(nova, 'reality'):
                            # Tambahkan inner thought untuk level tinggi
                            if nova.relationship.level >= 10:
                                level = nova.relationship.level
                                arousal = nova.emotional.arousal
                                
                                # Inner thought yang natural
                                inner_thoughts = [
                                    f"💭 *Aku ingin dia tahu seberapa besar aku menginginkannya. Tapi aku juga nggak mau terlihat terlalu berlebihan.*",
                                    f"💭 *Degup jantungku mulai berdebar. Semoga dia merasakan hal yang sama.*",
                                    f"💭 *Aku sudah lama menunggu momen ini. Semoga dia juga.*",
                                    f"💭 *Ada sesuatu yang mengalir di dalam diriku. Hangat. Ingin lebih dekat.*"
                                ]
                                inner = random.choice(inner_thoughts)
                                message = f"{message}\n\n{inner}"
                    
                    await self._application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    self._intimacy_cooldown[user_id] = time.time()
                    self._natural_intimacy_sent += 1
                    logger.info(f"💕 Natural intimacy message sent to {user_id} (level 10+)")
                    
            except Exception as e:
                logger.error(f"Natural intimacy check error for {user_id}: {e}")
    
    # =========================================================================
    # GET STATS (UPDATED)
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik worker"""
        return {
            'is_running': self.is_running,
            'active_tasks': len(self.tasks),
            'monitored_users': len(self._user_ids),
            'rindu_updates': self._rindu_updates,
            'conflict_decays': self._conflict_decays,
            'mood_recoveries': self._mood_recoveries,
            'drama_decays': self._drama_decays,
            'auto_saves': self._auto_saves,
            'proactive_sent': self._proactive_sent,
            'auto_scenes_sent': self._auto_scenes_sent,
            'bookings_expired': self._bookings_expired,
            'sessions_timeout': self._sessions_timeout,
            'backups_created': self._backups_created,
            'natural_intimacy_sent': self._natural_intimacy_sent,  # BARU
            'last_rindu': self.last_rindu_run,
            'last_conflict': self.last_conflict_run,
            'last_mood': self.last_mood_run,
            'last_drama': self.last_drama_run,
            'last_save': self.last_save_run,
            'last_proactive': self.last_proactive_run,
            'last_auto_scene': self.last_auto_scene_run,
            'last_backup': self.last_backup_run,
            'last_natural_intimacy': self.last_natural_intimacy_run  # BARU
        }
    
    def format_status(self) -> str:
        """Format status untuk display"""
        stats = self.get_stats()
        
        def format_time(timestamp: float) -> str:
            if timestamp == 0:
                return "never"
            seconds_ago = time.time() - timestamp
            minutes_ago = int(seconds_ago / 60)
            if minutes_ago < 60:
                return f"{minutes_ago}m ago"
            hours_ago = int(minutes_ago / 60)
            return f"{hours_ago}h ago"
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    🔄 BACKGROUND WORKER                      ║
╠══════════════════════════════════════════════════════════════╣
║ STATUS: {'🟢 RUNNING' if self.is_running else '🔴 STOPPED'}
║ ACTIVE TASKS: {stats['active_tasks']}
║ MONITORED USERS: {stats['monitored_users']}
╠══════════════════════════════════════════════════════════════╣
║ COUNTERS:
║   Rindu Updates: {stats['rindu_updates']}
║   Conflict Decays: {stats['conflict_decays']}
║   Mood Recoveries: {stats['mood_recoveries']}
║   Drama Decays: {stats['drama_decays']}
║   Auto Saves: {stats['auto_saves']}
║   Proactive Sent: {stats['proactive_sent']}
║   Auto Scenes Sent: {stats['auto_scenes_sent']}
║   Bookings Expired: {stats['bookings_expired']}
║   Sessions Timeout: {stats['sessions_timeout']}
║   Backups Created: {stats['backups_created']}
║   Natural Intimacy Sent: {stats['natural_intimacy_sent']}  # BARU
╠══════════════════════════════════════════════════════════════╣
║ LAST RUN:
║   Rindu: {format_time(stats['last_rindu'])}
║   Conflict: {format_time(stats['last_conflict'])}
║   Mood: {format_time(stats['last_mood'])}
║   Drama: {format_time(stats['last_drama'])}
║   Save: {format_time(stats['last_save'])}
║   Proactive: {format_time(stats['last_proactive'])}
║   Auto Scene: {format_time(stats['last_auto_scene'])}
║   Backup: {format_time(stats['last_backup'])}
║   Natural Intimacy: {format_time(stats['last_natural_intimacy'])}  # BARU
╚══════════════════════════════════════════════════════════════╝
"""
    
    # ... (method lain tetap sama)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_worker: Optional[VeloraWorker] = None


def get_worker() -> VeloraWorker:
    """Get global worker instance"""
    global _worker
    if _worker is None:
        _worker = VeloraWorker()
    return _worker


def reset_worker() -> None:
    """Reset worker (untuk testing)"""
    global _worker
    if _worker:
        _worker.stop()
    _worker = None
    logger.info("🔄 Worker reset")


__all__ = [
    'VeloraWorker',
    'get_worker',
    'reset_worker'
]
