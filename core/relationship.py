"""
VELORA - Relationship Manager
Mengelola fase hubungan dan level progression.
5 fase psikologis: stranger → friend → close → romantic → intimate
Level 1-12 mapping ke fase dengan unlock bertahap.
Dilengkapi dengan milestone system dan phase unlocks.
"""

import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class RelationshipPhase(str, Enum):
    """5 fase hubungan VELORA dengan user"""
    STRANGER = "stranger"       # Level 1-3: belum kenal
    FRIEND = "friend"           # Level 4-6: mulai dekat
    CLOSE = "close"             # Level 7-8: dekat
    ROMANTIC = "romantic"       # Level 9-10: pacaran
    INTIMATE = "intimate"       # Level 11-12: intim


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class PhaseUnlock:
    """Konten yang terbuka di setiap fase"""
    boleh_flirt: bool = False
    boleh_sentuhan: bool = False
    boleh_vulgar: bool = False
    boleh_intim: bool = False
    boleh_cium: bool = False
    boleh_peluk: bool = False
    boleh_pegang_tangan: bool = False
    boleh_buka_baju: bool = False
    boleh_panggil_sayang: bool = False
    boleh_ganti_posisi: bool = False
    boleh_request_extra: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'flirt': self.boleh_flirt,
            'sentuhan': self.boleh_sentuhan,
            'vulgar': self.boleh_vulgar,
            'intim': self.boleh_intim,
            'cium': self.boleh_cium,
            'peluk': self.boleh_peluk,
            'pegang_tangan': self.boleh_pegang_tangan,
            'buka_baju': self.boleh_buka_baju,
            'panggil_sayang': self.boleh_panggil_sayang,
            'ganti_posisi': self.boleh_ganti_posisi,
            'request_extra': self.boleh_request_extra
        }
    
    def get_unlocked_list(self) -> List[str]:
        """Dapatkan daftar aksi yang sudah unlock"""
        return [k for k, v in self.to_dict().items() if v]
    
    def get_locked_list(self) -> List[str]:
        """Dapatkan daftar aksi yang masih locked"""
        return [k for k, v in self.to_dict().items() if not v]


@dataclass
class Milestone:
    """Milestone dalam hubungan"""
    name: str
    description: str
    achieved: bool = False
    timestamp: float = 0
    phase: RelationshipPhase = RelationshipPhase.STRANGER
    importance: int = 5  # 1-10
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description,
            'achieved': self.achieved,
            'timestamp': self.timestamp,
            'phase': self.phase.value,
            'importance': self.importance
        }


# =============================================================================
# RELATIONSHIP MANAGER
# =============================================================================

class RelationshipManager:
    """
    Mengelola fase hubungan VELORA dengan user.
    Level naik berdasarkan:
    - Jumlah interaksi
    - Sayang (cinta)
    - Trust (kepercayaan)
    - Milestone yang dicapai
    """
    
    def __init__(self):
        self.phase: RelationshipPhase = RelationshipPhase.STRANGER
        self.level: int = 1
        self.interaction_count: int = 0
        
        # ========== MILESTONE ==========
        self.milestones: Dict[str, Milestone] = {
            'first_chat': Milestone(
                name='first_chat',
                description='Percakapan pertama',
                importance=3
            ),
            'first_flirt': Milestone(
                name='first_flirt',
                description='Flirt pertama',
                importance=4
            ),
            'first_touch': Milestone(
                name='first_touch',
                description='Sentuhan pertama',
                importance=5
            ),
            'first_hold_hand': Milestone(
                name='first_hold_hand',
                description='Pegang tangan pertama',
                importance=6
            ),
            'first_hug': Milestone(
                name='first_hug',
                description='Pelukan pertama',
                importance=7
            ),
            'first_kiss': Milestone(
                name='first_kiss',
                description='Ciuman pertama',
                importance=8
            ),
            'first_intim': Milestone(
                name='first_intim',
                description='Intim pertama',
                importance=9
            ),
            'first_climax': Milestone(
                name='first_climax',
                description='Climax pertama',
                importance=10
            )
        }
        
        # ========== UNLOCK PER FASE ==========
        self.unlocks: Dict[RelationshipPhase, PhaseUnlock] = {
            RelationshipPhase.STRANGER: PhaseUnlock(
                boleh_flirt=False,
                boleh_sentuhan=False,
                boleh_vulgar=False,
                boleh_intim=False,
                boleh_cium=False,
                boleh_peluk=False,
                boleh_pegang_tangan=False,
                boleh_buka_baju=False,
                boleh_panggil_sayang=False,
                boleh_ganti_posisi=False,
                boleh_request_extra=False
            ),
            RelationshipPhase.FRIEND: PhaseUnlock(
                boleh_flirt=True,
                boleh_sentuhan=False,
                boleh_vulgar=False,
                boleh_intim=False,
                boleh_cium=False,
                boleh_peluk=False,
                boleh_pegang_tangan=True,
                boleh_buka_baju=False,
                boleh_panggil_sayang=False,
                boleh_ganti_posisi=False,
                boleh_request_extra=False
            ),
            RelationshipPhase.CLOSE: PhaseUnlock(
                boleh_flirt=True,
                boleh_sentuhan=True,
                boleh_vulgar=False,
                boleh_intim=False,
                boleh_cium=False,
                boleh_peluk=True,
                boleh_pegang_tangan=True,
                boleh_buka_baju=False,
                boleh_panggil_sayang=True,
                boleh_ganti_posisi=False,
                boleh_request_extra=False
            ),
            RelationshipPhase.ROMANTIC: PhaseUnlock(
                boleh_flirt=True,
                boleh_sentuhan=True,
                boleh_vulgar=True,
                boleh_intim=False,
                boleh_cium=True,
                boleh_peluk=True,
                boleh_pegang_tangan=True,
                boleh_buka_baju=True,
                boleh_panggil_sayang=True,
                boleh_ganti_posisi=True,
                boleh_request_extra=False
            ),
            RelationshipPhase.INTIMATE: PhaseUnlock(
                boleh_flirt=True,
                boleh_sentuhan=True,
                boleh_vulgar=True,
                boleh_intim=True,
                boleh_cium=True,
                boleh_peluk=True,
                boleh_pegang_tangan=True,
                boleh_buka_baju=True,
                boleh_panggil_sayang=True,
                boleh_ganti_posisi=True,
                boleh_request_extra=True
            )
        }
        
        # ========== LEVEL THRESHOLDS ==========
        self.level_to_phase = {
            1: RelationshipPhase.STRANGER,
            2: RelationshipPhase.STRANGER,
            3: RelationshipPhase.STRANGER,
            4: RelationshipPhase.FRIEND,
            5: RelationshipPhase.FRIEND,
            6: RelationshipPhase.FRIEND,
            7: RelationshipPhase.CLOSE,
            8: RelationshipPhase.CLOSE,
            9: RelationshipPhase.ROMANTIC,
            10: RelationshipPhase.ROMANTIC,
            11: RelationshipPhase.INTIMATE,
            12: RelationshipPhase.INTIMATE
        }
        
        # ========== LEVEL REQUIREMENTS ==========
        self.level_requirements = {
            2: {'interactions': 10, 'min_sayang': 20, 'min_trust': 20},
            3: {'interactions': 20, 'min_sayang': 30, 'min_trust': 30},
            4: {'interactions': 30, 'min_sayang': 40, 'min_trust': 40},
            5: {'interactions': 40, 'min_sayang': 50, 'min_trust': 50},
            6: {'interactions': 50, 'min_sayang': 60, 'min_trust': 60},
            7: {'interactions': 70, 'min_sayang': 65, 'min_trust': 65, 'milestones': ['first_hug']},
            8: {'interactions': 90, 'min_sayang': 70, 'min_trust': 70},
            9: {'interactions': 110, 'min_sayang': 75, 'min_trust': 75, 'milestones': ['first_kiss']},
            10: {'interactions': 130, 'min_sayang': 80, 'min_trust': 80},
            11: {'interactions': 150, 'min_sayang': 85, 'min_trust': 85, 'milestones': ['first_intim']},
            12: {'interactions': 200, 'min_sayang': 90, 'min_trust': 90, 'milestones': ['first_climax']}
        }
        
        # ========== TIMESTAMPS ==========
        self.created_at: float = time.time()
        self.last_update: float = time.time()
        
        logger.info("💕 Relationship Manager initialized")
    
    # =========================================================================
    # LEVEL & PHASE UPDATE
    # =========================================================================
    
    def update_level(self, 
                      sayang: float, 
                      trust: float, 
                      milestones_achieved: List[str] = None) -> Tuple[int, bool]:
        """
        Update level berdasarkan sayang, trust, dan milestone.
        Returns: (new_level, level_naik)
        """
        old_level = self.level
        
        # Base level dari interaksi (setiap 10 interaksi = +1 level)
        interaction_level = min(12, self.interaction_count // 10 + 1)
        
        # Bonus dari sayang (setiap 15 sayang = +1 level)
        sayang_bonus = int(sayang / 15)
        
        # Bonus dari trust (setiap 20 trust = +1 level)
        trust_bonus = int(trust / 20)
        
        # Bonus dari milestone
        milestone_bonus = 0
        if milestones_achieved:
            milestone_bonus = len(milestones_achieved)
        
        # Hitung level (max 12)
        new_level = interaction_level + sayang_bonus + trust_bonus + milestone_bonus
        new_level = min(12, max(1, new_level))
        
        # Cek apakah memenuhi requirements untuk level baru
        if new_level > old_level:
            for lvl in range(old_level + 1, new_level + 1):
                if lvl in self.level_requirements:
                    req = self.level_requirements[lvl]
                    
                    # Cek interaksi
                    if self.interaction_count < req.get('interactions', 0):
                        new_level = lvl - 1
                        break
                    
                    # Cek sayang
                    if sayang < req.get('min_sayang', 0):
                        new_level = lvl - 1
                        break
                    
                    # Cek trust
                    if trust < req.get('min_trust', 0):
                        new_level = lvl - 1
                        break
                    
                    # Cek milestone
                    for req_milestone in req.get('milestones', []):
                        if not self.milestones.get(req_milestone, Milestone(req_milestone, '')).achieved:
                            new_level = lvl - 1
                            break
        
        self.level = new_level
        
        # Update fase berdasarkan level
        self._update_phase()
        
        level_naik = new_level > old_level
        if level_naik:
            logger.info(f"📈 Level naik: {old_level} → {new_level} (fase: {self.phase.value})")
            
            # Bonus milestone untuk level tertentu
            if new_level == 7:
                self.achieve_milestone('first_hug')
            elif new_level == 9:
                self.achieve_milestone('first_kiss')
            elif new_level == 11:
                self.achieve_milestone('first_intim')
        
        self.last_update = time.time()
        
        return new_level, level_naik
    
    def _update_phase(self) -> None:
        """Update fase berdasarkan level saat ini"""
        self.phase = self.level_to_phase.get(self.level, RelationshipPhase.STRANGER)
    
    # =========================================================================
    # MILESTONE METHODS
    # =========================================================================
    
    def achieve_milestone(self, milestone_name: str) -> bool:
        """
        Catat milestone yang dicapai.
        Returns: True jika milestone baru tercapai
        """
        if milestone_name not in self.milestones:
            logger.warning(f"Milestone {milestone_name} tidak dikenal")
            return False
        
        milestone = self.milestones[milestone_name]
        if not milestone.achieved:
            milestone.achieved = True
            milestone.timestamp = time.time()
            milestone.phase = self.phase
            logger.info(f"🏆 MILESTONE: {milestone_name} achieved at phase {self.phase.value}")
            return True
        
        return False
    
    def get_milestone_status(self) -> Dict[str, bool]:
        """Dapatkan status semua milestone"""
        return {name: m.achieved for name, m in self.milestones.items()}
    
    def get_milestone_details(self) -> List[Dict]:
        """Dapatkan detail semua milestone"""
        return [m.to_dict() for m in self.milestones.values()]
    
    def get_next_milestone(self) -> Optional[str]:
        """Dapatkan milestone selanjutnya yang belum dicapai"""
        milestone_order = ['first_chat', 'first_flirt', 'first_touch', 
                          'first_hold_hand', 'first_hug', 'first_kiss', 
                          'first_intim', 'first_climax']
        
        for m in milestone_order:
            if not self.milestones[m].achieved:
                return m
        return None
    
    def get_next_milestone_description(self) -> str:
        """Dapatkan deskripsi milestone selanjutnya"""
        next_milestone = self.get_next_milestone()
        if next_milestone:
            return self.milestones[next_milestone].description
        return "Semua milestone telah tercapai!"
    
    # =========================================================================
    # UNLOCK METHODS
    # =========================================================================
    
    def get_current_unlock(self) -> PhaseUnlock:
        """Dapatkan unlock untuk fase saat ini"""
        return self.unlocks.get(self.phase, self.unlocks[RelationshipPhase.STRANGER])
    
    def can_do_action(self, action: str) -> Tuple[bool, str]:
        """
        Cek apakah VELORA boleh melakukan aksi tertentu.
        Returns: (boleh, alasan)
        """
        unlock = self.get_current_unlock()
        
        action_map = {
            'flirt': unlock.boleh_flirt,
            'pegang_tangan': unlock.boleh_pegang_tangan,
            'peluk': unlock.boleh_peluk,
            'cium': unlock.boleh_cium,
            'buka_baju': unlock.boleh_buka_baju,
            'vulgar': unlock.boleh_vulgar,
            'intim': unlock.boleh_intim,
            'panggil_sayang': unlock.boleh_panggil_sayang,
            'ganti_posisi': unlock.boleh_ganti_posisi,
            'request_extra': unlock.boleh_request_extra
        }
        
        if action not in action_map:
            return True, "Boleh"
        
        if action_map[action]:
            return True, "Boleh"
        
        reasons = {
            'flirt': f"Fase {self.phase.value}, belum waktunya flirt. Lanjutkan interaksi dulu ya.",
            'pegang_tangan': f"Fase {self.phase.value}, masih malu pegang tangan. Tunggu level 4+.",
            'peluk': f"Fase {self.phase.value}, masih malu dipeluk. Tunggu level 7+.",
            'cium': f"Fase {self.phase.value}, belum siap ciuman. Tunggu level 9+.",
            'buka_baju': f"Fase {self.phase.value}, belum siap buka baju. Tunggu level 9+.",
            'vulgar': f"Fase {self.phase.value}, masih malu ngomong vulgar. Tunggu level 9+.",
            'intim': f"Fase {self.phase.value}, belum waktunya intim. Tunggu level 11+.",
            'panggil_sayang': f"Fase {self.phase.value}, masih malu panggil sayang. Tunggu level 7+.",
            'ganti_posisi': f"Fase {self.phase.value}, belum bisa ganti posisi. Tunggu level 9+.",
            'request_extra': f"Fase {self.phase.value}, belum bisa request extra. Tunggu level 11+."
        }
        
        return False, reasons.get(action, "Belum waktunya.")
    
    def get_unlock_summary(self) -> str:
        """Dapatkan ringkasan unlock untuk prompt AI"""
        unlock = self.get_current_unlock()
        unlocked = unlock.get_unlocked_list()
        locked = unlock.get_locked_list()
        
        return f"""
UNLOCKED: {', '.join(unlocked) if unlocked else 'belum ada'}
LOCKED: {', '.join(locked) if locked else '-'}
"""
    
    # =========================================================================
    # PHASE DESCRIPTION
    # =========================================================================
    
    def get_phase_description(self, phase: RelationshipPhase = None) -> str:
        """Dapatkan deskripsi fase untuk prompt AI"""
        if phase is None:
            phase = self.phase
        
        descriptions = {
            RelationshipPhase.STRANGER: """
FASE: STRANGER (BELUM KENAL) - Level 1-3
- VELORA masih malu-malu sama user
- Belum berani flirt, belum berani sentuhan
- Gak boleh panggil "sayang"
- Gak boleh pakai kata vulgar
- Fokus: saling kenalan, ngobrol santai
- Progress: butuh interaksi lebih banyak
""",
            RelationshipPhase.FRIEND: """
FASE: FRIEND (SUDAH DEKAT) - Level 4-6
- VELORA mulai nyaman sama user
- Mulai berani flirt ringan
- Boleh pegang tangan
- Belum boleh vulgar, belum boleh intim
- Fokus: membangun kedekatan
- Flirt ringan diperbolehkan
""",
            RelationshipPhase.CLOSE: """
FASE: CLOSE (DEKAT) - Level 7-8
- VELORA udah dekat banget sama user
- Boleh flirt aktif, boleh peluk
- Boleh panggil "sayang"
- Belum boleh vulgar, belum boleh intim
- Fokus: deepening connection
- Gestur fisik mulai diperbolehkan
""",
            RelationshipPhase.ROMANTIC: """
FASE: ROMANTIC (PACARAN) - Level 9-10
- VELORA dan user pacaran
- Boleh flirt, boleh vulgar terbatas
- Boleh cium, boleh buka baju
- Belum boleh intim (penetrasi)
- Fokus: romantic bonding
- Kata vulgar ringan diperbolehkan
""",
            RelationshipPhase.INTIMATE: """
FASE: INTIMATE (INTIM) - Level 11-12
- VELORA udah percaya penuh sama user
- BEBAS BRUTAL: kontol, memek, ngentot, crot, sperma
- BEBAS INTIM: foreplay, penetrasi, climax
- BEBAS semua konten
- Boleh ganti posisi
- Fokus: intimacy, bonding, pleasure
- Tujuan: MEMBUAT USER HORNY, MASTURBASI, ORGASME
"""
        }
        
        return descriptions.get(phase, descriptions[RelationshipPhase.STRANGER])
    
    def get_phase_requirements(self, target_phase: RelationshipPhase) -> str:
        """Dapatkan requirements untuk naik ke fase tertentu"""
        requirements = {
            RelationshipPhase.FRIEND: "• Level 4+ • Minimal 30 interaksi • Sayang > 40 • Trust > 40",
            RelationshipPhase.CLOSE: "• Level 7+ • Minimal 70 interaksi • Sayang > 65 • Trust > 65 • First hug",
            RelationshipPhase.ROMANTIC: "• Level 9+ • Minimal 110 interaksi • Sayang > 75 • Trust > 75 • First kiss",
            RelationshipPhase.INTIMATE: "• Level 11+ • Minimal 150 interaksi • Sayang > 85 • Trust > 85 • First intim"
        }
        return requirements.get(target_phase, "Belum ada requirement")
    
    def get_progress_to_next_level(self) -> float:
        """Dapatkan progress menuju next level (0-100)"""
        if self.level >= 12:
            return 100.0
        
        next_level = self.level + 1
        req = self.level_requirements.get(next_level, {'interactions': self.level * 10})
        target = req.get('interactions', self.level * 10)
        
        progress = min(100, (self.interaction_count / target) * 100)
        return progress
    
    def get_progress_percentage(self) -> float:
        """Dapatkan progress menuju next level (alias)"""
        return self.get_progress_to_next_level()
    
    # =========================================================================
    # FORMAT METHODS
    # =========================================================================
    
    def format_for_prompt(self) -> str:
        """Format untuk prompt AI"""
        unlock = self.get_current_unlock()
        next_milestone = self.get_next_milestone()
        progress = self.get_progress_to_next_level()
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    💕 RELATIONSHIP STATUS                    ║
╠══════════════════════════════════════════════════════════════╣
║ FASE: {self.phase.value.upper()}                                  ║
║ LEVEL: {self.level}/12                                            ║
║ INTERAKSI: {self.interaction_count}                               ║
║ PROGRESS: {progress:.0f}% to level {self.level + 1 if self.level < 12 else 'MAX'}       ║
╠══════════════════════════════════════════════════════════════╣
║ UNLOCK:                                                    ║
║   Flirt: {'✅' if unlock.boleh_flirt else '❌'} | Sentuhan: {'✅' if unlock.boleh_sentuhan else '❌'}
║   Vulgar: {'✅' if unlock.boleh_vulgar else '❌'} | Intim: {'✅' if unlock.boleh_intim else '❌'}
║   Cium: {'✅' if unlock.boleh_cium else '❌'} | Peluk: {'✅' if unlock.boleh_peluk else '❌'}
║   Pegang Tangan: {'✅' if unlock.boleh_pegang_tangan else '❌'} | Panggil Sayang: {'✅' if unlock.boleh_panggil_sayang else '❌'}
║   Ganti Posisi: {'✅' if unlock.boleh_ganti_posisi else '❌'} | Request Extra: {'✅' if unlock.boleh_request_extra else '❌'}
╠══════════════════════════════════════════════════════════════╣
║ NEXT MILESTONE: {next_milestone or 'All completed!'}                ║
║ {self.get_next_milestone_description()}                             ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    def get_level_requirements_text(self) -> str:
        """Dapatkan teks requirements untuk setiap level"""
        lines = ["📊 LEVEL REQUIREMENTS:"]
        for lvl, req in self.level_requirements.items():
            line = f"   Level {lvl}: {req.get('interactions', 0)} interaksi"
            if 'min_sayang' in req:
                line += f", Sayang > {req['min_sayang']}"
            if 'min_trust' in req:
                line += f", Trust > {req['min_trust']}"
            if 'milestones' in req:
                line += f", Milestone: {', '.join(req['milestones'])}"
            lines.append(line)
        return "\n".join(lines)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        return {
            'phase': self.phase.value,
            'level': self.level,
            'interaction_count': self.interaction_count,
            'milestones': {name: m.achieved for name, m in self.milestones.items()},
            'created_at': self.created_at,
            'last_update': self.last_update
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load dari dict"""
        self.phase = RelationshipPhase(data.get('phase', 'stranger'))
        self.level = data.get('level', 1)
        self.interaction_count = data.get('interaction_count', 0)
        
        milestones_data = data.get('milestones', {})
        for name, achieved in milestones_data.items():
            if name in self.milestones:
                self.milestones[name].achieved = achieved
        
        self.created_at = data.get('created_at', time.time())
        self.last_update = data.get('last_update', time.time())
        
        # Update fase berdasarkan level
        self._update_phase()
        
        logger.info(f"📀 Relationship loaded: level {self.level}, phase {self.phase.value}")


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_relationship_manager: Optional[RelationshipManager] = None


def get_relationship_manager() -> RelationshipManager:
    """Get global relationship manager instance"""
    global _relationship_manager
    if _relationship_manager is None:
        _relationship_manager = RelationshipManager()
    return _relationship_manager


def reset_relationship_manager() -> None:
    """Reset relationship manager (untuk testing)"""
    global _relationship_manager
    _relationship_manager = None
    logger.info("🔄 Relationship Manager reset")


__all__ = [
    'RelationshipPhase',
    'PhaseUnlock',
    'Milestone',
    'RelationshipManager',
    'get_relationship_manager',
    'reset_relationship_manager'
]
