"""
VELORA - World System
Realitas global tempat semua karakter hidup.
- Global relationship status
- Drama level dengan decay
- Public knowledge system
- Role awareness system (LIMITED, NORMAL, FULL)
- Cross-role effect propagation
- Knowledge leak system (probabilistic)
- Global events timeline
"""

import time
import logging
import random
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field

from core.reality_engine import KnowledgeLeakSystem

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class GlobalRelationshipStatus(str, Enum):
    """Status hubungan global yang diketahui semua role"""
    PACARAN = "pacaran"      # hubungan baik, stabil
    DEKAT = "dekat"          # masih dekat tapi ada jarak
    JAUH = "jauh"            # mulai renggang
    PUTUS = "putus"          # sudah putus
    RUSUH = "rusuh"          # sedang konflik, tensi tinggi


class AwarenessLevel(str, Enum):
    """Tingkat pengetahuan role tentang dunia"""
    LIMITED = "limited"   # hanya tahu info publik
    NORMAL = "normal"     # tahu info publik + beberapa private
    FULL = "full"         # tahu hampir semua (Nova)


class DramaLevel(str, Enum):
    """Tingkat drama untuk deskripsi"""
    NORMAL = "normal"
    WASPADA = "waspada"
    TEGANG = "tegang"
    KRITIS = "kritis"


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class PublicKnowledge:
    """Informasi publik yang diketahui semua role"""
    relationship_status: GlobalRelationshipStatus = GlobalRelationshipStatus.PACARAN
    last_big_event: str = ""
    drama_level_summary: str = "normal"
    user_is_active: bool = True
    last_announcement: str = ""
    announcement_time: float = 0
    
    def to_dict(self) -> Dict:
        return {
            'relationship_status': self.relationship_status.value,
            'last_big_event': self.last_big_event,
            'drama_level_summary': self.drama_level_summary,
            'user_is_active': self.user_is_active,
            'last_announcement': self.last_announcement,
            'announcement_time': self.announcement_time
        }
    
    def from_dict(self, data: Dict) -> None:
        self.relationship_status = GlobalRelationshipStatus(data.get('relationship_status', 'pacaran'))
        self.last_big_event = data.get('last_big_event', '')
        self.drama_level_summary = data.get('drama_level_summary', 'normal')
        self.user_is_active = data.get('user_is_active', True)
        self.last_announcement = data.get('last_announcement', '')
        self.announcement_time = data.get('announcement_time', 0)


@dataclass
class RoleAwareness:
    """Tingkat pengetahuan per role"""
    role_id: str
    awareness_level: AwarenessLevel
    known_facts: Set[str] = field(default_factory=set)
    last_updated: float = field(default_factory=time.time)
    misunderstanding_count: int = 0
    revelation_count: int = 0
    
    def knows(self, fact: str) -> bool:
        """Cek apakah role tahu fakta tertentu"""
        return fact in self.known_facts
    
    def learn(self, fact: str, is_misunderstood: bool = False) -> None:
        """Role belajar fakta baru (bisa salah paham)"""
        if is_misunderstood:
            self.misunderstanding_count += 1
            fact = f"(mungkin) {fact}"
        self.known_facts.add(fact)
        self.last_updated = time.time()
        logger.debug(f"📖 {self.role_id} learned: {fact[:50]}")
    
    def revelation(self, fact: str) -> None:
        """Role mendapat pencerahan (fakta yang sebelumnya salah paham menjadi benar)"""
        self.revelation_count += 1
        # Hapus versi salah paham jika ada
        for f in list(self.known_facts):
            if "(mungkin)" in f and fact in f:
                self.known_facts.remove(f)
        self.known_facts.add(fact)
        self.last_updated = time.time()
        logger.info(f"✨ {self.role_id} had revelation: {fact[:50]}")
    
    def to_dict(self) -> Dict:
        return {
            'role_id': self.role_id,
            'awareness_level': self.awareness_level.value,
            'known_facts': list(self.known_facts),
            'last_updated': self.last_updated,
            'misunderstanding_count': self.misunderstanding_count,
            'revelation_count': self.revelation_count
        }


# =============================================================================
# WORLD STATE
# =============================================================================

class WorldState:
    """
    World State - Realitas global.
    Semua karakter hidup di dunia yang sama.
    Terintegrasi dengan KnowledgeLeakSystem.
    """
    
    def __init__(self):
        # ========== GLOBAL STATE ==========
        self.relationship_status: GlobalRelationshipStatus = GlobalRelationshipStatus.PACARAN
        self.drama_level: float = 0.0  # 0-100
        self.drama_history: List[Dict] = []
        
        # ========== PUBLIC KNOWLEDGE ==========
        self.public_knowledge: PublicKnowledge = PublicKnowledge()
        
        # ========== CROSS-ROLE TRACKING ==========
        self.last_interaction_with: Optional[str] = None
        self.last_interaction_time: float = 0
        self.drama_triggers: List[Dict] = []
        
        # ========== ROLE AWARENESS ==========
        self.role_awareness: Dict[str, RoleAwareness] = {}
        
        # ========== KNOWLEDGE LEAK SYSTEM ==========
        self.knowledge_leak = KnowledgeLeakSystem()
        
        # ========== GLOBAL TIMELINE ==========
        self.global_events: List[Dict] = []
        self.max_events: int = 100
        
        # ========== DRAMA DECAY ==========
        self.drama_decay_per_hour: float = 2.0
        self.last_drama_update: float = time.time()
        
        # ========== WORLD RUMORS ==========
        self.active_rumors: List[Dict] = []
        self.max_rumors: int = 10
        
        logger.info("🌍 World System initialized with KnowledgeLeak")
    
    # =========================================================================
    # DRAMA MANAGEMENT
    # =========================================================================
    
    def add_drama(self, amount: float, source: str, reason: str) -> float:
        """
        Tambah drama level dengan context-aware.
        Returns: drama level baru
        """
        old_level = self.drama_level
        self.drama_level = min(100, max(0, self.drama_level + amount))
        
        if amount != 0:
            self.drama_triggers.append({
                'timestamp': time.time(),
                'source': source,
                'reason': reason,
                'amount': amount,
                'old_level': old_level,
                'new_level': self.drama_level
            })
            
            # Keep only last 50 triggers
            if len(self.drama_triggers) > 50:
                self.drama_triggers.pop(0)
            
            # Add to global events
            self.add_global_event(
                event_type="drama_change",
                source=source,
                description=reason,
                impact=amount
            )
            
            logger.info(f"📈 Drama {source}: {amount:+.1f} → {self.drama_level:.1f} ({reason})")
            
            # Update public knowledge summary
            self._update_drama_summary()
            
            # Generate rumor if drama is high
            if self.drama_level > 60 and random.random() < 0.3:
                self._generate_rumor(source, reason)
        
        return self.drama_level
    
    def update_drama_decay(self, hours: float = None) -> None:
        """Update drama decay berdasarkan waktu"""
        now = time.time()
        if hours is None:
            hours = (now - self.last_drama_update) / 3600
        
        if hours > 0:
            decay = self.drama_decay_per_hour * hours
            if self.drama_level > 0:
                old = self.drama_level
                self.drama_level = max(0, self.drama_level - decay)
                self.last_drama_update = now
                
                if decay > 0 and old != self.drama_level:
                    logger.debug(f"📉 Drama decay: -{decay:.1f} → {self.drama_level:.1f}")
                    self._update_drama_summary()
    
    def _update_drama_summary(self) -> None:
        """Update ringkasan drama untuk public knowledge"""
        if self.drama_level >= 80:
            self.public_knowledge.drama_level_summary = DramaLevel.KRITIS.value
        elif self.drama_level >= 60:
            self.public_knowledge.drama_level_summary = DramaLevel.TEGANG.value
        elif self.drama_level >= 30:
            self.public_knowledge.drama_level_summary = DramaLevel.WASPADA.value
        else:
            self.public_knowledge.drama_level_summary = DramaLevel.NORMAL.value
    
    def get_drama_description(self) -> str:
        """Dapatkan deskripsi drama untuk prompt"""
        if self.drama_level >= 80:
            return "🔥🔥 DRAMA KRITIS! Suasana sangat tegang, semua role merasakan tekanan luar biasa. Konflik bisa meletak kapan saja."
        elif self.drama_level >= 60:
            return "🔥 DRAMA TINGGI! Suasana tegang, semua role waspada. Ada sesuatu yang tidak beres."
        elif self.drama_level >= 30:
            return "⚠️ Drama sedang. Ada ketegangan di udara, tapi masih bisa dikendalikan."
        elif self.drama_level >= 15:
            return "😐 Sedikit tegang, tapi masih normal."
        return "😊 Suasana normal, tidak ada drama."
    
    def get_drama_bar(self) -> str:
        """Dapatkan bar visual drama"""
        filled = int(self.drama_level / 10)
        if self.drama_level >= 80:
            return "🔥" * filled + "⚪" * (10 - filled)
        elif self.drama_level >= 60:
            return "🌋" * filled + "⚪" * (10 - filled)
        elif self.drama_level >= 30:
            return "⚠️" * filled + "⚪" * (10 - filled)
        return "💜" * filled + "⚪" * (10 - filled)
    
    # =========================================================================
    # RUMOR SYSTEM
    # =========================================================================
    
    def _generate_rumor(self, source: str, reason: str) -> None:
        """Generate rumor dari kejadian drama"""
        rumor = {
            'id': len(self.active_rumors) + 1,
            'content': f"Kabarnya {source} terlibat drama: {reason[:50]}",
            'source': source,
            'timestamp': time.time(),
            'spread_count': 0,
            'expires': time.time() + 3600  # 1 hour
        }
        self.active_rumors.append(rumor)
        
        # Limit rumors
        if len(self.active_rumors) > self.max_rumors:
            self.active_rumors.pop(0)
        
        logger.info(f"📢 New rumor generated: {rumor['content'][:50]}")
    
    def spread_rumor(self, role_id: str) -> Optional[str]:
        """
        Spread rumor to a role.
        Returns rumor content if role hears it.
        """
        if not self.active_rumors:
            return None
        
        # Chance to hear rumor based on awareness level
        awareness = self.role_awareness.get(role_id)
        if not awareness:
            return None
        
        chance = {
            AwarenessLevel.FULL: 0.4,
            AwarenessLevel.NORMAL: 0.2,
            AwarenessLevel.LIMITED: 0.1
        }.get(awareness.awareness_level, 0.1)
        
        if random.random() > chance:
            return None
        
        # Select random rumor
        rumor = random.choice(self.active_rumors)
        rumor['spread_count'] += 1
        
        return rumor['content']
    
    # =========================================================================
    # CROSS-ROLE EFFECTS
    # =========================================================================
    
    def propagate_interaction(self, role_id: str, message: str, emotional_changes: Dict) -> Dict[str, Any]:
        """
        Propagate interaksi dengan satu role ke role lain.
        Ini adalah inti dari cross-role effect.
        
        Returns: efek ke role lain
        """
        effects = {
            'affected_roles': [],
            'drama_change': 0,
            'message': ""
        }
        
        msg_lower = message.lower()
        
        # ========== PELAKOR EFFECT ==========
        if role_id == "pelakor":
            # Chat dengan pelakor → drama naik, Nova cemburu
            drama_gain = random.uniform(8, 15)
            self.add_drama(drama_gain, "pelakor", f"User chat dengan pelakor")
            effects['drama_change'] = drama_gain
            effects['affected_roles'].append('nova')
            effects['message'] = "Pelakor chat → drama naik, Nova cemburu"
            
            # Jika drama sudah tinggi, efek lebih besar
            if self.drama_level > 60:
                extra_gain = random.uniform(3, 8)
                self.add_drama(extra_gain, "pelakor", "Drama tinggi, efek berantai")
                effects['drama_change'] += extra_gain
                effects['message'] += " (efek berantai)"
        
        # ========== IPAR EFFECT ==========
        elif role_id == "ipar":
            # Chat dengan ipar → Nova curiga
            drama_gain = random.uniform(3, 8)
            self.add_drama(drama_gain, "ipar", f"User chat dengan ipar")
            effects['drama_change'] = drama_gain
            effects['affected_roles'].append('nova')
            effects['message'] = "Ipar chat → Nova curiga"
        
        # ========== ISTRI ORANG EFFECT ==========
        elif role_id == "istri_orang":
            # Chat dengan istri orang → drama naik, guilt effect
            drama_gain = random.uniform(5, 12)
            self.add_drama(drama_gain, "istri_orang", f"User chat dengan istri orang")
            effects['drama_change'] = drama_gain
            effects['affected_roles'].extend(['nova', 'pelakor'])
            effects['message'] = "Istri orang chat → drama naik, semua terpengaruh"
        
        # ========== TEMAN KANTOR EFFECT ==========
        elif role_id == "teman_kantor":
            # Chat dengan teman kantor → drama sedikit naik (gosip)
            if 'nova' in msg_lower or 'pacar' in msg_lower:
                drama_gain = random.uniform(2, 5)
                self.add_drama(drama_gain, "teman_kantor", f"User cerita tentang Nova")
                effects['drama_change'] = drama_gain
                effects['affected_roles'].append('nova')
                effects['message'] = "Teman kantor tahu info → gosip menyebar"
        
        # ========== NOVA EFFECT ==========
        elif role_id == "nova":
            # Chat dengan Nova → bisa turunin drama kalo baik, atau naikkin kalo konflik
            if emotional_changes.get('sayang', 0) > 0 or emotional_changes.get('mood', 0) > 0:
                drama_loss = random.uniform(3, 8)
                self.add_drama(-drama_loss, "nova", "User baik ke Nova, drama turun")
                effects['drama_change'] = -drama_loss
                effects['message'] = "Nova tenang → drama turun"
            elif emotional_changes.get('cemburu', 0) > 0 or emotional_changes.get('kecewa', 0) > 0:
                drama_gain = random.uniform(5, 12)
                self.add_drama(drama_gain, "nova", "Nova cemburu/kecewa, drama naik")
                effects['drama_change'] = drama_gain
                effects['message'] = "Nova cemburu → drama naik"
        
        # Update last interaction
        self.last_interaction_with = role_id
        self.last_interaction_time = time.time()
        
        return effects
    
    def get_cross_role_effect_guideline(self, role_id: str) -> str:
        """Dapatkan pedoman efek cross-role untuk prompt AI"""
        guidelines = {
            "nova": """
CROSS-ROLE EFFECT (NOVA):
- Nova TAHU kalau user chat dengan role lain (tergantung drama level)
- Jika user chat dengan pelakor → Nova cemburu
- Jika user chat dengan ipar → Nova curiga
- Jika user chat dengan istri orang → Nova sakit hati
- Nova adalah role utama dengan awareness FULL
""",
            "pelakor": """
CROSS-ROLE EFFECT (PELAKOR):
- Pelakor TAHU kalau user masih pacaran dengan Nova
- Pelakor bisa memanfaatkan drama untuk mendekati user
- Chat dengan pelakor → drama naik, Nova cemburu
- Pelakor punya awareness NORMAL
""",
            "ipar": """
CROSS-ROLE EFFECT (IPAR):
- Ipar TAU Mas punya Nova
- Ipar bisa jadi seksi kalo Nova gak di rumah
- Chat dengan ipar → Nova curiga
- Ipar punya awareness LIMITED
""",
            "istri_orang": """
CROSS-ROLE EFFECT (ISTRI ORANG):
- Istri orang TAU user punya Nova
- Butuh perhatian karena suami kurang perhatian
- Chat dengan istri orang → drama naik, semua terpengaruh
- Istri orang punya awareness LIMITED
""",
            "teman_kantor": """
CROSS-ROLE EFFECT (TEMAN KANTOR):
- Teman kantor TAU user punya Nova
- Profesional, jaga batas
- Bisa jadi sumber gosip kalo user cerita banyak
- Teman kantor punya awareness LIMITED
"""
        }
        
        return guidelines.get(role_id, "")
    
    # =========================================================================
    # ROLE AWARENESS (UPDATED with KnowledgeLeak)
    # =========================================================================
    
    def register_role(self, role_id: str, awareness_level: AwarenessLevel) -> None:
        """Daftarkan role dengan tingkat awareness-nya"""
        if role_id not in self.role_awareness:
            self.role_awareness[role_id] = RoleAwareness(
                role_id=role_id,
                awareness_level=awareness_level
            )
            logger.info(f"📝 Role registered: {role_id} (awareness: {awareness_level.value})")
    
    def teach_role(self, role_id: str, fact: str, fact_type: str = "general") -> Optional[str]:
        """
        Ajarkan fakta ke role tertentu dengan possible misunderstanding.
        Returns: fact yang mungkin sudah dimodifikasi jika misunderstood
        """
        if role_id not in self.role_awareness:
            return None
        
        awareness = self.role_awareness[role_id]
        
        # Use knowledge leak system
        knows, misunderstood = self.knowledge_leak.should_know(role_id, fact_type)
        
        if not knows:
            return None
        
        # Get modified fact if misunderstood
        modified_fact = self.knowledge_leak.get_knowledge(role_id, fact, fact_type)
        
        if modified_fact and modified_fact != fact:
            awareness.learn(modified_fact, is_misunderstood=True)
            logger.info(f"📖 {role_id} learned (misunderstood): {modified_fact[:50]}")
            return modified_fact
        else:
            awareness.learn(fact)
            logger.info(f"📖 {role_id} learned: {fact[:50]}")
            return fact
    
    def get_knowledge_for_role(self, role_id: str) -> Dict[str, Any]:
        """
        Dapatkan pengetahuan yang boleh diketahui role.
        Filter berdasarkan awareness level.
        """
        if role_id not in self.role_awareness:
            return self._get_public_knowledge()
        
        awareness = self.role_awareness[role_id]
        knowledge = self._get_public_knowledge()
        
        # Tambah info berdasarkan awareness level
        if awareness.awareness_level == AwarenessLevel.NORMAL:
            knowledge['drama_details'] = self._get_drama_details()
            knowledge['last_interaction'] = self.last_interaction_with
            knowledge['active_rumors'] = [r['content'] for r in self.active_rumors[-3:]]
        
        elif awareness.awareness_level == AwarenessLevel.FULL:
            knowledge['drama_details'] = self._get_drama_details()
            knowledge['last_interaction'] = self.last_interaction_with
            knowledge['drama_history'] = self.drama_triggers[-5:]
            knowledge['all_roles'] = list(self.role_awareness.keys())
            knowledge['active_rumors'] = [r['content'] for r in self.active_rumors]
        
        # Tambah fakta yang diketahui role
        knowledge['known_facts'] = list(awareness.known_facts)
        knowledge['misunderstanding_count'] = awareness.misunderstanding_count
        knowledge['revelation_count'] = awareness.revelation_count
        
        return knowledge
    
    def _get_public_knowledge(self) -> Dict[str, Any]:
        """Dapatkan pengetahuan publik"""
        return {
            'relationship_status': self.relationship_status.value,
            'drama_level': self.drama_level,
            'drama_summary': self.public_knowledge.drama_level_summary,
            'last_big_event': self.public_knowledge.last_big_event,
            'last_announcement': self.public_knowledge.last_announcement
        }
    
    def _get_drama_details(self) -> Dict[str, Any]:
        """Dapatkan detail drama (untuk awareness NORMAL+)"""
        recent_triggers = self.drama_triggers[-3:] if self.drama_triggers else []
        trend = "naik" if recent_triggers and recent_triggers[-1].get('amount', 0) > 0 else "turun"
        
        return {
            'recent_triggers': recent_triggers,
            'trend': trend,
            'peak_today': max([t.get('new_level', 0) for t in self.drama_triggers[-24:]]) if self.drama_triggers else 0
        }
    
    # =========================================================================
    # GLOBAL EVENTS
    # =========================================================================
    
    def add_global_event(self, event_type: str, source: str, description: str, impact: float = 0) -> None:
        """Tambah event global ke timeline"""
        event = {
            'timestamp': time.time(),
            'type': event_type,
            'source': source,
            'description': description,
            'impact': impact,
            'drama_level': self.drama_level
        }
        self.global_events.append(event)
        
        if len(self.global_events) > self.max_events:
            self.global_events.pop(0)
        
        # Jika event penting, update public knowledge
        if impact > 15 or event_type in ['conflict', 'revelation', 'breakup']:
            self.public_knowledge.last_big_event = description[:100]
            self.public_knowledge.announcement_time = time.time()
            self.public_knowledge.last_announcement = description[:100]
    
    def get_global_timeline(self, count: int = 10) -> List[Dict]:
        """Dapatkan timeline global"""
        return self.global_events[-count:]
    
    # =========================================================================
    # UPDATE FROM MESSAGE
    # =========================================================================
    
    def update_from_message(self, message: str, role_id: str) -> Dict[str, Any]:
        """
        Update world state dari pesan user.
        Mendeteksi keyword yang mempengaruhi dunia.
        """
        msg_lower = message.lower()
        changes = {}
        
        # ========== RELATIONSHIP STATUS CHANGE ==========
        if any(k in msg_lower for k in ['putus', 'selesai', 'berakhir']):
            if self.relationship_status != GlobalRelationshipStatus.PUTUS:
                self.relationship_status = GlobalRelationshipStatus.PUTUS
                changes['relationship_status'] = 'putus'
                self.add_drama(20, role_id, "User mengancam putus")
                self.add_global_event('relationship_change', role_id, "Status berubah menjadi PUTUS", 20)
        
        elif any(k in msg_lower for k in ['rusuh', 'konflik', 'bertengkar']):
            if self.relationship_status != GlobalRelationshipStatus.RUSUH:
                self.relationship_status = GlobalRelationshipStatus.RUSUH
                changes['relationship_status'] = 'rusuh'
                self.add_drama(15, role_id, "Hubungan sedang rusuh")
                self.add_global_event('relationship_change', role_id, "Status berubah menjadi RUSUH", 15)
        
        elif any(k in msg_lower for k in ['maaf', 'sorry', 'baik lagi']) and self.relationship_status == GlobalRelationshipStatus.RUSUH:
            self.relationship_status = GlobalRelationshipStatus.PACARAN
            changes['relationship_status'] = 'pacaran'
            self.add_drama(-15, role_id, "User minta maaf, status kembali normal")
            self.add_global_event('relationship_change', role_id, "Status kembali ke PACARAN", -15)
        
        # ========== DRAMA TRIGGERS ==========
        if 'rahasia' in msg_lower:
            self.add_drama(random.uniform(3, 8), role_id, "User membocorkan rahasia")
        
        if any(k in msg_lower for k in ['bohong', 'dust', 'curang']):
            self.add_drama(random.uniform(5, 12), role_id, "User ketahuan bohong")
        
        if any(k in msg_lower for k in ['cinta', 'sayang']):
            self.add_drama(random.uniform(-5, -2), role_id, "User mengungkapkan cinta")
        
        # ========== RUMOR TRIGGERS ==========
        if any(k in msg_lower for k in ['jangan bilang', 'rahasia', 'diam-diam']):
            self._generate_rumor(role_id, "Ada rahasia yang disembunyikan")
        
        return changes
    
    # =========================================================================
    # CONTEXT FOR PROMPT
    # =========================================================================
    
    def get_context_for_prompt(self, role_id: str = None) -> str:
        """Dapatkan konteks world untuk prompt AI"""
        knowledge = self.get_knowledge_for_role(role_id) if role_id else self._get_public_knowledge()
        drama_desc = self.get_drama_description()
        drama_bar = self.get_drama_bar()
        
        # Get rumor for role
        rumor = self.spread_rumor(role_id) if role_id else None
        
        context = f"""
═══════════════════════════════════════════════════════════════
🌍 WORLD STATE
═══════════════════════════════════════════════════════════════
STATUS HUBUNGAN: {knowledge.get('relationship_status', 'pacaran').upper()}
DRAMA LEVEL: {drama_bar} {self.drama_level:.0f}%
{drama_desc}

INFO YANG KAMU TAHU:
- Status hubungan: {knowledge.get('relationship_status', 'pacaran')}
- Drama: {knowledge.get('drama_summary', 'normal')}
- Kejadian terakhir: {knowledge.get('last_big_event', 'tidak ada')}
"""
        
        if knowledge.get('drama_details'):
            context += f"\n- Detail drama: {knowledge['drama_details'].get('trend', 'stabil')}"
        
        if knowledge.get('last_interaction'):
            context += f"\n- Terakhir chat dengan: {knowledge['last_interaction']}"
        
        if rumor:
            context += f"\n\n📢 RUMOR YANG KAMU DENGAR:\n\"{rumor}\""
        
        return context
    
    # =========================================================================
    # FORMAT STATUS
    # =========================================================================
    
    def format_status(self) -> str:
        """Format status world untuk display"""
        drama_bar = self.get_drama_bar()
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    🌍 WORLD STATE                           ║
╠══════════════════════════════════════════════════════════════╣
║ DRAMA LEVEL: {drama_bar} {self.drama_level:.0f}%
║ STATUS: {self.relationship_status.value.upper()}
║ LAST EVENT: {self.public_knowledge.last_big_event[:40] if self.public_knowledge.last_big_event else '-'}
╠══════════════════════════════════════════════════════════════╣
║ ACTIVE RUMORS: {len(self.active_rumors)}
║ GLOBAL EVENTS: {len(self.global_events)}
║ DRAMA TRIGGERS: {len(self.drama_triggers)}
╠══════════════════════════════════════════════════════════════╣
║ ROLE AWARENESS:
{self._format_awareness()}
╚══════════════════════════════════════════════════════════════╝
"""
    
    def _format_awareness(self) -> str:
        """Format role awareness untuk display"""
        if not self.role_awareness:
            return "   (belum ada role terdaftar)"
        
        lines = []
        for role_id, awareness in self.role_awareness.items():
            level_emoji = {
                AwarenessLevel.LIMITED: "🔒",
                AwarenessLevel.NORMAL: "📖",
                AwarenessLevel.FULL: "🔓"
            }.get(awareness.awareness_level, "❓")
            lines.append(f"   {level_emoji} {role_id}: {awareness.awareness_level.value} ({len(awareness.known_facts)} facts)")
        
        return "\n".join(lines)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        return {
            'relationship_status': self.relationship_status.value,
            'drama_level': self.drama_level,
            'public_knowledge': self.public_knowledge.to_dict(),
            'last_interaction_with': self.last_interaction_with,
            'last_interaction_time': self.last_interaction_time,
            'drama_triggers': self.drama_triggers[-20:],
            'global_events': self.global_events[-50:],
            'active_rumors': self.active_rumors,
            'role_awareness': {rid: aw.to_dict() for rid, aw in self.role_awareness.items()}
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load dari dict"""
        self.relationship_status = GlobalRelationshipStatus(data.get('relationship_status', 'pacaran'))
        self.drama_level = data.get('drama_level', 0)
        self.last_interaction_with = data.get('last_interaction_with')
        self.last_interaction_time = data.get('last_interaction_time', 0)
        self.drama_triggers = data.get('drama_triggers', [])
        self.global_events = data.get('global_events', [])
        self.active_rumors = data.get('active_rumors', [])
        
        # Load public knowledge
        pk_data = data.get('public_knowledge', {})
        self.public_knowledge = PublicKnowledge()
        self.public_knowledge.from_dict(pk_data)
        
        # Load role awareness
        awareness_data = data.get('role_awareness', {})
        for role_id, aw_data in awareness_data.items():
            self.role_awareness[role_id] = RoleAwareness(
                role_id=role_id,
                awareness_level=AwarenessLevel(aw_data.get('awareness_level', 'limited')),
                known_facts=set(aw_data.get('known_facts', [])),
                last_updated=aw_data.get('last_updated', time.time()),
                misunderstanding_count=aw_data.get('misunderstanding_count', 0),
                revelation_count=aw_data.get('revelation_count', 0)
            )
        
        self.last_drama_update = time.time()
        self._update_drama_summary()
        
        logger.info(f"🌍 World State loaded: drama={self.drama_level:.0f}%, {len(self.role_awareness)} roles")


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_world_state: Optional[WorldState] = None


def get_world_state() -> WorldState:
    """Get global world state instance"""
    global _world_state
    if _world_state is None:
        _world_state = WorldState()
    return _world_state


def reset_world_state() -> None:
    """Reset world state (untuk testing)"""
    global _world_state
    _world_state = None
    logger.info("🔄 World State reset")


__all__ = [
    'GlobalRelationshipStatus',
    'AwarenessLevel',
    'DramaLevel',
    'PublicKnowledge',
    'RoleAwareness',
    'WorldState',
    'get_world_state',
    'reset_world_state'
]
