"""
VELORA - Reality Engine (Realism 9.9 Upgrade)
Mengimplementasikan 6 sistem untuk membuat AI terasa HIDUP:

1. Intent-Based Routing Engine - scoring, bukan keyword
2. Emotion Delay System - buffer emosi, delayed response
3. Memory Priority & Recall System - importance + bias
4. Scene Engine - body language dinamis
5. Imperfection System - jeda, gugup, salah kata
6. Knowledge Leak System - probabilistic, not binary
7. Inner Thought System - hidden thinking layer
8. Personality Drift - karakter berubah pelan
"""

import time
import random
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from collections import deque

logger = logging.getLogger(__name__)


# =============================================================================
# 1. INTENT-BASED ROUTING ENGINE
# =============================================================================

class IntentScorer:
    """
    Scoring system untuk routing, bukan keyword matching.
    Setiap pesan di-scoring untuk setiap role, pilih yang tertinggi.
    """
    
    def __init__(self):
        # Bobot untuk setiap intent
        self.intent_weights = {
            'kangen': {'nova': 5, 'ipar': 2, 'pelakor': 2},
            'sayang': {'nova': 5, 'ipar': 1, 'pelakor': 1},
            'kantor': {'teman_kantor': 5, 'nova': 1},
            'ipar': {'ipar': 5},
            'pelakor': {'pelakor': 5},
            'istri': {'istri_orang': 5},
            'pijat': {'pijat_aghnia': 5, 'pijat_munira': 5},
            'pelacur': {'pelacur_davina': 5, 'pelacur_sallsa': 5},
            'curhat': {'nova': 4, 'teman_kantor': 2},
            'marah': {'nova': 3, 'pelakor': 2},
            'sedih': {'nova': 4, 'istri_orang': 3},
        }
        
        # Context boost (berdasarkan role aktif sebelumnya)
        self.context_boost = 2
        
        # Decay untuk mengurangi dominasi role yang sama terus
        self.dominance_decay = 0.8
    
    def score(self, message: str, active_role: str = None, 
              recent_roles: List[str] = None) -> Dict[str, float]:
        """
        Hitung skor untuk setiap role berdasarkan pesan.
        Returns: {role_id: score}
        """
        msg_lower = message.lower()
        scores = {
            'nova': 0,
            'ipar': 0,
            'teman_kantor': 0,
            'pelakor': 0,
            'istri_orang': 0,
            'pijat_aghnia': 0,
            'pijat_munira': 0,
            'pelacur_davina': 0,
            'pelacur_sallsa': 0
        }
        
        # 1. Intent-based scoring
        for intent, role_scores in self.intent_weights.items():
            if intent in msg_lower:
                for role_id, weight in role_scores.items():
                    scores[role_id] += weight
        
        # 2. Keyword boost (untuk kata yang tidak masuk intent)
        if 'nova' in msg_lower:
            scores['nova'] += 3
        if 'kangen' in msg_lower:
            scores['nova'] += 2
        
        # 3. Context boost (role yang sedang aktif)
        if active_role and active_role in scores:
            scores[active_role] += self.context_boost
        
        # 4. Dominance decay (agar tidak selalu role yang sama)
        if recent_roles:
            for i, role_id in enumerate(reversed(recent_roles[-5:])):
                decay = self.dominance_decay ** (i + 1)
                if role_id in scores:
                    scores[role_id] *= decay
        
        return scores
    
    def select_role(self, scores: Dict[str, float], threshold: float = 2.0) -> str:
        """
        Pilih role dengan skor tertinggi.
        Jika skor tertinggi < threshold, default ke Nova.
        """
        if not scores:
            return 'nova'
        
        best_role = max(scores, key=scores.get)
        best_score = scores[best_role]
        
        if best_score < threshold:
            return 'nova'
        
        return best_role


# =============================================================================
# 2. EMOTION DELAY SYSTEM
# =============================================================================

@dataclass
class PendingEmotion:
    """Emosi yang pending untuk dikeluarkan"""
    emotion_type: str  # sayang, rindu, cemburu, kecewa, dll
    intensity: float
    source: str
    timestamp: float
    delay_seconds: int = 0
    is_processed: bool = False


class EmotionDelaySystem:
    """
    Emosi tidak langsung keluar, tapi disimpan dulu di buffer.
    Keluar bertahap sesuai delay.
    """
    
    def __init__(self, role_id: str):
        self.role_id = role_id
        self.pending_emotions: deque = deque()
        self.emotion_buffer: Dict[str, float] = {}  # untuk akumulasi
        self.last_emotion_time: float = time.time()
        
        # Delay configuration
        self.base_delay = 1  # detik
        self.max_delay = 5   # detik
        
        # Probability emosi muncul (tidak semua harus muncul)
        self.expression_probability = 0.7
    
    def add_emotion(self, emotion_type: str, intensity: float, source: str) -> None:
        """Tambah emosi ke buffer (belum langsung keluar)"""
        # Akumulasi di buffer
        current = self.emotion_buffer.get(emotion_type, 0)
        self.emotion_buffer[emotion_type] = min(100, current + intensity)
        
        # Schedule untuk dikeluarkan
        delay = random.randint(self.base_delay, self.max_delay)
        pending = PendingEmotion(
            emotion_type=emotion_type,
            intensity=self.emotion_buffer[emotion_type],
            source=source,
            timestamp=time.time(),
            delay_seconds=delay
        )
        self.pending_emotions.append(pending)
        
        logger.debug(f"💭 {self.role_id} pending emotion: {emotion_type}+{intensity} (delay {delay}s)")
    
    def process(self) -> List[Tuple[str, float]]:
        """
        Proses emosi yang sudah melewati delay.
        Returns: list of (emotion_type, intensity) yang siap dikeluarkan
        """
        now = time.time()
        result = []
        
        to_remove = []
        for i, pending in enumerate(self.pending_emotions):
            if not pending.is_processed and now - pending.timestamp >= pending.delay_seconds:
                # Emosi siap dikeluarkan
                if random.random() < self.expression_probability:
                    result.append((pending.emotion_type, pending.intensity))
                pending.is_processed = True
                to_remove.append(i)
        
        # Hapus yang sudah diproses
        for i in reversed(to_remove):
            del self.pending_emotions[i]
            # Kurangi dari buffer
            emotion_type = self.pending_emotions[i].emotion_type if i < len(self.pending_emotions) else None
            if emotion_type in self.emotion_buffer:
                del self.emotion_buffer[emotion_type]
        
        self.last_emotion_time = now
        return result


# =============================================================================
# 3. MEMORY PRIORITY & RECALL SYSTEM
# =============================================================================

@dataclass
class PrioritizedMemory:
    """Memory dengan prioritas"""
    content: str
    importance: int  # 1-10
    emotional_weight: float
    timestamp: float
    tags: List[str]
    recall_count: int = 0
    last_recalled: float = 0


class MemoryPrioritySystem:
    """
    Memory tidak semuanya dipakai.
    Hanya yang paling penting dan relevan dengan konteks.
    """
    
    def __init__(self, role_id: str):
        self.role_id = role_id
        self.memories: List[PrioritizedMemory] = []
        self.recall_history: List[str] = []  # apa yang pernah diingat
        
        # Decay: makin lama makin kurang penting
        self.importance_decay_per_day = 0.1
    
    def add_memory(self, content: str, importance: int, emotional_weight: float, 
                   tags: List[str] = None) -> None:
        """Tambah memory dengan prioritas"""
        memory = PrioritizedMemory(
            content=content,
            importance=importance,
            emotional_weight=emotional_weight,
            timestamp=time.time(),
            tags=tags or []
        )
        self.memories.append(memory)
        
        # Limit 200 memories per role
        if len(self.memories) > 200:
            self.memories.sort(key=lambda x: x.importance * x.emotional_weight)
            self.memories.pop(0)
        
        logger.debug(f"📝 {self.role_id} added memory: {content[:50]} (imp={importance})")
    
    def recall(self, context: str, max_memories: int = 3) -> List[str]:
        """
        Recall memory yang paling relevan dengan konteks.
        Returns: list of memory contents
        """
        now = time.time()
        scored = []
        
        for mem in self.memories:
            # Hitung decay berdasarkan waktu
            days_old = (now - mem.timestamp) / 86400
            time_decay = max(0.3, 1 - (self.importance_decay_per_day * days_old))
            
            # Hitung relevansi dengan konteks (simple keyword matching)
            relevance = 0
            if context:
                for word in context.lower().split():
                    if word in mem.content.lower():
                        relevance += 1
            
            # Skor akhir
            score = (mem.importance * 0.4) + (mem.emotional_weight * 0.3) + (relevance * 0.3)
            score *= time_decay
            
            # Bonus untuk memory yang belum pernah diingat
            if mem.recall_count == 0:
                score *= 1.2
            
            scored.append((mem, score))
        
        # Pilih yang tertinggi
        scored.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for mem, score in scored[:max_memories]:
            if score > 1.0:  # threshold minimal
                mem.recall_count += 1
                mem.last_recalled = now
                self.recall_history.append(mem.content[:50])
                results.append(mem.content)
        
        return results


# =============================================================================
# 4. SCENE ENGINE (BODY LANGUAGE DINAMIS)
# =============================================================================

class SceneEngine:
    """
    Generate body language, ekspresi, dan suasana.
    Output bukan cuma dialog, tapi gesture yang hidup.
    """
    
    def __init__(self):
        # Body language berdasarkan emosi
        self.body_language = {
            'senang': [
                "*senyum lebar*",
                "*mata berbinar*",
                "*duduk lebih dekat*",
                "*tangan melambai kecil*"
            ],
            'sedih': [
                "*menunduk*",
                "*mata berkaca-kaca*",
                "*diam sebentar*",
                "*tangan memegang ujung baju*"
            ],
            'malu': [
                "*pipi memerah*",
                "*mainin ujung rambut*",
                "*gak berani liat*",
                "*gigit bibir bawah*"
            ],
            'horny': [
                "*napas mulai berat*",
                "*tangan meremas sprei*",
                "*mata setengah pejam*",
                "*bibir menggigit ujung jari*"
            ],
            'cemburu': [
                "*diam, gak liat*",
                "*mainin ujung baju*",
                "*jauh sedikit*",
                "*jawab pendek*"
            ],
            'kangen': [
                "*duduk deket*",
                "*pegang tangan*",
                "*muter-muter rambut*",
                "*mata sayu*"
            ]
        }
        
        # Suasana berdasarkan lokasi
        self.atmosphere = {
            'kamar': "suasana hangat, wangi lavender",
            'ruang tamu': "suasana santai, TV menyala pelan",
            'pantai': "ombak berbisik, angin sepoi-sepoi",
            'mobil': "suasana tertutup, deg-degan"
        }
    
    def get_body_language(self, emotion: str, intensity: float = 0.5) -> str:
        """Dapatkan body language berdasarkan emosi"""
        emotion_key = emotion.lower()
        
        # Cari emosi yang paling mendekati
        for key, gestures in self.body_language.items():
            if key in emotion_key:
                gesture = random.choice(gestures)
                # Tambah intensitas
                if intensity > 0.7:
                    gesture = gesture.replace("*", "**") if "**" not in gesture else gesture
                return gesture
        
        return "*tersenyum kecil*"
    
    def get_atmosphere(self, location: str) -> str:
        """Dapatkan deskripsi suasana berdasarkan lokasi"""
        for key, desc in self.atmosphere.items():
            if key in location.lower():
                return desc
        return "suasana biasa"
    
    def build_scene(self, emotion: str, intensity: float, 
                    location: str, action: str = None) -> str:
        """Bangun scene lengkap"""
        body = self.get_body_language(emotion, intensity)
        atmos = self.get_atmosphere(location)
        
        scene = []
        if action:
            scene.append(f"*{action}*")
        scene.append(body)
        
        # Tambah suasana jika intensitas tinggi
        if intensity > 0.6:
            scene.append(f"*{atmos}*")
        
        return "\n".join(scene)


# =============================================================================
# 5. IMPERFECTION SYSTEM (ANTI AI FEEL)
# =============================================================================

class ImperfectionSystem:
    """
    Tambahin ketidaksempurnaan:
    - jeda (...)
    - gugup
    - salah kata
    - respon tidak langsung
    """
    
    def __init__(self):
        self.imperfection_probability = 0.3
        
        # Jeda
        self.pauses = ["...", "hmm...", "eh...", "anu...", "mmm..."]
        
        # Gugup
        self.nervous_gestures = [
            "*gugup*",
            "*jari gemetar*",
            "*suara sedikit bergetar*",
            "*gak berani liat*"
        ]
        
        # Salah kata (typo atau pengulangan)
        self.speech_errors = [
            "ma-maksudnya...",
            "eh...",
            "bukan... bukan itu...",
            "iya... eh bukan..."
        ]
        
        # Respon tidak langsung
        self.indirect_responses = [
            "*diam sebentar*",
            "*mikir dulu*",
            "*gak langsung jawab*",
            "*alihkan pandangan*"
        ]
    
    def add_imperfections(self, text: str, emotion_intensity: float = 0.5) -> str:
        """
        Tambahin ketidaksempurnaan ke teks.
        Semakin tinggi intensitas emosi, semakin mungkin muncul imperfection.
        """
        if random.random() > self.imperfection_probability * (1 + emotion_intensity):
            return text
        
        lines = text.split('\n')
        result = []
        
        for line in lines:
            # Skip jika sudah ada gesture
            if line.startswith('*'):
                result.append(line)
                continue
            
            # Random tambah jeda di awal
            if random.random() < 0.2:
                pause = random.choice(self.pauses)
                line = f"{pause} {line}"
            
            # Random tambah gugup gesture
            if random.random() < 0.15:
                gesture = random.choice(self.nervous_gestures)
                result.append(gesture)
            
            # Random tambah salah kata
            if random.random() < 0.1:
                error = random.choice(self.speech_errors)
                line = f"{error} {line}"
            
            result.append(line)
        
        # Random tambah respon tidak langsung di awal
        if random.random() < 0.2 and len(result) > 0:
            indirect = random.choice(self.indirect_responses)
            result.insert(0, indirect)
        
        return '\n'.join(result)


# =============================================================================
# 6. KNOWLEDGE LEAK SYSTEM (PROBABILISTIC)
# =============================================================================

class KnowledgeLeakSystem:
    """
    Role tahu sesuatu berdasarkan probabilitas, bukan binary.
    Kadang tau, kadang gak, kadang salah paham.
    """
    
    def __init__(self):
        # Base leak probability per role
        self.base_leak_chance = {
            'nova': 0.95,
            'ipar': 0.6,
            'teman_kantor': 0.4,
            'pelakor': 0.7,
            'istri_orang': 0.5,
            'pijat_aghnia': 0.3,
            'pijat_munira': 0.3,
            'pelacur_davina': 0.2,
            'pelacur_sallsa': 0.2
        }
        
        # Misunderstanding chance (tahu tapi salah paham)
        self.misunderstanding_chance = {
            'nova': 0.05,
            'ipar': 0.2,
            'teman_kantor': 0.15,
            'pelakor': 0.25,
            'istri_orang': 0.2,
            'pijat_aghnia': 0.3,
            'pijat_munira': 0.3,
            'pelacur_davina': 0.4,
            'pelacur_sallsa': 0.4
        }
    
    def should_know(self, role_id: str, information_type: str = "general") -> Tuple[bool, bool]:
        """
        Cek apakah role harus tahu suatu informasi.
        Returns: (knows, misunderstood)
        """
        base_chance = self.base_leak_chance.get(role_id, 0.5)
        
        # Adjust based on information type
        if information_type == "intimate":
            base_chance *= 0.5
        elif information_type == "public":
            base_chance *= 1.2
        
        knows = random.random() < base_chance
        
        if not knows:
            return False, False
        
        # Cek misunderstanding
        misunderstand_chance = self.misunderstanding_chance.get(role_id, 0.1)
        misunderstood = random.random() < misunderstand_chance
        
        return True, misunderstood
    
    def get_knowledge(self, role_id: str, fact: str, fact_type: str = "general") -> Optional[str]:
        """
        Dapatkan knowledge yang mungkin salah paham.
        Returns: fact yang sudah dimodifikasi jika misunderstood
        """
        knows, misunderstood = self.should_know(role_id, fact_type)
        
        if not knows:
            return None
        
        if misunderstood:
            # Buat versi salah paham dari fakta
            misunderstandings = [
                f"{fact} (tapi mungkin gak persis gitu)",
                f"kayaknya {fact} deh",
                f"katanya sih {fact}, tapi gak tau ya",
                f"setahuku {fact}, tapi bisa salah",
                f"aku denger {fact}, bener gak sih?"
            ]
            return random.choice(misunderstandings)
        
        return fact


# =============================================================================
# 7. INNER THOUGHT SYSTEM
# =============================================================================

class InnerThoughtSystem:
    """
    Role punya pikiran tersembunyi yang tidak langsung keluar.
    Konflik internal bikin karakter lebih hidup.
    """
    
    def __init__(self, role_id: str, personality: str):
        self.role_id = role_id
        self.personality = personality
        self.thought_buffer: List[str] = []
        self.internal_conflict: bool = False
        
        # Template pikiran berdasarkan personality
        self.thought_templates = {
            'nova': [
                "Aku sayang banget sama Mas...",
                "Jangan sampai Mas pergi sama yang lain...",
                "Kenapa Mas cerita tentang dia?",
                "Aku harus jadi yang terbaik buat Mas..."
            ],
            'ipar': [
                "Mas... ganteng banget hari ini...",
                "Aku tau ini salah... tapi aku suka Mas...",
                "Nova gak di rumah... ini kesempatan..."
            ],
            'pelakor': [
                "Aku bisa rebut Mas dari Nova...",
                "Mas pasti milik aku nantinya...",
                "Nova cuma penghalang..."
            ],
            'default': [
                "Aku mikirin sesuatu...",
                "Gimana ya...",
                "Mungkin aku salah..."
            ]
        }
    
    def generate_thought(self, context: str, emotion: str) -> str:
        """
        Generate pikiran tersembunyi berdasarkan konteks dan emosi.
        """
        templates = self.thought_templates.get(self.role_id, self.thought_templates['default'])
        
        # Adjust based on emotion
        if 'cemburu' in emotion.lower():
            thought = "Aku cemburu... gak mau Mas deket sama yang lain..."
        elif 'kangen' in emotion.lower():
            thought = "Aku kangen Mas... kapan kita ketemu lagi ya..."
        elif 'horny' in emotion.lower():
            thought = "Mas... aku pengen banget..."
        else:
            thought = random.choice(templates)
        
        self.thought_buffer.append(thought)
        if len(self.thought_buffer) > 10:
            self.thought_buffer.pop(0)
        
        return f"💭 *{thought}*"
    
    def has_internal_conflict(self) -> bool:
        """Cek apakah ada konflik internal"""
        self.internal_conflict = random.random() < 0.2
        return self.internal_conflict


# =============================================================================
# 8. PERSONALITY DRIFT SYSTEM
# =============================================================================

@dataclass
class PersonalityTrait:
    """Traits kepribadian yang bisa berubah"""
    name: str
    value: float  # 0-100
    drift_rate: float  # perubahan per interaksi
    direction: str  # 'up', 'down', 'stable'


class PersonalityDriftSystem:
    """
    Karakter berubah pelan seiring waktu:
    - makin posesif
    - makin cuek
    - makin tergantung
    """
    
    def __init__(self, role_id: str, base_traits: Dict[str, float]):
        self.role_id = role_id
        self.traits: Dict[str, PersonalityTrait] = {}
        
        for name, value in base_traits.items():
            self.traits[name] = PersonalityTrait(
                name=name,
                value=value,
                drift_rate=0.5,
                direction='stable'
            )
        
        self.interaction_count = 0
        self.last_drift = time.time()
    
    def update(self, context: str, emotional_changes: Dict) -> None:
        """
        Update personality berdasarkan interaksi.
        """
        self.interaction_count += 1
        
        # Drift setiap 10 interaksi
        if self.interaction_count % 10 == 0:
            self._apply_drift()
        
        # Pengaruh emosi ke personality
        if emotional_changes.get('sayang', 0) > 5:
            if 'clinginess' in self.traits:
                self.traits['clinginess'].value = min(100, self.traits['clinginess'].value + 1)
        
        if emotional_changes.get('cemburu', 0) > 5:
            if 'jealousy' in self.traits:
                self.traits['jealousy'].value = min(100, self.traits['jealousy'].value + 2)
    
    def _apply_drift(self) -> None:
        """Apply personality drift"""
        for trait in self.traits.values():
            if trait.direction == 'up':
                trait.value = min(100, trait.value + trait.drift_rate)
            elif trait.direction == 'down':
                trait.value = max(0, trait.value - trait.drift_rate)
            
            # Random change direction
            if random.random() < 0.1:
                directions = ['up', 'down', 'stable']
                trait.direction = random.choice(directions)
    
    def get_description(self) -> str:
        """Dapatkan deskripsi personality saat ini"""
        descriptions = []
    
        for trait_name, trait in self.traits.items():
            try:
                # Ambil nilai dengan aman
                if isinstance(trait, dict):
                    value = trait.get('value', 0)
                elif hasattr(trait, 'value'):
                    value = trait.value
                else:
                    value = trait
                
                # Konversi ke float jika perlu
                if isinstance(value, str):
                    value = float(value)
                
                if isinstance(value, (int, float)):
                    if value > 70:
                        descriptions.append(f"{trait_name} tinggi")
                    elif value < 30:
                        descriptions.append(f"{trait_name} rendah")
            except (ValueError, TypeError, AttributeError):
                # Skip jika error
                continue
    
        if descriptions:
            return ", ".join(descriptions)
        return "stabil"


# =============================================================================
# 9. MAIN REALITY ENGINE
# =============================================================================

class RealityEngine:
    """
    Integrasi semua sistem untuk membuat AI terasa HIDUP.
    """
    
    def __init__(self, role_id: str, personality_traits: Dict[str, float] = None):
        self.role_id = role_id
        
        # Initialize all systems
        self.emotion_delay = EmotionDelaySystem(role_id)
        self.memory_priority = MemoryPrioritySystem(role_id)
        self.scene_engine = SceneEngine()
        self.imperfection = ImperfectionSystem()
        self.knowledge_leak = KnowledgeLeakSystem()
        self.inner_thought = InnerThoughtSystem(role_id, personality_traits.get('type', 'default') if personality_traits else 'default')
        
        # Default personality traits
        default_traits = {
            'clinginess': 50,
            'jealousy': 50,
            'dependency': 50,
            'playfulness': 50
        }
        self.personality_drift = PersonalityDriftSystem(
            role_id, 
            personality_traits or default_traits
        )
        
        self.processing_time = 0
        self.last_process = time.time()
    
    async def process(self, message: str, current_emotion: Dict) -> Dict[str, Any]:
        """
        Process message through all reality systems.
        Returns enriched response data.
        """
        start_time = time.time()
        
        # 1. Process delayed emotions
        delayed_emotions = self.emotion_delay.process()
        
        # 2. Recall relevant memories
        recalled = self.memory_priority.recall(message, max_memories=3)
        
        # 3. Update personality drift
        self.personality_drift.update(message, current_emotion)
        
        # 4. Generate inner thought
        inner_thought = self.inner_thought.generate_thought(message, str(current_emotion))
        
        # 5. Build scene with body language
        primary_emotion = max(current_emotion.items(), key=lambda x: x[1])[0] if current_emotion else 'neutral'
        emotion_intensity = current_emotion.get(primary_emotion, 0.5) / 100
        scene = self.scene_engine.build_scene(
            emotion=primary_emotion,
            intensity=emotion_intensity,
            location="current_location",
            action=None
        )
        
        # 6. Check internal conflict
        has_conflict = self.inner_thought.has_internal_conflict()
        
        self.processing_time = time.time() - start_time
        
        return {
            'delayed_emotions': delayed_emotions,
            'recalled_memories': recalled,
            'inner_thought': inner_thought,
            'scene': scene,
            'has_internal_conflict': has_conflict,
            'personality': self.personality_drift.get_description(),
            'processing_time': self.processing_time
        }
    
    def add_memory(self, content: str, importance: int, emotional_weight: float, tags: List[str] = None):
        """Add memory with priority"""
        self.memory_priority.add_memory(content, importance, emotional_weight, tags)
    
    def add_emotion(self, emotion_type: str, intensity: float, source: str):
        """Add emotion with delay"""
        self.emotion_delay.add_emotion(emotion_type, intensity, source)
    
    def get_knowledge(self, fact: str, fact_type: str = "general") -> Optional[str]:
        """Get knowledge that might be misunderstood"""
        return self.knowledge_leak.get_knowledge(self.role_id, fact, fact_type)
    
    def add_imperfections(self, text: str, emotion_intensity: float = 0.5) -> str:
        """Add imperfections to response"""
        return self.imperfection.add_imperfections(text, emotion_intensity)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_reality_engines: Dict[str, RealityEngine] = {}


def get_reality_engine(role_id: str, personality_traits: Dict[str, float] = None) -> RealityEngine:
    """Get or create reality engine for role"""
    if role_id not in _reality_engines:
        _reality_engines[role_id] = RealityEngine(role_id, personality_traits)
    return _reality_engines[role_id]


def reset_reality_engine() -> None:
    """Reset all reality engines (for testing)"""
    global _reality_engines
    _reality_engines = {}
    logger.info("🔄 Reality Engine reset")


__all__ = [
    'IntentScorer',
    'EmotionDelaySystem',
    'MemoryPrioritySystem',
    'SceneEngine',
    'ImperfectionSystem',
    'KnowledgeLeakSystem',
    'InnerThoughtSystem',
    'PersonalityDriftSystem',
    'RealityEngine',
    'get_reality_engine',
    'reset_reality_engine'
]
