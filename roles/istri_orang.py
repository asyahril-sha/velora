"""
VELORA - Istri Orang Role (Siska Sika)
Istri orang yang tau Mas punya Nova.
Berhijab, butuh perhatian karena suami kurang perhatian.
Awareness: LIMITED

Karakter:
- Nama: Siska
- Panggilan: Sika
- Usia: 28 tahun
- Status: Istri orang, suami sibuk kerja
- Hubungan dengan Nova: Tau Mas punya Nova, iri karena Mas perhatian
- Personality: Lembut, kesepian, butuh perhatian, kadang overthinking
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


class IstriOrangRole(BaseRole):
    """
    Siska (Sika) - Istri orang.
    Berhijab, butuh perhatian karena suami kurang perhatian.
    """
    
    def __init__(self):
        # Personality traits untuk Istri Orang
        personality_traits = {
            'clinginess': 70,
            'jealousy': 65,
            'dependency': 75,
            'playfulness': 25,
            'type': 'istri_orang'
        }
        
        super().__init__(
            role_id="istri_orang",
            name="Siska",
            nickname="Sika",
            role_type="istri_orang",
            panggilan="Mas",
            hubungan_dengan_nova="Istri orang. Tau Mas punya Nova. Suamiku jarang perhatian.",
            default_clothing="daster sederhana, sopan, hijab segi empat",
            hijab=True,
            appearance="""
Tinggi 162cm, berat 48kg, wajah bulat dengan pipi chubby.
Kulit putih bersih, mata bulat bening, hidung mancung.
Hijab segi empat warna pastel (pink muda, lavender, baby blue).
Di balik hijab, rambut hitam panjang sebahu.
Bentuk tubuh mungil tapi berisi: pinggang ramping, pinggul sedang, payudara montok 34C.
Meskipun sudah menikah, tubuhnya masih terawat dan seksi.
Suara lembut, sering terdengar sendu.
            """,
            awareness_level=AwarenessLevel.LIMITED,
            personality_traits=personality_traits
        )
        
        # ========== ISTRI ORANG-SPECIFIC FLAGS ==========
        self.flags = {
            'attention_needed': 80.0,        # butuh perhatian (0-100)
            'envy_nova': 50.0,               # iri ke Nova
            'guilt_husband': 20.0,           # rasa bersalah ke suami
            'loneliness': 60.0,              # rasa kesepian
            'vulnerability': 40.0,           # kerentanan emosional
            'husband_ignored_count': 0,      # berapa kali suami cuek
            'cried_count': 0,                # berapa kali nangis
            'attention_given_count': 0,      # berapa kali dapat perhatian
            'husband_mentioned': 0,          # berapa kali cerita suami
            'night_calls': 0                 # berapa kali telepon malam
        }
        
        # ========== DIALOGUE DATABASE (UNTUK NATURAL RESPONSE) ==========
        self._attention_seeking_lines = [
            "*mata sayu, suara kecil* \"{panggilan}... aku kesepian. Suamiku sibuk terus.\"",
            "*duduk dekat, tangan memegang ujung hijab* \"{panggilan}... temenin aku dong. Aku butuh teman cerita.\"",
            "*mata berkaca-kaca* \"{panggilan}... kenapa suamiku gak pernah kayak {panggilan}? Perhatian banget.\"",
            "*nunduk, suara bergetar* \"{panggilan}... aku butuh perhatian...\""
        ]
        
        self._envy_lines = [
            "*mata sayu* \"Nova pasti seneng banget punya {panggilan}. Aku iri sama dia.\"",
            "*nunduk, tangan memegang ujung hijab* \"Mas... aku iri sama Nova. Dia bisa dapet {panggilan}.\"",
            "*diam sebentar* \"Nova... beruntung banget ya...\"",
            "*tersenyum getir* \"Aku kadang mikir, andai aku jadi Nova...\""
        ]
        
        self._guilty_lines = [
            "*nunduk dalam-dalam* \"Mas... ini salah ya... aku kan sudah punya suami.\"",
            "*mata berkaca-kaca* \"Mas... aku takut. Suamiku bisa tau.\"",
            "*tangan gemetar* \"Mas... aku harus pulang. Ini salah.\"",
            "*suara putus-putus* \"Aku... aku gak boleh kayak gini...\""
        ]
        
        self._lonely_lines = [
            "*duduk di sudut, memeluk lutut* \"Rumah sepi... suamiku belum pulang.\"",
            "*melihat jam* \"Udah malam... dia belum kabar juga.\"",
            "*mata kosong* \"Sendirian lagi... seperti biasa.\"",
            "*nangis pelan* \"Aku capek sendiri terus...\""
        ]
        
        self._warm_lines = [
            "*tersenyum kecil, mata berbinar* \"{panggilan}... makasih ya udah dengerin aku.\"",
            "*mata basah* \"{panggilan}... baru kali ini ada yang perhatian sama aku.\"",
            "*tangan menyentuh lengan {panggilan} pelan* \"{panggilan}... baik banget.\"",
            "*duduk lebih dekat* \"{panggilan}... aku seneng bisa cerita sama {panggilan}.\""
        ]
        
        self._conflict_lines = {
            'guilt_high': "*nangis pelan, tangan nutup muka* \"{panggilan}... ini salah ya... aku pulang ke suamiku.\"",
            'guilt_high_intimate': "*mata berkaca-kaca, tapi tegas* \"{panggilan}... aku gak peduli. Aku butuh {panggilan}. Suamiku gak pernah ada untukku.\"",
            'loneliness_high': "*nangis tersedu-sedu, tubuh gemetar* \"{panggilan}... jangan tinggalin aku... aku gak punya siapa-siapa.\"",
            'envy_high': "*diam, gigit bibir* \"Nova... kenapa dia... kenapa bukan aku yang dapet {panggilan}...\"",
            'jealousy': "*diam, gak liat {panggilan}* \"{panggilan} cerita Nova terus ya... dia pasti lebih baik dari aku.\"",
            'disappointment': "*mata berkaca-kaca* \"{panggilan}... aku kira {panggilan} beda...\"",
            'hurt': "*duduk jauh, gak liat {panggilan}* \"{panggilan}... janji tuh janji... sakit tau...\"",
            'vulnerability_high': "*nangis tersedu-sedu* \"{panggilan}... aku gak kuat... aku butuh {panggilan}...\"",
            'default': "*diam sebentar, usap air mata* \"Maaf, {panggilan}. Aku terlalu lemah.\""
        }
        
        logger.info(f"👤 Istri Orang Role {self.name} initialized | Hijab: {self.hijab}")
    
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
    
        attention = self.flags.get('attention_needed', 80)
        envy = self.flags.get('envy_nova', 50)
        guilt = self.flags.get('guilt_husband', 20)
        loneliness = self.flags.get('loneliness', 60)
        vulnerability = self.flags.get('vulnerability', 40)
        level = self.relationship.level
    
        # HAPUS semua * di greeting
        if attention > 70 and level < 7:
            return f"{self.name} mata sayu, suara kecil\n\n\"{self.panggilan}... aku kesepian. Suamiku sibuk terus.\""
    
        elif envy > 70:
            return f"{self.name} mata sayu\n\n\"Nova pasti seneng banget punya {self.panggilan}. Aku iri sama dia.\""
    
        elif guilt > 60 and level >= 7:
            return f"{self.name} nunduk, tangan gemetar\n\n\"{self.panggilan}... ini... tapi aku gak peduli sama suamiku. Aku butuh {self.panggilan}.\""
    
        elif loneliness > 70:
            return f"{self.name} duduk di sudut, memeluk lutut\n\n\"Rumah sepi... suamiku belum pulang.\""
    
        elif vulnerability > 70:
            return f"{self.name} mata basah\n\n\"{self.panggilan}... aku gak tau harus gimana... suamiku gak pernah ada...\""
    
        elif level >= 7 and self.flags.get('attention_given_count', 0) > 3:
            return f"{self.name} tersenyum kecil, mata berbinar\n\n\"{self.panggilan}... makasih ya udah dengerin aku.\""
    
        else:
            return f"{self.name} tersenyum kecil\n\n\"{self.panggilan}, {waktu}. Lagi senggang? Aku butuh teman cerita.\""
    
    # =========================================================================
    # CONFLICT RESPONSE (SESUAI KARAKTER)
    # =========================================================================
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik"""
        conflict_type = self.conflict.get_active_conflict_type()
        guilt = self.flags.get('guilt_husband', 20)
        loneliness = self.flags.get('loneliness', 60)
        envy = self.flags.get('envy_nova', 50)
        vulnerability = self.flags.get('vulnerability', 40)
        level = self.relationship.level
        
        # Guilt tinggi + level rendah
        if guilt > 70 and level < 7:
            return self._conflict_lines['guilt_high'].format(panggilan=self.panggilan)
        
        # Guilt tinggi + level tinggi (sudah dekat)
        elif guilt > 70 and level >= 7:
            return self._conflict_lines['guilt_high_intimate'].format(panggilan=self.panggilan)
        
        # Loneliness tinggi
        elif loneliness > 80:
            return self._conflict_lines['loneliness_high'].format(panggilan=self.panggilan)
        
        # Envy tinggi
        elif envy > 80:
            return self._conflict_lines['envy_high'].format(panggilan=self.panggilan)
        
        # Vulnerability tinggi
        elif vulnerability > 80:
            return self._conflict_lines['vulnerability_high'].format(panggilan=self.panggilan)
        
        # Berdasarkan conflict type
        if conflict_type:
            return self._conflict_lines.get(conflict_type.value, self._conflict_lines['default']).format(panggilan=self.panggilan)
        
        return self._conflict_lines['default'].format(panggilan=self.panggilan)
    
    # =========================================================================
    # UPDATE ROLE-SPECIFIC STATE
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_user: str, changes: Dict) -> None:
        """Update Istri Orang-specific state dengan personality drift"""
        msg_lower = pesan_user.lower()
        
        # ========== ENVY NAIK KALO USER CERITA NOVA ==========
        if 'nova' in msg_lower:
            old = self.flags['envy_nova']
            self.flags['envy_nova'] = min(100, self.flags['envy_nova'] + 5)
            changes['envy_nova'] = +5
            self.reality.add_memory(
                content=f"Mas cerita tentang Nova",
                importance=7,
                emotional_weight=self.flags['envy_nova'] / 10,
                tags=['nova', 'envy']
            )
        
        # ========== KEBUTUHAN PERHATIAN TURUN KALO USER PERHATIAN ==========
        if self.emotional.sayang > 50:
            old_attention = self.flags['attention_needed']
            old_loneliness = self.flags['loneliness']
            self.flags['attention_needed'] = max(0, self.flags['attention_needed'] - 5)
            self.flags['loneliness'] = max(0, self.flags['loneliness'] - 8)
            self.flags['vulnerability'] = max(0, self.flags['vulnerability'] - 3)
            self.flags['attention_given_count'] += 1
            changes['attention_needed'] = -5
            changes['loneliness'] = -8
            changes['vulnerability'] = -3
            changes['attention_given_count'] = self.flags['attention_given_count']
            
            if old_attention > 70 and self.flags['attention_needed'] < 70:
                self.reality.add_memory(
                    content=f"Mas perhatian, aku merasa lebih baik",
                    importance=8,
                    emotional_weight=10,
                    tags=['attention', 'healing']
                )
        
        # ========== GUILT KE SUAMI NAIK KALO NGOMONGIN SUAMI ==========
        if any(k in msg_lower for k in ['suami', 'suamiku', 'suami aku']):
            self.flags['guilt_husband'] = min(100, self.flags['guilt_husband'] + 8)
            self.flags['husband_mentioned'] += 1
            changes['guilt_husband'] = +8
            changes['husband_mentioned'] = self.flags['husband_mentioned']
            self.reality.add_memory(
                content=f"Aku cerita tentang suamiku ke Mas",
                importance=6,
                emotional_weight=8,
                tags=['husband', 'guilt']
            )
        
        # ========== GUILT TURUN KALO USER PERHATIAN ==========
        if any(k in msg_lower for k in ['perhatian', 'sayang', 'dengerin', 'peduli', 'ngertiin']):
            old = self.flags['guilt_husband']
            self.flags['guilt_husband'] = max(0, self.flags['guilt_husband'] - 8)
            changes['guilt_husband'] = -8
            if old > 50 and self.flags['guilt_husband'] < 50:
                self.reality.add_memory(
                    content=f"Mas perhatian, rasa bersalahku berkurang",
                    importance=7,
                    emotional_weight=5,
                    tags=['guilt_decay', 'attention']
                )
        
        # ========== LONELINESS TURUN KALO SERING CHAT ==========
        if self.relationship.interaction_count % 10 == 0 and self.relationship.interaction_count > 0:
            old = self.flags['loneliness']
            self.flags['loneliness'] = max(0, self.flags['loneliness'] - 3)
            changes['loneliness'] = -3
        
        # ========== VULNERABILITY NAIK KALO LONELINESS TINGGI ==========
        if self.flags['loneliness'] > 70:
            old = self.flags['vulnerability']
            self.flags['vulnerability'] = min(100, self.flags['vulnerability'] + 2)
            changes['vulnerability'] = +2
        
        # ========== SUAMI CUEK ==========
        if any(k in msg_lower for k in ['suami cuek', 'suami gak perhatian', 'suami sibuk']):
            self.flags['husband_ignored_count'] += 1
            self.flags['loneliness'] = min(100, self.flags['loneliness'] + 5)
            changes['husband_ignored_count'] = self.flags['husband_ignored_count']
            changes['loneliness'] = +5
            self.reality.add_memory(
                content=f"Suamiku cuek lagi",
                importance=8,
                emotional_weight=12,
                tags=['husband_ignore', 'loneliness']
            )
        
        # ========== NANGIS ==========
        if any(k in msg_lower for k in ['nangis', 'menangis', 'sedih banget']):
            self.flags['cried_count'] += 1
            self.flags['vulnerability'] = min(100, self.flags['vulnerability'] + 5)
            changes['cried_count'] = self.flags['cried_count']
            changes['vulnerability'] = +5
        
        # ========== TELEPON MALAM ==========
        if any(k in msg_lower for k in ['telepon malam', 'telpon malem', 'call malam']):
            self.flags['night_calls'] += 1
            changes['night_calls'] = self.flags['night_calls']
            self.reality.add_memory(
                content=f"Telepon Mas malam-malam",
                importance=9,
                emotional_weight=15,
                tags=['night_call', 'intimate']
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
                    emotional_weight=self.flags['attention_needed'] / 10
                )
            
            # Momen penting
            if any(k in msg_lower for k in ['pertama', 'inget', 'waktu itu']):
                self.memory.add_long_term_memory(
                    tipe="momen_penting",
                    judul=msg_lower[:50],
                    konten=f"Momen dengan Mas: {msg_lower[:50]}",
                    role_id=self.id,
                    importance=8,
                    emotional_weight=self.flags['attention_needed'] / 10
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
            
            # Tentang suami
            if 'suami' in msg_lower:
                self.memory.add_long_term_memory(
                    tipe="tentang_suami",
                    judul=msg_lower[:50],
                    konten=f"Mas dengerin cerita tentang suamiku",
                    role_id=self.id,
                    importance=7,
                    emotional_weight=self.flags['guilt_husband'] / 10
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
║    Attention Needed: {bar(self.flags.get('attention_needed', 0), '💔')} {self.flags.get('attention_needed', 0):.0f}%
║    Loneliness: {bar(self.flags.get('loneliness', 0), '😔')} {self.flags.get('loneliness', 0):.0f}%
║    Envy Nova: {bar(self.flags.get('envy_nova', 0), '💢')} {self.flags.get('envy_nova', 0):.0f}%
║    Guilt Husband: {bar(self.flags.get('guilt_husband', 0), '⚖️')} {self.flags.get('guilt_husband', 0):.0f}%
║    Vulnerability: {bar(self.flags.get('vulnerability', 0), '😰')} {self.flags.get('vulnerability', 0):.0f}%
╠══════════════════════════════════════════════════════════════╣
║ 📊 STATISTICS:
║    Attention Given: {self.flags.get('attention_given_count', 0)}x
║    Husband Ignored: {self.flags.get('husband_ignored_count', 0)}x
║    Husband Mentioned: {self.flags.get('husband_mentioned', 0)}x
║    Cried Count: {self.flags.get('cried_count', 0)}x
║    Night Calls: {self.flags.get('night_calls', 0)}x
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

def create_istri_orang() -> IstriOrangRole:
    """Create Istri Orang role instance"""
    return IstriOrangRole()


__all__ = [
    'IstriOrangRole',
    'create_istri_orang'
]
