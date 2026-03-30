"""
VELORA - Persistent Memory
Semua data disimpan ke SQLite database.
Tidak hilang saat restart.
- State per role (emotional, relationship, conflict)
- Memory (short-term, long-term, timeline)
- World state
- Conversation history
"""

import time
import json
import aiosqlite
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from config import get_settings

logger = logging.getLogger(__name__)


def safe_serialize(obj):
    """Safe serialization untuk object"""
    try:
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        if hasattr(obj, "value"):
            return obj.value
        return str(obj)
    except Exception:
        return str(obj)


# =============================================================================
# PERSISTENT MEMORY
# =============================================================================

class PersistentMemory:
    """
    Persistent Memory - Simpan semua data ke SQLite.
    """
    
    def __init__(self, db_path: Path = None):
        settings = get_settings()
        self.db_path = db_path or settings.database.path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()
        
        logger.info(f"💾 Persistent Memory initialized at {self.db_path}")
    
    # =========================================================================
    # DATABASE INITIALIZATION
    # =========================================================================
    
    async def init(self) -> None:
        """Buat semua tabel database"""
        self._conn = await aiosqlite.connect(str(self.db_path))
        self._conn.row_factory = aiosqlite.Row
        
        await self._conn.execute("PRAGMA journal_mode=WAL;")
        await self._conn.execute("PRAGMA synchronous=NORMAL;")
        await self._conn.execute("PRAGMA busy_timeout=5000;")
        
        # ========== TABEL STATE UTAMA ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS velora_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL WORLD STATE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS world_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                relationship_status TEXT NOT NULL,
                drama_level REAL NOT NULL,
                public_knowledge TEXT NOT NULL,
                role_awareness TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL EMOTIONAL STATE PER ROLE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS emotional_state (
                role_id TEXT PRIMARY KEY,
                sayang REAL NOT NULL,
                rindu REAL NOT NULL,
                trust REAL NOT NULL,
                mood REAL NOT NULL,
                desire REAL NOT NULL,
                arousal REAL NOT NULL,
                tension REAL NOT NULL,
                cemburu REAL NOT NULL,
                kecewa REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL RELATIONSHIP STATE PER ROLE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS relationship_state (
                role_id TEXT PRIMARY KEY,
                phase TEXT NOT NULL,
                level INTEGER NOT NULL,
                interaction_count INTEGER NOT NULL,
                milestones TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL CONFLICT STATE PER ROLE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS conflict_state (
                role_id TEXT PRIMARY KEY,
                cemburu REAL NOT NULL,
                kecewa REAL NOT NULL,
                marah REAL NOT NULL,
                sakit_hati REAL NOT NULL,
                is_cold_war INTEGER NOT NULL,
                is_waiting_for_apology INTEGER NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL ROLE FLAGS ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS role_flags (
                role_id TEXT PRIMARY KEY,
                flags TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL TIMELINE GLOBAL ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                waktu TEXT NOT NULL,
                kejadian TEXT NOT NULL,
                detail TEXT,
                source TEXT NOT NULL,
                role_id TEXT NOT NULL,
                drama_impact REAL DEFAULT 0,
                intimacy_phase TEXT,
                location TEXT,
                tags TEXT
            )
        ''')
        
        # ========== TABEL SHORT-TERM MEMORY ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS short_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                waktu TEXT NOT NULL,
                kejadian TEXT NOT NULL,
                detail TEXT,
                source TEXT NOT NULL,
                role_id TEXT NOT NULL,
                drama_impact REAL DEFAULT 0
            )
        ''')
        
        # ========== TABEL LONG-TERM MEMORY ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipe TEXT NOT NULL,
                judul TEXT NOT NULL,
                konten TEXT NOT NULL,
                perasaan TEXT,
                role_id TEXT NOT NULL,
                importance INTEGER DEFAULT 5,
                timestamp REAL NOT NULL
            )
        ''')
        
        # ========== TABEL ROLE KNOWLEDGE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS role_knowledge (
                role_id TEXT NOT NULL,
                fact TEXT NOT NULL,
                learned_at REAL NOT NULL,
                PRIMARY KEY (role_id, fact)
            )
        ''')
        
        # ========== TABEL CONVERSATION ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT,
                user_id INTEGER
            )
        ''')
        
        # ========== TABEL LOCATION VISITS ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS location_visits (
                id TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                visit_count INTEGER DEFAULT 1,
                last_visit REAL NOT NULL
            )
        ''')
        
        # ========== INDEXES ==========
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_timeline_role ON timeline(role_id)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_timeline_time ON timeline(timestamp)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_long_term_role ON long_term_memory(role_id)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_long_term_tipe ON long_term_memory(tipe)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_conversation_user ON conversation(user_id)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_conversation_time ON conversation(timestamp)')
        
        await self._conn.commit()
        
        # Inisialisasi state awal
        await self._init_state()
        
        logger.info(f"💾 Database initialized at {self.db_path}")
    
    async def _init_state(self) -> None:
        """Inisialisasi state awal jika belum ada"""
        
        # Cek world state
        cursor = await self._conn.execute("SELECT COUNT(*) FROM world_state")
        count = (await cursor.fetchone())[0]
        
        if count == 0:
            await self._conn.execute('''
                INSERT INTO world_state (id, relationship_status, drama_level, public_knowledge, role_awareness, updated_at)
                VALUES (1, 'pacaran', 0, '{}', '{}', ?)
            ''', (time.time(),))
            await self._conn.commit()
            logger.info("📀 World state initialized")
        
        # Cek role knowledge (kosong)
        cursor = await self._conn.execute("SELECT COUNT(*) FROM role_knowledge")
        if (await cursor.fetchone())[0] == 0:
            logger.info("📀 Role knowledge table ready")
    
    # =========================================================================
    # WORLD STATE
    # =========================================================================
    
    async def save_world_state(self, world) -> None:
        """Save world state ke database"""
        try:
            await self._conn.execute('''
                INSERT OR REPLACE INTO world_state 
                (id, relationship_status, drama_level, public_knowledge, role_awareness, updated_at)
                VALUES (1, ?, ?, ?, ?, ?)
            ''', (
                world.relationship_status.value,
                world.drama_level,
                json.dumps(world.public_knowledge.to_dict() if hasattr(world.public_knowledge, 'to_dict') else world.public_knowledge),
                json.dumps({rid: aw.to_dict() for rid, aw in world.role_awareness.items()}),
                time.time()
            ))
            await self._conn.commit()
        except Exception as e:
            logger.error(f"Error saving world state: {e}")
    
    async def load_world_state(self, world) -> bool:
        """Load world state dari database"""
        try:
            cursor = await self._conn.execute(
                "SELECT relationship_status, drama_level, public_knowledge, role_awareness FROM world_state WHERE id = 1"
            )
            row = await cursor.fetchone()
            if row:
                from core.world import GlobalRelationshipStatus
                world.relationship_status = GlobalRelationshipStatus(row[0])
                world.drama_level = row[1]
                
                # Load public knowledge
                pk_data = json.loads(row[2])
                if hasattr(world.public_knowledge, 'from_dict'):
                    world.public_knowledge.from_dict(pk_data)
                
                # Load role awareness
                awareness_data = json.loads(row[3])
                from core.world import RoleAwareness, AwarenessLevel
                for rid, aw_data in awareness_data.items():
                    world.role_awareness[rid] = RoleAwareness(
                        role_id=rid,
                        awareness_level=AwarenessLevel(aw_data.get('awareness_level', 'limited')),
                        known_facts=set(aw_data.get('known_facts', [])),
                        last_updated=aw_data.get('last_updated', time.time())
                    )
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading world state: {e}")
            return False
    
    # =========================================================================
    # ROLE STATE
    # =========================================================================
    
    async def save_role_state(self, role) -> None:
        """Save semua state role ke database"""
        role_id = role.id
        
        # Emotional state
        await self._conn.execute('''
            INSERT OR REPLACE INTO emotional_state 
            (role_id, sayang, rindu, trust, mood, desire, arousal, tension, cemburu, kecewa, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            role_id,
            role.emotional.sayang,
            role.emotional.rindu,
            role.emotional.trust,
            role.emotional.mood,
            role.emotional.desire,
            role.emotional.arousal,
            role.emotional.tension,
            role.emotional.cemburu,
            role.emotional.kecewa,
            time.time()
        ))
        
        # Relationship state
        await self._conn.execute('''
            INSERT OR REPLACE INTO relationship_state 
            (role_id, phase, level, interaction_count, milestones, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            role_id,
            role.relationship.phase.value,
            role.relationship.level,
            role.relationship.interaction_count,
            json.dumps(role.relationship.get_milestone_status()),
            time.time()
        ))
        
        # Conflict state
        await self._conn.execute('''
            INSERT OR REPLACE INTO conflict_state 
            (role_id, cemburu, kecewa, marah, sakit_hati, is_cold_war, is_waiting_for_apology, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            role_id,
            role.conflict.cemburu,
            role.conflict.kecewa,
            role.conflict.marah,
            role.conflict.sakit_hati,
            1 if role.conflict.is_cold_war else 0,
            1 if role.conflict.is_waiting_for_apology else 0,
            time.time()
        ))
        
        # Role flags
        await self._conn.execute('''
            INSERT OR REPLACE INTO role_flags 
            (role_id, flags, updated_at)
            VALUES (?, ?, ?)
        ''', (
            role_id,
            json.dumps(role.flags),
            time.time()
        ))
        
        await self._conn.commit()
    
    async def load_role_state(self, role) -> bool:
        """Load semua state role dari database"""
        role_id = role.id
        loaded = False
        
        # Load emotional state
        cursor = await self._conn.execute(
            "SELECT sayang, rindu, trust, mood, desire, arousal, tension, cemburu, kecewa FROM emotional_state WHERE role_id = ?",
            (role_id,)
        )
        row = await cursor.fetchone()
        if row:
            role.emotional.sayang = row[0]
            role.emotional.rindu = row[1]
            role.emotional.trust = row[2]
            role.emotional.mood = row[3]
            role.emotional.desire = row[4]
            role.emotional.arousal = row[5]
            role.emotional.tension = row[6]
            role.emotional.cemburu = row[7]
            role.emotional.kecewa = row[8]
            loaded = True
        
        # Load relationship state
        cursor = await self._conn.execute(
            "SELECT phase, level, interaction_count, milestones FROM relationship_state WHERE role_id = ?",
            (role_id,)
        )
        row = await cursor.fetchone()
        if row:
            from core.relationship import RelationshipPhase
            role.relationship.phase = RelationshipPhase(row[0])
            role.relationship.level = row[1]
            role.relationship.interaction_count = row[2]
            
            milestones = json.loads(row[3])
            for name, achieved in milestones.items():
                if name in role.relationship.milestones:
                    role.relationship.milestones[name].achieved = achieved
            loaded = True
        
        # Load conflict state
        cursor = await self._conn.execute(
            "SELECT cemburu, kecewa, marah, sakit_hati, is_cold_war, is_waiting_for_apology FROM conflict_state WHERE role_id = ?",
            (role_id,)
        )
        row = await cursor.fetchone()
        if row:
            role.conflict.cemburu = row[0]
            role.conflict.kecewa = row[1]
            role.conflict.marah = row[2]
            role.conflict.sakit_hati = row[3]
            role.conflict.is_cold_war = bool(row[4])
            role.conflict.is_waiting_for_apology = bool(row[5])
            loaded = True
        
        # Load role flags
        cursor = await self._conn.execute(
            "SELECT flags FROM role_flags WHERE role_id = ?",
            (role_id,)
        )
        row = await cursor.fetchone()
        if row:
            role.flags = json.loads(row[0])
            loaded = True
        
        return loaded
    
    # =========================================================================
    # MEMORY
    # =========================================================================
    
    async def save_timeline_event(self, event) -> None:
        """Save timeline event ke database"""
        try:
            await self._conn.execute('''
                INSERT INTO timeline 
                (timestamp, waktu, kejadian, detail, source, role_id, drama_impact, intimacy_phase, location, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.timestamp,
                event.waktu,
                event.kejadian[:500],
                event.detail[:500] if event.detail else "",
                event.source,
                event.role_id,
                event.drama_impact,
                event.intimacy_phase,
                event.location,
                json.dumps(list(event.tags)) if event.tags else None
            ))
            await self._conn.commit()
        except Exception as e:
            logger.error(f"Error saving timeline event: {e}")
    
    async def save_short_term(self, events: List) -> None:
        """Save short-term memory (replace semua)"""
        try:
            # Clear existing
            await self._conn.execute("DELETE FROM short_term_memory")
            
            # Insert new
            for event in events:
                await self._conn.execute('''
                    INSERT INTO short_term_memory 
                    (timestamp, waktu, kejadian, detail, source, role_id, drama_impact)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.timestamp,
                    event.waktu,
                    event.kejadian[:500],
                    event.detail[:500] if event.detail else "",
                    event.source,
                    event.role_id,
                    event.drama_impact
                ))
            
            await self._conn.commit()
        except Exception as e:
            logger.error(f"Error saving short-term memory: {e}")
    
    async def save_long_term_memory(self, memory) -> None:
        """Save long-term memory"""
        try:
            await self._conn.execute('''
                INSERT INTO long_term_memory 
                (tipe, judul, konten, perasaan, role_id, importance, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.tipe,
                memory.judul[:200],
                memory.konten[:500],
                memory.perasaan[:100],
                memory.role_id,
                memory.importance,
                memory.timestamp
            ))
            await self._conn.commit()
        except Exception as e:
            logger.error(f"Error saving long-term memory: {e}")
    
    async def load_long_term_memories(self, role_id: str, limit: int = 100) -> List[Dict]:
        """Load long-term memory untuk role tertentu"""
        cursor = await self._conn.execute('''
            SELECT * FROM long_term_memory 
            WHERE role_id = ? OR role_id = 'nova'
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
        ''', (role_id, limit))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def save_role_knowledge(self, role_id: str, facts: List[str]) -> None:
        """Save role knowledge"""
        try:
            # Clear existing
            await self._conn.execute("DELETE FROM role_knowledge WHERE role_id = ?", (role_id,))
            
            # Insert new
            now = time.time()
            for fact in facts:
                await self._conn.execute('''
                    INSERT INTO role_knowledge (role_id, fact, learned_at)
                    VALUES (?, ?, ?)
                ''', (role_id, fact[:200], now))
            
            await self._conn.commit()
        except Exception as e:
            logger.error(f"Error saving role knowledge: {e}")
    
    async def load_role_knowledge(self, role_id: str) -> List[str]:
        """Load role knowledge"""
        cursor = await self._conn.execute(
            "SELECT fact FROM role_knowledge WHERE role_id = ? ORDER BY learned_at DESC",
            (role_id,)
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    
    # =========================================================================
    # CONVERSATION
    # =========================================================================
    
    async def save_conversation(self, role: str, message: str, response: str = "", user_id: int = None) -> None:
        """Save conversation ke database"""
        try:
            await self._conn.execute('''
                INSERT INTO conversation (timestamp, role, message, response, user_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (time.time(), role, message[:1000], response[:1000], user_id))
            await self._conn.commit()
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
    
    async def get_recent_conversations(self, user_id: int = None, limit: int = 20) -> List[Dict]:
        """Get recent conversations"""
        if user_id:
            cursor = await self._conn.execute('''
                SELECT * FROM conversation 
                WHERE user_id = ? 
                ORDER BY timestamp DESC LIMIT ?
            ''', (user_id, limit))
        else:
            cursor = await self._conn.execute('''
                SELECT * FROM conversation 
                ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows][::-1]
    
    # =========================================================================
    # LOCATION
    # =========================================================================
    
    async def save_location_visit(self, location_id: str, nama: str) -> None:
        """Save location visit"""
        now = time.time()
        await self._conn.execute('''
            INSERT INTO location_visits (id, nama, visit_count, last_visit)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(id) DO UPDATE SET visit_count = visit_count + 1, last_visit = ?
        ''', (location_id, nama, now, now))
        await self._conn.commit()
    
    # =========================================================================
    # STATE UTILITY
    # =========================================================================
    
    async def get_state(self, key: str) -> Optional[str]:
        """Get state by key"""
        cursor = await self._conn.execute("SELECT value FROM velora_state WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row[0] if row else None
    
    async def set_state(self, key: str, value: str) -> None:
        """Set state by key"""
        await self._conn.execute(
            "INSERT OR REPLACE INTO velora_state (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, time.time())
        )
        await self._conn.commit()
    
    # =========================================================================
    # BACKUP & CLEANUP
    # =========================================================================
    
    async def create_backup(self, backup_path: Path) -> bool:
        """Create database backup"""
        try:
            import shutil
            shutil.copy(self.db_path, backup_path)
            logger.info(f"💾 Backup created: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    async def cleanup_old_data(self, days: int = 30) -> None:
        """Cleanup data lebih dari days hari"""
        cutoff = time.time() - (days * 24 * 3600)
        
        # Cleanup timeline
        await self._conn.execute("DELETE FROM timeline WHERE timestamp < ?", (cutoff,))
        
        # Cleanup conversation
        await self._conn.execute("DELETE FROM conversation WHERE timestamp < ?", (cutoff,))
        
        await self._conn.commit()
        logger.info(f"🧹 Cleaned up data older than {days} days")
    
    async def vacuum(self) -> None:
        """Vacuum database"""
        await self._conn.execute("VACUUM")
        logger.info("🧹 Database vacuumed")
    
    async def get_stats(self) -> Dict:
        """Get database statistics"""
        stats = {}
        tables = ['timeline', 'short_term_memory', 'long_term_memory', 'conversation', 'location_visits']
        
        for table in tables:
            cursor = await self._conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = (await cursor.fetchone())[0]
            stats[f"{table}_count"] = count
        
        if self.db_path.exists():
            stats['db_size_mb'] = round(self.db_path.stat().st_size / (1024 * 1024), 2)
        
        return stats
    
    async def close(self) -> None:
        """Close database connection"""
        if self._conn:
            await self._conn.close()
            logger.info("💾 Database connection closed")


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_persistent: Optional[PersistentMemory] = None


async def get_persistent() -> PersistentMemory:
    """Get global persistent memory instance"""
    global _persistent
    if _persistent is None:
        _persistent = PersistentMemory()
        await _persistent.init()
    return _persistent


__all__ = [
    'PersistentMemory',
    'get_persistent'
]
