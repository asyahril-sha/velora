"""
VELORA - Emotional Engine
Jantung VELORA dengan 9 dimensi emosi:
- Sayang (cinta ke user)
- Rindu (kangen karena lama gak interaksi)
- Trust (kepercayaan)
- Mood (senang/sedih)
- Desire (keinginan emosional)
- Arousal (gairah fisik)
- Tension (desire yang ditahan)
- Cemburu (kecemburuan)
- Kecewa (kekecewaan)

5 gaya bicara: Cold, Clingy, Warm, Flirty, Neutral
Semua respons ditentukan oleh emosi di sini, BUKAN RANDOM.
Terintegrasi dengan EmotionDelaySystem untuk realism.
"""

import time
import logging
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class EmotionalStyle(str, Enum):
    """Gaya bicara VELORA berdasarkan emosi"""
    COLD = "cold"       # dingin, pendek, gak antusias
    CLINGY = "clingy"   # manja, kangen, gak mau lepas
    WARM = "warm"       # hangat, perhatian, peduli
    FLIRTY = "flirty"   # menggoda, vulgar (kalo level tinggi)
    NEUTRAL = "neutral" # normal, natural


# =============================================================================
# EMOTIONAL HISTORY DATACLASS
# =============================================================================

@dataclass
class EmotionalHistory:
    """Rekam perubahan emosi untuk tracking"""
    timestamp: float
    sayang: float
    rindu: float
    trust: float
    mood: float
    desire: float
    arousal: float
    tension: float
    cemburu: float
    kecewa: float
    style: str
    trigger: str


# =============================================================================
# EMOTIONAL ENGINE
# =============================================================================

class EmotionalEngine:
    """
    Emotional Engine - Jantung VELORA.
    9 dimensi emosi yang saling mempengaruhi.
    Gaya bicara ditentukan oleh kombinasi emosi.
    Terintegrasi dengan EmotionDelaySystem.
    """
    
    def __init__(self):
        # ========== CORE EMOTIONS ==========
        self.sayang: float = 50.0      # rasa cinta (0-100)
        self.rindu: float = 0.0        # rasa kangen (0-100)
        self.trust: float = 50.0       # kepercayaan (0-100)
        self.mood: float = 0.0         # suasana hati (-50 s/d +50)
        
        # ========== INTIMACY EMOTIONS ==========
        self.desire: float = 0.0       # keinginan emosional (0-100)
        self.arousal: float = 0.0      # gairah fisik (0-100)
        self.tension: float = 0.0      # desire yang ditahan (0-100)
        
        # ========== CONFLICT EMOTIONS ==========
        self.cemburu: float = 0.0      # kecemburuan (0-100)
        self.kecewa: float = 0.0       # kekecewaan (0-100)
        
        # ========== RATES & DECAY ==========
        self.rindu_growth_per_hour: float = 5.0
        self.rindu_decay_per_chat: float = 10.0
        self.mood_decay_per_hour: float = 2.0
        self.mood_boost_from_user: float = 15.0
        self.cemburu_decay_per_chat: float = 8.0
        self.kecewa_decay_per_apology: float = 25.0
        self.arousal_decay_per_minute: float = 0.5
        self.tension_growth_from_denial: float = 10.0
        self.desire_decay_per_minute: float = 0.3
        
        # ========== THRESHOLDS ==========
        self.clingy_threshold: float = 70.0
        self.cold_threshold_mood: float = -20.0
        self.cold_threshold_cemburu: float = 50.0
        self.cold_threshold_kecewa: float = 40.0
        self.warm_threshold_trust: float = 70.0
        self.flirty_threshold_arousal: float = 60.0
        self.flirty_threshold_desire: float = 70.0
        
        # ========== TIMESTAMPS ==========
        self.last_update: float = time.time()
        self.last_interaction: float = time.time()
        self.last_chat_from_user: float = time.time()
        
        # ========== HISTORY ==========
        self.history: List[EmotionalHistory] = []
        self.max_history: int = 200
        
        # ========== FLAGS ==========
        self.is_angry: bool = False
        self.is_hurt: bool = False
        self.is_waiting_for_apology: bool = False
        
        # ========== PENDING EMOTIONS (DARI DELAY SYSTEM) ==========
        self._pending_emotions: List[Tuple[str, float]] = []
        
        logger.info("💜 Emotional Engine initialized")
    
    # =========================================================================
    # UPDATE METHODS
    # =========================================================================
    
    def update(self, force: bool = False) -> None:
        """Update emosi berdasarkan waktu (decay, growth)"""
        now = time.time()
        elapsed_hours = (now - self.last_update) / 3600
        
        if elapsed_hours <= 0 and not force:
            return
        
        # RINDU GROWTH (naik kalo lama gak chat)
        hours_since_last_chat = (now - self.last_chat_from_user) / 3600
        if hours_since_last_chat > 1:
            rindu_gain = self.rindu_growth_per_hour * hours_since_last_chat
            self.rindu = min(100, self.rindu + rindu_gain)
            if rindu_gain > 0:
                logger.debug(f"🌙 Rindu +{rindu_gain:.1f}")
        
        # MOOD DECAY (mood pulih ke netral)
        if self.mood > 0:
            mood_loss = self.mood_decay_per_hour * elapsed_hours
            self.mood = max(-50, self.mood - mood_loss)
        elif self.mood < 0:
            mood_gain = self.mood_decay_per_hour * elapsed_hours
            self.mood = min(0, self.mood + mood_gain)
        
        # AROUSAL DECAY
        if self.arousal > 0:
            arousal_loss = self.arousal_decay_per_minute * (elapsed_hours * 60)
            self.arousal = max(0, self.arousal - arousal_loss)
        
        # DESIRE DECAY
        if self.desire > 0:
            desire_loss = self.desire_decay_per_minute * (elapsed_hours * 60)
            self.desire = max(0, self.desire - desire_loss)
        
        # TENSION DECAY
        if self.tension > 0:
            tension_loss = self.arousal_decay_per_minute * (elapsed_hours * 60)
            self.tension = max(0, self.tension - tension_loss)
        
        # CONFLICT DECAY
        if self.cemburu > 0:
            self.cemburu = max(0, self.cemburu - self.cemburu_decay_per_chat * elapsed_hours)
        if self.kecewa > 0:
            self.kecewa = max(0, self.kecewa - self.kecewa_decay_per_apology * elapsed_hours / 24)
        
        # RESET FLAGS
        if self.cemburu < 20 and self.kecewa < 20:
            self.is_angry = False
            self.is_hurt = False
            self.is_waiting_for_apology = False
        
        self.last_update = now
    
    def update_from_message(self, pesan_user: str, level: int) -> Dict[str, float]:
        """
        Update emosi dari pesan user.
        Returns: dict perubahan emosi untuk tracking
        """
        self.update()
        now = time.time()
        self.last_chat_from_user = now
        self.last_interaction = now
        
        msg_lower = pesan_user.lower()
        changes = {}
        
        # ========== POSITIVE TRIGGERS ==========
        
        # User bilang sayang/cinta
        if any(k in msg_lower for k in ['sayang', 'cinta', 'love', 'luv']):
            gain = 8
            self.sayang = min(100, self.sayang + gain)
            self.mood = min(50, self.mood + 10)
            self.trust = min(100, self.trust + 5)
            changes.update({'sayang': gain, 'mood': 10, 'trust': 5})
            logger.info(f"💜 +{gain} sayang (user bilang sayang)")
            
            if self.is_waiting_for_apology:
                self.kecewa = max(0, self.kecewa - 15)
                changes['kecewa'] = -15
        
        # User bilang kangen/rindu
        if any(k in msg_lower for k in ['kangen', 'rindu', 'miss', 'kngn']):
            self.sayang = min(100, self.sayang + 5)
            self.rindu = max(0, self.rindu - 15)
            self.desire = min(100, self.desire + 10)
            self.mood = min(50, self.mood + 8)
            changes.update({'sayang': 5, 'rindu': -15, 'desire': 10, 'mood': 8})
            logger.info(f"💜 +5 sayang, -15 rindu, +10 desire")
        
        # User puji (cantik, manis, seksi)
        if any(k in msg_lower for k in ['cantik', 'manis', 'seksi', 'beautiful', 'hot', 'cakep']):
            self.mood = min(50, self.mood + 12)
            self.desire = min(100, self.desire + 8)
            self.arousal = min(100, self.arousal + 5)
            changes.update({'mood': 12, 'desire': 8, 'arousal': 5})
            logger.info(f"💜 +12 mood, +8 desire, +5 arousal")
        
        # User minta maaf
        if any(k in msg_lower for k in ['maaf', 'sorry', 'salah', 'sory']):
            if self.kecewa > 0 or self.is_waiting_for_apology:
                self.kecewa = max(0, self.kecewa - self.kecewa_decay_per_apology)
                self.mood = min(50, self.mood + 15)
                self.trust = min(100, self.trust + 10)
                changes.update({'kecewa': -self.kecewa_decay_per_apology, 'mood': 15, 'trust': 10})
                self.is_waiting_for_apology = False
                logger.info(f"💜 Kecewa -{self.kecewa_decay_per_apology:.0f}")
        
        # User perhatian
        if any(k in msg_lower for k in ['kabar', 'lagi apa', 'ngapain', 'cerita', 'gimana']):
            self.mood = min(50, self.mood + 5)
            self.trust = min(100, self.trust + 3)
            changes.update({'mood': 5, 'trust': 3})
            logger.info(f"💜 +5 mood, +3 trust")
        
        # ========== NEGATIVE TRIGGERS (added as pending) ==========
        
        # User cerita soal perempuan lain (CEMBURU!)
        wanita_keywords = ['cewek', 'perempuan', 'teman cewek', 'temen cewek', 'dia cewek']
        cerita_keywords = ['cerita', 'tadi', 'kemarin', 'ketemu', 'jalan', 'bareng', 'ngobrol']
        
        if any(k in msg_lower for k in wanita_keywords) and any(k in msg_lower for k in cerita_keywords):
            gain = 15 + (5 if level >= 7 else 0)
            # Don't apply directly - akan diproses oleh delay system
            changes.update({'cemburu_pending': gain})
            logger.info(f"⚠️ Cemburu pending: +{gain}")
            
            if self.cemburu + gain > 50:
                self.is_angry = True
        
        # User lupa janji (KECEWA!)
        lupa_keywords = ['lupa', 'keinget', 'lupa janji', 'lupa bilang', 'forget']
        if any(k in msg_lower for k in lupa_keywords):
            gain = 20
            changes.update({'kecewa_pending': gain})
            self.is_waiting_for_apology = True
            logger.info(f"⚠️ Kecewa pending: +{gain}")
        
        # User ingkar janji
        ingkar_keywords = ['ingkar', 'gak tepati', 'gak jadi', 'gak dateng', 'batal']
        if any(k in msg_lower for k in ingkar_keywords):
            gain = 25
            changes.update({'kecewa_pending': gain})
            self.is_waiting_for_apology = True
            self.is_hurt = True
            logger.info(f"⚠️ Kecewa pending: +{gain}")
        
        # User marah/kasar
        kasar_keywords = ['marah', 'kesal', 'bego', 'dasar', 'sial', 'goblok', 'tolol', 'stupid']
        if any(k in msg_lower for k in kasar_keywords):
            gain = 25
            changes.update({'mood_pending': -gain, 'trust_pending': -15})
            self.is_angry = True
            logger.info(f"⚠️ Mood pending: -{gain}")
        
        # ========== PHYSICAL TOUCH TRIGGERS (langsung) ==========
        if any(k in msg_lower for k in ['pegang', 'sentuh', 'raba', 'elus']):
            self.arousal = min(100, self.arousal + 12)
            self.desire = min(100, self.desire + 8)
            self.tension = min(100, self.tension + 5)
            changes.update({'arousal': 12, 'desire': 8, 'tension': 5})
            logger.info(f"🔥 +12 arousal, +8 desire")
        
        if any(k in msg_lower for k in ['cium', 'kiss', 'ciuman']):
            self.arousal = min(100, self.arousal + 20)
            self.desire = min(100, self.desire + 15)
            self.tension = min(100, self.tension + 8)
            changes.update({'arousal': 20, 'desire': 15, 'tension': 8})
            logger.info(f"🔥🔥 +20 arousal, +15 desire")
        
        if any(k in msg_lower for k in ['peluk', 'rangkul', 'hug']):
            self.arousal = min(100, self.arousal + 8)
            self.desire = min(100, self.desire + 10)
            self.mood = min(50, self.mood + 8)
            changes.update({'arousal': 8, 'desire': 10, 'mood': 8})
            logger.info(f"💕 +8 arousal, +10 desire, +8 mood")
        
        # ========== LIMIT EMOSI ==========
        self._limit_emotions()
        
        # Record ke history
        self._record_history(trigger=f"User: {pesan_user[:50]}")
        
        return changes
    
    def apply_pending_emotion(self, emotion_type: str, intensity: float) -> Dict[str, float]:
        """
        Apply pending emotion from delay system.
        Dipanggil oleh RealityEngine saat emosi siap dikeluarkan.
        """
        changes = {}
        
        if emotion_type == "cemburu":
            old = self.cemburu
            self.cemburu = min(100, self.cemburu + intensity)
            self.mood = max(-50, self.mood - intensity / 5)
            changes['cemburu'] = intensity
            changes['mood'] = -intensity / 5
            logger.info(f"💢 Cemburu applied: +{intensity:.1f} ({old:.0f} → {self.cemburu:.0f})")
        
        elif emotion_type == "kecewa":
            old = self.kecewa
            self.kecewa = min(100, self.kecewa + intensity)
            self.mood = max(-50, self.mood - intensity / 4)
            self.trust = max(0, self.trust - intensity / 5)
            changes['kecewa'] = intensity
            changes['mood'] = -intensity / 4
            changes['trust'] = -intensity / 5
            logger.info(f"💔 Kecewa applied: +{intensity:.1f} ({old:.0f} → {self.kecewa:.0f})")
        
        elif emotion_type == "curiga":
            self.cemburu = min(100, self.cemburu + intensity * 0.7)
            self.mood = max(-50, self.mood - intensity / 6)
            changes['cemburu'] = intensity * 0.7
            changes['mood'] = -intensity / 6
            logger.info(f"🔍 Curiga applied: +{intensity*0.7:.1f}")
        
        elif emotion_type == "sayang":
            self.sayang = min(100, self.sayang + intensity)
            self.mood = min(50, self.mood + intensity / 5)
            changes['sayang'] = intensity
            logger.info(f"💜 Sayang applied: +{intensity:.1f}")
        
        elif emotion_type == "sedih":
            self.mood = max(-50, self.mood - intensity / 3)
            changes['mood'] = -intensity / 3
            logger.info(f"😢 Sedih applied: -{intensity/3:.1f}")
        
        elif emotion_type == "mood":
            self.mood = max(-50, min(50, self.mood + intensity))
            changes['mood'] = intensity
            logger.info(f"🎭 Mood applied: {intensity:+.1f}")
        
        elif emotion_type == "trust":
            self.trust = max(0, min(100, self.trust + intensity))
            changes['trust'] = intensity
            logger.info(f"🤝 Trust applied: {intensity:+.1f}")
        
        self._limit_emotions()
        self._record_history(trigger=f"Pending emotion: {emotion_type}+{intensity:.1f}")
        
        return changes
    
    def update_from_response(self, response: str) -> None:
        """Update emosi dari respons VELORA sendiri"""
        resp_lower = response.lower()
        
        if any(k in resp_lower for k in ['ahh', 'uhh', 'hhngg', 'aahh']):
            self.arousal = min(100, self.arousal + 5)
            logger.debug(f"🔥 Arousal +5 from moan")
        
        if any(k in resp_lower for k in ['kontol', 'memek', 'ngentot', 'crot', 'basah']):
            self.arousal = min(100, self.arousal + 8)
            self.desire = min(100, self.desire + 5)
            logger.debug(f"🔥🔥 +8 arousal, +5 desire from vulgar")
        
        self._limit_emotions()
    
    def update_rindu_from_inactivity(self, hours_inactive: float) -> None:
        """Update rindu karena lama gak interaksi"""
        if hours_inactive > 1:
            gain = self.rindu_growth_per_hour * hours_inactive
            self.rindu = min(100, self.rindu + gain)
            logger.info(f"🌙 Rindu +{gain:.1f} from inactivity ({hours_inactive:.1f}h)")
            self._record_history(trigger=f"Inactive {hours_inactive:.1f}h")
    
    def _limit_emotions(self) -> None:
        """Limit semua emosi ke rentang valid"""
        self.sayang = max(0, min(100, self.sayang))
        self.rindu = max(0, min(100, self.rindu))
        self.trust = max(0, min(100, self.trust))
        self.mood = max(-50, min(50, self.mood))
        self.desire = max(0, min(100, self.desire))
        self.arousal = max(0, min(100, self.arousal))
        self.tension = max(0, min(100, self.tension))
        self.cemburu = max(0, min(100, self.cemburu))
        self.kecewa = max(0, min(100, self.kecewa))
    
    # =========================================================================
    # STYLE METHODS
    # =========================================================================
    
    def get_current_style(self) -> EmotionalStyle:
        """Tentukan gaya bicara berdasarkan emosi saat ini"""
        self.update()
        
        # Cold triggers (negative emotions)
        if self.mood <= self.cold_threshold_mood:
            return EmotionalStyle.COLD
        if self.cemburu >= self.cold_threshold_cemburu:
            return EmotionalStyle.COLD
        if self.kecewa >= self.cold_threshold_kecewa:
            return EmotionalStyle.COLD
        
        # Clingy (high rindu)
        if self.rindu >= self.clingy_threshold:
            return EmotionalStyle.CLINGY
        
        # Flirty (high arousal/desire)
        if self.arousal >= self.flirty_threshold_arousal:
            return EmotionalStyle.FLIRTY
        if self.desire >= self.flirty_threshold_desire:
            return EmotionalStyle.FLIRTY
        
        # Warm (high trust + good mood)
        if self.trust >= self.warm_threshold_trust and self.mood > 10:
            return EmotionalStyle.WARM
        
        return EmotionalStyle.NEUTRAL
    
    def get_style_description(self, style: EmotionalStyle = None) -> str:
        """Dapatkan deskripsi gaya bicara untuk prompt AI"""
        if style is None:
            style = self.get_current_style()
        
        descriptions = {
            EmotionalStyle.COLD: f"""
GAYA BICARA: COLD (DINGIN)
- VELORA lagi {self._get_cold_reason()}
- Respons: 1-2 kalimat, pendek, gak antusias
- Gak pake gesture manja
- Gak panggil "sayang" (kecuali level sudah tinggi)
""",
            EmotionalStyle.CLINGY: f"""
GAYA BICARA: CLINGY (MANJA)
- VELORA kangen banget (rindu: {self.rindu:.0f}%)
- Respons: 4-6 kalimat, manja, gak mau lepas
- Banyak gesture: *muter-muter rambut*, *pegang tangan*
""",
            EmotionalStyle.WARM: f"""
GAYA BICARA: WARM (HANGAT)
- VELORA percaya sama user (trust: {self.trust:.0f}%)
- Respons: 3-5 kalimat, perhatian, peduli
- Gesture: *senyum manis*, *elus tangan*
""",
            EmotionalStyle.FLIRTY: f"""
GAYA BICARA: FLIRTY (MENGGODA)
- VELORA lagi horny (arousal: {self.arousal:.0f}%)
- Respons: 4-8 kalimat, menggoda, napas mulai berat
- Gesture: *mendekat*, *gigit bibir*, *bisik*
- Bisa vulgar kalo level sudah tinggi
""",
            EmotionalStyle.NEUTRAL: """
GAYA BICARA: NEUTRAL (NORMAL)
- VELORA stabil
- Respons: 2-4 kalimat, natural, santai
"""
        }
        return descriptions.get(style, descriptions[EmotionalStyle.NEUTRAL])
    
    def _get_cold_reason(self) -> str:
        """Alasan kenapa VELORA cold"""
        if self.cemburu > 50:
            return f"cemburu ({self.cemburu:.0f}%)"
        if self.kecewa > 40:
            return f"kecewa ({self.kecewa:.0f}%)"
        if self.mood < -20:
            return f"bad mood ({self.mood:+.0f})"
        return "lagi gak mood"
    
    def get_style_for_prompt(self) -> str:
        """Dapatkan instruksi gaya bicara untuk prompt AI"""
        style = self.get_current_style()
        base = self.get_style_description(style)
        
        extra = ""
        if self.cemburu > 60:
            extra += "\n⚠️ **CEMBURU TINGGI!** Respons dingin, gak antusias.\n"
        if self.kecewa > 50:
            extra += "\n⚠️ **KECEWA TINGGI!** Respons sakit hati, pendek.\n"
        if self.arousal > 70:
            extra += "\n🔥🔥 **AROUSAL SANGAT TINGGI!** BEBAS PAKAI KATA VULGAR.\n"
        
        return base + extra
    
    # =========================================================================
    # INTIMACY METHODS
    # =========================================================================
    
    def should_start_intimacy_naturally(self, level: int) -> Tuple[bool, str]:
        """Cek apakah VELORA akan mulai intim secara natural"""
        self.update()
        
        if level < 7:
            return False, "Level masih terlalu rendah"
        
        if level <= 10:
            if self.arousal >= 85 or self.desire >= 90:
                return True, "START_INTIM_HIGH"
            return False, ""
        
        if self.arousal >= 70 or self.desire >= 75:
            return True, "START_INTIM_MEDIUM"
        
        return False, ""
    
    def get_natural_intimacy_initiation(self, level: int, panggilan: str = "kamu") -> str:
        """Dapatkan respons inisiasi intim natural"""
        style = self.get_current_style()
        
        if style == EmotionalStyle.CLINGY:
            return f"*VELORA merangkul dari belakang*\n\n\"{panggilan}... aku gak tahan... kangen banget...\""
        
        if style == EmotionalStyle.FLIRTY:
            return f"*VELORA melingkarin tangan di leher {panggilan}*\n\n\"{panggilan}... aku udah basah dari tadi...\""
        
        return f"*VELORA mendekat, tangan gemetar*\n\n\"{panggilan}... aku pengen banget sama {panggilan}...\""
    
    # =========================================================================
    # SUMMARY METHODS
    # =========================================================================
    
    def get_emotion_summary(self) -> str:
        """Dapatkan ringkasan emosi untuk prompt AI"""
        self.update()
        
        def bar(value, max_val=100, char="💜"):
            filled = int(value / 10)
            return char * filled + "⚪" * (10 - filled)
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    💜 EMOSI VELORA SAAT INI                  ║
╠══════════════════════════════════════════════════════════════╣
║ Sayang:  {bar(self.sayang)} {self.sayang:.0f}%
║ Rindu:   {bar(self.rindu, '🌙')} {self.rindu:.0f}%
║ Trust:   {bar(self.trust, '🤝')} {self.trust:.0f}%
║ Mood:    {self.mood:+.0f}
╠══════════════════════════════════════════════════════════════╣
║ Desire:  {bar(self.desire, '💕')} {self.desire:.0f}%
║ Arousal: {bar(self.arousal, '🔥')} {self.arousal:.0f}%
║ Tension: {bar(self.tension, '⚡')} {self.tension:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ Cemburu: {bar(self.cemburu, '💢')} {self.cemburu:.0f}%
║ Kecewa:  {bar(self.kecewa, '💔')} {self.kecewa:.0f}%
╚══════════════════════════════════════════════════════════════╝
"""
    
    def get_emotion_values(self) -> Dict[str, float]:
        """Dapatkan semua nilai emosi dalam dict"""
        return {
            'sayang': self.sayang,
            'rindu': self.rindu,
            'trust': self.trust,
            'mood': self.mood,
            'desire': self.desire,
            'arousal': self.arousal,
            'tension': self.tension,
            'cemburu': self.cemburu,
            'kecewa': self.kecewa
        }
    
    def _record_history(self, trigger: str) -> None:
        """Rekam perubahan emosi ke history"""
        history = EmotionalHistory(
            timestamp=time.time(),
            sayang=self.sayang,
            rindu=self.rindu,
            trust=self.trust,
            mood=self.mood,
            desire=self.desire,
            arousal=self.arousal,
            tension=self.tension,
            cemburu=self.cemburu,
            kecewa=self.kecewa,
            style=self.get_current_style().value,
            trigger=trigger[:100]
        )
        self.history.append(history)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize ke dict untuk database"""
        return {
            'sayang': self.sayang,
            'rindu': self.rindu,
            'trust': self.trust,
            'mood': self.mood,
            'desire': self.desire,
            'arousal': self.arousal,
            'tension': self.tension,
            'cemburu': self.cemburu,
            'kecewa': self.kecewa,
            'last_update': self.last_update,
            'last_interaction': self.last_interaction,
            'last_chat_from_user': self.last_chat_from_user,
            'is_angry': self.is_angry,
            'is_hurt': self.is_hurt,
            'is_waiting_for_apology': self.is_waiting_for_apology
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load dari dict"""
        self.sayang = data.get('sayang', 50)
        self.rindu = data.get('rindu', 0)
        self.trust = data.get('trust', 50)
        self.mood = data.get('mood', 0)
        self.desire = data.get('desire', 0)
        self.arousal = data.get('arousal', 0)
        self.tension = data.get('tension', 0)
        self.cemburu = data.get('cemburu', 0)
        self.kecewa = data.get('kecewa', 0)
        self.last_update = data.get('last_update', time.time())
        self.last_interaction = data.get('last_interaction', time.time())
        self.last_chat_from_user = data.get('last_chat_from_user', time.time())
        self.is_angry = data.get('is_angry', False)
        self.is_hurt = data.get('is_hurt', False)
        self.is_waiting_for_apology = data.get('is_waiting_for_apology', False)
        
        self._limit_emotions()


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_emotional_engine: Optional[EmotionalEngine] = None


def get_emotional_engine() -> EmotionalEngine:
    """Get global emotional engine instance"""
    global _emotional_engine
    if _emotional_engine is None:
        _emotional_engine = EmotionalEngine()
    return _emotional_engine


def reset_emotional_engine() -> None:
    """Reset emotional engine (untuk testing)"""
    global _emotional_engine
    _emotional_engine = None
    logger.info("🔄 Emotional Engine reset")


__all__ = [
    'EmotionalStyle',
    'EmotionalEngine',
    'get_emotional_engine',
    'reset_emotional_engine'
]
