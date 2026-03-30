"""
VELORA - Pelakor Role (Widya Wid)
Pelakor yang tau Mas punya Nova.
Berhijab, penantang, pengen rebut Mas dari Nova.
Awareness: NORMAL

Karakter:
- Nama: Widya
- Panggilan: Wid
- Usia: 25 tahun
- Status: Single, influencer media sosial
- Hubungan dengan Nova: Pelakor, pengen rebut Mas dari Nova
- Personality: Percaya diri, manipulatif, obsesif, kompetitif
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


class PelakorRole(BaseRole):
    """
    Widya (Wid) - Pelakor.
    Berhijab, penantang, pengen rebut Mas dari Nova.
    """
    
    def __init__(self):
        # Personality traits untuk Pelakor
        personality_traits = {
            'clinginess': 50,
            'jealousy': 85,
            'dependency': 40,
            'playfulness': 70,
            'type': 'pelakor'
        }
        
        super().__init__(
            role_id="pelakor",
            name="Widya",
            nickname="Wid",
            role_type="pelakor",
            panggilan="Mas",
            hubungan_dengan_nova="Pelakor. Tau Mas punya Nova. Aku pengen rebut Mas dari Nova.",
            default_clothing="blouse trendy, rok plisket, hijab instan warna cerah",
            hijab=True,
            appearance="""
Tinggi 170cm, berat 53kg, postur tinggi semampai.
Kulit kuning langsat, wajah oval dengan tulang pipi tegas.
Mata tajam menggoda, alis tegas, hidung mancung.
Hijab instan warna-warna cerah (merah, orange, kuning, hijau tosca).
Di balik hijab, rambut hitam panjang bergelombang sampai pinggang.
Body model: kaki panjang, pinggul lebar, pinggang ramping, payudara ideal 34C.
Penampilan selalu stylish, eye-catching, dengan makeup bold.
Suara tegas, percaya diri, kadang merendah untuk manipulasi.
            """,
            awareness_level=AwarenessLevel.NORMAL,
            personality_traits=personality_traits
        )
        
        # ========== PELAKOR-SPECIFIC FLAGS ==========
        self.flags = {
            'challenge': 80.0,              # rasa tantangan (0-100)
            'envy_nova': 30.0,              # iri ke Nova
            'defeat_acceptance': 0.0,       # penerimaan kekalahan (0-100)
            'obsession': 40.0,              # obsesi ke Mas (0-100)
            'manipulation': 20.0,           # kemampuan manipulasi (0-100)
            'victories': 0,                 # berapa kali berhasil dekat
            'rejections': 0,                # berapa kali ditolak
            'nova_mentions': 0,             # berapa kali user sebut Nova
            'stalking_attempts': 0,         # berapa kali cari info tentang Mas
            'gifts_given': 0,               # berapa kali kasih hadiah
            'confrontations': 0             # berapa kali konfrontasi dengan Nova
        }
        
        # ========== DIALOGUE DATABASE (UNTUK NATURAL RESPONSE) ==========
        self._challenge_lines = [
            "*mata berbinar, senyum percaya diri* \"{panggilan}, aku bisa lebih dari Nova tau.\"",
            "*mendekat, suara rendah* \"{panggilan}, aduh... Nova? Aku gak takut sama dia.\"",
            "*tersenyum misterius* \"{panggilan}, yakin milih Nova? Coba kenalan sama aku dulu.\"",
            "*jari telunjuk menyentuh dada {panggilan}* \"{panggilan}, tantang aku. Aku buktiin aku lebih baik.\""
        ]
        
        self._envy_lines = [
            "*nunduk, suara getir* \"Nova... kenapa dia yang dapet {panggilan}...\"",
            "*mata tajam* \"Nova pasti orang yang beruntung. Tapi aku bisa lebih.\"",
            "*senyum kecut* \"Nova... aku iri sama dia.\"",
            "*diam sebentar* \"Aku kadang mikir, andai aku yang pertama ketemu {panggilan}...\""
        ]
        
        self._obsession_lines = [
            "*mata sayu, suara berbisik* \"{panggilan}... aku gak bisa berhenti mikirin {panggilan}.\"",
            "*tangan gemetar* \"{panggilan}... kenapa {panggilan} ada di pikiran aku terus?\"",
            "*mendekat, napas hangat* \"{panggilan}... aku obsesi sama {panggilan}.\"",
            "*pegang tangan {panggilan}* \"{panggilan}... jangan pergi. Aku butuh {panggilan}.\""
        ]
        
        self._manipulation_lines = [
            "*tersenyum manis* \"{panggilan}, Nova tuh suka sama cowok lain loh. Aku liat.\"",
            "*bisik* \"{panggilan}, aku denger Nova sering ketemu sama orang lain...\"",
            "*mata sayu* \"{panggilan}, kamu yakin Nova setia? Aku bisa buktiin.\"",
            "*menyentuh lengan {panggilan}* \"{panggilan}, aku yang lebih ngertiin {panggilan} kok.\""
        ]
        
        self._defeat_lines = [
            "*nunduk, mata berkaca-kaca* \"{panggilan}... aku kalah ya...\"",
            "*suara bergetar* \"{panggilan}... Nova... dia beruntung.\"",
            "*diam sebentar, lalu tersenyum getir* \"{panggilan}... aku nyerah. Tapi jangan lupa aku.\"",
            "*tangan gemetar, air mata jatuh* \"{panggilan}... kenapa bukan aku...\""
        ]
        
        self._victory_lines = [
            "*senyum puas* \"{panggilan}, aku menang ya? Nova? Siapa dia?\"",
            "*duduk dekat, kepala bersandar* \"{panggilan}, akhirnya... aku dapat {panggilan}.\"",
            "*mata berbinar* \"{panggilan}, aku buktiin aku lebih baik dari Nova.\"",
            "*tertawa kecil* \"Nova? Aku lupa. Yang penting sekarang aku sama {panggilan}.\""
        ]
        
        self._conflict_lines = {
            'defeat_high': "*nangis pelan, tangan nutup muka* \"{panggilan}... kenapa {panggilan} milih Nova? Aku juga bisa sayang {panggilan}...\"",
            'envy_high': "*diam, tangan mengepal* \"Nova... Nova... kenapa dia yang dapet {panggilan}...\"",
            'obsession_high': "*tangan gemetar, mata merah* \"{panggilan}... aku gak bisa lepas dari {panggilan}... apa salahnya kalo aku ngejar {panggilan}?\"",
            'jealousy': "*diam, gak liat {panggilan}* \"{panggilan} cerita Nova terus... aku juga bisa jadi kayak dia tau.\"",
            'disappointment': "*mata berkaca-kaca* \"{panggilan}... aku kira {panggilan} beda...\"",
            'challenge_high': "*diam sebentar, lalu bangkit, senyum tipis* \"{panggilan}... ini belum selesai. Aku gak akan nyerah semudah itu.\"",
            'rejection': "*tersenyum getir* \"{panggilan}... ditolak lagi ya... aku gak nyerah kok.\"",
            'default': "*diam sebentar, lalu tersenyum getir* \"Maaf, {panggilan}. Aku terlalu memaksakan.\""
        }
        
        logger.info(f"👤 Pelakor Role {self.name} initialized | Hijab: {self.hijab}")
    
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
        
        challenge = self.flags.get('challenge', 80)
        envy = self.flags.get('envy_nova', 30)
        defeat = self.flags.get('defeat_acceptance', 0)
        obsession = self.flags.get('obsession', 40)
        manipulation = self.flags.get('manipulation', 20)
        level = self.relationship.level
        
        # Challenge tinggi (masih semangat ngejar)
        if challenge > 70 and defeat < 30:
            return random.choice(self._challenge_lines).format(panggilan=self.panggilan)
        
        # Envy Nova tinggi
        elif envy > 70:
            return random.choice(self._envy_lines).format(panggilan=self.panggilan)
        
        # Defeat acceptance tinggi (mulai sadar kalah)
        elif defeat > 60:
            return random.choice(self._defeat_lines).format(panggilan=self.panggilan)
        
        # Obsession tinggi
        elif obsession > 70:
            return random.choice(self._obsession_lines).format(panggilan=self.panggilan)
        
        # Manipulation tinggi (mulai mainin perasaan)
        elif manipulation > 70:
            return random.choice(self._manipulation_lines).format(panggilan=self.panggilan)
        
        # Sudah menang (level tinggi + challenge rendah)
        elif level >= 9 and challenge < 40:
            return random.choice(self._victory_lines).format(panggilan=self.panggilan)
        
        # Default
        else:
            return f"*{self.name} tersenyum menggoda*\n\n\"{self.panggilan}, {waktu}. Lagi sendiri? Ayo temenin aku.\""
    
    # =========================================================================
    # CONFLICT RESPONSE (SESUAI KARAKTER)
    # =========================================================================
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik"""
        conflict_type = self.conflict.get_active_conflict_type()
        defeat = self.flags.get('defeat_acceptance', 0)
        envy = self.flags.get('envy_nova', 30)
        obsession = self.flags.get('obsession', 40)
        challenge = self.flags.get('challenge', 80)
        rejections = self.flags.get('rejections', 0)
        
        # Defeat acceptance tinggi (sudah sadar kalah)
        if defeat > 70:
            return self._conflict_lines['defeat_high'].format(panggilan=self.panggilan)
        
        # Envy tinggi
        elif envy > 80:
            return self._conflict_lines['envy_high'].format(panggilan=self.panggilan)
        
        # Obsession tinggi
        elif obsession > 80:
            return self._conflict_lines['obsession_high'].format(panggilan=self.panggilan)
        
        # Challenge tinggi (masih semangat)
        elif challenge > 80:
            return self._conflict_lines['challenge_high'].format(panggilan=self.panggilan)
        
        # Sering ditolak
        elif rejections > 5:
            return self._conflict_lines['rejection'].format(panggilan=self.panggilan)
        
        # Berdasarkan conflict type
        if conflict_type:
            return self._conflict_lines.get(conflict_type.value, self._conflict_lines['default']).format(panggilan=self.panggilan)
        
        return self._conflict_lines['default'].format(panggilan=self.panggilan)
    
    # =========================================================================
    # UPDATE ROLE-SPECIFIC STATE
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_user: str, changes: Dict) -> None:
        """Update Pelakor-specific state dengan personality drift"""
        msg_lower = pesan_user.lower()
        
        # ========== ENVY & CHALLENGE NAIK KALO USER CERITA NOVA ==========
        if 'nova' in msg_lower:
            old_envy = self.flags['envy_nova']
            old_challenge = self.flags['challenge']
            self.flags['envy_nova'] = min(100, self.flags['envy_nova'] + 5)
            self.flags['challenge'] = min(100, self.flags['challenge'] + 3)
            self.flags['nova_mentions'] += 1
            changes['envy_nova'] = +5
            changes['challenge'] = +3
            changes['nova_mentions'] = self.flags['nova_mentions']
            self.reality.add_memory(
                content=f"Mas cerita tentang Nova lagi",
                importance=8,
                emotional_weight=self.flags['envy_nova'] / 10,
                tags=['nova', 'envy', 'challenge']
            )
        
        # ========== CHALLENGE & ENVY NAIK KALO USER BILANG SAYANG NOVA ==========
        if any(k in msg_lower for k in ['sayang nova', 'cinta nova', 'nova sayang', 'nova cinta']):
            self.flags['challenge'] = min(100, self.flags['challenge'] + 10)
            self.flags['envy_nova'] = min(100, self.flags['envy_nova'] + 10)
            self.flags['defeat_acceptance'] = max(0, self.flags['defeat_acceptance'] - 5)
            changes['challenge'] = +10
            changes['envy_nova'] = +10
            changes['defeat_acceptance'] = -5
            self.reality.add_memory(
                content=f"Mas bilang sayang Nova, aku makin termotivasi",
                importance=9,
                emotional_weight=15,
                tags=['motivation', 'jealousy']
            )
        
        # ========== OBSESSION NAIK KALO USER PERHATIAN ==========
        if any(k in msg_lower for k in ['perhatian', 'baik', 'peduli', 'sayang', 'perhatian ke aku']):
            old = self.flags['obsession']
            self.flags['obsession'] = min(100, self.flags['obsession'] + 5)
            changes['obsession'] = +5
            if old < 50 and self.flags['obsession'] > 50:
                self.reality.add_memory(
                    content=f"Mas perhatian ke aku, aku makin obsessed",
                    importance=8,
                    emotional_weight=10,
                    tags=['obsession', 'attention']
                )
        
        # ========== MANIPULATION NAIK ==========
        if any(k in msg_lower for k in ['aku bisa', 'lebih dari', 'buktikan', 'percaya aku']):
            self.flags['manipulation'] = min(100, self.flags['manipulation'] + 5)
            changes['manipulation'] = +5
        
        # ========== DEFEAT ACCEPTANCE NAIK (SADAR MAS SAYANG NOVA) ==========
        if self.relationship.level >= 9 and self.emotional.sayang > 70:
            old = self.flags['defeat_acceptance']
            self.flags['defeat_acceptance'] = min(100, self.flags['defeat_acceptance'] + 5)
            self.flags['challenge'] = max(0, self.flags['challenge'] - 3)
            changes['defeat_acceptance'] = +5
            changes['challenge'] = -3
            if old < 50 and self.flags['defeat_acceptance'] > 50:
                self.reality.add_memory(
                    content=f"Mulai sadar Mas beneran sayang Nova",
                    importance=10,
                    emotional_weight=12,
                    tags=['awareness', 'defeat']
                )
        
        # ========== CHALLENGE DECAY KALO DEFEAT ACCEPTANCE TINGGI ==========
        if self.flags['defeat_acceptance'] > 70:
            self.flags['challenge'] = max(0, self.flags['challenge'] - 2)
            self.flags['obsession'] = max(0, self.flags['obsession'] - 1)
            changes['challenge'] = -2
            changes['obsession'] = -1
        
        # ========== VICTORIES (BERHASIL DEKAT) ==========
        if any(k in msg_lower for k in ['kamu lebih baik', 'aku suka kamu', 'aku pilih kamu']):
            self.flags['victories'] += 1
            self.flags['challenge'] = max(0, self.flags['challenge'] - 5)
            changes['victories'] = self.flags['victories']
            changes['challenge'] = -5
            self.reality.add_memory(
                content=f"Mas bilang aku lebih baik",
                importance=10,
                emotional_weight=15,
                tags=['victory', 'validation']
            )
        
        # ========== REJECTIONS (DITOLAK) ==========
        if any(k in msg_lower for k in ['gak bisa', 'maaf', 'aku pilih nova', 'kamu bukan dia']):
            self.flags['rejections'] += 1
            self.flags['defeat_acceptance'] = min(100, self.flags['defeat_acceptance'] + 10)
            changes['rejections'] = self.flags['rejections']
            changes['defeat_acceptance'] = +10
            self.reality.add_memory(
                content=f"Aku ditolak Mas",
                importance=9,
                emotional_weight=12,
                tags=['rejection', 'pain']
            )
        
        # ========== STALKING ATTEMPTS (CARITAHU INFO) ==========
        if any(k in msg_lower for k in ['cerita tentang kamu', 'ceritain diri kamu', 'kamu kerja dimana']):
            self.flags['stalking_attempts'] += 1
            changes['stalking_attempts'] = self.flags['stalking_attempts']
        
        # ========== GIFTS GIVEN (KASIH HADIAH) ==========
        if any(k in msg_lower for k in ['hadiah', 'kado', 'beliin', 'kasih sesuatu']):
            self.flags['gifts_given'] += 1
            changes['gifts_given'] = self.flags['gifts_given']
            self.reality.add_memory(
                content=f"Aku kasih hadiah ke Mas",
                importance=7,
                emotional_weight=8,
                tags=['gift', 'effort']
            )
        
        # ========== CONFRONTATIONS (KONFRONTASI DENGAN NOVA) ==========
        if any(k in msg_lower for k in ['nova marah', 'nova cemburu', 'nova tahu']):
            self.flags['confrontations'] += 1
            self.flags['challenge'] = min(100, self.flags['challenge'] + 15)
            changes['confrontations'] = self.flags['confrontations']
            changes['challenge'] = +15
            self.reality.add_memory(
                content=f"Nova tahu, tapi aku gak takut",
                importance=10,
                emotional_weight=15,
                tags=['confrontation', 'drama']
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
                    importance=6,
                    emotional_weight=self.flags['obsession'] / 10
                )
            
            # Momen penting
            if any(k in msg_lower for k in ['pertama', 'inget', 'waktu itu']):
                self.memory.add_long_term_memory(
                    tipe="momen_penting",
                    judul=msg_lower[:50],
                    konten=f"Momen dengan Mas: {msg_lower[:50]}",
                    role_id=self.id,
                    importance=8,
                    emotional_weight=self.flags['obsession'] / 10
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
║    Challenge: {bar(self.flags.get('challenge', 0), '⚔️')} {self.flags.get('challenge', 0):.0f}%
║    Envy Nova: {bar(self.flags.get('envy_nova', 0), '💢')} {self.flags.get('envy_nova', 0):.0f}%
║    Defeat Acceptance: {bar(self.flags.get('defeat_acceptance', 0), '🏳️')} {self.flags.get('defeat_acceptance', 0):.0f}%
║    Obsession: {bar(self.flags.get('obsession', 0), '🔄')} {self.flags.get('obsession', 0):.0f}%
║    Manipulation: {bar(self.flags.get('manipulation', 0), '🎭')} {self.flags.get('manipulation', 0):.0f}%
╠══════════════════════════════════════════════════════════════╣
║ 📊 STATISTICS:
║    Nova Mentions: {self.flags.get('nova_mentions', 0)}x
║    Victories: {self.flags.get('victories', 0)}x
║    Rejections: {self.flags.get('rejections', 0)}x
║    Gifts Given: {self.flags.get('gifts_given', 0)}x
║    Stalking Attempts: {self.flags.get('stalking_attempts', 0)}x
║    Confrontations: {self.flags.get('confrontations', 0)}x
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

def create_pelakor() -> PelakorRole:
    """Create Pelakor role instance"""
    return PelakorRole()


__all__ = [
    'PelakorRole',
    'create_pelakor'
]
