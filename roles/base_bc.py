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
        
        # ========== REALITY ENGINE (BARU - UNTUK REALISM 9.9) ==========
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

        self.awareness_level = AwarenessLevel.LIMITED
        
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
    # GENERATE RESPONSE
    # =========================================================================
    
    async def generate_response(self, pesan_user: str, context: str = None) -> str:
        """
        Generate response menggunakan AI dengan RealityEngine enhancements.
        """
        from bot.prompt import get_prompt_builder
        from bot.ai_client import get_ai_client
        
        try:
            # 1. Process through reality engine
            current_emotion = {
                'sayang': self.emotional.sayang,
                'rindu': self.emotional.rindu,
                'cemburu': self.emotional.cemburu,
                'kecewa': self.emotional.kecewa,
                'arousal': self.emotional.arousal,
                'desire': self.emotional.desire
            }
            
            reality_result = await self.reality.process(pesan_user, current_emotion)
            
            # 2. Build prompt sesuai tipe role
            prompt_builder = get_prompt_builder()
            if self.role_type == "nova":
                prompt = prompt_builder.build_nova_prompt(self, pesan_user, context)
            else:
                prompt = prompt_builder.build_role_prompt(self, pesan_user, context)
            
            # 3. Add recalled memories to prompt
            if reality_result.get('recalled_memories'):
                prompt += f"\n\n📝 YANG DIINGAT:\n" + "\n".join([f"- {m[:100]}" for m in reality_result['recalled_memories'][:3]])
            
            # 4. Add inner thought if internal conflict
            if reality_result.get('has_internal_conflict'):
                inner = reality_result.get('inner_thought', '')
                if inner:
                    prompt += f"\n\n💭 PIKIRAN TERSEMBUNYI:\n{inner}"
            
            # 5. Call AI
            ai_client = get_ai_client()
            
            # Determine temperature based on arousal and style
            style = self.emotional.get_current_style()
            arousal = self.emotional.arousal
            
            if arousal > 80:
                temperature = 1.0
            elif style == EmotionalStyle.FLIRTY:
                temperature = 0.95
            elif style == EmotionalStyle.COLD:
                temperature = 0.7
            else:
                temperature = 0.85
            
            max_tokens = 1200 if arousal > 60 else 800
            
            response = await ai_client.generate_with_context(
                prompt, 
                pesan_user,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 6. Clean response
            response = response.strip()
            
            # 7. Add imperfections
            emotion_intensity = max(self.emotional.sayang, self.emotional.arousal, self.emotional.cemburu) / 100
            response = self.reality.add_imperfections(response, emotion_intensity)
            
            # 8. Add scene if needed
            if self.role_type != "pijat_plus_plus" and self.role_type != "pelacur":
                scene = self.reality.scene_engine.get_body_language(
                    style.value if style else "neutral",
                    emotion_intensity
                )
                if scene and scene not in response and not response.startswith('*'):
                    response = f"{scene}\n\n{response}"
            
            # 9. Validate
            if not response or len(response) < 3:
                return self.get_greeting()
            
            return response
            
        except Exception as e:
            logger.error(f"AI response error for {self.name}: {e}")
            return self.get_greeting()
    
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
    # CONTEXT FOR PROMPT
    # =========================================================================
    
    def get_context_for_prompt(self) -> str:
        """
        Dapatkan konteks lengkap untuk prompt AI.
        Menggunakan MemoryManager yang sudah terfilter.
        """
        if not self.memory:
            return "Memory tidak tersedia."
        
        # Dapatkan konteks dari memory (sudah difilter)
        memory_context = self.memory.get_context_for_role(self.id)
        
        # Dapatkan emotional summary
        emo_summary = self.emotional.get_emotion_summary()
        
        # Dapatkan relationship summary
        rel_summary = self.relationship.format_for_prompt()
        
        # Dapatkan conflict summary
        conflict_guideline = self.conflict.get_conflict_response_guideline()
        
        # Dapatkan percakapan terakhir
        recent_convo = self.get_recent_conversations(5)
        
        # Dapatkan role flags
        flags_summary = self._get_flags_summary()
        
        # Dapatkan personality drift
        personality = self.reality.personality_drift.get_description()
        
        return f"""
{memory_context}

{emo_summary}

{rel_summary}

{conflict_guideline}

═══════════════════════════════════════════════════════════════
PERCAKAPAN TERAKHIR:
═══════════════════════════════════════════════════════════════
{recent_convo if recent_convo else "Belum ada percakapan"}

{flags_summary}

🧠 PERSONALITY: {personality if personality else "stabil"}

═══════════════════════════════════════════════════════════════
ATURAN WAJIB:
═══════════════════════════════════════════════════════════════
1. BACA TIMELINE DI ATAS! Lanjutkan alur, jangan mundur!
2. JANGAN LUPA konteks pakaian dan posisi!
3. KAMU TAHU hubungan dengan Nova: {self.hubungan_dengan_nova}
4. RESPON NATURAL: 2-4 kalimat, bahasa campuran
5. JANGAN PAKAI TEMPLATE! Setiap respons harus UNIK!

═══════════════════════════════════════════════════════════════
RESPON {self.name}:
"""
    
    def _get_flags_summary(self) -> str:
        """
        Dapatkan ringkasan flags - OVERRIDE DI SUBCLASS.
        """
        if not self.flags:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════════════"]
        lines.append("🎭 ROLE-SPECIFIC FLAGS:")
        for key, value in self.flags.items():
            if isinstance(value, bool):
                lines.append(f"   {key}: {'✅' if value else '❌'}")
            elif isinstance(value, (int, float)):
                lines.append(f"   {key}: {value:.0f}%")
            else:
                lines.append(f"   {key}: {value}")
        
        return "\n".join(lines)
    
    # =========================================================================
    # STATUS & UTILITY
    # =========================================================================
    
    def format_status(self) -> str:
        """Format status role untuk display"""
        style = self.emotional.get_current_style()
        phase = self.relationship.phase
        
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
║ PAKAIAN: {clothing[:40] if clothing else '-'}
║ LOKASI: {location if location else '-'}
║ INTERAKSI: {self.relationship.interaction_count}x
║ PERSONALITY: {personality if personality else 'stabil'}
╚══════════════════════════════════════════════════════════════╝
"""
    
    # =========================================================================
    # CAN DO ACTION (BERDASARKAN RELATIONSHIP)
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
