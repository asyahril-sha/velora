"""
VELORA - Role Orchestrator
Pusat kendali untuk semua role.
- Message routing ke role yang tepat
- Cross-role effect propagation
- Drama level management
- Integrasi dengan MemoryManager dan World
"""

import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from core.memory import MemoryManager, get_memory_manager
from core.world import WorldState, get_world_state
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
    Mengatur alur pesan, memilih role yang tepat, dan propagate efek.
    """
    
    def __init__(self):
        self.memory: Optional[MemoryManager] = None
        self.world: Optional[WorldState] = None
        self.role_manager: Optional[RoleManager] = None
        
        self.active_sessions: Dict[int, str] = {}  # user_id -> active_role_id
        self.last_interaction: Dict[int, float] = {}
        
        # Keyword mapping untuk routing
        self.role_keywords = {
            'nova': ['nova', 'sayang', 'kangen', 'rindu', 'cinta'],
            'ipar': ['dietha', 'ipar', 'tasya', 'adik'],
            'teman_kantor': ['ipeh', 'kantor', 'kerja', 'teman kantor', 'musdalifah'],
            'pelakor': ['widya', 'pelakor', 'wid', 'rebut'],
            'istri_orang': ['siska', 'sika', 'istri', 'suami'],
            'pijat_aghnia': ['aghnia', 'pijat aghnia', 'pijat++ aghnia'],
            'pijat_munira': ['munira', 'pijat munira', 'pijat++ munira'],
            'pelacur_davina': ['davina', 'pelacur davina', 'davina karamoy'],
            'pelacur_sallsa': ['sallsa', 'pelacur sallsa', 'sallsa binta']
        }
        
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
        
        # Initialize role manager dengan memory dan world
        await self.role_manager.initialize(self.memory, self.world)
        
        logger.info("🎭 Role Orchestrator fully initialized")
    
    # =========================================================================
    # MESSAGE ROUTING
    # =========================================================================
    
    def _route_message(self, message: str, user_id: int) -> Tuple[str, RoutingResult]:
        """
        Route pesan ke role yang tepat.
        Priority: 1. Active session, 2. Keyword detection, 3. Default ke Nova
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
        
        # 3. Keyword detection
        for role_id, keywords in self.role_keywords.items():
            for keyword in keywords:
                if keyword in msg_lower:
                    return role_id, RoutingResult.TO_ROLE
        
        # 4. Provider keywords (khusus untuk layanan)
        provider_keywords = ['pijat', 'pijet', 'pijat++', 'pelacur', 'booking', 'nego', 'deal']
        if any(k in msg_lower for k in provider_keywords):
            # Cari provider yang paling relevan
            if 'aghnia' in msg_lower:
                return 'pijat_aghnia', RoutingResult.TO_PROVIDER
            elif 'munira' in msg_lower:
                return 'pijat_munira', RoutingResult.TO_PROVIDER
            elif 'davina' in msg_lower:
                return 'pelacur_davina', RoutingResult.TO_PROVIDER
            elif 'sallsa' in msg_lower:
                return 'pelacur_sallsa', RoutingResult.TO_PROVIDER
            elif 'pijat' in msg_lower:
                # Default pijat ke Aghnia
                return 'pijat_aghnia', RoutingResult.TO_PROVIDER
            elif 'pelacur' in msg_lower:
                # Default pelacur ke Davina
                return 'pelacur_davina', RoutingResult.TO_PROVIDER
        
        # 5. Default ke Nova
        return 'nova', RoutingResult.TO_NOVA
    
    # =========================================================================
    # CROSS-ROLE EFFECT PROPAGATION
    # =========================================================================
    
    async def _propagate_cross_role_effect(self, source_role_id: str, 
                                           message: str, 
                                           changes: Dict) -> None:
        """
        Propagate efek dari interaksi dengan satu role ke role lain.
        Ini adalah inti dari cross-role effect.
        """
        msg_lower = message.lower()
        
        # Propagate ke world
        if self.world:
            effects = self.world.propagate_interaction(source_role_id, message, changes)
            
            # Update memory dengan efek
            if effects['drama_change'] != 0:
                self.memory.add_event(
                    kejadian=f"Drama berubah dari interaksi {source_role_id}",
                    detail=f"Perubahan: {effects['drama_change']:+.1f}",
                    source="world",
                    role_id="global",
                    drama_impact=effects['drama_change']
                )
            
            # Propagate ke role yang terpengaruh
            for affected_role_id in effects.get('affected_roles', []):
                affected_role = self.role_manager.get_role(affected_role_id)
                if affected_role:
                    # Update emotional affected role
                    if source_role_id == "pelakor":
                        affected_role.emotional.cemburu = min(100, affected_role.emotional.cemburu + 15)
                        logger.info(f"💢 {affected_role_id} cemburu karena chat dengan pelakor")
                    
                    elif source_role_id == "ipar":
                        affected_role.emotional.cemburu = min(100, affected_role.emotional.cemburu + 8)
                        logger.info(f"💢 {affected_role_id} curiga karena chat dengan ipar")
                    
                    elif source_role_id == "istri_orang":
                        affected_role.emotional.cemburu = min(100, affected_role.emotional.cemburu + 10)
                        affected_role.emotional.mood = max(-50, affected_role.emotional.mood - 5)
                        logger.info(f"💢 {affected_role_id} terpengaruh oleh chat dengan istri orang")
                    
                    # Update memory affected role
                    self.memory.add_event(
                        kejadian=f"Terpengaruh dari interaksi {source_role_id}",
                        detail=effects.get('message', ''),
                        source=source_role_id,
                        role_id=affected_role_id,
                        drama_impact=effects.get('drama_change', 0) / 2
                    )
        
        # Propagate ke memory untuk cross-role knowledge
        if self.memory:
            # Role yang tahu tentang interaksi ini (sesuai awareness)
            for role_id, role in self.role_manager.roles.items():
                if role_id != source_role_id:
                    # Cek apakah role ini boleh tahu
                    can_know = False
                    if role.awareness_level.value == "full":
                        can_know = True
                    elif role.awareness_level.value == "normal":
                        if source_role_id in ['nova', 'pelakor']:
                            can_know = True
                    elif role.awareness_level.value == "limited":
                        if source_role_id == 'nova':
                            can_know = True
                    
                    if can_know:
                        fact = f"{source_role_id} berinteraksi dengan user: {message[:50]}"
                        self.memory.add_role_knowledge(role_id, fact)
    
    # =========================================================================
    # DRAMA MANAGEMENT
    # =========================================================================
    
    async def _update_drama_from_message(self, message: str, role_id: str) -> None:
        """Update drama level berdasarkan pesan"""
        if not self.world:
            return
        
        msg_lower = message.lower()
        drama_impact = 0
        
        # Deteksi kata kunci yang mempengaruhi drama
        if any(k in msg_lower for k in ['rahasia', 'bohong', 'dust', 'curang']):
            drama_impact = 10
        elif any(k in msg_lower for k in ['marah', 'kesal', 'benci']):
            drama_impact = 8
        elif any(k in msg_lower for k in ['maaf', 'sorry', 'sayang', 'cinta']):
            drama_impact = -5
        elif any(k in msg_lower for k in ['putus', 'selesai', 'tinggal']):
            drama_impact = 20
        
        if drama_impact != 0:
            self.world.add_drama(drama_impact, role_id, message[:50])
    
    # =========================================================================
    # MAIN HANDLE MESSAGE
    # =========================================================================
    
    async def handle_message(self, message: str, user_id: int) -> str:
        """
        Handle pesan dari user.
        Ini adalah method utama yang dipanggil oleh bot.
        """
        # Update last interaction
        self.last_interaction[user_id] = time.time()
        
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
            detail=f"Routed to {target_role_id}",
            source="user",
            role_id=target_role_id,
            drama_impact=0
        )
        
        # Proses pesan di role
        response = await self.role_manager.process_message(target_role_id, message, user_id)
        
        # Propagate cross-role effect
        changes = {}
        await self._propagate_cross_role_effect(target_role_id, message, changes)
        
        # Update memory dengan response
        self.memory.add_event(
            kejadian=f"{role.name}: {response[:50]}",
            detail=f"Response to user",
            source=target_role_id,
            role_id=target_role_id,
            drama_impact=0
        )
        
        # Cek apakah perlu ada efek tambahan (cold war, dll)
        if target_role_id == 'nova':
            # Cek cold war status
            if role.conflict.is_cold_war:
                response = f"*{role.name} diem sebentar, gak liat kamu*\n\n{response}"
        
        logger.info(f"📨 Message from user {user_id} → {target_role_id} | Response length: {len(response)}")
        
        return response
    
    # =========================================================================
    # PROACTIVE CHECKS (DIPANGGIL BACKGROUND WORKER)
    # =========================================================================
    
    async def check_proactive_for_user(self, user_id: int) -> Optional[str]:
        """
        Cek apakah perlu mengirim proactive chat ke user.
        Dipanggil oleh background worker.
        """
        # Cek natural intimacy initiation dari Nova
        if user_id in self.active_sessions:
            active_role = self.active_sessions.get(user_id)
            if active_role == 'nova':
                nova = self.role_manager.get_role('nova')
                if nova:
                    should_start, message = nova.should_start_intimacy_naturally()
                    if should_start:
                        return message
        
        # Cek proactive chat dari Nova
        nova = self.role_manager.get_role('nova')
        if nova:
            should_chat, message = nova.should_chat_proactive()
            if should_chat:
                return message
        
        return None
    
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
            'total_memory_events': self.memory.total_events if self.memory else 0
        }
    
    def format_status(self) -> str:
        """Format status untuk display"""
        stats = self.get_stats()
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    🎭 ROLE ORCHESTRATOR                      ║
╠══════════════════════════════════════════════════════════════╣
║ ACTIVE SESSIONS: {stats['active_sessions']}
║ TOTAL ROLES: {stats['total_roles']}
║ DRAMA LEVEL: {stats['drama_level']:.0f}%
║ TOTAL MEMORY EVENTS: {stats['total_memory_events']}
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
        for user_id, role_id in list(self.active_sessions.items())[:5]:
            last_time = self.last_interaction.get(user_id, 0)
            if last_time:
                minutes_ago = int((time.time() - last_time) / 60)
                lines.append(f"   User {user_id}: {role_id} ({minutes_ago}m ago)")
            else:
                lines.append(f"   User {user_id}: {role_id}")
        
        return "\n".join(lines)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_orchestrator: Optional[RoleOrchestrator] = None


async def get_orchestrator() -> RoleOrchestrator:
    """Get global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = RoleOrchestrator()
        await _orchestrator.initialize()
    return _orchestrator


__all__ = [
    'RoutingResult',
    'RoleOrchestrator',
    'get_orchestrator'
]
