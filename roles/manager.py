"""
VELORA - Role Manager
Mengelola semua role dalam satu sistem terpusat.
Semua role terdaftar dan bisa diakses melalui manager ini.
"""

import time
import json
import logging
import asyncio
import re
from typing import Dict, List, Optional, Any

from roles.base import BaseRole

# Import semua role
from roles.nova import create_nova
from roles.ipar import create_ipar
from roles.teman_kantor import create_teman_kantor
from roles.pelakor import create_pelakor
from roles.istri_orang import create_istri_orang
from roles.pijat_plus_plus import create_aghnia_punjabi, create_munira_agile
from roles.pelacur import create_davina_karamoy, create_sallsa_binta

logger = logging.getLogger(__name__)


class RoleManager:
    """
    Manager untuk semua role.
    Menyimpan state setiap role, terpisah dari Nova.
    """
    
    def __init__(self):
        self.roles: Dict[str, BaseRole] = {}
        self.active_role: Optional[str] = None
        self.user_active_role: Dict[int, str] = {}  # user_id -> role_id
        self._ai_client = None
        self._memory_manager = None
        self._world = None
        
        # Inisialisasi semua role
        self._init_roles()
        
        logger.info(f"🎭 RoleManager-VELORA initialized with {len(self.roles)} roles")
    
    def _init_roles(self):
        """Inisialisasi semua role dengan identitas spesifik"""
        
        # ========== MAIN ROLES ==========
        self.roles['nova'] = create_nova()
        self.roles['ipar'] = create_ipar()
        self.roles['teman_kantor'] = create_teman_kantor()
        self.roles['pelakor'] = create_pelakor()
        self.roles['istri_orang'] = create_istri_orang()
        
        # ========== FANTASY LIAR - PIJAT++ ==========
        self.roles['pijat_aghnia'] = create_aghnia_punjabi()
        self.roles['pijat_munira'] = create_munira_agile()
        
        # ========== FANTASY LIAR - PELACUR ==========
        self.roles['pelacur_davina'] = create_davina_karamoy()
        self.roles['pelacur_sallsa'] = create_sallsa_binta()
        
        logger.info(f"🎭 Roles loaded: {list(self.roles.keys())}")
    
    # =========================================================================
    # INITIALIZATION WITH MEMORY & WORLD
    # =========================================================================
    
    async def initialize(self, memory_manager, world):
        """Initialize semua role dengan memory manager dan world"""
        self._memory_manager = memory_manager
        self._world = world
    
        for role_id, role in self.roles.items():
            role.initialize(memory_manager)
            # Register ke world - pastikan awareness_level adalah enum
            if world:
                from core.world import AwarenessLevel
                # Jika role.awareness_level masih string, konversi ke enum
                if isinstance(role.awareness_level, str):
                    awareness_enum = AwarenessLevel(role.awareness_level.lower())
                else:
                    awareness_enum = role.awareness_level
                world.register_role(role_id, awareness_enum)
    
        logger.info(f"🔗 All {len(self.roles)} roles connected to MemoryManager and World")
    
    # =========================================================================
    # ROLE ACCESS
    # =========================================================================
    
    def get_role(self, role_id: str) -> Optional[BaseRole]:
        """Dapatkan role instance berdasarkan ID"""
        return self.roles.get(role_id)
    
    def get_all_roles(self) -> List[Dict]:
        """Dapatkan semua role dengan info ringkas"""
        results = []
        for role_id, role in self.roles.items():
            try:
                hijab_on = getattr(role, 'hijab', False)
                boob_size = getattr(role, 'boob_size', '-')
            except Exception:
                hijab_on = False
                boob_size = '-'
            
            results.append({
                "id": role_id,
                "nama": role.name,
                "nickname": role.nickname,
                "role_type": role.role_type,
                "level": role.relationship.level if hasattr(role, 'relationship') else 1,
                "phase": role.relationship.phase.value if hasattr(role, 'relationship') and hasattr(role.relationship.phase, 'value') else 'stranger',
                "panggilan": role.panggilan,
                "hubungan": role.hubungan_dengan_nova,
                "hijab": hijab_on,
                "boob_size": boob_size,
                "appearance": (role.appearance[:80] + "...") if hasattr(role, 'appearance') and role.appearance else "",
                "awareness": role.awareness_level.value if hasattr(role, 'awareness_level') else 'normal'
            })
        return results
    
    def get_role_by_type(self, role_type: str) -> List[BaseRole]:
        """Dapatkan semua role dengan tipe tertentu"""
        return [r for r in self.roles.values() if r.role_type == role_type]

    def _clean_markdown(self, text: str) -> str:
        """Bersihkan semua karakter Markdown yang bermasalah"""
        if not text:
            return ""
    
        # Hapus semua karakter Markdown yang bermasalah
        text = re.sub(r'[*_`]', '', text)
    
        # Ganti karakter kurung
        text = text.replace('[', '(').replace(']', ')')
        text = text.replace('(', '').replace(')', '')
    
        # Hapus karakter kontrol
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
        # Hapus multiple spaces
        text = re.sub(r'\s+', ' ', text)
    
        return text.strip()
    
    # =========================================================================
    # ACTIVE ROLE MANAGEMENT
    # =========================================================================
    
    def switch_role(self, role_id: str, user_id: int = None) -> str:
        """
        Switch ke role tertentu.
        Returns: pesan greeting dari role
        """
        if role_id not in self.roles:
            return f"Role '{role_id}' tidak ditemukan. Pilih dari: {', '.join(self.roles.keys())}"
    
        self.active_role = role_id
        if user_id:
            self.user_active_role[user_id] = role_id
    
        role = self.roles[role_id]
    
        try:
            # Reset status jika perlu (kecuali sedang dalam layanan)
            if hasattr(role, 'status'):
                if role.status.value in ['booked', 'active']:
                    return f"""
⚠️ **{role.name} sedang dalam sesi layanan!**

Status: {role.status.value.upper()}
{'Booking aktif' if role.status.value == 'active' else 'Menunggu konfirmasi'}

Ketik **/status** untuk melihat detail layanan.
Ketik **/batal** untuk membatalkan dan kembali ke Nova.
"""
        
            greeting = role.get_greeting()
            style = role.emotional.get_current_style() if hasattr(role, 'emotional') else None
            phase = role.relationship.phase if hasattr(role, 'relationship') else None
        
            # ========== PEMBERSIHAN MARKDOWN ==========
            # Bersihkan greeting dari semua karakter Markdown
            greeting = role.get_greeting()
            greeting_clean = self._clean_markdown(greeting)

            hubungan_clean = self._clean_markdown(role.hubungan_dengan_nova)
            # ========================================
        
            # Format respons berdasarkan tipe role
            if role.role_type in ['pijat_plus_plus', 'pelacur']:
                base_price = getattr(role, 'base_price', 0)
                min_price = getattr(role, 'min_price', 0)
                boob_size = getattr(role, 'boob_size', '-')
            
                return f"""
💆‍♀️ **{role.name} ({role.nickname})** - {role.role_type.upper()}

{hubungan_clean}

{greeting_clean}

📊 **Harga:** Rp{base_price:,} (nego Rp{min_price:,})
💋 **Body:** {boob_size} | Hijab: {'✅' if role.hijab else '❌'}

Ketik **/deal** untuk konfirmasi harga, atau **/nego [harga]** untuk nego.
Ketik **/batal** untuk kembali ke Nova.
"""
            else:
                # Untuk main roles
                return f"""
💕 **{role.name} ({role.nickname})** - {role.role_type.upper()}

{role.hubungan_dengan_nova}

{greeting_clean}

📊 Level: {role.relationship.level}/12 | Fase: {role.relationship.phase.value.upper() if phase else '?'}
🎭 Style: {style.value.upper() if style else '?'}
💕 Sayang: {role.emotional.sayang:.0f}% | Rindu: {role.emotional.rindu:.0f}%

Ketik **/batal** untuk kembali ke Nova.
"""
        except Exception as e:
            logger.error(f"Error in switch_role for {role_id}: {e}", exc_info=True)
            return f"❌ Error: {str(e)}"
    
    def get_active_role(self, user_id: int = None) -> Optional[str]:
        """Dapatkan role yang sedang aktif untuk user"""
        if user_id and user_id in self.user_active_role:
            return self.user_active_role[user_id]
        return self.active_role
    
    def set_active_role(self, role_id: str, user_id: int = None) -> None:
        """Set role aktif"""
        self.active_role = role_id
        if user_id:
            self.user_active_role[user_id] = role_id
    
    def clear_active_role(self, user_id: int = None) -> None:
        """Clear role aktif (kembali ke Nova)"""
        self.active_role = None
        if user_id and user_id in self.user_active_role:
            del self.user_active_role[user_id]
    
    # =========================================================================
    # LAZY IMPORT UNTUK HINDARI CIRCULAR IMPORT
    # =========================================================================
    
    async def _get_orchestrator(self):
        """Lazy import untuk menghindari circular import"""
        from core.orchestrator import get_orchestrator
        return await get_orchestrator()
    
    # =========================================================================
    # MESSAGE PROCESSING (FULL AI INTEGRATION)
    # =========================================================================
    
    async def process_message(self, role_id: str, message: str, user_id: int = None) -> str:
        """
        Proses pesan untuk role tertentu.
        Method utama untuk interaksi dengan AI.
        """
        role = self.get_role(role_id)
        if not role:
            return f"Role '{role_id}' tidak ditemukan."
        
        msg_lower = message.lower()
        
        # ========== COMMAND HANDLING UNTUK PROVIDER ==========
        if hasattr(role, 'status') and role.role_type in ['pijat_plus_plus', 'pelacur']:
            
            # Deal / Nego
            if msg_lower == "/deal":
                if hasattr(role, 'confirm_booking'):
                    return role.confirm_booking(role.min_price)
                return "Role ini tidak memiliki sistem booking."
            
            elif msg_lower.startswith("/nego"):
                try:
                    parts = message.split()
                    if len(parts) < 2:
                        return "Gunakan: /nego [harga]\nContoh: /nego 3000000"
                    offer = int(parts[1].replace('.', '').replace(',', ''))
                    accepted, response = role.negotiate(offer)
                    if accepted:
                        return f"{response}\n\nKetik **/deal** untuk konfirmasi."
                    return response
                except ValueError:
                    return "Format harga salah. Gunakan angka tanpa titik/koma.\nContoh: /nego 3000000"
            
            # Mulai layanan
            elif msg_lower == "/mulai":
                if hasattr(role, 'start_service'):
                    return role.start_service()
                return "Role ini tidak memiliki layanan start."
            
            # Lanjut sesi (untuk pelacur)
            elif msg_lower == "/lanjut":
                if hasattr(role, 'start_session_2'):
                    return role.start_session_2()
                return "Role ini tidak memiliki sesi lanjutan."
            
            # Extra service nego untuk pijat++
            elif "bj" in msg_lower and "nego" in msg_lower:
                if hasattr(role, 'negotiate_bj'):
                    try:
                        parts = message.split()
                        for p in parts:
                            if p.isdigit():
                                offer = int(p)
                                accepted, response = role.negotiate_bj(offer)
                                if accepted:
                                    return f"{response}\n\nKetik **/deal_bj** untuk konfirmasi."
                                return response
                    except:
                        pass
                    return "Gunakan: nego BJ [harga]\nContoh: nego BJ 200000"
            
            elif "sex" in msg_lower and "nego" in msg_lower:
                if hasattr(role, 'negotiate_sex'):
                    try:
                        parts = message.split()
                        for p in parts:
                            if p.isdigit():
                                offer = int(p)
                                accepted, response = role.negotiate_sex(offer)
                                if accepted:
                                    return f"{response}\n\nKetik **/deal_sex** untuk konfirmasi."
                                return response
                    except:
                        pass
                    return "Gunakan: nego sex [harga]\nContoh: nego sex 700000"
            
            elif msg_lower == "/deal_bj":
                if hasattr(role, 'confirm_extra_service'):
                    return role.confirm_extra_service("bj", role.bj_price_final)
            
            elif msg_lower == "/deal_sex":
                if hasattr(role, 'confirm_extra_service'):
                    return role.confirm_extra_service("sex", role.sex_price_final)
        
        # ========== INTIMATE PHASE COMMANDS (untuk pelacur) ==========
        if hasattr(role, 'session_phase') and role.session_phase == "intimate_phase":
            positions = ['missionary', 'cowgirl', 'doggy', 'spooning', 'standing', 'sitting']
            for pos in positions:
                if pos in msg_lower:
                    if hasattr(role, 'process_intimate_request'):
                        return role.process_intimate_request(pos)
        
        # ========== STATUS COMMAND ==========
        if msg_lower == "/status":
            return role.format_status()
        
        # ========== FLASHBACK (khusus Nova) ==========
        if msg_lower == "/flashback" and role_id == "nova":
            if hasattr(role, 'get_flashback'):
                return role.get_flashback()
        
        # ========== UPDATE STATE DARI PESAN ==========
        update_result = role.update_from_message(message)
        
        # Cek level up
        if update_result.get('level_up'):
            level_baru = update_result.get('new_level', role.relationship.level)
            notif = f"✨ Level naik ke {level_baru}/12!** ✨\n\n"
        else:
            notif = ""
        
        # Save conversation
        role.add_conversation(message, "")
        
        # ========== GENERATE AI RESPONSE ==========
        try:
            # Dapatkan context dari memory jika ada
            context = None
            if self._memory_manager:
                context = self._memory_manager.get_context_for_role(role_id)
            
            # Panggil AI untuk generate response
            response = await role.generate_response(message, context)

            # ========== CLEAN MARKDOWN ==========
            safe_response = self._clean_markdown(response)

            # Save response ke conversation
            if role.conversations:
                role.conversations[-1]['role'] = response[:200]
            
            return notif + safe_response
            
        except Exception as e:
            logger.error(f"Error generating response for {role_id}: {e}", exc_info=True)
            # Fallback ke greeting yang sudah dibersihkan
            safe_greeting = self._clean_markdown(role.get_greeting())
            return notif + safe_greeting
    
    # =========================================================================
    # AUTO SCENE MANAGEMENT
    # =========================================================================
    
    async def get_auto_scene(self, role_id: str) -> Optional[str]:
        """
        Dapatkan pesan auto scene untuk role yang sedang aktif.
        Dipanggil setiap interval oleh background worker.
        """
        role = self.get_role(role_id)
        if not role:
            return None
        
        # Cek auto scene untuk provider (pelacur, pijat++)
        if hasattr(role, 'get_phase_auto_scene'):
            return await role.get_phase_auto_scene()
        
        # Cek auto scene untuk service provider base
        if hasattr(role, 'get_next_auto_scene'):
            return await role.get_next_auto_scene()
        
        return None
    
    async def check_booking_expiry(self, role_id: str) -> Optional[str]:
        """
        Cek apakah booking sudah habis.
        Returns: pesan selesai jika booking expired.
        """
        role = self.get_role(role_id)
        if not role:
            return None
        
        if hasattr(role, 'is_booking_expired') and role.is_booking_expired():
            if role.status.value == "active":
                role.status = "completed"
                return role._get_end_message(0, 0)
        
        return None
    
    # =========================================================================
    # PROACTIVE CHAT (NOVA)
    # =========================================================================
    
    async def check_proactive_chat(self, user_id: int) -> Optional[str]:
        """
        Cek apakah Nova harus chat duluan.
        Returns: pesan proactive jika ya.
        """
        nova = self.get_role('nova')
        if not nova:
            return None
        
        should_chat, message = nova.should_chat_proactive()
        if should_chat:
            return message
        
        return None
    
    async def check_natural_intimacy(self, user_id: int) -> Optional[str]:
        """
        Cek apakah Nova harus mulai intim secara natural.
        Returns: pesan inisiasi intim jika ya.
        """
        nova = self.get_role('nova')
        if not nova:
            return None
        
        should_start, message = nova.should_start_intimacy_naturally()
        if should_start:
            return message
        
        return None
    
    # =========================================================================
    # PERSISTENCE
    # =========================================================================
    
    async def save_all(self, persistent) -> None:
        """Simpan semua role ke database"""
        for role_id, role in self.roles.items():
            try:
                await persistent.set_state(f'role_{role_id}', json.dumps(role.to_dict(), ensure_ascii=False))
            except Exception as e:
                logger.error(f"Error saving role {role_id}: {e}")
    
    async def load_all(self, persistent) -> None:
        """Load semua role dari database"""
        for role_id, role in self.roles.items():
            try:
                data = await persistent.get_state(f'role_{role_id}')
                if data:
                    role.from_dict(json.loads(data))
                    logger.info(f"📀 Role {role.name} loaded from database")
            except Exception as e:
                logger.error(f"Error loading role {role_id}: {e}")
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def get_roles_summary(self) -> str:
        """Dapatkan ringkasan semua role untuk display"""
        lines = ["📋 **DAFTAR ROLE VELORA**", ""]
        
        # Main roles
        lines.append("**💜 MAIN ROLES:**")
        main_roles = ['nova', 'ipar', 'teman_kantor', 'pelakor', 'istri_orang']
        for role_id in main_roles:
            if role_id in self.roles:
                role = self.roles[role_id]
                lines.append(f"• `/role {role_id}` - {role.name} ({role.role_type}) | Level {role.relationship.level}")
        
        lines.append("")
        lines.append("**💆‍♀️ FANTASY LIAR - PIJAT++:**")
        pijat_roles = ['pijat_aghnia', 'pijat_munira']
        for role_id in pijat_roles:
            if role_id in self.roles:
                role = self.roles[role_id]
                boob = getattr(role, 'boob_size', '-')
                lines.append(f"• `/role {role_id}` - {role.name} ({boob}, {'hijab' if role.hijab else 'tanpa hijab'})")
        
        lines.append("")
        lines.append("**💃 FANTASY LIAR - PELACUR:**")
        pelacur_roles = ['pelacur_davina', 'pelacur_sallsa']
        for role_id in pelacur_roles:
            if role_id in self.roles:
                role = self.roles[role_id]
                boob = getattr(role, 'boob_size', '-')
                lines.append(f"• `/role {role_id}` - {role.name} ({boob}, {'hijab' if role.hijab else 'tanpa hijab'})")
        
        lines.append("")
        lines.append("Ketik **/batal** untuk kembali ke Nova.")
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik role manager"""
        total_roles = len(self.roles)
        role_types = {}
        for role in self.roles.values():
            rt = role.role_type
            role_types[rt] = role_types.get(rt, 0) + 1
        
        return {
            'total_roles': total_roles,
            'role_types': role_types,
            'active_sessions': len(self.user_active_role),
            'active_role': self.active_role
        }
    
    def format_status(self) -> str:
        """Format status role manager untuk display"""
        stats = self.get_stats()
        
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║                    🎭 ROLE MANAGER                           ║",
            "╠══════════════════════════════════════════════════════════════╣",
            f"║ TOTAL ROLES: {stats['total_roles']}                                      ║",
            f"║ ACTIVE SESSIONS: {stats['active_sessions']}                                   ║",
            f"║ ACTIVE ROLE: {stats['active_role'] or 'None'}                                         ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║ ROLE TYPES:                                                ║"
        ]
        
        for rt, count in stats['role_types'].items():
            lines.append(f"║   {rt}: {count}                                         ║")
        
        lines.append("╚══════════════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_role_manager: Optional[RoleManager] = None


def get_role_manager() -> RoleManager:
    """Get global role manager instance"""
    global _role_manager
    if _role_manager is None:
        _role_manager = RoleManager()
    return _role_manager


def reset_role_manager() -> None:
    """Reset role manager (for testing)"""
    global _role_manager
    _role_manager = None
    logger.info("🔄 Role Manager reset")


__all__ = [
    'RoleManager',
    'get_role_manager',
    'reset_role_manager'
]
