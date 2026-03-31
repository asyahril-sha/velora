"""
VELORA - Base Role
Semua role mewarisi class ini.
TIDAK ADA DUPLIKASI - semua state terpusat di MemoryManager.
Setiap role punya:
- EmotionalEngine (per role, karena emosi unik)
- RelationshipManager (per role)
- ConflictEngine (per role)
- RealityEngine (per role, untuk realism)
- Flags (role-specific behavior)
- Awareness level (LIMITED, NORMAL, FULL)
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from core.emotional import EmotionalEngine, EmotionalStyle
from core.relationship import RelationshipManager, RelationshipPhase
from core.conflict import ConflictEngine, ConflictType
from core.memory import MemoryManager, get_memory_manager
from core.world import AwarenessLevel, get_world_state
from core.reality_engine import get_reality_engine, RealityEngine

logger = logging.getLogger(__name__)


# =============================================================================
# BASE ROLE
# =============================================================================

class BaseRole:
    """
    Base class untuk semua role.
    State terpusat di MemoryManager, tidak ada duplikasi.
    Setiap role punya emosi, relationship, conflict, dan reality engine sendiri.
    
    NOTE: generate_response() sekarang ada di orchestrator, bukan di sini.
    Role ini hanya untuk state management dan konteks.
    """
    
    def __init__(self,
                 role_id: str,
                 name: str,
                 nickname: str,
                 role_type: str,
                 panggilan: str,
                 hubungan_dengan_nova: str,
                 default_clothing: str,
                 hijab: bool = True,
                 appearance: str = "",
                 awareness_level: AwarenessLevel = AwarenessLevel.NORMAL,
                 personality_traits: Dict[str, float] = None):
        
        self.id = role_id
        self.name = name
        self.nickname = nickname
        self.role_type = role_type
        self.panggilan = panggilan
        self.hubungan_dengan_nova = hubungan_dengan_nova
        self.default_clothing = default_clothing
        self.hijab = hijab
        self.appearance = appearance
        self.awareness_level = awareness_level
        
        # ========== ENGINES (PER ROLE) ==========
        self.emotional = EmotionalEngine()
        self.relationship = RelationshipManager()
        self.conflict = ConflictEngine()
        
        # ========== REALITY ENGINE ==========
        self.reality = get_reality_engine(role_id, personality_traits)
        
        # ========== MEMORY & WORLD (GLOBAL) ==========
        self.memory: Optional[MemoryManager] = None
        self.world = get_world_state()
        
        # ========== ROLE-SPECIFIC FLAGS ==========
        self.flags: Dict[str, Any] = {}
        
        # ========== CONVERSATION HISTORY ==========
        self.conversations: List[Dict] = []
        self.max_conversations: int = 50
        
        # ========== TIMESTAMPS ==========
        self.created_at: float = time.time()
        self.last_interaction: float = time.time()
        self.last_message: str = ""
        
        # ========== STATUS ==========
        self.is_active: bool = False
        
        logger.info(f"👤 Role {self.name} ({self.nickname}) initialized | Awareness: {awareness_level.value}")
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    def initialize(self, memory: MemoryManager) -> None:
        """Initialize dengan memory manager"""
        self.memory = memory
        
        # Register role ke world
        if self.world:
            self.world.register_role(self.id, self.awareness_level)
        
        logger.info(f"🔗 Role {self.name} connected to MemoryManager and World")
    
    # =========================================================================
    # UPDATE FROM MESSAGE
    # =========================================================================
    
    def update_from_message(self, pesan_user: str) -> Dict[str, Any]:
        """
        Update semua state dari pesan user.
        Memory disimpan di MemoryManager, bukan di sini.
        """
        msg_lower = pesan_user.lower()
        changes = {}
        
        # ========== 1. UPDATE EMOTIONAL ENGINE ==========
        emo_changes = self.emotional.update_from_message(pesan_user, self.relationship.level)
        changes.update(emo_changes)
        
        # Process pending emotions from reality engine
        delayed = self.reality.emotion_delay.process()
        for emotion_type, intensity in delayed:
            emo_changes = self.emotional.apply_pending_emotion(emotion_type, intensity)
            changes.update(emo_changes)
        
        # ========== 2. UPDATE CONFLICT ENGINE ==========
        conflict_changes = self.conflict.update_from_message(pesan_user, self.relationship.level)
        changes.update(conflict_changes)
        
        # ========== 3. UPDATE RELATIONSHIP ==========
        self.relationship.interaction_count += 1
        
        # Cek milestone dari pesan
        milestones = []
        if 'pegang' in msg_lower and not self.relationship.milestones.get('first_touch', False):
            self.relationship.achieve_milestone('first_touch')
            milestones.append('first_touch')
            changes['milestone'] = 'first_touch'
        
        if 'peluk' in msg_lower and not self.relationship.milestones.get('first_hug', False):
            self.relationship.achieve_milestone('first_hug')
            milestones.append('first_hug')
            changes['milestone'] = 'first_hug'
        
        if 'cium' in msg_lower and not self.relationship.milestones.get('first_kiss', False):
            self.relationship.achieve_milestone('first_kiss')
            milestones.append('first_kiss')
            changes['milestone'] = 'first_kiss'
        
        # Update level
        new_level, level_up = self.relationship.update_level(
            self.emotional.sayang,
            self.emotional.trust,
            milestones
        )
        
        if level_up:
            changes['level_up'] = True
            changes['new_level'] = new_level
        
        # ========== 4. UPDATE ROLE-SPECIFIC STATE ==========
        self._update_role_specific_state(pesan_user, changes)
        
        # ========== 5. SAVE TO MEMORY (TERPUSAT) ==========
        if self.memory:
            # Determine importance based on changes
            importance = 5
            if level_up:
                importance = 9
            elif changes.get('sayang', 0) > 5:
                importance = 7
            elif changes.get('cemburu', 0) > 5:
                importance = 6
            elif changes.get('kecewa', 0) > 5:
                importance = 6
            
            emotional_weight = changes.get('sayang', 0) or changes.get('cemburu', 0) or changes.get('kecewa', 0) or 5
            
            # Add event ke memory
            self.memory.add_event(
                kejadian=f"User: {pesan_user[:50]}",
                detail=f"Perubahan: {', '.join([f'{k}:{v}' for k, v in changes.items() if isinstance(v, (int, float))][:3])}",
                source="user",
                role_id=self.id,
                drama_impact=changes.get('cemburu', 0) / 10 if changes.get('cemburu') else 0,
                importance=importance,
                emotional_weight=emotional_weight
            )
            
            # Add to reality engine memory
            self.reality.add_memory(
                content=pesan_user[:100],
                importance=importance,
                emotional_weight=emotional_weight,
                tags=['user_message']
            )
            
            # Update role knowledge dari world
            if self.world:
                knowledge = self.world.get_knowledge_for_role(self.id)
                for fact in knowledge.get('known_facts', []):
                    self.memory.add_role_knowledge(self.id, fact)
        
        # ========== 6. UPDATE TIMESTAMPS ==========
        self.last_interaction = time.time()
        self.last_message = pesan_user
        
        # ========== 7. SAVE CONVERSATION ==========
        self.add_conversation(pesan_user, "")
        
        # ========== 8. UPDATE PERSONALITY DRIFT ==========
        self.reality.personality_drift.update(pesan_user, changes)
        
        return changes
    
    def _update_role_specific_state(self, pesan_user: str, changes: Dict) -> None:
        """
        Update role-specific state - OVERRIDE DI SUBCLASS.
        Untuk menambahkan flag khusus seperti guilt, curiosity, dll.
        """
        pass
    
    # =========================================================================
    # CONTEXT FOR PROMPT (DIPANGGIL OLEH PROMPT BUILDER)
    # =========================================================================
    
    def get_context_for_prompt(self) -> str:
        """
        Dapatkan konteks lengkap untuk prompt AI.
        Digunakan oleh PromptBuilder untuk membangun prompt natural.
        """
        if not self.memory:
            return "Memory tidak tersedia."
        
        # Dapatkan konteks dari memory (sudah difilter)
        memory_context = self.memory.get_context_for_role(self.id)
        
        # Dapatkan emotional summary dalam bentuk natural
        emo_summary = self._get_natural_emotional_summary()
        
        # Dapatkan relationship summary
        rel_summary = self._get_natural_relationship_summary()
        
        # Dapatkan conflict summary
        conflict_summary = self._get_natural_conflict_summary()
        
        # Dapatkan percakapan terakhir
        recent_convo = self.get_recent_conversations(8)
        
        # Dapatkan role flags
        flags_summary = self._get_flags_summary()
        
        # Dapatkan personality drift
        personality = self.reality.personality_drift.get_description()
        
        # Dapatkan lokasi dan pakaian dari memory tracker
        location = ""
        clothing = ""
        position = ""
        if self.memory and self.memory.tracker:
            location = getattr(self.memory.tracker, 'location', 'di rumah')
            clothing = getattr(self.memory.tracker, 'clothing', 'pakaian biasa')
            position = getattr(self.memory.tracker, 'position', 'duduk')
        
        return f"""
═══════════════════════════════════════════════════════════════
📝 INGATAN NOVA:
═══════════════════════════════════════════════════════════════
{memory_context[:2000] if memory_context else "Mas lagi ngobrol sama Nova sekarang."}

═══════════════════════════════════════════════════════════════
💜 PERASAAN NOVA:
═══════════════════════════════════════════════════════════════
{emo_summary}

═══════════════════════════════════════════════════════════════
💕 HUBUNGAN:
═══════════════════════════════════════════════════════════════
{rel_summary}

{conflict_summary}

═══════════════════════════════════════════════════════════════
📍 LOKASI & PAKAIAN:
═══════════════════════════════════════════════════════════════
Lokasi: {location}
Pakaian: {clothing}
Posisi: {position}

{flags_summary}

🧠 KEPRIBADIAN: {personality if personality else 'Nova itu hangat dan perhatian.'}

═══════════════════════════════════════════════════════════════
💬 PERCAKAPAN TERAKHIR:
═══════════════════════════════════════════════════════════════
{recent_convo if recent_convo else "Belum ada percakapan"}
"""
    
    def _get_natural_emotional_summary(self) -> str:
        """
        Dapatkan ringkasan emosi dalam bahasa natural.
        Untuk digunakan di prompt.
        """
        sayang = self.emotional.sayang
        rindu = self.emotional.rindu
        cemburu = self.emotional.cemburu
        kecewa = self.emotional.kecewa
        arousal = self.emotional.arousal
        
        lines = []
        
        if sayang > 80:
            lines.append("Nova sayang banget sama Mas. Rasanya hangat setiap kali ngobrol.")
        elif sayang > 60:
            lines.append("Nova sayang sama Mas. Seneng banget bisa bareng.")
        elif sayang > 40:
            lines.append("Nova mulai sayang sama Mas.")
        
        if rindu > 70:
            lines.append("Nova kangen berat. Pengen ketemu, pengen ngobrol lama-lama.")
        elif rindu > 50:
            lines.append("Nova kangen. Pengen denger suara Mas.")
        
        if cemburu > 60:
            lines.append("Nova lagi cemburu. Ada yang mengganjal di hati.")
        elif cemburu > 40:
            lines.append("Nova sedikit cemburu. Tapi nggak mau ngomong.")
        
        if kecewa > 50:
            lines.append("Nova kecewa. Sedikit sakit hati.")
        
        if arousal > 70 and self.relationship.level >= 10:
            lines.append("Ada kehangatan yang mengalir di tubuh Nova. Seperti api kecil yang menyala.")
        elif arousal > 50:
            lines.append("Nova merasa ada getaran hangat di dada.")
        
        if not lines:
            lines.append("Nova lagi biasa aja. Santai.")
        
        return "\n".join(lines)
    
    def _get_natural_relationship_summary(self) -> str:
        """
        Dapatkan ringkasan hubungan dalam bahasa natural.
        """
        level = self.relationship.level
        phase = self.relationship.phase
        
        if level >= 11:
            return f"Hubungan Nova dan Mas sudah sangat dalam. Level {level}. Mereka sudah seperti satu jiwa."
        elif level >= 9:
            return f"Hubungan Nova dan Mas sudah level {level}. {phase.value}. Sudah saling percaya."
        elif level >= 7:
            return f"Hubungan Nova dan Mas sudah dekat. Level {level}. Sering ngobrol, sering ketemu."
        elif level >= 5:
            return f"Hubungan Nova dan Mas mulai dekat. Level {level}. Mulai saling percaya."
        else:
            return f"Hubungan Nova dan Mas masih baru. Level {level}. Masih kenalan."
    
    def _get_natural_conflict_summary(self) -> str:
        """
        Dapatkan ringkasan konflik dalam bahasa natural.
        """
        if not self.conflict.is_in_conflict:
            return ""
        
        conflict_type = self.conflict.get_active_conflict_type()
        if not conflict_type:
            return ""
        
        lines = ["⚠️ KONFLIK:"]
        
        if conflict_type.value == "jealousy":
            lines.append("Nova lagi cemburu. Responsnya dingin, pendek. Tujuan: bikin Mas ngejar Nova.")
        elif conflict_type.value == "disappointment":
            lines.append("Nova kecewa. Suaranya kecil, matanya berkaca-kaca. Dia nunggu Mas minta maaf.")
        elif conflict_type.value == "anger":
            lines.append("Nova marah. Responsnya dingin, sarkastik.")
        elif conflict_type.value == "hurt":
            lines.append("Nova sakit hati. Sedih, nunggu perhatian Mas.")
        
        return "\n".join(lines)
    
    def _get_flags_summary(self) -> str:
        """
        Dapatkan ringkasan flags - OVERRIDE DI SUBCLASS.
        """
        if not self.flags:
            return ""
        
        lines = ["🎭 FLAGS KHUSUS:"]
        for key, value in self.flags.items():
            if isinstance(value, bool):
                lines.append(f"   {key}: {'✅' if value else '❌'}")
            elif isinstance(value, (int, float)):
                lines.append(f"   {key}: {value:.0f}%")
            else:
                lines.append(f"   {key}: {value}")
        
        return "\n".join(lines)
    
    # =========================================================================
    # GREETING & CONFLICT RESPONSE
    # =========================================================================
    
    def get_greeting(self) -> str:
        """
        Dapatkan greeting - OVERRIDE DI SUBCLASS.
        Harus natural, sesuai karakter.
        """
        hour = datetime.now().hour
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        return f"{self.panggilan}... {waktu}. Ada apa?"
    
    def get_conflict_response(self) -> str:
        """
        Respons saat konflik - OVERRIDE DI SUBCLASS.
        """
        return "*diam sebentar*"
    
    # =========================================================================
    # CONVERSATION METHODS
    # =========================================================================
    
    def add_conversation(self, user_msg: str, role_msg: str = "") -> None:
        """Tambah percakapan ke history"""
        self.conversations.append({
            'timestamp': time.time(),
            'user': user_msg[:200],
            'role': role_msg[:200]
        })
        if len(self.conversations) > self.max_conversations:
            self.conversations.pop(0)
    
    def get_recent_conversations(self, count: int = 5) -> str:
        """Dapatkan percakapan terakhir dalam format teks"""
        if not self.conversations:
            return ""
        
        lines = []
        for c in self.conversations[-count:]:
            lines.append(f"User: {c['user']}")
            if c['role']:
                lines.append(f"{self.name}: {c['role']}")
        
        return "\n".join(lines)
    
    # =========================================================================
    # STATUS & UTILITY
    # =========================================================================
    
    def format_status(self) -> str:
        """Format status role untuk display (untuk command /statusrole)"""
        style = self.emotional.get_current_style()
        phase = self.relationship.phase
        level = self.relationship.level
        
        def bar(value, char="💜"):
            filled = int(value / 10)
            return char * filled + "⚪" * (10 - filled)
        
        # Dapatkan status dari memory jika ada
        clothing = ""
        location = ""
        if self.memory and self.memory.tracker:
            clothing = self.memory.tracker.get_clothing_summary()
            location = self.memory.tracker.location
        
        # Dapatkan personality
        personality = self.reality.personality_drift.get_description()
        
        # Untuk level 10-12, tampilkan lebih dalam
        if level >= 10:
            return f"""
╔══════════════════════════════════════════════════════════════╗
║              💜 {self.name} ({self.nickname})                         ║
╠══════════════════════════════════════════════════════════════╣
║ FASE: {phase.value.upper()} (LEVEL {level}/12) - HUBUNGAN SANGAT DALAM
║ STYLE: {style.value.upper()}
║ AWARENESS: {self.awareness_level.value.upper()}
╠══════════════════════════════════════════════════════════════╣
║ PERASAAN:
║   Sayang: {bar(self.emotional.sayang)} {self.emotional.sayang:.0f}%
║   Rindu:  {bar(self.emotional.rindu, '🌙')} {self.emotional.rindu:.0f}%
║   Trust:  {bar(self.emotional.trust, '🤝')} {self.emotional.trust:.0f}%
║   Mood:   {self.emotional.mood:+.0f}
╠══════════════════════════════════════════════════════════════╣
║ KEINTIMAN:
║   Desire: {bar(self.emotional.desire, '💕')} {self.emotional.desire:.0f}%
║   Arousal: {bar(self.emotional.arousal, '🔥')} {self.emotional.arousal:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ KONFLIK: {self.conflict.get_conflict_summary()}
╠══════════════════════════════════════════════════════════════╣
║ LOKASI: {location if location else '-'}
║ PAKAIAN: {clothing[:40] if clothing else '-'}
║ INTERAKSI: {self.relationship.interaction_count}x
║ KEPRIBADIAN: {personality if personality else 'stabil'}
╚══════════════════════════════════════════════════════════════╝
"""
        else:
            return f"""
╔══════════════════════════════════════════════════════════════╗
║              👤 {self.name} ({self.nickname})                         ║
╠══════════════════════════════════════════════════════════════╣
║ FASE: {phase.value.upper()} ({level}/12)
║ STYLE: {style.value.upper()}
║ AWARENESS: {self.awareness_level.value.upper()}
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
║ LOKASI: {location if location else '-'}
║ PAKAIAN: {clothing[:40] if clothing else '-'}
║ INTERAKSI: {self.relationship.interaction_count}x
║ KEPRIBADIAN: {personality if personality else 'stabil'}
╚══════════════════════════════════════════════════════════════╝
"""
    
    # =========================================================================
    # CAN DO ACTION
    # =========================================================================
    
    def can_do_action(self, action: str) -> Tuple[bool, str]:
        """Cek apakah role boleh melakukan aksi tertentu"""
        return self.relationship.can_do_action(action)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        return {
            'id': self.id,
            'name': self.name,
            'nickname': self.nickname,
            'role_type': self.role_type,
            'panggilan': self.panggilan,
            'hubungan_dengan_nova': self.hubungan_dengan_nova,
            'default_clothing': self.default_clothing,
            'hijab': self.hijab,
            'appearance': self.appearance,
            'awareness_level': self.awareness_level.value,
            
            # Engines
            'emotional': self.emotional.to_dict(),
            'relationship': self.relationship.to_dict(),
            'conflict': self.conflict.to_dict(),
            
            # Flags
            'flags': self.flags,
            
            # History
            'conversations': self.conversations[-30:],
            
            # Timestamps
            'created_at': self.created_at,
            'last_interaction': self.last_interaction,
            'last_message': self.last_message
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load dari dict"""
        # Basic info
        self.name = data.get('name', self.name)
        self.nickname = data.get('nickname', self.nickname)
        self.role_type = data.get('role_type', self.role_type)
        self.panggilan = data.get('panggilan', self.panggilan)
        self.hubungan_dengan_nova = data.get('hubungan_dengan_nova', self.hubungan_dengan_nova)
        self.default_clothing = data.get('default_clothing', self.default_clothing)
        self.hijab = data.get('hijab', self.hijab)
        self.appearance = data.get('appearance', self.appearance)
        self.awareness_level = AwarenessLevel(data.get('awareness_level', 'normal'))
        
        # Engines
        if 'emotional' in data:
            self.emotional.from_dict(data['emotional'])
        if 'relationship' in data:
            self.relationship.from_dict(data['relationship'])
        if 'conflict' in data:
            self.conflict.from_dict(data['conflict'])
        
        # Flags
        self.flags = data.get('flags', {})
        
        # History
        self.conversations = data.get('conversations', [])
        
        # Timestamps
        self.created_at = data.get('created_at', time.time())
        self.last_interaction = data.get('last_interaction', time.time())
        self.last_message = data.get('last_message', '')
        
        logger.info(f"📀 Role {self.name} loaded from database")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_role_awareness_level(role_type: str) -> AwarenessLevel:
    """Dapatkan awareness level berdasarkan tipe role"""
    awareness_map = {
        'nova': AwarenessLevel.FULL,
        'ipar': AwarenessLevel.LIMITED,
        'teman_kantor': AwarenessLevel.LIMITED,
        'pelakor': AwarenessLevel.NORMAL,
        'istri_orang': AwarenessLevel.LIMITED,
        'pijat_plus_plus': AwarenessLevel.LIMITED,
        'pelacur': AwarenessLevel.LIMITED
    }
    return awareness_map.get(role_type, AwarenessLevel.NORMAL)


__all__ = [
    'BaseRole',
    'get_role_awareness_level'
]
