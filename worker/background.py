"""
VELORA - Background Worker
Menjalankan task-task periodic di background:
- Rindu growth (naik kalo lama gak chat)
- Conflict decay (konflik reda pelan)
- Mood recovery (mood pulih seiring waktu)
- Auto save state ke database
- Proactive chat (Nova chat duluan)
- Auto scene (untuk provider: pijat++, pelacur)
- Auto backup database
- Booking expiry check
"""

import asyncio
import time
import logging
import random
from datetime import datetime
from typing import Optional, Dict, Any, Callable

logger = logging.getLogger(__name__)


# =============================================================================
# BACKGROUND WORKER
# =============================================================================

class VeloraWorker:
    """
    Background worker untuk VELORA.
    Menjalankan task-task periodic secara async.
    """
    
    def __init__(self):
        self.is_running = False
        self.tasks: list[asyncio.Task] = []
        
        # ========== INTERVAL (detik) ==========
        self.rindu_interval = 1800      # 30 menit
        self.conflict_interval = 1800   # 30 menit
        self.mood_interval = 3600       # 1 jam
        self.save_interval = 60         # 1 menit
        self.proactive_interval = 300   # 5 menit
        self.auto_scene_interval = 15   # 15 detik
        self.booking_check_interval = 60  # 1 menit
        self.backup_interval = 21600    # 6 jam
        
        # ========== LAST RUN TIMES ==========
        self.last_rindu_run = 0
        self.last_conflict_run = 0
        self.last_mood_run = 0
        self.last_save_run = 0
        self.last_proactive_run = 0
        self.last_auto_scene_run = 0
        self.last_booking_check_run = 0
        self.last_backup_run = 0
        
        # ========== REFERENCES ==========
        self._application = None
        self._user_ids: list[int] = []
        self._get_orchestrator = None
        self._get_persistent = None
        self._get_emotional_engine = None
        self._get_relationship_manager = None
        self._get_conflict_engine = None
        self._get_brain = None
        
        # ========== PROACTIVE COOLDOWN PER USER ==========
        self._proactive_cooldown: Dict[int, float] = {}
        self._proactive_cooldown_seconds = 3600  # 1 jam
        
        logger.info("🔄 VeloraWorker initialized")
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    def initialize(self, 
                   application=None,
                   user_ids: list[int] = None,
                   get_orchestrator=None,
                   get_persistent=None,
                   get_emotional_engine=None,
                   get_relationship_manager=None,
                   get_conflict_engine=None,
                   get_brain=None):
        """Initialize dengan references ke komponen lain"""
        self._application = application
        self._user_ids = user_ids or []
        self._get_orchestrator = get_orchestrator
        self._get_persistent = get_persistent
        self._get_emotional_engine = get_emotional_engine
        self._get_relationship_manager = get_relationship_manager
        self._get_conflict_engine = get_conflict_engine
        self._get_brain = get_brain
        
        logger.info(f"🔧 VeloraWorker initialized with {len(self._user_ids)} users")
    
    def add_user(self, user_id: int) -> None:
        """Tambah user ke daftar yang dipantau"""
        if user_id not in self._user_ids:
            self._user_ids.append(user_id)
            logger.info(f"👤 User {user_id} added to worker monitoring")
    
    def remove_user(self, user_id: int) -> None:
        """Hapus user dari daftar yang dipantau"""
        if user_id in self._user_ids:
            self._user_ids.remove(user_id)
            logger.info(f"👤 User {user_id} removed from worker monitoring")
    
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
            asyncio.create_task(self._save_loop()),
            asyncio.create_task(self._proactive_loop()),
            asyncio.create_task(self._auto_scene_loop()),
            asyncio.create_task(self._booking_check_loop()),
            asyncio.create_task(self._backup_loop()),
        ]
        
        logger.info("🔄 All background loops started")
    
    async def stop(self) -> None:
        """Stop semua background tasks"""
        self.is_running = False
        
        for task in self.tasks:
            task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
        
        logger.info("🔄 All background loops stopped")
    
    # =========================================================================
    # RINDU GROWTH LOOP
    # =========================================================================
    
    async def _rindu_loop(self) -> None:
        """Rindu naik setiap kali lama gak interaksi"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_rindu_run
            
            if elapsed >= self.rindu_interval:
                await self._update_rindu()
                self.last_rindu_run = now
            
            await asyncio.sleep(60)
    
    async def _update_rindu(self) -> None:
        """Update rindu berdasarkan waktu terakhir interaksi"""
        try:
            if not self._get_emotional_engine:
                return
            
            emo = self._get_emotional_engine()
            last_interaction = emo.last_interaction
            now = time.time()
            hours_inactive = (now - last_interaction) / 3600
            
            if hours_inactive > 1:
                emo.update_rindu_from_inactivity(hours_inactive)
                logger.info(f"🌙 Rindu updated: {emo.rindu:.1f}% (inactive {hours_inactive:.1f}h)")
                
                # Sync ke tracker jika ada
                if self._get_brain:
                    brain = self._get_brain()
                    if hasattr(brain, 'tracker'):
                        brain.tracker.add_to_timeline(
                            f"Rindu naik karena {hours_inactive:.1f} jam gak chat",
                            f"Rindu: {emo.rindu:.1f}%"
                        )
                        
        except Exception as e:
            logger.error(f"Rindu update error: {e}")
    
    # =========================================================================
    # CONFLICT DECAY LOOP
    # =========================================================================
    
    async def _conflict_loop(self) -> None:
        """Conflict decay setiap 30 menit"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_conflict_run
            
            if elapsed >= self.conflict_interval:
                await self._decay_conflicts()
                self.last_conflict_run = now
            
            await asyncio.sleep(60)
    
    async def _decay_conflicts(self) -> None:
        """Decay konflik berdasarkan waktu"""
        try:
            if not self._get_conflict_engine:
                return
            
            conflict = self._get_conflict_engine()
            conflict.update_decay(0.5)  # decay 30 menit = 0.5 jam
            
            logger.debug(f"⚡ Conflict decay: cemburu={conflict.cemburu:.1f}, kecewa={conflict.kecewa:.1f}")
            
        except Exception as e:
            logger.error(f"Conflict decay error: {e}")
    
    # =========================================================================
    # MOOD RECOVERY LOOP
    # =========================================================================
    
    async def _mood_loop(self) -> None:
        """Mood recovery setiap 1 jam"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_mood_run
            
            if elapsed >= self.mood_interval:
                await self._recover_mood()
                self.last_mood_run = now
            
            await asyncio.sleep(60)
    
    async def _recover_mood(self) -> None:
        """Mood pulih seiring waktu"""
        try:
            if not self._get_emotional_engine:
                return
            
            emo = self._get_emotional_engine()
            
            # Mood naik pelan kalo gak ada konflik aktif
            if emo.mood < 0 and not emo.is_angry and not emo.is_hurt:
                recovery = min(10, abs(emo.mood) * 0.3)
                emo.mood = min(0, emo.mood + recovery)
                logger.info(f"😊 Mood recovery: {emo.mood:+.1f}")
            
            # Mood juga naik kalo trust tinggi
            if emo.trust > 70 and emo.mood < 20:
                emo.mood = min(50, emo.mood + 5)
                logger.info(f"😊 Mood +5 from high trust")
            
        except Exception as e:
            logger.error(f"Mood recovery error: {e}")
    
    # =========================================================================
    # AUTO SAVE LOOP
    # =========================================================================
    
    async def _save_loop(self) -> None:
        """Save state ke database setiap 1 menit"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_save_run
            
            if elapsed >= self.save_interval:
                await self._save_all_states()
                self.last_save_run = now
            
            await asyncio.sleep(30)
    
    async def _save_all_states(self) -> None:
        """Simpan semua state ke database"""
        try:
            if not self._get_persistent:
                return
            
            persistent = await self._get_persistent()
            
            # Save emotional state
            if self._get_emotional_engine:
                emo = self._get_emotional_engine()
                await persistent.save_emotional_state(emo)
            
            # Save relationship state
            if self._get_relationship_manager:
                rel = self._get_relationship_manager()
                await persistent.save_relationship_state(rel)
            
            # Save conflict state
            if self._get_conflict_engine:
                conflict = self._get_conflict_engine()
                await persistent.save_conflict_state(conflict)
            
            # Save world state
            if self._get_orchestrator:
                orchestrator = await self._get_orchestrator()
                if orchestrator and orchestrator.world:
                    await persistent.save_world_state(orchestrator.world)
            
            logger.debug("💾 Autosave completed")
            
        except Exception as e:
            logger.error(f"Save state error: {e}")
    
    # =========================================================================
    # PROACTIVE CHAT LOOP (NOVA)
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
        """Cek apakah Nova harus chat duluan untuk setiap user"""
        if not self._application or not self._user_ids:
            return
        
        for user_id in self._user_ids:
            # Cek cooldown
            last_proactive = self._proactive_cooldown.get(user_id, 0)
            if time.time() - last_proactive < self._proactive_cooldown_seconds:
                continue
            
            try:
                if not self._get_orchestrator:
                    continue
                
                orchestrator = await self._get_orchestrator()
                message = await orchestrator.check_proactive_for_user(user_id)
                
                if message:
                    await self._application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    self._proactive_cooldown[user_id] = time.time()
                    logger.info(f"💬 Proactive message sent to {user_id}")
                    
            except Exception as e:
                logger.error(f"Proactive check error for {user_id}: {e}")
    
    # =========================================================================
    # AUTO SCENE LOOP (UNTUK PROVIDER)
    # =========================================================================
    
    async def _auto_scene_loop(self) -> None:
        """Auto scene untuk provider (pijat++, pelacur) setiap 15 detik"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_auto_scene_run
            
            if elapsed >= self.auto_scene_interval:
                await self._send_auto_scene()
                self.last_auto_scene_run = now
            
            await asyncio.sleep(self.auto_scene_interval)
    
    async def _send_auto_scene(self) -> None:
        """Kirim auto scene untuk user yang sedang dalam sesi provider"""
        if not self._application or not self._user_ids:
            return
        
        for user_id in self._user_ids:
            try:
                if not self._get_orchestrator:
                    continue
                
                orchestrator = await self._get_orchestrator()
                message = await orchestrator.check_auto_scene(user_id)
                
                if message:
                    await self._application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    logger.debug(f"🎬 Auto scene sent to {user_id}")
                    
            except Exception as e:
                logger.error(f"Auto scene error for {user_id}: {e}")
    
    # =========================================================================
    # BOOKING CHECK LOOP
    # =========================================================================
    
    async def _booking_check_loop(self) -> None:
        """Cek booking expiry setiap 1 menit"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_booking_check_run
            
            if elapsed >= self.booking_check_interval:
                await self._check_bookings()
                self.last_booking_check_run = now
            
            await asyncio.sleep(60)
    
    async def _check_bookings(self) -> None:
        """Cek apakah ada booking yang habis"""
        if not self._application or not self._user_ids:
            return
        
        for user_id in self._user_ids:
            try:
                if not self._get_orchestrator:
                    continue
                
                orchestrator = await self._get_orchestrator()
                
                # Dapatkan role aktif
                active_role = orchestrator.get_active_role(user_id)
                if not active_role:
                    continue
                
                # Cek booking expiry
                message = await orchestrator.check_auto_scene(user_id)
                if message and "habis" in message.lower():
                    # Booking habis, kirim notifikasi
                    await self._application.bot.send_message(
                        chat_id=user_id,
                        text=f"⏰ *Booking Telah Berakhir*\n\n{message}",
                        parse_mode='Markdown'
                    )
                    logger.info(f"⏰ Booking expired for user {user_id}")
                    
            except Exception as e:
                logger.error(f"Booking check error for {user_id}: {e}")
    
    # =========================================================================
    # AUTO BACKUP LOOP
    # =========================================================================
    
    async def _backup_loop(self) -> None:
        """Auto backup database setiap 6 jam"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_backup_run
            
            if elapsed >= self.backup_interval:
                await self._auto_backup()
                self.last_backup_run = now
            
            await asyncio.sleep(3600)
    
    async def _auto_backup(self) -> None:
        """Auto backup database"""
        try:
            from pathlib import Path
            from datetime import datetime
            
            if not self._get_persistent:
                return
            
            persistent = await self._get_persistent()
            db_path = persistent.db_path
            
            backup_dir = Path("data/backups")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            if db_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"velora_auto_{timestamp}.db"
                
                await persistent.create_backup(backup_path)
                
                # Hapus backup auto yang lebih dari 7 hari
                import shutil
                for b in backup_dir.glob("velora_auto_*.db"):
                    age = time.time() - b.stat().st_mtime
                    if age > 7 * 24 * 3600:
                        b.unlink()
                        logger.info(f"🗑️ Deleted old backup: {b.name}")
                
                logger.info(f"💾 Auto backup saved: {backup_path.name}")
                
        except Exception as e:
            logger.error(f"Auto backup error: {e}")
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik worker"""
        return {
            'is_running': self.is_running,
            'active_tasks': len(self.tasks),
            'monitored_users': len(self._user_ids),
            'last_rindu': self.last_rindu_run,
            'last_conflict': self.last_conflict_run,
            'last_mood': self.last_mood_run,
            'last_save': self.last_save_run,
            'last_proactive': self.last_proactive_run,
            'last_auto_scene': self.last_auto_scene_run,
            'last_backup': self.last_backup_run
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
║ LAST RUN:
║   Rindu: {format_time(stats['last_rindu'])}
║   Conflict: {format_time(stats['last_conflict'])}
║   Mood: {format_time(stats['last_mood'])}
║   Save: {format_time(stats['last_save'])}
║   Proactive: {format_time(stats['last_proactive'])}
║   Auto Scene: {format_time(stats['last_auto_scene'])}
║   Backup: {format_time(stats['last_backup'])}
╚══════════════════════════════════════════════════════════════╝
"""


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


__all__ = [
    'VeloraWorker',
    'get_worker'
]
