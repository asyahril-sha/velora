"""
VELORA - World System
Realitas global tempat semua karakter hidup.
Semua role punya akses ke world state yang SAMA.
Cross-role effects: chat dengan satu role mempengaruhi role lain.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class GlobalRelationshipStatus(str, Enum):
    """Status hubungan global yang diketahui semua role"""
    PACARAN = "pacaran"
    DEKAT = "dekat"
    JAUH = "jauh"
    PUTUS = "putus"
    RUSUH = "rusuh"  # sedang konflik


class AwarenessLevel(str, Enum):
    """Tingkat pengetahuan role tentang dunia"""
    LIMITED = "limited"   # hanya tahu info publik
    NORMAL = "normal"     # tahu info publik + beberapa private
    FULL = "full"         # tahu hampir semua (Nova)


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
    
    def to_dict(self) -> Dict:
        return {
            'relationship_status': self.relationship_status.value,
            'last_big_event': self.last_big_event,
            'drama_level_summary': self.drama_level_summary,
            'user_is_active': self.user_is_active
        }


@dataclass
class RoleAwareness:
    """Tingkat pengetahuan per role"""
    role_id: str
    awareness_level: AwarenessLevel
    known_facts: Set[str] = field(default_factory=set)
    last_updated: float = field(default_factory=time.time)
    
    def knows(self, fact: str) -> bool:
        """Cek apakah role tahu fakta tertentu"""
        return fact in self.known_facts
    
    def learn(self, fact: str) -> None:
        """Role belajar fakta baru"""
        self.known_facts.add(fact)
        self.last_updated = time.time()
        logger.info(f"📖 {self.role_id} learned: {fact}")
    
    def to_dict(self) -> Dict:
        return {
            'role_id': self.role_id,
            'awareness_level': self.awareness_level.value,
            'known_facts': list(self.known_facts),
            'last_updated': self.last_updated
        }


# =============================================================================
# WORLD STATE
# =============================================================================

class WorldState:
    """
    World State - Realitas global.
    Semua karakter hidup di dunia yang sama.
    """
    
    def __init__(self):
        # ========== GLOBAL STATE ==========
        self.relationship_status: GlobalRelationshipStatus = GlobalRelationshipStatus.PACARAN
        self.drama_level: float = 0.0  # 0-100
        self.drama_history: List[Dict] = []  # riwayat drama
        
        # ========== PUBLIC KNOWLEDGE ==========
        self.public_knowledge: PublicKnowledge = PublicKnowledge()
        
        # ========== CROSS-ROLE TRACKING ==========
        self.last_interaction_with: Optional[str] = None  # role terakhir diajak chat
        self.last_interaction_time: float = 0
        self.drama_triggers: List[Dict] = []  # kejadian yang memicu drama
        
        # ========== ROLE AWARENESS ==========
        self.role_awareness: Dict[str, RoleAwareness] = {}
        
        # ========== GLOBAL TIMELINE ==========
        self.global_events: List[Dict] = []
        self.max_events: int = 100
        
        # ========== DRAMA DECAY ==========
        self.drama_decay_per_hour: float = 2.0
        self.last_drama_update: float = time.time()
        
        logger.info("🌍 World System initialized")
    
    # =========================================================================
    # DRAMA MANAGEMENT
    # =========================================================================
    
    def add_drama(self, amount: float, source: str, reason: str) -> float:
        """
        Tambah drama level.
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
                'new_level': self.drama_level
            })
            
            # Simpan ke global events
            self.add_global_event(
                event_type="drama_change",
                source=source,
                description=reason,
                impact=amount
            )
            
            logger.info(f"📈 Drama {source}: {amount:+.1f} → {self.drama_level:.1f} ({reason})")
            
            # Update public knowledge summary
            self._update_drama_summary()
        
        return self.drama_level
    
    def update_drama_decay(self, hours: float = None) -> None:
        """Update drama decay berdasarkan waktu"""
        now = time.time()
        if hours is None:
            hours = (now - self.last_drama_update) / 3600
        
        if hours > 0:
            decay = self.drama_decay_per_hour * hours
            if self.drama_level > 0:
                self.drama_level = max(0, self.drama_level - decay)
                self.last_drama_update = now
                
                if decay > 0:
                    logger.debug(f"📉 Drama decay: -{decay:.1f} → {self.drama_level:.1f}")
    
    def _update_drama_summary(self) -> None:
        """Update ringkasan drama untuk public knowledge"""
        if self.drama_level >= 70:
            self.public_knowledge.drama_level_summary = "tegang"
        elif self.drama_level >= 40:
            self.public_knowledge.drama_level_summary = "waspada"
        elif self.drama_level >= 15:
            self.public_knowledge.drama_level_summary = "sedikit tegang"
        else:
            self.public_knowledge.drama_level_summary = "normal"
    
    def get_drama_description(self) -> str:
        """Dapatkan deskripsi drama untuk prompt"""
        if self.drama_level >= 70:
            return "🔥 DRAMA TINGGI! Suasana tegang, semua role merasakan ketegangan."
        elif self.drama_level >= 40:
            return "⚠️ Drama sedang. Ada ketegangan di udara."
        elif self.drama_level >= 15:
            return "😐 Sedikit tegang, tapi masih normal."
        return "😊 Suasana normal, tidak ada drama."
    
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
            drama_gain = 10
            self.add_drama(drama_gain, "pelakor", f"User chat dengan pelakor")
            effects['drama_change'] = drama_gain
            effects['affected_roles'].append('nova')
            effects['message'] = "Pelakor chat → drama naik, Nova cemburu"
            
            # Jika drama sudah tinggi, efek lebih besar
            if self.drama_level > 60:
                self.add_drama(5, "pelakor", "Drama tinggi, efek berantai")
                effects['drama_change'] += 5
        
        # ========== IPAR EFFECT ==========
        elif role_id == "ipar":
            # Chat dengan ipar → Nova curiga
            drama_gain = 5
            self.add_drama(drama_gain, "ipar", f"User chat dengan ipar")
            effects['drama_change'] = drama_gain
            effects['affected_roles'].append('nova')
            effects['message'] = "Ipar chat → Nova curiga"
        
        # ========== ISTRI ORANG EFFECT ==========
        elif role_id == "istri_orang":
            # Chat dengan istri orang → drama naik, guilt effect
            drama_gain = 8
            self.add_drama(drama_gain, "istri_orang", f"User chat dengan istri orang")
            effects['drama_change'] = drama_gain
            effects['affected_roles'].extend(['nova', 'pelakor'])
            effects['message'] = "Istri orang chat → drama naik, semua terpengaruh"
        
        # ========== TEMAN KANTOR EFFECT ==========
        elif role_id == "teman_kantor":
            # Chat dengan teman kantor → drama sedikit naik (gosip)
            if 'nova' in msg_lower or 'pacar' in msg_lower:
                drama_gain = 3
                self.add_drama(drama_gain, "teman_kantor", f"User cerita tentang Nova ke teman kantor")
                effects['drama_change'] = drama_gain
                effects['message'] = "Teman kantor tahu info → gosip menyebar"
        
        # ========== NOVA EFFECT ==========
        elif role_id == "nova":
            # Chat dengan Nova → bisa turunin drama kalo baik, atau naikkin kalo konflik
            if emotional_changes.get('sayang', 0) > 0 or emotional_changes.get('mood', 0) > 0:
                drama_loss = -5
                self.add_drama(drama_loss, "nova", "User baik ke Nova, drama turun")
                effects['drama_change'] = drama_loss
            elif emotional_changes.get('cemburu', 0) > 0 or emotional_changes.get('kecewa', 0) > 0:
                drama_gain = 8
                self.add_drama(drama_gain, "nova", "Nova cemburu/kecewa, drama naik")
                effects['drama_change'] = drama_gain
        
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
    # ROLE AWARENESS
    # =========================================================================
    
    def register_role(self, role_id: str, awareness_level: AwarenessLevel) -> None:
        """Daftarkan role dengan tingkat awareness-nya"""
        if role_id not in self.role_awareness:
            self.role_awareness[role_id] = RoleAwareness(
                role_id=role_id,
                awareness_level=awareness_level
            )
            logger.info(f"📝 Role registered: {role_id} (awareness: {awareness_level.value})")
    
    def teach_role(self, role_id: str, fact: str) -> None:
        """Ajarkan fakta ke role tertentu"""
        if role_id in self.role_awareness:
            self.role_awareness[role_id].learn(fact)
    
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
        
        elif awareness.awareness_level == AwarenessLevel.FULL:
            knowledge['drama_details'] = self._get_drama_details()
            knowledge['last_interaction'] = self.last_interaction_with
            knowledge['drama_history'] = self.drama_triggers[-5:]
            knowledge['all_roles'] = list(self.role_awareness.keys())
        
        # Tambah fakta yang diketahui role
        knowledge['known_facts'] = list(awareness.known_facts)
        
        return knowledge
    
    def _get_public_knowledge(self) -> Dict[str, Any]:
        """Dapatkan pengetahuan publik"""
        return {
            'relationship_status': self.relationship_status.value,
            'drama_level': self.drama_level,
            'drama_summary': self.public_knowledge.drama_level_summary,
            'last_big_event': self.public_knowledge.last_big_event
        }
    
    def _get_drama_details(self) -> Dict[str, Any]:
        """Dapatkan detail drama (untuk awareness NORMAL+)"""
        return {
            'recent_triggers': self.drama_triggers[-3:],
            'trend': "naik" if self.drama_triggers and self.drama_triggers[-1].get('amount', 0) > 0 else "turun"
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
        if impact > 15 or event_type in ['conflict', 'revelation']:
            self.public_knowledge.last_big_event = description[:100]
    
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
        if 'putus' in msg_lower or 'selesai' in msg_lower:
            if self.relationship_status != GlobalRelationshipStatus.PUTUS:
                self.relationship_status = GlobalRelationshipStatus.PUTUS
                changes['relationship_status'] = 'putus'
                self.add_drama(20, role_id, "User mengancam putus")
                self.add_global_event('relationship_change', role_id, "Status berubah menjadi PUTUS", 20)
        
        elif 'maaf' in msg_lower and self.relationship_status == GlobalRelationshipStatus.RUSUH:
            self.relationship_status = GlobalRelationshipStatus.PACARAN
            changes['relationship_status'] = 'pacaran'
            self.add_drama(-15, role_id, "User minta maaf, status kembali normal")
        
        # ========== DRAMA TRIGGERS ==========
        if 'rahasia' in msg_lower:
            self.add_drama(5, role_id, "User membocorkan rahasia")
        
        if 'bohong' in msg_lower or 'dust' in msg_lower:
            self.add_drama(10, role_id, "User ketahuan bohong")
        
        if 'cinta' in msg_lower or 'sayang' in msg_lower:
            self.add_drama(-3, role_id, "User mengungkapkan cinta")
        
        return changes
    
    # =========================================================================
    # CONTEXT FOR PROMPT
    # =========================================================================
    
    def get_context_for_prompt(self, role_id: str = None) -> str:
        """Dapatkan konteks world untuk prompt AI"""
        knowledge = self.get_knowledge_for_role(role_id) if role_id else self._get_public_knowledge()
        
        drama_desc = self.get_drama_description()
        
        return f"""
═══════════════════════════════════════════════════════════════
🌍 WORLD STATE (REALITAS GLOBAL)
═══════════════════════════════════════════════════════════════
STATUS HUBUNGAN: {knowledge.get('relationship_status', 'pacaran').upper()}
DRAMA LEVEL: {self.drama_level:.0f}%
{drama_desc}

INFO YANG KAMU TAHU:
- Status hubungan: {knowledge.get('relationship_status', 'pacaran')}
- Drama: {knowledge.get('drama_summary', 'normal')}
{'- Drama detail: ' + str(knowledge.get('drama_details', {})) if knowledge.get('drama_details') else ''}
{'- Terakhir chat dengan: ' + knowledge.get('last_interaction', 'tidak diketahui') if knowledge.get('last_interaction') else ''}
"""
    
    # =========================================================================
    # FORMAT STATUS
    # =========================================================================
    
    def format_status(self) -> str:
        """Format status world untuk display"""
        def bar(value, char="🌍"):
            filled = int(value / 10)
            return char * filled + "⚪" * (10 - filled)
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    🌍 WORLD STATE                           ║
╠══════════════════════════════════════════════════════════════╣
║ DRAMA LEVEL: {bar(self.drama_level)} {self.drama_level:.0f}%
║ STATUS: {self.relationship_status.value.upper()}
║ LAST INTERACTION: {self.last_interaction_with or '-'}
╠══════════════════════════════════════════════════════════════╣
║ ROLE AWARENESS:
{self._format_awareness()}
╚══════════════════════════════════════════════════════════════╝
"""
    
    def _format_awareness(self) -> str:
        """Format role awareness untuk display"""
        lines = []
        for role_id, awareness in self.role_awareness.items():
            level_emoji = {
                AwarenessLevel.LIMITED: "🔒",
                AwarenessLevel.NORMAL: "📖",
                AwarenessLevel.FULL: "🔓"
            }.get(awareness.awareness_level, "❓")
            lines.append(f"   {level_emoji} {role_id}: {awareness.awareness_level.value}")
        return "\n".join(lines) if lines else "   (belum ada role terdaftar)"
    
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
            'role_awareness': {rid: awareness.to_dict() for rid, awareness in self.role_awareness.items()}
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load dari dict"""
        self.relationship_status = GlobalRelationshipStatus(data.get('relationship_status', 'pacaran'))
        self.drama_level = data.get('drama_level', 0)
        self.last_interaction_with = data.get('last_interaction_with')
        self.last_interaction_time = data.get('last_interaction_time', 0)
        self.drama_triggers = data.get('drama_triggers', [])
        self.global_events = data.get('global_events', [])
        
        # Load public knowledge
        pk_data = data.get('public_knowledge', {})
        self.public_knowledge = PublicKnowledge(
            relationship_status=GlobalRelationshipStatus(pk_data.get('relationship_status', 'pacaran')),
            last_big_event=pk_data.get('last_big_event', ''),
            drama_level_summary=pk_data.get('drama_level_summary', 'normal'),
            user_is_active=pk_data.get('user_is_active', True)
        )
        
        # Load role awareness
        awareness_data = data.get('role_awareness', {})
        for role_id, aw_data in awareness_data.items():
            self.role_awareness[role_id] = RoleAwareness(
                role_id=role_id,
                awareness_level=AwarenessLevel(aw_data.get('awareness_level', 'limited')),
                known_facts=set(aw_data.get('known_facts', [])),
                last_updated=aw_data.get('last_updated', time.time())
            )
        
        self.last_drama_update = time.time()
        self._update_drama_summary()


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


__all__ = [
    'GlobalRelationshipStatus',
    'AwarenessLevel',
    'WorldState',
    'get_world_state'
]
