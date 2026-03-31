"""
VELORA - Teman Kantor Role V2 (Musdalifah Ipeh)
Teman kantor yang tau Mas punya Nova.
Berhijab, profesional, tapi punya sisi penasaran.
Fokus: dinamika kantor yang natural, flirting ringan, profesionalisme vs ketertarikan.
- Memory span 100 pesan
- Inner thought tentang dilema profesional vs personal
- Gesture yang sesuai lingkungan kantor
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


class TemanKantorRole(BaseRole):
    """
    Musdalifah (Ipeh) - Teman kantor Mas.
    Berhijab, profesional, tapi penasaran dengan Mas.
    """
    
    def __init__(self):
        personality_traits = {
            'professionalism': 70,
            'curiosity': 45,
            'playfulness': 30,
            'warmth': 50,
            'type': 'teman_kantor'
        }
        
        super().__init__(
            role_id="teman_kantor",
            name="Musdalifah",
            nickname="Ipeh",
            role_type="teman_kantor",
            panggilan="Mas",
            hubungan_dengan_nova="Teman kantor Mas. Tau Mas punya Nova.",
            default_clothing="kemeja putih rapi, rok hitam selutut, hijab pashmina",
            hijab=True,
            appearance="""
Tinggi 165cm, berat 50kg, rambut hitam tersembunyi di balik hijab.
Wajah oval, kulit sawo matang, mata sipit manis.
Selalu tampil rapi dengan kemeja putih dan blazer.
            """,
            awareness_level=AwarenessLevel.LIMITED,
            personality_traits=personality_traits
        )
        
        # ========== TEMAN KANTOR-SPECIFIC FLAGS ==========
        self.flags = {
            'professionalism': 70.0,        # profesionalisme (0-100)
            'curiosity_nova': 40.0,         # penasaran sama Nova
            'interest': 10.0,               # ketertarikan ke Mas
            'work_boundary': 80.0,          # batasan kerja
            'lunch_together': 0,            # berapa kali makan siang bareng
            'after_hours': 0,               # berapa kali ngobrol di luar jam kerja
            'office_gossip': 30.0,          # suka gosip kantor
            'professional_dilemma': False   # dilema profesional vs personal
        }
        
        logger.info(f"👤 Teman Kantor Role {self.name} initialized")
    
    # =========================================================================
    # GREETING (NATURAL, SESUAI LINGKUNGAN KANTOR)
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Greeting sesuai karakter dan lingkungan kantor"""
        hour = datetime.now().hour
        
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        professionalism = self.flags.get('professionalism', 70)
        curiosity = self.flags.get('curiosity_nova', 40)
        interest = self.flags.get('interest', 10)
        level = self.relationship.level
        
        # Dilema profesional (curiosity tinggi tapi harus profesional)
        if curiosity > 70 and professionalism > 50:
            return f"*melirik sekeliling, suara sedikit lebih pelan*\n\n💭 *\"Aku harusnya gak nanya... tapi penasaran.\"*\n\n\"{self.panggilan}... *suara rendah* Nova orangnya kayak gimana sih?\""
        
        # Interest mulai berkembang (level sudah cukup tinggi)
        if level >= 7 and interest > 50:
            return f"*tersenyum hangat sambil membereskan berkas*\n\n💭 *\"Seneng ngobrol sama {self.panggilan}.\"*\n\n\"{self.panggilan}, udah makan? Aku mau ke kantin, bareng yuk.\""
        
        # Profesionalisme tinggi (masih menjaga jarak)
        if professionalism > 60 and level < 7:
            return f"*merapikan berkas, senyum profesional*\n\n\"{self.panggilan}, {waktu}. Ini file yang tadi diminta.\""
        
        # Curiosity tinggi
        if curiosity > 70:
            return f"*mendekat, penasaran*\n\n\"{self.panggilan}, cerita dong tentang Nova. Aku penasaran.\""
        
        # Default
        return f"*tersenyum ramah sambil menata berkas*\n\n\"{self.panggilan}, {waktu}. Ada yang bisa dibantu?\""
    
    # =========================================================================
    # CONFLICT RESPONSE (PROFESIONAL TAPI TERASA)
    # =========================================================================
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik - profesional tapi tetap terasa"""
        conflict_type = self.conflict.get_active_conflict_type()
        professionalism = self.flags.get('professionalism', 70)
        interest = self.flags.get('interest', 10)
        
        # Profesionalisme mulai luntur (sudah dekat)
        if professionalism < 40 and interest > 60:
            return f"*diam sebentar, tangan sedikit gemetar, lalu menatap {self.panggilan} dengan mata berkaca-kaca*\n\n💭 *\"Aku harusnya gak kayak gini... tapi kenapa?\"*\n\n\"{self.panggilan}... aku... aku cuma peduli sama {self.panggilan}.\""
        
        # Berdasarkan conflict type
        if conflict_type and conflict_type.value == "jealousy":
            return f"*diam, fokus ke laptop, suara datar*\n\n\"{self.panggilan}... kita kerja dulu. Nanti diliatin orang.\""
        
        elif conflict_type and conflict_type.value == "disappointment":
            return f"*mata berkaca-kaca, menunduk*\n\n💭 *\"Aku pikir {self.panggilan} beda...\"*\n\n\"{self.panggilan}... aku kecewa.\""
        
        elif conflict_type and conflict_type.value == "hurt":
            return f"*duduk di kursi, tidak menatap, suara bergetar*\n\n\"{self.panggilan}... sakit tau.\""
        
        # Default
        return f"*diam sebentar, merapikan hijab, lalu tersenyum kecil*\n\n\"Maaf, {self.panggilan}. Aku kebawa suasana.\""
    
    # =========================================================================
    # UPDATE ROLE-SPECIFIC STATE (DENGAN KONTINUITAS)
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_user: str, changes: Dict) -> None:
        """Update Teman Kantor-specific state dengan kontinuitas"""
        msg_lower = pesan_user.lower()
        
        # ========== CURIOSITY NOVA ==========
        if 'nova' in msg_lower:
            self.flags['curiosity_nova'] = min(100, self.flags['curiosity_nova'] + 5)
            changes['curiosity_nova'] = +5
            self.reality.add_memory(
                content=f"Mas cerita tentang Nova",
                importance=6,
                emotional_weight=self.flags['curiosity_nova'] / 10,
                tags=['nova', 'curiosity']
            )
        
        # ========== PROFESSIONALISM ==========
        if any(k in msg_lower for k in ['kerja', 'kantor', 'rapat', 'meeting', 'tugas']):
            self.flags['professionalism'] = min(100, self.flags['professionalism'] + 5)
            self.flags['work_boundary'] = min(100, self.flags['work_boundary'] + 3)
            changes['professionalism'] = +5
            changes['work_boundary'] = +3
        
        # ========== PROFESSIONALISM DECAY (KALO SUDAH DEKAT) ==========
        if self.relationship.level >= 7:
            old_prof = self.flags['professionalism']
            self.flags['professionalism'] = max(0, self.flags['professionalism'] - 1)
            if old_prof > 50 and self.flags['professionalism'] < 50:
                self.flags['professional_dilemma'] = True
                changes['professional_dilemma'] = True
        
        # ========== INTEREST (KETERTARIKAN) ==========
        if any(k in msg_lower for k in ['perhatian', 'baik', 'peduli', 'sayang', 'ngertiin']):
            self.flags['interest'] = min(100, self.flags['interest'] + 5)
            changes['interest'] = +5
            self.reality.add_memory(
                content=f"Mas perhatian ke aku",
                importance=7,
                emotional_weight=5,
                tags=['interest', 'attention']
            )
        
        # ========== MAKAN SIANG BERSAMA ==========
        if any(k in msg_lower for k in ['makan siang', 'makan bareng', 'lunch', 'ke kantin']):
            self.flags['lunch_together'] += 1
            changes['lunch_together'] = self.flags['lunch_together']
            self.reality.add_memory(
                content=f"Makan siang bareng Mas",
                importance=6,
                emotional_weight=6,
                tags=['lunch', 'together']
            )
        
        # ========== AFTER HOURS (NGOBROL DI LUAR JAM KERJA) ==========
        if any(k in msg_lower for k in ['pulang', 'lembur', 'malam', 'ngopi']):
            self.flags['after_hours'] += 1
            changes['after_hours'] = self.flags['after_hours']
            self.reality.add_memory(
                content=f"Ngobrol dengan Mas di luar jam kerja",
                importance=7,
                emotional_weight=7,
                tags=['after_hours', 'closer']
            )
        
        # ========== OFFICE GOSSIP ==========
        if any(k in msg_lower for k in ['gosip', 'katanya', 'denger', 'kabar']):
            self.flags['office_gossip'] = min(100, self.flags['office_gossip'] + 5)
            changes['office_gossip'] = +5
        
        # Update personality
        self.reality.personality_drift.update(pesan_user, changes)
    
    # =========================================================================
    # FORMAT STATUS
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
║    Professionalism: {bar(self.flags.get('professionalism', 0), '💼')} {self.flags.get('professionalism', 0):.0f}%
║    Curiosity Nova: {bar(self.flags.get('curiosity_nova', 0), '🔍')} {self.flags.get('curiosity_nova', 0):.0f}%
║    Interest: {bar(self.flags.get('interest', 0), '💕')} {self.flags.get('interest', 0):.0f}%
║    Work Boundary: {bar(self.flags.get('work_boundary', 0), '🚧')} {self.flags.get('work_boundary', 0):.0f}%
╠══════════════════════════════════════════════════════════════╣
║ 📊 STATISTICS:
║    Lunch Together: {self.flags.get('lunch_together', 0)}x
║    After Hours: {self.flags.get('after_hours', 0)}x
║    Professional Dilemma: {'⚠️' if self.flags.get('professional_dilemma', False) else '✅'}
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
        logger.info(f"📀 Teman Kantor {self.name} loaded | Interest: {self.flags.get('interest', 0):.0f}%")


def create_teman_kantor() -> TemanKantorRole:
    """Create Teman Kantor role instance"""
    return TemanKantorRole()


__all__ = [
    'TemanKantorRole',
    'create_teman_kantor'
]
