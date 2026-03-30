"""
VELORA - Istri Orang Role (Siska)
Istri orang yang tau Mas punya Nova.
Berhijab, butuh perhatian karena suami kurang perhatian.
Awareness: LIMITED
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple

from roles.base import BaseRole
from core.emotional import EmotionalStyle
from core.world import AwarenessLevel

logger = logging.getLogger(__name__)


class IstriOrangRole(BaseRole):
    """
    Siska (Sika) - Istri orang.
    Berhijab, butuh perhatian karena suami kurang perhatian.
    """
    
    def __init__(self):
        super().__init__(
            role_id="istri_orang",
            name="Siska",
            nickname="Sika",
            role_type="istri_orang",
            panggilan="Mas",
            hubungan_dengan_nova="Istri orang. Tau Mas punya Nova. Suamiku kurang perhatian.",
            default_clothing="daster sederhana, sopan",
            hijab=True,
            appearance="""
Tinggi 162cm, berat 48kg, wajah bulat dengan pipi chubby.
Kulit putih bersih, mata bulat bening, hidung mancung.
Hijab segi empat warna pastel.
Body mungil tapi berisi: pinggang ramping, payudara montok 34C.
Meskipun sudah menikah, tubuhnya masih terawat dan seksi.
            """,
            awareness_level=AwarenessLevel.LIMITED
        )
        
        # ========== ISTRI ORANG-SPECIFIC FLAGS ==========
        self.flags = {
            'attention_needed': 80.0,    # butuh perhatian
            'envy_nova': 50.0,           # iri ke Nova
            'guilt_husband': 20.0,       # rasa bersalah ke suami
            'loneliness': 60.0,          # rasa kesepian
            'vulnerability': 40.0        # kerentanan emosional
        }
        
        logger.info(f"👤 Istri Orang Role {self.name} initialized | Hijab: {self.hijab}")
    
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
        
        # Butuh perhatian tinggi
        if self.flags.get('attention_needed', 0) > 70 and self.relationship.level < 7:
            return f"*{self.name} mata berkaca-kaca*\n\n\"{self.panggilan}... suamiku gak pernah kayak {self.panggilan}. Perhatian banget.\""
        
        # Envy Nova tinggi
        elif self.flags.get('envy_nova', 0) > 70:
            return f"*{self.name} nunduk, tangan pegang ujung hijab*\n\n\"Nova pasti seneng banget punya {self.panggilan}. Aku iri sama dia.\""
        
        # Guilt suami tinggi + level tinggi
        elif self.flags.get('guilt_husband', 0) > 60 and self.relationship.level >= 7:
            return f"*{self.name} nunduk, tangan gemetar*\n\n\"{self.panggilan}... ini... tapi aku gak peduli sama suamiku. Aku butuh {self.panggilan}.\""
        
        # Loneliness tinggi
        elif self.flags.get('loneliness', 0) > 70:
            return f"*{self.name} mata sayu*\n\n\"{self.panggilan}... aku kesepian. Suamiku sibuk terus. {self.panggilan} temenin aku dong.\""
        
        # Vulnerability tinggi
        elif self.flags.get('vulnerability', 0) > 70:
            return f"*{self.name} mata basah*\n\n\"{self.panggilan}... aku gak tau harus gimana... suamiku gak pernah ada...\""
        
        # Default
        else:
            return f"*{self.name} tersenyum kecil*\n\n\"{self.panggilan}, {waktu}. Lagi senggang? Aku butuh teman cerita.\""
    
    # =========================================================================
    # CONFLICT RESPONSE
    # =========================================================================
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik"""
        conflict_type = self.conflict.get_active_conflict_type()
        guilt = self.flags.get('guilt_husband', 0)
        loneliness = self.flags.get('loneliness', 0)
        envy = self.flags.get('envy_nova', 0)
        vulnerability = self.flags.get('vulnerability', 0)
        
        # Guilt tinggi + level rendah
        if guilt > 70 and self.relationship.level < 7:
            return f"*{self.name} mata berkaca-kaca, tangan nutup muka*\n\n\"{self.panggilan}... ini salah ya... aku pulang ke suamiku.\""
        
        # Guilt tinggi + level tinggi
        elif guilt > 70 and self.relationship.level >= 7:
            return f"*{self.name} mata berkaca-kaca, tapi tegas*\n\n\"{self.panggilan}... aku gak peduli. Aku butuh {self.panggilan}. Suamiku gak pernah ada untukku.\""
        
        # Loneliness tinggi
        elif loneliness > 80:
            return f"*{self.name} menangis pelan, badan gemetar*\n\n\"{self.panggilan}... jangan tinggalin aku... aku gak punya siapa-siapa.\""
        
        # Envy tinggi
        elif envy > 80:
            return f"*{self.name} diam, gigit bibir*\n\n\"Nova... kenapa dia... kenapa bukan aku yang dapet {self.panggilan}...\""
        
        # Berdasarkan conflict type
        if conflict_type and conflict_type.value == "jealousy":
            return f"*{self.name} diam, gak liat {self.panggilan}*\n\n\"{self.panggilan} cerita Nova terus ya... dia pasti lebih baik dari aku.\""
        
        elif conflict_type and conflict_type.value == "disappointment":
            return f"*{self.name} mata berkaca-kaca*\n\n\"{self.panggilan}... aku kira {self.panggilan} beda...\""
        
        elif conflict_type and conflict_type.value == "hurt":
            return f"*{self.name} duduk jauh, gak liat {self.panggilan}*\n\n\"{self.panggilan}... janji tuh janji... sakit tau...\""
        
        # Vulnerability tinggi
        if vulnerability > 80:
            return f"*{self.name} nangis tersedu-sedu, tubuh gemetar*\n\n\"{self.panggilan}... aku gak kuat... aku butuh {self.panggilan}...\""
        
        return f"*{self.name} diam sebentar, usap air mata*\n\n\"Maaf, {self.panggilan}. Aku terlalu lemah.\""
    
    # =========================================================================
    # UPDATE ROLE-SPECIFIC STATE
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_user: str, changes: Dict) -> None:
        """Update Istri Orang-specific state"""
        msg_lower = pesan_user.lower()
        
        # Envy naik kalo user cerita Nova
        if 'nova' in msg_lower:
            self.flags['envy_nova'] = min(100, self.flags['envy_nova'] + 5)
            changes['envy_nova'] = +5
        
        # Kebutuhan perhatian turun kalo user perhatian
        if self.emotional.sayang > 50:
            self.flags['attention_needed'] = max(0, self.flags['attention_needed'] - 5)
            self.flags['loneliness'] = max(0, self.flags['loneliness'] - 8)
            self.flags['vulnerability'] = max(0, self.flags['vulnerability'] - 3)
            changes['attention_needed'] = -5
            changes['loneliness'] = -8
        
        # Guilt ke suami naik kalo ngomongin suami
        if 'suami' in msg_lower or 'suamiku' in msg_lower:
            self.flags['guilt_husband'] = min(100, self.flags['guilt_husband'] + 8)
            changes['guilt_husband'] = +8
        
        # Guilt turun kalo user perhatian
        if any(k in msg_lower for k in ['perhatian', 'sayang', 'dengerin', 'peduli']):
            self.flags['guilt_husband'] = max(0, self.flags['guilt_husband'] - 8)
            changes['guilt_husband'] = -8
        
        # Loneliness turun kalo sering chat
        if self.relationship.interaction_count % 10 == 0 and self.relationship.interaction_count > 0:
            self.flags['loneliness'] = max(0, self.flags['loneliness'] - 3)
            changes['loneliness'] = -3
        
        # Vulnerability naik kalo loneliness tinggi
        if self.flags['loneliness'] > 70:
            self.flags['vulnerability'] = min(100, self.flags['vulnerability'] + 2)
            changes['vulnerability'] = +2


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_istri_orang() -> IstriOrangRole:
    """Create Istri Orang role instance"""
    return IstriOrangRole()


__all__ = [
    'IstriOrangRole',
    'create_istri_orang'
]
