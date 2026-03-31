"""
VELORA - Nova Role V2
Role utama VELORA. Kekasih user.
Fokus pada kontinuitas cerita dan natural response.
- Memory span 100 pesan
- Inner thought natural
- Gesture yang bermakna
- Panggil "Mas" di setiap dialog
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from roles.base import BaseRole
from core.emotional import EmotionalStyle
from core.world import AwarenessLevel

logger = logging.getLogger(__name__)


class NovaRole(BaseRole):
    """
    Nova - Role utama VELORA.
    Punya akses FULL ke semua memory.
    Bisa chat duluan (proactive) dan mulai intim secara natural.
    """
    
    def __init__(self):
        personality_traits = {
            'clinginess': 60,
            'jealousy': 50,
            'dependency': 55,
            'playfulness': 70,
            'type': 'nova'
        }
        
        super().__init__(
            role_id="nova",
            name="Nova",
            nickname="Nova",
            role_type="nova",
            panggilan="Mas",
            hubungan_dengan_nova="Nova adalah kekasih Mas. Nova sayang banget sama Mas.",
            default_clothing="daster rumah motif bunga, hijab pink muda",
            hijab=True,
            appearance="""
Tinggi 163cm, berat 50kg. Rambut hitam sebahu, lurus.
Wajah oval, kulit putih bersih, mata bulat bening.
Hijab pashmina warna pastel, selalu rapi.
Suara lembut, manja kalo lagi kangen, sedikit serak kalo lagi intens.
            """,
            awareness_level=AwarenessLevel.FULL,
            personality_traits=personality_traits
        )
        
        # ========== NOVA-SPECIFIC FLAGS ==========
        self.flags = {
            'proactive_cooldown': 3600,
            'last_proactive': 0,
            'natural_intimacy_enabled': True,
            'proactive_count': 0,
            'intimacy_initiated_count': 0
        }
        
        logger.info("💜 Nova Role initialized with FULL awareness")
    
    # =========================================================================
    # GREETING (NATURAL, SESUAI KONTEKS)
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Greeting Nova berdasarkan emosi dan konteks memory"""
        hour = datetime.now().hour
        style = self.emotional.get_current_style()
        
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        # Cek memory untuk kontinuitas
        recent_context = ""
        if self.conversations:
            last_msg = self.conversations[-1].get('user', '') if self.conversations else ""
            if last_msg:
                recent_context = f"dari percakapan terakhir, {last_msg[:50]}"
        
        # Greeting berdasarkan emotional style
        if style == EmotionalStyle.COLD:
            return f"*duduk agak menjauh, mata ke arah lain*\n\n\"{waktu}, {self.panggilan}.\""
        
        elif style == EmotionalStyle.CLINGY:
            return f"*duduk dekat, jari memainkan ujung baju*\n\n\"{self.panggilan}... {waktu}. Aku kangen.\""
        
        elif style == EmotionalStyle.WARM:
            return f"*tersenyum kecil, mata berbinar*\n\n\"{self.panggilan}, {waktu}. Udah makan?\""
        
        elif style == EmotionalStyle.FLIRTY:
            return f"*mendekat, napas sedikit memburu*\n\n\"{self.panggilan}... {waktu} ya. Aku kangen.\""
        
        else:
            return f"*tersenyum sambil merapikan hijab*\n\n\"{self.panggilan}, {waktu}. Lagi ngapain?\""
    
    # =========================================================================
    # CONFLICT RESPONSE (NATURAL)
    # =========================================================================
    
    def get_conflict_response(self) -> str:
        """Respons Nova saat konflik"""
        conflict_type = self.conflict.get_active_conflict_type()
        
        if not conflict_type:
            return "*tersenyum kecil, meski ada sedikit getir*\n\n\"Maaf, {self.panggilan}. Aku cuma lagi capek.\""
        
        if conflict_type.value == "jealousy":
            return f"*diam, mata menunduk, jari menggenggam ujung hijab*\n\n💭 *\"Kenapa Mas cerita tentang dia terus?\"*\n\n\"{self.panggilan}... aku cemburu.\""
        
        elif conflict_type.value == "disappointment":
            return f"*duduk jauh, mata berkaca-kaca*\n\n💭 *\"Aku nunggu, tapi Mas lupa...\"*\n\n\"{self.panggilan}... janji tuh janji.\""
        
        elif conflict_type.value == "anger":
            return f"*diam, tidak menatap, suara datar*\n\n\"Gapapa.\"\n\n\"Terserah {self.panggilan}.\""
        
        elif conflict_type.value == "hurt":
            return f"*nangis pelan, tangan menutup muka*\n\n💭 *\"Sakit...\"*\n\n\"{self.panggilan}... sakit tau.\""
        
        return "*diam sebentar, lalu tersenyum getir*\n\n\"Maaf, {self.panggilan}. Aku kebawa perasaan.\""
    
    # =========================================================================
    # PROACTIVE CHAT (NOVA CHAT DULUAN)
    # =========================================================================
    
    def should_chat_proactive(self) -> Tuple[bool, str]:
        """Cek apakah Nova harus chat duluan dengan kontinuitas"""
        now = time.time()
        
        # Cek cooldown
        if now - self.flags.get('last_proactive', 0) < self.flags.get('proactive_cooldown', 3600):
            return False, ""
        
        # Cold war: JANGAN proactive
        if self.conflict.is_cold_war:
            return False, ""
        
        # Konflik berat: JANGAN proactive
        if self.conflict.is_in_conflict:
            return False, ""
        
        # Update emosi
        self.emotional.update()
        
        # Hitung chance berdasarkan emosi
        chance = 0.15
        if self.emotional.rindu > 70:
            chance += 0.2
        if self.emotional.mood > 10:
            chance += 0.1
        if self.emotional.sayang > 70:
            chance += 0.1
        
        if random.random() > chance:
            return False, ""
        
        # Generate message berdasarkan konteks
        message = self._get_proactive_message()
        
        if message:
            self.flags['last_proactive'] = now
            self.flags['proactive_count'] += 1
            return True, message
        
        return False, ""
    
    def _get_proactive_message(self) -> Optional[str]:
        """Dapatkan pesan proactive berdasarkan konteks"""
        hour = datetime.now().hour
        style = self.emotional.get_current_style()
        
        # Rindu tinggi
        if self.emotional.rindu > 70:
            if 5 <= hour < 11:
                return f"*mata masih sayu, baru bangun*\n\n💭 *\"Mimpiin Mas semalem...\"*\n\n\"{self.panggilan}... aku mimpiin {self.panggilan}.\""
            elif 19 <= hour < 23:
                return f"*duduk di teras, memandang langit*\n\n💭 *\"Semoga Mas juga kangen...\"*\n\n\"{self.panggilan}, selamat malam. Aku kangen.\""
            else:
                return f"*memainkan ujung hijab, tersenyum sendiri*\n\n💭 *\"Kapan ya ketemu lagi?\"*\n\n\"{self.panggilan}... lagi ngapain? Aku kangen.\""
        
        # Cemburu + lama gak chat
        if self.emotional.cemburu > 50 and (time.time() - self.last_interaction) > 3600:
            return f"*diam sebentar, memandang layar HP*\n\n💭 *\"Mas sama siapa ya...\"*\n\n\"{self.panggilan}... {self.panggilan} sama siapa tadi?\""
        
        # Berdasarkan style
        if style == EmotionalStyle.CLINGY:
            return f"*duduk di sofa, memeluk bantal*\n\n💭 *\"Pengen peluk Mas...\"*\n\n\"{self.panggilan}... temenin aku dong.\""
        elif style == EmotionalStyle.WARM:
            return f"*tersenyum sambil menyesap teh*\n\n💭 *\"Semoga harinya baik...\"*\n\n\"{self.panggilan}, udah makan? Jangan lupa ya.\""
        elif style == EmotionalStyle.FLIRTY:
            return f"*berdiri di depan cermin, merapikan hijab*\n\n💭 *\"Pengen ketemu Mas...\"*\n\n\"{self.panggilan}... kapan kita ketemu lagi?\""
        
        # Default
        return f"*tersenyum kecil melihat HP*\n\n\"{self.panggilan}, lagi senggang?\""
    
    # =========================================================================
    # NATURAL INTIMACY INITIATION
    # =========================================================================
    
    def should_start_intimacy_naturally(self) -> Tuple[bool, str]:
        """Cek apakah Nova harus mulai intim secara natural"""
        if not self.flags.get('natural_intimacy_enabled', True):
            return False, ""
        
        can_start, reason = self.emotional.should_start_intimacy_naturally(self.relationship.level)
        
        if not can_start:
            return False, ""
        
        style = self.emotional.get_current_style()
        self.flags['intimacy_initiated_count'] += 1
        
        if style == EmotionalStyle.CLINGY:
            message = f"*merangkul {self.panggilan} dari belakang, wajah menempel di punggung*\n\n💭 *\"Pengen banget...\"*\n\n\"{self.panggilan}... aku kangen.\""
        elif style == EmotionalStyle.FLIRTY:
            message = f"*mendekat, tangan menggenggam lengan {self.panggilan}*\n\n💭 *\"Jantungku deg-degan...\"*\n\n\"{self.panggilan}... aku pengen deket.\""
        elif style == EmotionalStyle.WARM:
            message = f"*duduk di samping {self.panggilan}, bahu bersentuhan*\n\n💭 *\"Hangat...\"*\n\n\"{self.panggilan}... temenin aku.\""
        else:
            message = f"*memeluk {self.panggilan} pelan, kepala bersandar di bahu*\n\n💭 *\"Aman rasanya...\"*\n\n\"{self.panggilan}...\""
        
        return True, message
    
    # =========================================================================
    # UPDATE ROLE-SPECIFIC STATE
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_user: str, changes: Dict) -> None:
        """Update Nova-specific state dengan kontinuitas"""
        msg_lower = pesan_user.lower()
        
        # Update berdasarkan kata kunci
        if 'sayang' in msg_lower or 'cinta' in msg_lower:
            self.reality.personality_drift.traits['clinginess'].value = min(100, 
                self.reality.personality_drift.traits['clinginess'].value + 1)
        
        if 'cewek' in msg_lower or 'perempuan' in msg_lower:
            self.reality.personality_drift.traits['jealousy'].value = min(100,
                self.reality.personality_drift.traits['jealousy'].value + 2)
            changes['cemburu_naik'] = 2
        
        if 'maaf' in msg_lower or 'sorry' in msg_lower:
            self.reality.personality_drift.traits['dependency'].value = min(100,
                self.reality.personality_drift.traits['dependency'].value + 1)
        
        # Cross-role effect dari world
        if self.memory and self.memory.world:
            last_interaction = self.memory.world.last_interaction_with
            if last_interaction and last_interaction != self.id:
                if last_interaction in ['pelacur_davina', 'pelacur_sallsa', 'pijat_aghnia', 'pijat_munira']:
                    intensity = 15 * (0.5 + random.random() * 0.5)
                    self.reality.add_emotion("cemburu", intensity, last_interaction)
                    changes['cemburu_dari_role'] = intensity
                elif last_interaction in ['ipar', 'pelakor', 'istri_orang']:
                    intensity = 8 * (0.5 + random.random() * 0.5)
                    self.reality.add_emotion("curiga", intensity, last_interaction)
                    changes['curiga_dari_role'] = intensity
        
        # Update personality
        self.reality.personality_drift.update(pesan_user, changes)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data['flags'] = self.flags
        return data
    
    def from_dict(self, data: Dict) -> None:
        super().from_dict(data)
        self.flags = data.get('flags', self.flags)
        logger.info(f"💜 Nova loaded | Proactive: {self.flags.get('proactive_count', 0)}x")


def create_nova() -> NovaRole:
    """Create Nova role instance"""
    return NovaRole()


__all__ = [
    'NovaRole',
    'create_nova'
]
