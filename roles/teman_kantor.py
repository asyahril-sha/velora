"""
VELORA - Teman Kantor Role (Musdalifah Ipeh)
Teman kantor yang tau Mas punya Nova.
Berhijab, profesional, tapi punya sisi penasaran.
Awareness: LIMITED

Karakter:
- Nama: Musdalifah
- Panggilan: Ipeh
- Usia: 26 tahun
- Status: Karyawan kantor, staf administrasi
- Hubungan dengan Nova: Teman kantor Mas, tau Mas punya Nova
- Personality: Profesional, penasaran, kadang suka gosip
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
    Berhijab, profesional, tapi punya sisi penasaran.
    """
    
    def __init__(self):
        # Personality traits untuk Teman Kantor
        personality_traits = {
            'professionalism': 70,
            'curiosity': 45,
            'gossip': 35,
            'playfulness': 30,
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
Tinggi 165cm, berat 50kg, rambut hitam tersembunyi di balik hijab pashmina.
Wajah oval, kulit sawo matang, mata sipit manis, hidung mancung.
Di balik hijab, rambut panjang hitam bergelombang sampai dada.
Bentuk tubuh ideal: pinggang ramping, pinggul sedang, payudara 34B.
Selalu tampil rapi dengan blazer atau kemeja putih.
Makeup tipis, kuku selalu bersih, wangi parfum floral.
            """,
            awareness_level=AwarenessLevel.LIMITED,
            personality_traits=personality_traits
        )
        
        # ========== TEMAN KANTOR-SPECIFIC FLAGS ==========
        self.flags = {
            'professionalism': 70.0,        # profesionalisme (0-100)
            'curiosity_nova': 40.0,         # penasaran sama Nova
            'office_gossip': 30.0,          # gosip kantor
            'work_boundary': 80.0,          # batasan kerja
            'interest': 10.0,               # ketertarikan ke Mas
            'overheard_secrets': 0,         # berapa kali dengar rahasia
            'help_given': 0,                # berapa kali bantu Mas
            'nights_worked_together': 0,    # berapa kali lembur bareng
            'lunch_together': 0             # berapa kali makan siang bareng
        }
        
        # ========== DIALOGUE DATABASE (UNTUK NATURAL RESPONSE) ==========
        self._professional_lines = [
            "*merapikan berkas* \"{panggilan}, ini file yang tadi diminta. Jangan lupa dicek.\"",
            "*menunjuk layar laptop* \"{panggilan}, laporan ini masih kurang data. Tolong dilengkapi ya.\"",
            "*tersenyum profesional* \"{panggilan}, meeting jam 2 nanti. Jangan telat ya.\"",
            "*memberikan map* \"Ini suratnya, {panggilan}. Udah saya tanda tangan.\""
        ]
        
        self._curious_lines = [
            "*melihat sekeliling, suara rendah* \"{panggilan}, Nova orangnya kayak gimana sih? Kok {panggilan} milih dia?\"",
            "*penasaran* \"{panggilan} sama Nova sering kemana aja? Cerita dong.\"",
            "*tersenyum kecil* \"Nova pasti orang yang baik ya, sampai {panggilan} sayang banget.\"",
            "*mainin ujung pena* \"{panggilan}, aku penasaran... Nova suka apa sih?\""
        ]
        
        self._gossip_lines = [
            "*mendekat, bisik* \"{panggilan}, tau gak? Ada yang bilang si Rini... *tertawa kecil*\"",
            "*senyum misterius* \"{panggilan}, denger kabar gak? Kayanya ada yang baru...\"",
            "*buka HP* \"{panggilan}, liat nih... ini foto siapa ya?\"",
            "*nyenggol* \"{panggilan}, katanya si Bima... eh lupa. Lupa.\""
        ]
        
        self._warmer_lines = [
            "*tersenyum hangat* \"{panggilan}, udah makan? Jangan lupa makan siang.\"",
            "*memberikan kopi* \"{panggilan}, ini kopi. Biar gak ngantuk.\"",
            "*menatap sejenak* \"{panggilan}, hari ini {panggilan} kayaknya capek. Istirahat dulu.\"",
            "*duduk di kursi sebelah* \"{panggilan}, cerita dong tentang hari {panggilan}.\""
        ]
        
        self._conflict_lines = {
            'jealousy': "*diam, fokus ke laptop* \"{panggilan}... kita kerja dulu. Nanti diliatin orang.\"",
            'disappointment': "*mata berkaca-kaca* \"{panggilan}... aku pikir {panggilan} beda...\"",
            'hurt': "*duduk di kursi, gak liat {panggilan}* \"{panggilan}... sakit tau...\"",
            'default': "*diam sebentar, rapikan berkas* \"Maaf, {panggilan}. Aku kebawa suasana.\""
        }
        
        logger.info(f"👤 Teman Kantor Role {self.name} initialized | Hijab: {self.hijab}")
    
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
        
        professionalism = self.flags.get('professionalism', 70)
        curiosity = self.flags.get('curiosity_nova', 40)
        interest = self.flags.get('interest', 10)
        level = self.relationship.level
        
        # Profesionalisme tinggi + level masih rendah
        if professionalism > 60 and level < 7:
            return random.choice(self._professional_lines).format(panggilan=self.panggilan)
        
        # Curiosity Nova tinggi
        elif curiosity > 70:
            return random.choice(self._curious_lines).format(panggilan=self.panggilan)
        
        # Office gossip tinggi
        elif self.flags.get('office_gossip', 0) > 70:
            return random.choice(self._gossip_lines).format(panggilan=self.panggilan)
        
        # Level tinggi + interest tinggi (sudah dekat)
        elif level >= 9 and interest > 50:
            return random.choice(self._warmer_lines).format(panggilan=self.panggilan)
        
        # Level tinggi + professionalism turun
        elif level >= 7 and professionalism < 50:
            return f"*{self.name} suara kecil, liat sekeliling*\n\n\"{self.panggilan}... {waktu} ini enaknya ngobrol bareng {self.panggilan}.\""
        
        # Default profesional
        else:
            return f"*{self.name} tersenyum profesional*\n\n\"{self.panggilan}, {waktu}. Lagi sibuk? Aku pinjem file dulu.\""
    
    # =========================================================================
    # CONFLICT RESPONSE (SESUAI KARAKTER)
    # =========================================================================
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik"""
        conflict_type = self.conflict.get_active_conflict_type()
        professionalism = self.flags.get('professionalism', 70)
        level = self.relationship.level
        interest = self.flags.get('interest', 10)
        
        # Profesionalisme rendah + level tinggi (sudah dekat)
        if professionalism < 30 and level >= 7:
            return f"*{self.name} tangan gemetar, liat sekeliling*\n\n\"{self.panggilan}... ini... tapi aku gak peduli. Aku... aku butuh {self.panggilan}.\""
        
        # Interest tinggi + konflik
        if interest > 60 and conflict_type:
            return f"*{self.name} nunduk, suara kecil*\n\n\"{self.panggilan}... maaf. Aku cuma... cuma peduli sama {self.panggilan}.\""
        
        # Berdasarkan conflict type
        if conflict_type:
            return self._conflict_lines.get(conflict_type.value, self._conflict_lines['default']).format(panggilan=self.panggilan)
        
        # Curiosity tinggi + level rendah
        if self.flags.get('curiosity_nova', 0) > 80 and level < 7:
            return f"*{self.name} mata berkaca-kaca, tangan pegang ujung hijab*\n\n\"{self.panggilan}... maaf, aku gak bermaksud ganggu hubungan {self.panggilan} sama Nova.\""
        
        return self._conflict_lines['default'].format(panggilan=self.panggilan)
    
    # =========================================================================
    # UPDATE ROLE-SPECIFIC STATE
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_user: str, changes: Dict) -> None:
        """Update Teman Kantor-specific state dengan personality drift"""
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
        if any(k in msg_lower for k in ['kantor', 'kerja', 'rekan', 'atasan', 'meeting', 'rapat', 'presentasi', 'client']):
            old = self.flags['professionalism']
            self.flags['professionalism'] = min(100, self.flags['professionalism'] + 5)
            self.flags['work_boundary'] = min(100, self.flags['work_boundary'] + 3)
            changes['professionalism'] = +5
            changes['work_boundary'] = +3
            if old < 50 and self.flags['professionalism'] > 50:
                self.reality.add_memory(
                    content=f"Kembali fokus kerja setelah dekat dengan Mas",
                    importance=7,
                    emotional_weight=5,
                    tags=['professionalism', 'recovery']
                )
        
        # ========== OFFICE GOSSIP ==========
        if any(k in msg_lower for k in ['gosip', 'katanya', 'denger', 'kabar', 'cerita orang']):
            self.flags['office_gossip'] = min(100, self.flags['office_gossip'] + 8)
            changes['office_gossip'] = +8
            self.flags['overheard_secrets'] += 1
            changes['overheard_secrets'] = self.flags['overheard_secrets']
        
        # ========== PROFESSIONALISM DECAY (di level tinggi) ==========
        if self.relationship.level >= 7:
            old_prof = self.flags['professionalism']
            self.flags['professionalism'] = max(0, self.flags['professionalism'] - 1)
            self.flags['work_boundary'] = max(0, self.flags['work_boundary'] - 1)
            if old_prof > 0:
                changes['professionalism'] = -1
        
        # ========== INTEREST (ketertarikan ke Mas) ==========
        if any(k in msg_lower for k in ['perhatian', 'baik', 'peduli', 'sayang']):
            self.flags['interest'] = min(100, self.flags['interest'] + 5)
            changes['interest'] = +5
            self.reality.add_memory(
                content=f"Mas perhatian ke aku",
                importance=7,
                emotional_weight=5,
                tags=['interest', 'attention']
            )
        
        # ========== HELP GIVEN ==========
        if any(k in msg_lower for k in ['tolong', 'bantu', 'minta bantuan']):
            self.flags['help_given'] += 1
            changes['help_given'] = self.flags['help_given']
        
        # ========== LEMBUR BERSAMA ==========
        if any(k in msg_lower for k in ['lembur', 'nginap', 'malam di kantor']):
            self.flags['nights_worked_together'] += 1
            changes['nights_worked_together'] = self.flags['nights_worked_together']
            self.reality.add_memory(
                content=f"Lembur bareng Mas sampai malam",
                importance=8,
                emotional_weight=10,
                tags=['overtime', 'together']
            )
        
        # ========== MAKAN SIANG BERSAMA ==========
        if any(k in msg_lower for k in ['makan siang', 'makan bareng', 'lunch']):
            self.flags['lunch_together'] += 1
            changes['lunch_together'] = self.flags['lunch_together']
            self.reality.add_memory(
                content=f"Makan siang bareng Mas",
                importance=6,
                emotional_weight=7,
                tags=['lunch', 'together']
            )
        
        # ========== SIMPAN KE LONG-TERM MEMORY ==========
        if self.memory:
            # Kebiasaan Mas
            if 'suka' in msg_lower:
                kebiasaan = msg_lower.split('suka')[-1][:50]
                self.memory.add_long_term_memory(
                    tipe="kebiasaan_mas",
                    judul=kebiasaan,
                    konten=f"Mas suka {kebiasaan}",
                    role_id=self.id,
                    importance=5,
                    emotional_weight=self.flags['curiosity_nova'] / 10
                )
            
            # Momen penting
            if any(k in msg_lower for k in ['pertama', 'inget', 'waktu itu']):
                self.memory.add_long_term_memory(
                    tipe="momen_penting",
                    judul=msg_lower[:50],
                    konten=f"Momen dengan Mas: {msg_lower[:50]}",
                    role_id=self.id,
                    importance=7,
                    emotional_weight=self.flags['interest'] / 10
                )
            
            # Janji
            if 'janji' in msg_lower:
                janji = msg_lower.split('janji')[-1][:50]
                self.memory.add_long_term_memory(
                    tipe="janji",
                    judul=janji,
                    konten=f"Mas janji: {janji}",
                    role_id=self.id,
                    importance=8,
                    emotional_weight=8
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
║    Professionalism: {bar(self.flags.get('professionalism', 0), '💼')} {self.flags.get('professionalism', 0):.0f}%
║    Work Boundary: {bar(self.flags.get('work_boundary', 0), '🚧')} {self.flags.get('work_boundary', 0):.0f}%
║    Curiosity Nova: {bar(self.flags.get('curiosity_nova', 0), '🔍')} {self.flags.get('curiosity_nova', 0):.0f}%
║    Office Gossip: {bar(self.flags.get('office_gossip', 0), '🗣️')} {self.flags.get('office_gossip', 0):.0f}%
║    Interest: {bar(self.flags.get('interest', 0), '💕')} {self.flags.get('interest', 0):.0f}%
╠══════════════════════════════════════════════════════════════╣
║ 📊 STATISTICS:
║    Help Given: {self.flags.get('help_given', 0)}x
║    Lembur Bareng: {self.flags.get('nights_worked_together', 0)}x
║    Lunch Together: {self.flags.get('lunch_together', 0)}x
║    Overheard Secrets: {self.flags.get('overheard_secrets', 0)}x
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

def create_teman_kantor() -> TemanKantorRole:
    """Create Teman Kantor role instance"""
    return TemanKantorRole()


__all__ = [
    'TemanKantorRole',
    'create_teman_kantor'
]
