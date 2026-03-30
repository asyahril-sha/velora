"""
VELORA - Memory Manager
Satu sumber kebenaran untuk semua memory VELORA.
- Short-term memory (sliding window 50 kejadian)
- Long-term memory (kebiasaan, momen penting, janji)
- Global timeline (semua kejadian)
- Memory priority system (importance + emotional weight)
- Role-specific knowledge dengan leak system
- Integrasi dengan StateTracker dan WorldSystem
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from dataclasses import dataclass, field

from core.tracker import StateTracker
from core.world import WorldState, AwarenessLevel
from core.reality_engine import MemoryPrioritySystem, get_reality_engine

logger = logging.getLogger(__name__)


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class MemoryEvent:
    """Satu event dalam memory"""
    timestamp: float
    waktu: str
    kejadian: str
    detail: str
    source: str
    role_id: str
    drama_impact: float = 0
    importance: int = 5
    emotional_weight: float = 0
    intimacy_phase: str = "none"
    location: str = ""
    tags: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'waktu': self.waktu,
            'kejadian': self.kejadian,
            'detail': self.detail,
            'source': self.source,
            'role_id': self.role_id,
            'drama_impact': self.drama_impact,
            'importance': self.importance,
            'emotional_weight': self.emotional_weight,
            'intimacy_phase': self.intimacy_phase,
            'location': self.location,
            'tags': list(self.tags)
        }


@dataclass
class LongTermMemory:
    """Long-term memory permanen"""
    tipe: str  # kebiasaan_mas, momen_penting, janji, rencana, tentang_suami, dll
    judul: str
    konten: str
    perasaan: str = ""
    timestamp: float = field(default_factory=time.time)
    role_id: str = "nova"
    importance: int = 5
    emotional_weight: float = 0
    recall_count: int = 0
    last_recalled: float = 0
    
    def to_dict(self) -> Dict:
        return {
            'tipe': self.tipe,
            'judul': self.judul,
            'konten': self.konten,
            'perasaan': self.perasaan,
            'timestamp': self.timestamp,
            'role_id': self.role_id,
            'importance': self.importance,
            'emotional_weight': self.emotional_weight,
            'recall_count': self.recall_count,
            'last_recalled': self.last_recalled
        }


# =============================================================================
# MEMORY MANAGER
# =============================================================================

class MemoryManager:
    """
    Memory Manager - Satu sumber kebenaran untuk semua memory.
    Terintegrasi dengan MemoryPrioritySystem untuk recall cerdas.
    """
    
    def __init__(self):
        # ========== STATE TRACKER (GLOBAL) ==========
        self.tracker: Optional[StateTracker] = None
        
        # ========== WORLD SYSTEM ==========
        self.world: Optional[WorldState] = None
        
        # ========== SHORT-TERM MEMORY (SLIDING WINDOW) ==========
        self.short_term: List[MemoryEvent] = []
        self.max_short_term: int = 50
        
        # ========== LONG-TERM MEMORY (PER ROLE) ==========
        self.long_term: Dict[str, List[LongTermMemory]] = {
            'nova': [],
            'ipar': [],
            'teman_kantor': [],
            'pelakor': [],
            'istri_orang': [],
            'pijat_aghnia': [],
            'pijat_munira': [],
            'pelacur_davina': [],
            'pelacur_sallsa': []
        }
        
        # ========== PRIORITY MEMORY SYSTEMS PER ROLE ==========
        self.priority_memory: Dict[str, MemoryPrioritySystem] = {}
        
        # ========== ROLE-SPECIFIC KNOWLEDGE ==========
        self.role_knowledge: Dict[str, Set[str]] = {
            'nova': set(),
            'ipar': set(),
            'teman_kantor': set(),
            'pelakor': set(),
            'istri_orang': set(),
            'pijat_aghnia': set(),
            'pijat_munira': set(),
            'pelacur_davina': set(),
            'pelacur_sallsa': set()
        }
        
        # ========== GLOBAL TIMELINE ==========
        self.global_timeline: List[MemoryEvent] = []
        self.max_global_timeline: int = 200
        
        # ========== STATISTICS ==========
        self.total_events: int = 0
        self.created_at: float = time.time()
        
        logger.info("🧠 Memory Manager initialized")
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    def initialize(self, tracker: StateTracker, world: WorldState) -> None:
        """Initialize dengan tracker dan world"""
        self.tracker = tracker
        self.world = world
        logger.info("🧠 Memory Manager connected to Tracker and World")
    
    # =========================================================================
    # PRIORITY MEMORY ACCESS
    # =========================================================================
    
    def _get_priority_memory(self, role_id: str) -> MemoryPrioritySystem:
        """Get or create priority memory system for role"""
        if role_id not in self.priority_memory:
            self.priority_memory[role_id] = MemoryPrioritySystem(role_id)
        return self.priority_memory[role_id]
    
    # =========================================================================
    # ADD MEMORY
    # =========================================================================
    
    def add_event(self, 
                   kejadian: str, 
                   detail: str, 
                   source: str, 
                   role_id: str = "nova",
                   drama_impact: float = 0,
                   importance: int = 5,
                   emotional_weight: float = 0,
                   tags: List[str] = None) -> MemoryEvent:
        """
        Tambah event ke memory.
        Ini adalah method utama untuk mencatat semua kejadian.
        """
        now = time.time()
        event = MemoryEvent(
            timestamp=now,
            waktu=datetime.now().strftime("%H:%M:%S"),
            kejadian=kejadian,
            detail=detail,
            source=source,
            role_id=role_id,
            drama_impact=drama_impact,
            importance=importance,
            emotional_weight=emotional_weight,
            intimacy_phase=self.tracker.intimacy_phase.value if self.tracker else "none",
            location=self.tracker.location if self.tracker else "",
            tags=set(tags) if tags else set()
        )
        
        # Add to priority memory system
        priority = self._get_priority_memory(role_id)
        priority.add_memory(
            content=kejadian,
            importance=importance,
            emotional_weight=emotional_weight,
            tags=tags
        )
        
        # Add to short-term memory (sliding window)
        self.short_term.append(event)
        if len(self.short_term) > self.max_short_term:
            self.short_term.pop(0)
        
        # Add to global timeline
        self.global_timeline.append(event)
        if len(self.global_timeline) > self.max_global_timeline:
            self.global_timeline.pop(0)
        
        # Update tracker jika ada
        if self.tracker:
            self.tracker.add_to_timeline(kejadian, detail)
        
        # Update world drama jika ada impact
        if self.world and drama_impact != 0:
            self.world.add_drama(drama_impact, source, kejadian[:50])
        
        self.total_events += 1
        
        logger.debug(f"📝 Event added: [{source}] {kejadian[:50]} (imp={importance}, emo={emotional_weight:.1f})")
        
        return event
    
    def add_long_term_memory(self,
                              tipe: str,
                              judul: str,
                              konten: str,
                              perasaan: str = "",
                              role_id: str = "nova",
                              importance: int = 5,
                              emotional_weight: float = 0) -> None:
        """
        Tambah long-term memory permanen.
        """
        memory = LongTermMemory(
            tipe=tipe,
            judul=judul,
            konten=konten,
            perasaan=perasaan,
            timestamp=time.time(),
            role_id=role_id,
            importance=importance,
            emotional_weight=emotional_weight
        )
        
        if role_id not in self.long_term:
            self.long_term[role_id] = []
        
        self.long_term[role_id].append(memory)
        
        # Also add to priority memory
        priority = self._get_priority_memory(role_id)
        priority.add_memory(
            content=f"{tipe}: {judul} - {konten[:100]}",
            importance=importance,
            emotional_weight=emotional_weight,
            tags=[tipe]
        )
        
        # Limit per role (keep most important)
        if len(self.long_term[role_id]) > 100:
            self.long_term[role_id].sort(key=lambda x: (x.importance * x.emotional_weight, x.timestamp), reverse=True)
            self.long_term[role_id] = self.long_term[role_id][:100]
        
        logger.info(f"📝 Long-term memory added: {role_id} - {tipe}: {judul[:50]} (imp={importance}, emo={emotional_weight:.1f})")
    
    def add_role_knowledge(self, role_id: str, fact: str) -> None:
        """Tambah fakta yang diketahui role tertentu"""
        if role_id not in self.role_knowledge:
            self.role_knowledge[role_id] = set()
        self.role_knowledge[role_id].add(fact)
        logger.debug(f"📖 {role_id} learned: {fact[:50]}")
    
    # =========================================================================
    # RECALL MEMORY
    # =========================================================================
    
    def recall_memories(self, role_id: str, context: str, max_memories: int = 3) -> List[str]:
        """
        Recall memories using priority system.
        Returns list of memory contents yang paling relevan.
        """
        priority = self._get_priority_memory(role_id)
        return priority.recall(context, max_memories)
    
    def get_relevant_memories(self, role_id: str, context: str, max_memories: int = 5) -> List[Dict]:
        """
        Get relevant memories with full details.
        """
        recalled_texts = self.recall_memories(role_id, context, max_memories)
        result = []
        
        # Find matching long-term memories
        if role_id in self.long_term:
            for mem in self.long_term[role_id]:
                for recalled in recalled_texts:
                    if recalled in mem.konten or recalled in mem.judul:
                        result.append(mem.to_dict())
                        break
        
        # Add short-term if not enough
        if len(result) < max_memories:
            for event in self.short_term[-max_memories:]:
                if event.role_id == role_id or event.source == "user":
                    result.append(event.to_dict())
                    if len(result) >= max_memories:
                        break
        
        return result[:max_memories]
    
    # =========================================================================
    # GET MEMORY (FILTERED)
    # =========================================================================
    
    def get_short_term(self, count: int = 10, role_id: str = None) -> List[Dict]:
        """
        Dapatkan short-term memory.
        Jika role_id diberikan, filter berdasarkan awareness level.
        """
        if not self.short_term:
            return []
        
        recent = self.short_term[-count:]
        
        if role_id and self.world:
            # Filter berdasarkan awareness level role
            awareness = self.world.role_awareness.get(role_id)
            if awareness:
                filtered = []
                for event in recent:
                    # Role dengan LIMITED hanya tahu event publik
                    if awareness.awareness_level == AwarenessLevel.LIMITED:
                        if event.source == "user" or "public" in event.tags:
                            filtered.append(event.to_dict())
                    # NORMAL tahu lebih banyak
                    elif awareness.awareness_level == AwarenessLevel.NORMAL:
                        if event.source != "intimate" or "private" not in event.tags:
                            filtered.append(event.to_dict())
                    # FULL tahu semua
                    else:
                        filtered.append(event.to_dict())
                return filtered
        
        return [e.to_dict() for e in recent]
    
    def get_short_term_text(self, count: int = 10, role_id: str = None) -> str:
        """Dapatkan short-term memory dalam format teks untuk prompt"""
        events = self.get_short_term(count, role_id)
        
        if not events:
            return "Belum ada kejadian."
        
        lines = [
            "═══════════════════════════════════════════════════════════════",
            "⚠️ KEJADIAN TERAKHIR (WAJIB DIPERHATIKAN!):",
            "═══════════════════════════════════════════════════════════════"
        ]
        
        for i, e in enumerate(events, 1):
            lines.append(f"{i}. [{e['waktu']}] {e['kejadian']}")
            if e['detail']:
                lines.append(f"   └─ {e['detail']}")
        
        return "\n".join(lines)
    
    def get_long_term(self, role_id: str = "nova", tipe: str = None, limit: int = 5) -> List[Dict]:
        """Dapatkan long-term memory untuk role tertentu"""
        memories = self.long_term.get(role_id, [])
        
        if tipe:
            memories = [m for m in memories if m.tipe == tipe]
        
        # Urutkan berdasarkan importance * emotional_weight dan timestamp
        memories.sort(key=lambda x: (x.importance * x.emotional_weight, x.timestamp), reverse=True)
        
        return [m.to_dict() for m in memories[:limit]]
    
    def get_long_term_text(self, role_id: str = "nova") -> str:
        """Dapatkan long-term memory dalam format teks untuk prompt"""
        moments = self.get_long_term(role_id, "momen_penting", 5)
        habits = self.get_long_term(role_id, "kebiasaan_mas", 5)
        promises = self.get_long_term(role_id, "janji", 3)
        
        lines = []
        
        if moments:
            lines.append("📝 MOMEN PENTING:")
            for m in moments:
                lines.append(f"- {m['judul']} (rasanya: {m['perasaan']})")
        
        if habits:
            lines.append("\n📝 KEBIASAAN USER:")
            for h in habits:
                lines.append(f"- {h['judul']}")
        
        if promises:
            lines.append("\n📝 JANJI YANG BELUM DITEPATI:")
            for p in promises[:3]:
                lines.append(f"- {p['judul']}")
        
        return "\n".join(lines) if lines else "Belum ada memory jangka panjang."
    
    def get_global_timeline(self, count: int = 20) -> List[Dict]:
        """Dapatkan timeline global"""
        return [e.to_dict() for e in self.global_timeline[-count:]]
    
    def get_role_knowledge(self, role_id: str) -> List[str]:
        """Dapatkan fakta yang diketahui role"""
        return list(self.role_knowledge.get(role_id, set()))
    
    # =========================================================================
    # CONTEXT FOR PROMPT (FILTERED BY ROLE)
    # =========================================================================
    
    def get_context_for_role(self, role_id: str, include_timeline: bool = True) -> str:
        """
        Dapatkan konteks lengkap untuk prompt AI role tertentu.
        Memory sudah difilter sesuai awareness level role.
        """
        parts = []
        
        # Timeline
        if include_timeline:
            timeline_text = self.get_short_term_text(10, role_id)
            parts.append(timeline_text)
        
        # Recalled memories (priority recall)
        recalled = self.recall_memories(role_id, timeline_text, 3)
        if recalled:
            parts.append(f"\n{'─'*70}\n📌 YANG DIINGAT (PENTING):")
            for r in recalled[:3]:
                parts.append(f"  • {r[:100]}")
        
        # Long-term memory
        long_term_text = self.get_long_term_text(role_id)
        if long_term_text:
            parts.append(f"\n{'─'*70}\n💭 MEMORY JANGKA PANJANG:\n{long_term_text}")
        
        # Role knowledge (fakta yang diketahui)
        knowledge = self.get_role_knowledge(role_id)
        if knowledge:
            parts.append(f"\n{'─'*70}\n📖 FAKTA YANG KAMU KETAHUI:")
            for k in knowledge[:10]:
                parts.append(f"  • {k[:80]}")
        
        # Current state dari tracker
        if self.tracker:
            parts.append(f"\n{self.tracker.get_context_for_prompt()}")
        
        return "\n".join(parts)
    
    # =========================================================================
    # CROSS-ROLE MEMORY PROPAGATION
    # =========================================================================
    
    def propagate_to_other_roles(self, event: MemoryEvent, exclude_role: str = None) -> None:
        """
        Propagate event ke role lain berdasarkan awareness level.
        Ini adalah inti dari cross-role effect di level memory.
        """
        if not self.world:
            return
        
        for role_id, awareness in self.world.role_awareness.items():
            if role_id == exclude_role:
                continue
            
            # Cek apakah role ini boleh tahu event ini
            can_know = False
            
            if awareness.awareness_level == AwarenessLevel.FULL:
                can_know = True
            elif awareness.awareness_level == AwarenessLevel.NORMAL:
                # NORMAL tahu event publik dan event dengan tag tertentu
                if event.source == "user" or "public" in event.tags:
                    can_know = True
            elif awareness.awareness_level == AwarenessLevel.LIMITED:
                # LIMITED hanya tahu event publik
                if event.source == "user":
                    can_know = True
            
            if can_know:
                # Tambah ke knowledge role
                fact = f"{event.source} {event.kejadian}"
                self.add_role_knowledge(role_id, fact[:100])
                
                # Jika event penting, tambah ke long-term role
                if event.importance >= 7 or event.drama_impact > 10:
                    self.add_long_term_memory(
                        tipe="momen_penting",
                        judul=event.kejadian[:50],
                        konten=event.detail[:100],
                        role_id=role_id,
                        importance=event.importance,
                        emotional_weight=event.emotional_weight
                    )
    
    # =========================================================================
    # MEMORY MAINTENANCE
    # =========================================================================
    
    def cleanup_old_memories(self, max_age_days: int = 30) -> None:
        """Bersihkan memory lama"""
        now = time.time()
        cutoff = now - (max_age_days * 24 * 3600)
        
        # Bersihkan global timeline
        self.global_timeline = [e for e in self.global_timeline if e.timestamp > cutoff]
        
        # Bersihkan short-term (sliding window, sudah otomatis)
        
        logger.info(f"🧹 Memory cleanup: kept {len(self.global_timeline)} global events")
    
    def increment_recall_count(self, role_id: str, memory_content: str) -> None:
        """Increment recall count for a memory"""
        if role_id in self.long_term:
            for mem in self.long_term[role_id]:
                if memory_content in mem.konten or memory_content in mem.judul:
                    mem.recall_count += 1
                    mem.last_recalled = time.time()
                    break
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik memory"""
        return {
            'total_events': self.total_events,
            'short_term_count': len(self.short_term),
            'global_timeline_count': len(self.global_timeline),
            'long_term_by_role': {k: len(v) for k, v in self.long_term.items()},
            'role_knowledge': {k: len(v) for k, v in self.role_knowledge.items()},
            'created_at': self.created_at
        }
    
    def format_stats(self) -> str:
        """Format statistik untuk display"""
        stats = self.get_stats()
        
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║                    🧠 MEMORY STATISTICS                      ║",
            "╠══════════════════════════════════════════════════════════════╣",
            f"║ TOTAL EVENTS: {stats['total_events']}                                           ║",
            f"║ SHORT-TERM: {stats['short_term_count']}/50                                        ║",
            f"║ GLOBAL TIMELINE: {stats['global_timeline_count']}                                      ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║ LONG-TERM MEMORY BY ROLE:                                  ║"
        ]
        
        for role_id, count in stats['long_term_by_role'].items():
            if count > 0:
                lines.append(f"║   {role_id}: {count}                                          ║")
        
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        lines.append("║ ROLE KNOWLEDGE:                                              ║")
        
        for role_id, count in stats['role_knowledge'].items():
            if count > 0:
                lines.append(f"║   {role_id}: {count} facts                                      ║")
        
        lines.append("╚══════════════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        return {
            'short_term': [e.to_dict() for e in self.short_term],
            'global_timeline': [e.to_dict() for e in self.global_timeline[-100:]],
            'long_term': {k: [m.to_dict() for m in v] for k, v in self.long_term.items()},
            'role_knowledge': {k: list(v) for k, v in self.role_knowledge.items()},
            'total_events': self.total_events,
            'created_at': self.created_at
        }
    
    def from_dict(self, data: Dict, tracker: StateTracker = None, world: WorldState = None) -> None:
        """Load dari dict"""
        self.tracker = tracker
        self.world = world
        
        # Load short-term
        self.short_term = []
        for e_data in data.get('short_term', []):
            event = MemoryEvent(
                timestamp=e_data.get('timestamp', time.time()),
                waktu=e_data.get('waktu', ''),
                kejadian=e_data.get('kejadian', ''),
                detail=e_data.get('detail', ''),
                source=e_data.get('source', ''),
                role_id=e_data.get('role_id', 'nova'),
                drama_impact=e_data.get('drama_impact', 0),
                importance=e_data.get('importance', 5),
                emotional_weight=e_data.get('emotional_weight', 0),
                intimacy_phase=e_data.get('intimacy_phase', 'none'),
                location=e_data.get('location', ''),
                tags=set(e_data.get('tags', []))
            )
            self.short_term.append(event)
        
        # Load long-term
        long_data = data.get('long_term', {})
        for role_id, memories in long_data.items():
            if role_id not in self.long_term:
                self.long_term[role_id] = []
            for m_data in memories:
                memory = LongTermMemory(
                    tipe=m_data.get('tipe', ''),
                    judul=m_data.get('judul', ''),
                    konten=m_data.get('konten', ''),
                    perasaan=m_data.get('perasaan', ''),
                    timestamp=m_data.get('timestamp', time.time()),
                    role_id=m_data.get('role_id', role_id),
                    importance=m_data.get('importance', 5),
                    emotional_weight=m_data.get('emotional_weight', 0),
                    recall_count=m_data.get('recall_count', 0),
                    last_recalled=m_data.get('last_recalled', 0)
                )
                self.long_term[role_id].append(memory)
        
        # Load role knowledge
        knowledge_data = data.get('role_knowledge', {})
        for role_id, facts in knowledge_data.items():
            if role_id not in self.role_knowledge:
                self.role_knowledge[role_id] = set()
            self.role_knowledge[role_id] = set(facts)
        
        self.total_events = data.get('total_events', len(self.short_term))
        self.created_at = data.get('created_at', time.time())
        
        logger.info(f"🧠 Memory Manager loaded: {len(self.short_term)} short-term, {self.total_events} total events")


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


def reset_memory_manager() -> None:
    """Reset memory manager (untuk testing)"""
    global _memory_manager
    _memory_manager = None
    logger.info("🔄 Memory Manager reset")


__all__ = [
    'MemoryEvent',
    'LongTermMemory',
    'MemoryManager',
    'get_memory_manager',
    'reset_memory_manager'
]
