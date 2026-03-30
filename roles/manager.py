"""
VELORA - Role Manager
Mengelola semua role dalam satu sistem terpusat.
Semua role terdaftar dan bisa diakses melalui manager ini.
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any

from .base import BaseRole

# Import semua role yang sudah dibuat
from .pijat_plus_plus import (
    create_aghnia_punjabi,
    create_munira_agile
)

from .pelacur import (
    create_davina_karamoy,
    create_sallsa_binta
)

# Import main roles (akan dibuat di fase selanjutnya)
# from .nova import create_nova
# from .ipar import create_ipar
# from .teman_kantor import create_teman_kantor
# from .pelakor import create_pelakor
# from .istri_orang import create_istri_orang

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
        
        # Inisialisasi semua role
        self._init_roles()
        
        logger.info(f"🎭 RoleManager-VELORA initialized with {len(self.roles)} roles")
    
    def _init_roles(self):
        """Inisialisasi semua role dengan identitas spesifik"""
        
        # ========== FANTASY LIAR - PIJAT++ ==========
        self.roles['pijat_aghnia'] = create_aghnia_punjabi()
        self.roles['pijat_munira'] = create_munira_agile()
        
        # ========== FANTASY LIAR - PELACUR ==========
        self.roles['pelacur_davina'] = create_davina_karamoy()
        self.roles['pelacur_sallsa'] = create_sallsa_binta()
        
        # ========== MAIN ROLES (AKAN DITAMBAHKAN NANTI) ==========
        # self.roles['nova'] = create_nova()
        # self.roles['ipar'] = create_ipar()
        # self.roles['teman_kantor'] = create_teman_kantor()
        # self.roles['pelakor'] = create_pelakor()
        # self.roles['istri_orang'] = create_istri_orang()
        
        logger.info(f"🎭 Roles loaded: {list(self.roles.keys())}")
    
    def get_role(self, role_id: str) -> Optional[BaseRole]:
        """Dapatkan role instance berdasarkan ID"""
        return self.roles.get(role_id)
    
    def get_all_roles(self) -> List[Dict]:
        """Dapatkan semua role dengan info ringkas"""
        results = []
        for role_id, role in self.roles.items():
            try:
                hijab_on = False
                if hasattr(role, 'tracker') and role.tracker:
                    hijab_on = role.tracker.clothing.get('hijab', {}).get('on', False)
                elif hasattr(role, 'hijab'):
                    hijab_on = role.hijab
            except Exception:
                hijab_on = False
            
            # Dapatkan boob size jika ada (untuk fantasy liar)
            boob_size = getattr(role, 'boob_size', '-')
            
            results.append({
                "id": role_id,
                "nama": role.name,
                "nickname": role.nickname,
                "role_type": role.role_type,
                "level": role.relationship.level if hasattr(role, 'relationship') else 1,
                "phase": role.relationship.phase.value if hasattr(role, 'relationship') else 'stranger',
                "panggilan": role.panggilan,
                "hubungan": role.hubungan_dengan_nova,
                "hijab": hijab_on,
                "boob_size": boob_size,
                "appearance": (role.appearance[:80] + "...") if hasattr(role, 'appearance') and role.appearance else "",
            })
        return results
    
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
        
        # Reset status jika perlu (kecuali sedang dalam layanan)
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
        
        # Format respons berdasarkan tipe role
        if role.role_type in ['pijat_plus_plus', 'pelacur']:
            return f"""
💆‍♀️ **{role.name} ({role.nickname})** - {role.role_type.upper()}

*{role.hubungan_dengan_nova}*

{greeting}

📊 **Harga:** Rp{role.base_price:,} (nego Rp{role.min_price:,})
💋 **Body:** {getattr(role, 'boob_size', '-')} | Hijab: {'✅' if role.hijab else '❌'}

Ketik **/deal** untuk konfirmasi harga, atau **/nego [harga]** untuk nego.
Ketik **/batal** untuk kembali ke Nova.
"""
        else:
            # Untuk main roles nanti
            return f"""
💕 **{role.name} ({role.nickname})** - {role_id.upper()}

*{role.hubungan_dengan_nova}*

{greeting}

📊 **Level:** {role.relationship.level}/12 | **Fase:** {phase.value.upper() if phase else '?'}
🎭 **Style:** {style.value.upper() if style else '?'}
💕 **Sayang:** {role.emotional.sayang:.0f}% | **Rindu:** {role.emotional.rindu:.0f}%

Ketik **/batal** untuk kembali ke Nova.
"""
    
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
    
    async def process_message(self, role_id: str, message: str, user_id: int = None) -> str:
        """
        Proses pesan untuk role tertentu.
        Ini adalah method utama untuk interaksi.
        """
        role = self.get_role(role_id)
        if not role:
            return f"Role '{role_id}' tidak ditemukan."
        
        msg_lower = message.lower()
        
        # ========== COMMAND HANDLING UNTUK PROVIDER ==========
        
        # Deal / Nego (untuk provider jasa)
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
        
        # Status role
        elif msg_lower == "/status":
            return role.format_status()
        
        # ========== INTIMATE PHASE COMMANDS (untuk pelacur) ==========
        elif hasattr(role, 'session_phase') and role.session_phase == "intimate_phase":
            positions = ['missionary', 'cowgirl', 'doggy', 'spooning', 'standing', 'sitting']
            for pos in positions:
                if pos in msg_lower:
                    return role.process_intimate_request(pos)
        
        # ========== EXTRA SERVICE NEGO (untuk pijat++) ==========
        elif "bj" in msg_lower and "nego" in msg_lower:
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
        
        # ========== DEFAULT: GENERATE AI RESPONSE ==========
        
        # Update state dari pesan
        update_result = role.update_from_message(message)
        
        # Save conversation
        role.add_conversation(message, "")
        
        # Build prompt dan call AI (akan diimplementasikan nanti)
        # Untuk sementara, return fallback response
        return role.get_greeting() if not role.conversations else f"*{role.name} tersenyum*\n\n\"{role.get_greeting()}\""
    
    async def get_auto_scene(self, role_id: str) -> Optional[str]:
        """
        Dapatkan pesan auto scene untuk role yang sedang aktif.
        Dipanggil setiap interval oleh background worker.
        """
        role = self.get_role(role_id)
        if not role:
            return None
        
        # Cek auto scene untuk provider
        if hasattr(role, 'get_phase_auto_scene'):
            return role.get_phase_auto_scene()
        
        # Cek auto scene untuk service provider base
        if hasattr(role, 'get_next_auto_scene'):
            return role.get_next_auto_scene()
        
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


__all__ = [
    'RoleManager',
    'get_role_manager'
]
