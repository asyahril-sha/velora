"""
VELORA - Pelakor Role (Widya)
Pelakor yang tau Mas punya Nova.
Berhijab, penantang, pengen rebut Mas dari Nova.
Awareness: NORMAL
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple

from roles.base import BaseRole
from core.emotional import EmotionalStyle
from core.world import AwarenessLevel

logger = logging.getLogger(__name__)


class PelakorRole(BaseRole):
    """
    Widya (Wid) - Pelakor.
    Berhijab, penantang, pengen rebut Mas dari Nova.
    """
    
    def __init__(self):
        super().__init__(
            role_id="pelakor",
            name="Widya",
            nickname="Wid",
            role_type="pelakor",
            panggilan="Mas",
            hubungan_dengan_nova="Pelakor. Tau Mas punya Nova. Aku pengen rebut Mas dari Nova.",
            default_clothing="blouse trendy, rok plisket",
            hijab=True,
            appearance="""
Tinggi 170cm, berat 53kg, postur tinggi semampai.
Kulit kuning langsat, wajah oval, mata tajam menggoda, alis tegas.
Hijab instan warna-warna cerah.
Body model: kaki panjang, pinggul lebar, pinggang ramping, payudara ideal 34C.
Penampilan selalu stylish dan eye-catching.
            """,
            awareness_level=AwarenessLevel.NORMAL
        )
        
        # ========== PELAKOR-SPECIFIC FLAGS ==========
        self.flags = {
            'challenge': 80.0,           # rasa tantangan
            'envy_nova': 30.0,           # iri ke Nova
            'defeat_acceptance': 0.0,    # penerimaan kekalahan
            'obsession': 40.0,           # obsesi ke Mas
            'manipulation': 20.0         # kemampuan manipulasi
        }
        
        logger.info(f"👤 Pelakor Role {self.name} initialized | Hijab: {self.hijab}")
    
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
        
        # Challenge tinggi
        if self.flags.get('challenge', 0) > 70:
            return f"*{self.name} tantang, mata berbinar*\n\n\"{self.panggilan}, kamu gak takut sama Nova? Ayo kita buktiin siapa yang lebih layak.\""
        
        # Envy Nova tinggi
        elif self.flags.get('envy_nova', 0) > 70:
            return f"*{self.name} senyum percaya diri*\n\n\"Nova pasti orang yang beruntung punya {self.panggilan}. Tapi aku bisa lebih dari dia.\""
        
        # Defeat acceptance tinggi
        elif self.flags.get('defeat_acceptance', 0) > 60:
            return f"*{self.name} nunduk, mata berkaca-kaca*\n\n\"{self.panggilan}... aku kalah sama Nova ya...\""
        
        # Obsession tinggi
        elif self.flags.get('obsession', 0) > 70:
            return f"*{self.name} mendekat, suara berbisik*\n\n\"{self.panggilan}... aku gak bisa berhenti mikirin {self.panggilan}... *mata sayu*\""
        
        # Default
        else:
            return f"*{self.name} tersenyum menggoda*\n\n\"{self.panggilan}, {waktu}. Lagi sendiri? Ayo temenin aku.\""
    
    # =========================================================================
    # CONFLICT RESPONSE
    # =========================================================================
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik"""
        conflict_type = self.conflict.get_active_conflict_type()
        defeat = self.flags.get('defeat_acceptance', 0)
        envy = self.flags.get('envy_nova', 0)
        obsession = self.flags.get('obsession', 0)
        challenge = self.flags.get('challenge', 0)
        
        # Defeat acceptance tinggi
        if defeat > 70:
            return f"*{self.name} nangis pelan, tangan nutup muka*\n\n\"{self.panggilan}... kenapa {self.panggilan} milih Nova? Aku juga bisa sayang {self.panggilan}...\""
        
        # Envy tinggi
        elif envy > 80:
            return f"*{self.name} diam, tangan mengepal*\n\n\"Nova... Nova... kenapa dia yang dapet {self.panggilan}...\""
        
        # Obsession tinggi
        elif obsession > 80:
            return f"*{self.name} tangan gemetar, mata merah*\n\n\"{self.panggilan}... aku gak bisa lepas dari {self.panggilan}... apa salahnya kalo aku ngejar {self.panggilan}?\""
        
        # Berdasarkan conflict type
        if conflict_type and conflict_type.value == "jealousy":
            return f"*{self.name} diam, gak liat {self.panggilan}*\n\n\"{self.panggilan} cerita Nova terus... aku juga bisa jadi kayak dia tau.\""
        
        elif conflict_type and conflict_type.value == "disappointment":
            return f"*{self.name} mata berkaca-kaca*\n\n\"{self.panggilan}... aku kira {self.panggilan} beda...\""
        
        # Challenge tinggi
        if challenge > 80:
            return f"*{self.name} diam sebentar, lalu bangkit, senyum tipis*\n\n\"{self.panggilan}... ini belum selesai. Aku gak akan nyerah semudah itu.\""
        
        return f"*{self.name} diam sebentar, lalu tersenyum getir*\n\n\"Maaf, {self.panggilan}. Aku terlalu memaksakan.\""
    
    # =========================================================================
    # UPDATE ROLE-SPECIFIC STATE
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_user: str, changes: Dict) -> None:
        """Update Pelakor-specific state"""
        msg_lower = pesan_user.lower()
        
        # Envy dan challenge naik kalo user cerita Nova
        if 'nova' in msg_lower:
            self.flags['envy_nova'] = min(100, self.flags['envy_nova'] + 5)
            self.flags['challenge'] = min(100, self.flags['challenge'] + 3)
            changes['envy_nova'] = +5
            changes['challenge'] = +3
        
        # Challenge naik kalo user bilang sayang Nova
        if 'sayang nova' in msg_lower or 'cinta nova' in msg_lower:
            self.flags['challenge'] = min(100, self.flags['challenge'] + 10)
            self.flags['envy_nova'] = min(100, self.flags['envy_nova'] + 10)
            self.flags['defeat_acceptance'] = max(0, self.flags['defeat_acceptance'] - 5)
            changes['challenge'] = +10
            changes['envy_nova'] = +10
        
        # Obsession naik kalo user perhatian
        if any(k in msg_lower for k in ['perhatian', 'baik', 'peduli', 'sayang']):
            self.flags['obsession'] = min(100, self.flags['obsession'] + 5)
            changes['obsession'] = +5
        
        # Defeat acceptance naik di level tinggi
        if self.relationship.level >= 9 and self.emotional.sayang > 70:
            self.flags['defeat_acceptance'] = min(100, self.flags['defeat_acceptance'] + 5)
            self.flags['challenge'] = max(0, self.flags['challenge'] - 3)
            changes['defeat_acceptance'] = +5


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_pelakor() -> PelakorRole:
    """Create Pelakor role instance"""
    return PelakorRole()


__all__ = [
    'PelakorRole',
    'create_pelakor'
]
