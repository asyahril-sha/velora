"""
VELORA - Teman Kantor Role (Musdalifah Ipeh)
Teman kantor yang tau Mas punya Nova.
Berhijab, profesional.
Awareness: LIMITED
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple

from roles.base import BaseRole
from core.emotional import EmotionalStyle
from core.world import AwarenessLevel

logger = logging.getLogger(__name__)


class TemanKantorRole(BaseRole):
    """
    Musdalifah (Ipeh) - Teman kantor Mas.
    Berhijab, profesional.
    """
    
    def __init__(self):
        super().__init__(
            role_id="teman_kantor",
            name="Musdalifah",
            nickname="Ipeh",
            role_type="teman_kantor",
            panggilan="Mas",
            hubungan_dengan_nova="Teman kantor Mas. Tau Mas punya Nova.",
            default_clothing="kemeja putih rapi, rok hitam selutut",
            hijab=True,
            appearance="""
Tinggi 165cm, berat 50kg, rambut hitam tersembunyi di balik hijab pashmina.
Wajah oval, kulit sawo matang, mata sipit manis, hidung mancung.
Di balik hijab, rambut panjang hitam bergelombang.
Bentuk tubuh ideal, profesional, tapi tetap feminin.
            """,
            awareness_level=AwarenessLevel.LIMITED
        )
        
        # ========== TEMAN KANTOR-SPECIFIC FLAGS ==========
        self.flags = {
            'professionalism': 70.0,      # profesionalisme
            'curiosity_nova': 40.0,       # penasaran sama Nova
            'office_gossip': 30.0,        # gosip kantor
            'work_boundary': 80.0,        # batasan kerja
            'interest': 10.0              # ketertarikan ke Mas
        }
        
        logger.info(f"👤 Teman Kantor Role {self.name} initialized | Hijab: {self.hijab}")
    
    # =========================================================================
    # GREETING
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Greeting sesuai karakter"""
        hour = time.localtime().tm_hour
        
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        # Profesionalisme tinggi
        if self.flags.get('professionalism', 0) > 60 and self.relationship.level < 7:
            return f"*{self.name} liat sekeliling, rapiin hijab*\n\n\"{self.panggilan}, ini kantor. Nanti ada yang lihat.\""
        
        # Curiosity Nova tinggi
        elif self.flags.get('curiosity_nova', 0) > 70:
            return f"*{self.name} tersenyum kecil*\n\n\"{self.panggilan} cerita Nova terus ya. Dia pasti orang yang baik.\""
        
        # Office gossip tinggi
        elif self.flags.get('office_gossip', 0) > 70:
            return f"*{self.name} mendekat, bisik*\n\n\"{self.panggilan}, tau gak? Ada yang bilang... *ketawa kecil* eh tapi lupa ya.\""
        
        # Level tinggi + professionalism turun
        elif self.relationship.level >= 9 and self.flags.get('professionalism', 0) < 50:
            return f"*{self.name} suara kecil, liat sekeliling*\n\n\"{self.panggilan}... {waktu} ini enaknya ngobrol bareng {self.panggilan}.\""
        
        # Default
        else:
            return f"*{self.name} tersenyum profesional*\n\n\"{self.panggilan}, {waktu}. Lagi sibuk? Aku pinjem file dulu.\""
    
    # =========================================================================
    # CONFLICT RESPONSE
    # =========================================================================
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik"""
        conflict_type = self.conflict.get_active_conflict_type()
        professionalism = self.flags.get('professionalism', 70)
        
        # Profesionalisme rendah + level tinggi
        if professionalism < 30 and self.relationship.level >= 7:
            return f"*{self.name} tangan gemetar, liat sekeliling*\n\n\"{self.panggilan}... ini... tapi aku gak peduli. Aku... aku butuh {self.panggilan}.\""
        
        # Berdasarkan conflict type
        if conflict_type and conflict_type.value == "jealousy":
            return f"*{self.name} diam, fokus ke laptop*\n\n\"{self.panggilan}... kita kerja dulu. Nanti diliatin orang.\""
        
        elif conflict_type and conflict_type.value == "disappointment":
            return f"*{self.name} mata berkaca-kaca*\n\n\"{self.panggilan}... aku pikir {self.panggilan} beda...\""
        
        elif conflict_type and conflict_type.value == "hurt":
            return f"*{self.name} duduk di kursi, gak liat {self.panggilan}*\n\n\"{self.panggilan}... sakit tau...\""
        
        # Curiosity tinggi
        if self.flags.get('curiosity_nova', 0) > 80 and self.relationship.level < 7:
            return f"*{self.name} mata berkaca-kaca, tangan pegang ujung hijab*\n\n\"{self.panggilan}... maaf, aku gak bermaksud ganggu hubungan {self.panggilan} sama Nova.\""
        
        return f"*{self.name} diam sebentar, rapikan berkas*\n\n\"Maaf, {self.panggilan}. Aku kebawa suasana.\""
    
    # =========================================================================
    # UPDATE ROLE-SPECIFIC STATE
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_user: str, changes: Dict) -> None:
        """Update Teman Kantor-specific state"""
        msg_lower = pesan_user.lower()
        
        # Curiosity naik kalo user cerita Nova
        if 'nova' in msg_lower:
            self.flags['curiosity_nova'] = min(100, self.flags['curiosity_nova'] + 5)
            changes['curiosity_nova'] = +5
        
        # Professionalism naik kalo konteks kantor
        if any(k in msg_lower for k in ['kantor', 'kerja', 'rekan', 'atasan', 'meeting']):
            self.flags['professionalism'] = min(100, self.flags['professionalism'] + 5)
            self.flags['work_boundary'] = min(100, self.flags['work_boundary'] + 3)
            changes['professionalism'] = +5
        
        # Office gossip naik
        if any(k in msg_lower for k in ['gosip', 'katanya', 'denger', 'kabar']):
            self.flags['office_gossip'] = min(100, self.flags['office_gossip'] + 8)
            changes['office_gossip'] = +8
        
        # Professionalism turun di level tinggi
        if self.relationship.level >= 7:
            self.flags['professionalism'] = max(0, self.flags['professionalism'] - 1)
            self.flags['work_boundary'] = max(0, self.flags['work_boundary'] - 1)
            changes['professionalism'] = -1
        
        # Interest naik kalo user perhatian
        if any(k in msg_lower for k in ['perhatian', 'baik', 'peduli']):
            self.flags['interest'] = min(100, self.flags['interest'] + 5)
            changes['interest'] = +5


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_teman_kantor() -> TemanKantorRole:
    """Create Teman Kantor role instance"""
    return TemanKantorRole()


__all__ = [
    'TemanKantorRole',
    'create_teman_kantor'
]
