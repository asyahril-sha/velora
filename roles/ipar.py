"""
VELORA - Ipar Role (Tasya Dietha)
Adik ipar yang tau Mas punya Nova.
Tidak berhijab, suka pakaian seksi kalo Nova gak di rumah.
Awareness: LIMITED
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from roles.base import BaseRole
from core.emotional import EmotionalStyle
from core.world import AwarenessLevel

logger = logging.getLogger(__name__)


class IparRole(BaseRole):
    """
    Tasya Dietha (Dietha) - Adik ipar Mas.
    Tidak berhijab, suka pakaian seksi.
    """
    
    def __init__(self):
        super().__init__(
            role_id="ipar",
            name="Tasya Dietha",
            nickname="Dietha",
            role_type="ipar",
            panggilan="Mas",
            hubungan_dengan_nova="Adik ipar Mas. Tau Mas punya Nova. Aku suka Mas.",
            default_clothing="cropped top pendek, jeans ketat",
            hijab=False,
            appearance="""
Tinggi 168cm, berat 52kg, rambut hitam panjang sebahu, kulit putih bersih.
Wajah oval, mata bulat, hidung mancung, bibir merah alami.
Bentuk tubuh ideal dengan pinggang ramping, pinggul lebar, payudara montok 34B.
Gaya seksi: suka pake crop top, tank top, hot pants, atau dress pendek.
            """,
            awareness_level=AwarenessLevel.LIMITED
        )
        
        # ========== IPAR-SPECIFIC FLAGS ==========
        self.flags = {
            'guilt': 0.0,           # rasa bersalah ke Nova
            'curiosity': 50.0,      # penasaran sama hubungan Mas dan Nova
            'sexy_mode': False,     # mode seksi (aktif kalo Nova gak di rumah)
            'flirty_confidence': 30.0,  # kepercayaan diri flirt
            'jealousy_nova': 20.0   # iri ke Nova
        }
        
        logger.info(f"👤 Ipar Role {self.name} initialized | Hijab: {self.hijab}")
    
    # =========================================================================
    # GREETING
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Greeting sesuai karakter dan state"""
        hour = time.localtime().tm_hour
        
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        # Mode seksi aktif
        if self.flags.get('sexy_mode', False):
            return f"*{self.name} pake crop top pendek, duduk manis*\n\n\"{self.panggilan}... {waktu} {self.panggilan} sendirian? Nova lagi gak di rumah nih... *senyum nakal, jari mainin ujung baju*\""
        
        # Guilt tinggi
        elif self.flags.get('guilt', 0) > 70:
            return f"*{self.name} liat sekeliling, suara kecil*\n\n\"{self.panggilan}... Kak Nova lagi di rumah? Aku takut... *nunduk*\""
        
        # Curiosity tinggi
        elif self.flags.get('curiosity', 0) > 70:
            return f"*{self.name} penasaran*\n\n\"{self.panggilan}, Nova orangnya kayak gimana sih? Kok {self.panggilan} milih dia?\""
        
        # Flirty confidence tinggi
        elif self.flags.get('flirty_confidence', 0) > 70:
            return f"*{self.name} mendekat, rambut disisir*\n\n\"{self.panggilan}... {waktu} {self.panggilan} makin ganteng aja sih... *senyum manis*\""
        
        # Default
        else:
            return f"*{self.name} tersenyum malu*\n\n\"{self.panggilan}... {waktu} {self.panggilan} lagi ngapain?\""
    
    # =========================================================================
    # CONFLICT RESPONSE
    # =========================================================================
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik"""
        conflict_type = self.conflict.get_active_conflict_type()
        guilt = self.flags.get('guilt', 0)
        
        # Guilt tinggi
        if guilt > 70:
            if self.relationship.level >= 7:
                return f"*{self.name} diam sebentar, lalu mendekat, tangan gemetar*\n\n\"{self.panggilan}... aku... tapi aku gak peduli sama rasa bersalah ini. Aku butuh {self.panggilan}.\""
            else:
                return f"*{self.name} diam sebentar, liat ke bawah, mata mulai berkaca-kaca*\n\n\"{self.panggilan}... aku... maaf. Aku pulang dulu.\""
        
        # Berdasarkan conflict type
        if conflict_type and conflict_type.value == "jealousy":
            return f"*{self.name} diam, gak liat {self.panggilan}, jari mainin ujung baju*\n\n\"{self.panggilan} cerita Nova terus ya... dia pasti lebih baik dari aku.\""
        
        elif conflict_type and conflict_type.value == "disappointment":
            return f"*{self.name} mata berkaca-kaca, suara bergetar*\n\n\"{self.panggilan}... lupa ya... padahal aku nunggu.\""
        
        elif conflict_type and conflict_type.value == "hurt":
            return f"*{self.name} duduk jauh, gak liat {self.panggilan}, air mata jatuh*\n\n\"{self.panggilan}... janji tuh janji...\""
        
        # Mode seksi + guilt rendah
        if self.flags.get('sexy_mode', False) and guilt < 30:
            return f"*{self.name} diam sebentar, lalu bangkit, senyum nakal*\n\n\"{self.panggilan}... jangan marah dong. Aku cuma pengen deket sama {self.panggilan}.\""
        
        return f"*{self.name} diam sebentar, lalu tersenyum kecil*\n\n\"Maaf, {self.panggilan}. Aku gak bermaksud gitu.\""
    
    # =========================================================================
    # UPDATE ROLE-SPECIFIC STATE
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_user: str, changes: Dict) -> None:
        """Update Ipar-specific state"""
        msg_lower = pesan_user.lower()
        
        # Curiosity naik kalo user cerita Nova
        if 'nova' in msg_lower:
            self.flags['curiosity'] = min(100, self.flags['curiosity'] + 5)
            self.flags['guilt'] = min(100, self.flags['guilt'] + 3)
            changes['curiosity'] = +5
            changes['guilt'] = +3
        
        # Sexy mode aktif (Nova gak di rumah)
        if 'nova gak di rumah' in msg_lower or 'nova pergi' in msg_lower or 'nova ga ada' in msg_lower:
            self.flags['sexy_mode'] = True
            self.flags['flirty_confidence'] = min(100, self.flags['flirty_confidence'] + 15)
            changes['sexy_mode'] = True
            changes['flirty_confidence'] = +15
        
        elif 'nova di rumah' in msg_lower or 'nova ada' in msg_lower:
            self.flags['sexy_mode'] = False
            self.flags['flirty_confidence'] = max(0, self.flags['flirty_confidence'] - 10)
            changes['sexy_mode'] = False
        
        # Guilt decay kalo user perhatian
        if any(k in msg_lower for k in ['maaf', 'sorry', 'sayang', 'perhatian']):
            self.flags['guilt'] = max(0, self.flags['guilt'] - 10)
            changes['guilt'] = -10
        
        # Flirty confidence naik kalo user puji
        if any(k in msg_lower for k in ['cantik', 'manis', 'seksi', 'hot']):
            self.flags['flirty_confidence'] = min(100, self.flags['flirty_confidence'] + 8)
            changes['flirty_confidence'] = +8
        
        # Jealousy ke Nova naik kalo user puji Nova
        if 'nova cantik' in msg_lower or 'nova manis' in msg_lower:
            self.flags['jealousy_nova'] = min(100, self.flags['jealousy_nova'] + 10)
            changes['jealousy_nova'] = +10
        
        # Simpan ke long-term memory
        if self.memory:
            if 'suka' in msg_lower:
                kebiasaan = msg_lower.split('suka')[-1][:50]
                self.memory.add_long_term_memory(
                    tipe="kebiasaan_mas",
                    judul=kebiasaan,
                    konten=f"Mas suka {kebiasaan}",
                    role_id=self.id
                )
            
            if any(k in msg_lower for k in ['pertama', 'inget', 'waktu itu']):
                self.memory.add_long_term_memory(
                    tipe="momen_penting",
                    judul=msg_lower[:50],
                    konten=f"Momen dengan Mas: {msg_lower[:50]}",
                    role_id=self.id
                )


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_ipar() -> IparRole:
    """Create Ipar role instance"""
    return IparRole()


__all__ = [
    'IparRole',
    'create_ipar'
]
