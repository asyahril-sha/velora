"""
VELORA - Role Session Manager
Mengelola active session per user untuk routing yang konsisten.
SOLUSI untuk masalah: setelah /role, role lain yang menjawab, BUKAN Nova.

CARA INTEGRASI (TANPA MENGUBAH FUNGSI EXISTING):
1. Import session_manager di file yang membutuhkan
2. Tambahkan panggilan di awal fungsi (tanpa menghapus kode lama)
3. Session manager akan bekerja PARALEL dengan sistem lama
4. Prioritaskan session manager untuk routing
"""

import time
import logging
from typing import Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field

# ========== HAPUS INI! ==========
# from core.orchestrator import get_orchestrator   # <-- CIRCULAR IMPORT!
# =================================

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class SessionMode(str, Enum):
    """Mode sesi user"""
    CHAT = "chat"           # Chat dengan Nova (default)
    ROLEPLAY = "roleplay"   # Roleplay dengan Nova (mode intim)
    ROLE = "role"           # Berinteraksi dengan role lain


# =============================================================================
# SESSION DATA
# =============================================================================

@dataclass
class UserSession:
    """Data sesi untuk satu user"""
    user_id: int
    mode: SessionMode = SessionMode.CHAT
    active_role: str = "nova"           # role yang sedang aktif
    last_interaction: float = field(default_factory=time.time)
    conversation_count: int = 0
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'mode': self.mode.value,
            'active_role': self.active_role,
            'last_interaction': self.last_interaction,
            'conversation_count': self.conversation_count,
            'created_at': self.created_at
        }
    
    def is_active(self, timeout_seconds: int = 3600) -> bool:
        """Cek apakah session masih aktif (belum timeout)"""
        return time.time() - self.last_interaction < timeout_seconds


# =============================================================================
# ROLE SESSION MANAGER
# =============================================================================

class RoleSessionManager:
    """
    Manager untuk session user.
    SATU-SATUNYA sumber kebenaran untuk role aktif per user.
    
    DESIGN: 
    - Bekerja PARALEL dengan sistem lama (user_mode, active_sessions)
    - TIDAK menghapus atau mengganti fungsi existing
    - Cukup ditambahkan panggilan di awal fungsi handler
    """
    
    def __init__(self):
        self._sessions: Dict[int, UserSession] = {}
        self._enabled: bool = True
        logger.info("🎭 RoleSessionManager initialized (running parallel with old system)")
    
    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    
    def enable(self) -> None:
        """Enable session manager"""
        self._enabled = True
        logger.info("🎭 RoleSessionManager enabled")
    
    def disable(self) -> None:
        """Disable session manager (fallback ke old system)"""
        self._enabled = False
        logger.info("🎭 RoleSessionManager disabled (fallback to old system)")
    
    def is_enabled(self) -> bool:
        """Cek apakah session manager aktif"""
        return self._enabled
    
    # =========================================================================
    # GETTERS
    # =========================================================================
    
    def get_session(self, user_id: int, auto_create: bool = True) -> Optional[UserSession]:
        """Dapatkan session user, buat baru jika auto_create=True"""
        if user_id not in self._sessions and auto_create:
            self._sessions[user_id] = UserSession(user_id=user_id)
            logger.debug(f"📝 New session created for user {user_id}")
        return self._sessions.get(user_id)
    
    def get_active_role(self, user_id: int) -> str:
        """Dapatkan role aktif untuk user"""
        session = self.get_session(user_id)
        if session:
            return session.active_role
        return "nova"
    
    def get_mode(self, user_id: int) -> SessionMode:
        """Dapatkan mode sesi user"""
        session = self.get_session(user_id)
        if session:
            return session.mode
        return SessionMode.CHAT
    
    def is_role_active(self, user_id: int, role_id: str) -> bool:
        """Cek apakah role tertentu sedang aktif"""
        session = self.get_session(user_id)
        if session:
            return session.active_role == role_id
        return role_id == "nova"
    
    def is_nova_active(self, user_id: int) -> bool:
        """Cek apakah Nova sedang aktif"""
        return self.is_role_active(user_id, "nova")
    
    def should_use_role(self, user_id: int) -> bool:
        """Cek apakah user sedang dalam mode role (bukan Nova)"""
        session = self.get_session(user_id)
        if session:
            return session.active_role != "nova"
        return False
    
    # =========================================================================
    # SETTERS - INI YANG PALING PENTING
    # =========================================================================
    
    def set_active_role(self, user_id: int, role_id: str, mode: SessionMode = None) -> None:
        """
        SET ACTIVE ROLE - INI YANG AKAN DIPANGGIL SAAT /role
        Setelah ini, semua pesan akan diarahkan ke role_id, BUKAN Nova.
        """
        session = self.get_session(user_id, auto_create=True)
        if not session:
            session = UserSession(user_id=user_id)
            self._sessions[user_id] = session
        
        session.active_role = role_id
        
        if mode:
            session.mode = mode
        elif role_id == "nova":
            session.mode = SessionMode.CHAT
        else:
            session.mode = SessionMode.ROLE
        
        session.last_interaction = time.time()
        
        logger.info(f"🎭 [SESSION] ACTIVE ROLE SET: user={user_id} -> {role_id} (mode={session.mode.value})")
    
    def set_mode(self, user_id: int, mode: SessionMode) -> None:
        """Set mode sesi"""
        session = self.get_session(user_id, auto_create=True)
        if session:
            session.mode = mode
            logger.info(f"🎭 [SESSION] Mode set: user={user_id} -> {mode.value}")
    
    def switch_to_nova(self, user_id: int) -> None:
        """
        Kembali ke Nova - DIPANGGIL SAAT /nova ATAU /batal
        """
        self.set_active_role(user_id, "nova", SessionMode.CHAT)
        logger.info(f"💜 [SESSION] Switched to Nova for user {user_id}")
    
    def switch_to_roleplay(self, user_id: int) -> None:
        """
        Switch ke mode roleplay dengan Nova
        """
        self.set_active_role(user_id, "nova", SessionMode.ROLEPLAY)
        logger.info(f"🎭 [SESSION] Switched to roleplay mode for user {user_id}")
    
    def switch_to_role(self, user_id: int, role_id: str) -> None:
        """
        Switch ke role tertentu - DIPANGGIL SAAT /role <id>
        """
        if role_id == "nova":
            self.switch_to_nova(user_id)
        else:
            self.set_active_role(user_id, role_id, SessionMode.ROLE)
            logger.info(f"🔄 [SESSION] Switched to role {role_id} for user {user_id}")
    
    # =========================================================================
    # CLEAR / RESET
    # =========================================================================
    
    def clear_session(self, user_id: int) -> None:
        """Clear session user (kembali ke default)"""
        if user_id in self._sessions:
            del self._sessions[user_id]
            logger.info(f"🗑️ [SESSION] Session cleared for user {user_id}")
    
    def reset_session(self, user_id: int) -> None:
        """Reset session ke default (Nova, chat mode)"""
        self.set_active_role(user_id, "nova", SessionMode.CHAT)
        logger.info(f"🔄 [SESSION] Session reset for user {user_id}")
    
    def update_activity(self, user_id: int) -> None:
        """Update last interaction timestamp"""
        session = self.get_session(user_id, auto_create=True)
        if session:
            session.last_interaction = time.time()
            session.conversation_count += 1
    
    # =========================================================================
    # ROUTING - INI YANG AKAN DIPAKAI ORCHESTRATOR
    # =========================================================================
    
    def get_target_role(self, user_id: int, message: str = "") -> Optional[str]:
        """
        Tentukan role target untuk pesan.
        PRIORITAS UTAMA: active session yang sudah diset.
        
        RETURNS: role_id yang harus menjawab, atau None jika tidak ada override
        """
        # Jika session manager disabled, return None (fallback ke old system)
        if not self._enabled:
            return None
        
        session = self.get_session(user_id)
        if not session:
            return None
        
        # PRIORITAS TERTINGGI: active role dari session
        if session.active_role != "nova":
            logger.debug(f"🎯 [SESSION] Routing to active role: {session.active_role} (user={user_id})")
            return session.active_role
        
        # Kalau active role = Nova, cek apakah ada command /role di pesan
        msg_lower = message.lower()
        if msg_lower.startswith('/role '):
            parts = message.split()
            if len(parts) > 1:
                requested_role = parts[1].lower()
                if requested_role != "nova":
                    return requested_role
        
        # Default: biarkan old system yang menentukan
        return None
    
    def should_override_routing(self, user_id: int) -> bool:
        """
        Cek apakah session manager harus meng-override routing.
        Returns True jika ada active role selain Nova.
        """
        session = self.get_session(user_id)
        if session and self._enabled:
            return session.active_role != "nova"
        return False
    
    # =========================================================================
    # SYNC DENGAN OLD SYSTEM (OPSIONAL)
    # =========================================================================
    
    def sync_from_old_system(self, user_id: int, mode: str, active_role: str = None) -> None:
        """
        Sinkronkan dari old system (user_mode, active_role)
        DIPANGGIL OPSIONAL untuk menjaga konsistensi
        """
        if not self._enabled:
            return
        
        session = self.get_session(user_id, auto_create=True)
        if not session:
            return
        
        # Sync mode
        if mode == "chat":
            session.mode = SessionMode.CHAT
            session.active_role = "nova"
        elif mode == "roleplay":
            session.mode = SessionMode.ROLEPLAY
            session.active_role = "nova"
        elif mode == "role" and active_role:
            session.mode = SessionMode.ROLE
            session.active_role = active_role
        elif mode == "paused":
            # Paused mode tidak mengubah active role
            pass
        
        logger.debug(f"🔄 [SESSION] Synced from old system: user={user_id}, mode={mode}, role={active_role}")
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik session"""
        active_roles = {}
        for session in self._sessions.values():
            role = session.active_role
            active_roles[role] = active_roles.get(role, 0) + 1
        
        return {
            'enabled': self._enabled,
            'total_sessions': len(self._sessions),
            'active_roles': active_roles,
            'sessions': {uid: s.to_dict() for uid, s in self._sessions.items()}
        }
    
    def format_stats(self) -> str:
        """Format statistik untuk display"""
        stats = self.get_stats()
        
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║                    🎭 ROLE SESSION MANAGER                   ║",
            "╠══════════════════════════════════════════════════════════════╣",
            f"║ ENABLED: {'✅' if stats['enabled'] else '❌'}                                           ║",
            f"║ TOTAL SESSIONS: {stats['total_sessions']}                                          ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║ ACTIVE ROLES:                                              ║"
        ]
        
        for role, count in stats['active_roles'].items():
            lines.append(f"║   {role}: {count} session(s)                                      ║")
        
        lines.append("╚══════════════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def get_active_sessions_summary(self) -> str:
        """Dapatkan ringkasan session aktif untuk debugging"""
        if not self._sessions:
            return "No active sessions"
        
        lines = ["Active Sessions:"]
        for user_id, session in self._sessions.items():
            lines.append(f"  User {user_id}: {session.active_role} ({session.mode.value}) - {session.conversation_count} msgs")
        return "\n".join(lines)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_session_manager: Optional[RoleSessionManager] = None


def get_session_manager() -> RoleSessionManager:
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = RoleSessionManager()
    return _session_manager


def reset_session_manager() -> None:
    """Reset session manager (for testing)"""
    global _session_manager
    _session_manager = None
    logger.info("🔄 RoleSessionManager reset")


# =============================================================================
# HELPER FUNCTIONS (UNTUK INTEGRASI MUDAH)
# =============================================================================

def get_target_role_for_user(user_id: int, message: str = "") -> Optional[str]:
    """
    Helper function untuk mendapatkan target role dari session manager.
    Returns None jika session manager tidak memiliki override.
    """
    sm = get_session_manager()
    if sm.is_enabled():
        return sm.get_target_role(user_id, message)
    return None


def is_role_override_active(user_id: int) -> bool:
    """
    Helper function untuk cek apakah ada override role.
    """
    sm = get_session_manager()
    return sm.is_enabled() and sm.should_override_routing(user_id)


def update_session_activity(user_id: int) -> None:
    """
    Helper function untuk update activity.
    """
    sm = get_session_manager()
    sm.update_activity(user_id)


def sync_session_from_old(user_id: int, mode: str, active_role: str = None) -> None:
    """
    Helper function untuk sinkron dari old system.
    """
    sm = get_session_manager()
    sm.sync_from_old_system(user_id, mode, active_role)


__all__ = [
    'SessionMode',
    'UserSession',
    'RoleSessionManager',
    'get_session_manager',
    'reset_session_manager',
    'get_target_role_for_user',
    'is_role_override_active',
    'update_session_activity',
    'sync_session_from_old'
]
