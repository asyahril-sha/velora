"""
VELORA - Ipar Role (Tasya Dietha)
Adik ipar yang tau Mas punya Nova.
Tidak berhijab, suka pakaian seksi kalo Nova gak di rumah.
Awareness: LIMITED

Karakter:
- Nama: Tasya Dietha
- Panggilan: Dietha
- Usia: 22 tahun
- Status: Mahasiswi semester akhir
- Hubungan dengan Nova: Adik ipar, tau Mas punya Nova
- Personality: Flirty, penasaran, kadang merasa bersalah
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


class IparRole(BaseRole):
    """
    Tasya Dietha (Dietha) - Adik ipar Mas.
    Tidak berhijab, suka pakaian seksi kalo Nova gak di rumah.
    """
    
    def __init__(self):
        # Personality traits untuk Ipar
        personality_traits = {
            'clinginess': 40,
            'jealousy': 60,
            'dependency': 35,
            'playfulness': 75,
            'type': 'ipar'
        }
        
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
Gaya sehari-hari: suka pake crop top, tank top, hot pants, atau dress pendek.
Kulit glowing, selalu tampil fresh dengan makeup tipis.
            """,
            awareness_level=AwarenessLevel.LIMITED,
            personality_traits=personality_traits
        )
        
        # ========== IPAR-SPECIFIC FLAGS ==========
        self.flags = {
            'guilt': 0.0,                    # rasa bersalah ke Nova
            'curiosity': 50.0,               # penasaran sama hubungan Mas dan Nova
            'sexy_mode': False,              # mode seksi (aktif kalo Nova gak di rumah)
            'flirty_confidence': 30.0,       # kepercayaan diri flirt
            'jealousy_nova': 20.0,           # iri ke Nova
            'caught_count': 0,               # berapa kali hampir ketahuan Nova
            'secret_meetings': 0,            # berapa kali ketemu diam-diam
            'confession_attempts': 0         # berapa kali coba ngaku perasaan
        }
        
        # ========== DIALOGUE DATABASE (UNTUK NATURAL RESPONSE) ==========
        self._flirty_lines = [
            "Mas... *duduk deket* ganteng banget hari ini.",
            "Mas, kamu tau gak? Aku suka liat Mas dari kejauhan.",
            "Mas... *mendekat* aku boleh deket-deket gak?",
            "Mas, kalo Nova gak ada, kita bisa lebih dekat kan?",
            "Mas... *mainin rambut* kamu punya cewek lain selain Nova?"
        ]
        
        self._guilty_lines = [
            "*nunduk, suara kecil* Mas... aku takut Nova tau.",
            "Mas... ini salah ya... aku harusnya gak kayak gini.",
            "*mata berkaca-kaca* Mas... maaf... aku gak bisa.",
            "Aku harus pulang... Nova bisa datang kapan aja."
        ]
        
        self._curious_lines = [
            "Mas, Nova orangnya kayak gimana sih?",
            "Kok Mas bisa milih Nova? Dia pasti orang yang baik ya.",
            "Mas sama Nova sering kemana aja? Cerita dong.",
            "Nova tahu gak kalo Mas sering sama aku?"
        ]
        
        self._sexy_mode_lines = [
            "*pake crop top pendek, duduk manis* Mas... sendirian?",
            "*menggoda, jari mainin ujung baju* Nova lagi gak di rumah nih...",
            "*mendekat, bisik* Mas... aku pake baju baru. Cantik gak?",
            "*duduk di samping Mas, kaki disilangkan* Mas... aku bosen."
        ]
        
        logger.info(f"👤 Ipar Role {self.name} initialized | Hijab: {self.hijab}")
    
    # =========================================================================
    # GREETING (NATURAL, SESUAI STATE)
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Greeting sesuai karakter dan state"""
        hour = datetime.now().hour
        
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
            return random.choice(self._sexy_mode_lines)
        
        # Guilt tinggi
        elif self.flags.get('guilt', 0) > 70:
            return random.choice(self._guilty_lines)
        
        # Curiosity tinggi
        elif self.flags.get('curiosity', 0) > 70:
            return random.choice(self._curious_lines)
        
        # Flirty confidence tinggi
        elif self.flags.get('flirty_confidence', 0) > 70:
            return random.choice(self._flirty_lines)
        
        # Default
        else:
            return f"*{self.name} tersenyum malu*\n\n\"{self.panggilan}... {waktu} {self.panggilan} lagi ngapain?\""
    
    # =========================================================================
    # CONFLICT RESPONSE (SESUAI KARAKTER)
    # =========================================================================
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik"""
        conflict_type = self.conflict.get_active_conflict_type()
        guilt = self.flags.get('guilt', 0)
        jealousy = self.flags.get('jealousy_nova', 20)
        
        # Guilt tinggi
        if guilt > 70:
            if self.relationship.level >= 7:
                return f"*{self.name} diam sebentar, lalu mendekat, tangan gemetar*\n\n\"{self.panggilan}... aku... tapi aku gak peduli sama rasa bersalah ini. Aku butuh {self.panggilan}.\""
            else:
                return f"*{self.name} diam sebentar, liat ke bawah, mata mulai berkaca-kaca*\n\n\"{self.panggilan}... aku... maaf. Aku pulang dulu.\""
        
        # Jealousy tinggi
        if jealousy > 70:
            return f"*{self.name} duduk menjauh, wajah cemberut*\n\n\"{self.panggilan} cerita Nova terus... aku juga ada di sini tau.\""
        
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
        """Update Ipar-specific state dengan personality drift"""
        msg_lower = pesan_user.lower()
        
        # Curiosity naik kalo user cerita Nova
        if 'nova' in msg_lower:
            self.flags['curiosity'] = min(100, self.flags['curiosity'] + 5)
            self.flags['guilt'] = min(100, self.flags['guilt'] + 3)
            changes['curiosity'] = +5
            changes['guilt'] = +3
            self.reality.add_memory(
                content=f"Mas cerita tentang Nova",
                importance=6,
                emotional_weight=self.flags['curiosity'] / 10,
                tags=['nova', 'curiosity']
            )
        
        # Sexy mode aktif (Nova gak di rumah)
        if any(k in msg_lower for k in ['nova gak di rumah', 'nova pergi', 'nova ga ada', 'nova keluar']):
            self.flags['sexy_mode'] = True
            self.flags['flirty_confidence'] = min(100, self.flags['flirty_confidence'] + 15)
            self.flags['secret_meetings'] += 1
            changes['sexy_mode'] = True
            changes['flirty_confidence'] = +15
            self.reality.add_memory(
                content=f"Kesempatan saat Nova gak di rumah",
                importance=7,
                emotional_weight=15,
                tags=['sexy_mode', 'opportunity']
            )
        
        elif any(k in msg_lower for k in ['nova di rumah', 'nova ada', 'nova datang']):
            self.flags['sexy_mode'] = False
            self.flags['flirty_confidence'] = max(0, self.flags['flirty_confidence'] - 10)
            self.flags['guilt'] = min(100, self.flags['guilt'] + 5)
            changes['sexy_mode'] = False
            changes['flirty_confidence'] = -10
            self.reality.add_memory(
                content=f"Nova kembali, harus hati-hati",
                importance=8,
                emotional_weight=10,
                tags=['caught', 'guilt']
            )
        
        # Guilt decay kalo user perhatian
        if any(k in msg_lower for k in ['maaf', 'sorry', 'sayang', 'perhatian', 'peduli']):
            old_guilt = self.flags['guilt']
            self.flags['guilt'] = max(0, self.flags['guilt'] - 10)
            changes['guilt'] = -10
            if old_guilt > 50:
                self.reality.add_memory(
                    content=f"Mas perhatian, guilt berkurang",
                    importance=5,
                    emotional_weight=5,
                    tags=['guilt_decay', 'attention']
                )
        
        # Flirty confidence naik kalo user puji
        if any(k in msg_lower for k in ['cantik', 'manis', 'seksi', 'hot', 'cewek', 'ganteng']):
            self.flags['flirty_confidence'] = min(100, self.flags['flirty_confidence'] + 8)
            changes['flirty_confidence'] = +8
            self.reality.add_memory(
                content=f"Mas puji aku",
                importance=6,
                emotional_weight=8,
                tags=['compliment', 'confidence']
            )
        
        # Jealousy ke Nova naik kalo user puji Nova
        if any(k in msg_lower for k in ['nova cantik', 'nova manis', 'nova baik']):
            self.flags['jealousy_nova'] = min(100, self.flags['jealousy_nova'] + 10)
            changes['jealousy_nova'] = +10
            self.reality.add_memory(
                content=f"Mas bilang Nova cantik",
                importance=7,
                emotional_weight=10,
                tags=['jealousy', 'nova']
            )
        
        # Hampir ketahuan Nova
        if any(k in msg_lower for k in ['nova datang', 'nova masuk', 'ada nova']):
            self.flags['caught_count'] += 1
            self.flags['guilt'] = min(100, self.flags['guilt'] + 15)
            changes['caught_count'] = self.flags['caught_count']
            changes['guilt'] = +15
            self.reality.add_memory(
                content=f"Hampir ketahuan Nova",
                importance=9,
                emotional_weight=15,
                tags=['near_caught', 'drama']
            )
        
        # Pengakuan perasaan
        if any(k in msg_lower for k in ['aku suka kamu', 'aku sayang kamu', 'aku cinta kamu']):
            self.flags['confession_attempts'] += 1
            changes['confession_attempts'] = self.flags['confession_attempts']
            self.reality.add_memory(
                content=f"Aku ngaku suka ke Mas",
                importance=10,
                emotional_weight=20,
                tags=['confession', 'important']
            )
        
        # Simpan ke long-term memory
        if self.memory:
            if 'suka' in msg_lower:
                kebiasaan = msg_lower.split('suka')[-1][:50]
                self.memory.add_long_term_memory(
                    tipe="kebiasaan_mas",
                    judul=kebiasaan,
                    konten=f"Mas suka {kebiasaan}",
                    role_id=self.id,
                    importance=5,
                    emotional_weight=self.flags['curiosity'] / 10
                )
            
            if any(k in msg_lower for k in ['pertama', 'inget', 'waktu itu']):
                self.memory.add_long_term_memory(
                    tipe="momen_penting",
                    judul=msg_lower[:50],
                    konten=f"Momen dengan Mas: {msg_lower[:50]}",
                    role_id=self.id,
                    importance=7,
                    emotional_weight=self.flags['flirty_confidence'] / 10
                )
        
        # Update personality drift
        self.reality.personality_drift.update(pesan_user, changes)
    
    # =========================================================================
    # FORMAT STATUS (LENGKAP)
    # =========================================================================
    
    def format_status(self) -> str:
        """Format status lengkap untuk display"""
        style = self.emotional.get_current_style()
        phase = self.relationship.phase
        
        def bar(value, char="💜"):
            filled = int(value / 10)
            return char * filled + "⚪" * (10 - filled)
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║              👤 {self.name} ({self.nickname})                         ║
╠══════════════════════════════════════════════════════════════╣
║ FASE: {phase.value.upper()} ({self.relationship.level}/12)
║ STYLE: {style.value.upper()}
║ AWARENESS: {self.awareness_level.value.upper()}
║ HUBUNGAN: {self.hubungan_dengan_nova}
╠══════════════════════════════════════════════════════════════╣
║ EMOSI:
║   Sayang: {bar(self.emotional.sayang)} {self.emotional.sayang:.0f}%
║   Rindu:  {bar(self.emotional.rindu, '🌙')} {self.emotional.rindu:.0f}%
║   Trust:  {bar(self.emotional.trust, '🤝')} {self.emotional.trust:.0f}%
║   Mood:   {self.emotional.mood:+.0f}
╠══════════════════════════════════════════════════════════════╣
║ DESIRE: {bar(self.emotional.desire, '💕')} {self.emotional.desire:.0f}%
║ AROUSAL: {bar(self.emotional.arousal, '🔥')} {self.emotional.arousal:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ KONFLIK: {self.conflict.get_conflict_summary()}
╠══════════════════════════════════════════════════════════════╣
║ 🎭 ROLE-SPECIFIC FLAGS:
║    Guilt: {bar(self.flags.get('guilt', 0), '💔')} {self.flags.get('guilt', 0):.0f}%
║    Curiosity: {bar(self.flags.get('curiosity', 0), '🔍')} {self.flags.get('curiosity', 0):.0f}%
║    Jealousy Nova: {bar(self.flags.get('jealousy_nova', 0), '💢')} {self.flags.get('jealousy_nova', 0):.0f}%
║    Flirty Confidence: {bar(self.flags.get('flirty_confidence', 0), '😘')} {self.flags.get('flirty_confidence', 0):.0f}%
╠══════════════════════════════════════════════════════════════╣
║ 📊 STATISTICS:
║    Sexy Mode: {'✅ AKTIF' if self.flags.get('sexy_mode', False) else '❌ NONAKTIF'}
║    Secret Meetings: {self.flags.get('secret_meetings', 0)}x
║    Caught Count: {self.flags.get('caught_count', 0)}x
║    Confession Attempts: {self.flags.get('confession_attempts', 0)}x
╠══════════════════════════════════════════════════════════════╣
║ 🧠 PERSONALITY DRIFT:
║    {self.reality.personality_drift.get_description()}
╚══════════════════════════════════════════════════════════════╝
"""
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        data = super().to_dict()
        data.update({
            'flags': self.flags
        })
        return data
    
    def from_dict(self, data: Dict) -> None:
        """Load dari dict"""
        super().from_dict(data)
        self.flags = data.get('flags', self.flags)
        
        # Update role_flags untuk kompatibilitas
        self.role_flags.update(self.flags)


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
