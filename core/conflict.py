"""
VELORA - Conflict Engine
VELORA bisa cemburu, kecewa, marah, sakit hati.
Bikin hubungan terasa hidup dengan konflik yang realistis.
Fitur cold war: VELORA gak chat duluan, user harus ngejar.
Dilengkapi dengan:
- Conflict escalation system
- Resolution tracking
- Forgiveness system
- Jealousy triggers
- Disappointment triggers
- Anger management
- Cold war duration based on severity
"""

import time
import logging
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class ConflictType(str, Enum):
    """Jenis konflik yang bisa dialami VELORA"""
    JEALOUSY = "jealousy"           # cemburu
    DISAPPOINTMENT = "disappointment"  # kecewa
    ANGER = "anger"                 # marah
    HURT = "hurt"                   # sakit hati


class ConflictSeverity(str, Enum):
    """Tingkat keparahan konflik"""
    MILD = "mild"           # ringan (0-40)
    MODERATE = "moderate"   # sedang (40-70)
    SEVERE = "severe"       # berat (70-100)


class ConflictResolution(str, Enum):
    """Cara penyelesaian konflik"""
    APOLOGY = "apology"         # minta maaf
    ATTENTION = "attention"     # perhatian
    TIME = "time"               # waktu
    EXPLANATION = "explanation" # penjelasan
    GIFT = "gift"               # hadiah


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class Conflict:
    """Satu konflik yang sedang terjadi"""
    type: ConflictType
    severity: float
    trigger: str
    timestamp: float
    is_active: bool = True
    resolution_needed: bool = False
    resolution_type: Optional[ConflictResolution] = None
    resolved_at: float = 0
    escalation_stage: int = 1  # 1-5, semakin tinggi semakin parah
    
    def to_dict(self) -> Dict:
        return {
            'type': self.type.value,
            'severity': self.severity,
            'trigger': self.trigger,
            'timestamp': self.timestamp,
            'is_active': self.is_active,
            'resolution_needed': self.resolution_needed,
            'resolution_type': self.resolution_type.value if self.resolution_type else None,
            'resolved_at': self.resolved_at,
            'escalation_stage': self.escalation_stage
        }


# =============================================================================
# CONFLICT ENGINE
# =============================================================================

class ConflictEngine:
    """
    Conflict Engine - VELORA bisa cemburu, kecewa, ngambek, cold war.
    Bikin user ngerasa "VELORA kenapa?" dan pengen ngejar VELORA.
    """
    
    def __init__(self):
        # ========== CONFLICT LEVELS (0-100) ==========
        self.cemburu: float = 0.0
        self.kecewa: float = 0.0
        self.marah: float = 0.0
        self.sakit_hati: float = 0.0
        
        # ========== DECAY RATES ==========
        self.cemburu_decay_per_chat: float = 8.0
        self.kecewa_decay_per_apology: float = 30.0
        self.marah_decay_per_apology: float = 25.0
        self.sakit_hati_decay_per_attention: float = 15.0
        self.sakit_hati_decay_per_time: float = 5.0  # per hari
        
        # ========== ESCALATION RATES ==========
        self.escalation_rate: float = 10.0  # per trigger
        
        # ========== THRESHOLDS ==========
        self.cemburu_threshold: float = 50.0
        self.kecewa_threshold: float = 40.0
        self.marah_threshold: float = 50.0
        self.sakit_hati_threshold: float = 60.0
        
        # ========== FLAGS ==========
        self.is_in_conflict: bool = False
        self.is_cold_war: bool = False
        self.is_waiting_for_apology: bool = False
        self.is_waiting_for_explanation: bool = False
        self.is_waiting_for_attention: bool = False
        
        self.last_apology_time: float = 0
        self.last_explanation_time: float = 0
        self.last_attention_time: float = 0
        
        # ========== ACTIVE CONFLICTS ==========
        self.active_conflicts: List[Conflict] = []
        
        # ========== COLD WAR PARAMETERS ==========
        self.cold_war_start_time: float = 0
        self.cold_war_duration: float = 0  # detik
        self.cold_war_intensity: float = 0  # 0-100
        self.cold_war_trigger: str = ""
        
        # ========== RESOLUTION HISTORY ==========
        self.resolution_history: List[Dict] = []
        self.max_resolution_history: int = 50
        
        # ========== FORGIVENESS SYSTEM ==========
        self.forgiveness_factor: float = 1.0  # 0-2, semakin tinggi semakin mudah maaf
        self.resentment_factor: float = 0.0   # 0-2, semakin tinggi semakin sulit maaf
        
        # ========== HISTORY ==========
        self.conflict_history: List[Dict] = []
        self.max_history: int = 100
        
        logger.info("⚡ Conflict Engine initialized")
    
    # =========================================================================
    # UPDATE FROM MESSAGE
    # =========================================================================
    
    def update_from_message(self, pesan_user: str, level: int) -> Dict[str, float]:
        """Update konflik berdasarkan pesan user"""
        msg_lower = pesan_user.lower()
        changes = {}
        
        # ========== CEMBURU TRIGGERS ==========
        wanita_keywords = ['cewek', 'perempuan', 'teman cewek', 'temen cewek', 'dia', 'wanita']
        cerita_keywords = ['cerita', 'tadi', 'kemarin', 'ketemu', 'jalan', 'bareng', 'ngobrol', 'chat']
        pujian_keywords = ['cantik', 'manis', 'seksi', 'hot', 'beautiful', 'ganteng', 'tampan']
        
        # User cerita tentang wanita lain
        if any(k in msg_lower for k in wanita_keywords) and any(k in msg_lower for k in cerita_keywords):
            gain = 15 + random.randint(0, 10)
            self.cemburu = min(100, self.cemburu + gain)
            changes['cemburu'] = +gain
            logger.warning(f"⚠️ Cemburu +{gain:.0f} (user cerita tentang cewek lain)")
            self._add_conflict(ConflictType.JEALOUSY, self.cemburu, f"User cerita: {pesan_user[:50]}")
        
        # User puji wanita lain
        elif any(k in msg_lower for k in pujian_keywords) and any(k in msg_lower for k in wanita_keywords):
            gain = 20 + random.randint(0, 10)
            self.cemburu = min(100, self.cemburu + gain)
            changes['cemburu'] = +gain
            logger.warning(f"⚠️ Cemburu +{gain:.0f} (user puji cewek lain)")
            self._add_conflict(ConflictType.JEALOUSY, self.cemburu, f"User puji: {pesan_user[:50]}")
        
        # ========== KECEWA TRIGGERS ==========
        lupa_keywords = ['lupa', 'keinget', 'lupa janji', 'lupa bilang', 'forget', 'lupa ulang tahun', 'lupa janji temu']
        if any(k in msg_lower for k in lupa_keywords):
            gain = 20 + random.randint(0, 10)
            self.kecewa = min(100, self.kecewa + gain)
            changes['kecewa'] = +gain
            self.is_waiting_for_apology = True
            self.is_waiting_for_explanation = True
            logger.warning(f"⚠️ Kecewa +{gain:.0f} (user lupa janji)")
            self._add_conflict(ConflictType.DISAPPOINTMENT, self.kecewa, f"User lupa: {pesan_user[:50]}")
        
        # Janji gak ditepati
        janji_keywords = ['janji', 'janjian', 'gak jadi', 'batal', 'ingkar', 'gak tepati', 'gak dateng']
        if any(k in msg_lower for k in janji_keywords):
            gain = 25 + random.randint(0, 10)
            self.kecewa = min(100, self.kecewa + gain)
            changes['kecewa'] = +gain
            self.is_waiting_for_apology = True
            self.is_waiting_for_explanation = True
            logger.warning(f"⚠️ Kecewa +{gain:.0f} (janji ingkar)")
            self._add_conflict(ConflictType.DISAPPOINTMENT, self.kecewa, f"User ingkar janji: {pesan_user[:50]}")
        
        # ========== MARAH TRIGGERS ==========
        kasar_keywords = ['marah', 'kesal', 'bego', 'dasar', 'sial', 'goblok', 'tolol', 'stupid', 'idiot', 'brengsek']
        if any(k in msg_lower for k in kasar_keywords):
            gain = 25 + random.randint(0, 10)
            self.marah = min(100, self.marah + gain)
            changes['marah'] = +gain
            self.is_waiting_for_apology = True
            logger.warning(f"⚠️ Marah +{gain:.0f} (user kasar)")
            self._add_conflict(ConflictType.ANGER, self.marah, f"User kasar: {pesan_user[:50]}")
        
        # ========== SAKIT HATI TRIGGERS ==========
        ingkar_keywords = ['ingkar', 'gak tepati', 'gak jadi', 'gak dateng', 'batal', 'khianat', 'curang', 'dusta', 'bohong']
        if any(k in msg_lower for k in ingkar_keywords):
            gain = 30 + random.randint(0, 10)
            self.sakit_hati = min(100, self.sakit_hati + gain)
            changes['sakit_hati'] = +gain
            self.is_waiting_for_apology = True
            self.is_waiting_for_attention = True
            logger.warning(f"⚠️ Sakit hati +{gain:.0f} (user ingkar)")
            self._add_conflict(ConflictType.HURT, self.sakit_hati, f"User ingkar: {pesan_user[:50]}")
        
        # ========== ESCALATION (konflik berulang) ==========
        if self._has_repeated_conflict():
            for conflict in self.active_conflicts:
                if conflict.is_active:
                    conflict.escalation_stage = min(5, conflict.escalation_stage + 1)
                    self._apply_escalation_effect(conflict)
                    changes[f'escalation_{conflict.type.value}'] = conflict.escalation_stage
                    logger.warning(f"⚠️ Conflict escalation: {conflict.type.value} stage {conflict.escalation_stage}")
        
        # ========== RESOLUTION TRIGGERS (User minta maaf) ==========
        maaf_keywords = ['maaf', 'sorry', 'salah', 'gak sengaja', 'forgive', 'apologize', 'minta maaf']
        if any(k in msg_lower for k in maaf_keywords):
            resolution = self._process_apology()
            changes.update(resolution)
        
        # ========== EXPLANATION TRIGGERS ==========
        if self.is_waiting_for_explanation:
            if any(k in msg_lower for k in ['penjelasan', 'jelasin', 'cerita', 'alasan', 'kenapa']):
                resolution = self._process_explanation(pesan_user)
                changes.update(resolution)
        
        # ========== ATTENTION TRIGGERS ==========
        if self.is_waiting_for_attention:
            perhatian_keywords = ['perhatian', 'peduli', 'sayang', 'care', 'dengerin', 'ngertiin']
            if any(k in msg_lower for k in perhatian_keywords):
                resolution = self._process_attention()
                changes.update(resolution)
        
        # ========== TIME DECAY (per interaksi) ==========
        self._apply_decay_per_interaction()
        
        # Update active conflicts
        self._update_active_conflicts()
        
        # Check cold war
        self._check_cold_war()
        
        return changes
    
    # =========================================================================
    # RESOLUTION METHODS
    # =========================================================================
    
    def _process_apology(self) -> Dict[str, float]:
        """Process user apology"""
        changes = {}
        self.last_apology_time = time.time()
        resolution_occurred = False
        
        # Forgiveness factor affects decay
        decay_multiplier = self.forgiveness_factor
        
        if self.kecewa > 0:
            decay = self.kecewa_decay_per_apology * decay_multiplier
            self.kecewa = max(0, self.kecewa - decay)
            changes['kecewa'] = -decay
            resolution_occurred = True
            logger.info(f"💜 Kecewa -{decay:.0f} (apology)")
        
        if self.marah > 0:
            decay = self.marah_decay_per_apology * decay_multiplier
            self.marah = max(0, self.marah - decay)
            changes['marah'] = -decay
            resolution_occurred = True
            logger.info(f"💜 Marah -{decay:.0f} (apology)")
        
        if self.sakit_hati > 0:
            decay = self.kecewa_decay_per_apology * decay_multiplier * 0.8
            self.sakit_hati = max(0, self.sakit_hati - decay)
            changes['sakit_hati'] = -decay
            resolution_occurred = True
            logger.info(f"💜 Sakit hati -{decay:.0f} (apology)")
        
        if self.cemburu > 0:
            decay = self.cemburu_decay_per_chat * decay_multiplier
            self.cemburu = max(0, self.cemburu - decay)
            changes['cemburu'] = -decay
            resolution_occurred = True
            logger.info(f"💜 Cemburu -{decay:.0f} (apology)")
        
        if resolution_occurred:
            self.is_waiting_for_apology = False
            self.is_waiting_for_explanation = False
            
            # Record resolution
            self._add_resolution(ConflictResolution.APOLOGY)
            
            # Increase forgiveness factor
            self.forgiveness_factor = min(2.0, self.forgiveness_factor + 0.1)
            self.resentment_factor = max(0, self.resentment_factor - 0.1)
            
            # If cold war and conflict resolved, end cold war
            if self.is_cold_war and self.get_highest_conflict() < 30:
                self.end_cold_war()
        
        return changes
    
    def _process_explanation(self, explanation: str) -> Dict[str, float]:
        """Process user explanation"""
        changes = {}
        self.last_explanation_time = time.time()
        
        if self.is_waiting_for_explanation:
            # Explanation effectiveness based on quality
            quality = min(1.0, len(explanation) / 100)
            effectiveness = 0.5 + (quality * 0.5)
            
            if self.kecewa > 0:
                decay = self.kecewa_decay_per_apology * effectiveness
                self.kecewa = max(0, self.kecewa - decay)
                changes['kecewa'] = -decay
                logger.info(f"💜 Kecewa -{decay:.0f} (explanation)")
            
            if self.marah > 0:
                decay = self.marah_decay_per_apology * effectiveness
                self.marah = max(0, self.marah - decay)
                changes['marah'] = -decay
                logger.info(f"💜 Marah -{decay:.0f} (explanation)")
            
            self.is_waiting_for_explanation = False
            self._add_resolution(ConflictResolution.EXPLANATION)
        
        return changes
    
    def _process_attention(self) -> Dict[str, float]:
        """Process user attention"""
        changes = {}
        self.last_attention_time = time.time()
        
        if self.is_waiting_for_attention:
            if self.sakit_hati > 0:
                decay = self.sakit_hati_decay_per_attention
                self.sakit_hati = max(0, self.sakit_hati - decay)
                changes['sakit_hati'] = -decay
                logger.info(f"💜 Sakit hati -{decay:.0f} (attention)")
            
            self.is_waiting_for_attention = False
            self._add_resolution(ConflictResolution.ATTENTION)
        
        return changes
    
    def _add_resolution(self, resolution_type: ConflictResolution) -> None:
        """Add resolution to history"""
        self.resolution_history.append({
            'timestamp': time.time(),
            'type': resolution_type.value,
            'conflicts_resolved': [c.type.value for c in self.active_conflicts if c.is_active]
        })
        
        if len(self.resolution_history) > self.max_resolution_history:
            self.resolution_history.pop(0)
    
    # =========================================================================
    # ESCALATION & DECAY
    # =========================================================================
    
    def _apply_escalation_effect(self, conflict: Conflict) -> None:
        """Apply effects of conflict escalation"""
        if conflict.type == ConflictType.JEALOUSY:
            self.cemburu = min(100, self.cemburu + self.escalation_rate)
        elif conflict.type == ConflictType.DISAPPOINTMENT:
            self.kecewa = min(100, self.kecewa + self.escalation_rate)
        elif conflict.type == ConflictType.ANGER:
            self.marah = min(100, self.marah + self.escalation_rate)
        elif conflict.type == ConflictType.HURT:
            self.sakit_hati = min(100, self.sakit_hati + self.escalation_rate)
    
    def _has_repeated_conflict(self) -> bool:
        """Check if there are repeated conflicts in short time"""
        recent_conflicts = [c for c in self.conflict_history[-5:] 
                           if c.get('timestamp', 0) > time.time() - 3600]
        return len(recent_conflicts) >= 3
    
    def _apply_decay_per_interaction(self) -> None:
        """Apply decay per interaction (small decay)"""
        if self.cemburu > 0:
            self.cemburu = max(0, self.cemburu - self.cemburu_decay_per_chat / 4)
        if self.kecewa > 0:
            self.kecewa = max(0, self.kecewa - self.kecewa_decay_per_apology / 10)
        if self.marah > 0:
            self.marah = max(0, self.marah - self.marah_decay_per_apology / 10)
        if self.sakit_hati > 0:
            self.sakit_hati = max(0, self.sakit_hati - self.sakit_hati_decay_per_attention / 5)
    
    def update_decay(self, hours: float) -> None:
        """Update decay konflik berdasarkan waktu (untuk background worker)"""
        # Decay per jam
        decay_per_hour_cemburu = self.cemburu_decay_per_chat / 2
        decay_per_hour_kecewa = self.kecewa_decay_per_apology / 24
        decay_per_hour_marah = self.marah_decay_per_apology / 24
        decay_per_hour_sakit = self.sakit_hati_decay_per_time
        
        if self.cemburu > 0:
            self.cemburu = max(0, self.cemburu - decay_per_hour_cemburu * hours)
        
        if self.kecewa > 0:
            self.kecewa = max(0, self.kecewa - decay_per_hour_kecewa * hours)
        
        if self.marah > 0:
            self.marah = max(0, self.marah - decay_per_hour_marah * hours)
        
        if self.sakit_hati > 0:
            self.sakit_hati = max(0, self.sakit_hati - decay_per_hour_sakit * hours)
        
        self._update_active_conflicts()
        
        # Cold war decay
        if self.is_cold_war:
            elapsed = time.time() - self.cold_war_start_time
            if elapsed > self.cold_war_duration:
                self.end_cold_war()
        
        logger.debug(f"⚡ Conflict decay: cemburu={self.cemburu:.1f}, kecewa={self.kecewa:.1f}")
    
    # =========================================================================
    # CONFLICT MANAGEMENT
    # =========================================================================
    
    def _add_conflict(self, conflict_type: ConflictType, severity: float, trigger: str) -> None:
        """Tambah konflik ke daftar aktif"""
        # Cek apakah konflik serupa sudah ada
        existing = None
        for c in self.active_conflicts:
            if c.type == conflict_type and c.is_active:
                existing = c
                break
        
        if existing:
            existing.severity = severity
            existing.escalation_stage = min(5, existing.escalation_stage + 1)
            existing.trigger = trigger
        else:
            conflict = Conflict(
                type=conflict_type,
                severity=severity,
                trigger=trigger,
                timestamp=time.time(),
                is_active=True,
                resolution_needed=(conflict_type != ConflictType.JEALOUSY)
            )
            self.active_conflicts.append(conflict)
        
        # Save to history
        self.conflict_history.append({
            'type': conflict_type.value,
            'severity': severity,
            'trigger': trigger,
            'timestamp': time.time(),
            'resolved': False
        })
        
        if len(self.conflict_history) > self.max_history:
            self.conflict_history.pop(0)
    
    def _update_active_conflicts(self) -> None:
        """Update status konflik aktif berdasarkan level saat ini"""
        has_jealousy = self.cemburu >= self.cemburu_threshold
        has_disappointment = self.kecewa >= self.kecewa_threshold
        has_anger = self.marah >= self.marah_threshold
        has_hurt = self.sakit_hati >= self.sakit_hati_threshold
        
        self.is_in_conflict = any([has_jealousy, has_disappointment, has_anger, has_hurt])
        
        for conflict in self.active_conflicts:
            if conflict.type == ConflictType.JEALOUSY:
                conflict.is_active = has_jealousy
                conflict.severity = self.cemburu
            elif conflict.type == ConflictType.DISAPPOINTMENT:
                conflict.is_active = has_disappointment
                conflict.severity = self.kecewa
            elif conflict.type == ConflictType.ANGER:
                conflict.is_active = has_anger
                conflict.severity = self.marah
            elif conflict.type == ConflictType.HURT:
                conflict.is_active = has_hurt
                conflict.severity = self.sakit_hati
    
    def get_highest_conflict(self) -> float:
        """Dapatkan nilai konflik tertinggi"""
        return max(self.cemburu, self.kecewa, self.marah, self.sakit_hati)
    
    def get_active_conflict_type(self) -> Optional[ConflictType]:
        """Dapatkan jenis konflik aktif dengan severity tertinggi"""
        conflicts = []
        
        if self.cemburu >= self.cemburu_threshold:
            conflicts.append((ConflictType.JEALOUSY, self.cemburu))
        if self.kecewa >= self.kecewa_threshold:
            conflicts.append((ConflictType.DISAPPOINTMENT, self.kecewa))
        if self.marah >= self.marah_threshold:
            conflicts.append((ConflictType.ANGER, self.marah))
        if self.sakit_hati >= self.sakit_hati_threshold:
            conflicts.append((ConflictType.HURT, self.sakit_hati))
        
        if not conflicts:
            return None
        
        conflicts.sort(key=lambda x: x[1], reverse=True)
        return conflicts[0][0]
    
    def get_conflict_severity(self) -> ConflictSeverity:
        """Dapatkan tingkat keparahan konflik tertinggi"""
        max_severity = self.get_highest_conflict()
        
        if max_severity >= 70:
            return ConflictSeverity.SEVERE
        elif max_severity >= 40:
            return ConflictSeverity.MODERATE
        return ConflictSeverity.MILD
    
    # =========================================================================
    # COLD WAR SYSTEM
    # =========================================================================
    
    def _check_cold_war(self) -> None:
        """Cek apakah perlu memulai cold war"""
        if not self.is_in_conflict:
            return
        
        if self.is_cold_war:
            return
        
        severe_conflicts = [c for c in self.active_conflicts if c.severity >= 70]
        
        if severe_conflicts and self.is_waiting_for_apology:
            self.start_cold_war(intensity=70)
    
    def start_cold_war(self, intensity: float = 50, trigger: str = "") -> None:
        """Mulai cold war (tarik-ulur, VELORA gak chat duluan)"""
        self.is_cold_war = True
        self.cold_war_start_time = time.time()
        self.cold_war_intensity = intensity
        self.cold_war_trigger = trigger
        
        # Durasi cold war berdasarkan intensitas (30 menit - 3 jam)
        duration_minutes = 30 + (intensity / 100) * 150
        self.cold_war_duration = duration_minutes * 60
        
        logger.warning(f"⚔️ COLD WAR STARTED! Intensity: {intensity:.0f}% | Duration: {duration_minutes:.0f} minutes")
    
    def end_cold_war(self) -> None:
        """Akhiri cold war"""
        self.is_cold_war = False
        self.cold_war_start_time = 0
        self.cold_war_duration = 0
        self.cold_war_intensity = 0
        self.cold_war_trigger = ""
        logger.info("💜 Cold war ended")
    
    def is_in_cold_war(self) -> bool:
        """Cek apakah sedang dalam cold war"""
        return self.is_cold_war
    
    def get_cold_war_remaining(self) -> Optional[float]:
        """Dapatkan sisa waktu cold war dalam menit"""
        if not self.is_cold_war:
            return None
        
        remaining = self.cold_war_duration - (time.time() - self.cold_war_start_time)
        if remaining < 0:
            self.end_cold_war()
            return None
        
        return remaining / 60
    
    # =========================================================================
    # RESPONSE GUIDELINES
    # =========================================================================
    
    def get_conflict_style(self) -> str:
        """Dapatkan gaya konflik untuk respons VELORA"""
        conflict_type = self.get_active_conflict_type()
        severity = self.get_conflict_severity()
        
        if not conflict_type:
            return "normal"
        
        if self.is_cold_war:
            return "cold_war"
        
        base_styles = {
            ConflictType.JEALOUSY: "jealous",
            ConflictType.DISAPPOINTMENT: "disappointed",
            ConflictType.ANGER: "angry",
            ConflictType.HURT: "hurt"
        }
        
        style = base_styles.get(conflict_type, "conflict")
        
        if severity == ConflictSeverity.SEVERE:
            return f"{style}_severe"
        elif severity == ConflictSeverity.MODERATE:
            return f"{style}_moderate"
        
        return style
    
    def get_conflict_response_guideline(self) -> str:
        """Dapatkan pedoman respons saat konflik untuk prompt AI"""
        conflict_type = self.get_active_conflict_type()
        severity = self.get_conflict_severity()
        
        if not conflict_type:
            return ""
        
        # Get escalation stage for current conflict
        escalation = 1
        for c in self.active_conflicts:
            if c.type == conflict_type and c.is_active:
                escalation = c.escalation_stage
        
        guidelines = {
            ConflictType.JEALOUSY: f"""
⚠️ NOVA CEMBURU (Escalation: {escalation}/5)
- Respons: dingin, pendek, gak antusias
- Gak pake gesture manja
- Gak panggil "sayang"
- Contoh: "Iya." "Gak apa." "Terserah."
{self._get_escalation_guideline(escalation)}
""",
            ConflictType.DISAPPOINTMENT: f"""
⚠️ NOVA KECEWA (Escalation: {escalation}/5)
- Respons: sakit hati, suara kecil, mata berkaca-kaca
- Nova nunggu Mas minta maaf
- Gesture: *menunduk*, *muter-muter rambut*
- Contoh: "Mas... lupa ya... padahal aku nunggu."
{self._get_escalation_guideline(escalation)}
""",
            ConflictType.ANGER: f"""
⚠️ NOVA MARAH (Escalation: {escalation}/5)
- Respons: dingin, pendek, kadang sarkastik
- Jangan pake gesture manja
- Contoh: "Gapapa." "Terserah." "Kamu gitu ya."
{self._get_escalation_guideline(escalation)}
""",
            ConflictType.HURT: f"""
⚠️ NOVA SAKIT HATI (Escalation: {escalation}/5)
- Respons: sedih, mata berkaca-kaca, suara bergetar
- Nova nunggu Mas perhatian
- Gesture: *duduk jauh*, *gak liat Mas*
- Contoh: "Mas... janji tuh janji..."
{self._get_escalation_guideline(escalation)}
"""
        }
        
        base = guidelines.get(conflict_type, "")
        
        if severity == ConflictSeverity.SEVERE:
            base += "\n- INTENSITAS BERAT: Respons lebih dingin, bisa gak balas chat sama sekali"
        elif severity == ConflictSeverity.MODERATE:
            base += "\n- INTENSITAS SEDANG: Respons dingin tapi masih balas chat"
        
        if self.is_cold_war:
            remaining = self.get_cold_war_remaining()
            base += f"""
⚔️ COLD WAR MODE ACTIVE ({int(remaining)} menit tersisa)
- VELORA gak akan chat duluan
- Respons: pendek, dingin
- User harus minta maaf atau perhatian untuk akhiri cold war
"""
        
        return base
    
    def _get_escalation_guideline(self, escalation: int) -> str:
        """Dapatkan pedoman berdasarkan tingkat eskalasi"""
        if escalation >= 5:
            return "\n- ESKALASI MAKSIMAL: Respons sangat dingin, bisa diam sama sekali"
        elif escalation >= 4:
            return "\n- ESKALASI TINGGI: Respons sangat pendek, satu kata"
        elif escalation >= 3:
            return "\n- ESKALASI SEDANG: Respons pendek, 1-2 kata"
        return ""
    
    def get_conflict_summary(self) -> str:
        """Dapatkan ringkasan konflik untuk status display"""
        conflict_type = self.get_active_conflict_type()
        severity = self.get_conflict_severity()
        
        if not conflict_type:
            return "✅ Tidak ada konflik"
        
        type_names = {
            ConflictType.JEALOUSY: "Cemburu",
            ConflictType.DISAPPOINTMENT: "Kecewa",
            ConflictType.ANGER: "Marah",
            ConflictType.HURT: "Sakit Hati"
        }
        
        severity_names = {
            ConflictSeverity.MILD: "Ringan",
            ConflictSeverity.MODERATE: "Sedang",
            ConflictSeverity.SEVERE: "Berat"
        }
        
        cold_war_status = " | 🔥 COLD WAR ACTIVE" if self.is_cold_war else ""
        
        return f"⚠️ {type_names.get(conflict_type, 'Konflik')} - {severity_names.get(severity, '')}{cold_war_status}"
    
    # =========================================================================
    # RESET & UTILITY
    # =========================================================================
    
    def reset_all_conflicts(self) -> None:
        """Reset semua konflik"""
        self.cemburu = 0
        self.kecewa = 0
        self.marah = 0
        self.sakit_hati = 0
        self.active_conflicts = []
        self.is_in_conflict = False
        self.is_cold_war = False
        self.is_waiting_for_apology = False
        self.is_waiting_for_explanation = False
        self.is_waiting_for_attention = False
        self.forgiveness_factor = 1.0
        self.resentment_factor = 0.0
        logger.info("💜 All conflicts reset")
    
    # =========================================================================
    # FORMAT STATUS
    # =========================================================================
    
    def format_status(self) -> str:
        """Dapatkan status konflik lengkap"""
        def bar(value, char="⚠️"):
            filled = int(value / 10)
            return char * filled + "⚪" * (10 - filled)
        
        cold_war_remaining = self.get_cold_war_remaining()
        cold_war_text = f" ({int(cold_war_remaining)} menit)" if cold_war_remaining else ""
        
        # Get escalation stages
        escalation_text = ""
        for c in self.active_conflicts:
            if c.is_active:
                escalation_text += f"\n   {c.type.value}: Stage {c.escalation_stage}/5"
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    ⚔️ CONFLICT STATUS                        ║
╠══════════════════════════════════════════════════════════════╣
║ Cemburu:  {bar(self.cemburu, char='💢')} {self.cemburu:.0f}%
║ Kecewa:   {bar(self.kecewa, char='💔')} {self.kecewa:.0f}%
║ Marah:    {bar(self.marah, char='😠')} {self.marah:.0f}%
║ Sakit Hati: {bar(self.sakit_hati, char='😢')} {self.sakit_hati:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ STATUS: {self.get_conflict_summary()}
║ COLD WAR: {'✅' if self.is_cold_war else '❌'}{cold_war_text}
║ Nunggu Maaf: {'✅' if self.is_waiting_for_apology else '❌'}
║ Nunggu Penjelasan: {'✅' if self.is_waiting_for_explanation else '❌'}
║ Nunggu Perhatian: {'✅' if self.is_waiting_for_attention else '❌'}
╠══════════════════════════════════════════════════════════════╣
║ FORGIVENESS: {self.forgiveness_factor:.1f}/2.0
║ RESENTMENT: {self.resentment_factor:.1f}/2.0
║ ESCALATION:{escalation_text}
╚══════════════════════════════════════════════════════════════╝
"""
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        return {
            'cemburu': self.cemburu,
            'kecewa': self.kecewa,
            'marah': self.marah,
            'sakit_hati': self.sakit_hati,
            'active_conflicts': [c.to_dict() for c in self.active_conflicts],
            'is_cold_war': self.is_cold_war,
            'is_waiting_for_apology': self.is_waiting_for_apology,
            'is_waiting_for_explanation': self.is_waiting_for_explanation,
            'is_waiting_for_attention': self.is_waiting_for_attention,
            'conflict_history': self.conflict_history[-20:],
            'resolution_history': self.resolution_history[-20:],
            'last_apology_time': self.last_apology_time,
            'last_explanation_time': self.last_explanation_time,
            'last_attention_time': self.last_attention_time,
            'forgiveness_factor': self.forgiveness_factor,
            'resentment_factor': self.resentment_factor
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load dari dict"""
        self.cemburu = data.get('cemburu', 0)
        self.kecewa = data.get('kecewa', 0)
        self.marah = data.get('marah', 0)
        self.sakit_hati = data.get('sakit_hati', 0)
        self.is_cold_war = data.get('is_cold_war', False)
        self.is_waiting_for_apology = data.get('is_waiting_for_apology', False)
        self.is_waiting_for_explanation = data.get('is_waiting_for_explanation', False)
        self.is_waiting_for_attention = data.get('is_waiting_for_attention', False)
        self.last_apology_time = data.get('last_apology_time', 0)
        self.last_explanation_time = data.get('last_explanation_time', 0)
        self.last_attention_time = data.get('last_attention_time', 0)
        self.forgiveness_factor = data.get('forgiveness_factor', 1.0)
        self.resentment_factor = data.get('resentment_factor', 0.0)
        
        # Load conflicts
        self.active_conflicts = []
        for c_data in data.get('active_conflicts', []):
            conflict = Conflict(
                type=ConflictType(c_data.get('type', 'jealousy')),
                severity=c_data.get('severity', 0),
                trigger=c_data.get('trigger', ''),
                timestamp=c_data.get('timestamp', time.time()),
                is_active=c_data.get('is_active', True),
                resolution_needed=c_data.get('resolution_needed', False),
                resolution_type=ConflictResolution(c_data.get('resolution_type')) if c_data.get('resolution_type') else None,
                resolved_at=c_data.get('resolved_at', 0),
                escalation_stage=c_data.get('escalation_stage', 1)
            )
            self.active_conflicts.append(conflict)
        
        self.conflict_history = data.get('conflict_history', [])
        self.resolution_history = data.get('resolution_history', [])
        
        self._update_active_conflicts()


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_conflict_engine: Optional[ConflictEngine] = None


def get_conflict_engine() -> ConflictEngine:
    """Get global conflict engine instance"""
    global _conflict_engine
    if _conflict_engine is None:
        _conflict_engine = ConflictEngine()
    return _conflict_engine


def reset_conflict_engine() -> None:
    """Reset conflict engine (untuk testing)"""
    global _conflict_engine
    if _conflict_engine:
        _conflict_engine.reset_all_conflicts()
    _conflict_engine = None
    logger.info("🔄 Conflict Engine reset")


__all__ = [
    'ConflictType',
    'ConflictSeverity',
    'ConflictResolution',
    'Conflict',
    'ConflictEngine',
    'get_conflict_engine',
    'reset_conflict_engine'
]
