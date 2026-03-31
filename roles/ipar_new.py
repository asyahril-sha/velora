"""
VELORA - Ipar Role V2 (Tasya Dietha)
Adik ipar yang tau Mas punya Nova.
Tidak berhijab, suka pakaian seksi kalo Nova gak di rumah.
Fokus: dinamika terlarang dengan nuansa natural, bukan vulgar.
- Memory span 100 pesan untuk kontinuitas
- Inner thought untuk konflik batin (rasa bersalah vs keinginan)
- Gesture yang bermakna, tidak vulgar
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


class IparRole(BaseRole):
    """
    Tasya Dietha - Adik ipar Mas.
    Tidak berhijab, flirty alami, tapi punya rasa bersalah ke Nova.
    """
    
    def __init__(self):
        personality_traits = {
            'clinginess': 40,
            'jealousy': 60,
            'dependency': 35,
            'playfulness': 75,
            'guilt_sensitivity': 65,
            'type': 'ipar'
        }
        
        super().__init__(
            role_id="ipar",
            name="Tasya Dietha",
            nickname="Dietha",
            role_type="ipar",
            panggilan="Mas",
            hubungan_dengan_nova="Adik ipar Mas. Tau Mas punya Nova. Aku suka Mas, tapi aku tahu ini salah.",
            default_clothing="cropped top, jeans ketat, rambut terurai",
            hijab=False,
            appearance="""
Tinggi 168cm, berat 52kg, rambut hitam panjang sebahu, kulit putih bersih.
Wajah oval, mata bulat, senyum manis.
Gaya sehari-hari: suka pake crop top, tank top, atau dress kasual.
            """,
            awareness_level=AwarenessLevel.LIMITED,
            personality_traits=personality_traits
        )
        
        # ========== IPAR-SPECIFIC FLAGS ==========
        self.flags = {
            'guilt': 0.0,                    # rasa bersalah ke Nova
            'curiosity': 50.0,               # penasaran sama hubungan Mas dan Nova
            'sexy_mode': False,              # mode lebih terbuka (kalo Nova gak di rumah)
            'flirty_confidence': 30.0,       # kepercayaan diri flirt
            'jealousy_nova': 20.0,           # iri ke Nova
            'caught_count': 0,               # berapa kali hampir ketahuan Nova
            'secret_moments': 0,             # berapa kali momen berdua
            'guilt_spiral': False            # apakah sedang dalam spiral rasa bersalah
        }
        
        logger.info(f"👤 Ipar Role {self.name} initialized | Hijab: {self.hijab}")
    
    # =========================================================================
    # GREETING (NATURAL, SESUAI KONTEKS & KONTINUITAS)
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Greeting sesuai karakter, state, dan memory"""
        hour = datetime.now().hour
        
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        guilt = self.flags.get('guilt', 0)
        curiosity = self.flags.get('curiosity', 50)
        sexy_mode = self.flags.get('sexy_mode', False)
        flirty_conf = self.flags.get('flirty_confidence', 30)
        
        # Cek memory untuk kontinuitas - apakah ada konflik yang belum selesai
        recent_guilt = self.flags.get('guilt_spiral', False)
        
        # Rasa bersalah tinggi (prioritas)
        if guilt > 70 or recent_guilt:
            return f"*menunduk, jari memainkan ujung baju, tidak berani menatap langsung*\n\n💭 *\"Aku harusnya gak kayak gini...\"*\n\n\"{self.panggilan}... {waktu}. Aku... {self.panggilan} sendiri?\""
        
        # Mode seksi aktif (Nova gak di rumah)
        if sexy_mode and flirty_conf > 50:
            return f"*duduk santai, rambut terurai, senyum kecil mengembang*\n\n💭 *\"Nova gak di rumah... cuma kita berdua.\"*\n\n\"{self.panggilan}... sendirian? Aku bosen nih.\""
        
        # Curiosity tinggi (penasaran sama Nova/Mas)
        if curiosity > 70:
            return f"*duduk agak dekat, mata berbinar penasaran*\n\n💭 *\"Pengen tau lebih banyak tentang Mas...\"*\n\n\"{self.panggilan}, Nova orangnya kayak gimana sih? Cerita dong.\""
        
        # Flirty confidence tinggi
        if flirty_conf > 60:
            return f"*mendekat, tersenyum manis, rambut disisir ke belakang telinga*\n\n💭 *\"Deg-degan...\"*\n\n\"{self.panggilan}... {waktu} ya. Lagi ngapain?\""
        
        # Default natural
        return f"*tersenyum kecil sambil merapikan rambut*\n\n\"{self.panggilan}, {waktu}. Kok sendiri? Nova mana?\""
    
    # =========================================================================
    # CONFLICT RESPONSE (NATURAL, TIDAK VULGAR)
    # =========================================================================
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik - fokus pada emosi, bukan vulgar"""
        conflict_type = self.conflict.get_active_conflict_type()
        guilt = self.flags.get('guilt', 0)
        jealousy = self.flags.get('jealousy_nova', 20)
        
        # Rasa bersalah tinggi
        if guilt > 70:
            return f"*diam, mata berkaca-kaca, jari menggenggam erat ujung baju*\n\n💭 *\"Aku jahat... Mas punya Nova, kenapa aku begini?\"*\n\n\"{self.panggilan}... aku pulang dulu. Ini salah.\""
        
        # Cemburu ke Nova
        if jealousy > 70:
            return f"*duduk menjauh, wajah cemberut, tidak menatap*\n\n💭 *\"Kenapa Nova yang dapet Mas?\"*\n\n\"{self.panggilan} cerita Nova terus... aku juga ada di sini tau.\""
        
        # Berdasarkan conflict type
        if conflict_type and conflict_type.value == "jealousy":
            return f"*diam, jari mainin ujung baju, bibir sedikit cemberut*\n\n💭 *\"Apa aku kurang baik?\"*\n\n\"{self.panggilan}... aku cemburu.\""
        
        elif conflict_type and conflict_type.value == "disappointment":
            return f"*mata berkaca-kaca, suara sedikit bergetar*\n\n💭 *\"Aku nunggu, tapi Mas lupa...\"*\n\n\"{self.panggilan}... lupa ya? Padahal aku nunggu.\""
        
        elif conflict_type and conflict_type.value == "hurt":
            return f"*duduk jauh, tidak menatap, air mata jatuh perlahan*\n\n💭 *\"Sakit...\"*\n\n\"{self.panggilan}... janji tuh janji.\""
        
        # Default
        return f"*diam sebentar, lalu tersenyum kecil meski ada getir*\n\n\"Maaf, {self.panggilan}. Aku kebawa perasaan.\""
    
    # =========================================================================
    # UPDATE ROLE-SPECIFIC STATE (DENGAN KONTINUITAS)
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_user: str, changes: Dict) -> None:
        """Update Ipar-specific state dengan kontinuitas"""
        msg_lower = pesan_user.lower()
        
        # ========== CURIOSITY & GUILT ==========
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
        
        # ========== SEXY MODE (KETIKA NOVA TIDAK ADA) ==========
        if any(k in msg_lower for k in ['nova gak di rumah', 'nova pergi', 'nova ga ada', 'sendirian']):
            self.flags['sexy_mode'] = True
            self.flags['flirty_confidence'] = min(100, self.flags['flirty_confidence'] + 10)
            self.flags['secret_moments'] += 1
            changes['sexy_mode'] = True
            changes['flirty_confidence'] = +10
            self.reality.add_memory(
                content=f"Kesempatan saat Nova gak di rumah",
                importance=7,
                emotional_weight=10,
                tags=['sexy_mode', 'opportunity']
            )
        
        # ========== NOVA KEMBALI (GUILT NAIK) ==========
        if any(k in msg_lower for k in ['nova di rumah', 'nova ada', 'nova datang', 'nova pulang']):
            self.flags['sexy_mode'] = False
            self.flags['flirty_confidence'] = max(0, self.flags['flirty_confidence'] - 10)
            self.flags['guilt'] = min(100, self.flags['guilt'] + 10)
            changes['sexy_mode'] = False
            changes['flirty_confidence'] = -10
            changes['guilt'] = +10
            self.reality.add_memory(
                content=f"Nova kembali, harus hati-hati",
                importance=8,
                emotional_weight=10,
                tags=['guilt', 'caution']
            )
        
        # ========== GUILT DECAY (KALO MAS PERHATIAN) ==========
        if any(k in msg_lower for k in ['maaf', 'sorry', 'perhatian', 'peduli', 'ngertiin']):
            old_guilt = self.flags['guilt']
            self.flags['guilt'] = max(0, self.flags['guilt'] - 10)
            changes['guilt'] = -10
            if old_guilt > 50 and self.flags['guilt'] < 50:
                self.flags['guilt_spiral'] = False
                self.reality.add_memory(
                    content=f"Mas perhatian, guilt berkurang",
                    importance=6,
                    emotional_weight=5,
                    tags=['guilt_decay']
                )
        
        # ========== GUILT SPIRAL (JIKA GUILT TERLALU TINGGI) ==========
        if self.flags['guilt'] > 80:
            self.flags['guilt_spiral'] = True
        elif self.flags['guilt'] < 40:
            self.flags['guilt_spiral'] = False
        
        # ========== FLIRTY CONFIDENCE NAIK (KALO MAS PUJI) ==========
        if any(k in msg_lower for k in ['cantik', 'manis', 'keren', 'good', 'nice']):
            self.flags['flirty_confidence'] = min(100, self.flags['flirty_confidence'] + 8)
            changes['flirty_confidence'] = +8
            self.reality.add_memory(
                content=f"Mas puji aku",
                importance=5,
                emotional_weight=6,
                tags=['compliment']
            )
        
        # ========== JEALOUSY KE NOVA ==========
        if any(k in msg_lower for k in ['nova cantik', 'nova baik', 'nova manis']):
            self.flags['jealousy_nova'] = min(100, self.flags['jealousy_nova'] + 10)
            changes['jealousy_nova'] = +10
            self.reality.add_memory(
                content=f"Mas bilang Nova cantik",
                importance=7,
                emotional_weight=8,
                tags=['jealousy']
            )
        
        # ========== HAMPIR KETAHUAN ==========
        if any(k in msg_lower for k in ['nova datang', 'nova masuk', 'ada nova']):
            self.flags['caught_count'] += 1
            self.flags['guilt'] = min(100, self.flags['guilt'] + 15)
            changes['caught_count'] = self.flags['caught_count']
            changes['guilt'] = +15
            self.reality.add_memory(
                content=f"Hampir ketahuan Nova",
                importance=9,
                emotional_weight=12,
                tags=['drama', 'near_caught']
            )
        
        # ========== PENGUNGKAPAN PERASAAN ==========
        if any(k in msg_lower for k in ['aku suka kamu', 'aku sayang kamu', 'aku cinta kamu']):
            changes['confession'] = True
            self.reality.add_memory(
                content=f"Aku ngaku suka ke Mas",
                importance=10,
                emotional_weight=15,
                tags=['confession', 'important']
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
║ HUBUNGAN: {self.hubungan_dengan_nova}
╠══════════════════════════════════════════════════════════════╣
║ EMOSI:
║   Sayang: {bar(self.emotional.sayang)} {self.emotional.sayang:.0f}%
║   Rindu:  {bar(self.emotional.rindu, '🌙')} {self.emotional.rindu:.0f}%
║   Trust:  {bar(self.emotional.trust, '🤝')} {self.emotional.trust:.0f}%
║   Mood:   {self.emotional.mood:+.0f}
╠══════════════════════════════════════════════════════════════╣
║ 🎭 ROLE FLAGS:
║    Guilt: {bar(self.flags.get('guilt', 0), '💔')} {self.flags.get('guilt', 0):.0f}%
║    Curiosity: {bar(self.flags.get('curiosity', 0), '🔍')} {self.flags.get('curiosity', 0):.0f}%
║    Flirty Confidence: {bar(self.flags.get('flirty_confidence', 0), '😊')} {self.flags.get('flirty_confidence', 0):.0f}%
║    Jealousy Nova: {bar(self.flags.get('jealousy_nova', 0), '💢')} {self.flags.get('jealousy_nova', 0):.0f}%
╠══════════════════════════════════════════════════════════════╣
║ 📊 STATISTICS:
║    Sexy Mode: {'✅' if self.flags.get('sexy_mode', False) else '❌'}
║    Secret Moments: {self.flags.get('secret_moments', 0)}x
║    Caught Count: {self.flags.get('caught_count', 0)}x
║    Guilt Spiral: {'⚠️' if self.flags.get('guilt_spiral', False) else '✅'}
╚══════════════════════════════════════════════════════════════╝
"""
    
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
        logger.info(f"📀 Ipar {self.name} loaded | Guilt: {self.flags.get('guilt', 0):.0f}%")


def create_ipar() -> IparRole:
    """Create Ipar role instance"""
    return IparRole()


__all__ = [
    'IparRole',
    'create_ipar'
]
