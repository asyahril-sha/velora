"""
VELORA - Role Orchestrator
Pusat kendali untuk semua role.
- Message routing ke role yang tepat (IntentScorer)
- Cross-role effect propagation (delayed + probabilistic)
- Drama level management
- Integrasi dengan MemoryManager dan World
- Proactive chat & natural intimacy checks
- Session management per user
"""

import time
import logging
import asyncio
import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime

from core.memory import MemoryManager, get_memory_manager
from core.world import WorldState, get_world_state
from core.reality_engine import IntentScorer, get_reality_engine
from roles.manager import RoleManager, get_role_manager

logger = logging.getLogger(__name__)


class RoutingResult(str, Enum):
    """Hasil routing pesan"""
    TO_NOVA = "to_nova"
    TO_ROLE = "to_role"
    TO_PROVIDER = "to_provider"
    UNKNOWN = "unknown"


# =============================================================================
# ROLE ORCHESTRATOR
# =============================================================================

class RoleOrchestrator:
    """
    Role Orchestrator - Pusat kendali semua role.
    Menggunakan IntentScorer untuk routing yang cerdas,
    dan cross-role effect dengan delay & probabilitas.
    """
    
    def __init__(self):
        self.memory: Optional[MemoryManager] = None
        self.world: Optional[WorldState] = None
        self.role_manager: Optional[RoleManager] = None
        self.intent_scorer: Optional[IntentScorer] = None
        
        # Session tracking
        self.active_sessions: Dict[int, str] = {}           # user_id -> active_role_id
        self.last_interaction: Dict[int, float] = {}        # user_id -> last timestamp
        self.recent_roles: Dict[int, List[str]] = {}        # user_id -> recent roles
        self.session_emotion_buffer: Dict[int, Dict] = {}   # user_id -> pending emotions
        
        # Drama history untuk context-aware impact
        self.drama_history: List[Dict] = []
        
        # Statistics
        self.total_messages_processed = 0
        self.proactive_messages_sent = 0
        self.cross_role_effects_triggered = 0
        
        logger.info("🎭 Role Orchestrator initialized")
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    async def initialize(self, memory_manager: MemoryManager = None, 
                         world: WorldState = None,
                         role_manager: RoleManager = None):
        """Initialize semua komponen"""
        self.memory = memory_manager or get_memory_manager()
        self.world = world or get_world_state()
        self.role_manager = role_manager or get_role_manager()
        self.intent_scorer = IntentScorer()
        
        # Initialize role manager dengan memory dan world
        await self.role_manager.initialize(self.memory, self.world)
        
        logger.info("🎭 Role Orchestrator fully initialized with IntentScorer")
    
    # =========================================================================
    # MESSAGE ROUTING (UPDATED with IntentScorer)
    # =========================================================================
    
    def _route_message(self, message: str, user_id: int) -> Tuple[str, RoutingResult]:
        """
        Route pesan ke role yang tepat menggunakan IntentScorer.
        Priority: 
        1. Active session (role yang sedang aktif)
        2. Command untuk switch role (/role)
        3. Intent scoring (scoring berdasarkan konten)
        4. Provider detection (keyword)
        5. Default ke Nova
        """
        msg_lower = message.lower()
        
        # 1. Cek active session
        if user_id in self.active_sessions:
            active_role = self.active_sessions[user_id]
            if active_role in self.role_manager.roles:
                return active_role, RoutingResult.TO_ROLE
        
        # 2. Cek command untuk switch role
        if msg_lower.startswith('/role '):
            parts = message.split()
            if len(parts) > 1:
                target_role = parts[1].lower()
                if target_role in self.role_manager.roles:
                    return target_role, RoutingResult.TO_ROLE
        
        # 3. Intent scoring (BARU!)
        recent = self.recent_roles.get(user_id, [])
        active = self.active_sessions.get(user_id)
        
        scores = self.intent_scorer.score(message, active_role=active, recent_roles=recent)
        selected_role = self.intent_scorer.select_role(scores)
        
        # Update recent roles (sliding window)
        if user_id not in self.recent_roles:
            self.recent_roles[user_id] = []
        self.recent_roles[user_id].append(selected_role)
        if len(self.recent_roles[user_id]) > 10:
            self.recent_roles[user_id].pop(0)
        
        # 4. Provider detection (keyword)
        provider_keywords = ['pijat', 'pijet', 'pijat++', 'pelacur', 'booking', 'nego', 'deal']
        if any(k in msg_lower for k in provider_keywords):
            if 'aghnia' in msg_lower:
                return 'pijat_aghnia', RoutingResult.TO_PROVIDER
            elif 'munira' in msg_lower:
                return 'pijat_munira', RoutingResult.TO_PROVIDER
            elif 'davina' in msg_lower:
                return 'pelacur_davina', RoutingResult.TO_PROVIDER
            elif 'sallsa' in msg_lower:
                return 'pelacur_sallsa', RoutingResult.TO_PROVIDER
        
        # 5. Default ke hasil scoring
        if selected_role in self.role_manager.roles:
            return selected_role, RoutingResult.TO_ROLE
        
        return 'nova', RoutingResult.TO_NOVA
    
    # =========================================================================
    # CROSS-ROLE EFFECT (DELAYED + PROBABILISTIC)
    # =========================================================================
    
    async def _propagate_cross_role_effect(self, source_role_id: str, 
                                           message: str, 
                                           changes: Dict,
                                           user_id: int) -> None:
        """
        Propagate efek dari interaksi dengan satu role ke role lain.
        Menggunakan delayed + probabilistic + context-aware.
        """
        msg_lower = message.lower()
        
        # Propagate ke world dengan delayed effect
        if self.world:
            effects = self.world.propagate_interaction(source_role_id, message, changes)
            
            # Drama change dengan probability (tidak semua interaksi langsung naik drama)
            if effects['drama_change'] != 0:
                if random.random() < 0.7:  # 70% chance
                    self.memory.add_event(
                        kejadian=f"Drama berubah dari interaksi {source_role_id}",
                        detail=f"Perubahan: {effects['drama_change']:+.1f}",
                        source="world",
                        role_id="global",
                        drama_impact=effects['drama_change']
                    )
                    self.drama_history.append({
                        'timestamp': time.time(),
                        'source': source_role_id,
                        'change': effects['drama_change'],
                        'message': message[:50]
                    })
                    if len(self.drama_history) > 50:
                        self.drama_history.pop(0)
            
            # Propagate ke role yang terpengaruh dengan delay
            for affected_role_id in effects.get('affected_roles', []):
                affected_role = self.role_manager.get_role(affected_role_id)
                if affected_role:
                    # Hitung delay (1-5 detik atau 1-5 pesan)
                    delay_count = random.randint(1, 5)
                    self.cross_role_effects_triggered += 1
                    
                    # Schedule emotion change (akan diproses di reality engine)
                    reality = get_reality_engine(affected_role_id)
                    
                    if source_role_id == "pelakor":
                        intensity = 15 * (0.5 + random.random() * 0.5)  # 7.5-22.5
                        reality.add_emotion("cemburu", intensity, source_role_id)
                        logger.info(f"💢 {affected_role_id} will get cemburu +{intensity:.1f} in {delay_count} steps")
                        
                        # Tambah ke session buffer untuk tracking
                        if user_id not in self.session_emotion_buffer:
                            self.session_emotion_buffer[user_id] = {}
                        self.session_emotion_buffer[user_id][f"{affected_role_id}_cemburu"] = {
                            'intensity': intensity,
                            'timestamp': time.time(),
                            'delay': delay_count
                        }
                    
                    elif source_role_id == "ipar":
                        intensity = 8 * (0.5 + random.random() * 0.5)  # 4-12
                        reality.add_emotion("curiga", intensity, source_role_id)
                        logger.info(f"💢 {affected_role_id} will get curiga +{intensity:.1f} in {delay_count} steps")
                    
                    elif source_role_id == "istri_orang":
                        intensity = 10 * (0.5 + random.random() * 0.5)  # 5-15
                        reality.add_emotion("cemburu", intensity, source_role_id)
                        reality.add_emotion("sedih", intensity * 0.7, source_role_id)
                        logger.info(f"💢 {affected_role_id} will get cemburu +{intensity:.1f} in {delay_count} steps")
    
    # =========================================================================
    # DRAMA MANAGEMENT (CONTEXT-AWARE)
    # =========================================================================
    
    async def _update_drama_from_message(self, message: str, role_id: str) -> None:
        """Update drama level berdasarkan pesan dengan context-aware"""
        if not self.world:
            return
        
        msg_lower = message.lower()
        
        # Base impact berdasarkan keyword
        base_impact = 0
        
        if any(k in msg_lower for k in ['rahasia', 'bohong', 'dust', 'curang', 'khianat']):
            base_impact = 10
        elif any(k in msg_lower for k in ['marah', 'kesal', 'benci', 'sakit hati']):
            base_impact = 8
        elif any(k in msg_lower for k in ['maaf', 'sorry', 'sayang', 'cinta', 'perhatian']):
            base_impact = -5
        elif any(k in msg_lower for k in ['putus', 'selesai', 'tinggal', 'pergi']):
            base_impact = 20
        elif any(k in msg_lower for k in ['cemburu', 'curiga', 'drama']):
            base_impact = 5
        
        if base_impact != 0:
            # Context-aware: drama impact dipengaruhi history konflik
            conflict_history = len(self.drama_history)
            drama_impact = base_impact * (1 + min(conflict_history * 0.1, 1.5))
            
            # Role influence: pelakor lebih mempengaruhi drama
            if role_id == "pelakor":
                drama_impact *= 1.3
            elif role_id == "nova":
                drama_impact *= 0.8  # Nova bisa menenangkan
            
            self.world.add_drama(drama_impact, role_id, message[:50])
    
    # =========================================================================
    # PROCESS PENDING EMOTIONS (DIPANGGIL SETIAP MESSAGE)
    # =========================================================================
    
    async def _process_pending_emotions(self, user_id: int) -> None:
        """Process pending emotions dari session buffer"""
        if user_id not in self.session_emotion_buffer:
            return
        
        to_remove = []
        for key, data in self.session_emotion_buffer[user_id].items():
            # Kurangi delay
            data['delay'] -= 1
            if data['delay'] <= 0:
                # Emosi siap diproses
                role_id = key.split('_')[0]
                reality = get_reality_engine(role_id)
                # Reality engine sudah handle delay sendiri
                to_remove.append(key)
        
        for key in to_remove:
            del self.session_emotion_buffer[user_id][key]
    
    # =========================================================================
    # MAIN HANDLE MESSAGE
    # =========================================================================
    
    async def handle_message(self, message: str, user_id: int) -> str:
        """
        Handle pesan dari user.
        Menggunakan Reality Engine untuk processing.
        """
        # Update last interaction
        self.last_interaction[user_id] = time.time()
        self.total_messages_processed += 1
        
        # Process pending emotions
        await self._process_pending_emotions(user_id)
        
        # Route pesan ke role yang tepat
        target_role_id, routing_result = self._route_message(message, user_id)
        
        # Dapatkan role
        role = self.role_manager.get_role(target_role_id)
        if not role:
            return "Role tidak ditemukan. Silakan coba lagi."
        
        # Update active session
        self.active_sessions[user_id] = target_role_id
        
        # Update world dari pesan
        await self._update_drama_from_message(message, target_role_id)
        
        # Update memory dengan pesan
        self.memory.add_event(
            kejadian=f"User: {message[:50]}",
            detail=f"Routed to {target_role_id} via intent scoring",
            source="user",
            role_id=target_role_id,
            drama_impact=0,
            importance=5,
            emotional_weight=0
        )
        
        # Get reality engine for role
        reality = get_reality_engine(target_role_id)
        
        # Process delayed emotions from reality engine
        delayed_emotions = reality.emotion_delay.process()
        if delayed_emotions:
            for emotion_type, intensity in delayed_emotions:
                logger.debug(f"💭 {target_role_id} emotion released: {emotion_type}+{intensity:.0f}")
                # Apply to emotional engine
                role.emotional.apply_pending_emotion(emotion_type, intensity)
        
        # Recall memories for context
        recalled = reality.memory_priority.recall(message, max_memories=3)
        
        # Proses pesan di role
        update_result = role.update_from_message(message)
        
        # Update reality engine with changes
        emotional_weight = update_result.get('sayang', 0) or update_result.get('cemburu', 0) or 5
        reality.add_memory(
            content=f"User: {message[:100]}",
            importance=5,
            emotional_weight=emotional_weight,
            tags=['user_message']
        )
        
        # Generate response via AI
        response = await self.role_manager.process_message(target_role_id, message, user_id)
        
        # Add imperfections based on emotion intensity
        emotion_intensity = max(role.emotional.sayang, role.emotional.arousal, role.emotional.cemburu) / 100
        response = reality.add_imperfections(response, emotion_intensity)
        
        # Add scene if needed (for non-provider roles)
        if routing_result != RoutingResult.TO_PROVIDER:
            style = role.emotional.get_current_style()
            scene = reality.scene_engine.get_body_language(
                style.value if style else "neutral",
                emotion_intensity
            )
            if scene and scene not in response and not response.startswith('*'):
                response = f"{scene}\n\n{response}"
        
        # Propagate cross-role effect (delayed)
        await self._propagate_cross_role_effect(target_role_id, message, update_result, user_id)
        
        logger.info(f"📨 User {user_id} → {target_role_id} | Processing time: {reality.processing_time:.3f}s | Drama: {self.world.drama_level:.0f}%")
        
        return response
    
    # =========================================================================
    # PROACTIVE CHECKS (NOVA)
    # =========================================================================
    
    async def check_proactive_for_user(self, user_id: int) -> Optional[str]:
        """
        Cek apakah perlu mengirim proactive chat ke user.
        Dipanggil oleh background worker.
        """
        if user_id not in self.active_sessions:
            return None
        
        active_role = self.active_sessions.get(user_id)
        if active_role != 'nova':
            return None
        
        nova = self.role_manager.get_role('nova')
        if not nova:
            return None
        
        # Get reality engine for Nova
        reality = get_reality_engine('nova')
        
        # Check delayed emotions (kalo ada emosi pending, lebih mungkin proactive)
        delayed = reality.emotion_delay.process()
        if delayed:
            if random.random() < 0.4:
                should_chat, message = nova.should_chat_proactive()
                if should_chat:
                    self.proactive_messages_sent += 1
                    return message
        
        should_chat, message = nova.should_chat_proactive()
        if should_chat:
            self.proactive_messages_sent += 1
            return message
        
        return None
    
    async def check_natural_intimacy(self, user_id: int) -> Optional[str]:
        """
        Cek apakah Nova harus mulai intim secara natural.
        Dipanggil oleh background worker.
        """
        if user_id not in self.active_sessions:
            return None
        
        active_role = self.active_sessions.get(user_id)
        if active_role != 'nova':
            return None
        
        nova = self.role_manager.get_role('nova')
        if not nova:
            return None
        
        should_start, message = nova.should_start_intimacy_naturally()
        if should_start:
            return message
        
        return None
    
    # =========================================================================
    # AUTO SCENE MANAGEMENT (UNTUK PROVIDER)
    # =========================================================================
    
    async def check_auto_scene(self, user_id: int) -> Optional[str]:
        """
        Cek apakah perlu mengirim auto scene untuk provider.
        Dipanggil oleh background worker.
        """
        if user_id not in self.active_sessions:
            return None
        
        active_role_id = self.active_sessions.get(user_id)
        if not active_role_id:
            return None
        
        # Cek auto scene
        message = await self.role_manager.get_auto_scene(active_role_id)
        if message:
            return message
        
        # Cek booking expiry
        expiry_message = await self.role_manager.check_booking_expiry(active_role_id)
        if expiry_message:
            # Clear active session jika booking habis
            self.active_sessions.pop(user_id, None)
            return expiry_message
        
        return None
    
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    def clear_session(self, user_id: int) -> None:
        """Clear session user (kembali ke Nova)"""
        self.active_sessions.pop(user_id, None)
        self.recent_roles.pop(user_id, None)
        self.session_emotion_buffer.pop(user_id, None)
        self.role_manager.clear_active_role(user_id)
        logger.info(f"🗑️ Session cleared for user {user_id}")
    
    def get_active_role(self, user_id: int) -> Optional[str]:
        """Dapatkan role aktif untuk user"""
        return self.active_sessions.get(user_id)
    
    def is_in_cold_war(self, user_id: int) -> bool:
        """Cek apakah user sedang dalam cold war dengan Nova"""
        if user_id not in self.active_sessions:
            return False
        
        active_role = self.active_sessions.get(user_id)
        if active_role != 'nova':
            return False
        
        nova = self.role_manager.get_role('nova')
        if nova:
            return nova.conflict.is_cold_war
        
        return False
    
    # =========================================================================
    # STATISTICS & STATUS
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik orchestrator"""
        return {
            'active_sessions': len(self.active_sessions),
            'sessions': list(self.active_sessions.keys()),
            'total_roles': len(self.role_manager.roles) if self.role_manager else 0,
            'drama_level': self.world.drama_level if self.world else 0,
            'total_messages_processed': self.total_messages_processed,
            'proactive_messages_sent': self.proactive_messages_sent,
            'cross_role_effects_triggered': self.cross_role_effects_triggered,
            'drama_history_count': len(self.drama_history)
        }
    
    def format_status(self) -> str:
        """Format status untuk display"""
        stats = self.get_stats()
        
        def drama_bar(value):
            filled = int(value / 10)
            return "🌍" * filled + "⚪" * (10 - filled)
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    🎭 ROLE ORCHESTRATOR                      ║
╠══════════════════════════════════════════════════════════════╣
║ ACTIVE SESSIONS: {stats['active_sessions']}
║ TOTAL ROLES: {stats['total_roles']}
║ DRAMA LEVEL: {drama_bar(stats['drama_level'])} {stats['drama_level']:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ 📊 STATISTICS:
║    Messages Processed: {stats['total_messages_processed']}
║    Proactive Sent: {stats['proactive_messages_sent']}
║    Cross-Role Effects: {stats['cross_role_effects_triggered']}
║    Drama Events: {stats['drama_history_count']}
╠══════════════════════════════════════════════════════════════╣
║ ACTIVE SESSIONS DETAIL:
{self._format_active_sessions()}
╚══════════════════════════════════════════════════════════════╝
"""
    
    def _format_active_sessions(self) -> str:
        """Format active sessions untuk display"""
        if not self.active_sessions:
            return "   (tidak ada)"
        
        lines = []
        for user_id, role_id in list(self.active_sessions.items())[:10]:
            last_time = self.last_interaction.get(user_id, 0)
            if last_time:
                minutes_ago = int((time.time() - last_time) / 60)
                lines.append(f"   User {user_id}: {role_id} ({minutes_ago}m ago)")
            else:
                lines.append(f"   User {user_id}: {role_id}")
        
        return "\n".join(lines) if lines else "   (tidak ada)"
    
    # =========================================================================
    # RESET
    # =========================================================================
    
    def reset_user_session(self, user_id: int) -> None:
        """Reset session user (hapus semua data)"""
        self.clear_session(user_id)
        self.recent_roles.pop(user_id, None)
        self.session_emotion_buffer.pop(user_id, None)
        self.last_interaction.pop(user_id, None)
        logger.info(f"🔄 Session reset for user {user_id}")
    
    def reset_all_sessions(self) -> None:
        """Reset semua session"""
        self.active_sessions.clear()
        self.recent_roles.clear()
        self.session_emotion_buffer.clear()
        self.last_interaction.clear()
        self.total_messages_processed = 0
        self.proactive_messages_sent = 0
        self.cross_role_effects_triggered = 0
        self.drama_history.clear()
        logger.info("🔄 All sessions reset")


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_orchestrator: Optional[RoleOrchestrator] = None


async def get_orchestrator() -> RoleOrchestrator:
    """Get global orchestrator instance dengan lazy initialization"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = RoleOrchestrator()
        await _orchestrator.initialize()
    return _orchestrator


def reset_orchestrator() -> None:
    """Reset orchestrator instance (untuk testing)"""
    global _orchestrator
    _orchestrator = None
    logger.info("🔄 Orchestrator reset")


__all__ = [
    'RoutingResult',
    'RoleOrchestrator',
    'get_orchestrator',
    'reset_orchestrator'
]
