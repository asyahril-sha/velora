"""
VELORA - Base Role V2
Semua role mewarisi class ini.
State terpusat di MemoryManager dengan memory span 100 pesan.
Fokus pada kontinuitas cerita dan natural response.
"""

import time
import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from core.emotional import EmotionalEngine, EmotionalStyle
from core.relationship import RelationshipManager, RelationshipPhase
from core.conflict import ConflictEngine, ConflictType
from core.memory import MemoryManager, get_memory_manager
from core.world import AwarenessLevel, get_world_state
from core.reality_engine import get_reality_engine, RealityEngine

logger = logging.getLogger(__name__)


class BaseRole:
    """
    Base class untuk semua role.
    State terpusat di MemoryManager dengan memory span 100 pesan.
    Fokus pada kontinuitas cerita yang hidup.
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
        self.panggilan = panggilan  # WAJIB: "Mas" untuk semua role
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
        
        # ========== CONVERSATION HISTORY (UNTUK KONTINUITAS) ==========
        self.conversations: List[Dict] = []
        self.max_conversations: int = 100  # 100 pesan untuk kontinuitas
        
        # ========== TIMESTAMPS ==========
        self.created_at: float = time.time()
        self.last_interaction: float = time.time()
        self.last_message: str = ""
        
        # ========== STATUS ==========
        self.is_active: bool = False
        
        logger.info(f"👤 Role {self.name} initialized | Memory: {self.max_conversations} messages")
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    def initialize(self, memory: MemoryManager) -> None:
        """Initialize dengan memory manager"""
        self.memory = memory
        
        if self.world:
            self.world.register_role(self.id, self.awareness_level)
        
        logger.info(f"🔗 Role {self.name} connected to MemoryManager")
    
    # =========================================================================
    # UPDATE FROM MESSAGE (DENGAN KONTINUITAS)
    # =========================================================================
    
    def update_from_message(self, pesan_user: str) -> Dict[str, Any]:
        """
        Update semua state dari pesan user.
        Memory disimpan di MemoryManager dengan kontinuitas.
        """
        msg_lower = pesan_user.lower()
        changes = {}
        
        # ========== 1. UPDATE EMOTIONAL ENGINE ==========
        emo_changes = self.emotional.update_from_message(pesan_user, self.relationship.level)
        changes.update(emo_changes)
        
        # Process pending emotions
        delayed = self.reality.emotion_delay.process()
        for emotion_type, intensity in delayed:
            emo_changes = self.emotional.apply_pending_emotion(emotion_type, intensity)
            changes.update(emo_changes)
        
        # ========== 2. UPDATE CONFLICT ENGINE ==========
        conflict_changes = self.conflict.update_from_message(pesan_user, self.relationship.level)
        changes.update(conflict_changes)
        
        # ========== 3. UPDATE RELATIONSHIP ==========
        self.relationship.interaction_count += 1
        
        # Cek milestone
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
        
        # ========== 5. SAVE TO MEMORY (DENGAN KONTINUITAS) ==========
        if self.memory:
            # Hitung importance berdasarkan perubahan
            importance = 5
            if level_up:
                importance = 9
            elif changes.get('sayang', 0) > 5:
                importance = 7
            elif changes.get('cemburu', 0) > 5:
                importance = 6
            elif changes.get('kecewa', 0) > 5:
                importance = 6
            
            # Tambahkan topik untuk kontinuitas
            topik = self._extract_topic(pesan_user)
            
            # Add event ke memory dengan topik
            self.memory.add_event(
                kejadian=f"{'[PERTANYAAN] ' if pesan_user.endswith('?') else ''}{pesan_user[:150]}",
                detail=f"Perubahan: {', '.join([f'{k}:{v}' for k, v in changes.items() if isinstance(v, (int, float))][:3])} | Topik: {topik}",
                source="user",
                role_id=self.id,
                drama_impact=changes.get('cemburu', 0) / 10 if changes.get('cemburu') else 0,
                importance=importance,
                emotional_weight=changes.get('sayang', 0) or changes.get('cemburu', 0) or 5
            )
            
            # Add to reality engine
            self.reality.add_memory(
                content=pesan_user[:150],
                importance=importance,
                emotional_weight=changes.get('sayang', 0) or 5,
                tags=['user_message', topik]
            )
            
            # Update role knowledge
            if self.world:
                knowledge = self.world.get_knowledge_for_role(self.id)
                for fact in knowledge.get('known_facts', []):
                    self.memory.add_role_knowledge(self.id, fact)
        
        # ========== 6. UPDATE TIMESTAMPS ==========
        self.last_interaction = time.time()
        self.last_message = pesan_user
        
        # ========== 7. SAVE CONVERSATION (100 PESAN) ==========
        self.add_conversation(pesan_user, "")
        
        # ========== 8. UPDATE PERSONALITY DRIFT ==========
        self.reality.personality_drift.update(pesan_user, changes)
        
        return changes
    
    def _extract_topic(self, pesan_user: str) -> str:
        """Ekstrak topik dari pesan untuk kontinuitas"""
        msg_lower = pesan_user.lower()
        
        topics = {
            'kangen': 'rindu',
            'rindu': 'rindu',
            'sayang': 'kasih_sayang',
            'cinta': 'kasih_sayang',
            'marah': 'konflik',
            'kecewa': 'konflik',
            'maaf': 'resolusi',
            'jalan': 'aktivitas',
            'makan': 'aktivitas',
            'pulang': 'perpindahan',
            'pergi': 'perpindahan',
            'nova': 'nova',
            'dia': 'orang_lain'
        }
        
        for keyword, topic in topics.items():
            if keyword in msg_lower:
                return topic
        return 'umum'
    
    def _update_role_specific_state(self, pesan_user: str, changes: Dict) -> None:
        """Update role-specific state - OVERRIDE DI SUBCLASS"""
        pass
    
    # =========================================================================
    # GENERATE RESPONSE (DENGAN KONTINUITAS)
    # =========================================================================
    
    async def generate_response(self, pesan_user: str, context: str = None) -> str:
        """Generate response menggunakan AI dengan kontinuitas"""
        from bot.prompt import get_prompt_builder
        from bot.ai_client import get_ai_client
        
        try:
            # Process through reality engine
            current_emotion = {
                'sayang': self.emotional.sayang,
                'rindu': self.emotional.rindu,
                'cemburu': self.emotional.cemburu,
                'kecewa': self.emotional.kecewa,
                'arousal': self.emotional.arousal,
                'desire': self.emotional.desire
            }
            
            reality_result = await self.reality.process(pesan_user, current_emotion)
            
            # Build prompt
            prompt_builder = get_prompt_builder()
            if self.role_type == "nova":
                prompt = prompt_builder.build_nova_prompt(self, pesan_user, context)
            else:
                prompt = prompt_builder.build_role_prompt(self, pesan_user, context)
            
            # Add recalled memories
            if reality_result.get('recalled_memories'):
                prompt += f"\n\n📝 DIINGAT:\n" + "\n".join([f"- {m[:100]}" for m in reality_result['recalled_memories'][:3]])
            
            # Add inner thought if internal conflict
            if reality_result.get('has_internal_conflict'):
                inner = reality_result.get('inner_thought', '')
                if inner:
                    prompt += f"\n\n💭 PIKIRAN TERSEMBUNYI:\n{inner}"
            
            # Call AI
            ai_client = get_ai_client()
            
            style = self.emotional.get_current_style()
            arousal = self.emotional.arousal
            
            if arousal > 80:
                temperature = 0.95
            elif style == EmotionalStyle.FLIRTY:
                temperature = 0.9
            elif style == EmotionalStyle.COLD:
                temperature = 0.7
            else:
                temperature = 0.85
            
            max_tokens = 1000 if arousal > 60 else 800
            
            response = await ai_client.generate_with_context(
                prompt, 
                pesan_user,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Clean response
            response = response.strip()
            
            # Add imperfections
            emotion_intensity = max(self.emotional.sayang, self.emotional.arousal, self.emotional.cemburu) / 100
            response = self.reality.add_imperfections(response, emotion_intensity)
            
            # Validate
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
        """Greeting natural sesuai karakter - OVERRIDE DI SUBCLASS"""
        hour = datetime.now().hour
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        return f"*tersenyum kecil*\n\n\"{self.panggilan}, {waktu}. Ada yang bisa dibantu?\""
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik - OVERRIDE DI SUBCLASS"""
        return "*diam sebentar, menunduk*\n\n\"...\""
    
    # =========================================================================
    # CONVERSATION METHODS (100 PESAN)
    # =========================================================================
    
    def add_conversation(self, user_msg: str, role_msg: str = "") -> None:
        """Tambah percakapan ke history (max 100 pesan)"""
        self.conversations.append({
            'timestamp': time.time(),
            'user': user_msg[:200],
            'role': role_msg[:200]
        })
        if len(self.conversations) > self.max_conversations:
            self.conversations.pop(0)
    
    def get_recent_conversations(self, count: int = 10) -> str:
        """Dapatkan percakapan terakhir (default 10 pesan)"""
        if not self.conversations:
            return ""
        
        lines = []
        for c in self.conversations[-count:]:
            lines.append(f"Mas: {c['user']}")
            if c['role']:
                lines.append(f"{self.name}: {c['role']}")
        
        return "\n".join(lines)
    
    def get_full_conversation_history(self) -> List[Dict]:
        """Dapatkan seluruh history percakapan (max 100 pesan)"""
        return self.conversations[-self.max_conversations:]
    
    # =========================================================================
    # CONTEXT FOR PROMPT (DENGAN KONTINUITAS)
    # =========================================================================
    
    def get_context_for_prompt(self) -> str:
        """Dapatkan konteks lengkap untuk prompt AI dengan kontinuitas"""
        if not self.memory:
            return "Memory tidak tersedia."
        
        memory_context = self.memory.get_context_for_role(self.id)
        emo_summary = self.emotional.get_emotion_summary()
        rel_summary = self.relationship.format_for_prompt()
        conflict_guideline = self.conflict.get_conflict_response_guideline()
        recent_convo = self.get_recent_conversations(10)
        
        personality = self.reality.personality_drift.get_description()
        
        return f"""
{memory_context}

{emo_summary}

{rel_summary}

{conflict_guideline}

═══════════════════════════════════════════════════════════════
10 PESAN TERAKHIR:
═══════════════════════════════════════════════════════════════
{recent_convo if recent_convo else "Belum ada percakapan"}

🧠 KEPRIBADIAN: {personality if personality else "stabil"}

═══════════════════════════════════════════════════════════════
ATURAN:
1. LANJUTKAN alur dari 10 pesan terakhir
2. KONSISTEN dengan lokasi dan pakaian
3. KAMU TAHU hubungan dengan Nova: {self.hubungan_dengan_nova}
4. RESPON: 3-5 kalimat, natural, panggil "{self.panggilan}"
5. JANGAN PAKAI TEMPLATE

RESPON {self.name}:
"""
    
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
        
        clothing = ""
        location = ""
        if self.memory and self.memory.tracker:
            clothing = self.memory.tracker.get_clothing_summary()
            location = self.memory.tracker.location
        
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
║ DESIRE: {bar(self.emotional.desire, '💕')} {self.emotional.desire:.0f}%
║ AROUSAL: {bar(self.emotional.arousal, '🔥')} {self.emotional.arousal:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ LOKASI: {location if location else '-'}
║ PAKAIAN: {clothing[:40] if clothing else '-'}
║ INTERAKSI: {self.relationship.interaction_count}x
║ MEMORY: {len(self.conversations)} pesan
╚══════════════════════════════════════════════════════════════╝
"""
    
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
            'emotional': self.emotional.to_dict(),
            'relationship': self.relationship.to_dict(),
            'conflict': self.conflict.to_dict(),
            'flags': self.flags,
            'conversations': self.conversations[-100:],
            'created_at': self.created_at,
            'last_interaction': self.last_interaction,
            'last_message': self.last_message
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load dari dict"""
        self.name = data.get('name', self.name)
        self.nickname = data.get('nickname', self.nickname)
        self.role_type = data.get('role_type', self.role_type)
        self.panggilan = data.get('panggilan', self.panggilan)
        self.hubungan_dengan_nova = data.get('hubungan_dengan_nova', self.hubungan_dengan_nova)
        self.default_clothing = data.get('default_clothing', self.default_clothing)
        self.hijab = data.get('hijab', self.hijab)
        self.appearance = data.get('appearance', self.appearance)
        self.awareness_level = AwarenessLevel(data.get('awareness_level', 'normal'))
        
        if 'emotional' in data:
            self.emotional.from_dict(data['emotional'])
        if 'relationship' in data:
            self.relationship.from_dict(data['relationship'])
        if 'conflict' in data:
            self.conflict.from_dict(data['conflict'])
        
        self.flags = data.get('flags', {})
        self.conversations = data.get('conversations', [])
        self.created_at = data.get('created_at', time.time())
        self.last_interaction = data.get('last_interaction', time.time())
        self.last_message = data.get('last_message', '')
        
        logger.info(f"📀 Role {self.name} loaded | {len(self.conversations)} messages")


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
