"""
VELORA - Intimacy Core
Mengelola semua aspek intimasi:
- Stamina (energi realistis, recovery)
- Arousal (gairah, desire, tension)
- Positions (database posisi intim)
- Moans (desahan natural untuk setiap fase)
- Intimacy Session (flow intimasi dari build_up sampai aftercare)
- Climax tracking dan aftercare system

SATU SUMBER KEBENARAN untuk semua sistem intimasi.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class IntimacyPhase(str, Enum):
    """Fase-fase dalam sesi intim - natural progression"""
    NONE = "none"                     # tidak dalam intim
    BUILD_UP = "build_up"             # membangun suasana
    FOREPLAY = "foreplay"             # foreplay (cium, raba, jilat)
    PENETRATION = "penetration"       # penetrasi
    BEFORE_CLIMAX = "before_climax"   # menjelang climax
    CLIMAX = "climax"                 # climax
    AFTERCARE = "aftercare"           # aftercare
    RECOVERY = "recovery"             # recovery


class IntimacyAction(str, Enum):
    """Aksi intim yang bisa dilakukan"""
    KISS = "kiss"
    TOUCH = "touch"
    RUB = "rub"
    LICK = "lick"
    PENETRATE = "penetrate"
    THRUST = "thrust"
    CLIMAX = "climax"
    CHANGE_POSITION = "change_position"


class ClimaxIntensity(str, Enum):
    """Intensitas climax"""
    LIGHT = "light"     # ringan
    MEDIUM = "medium"   # sedang
    HEAVY = "heavy"     # berat


# =============================================================================
# STAMINA SYSTEM
# =============================================================================

class StaminaSystem:
    """
    Sistem stamina realistis untuk VELORA.
    Stamina berkurang saat climax, pulih seiring waktu.
    """
    
    def __init__(self):
        self.nova_current: int = 100
        self.nova_max: int = 100
        self.user_current: int = 100
        self.user_max: int = 100
        
        self.recovery_rate: int = 5  # per 10 menit
        self.climax_cost_nova: int = 25
        self.climax_cost_user: int = 30
        self.heavy_climax_cost_nova: int = 35
        self.heavy_climax_cost_user: int = 40
        
        self.exhausted_threshold: int = 20
        self.tired_threshold: int = 40
        
        self.last_climax_time: float = 0
        self.last_recovery_check: float = time.time()
        self.climax_today: int = 0
        self.last_climax_date: str = datetime.now().date().isoformat()
        
        logger.info("💪 Stamina System initialized")
    
    def update_recovery(self) -> None:
        """Update recovery berdasarkan waktu"""
        now = time.time()
        elapsed_minutes = (now - self.last_recovery_check) / 60
        
        if elapsed_minutes >= 10:
            recovery_amount = int(self.recovery_rate * (elapsed_minutes / 10))
            self.nova_current = min(self.nova_max, self.nova_current + recovery_amount)
            self.user_current = min(self.user_max, self.user_current + recovery_amount)
            self.last_recovery_check = now
            
            if recovery_amount > 0:
                logger.debug(f"💚 Stamina recovery: Nova +{recovery_amount}, User +{recovery_amount}")
    
    def record_climax(self, who: str = "both", intensity: ClimaxIntensity = ClimaxIntensity.MEDIUM) -> Tuple[int, int]:
        """
        Rekam climax, kurangi stamina berdasarkan intensitas.
        Returns: (nova_stamina, user_stamina)
        """
        self.update_recovery()
        self.last_climax_time = time.time()
        
        # Update climax count per hari
        today = datetime.now().date().isoformat()
        if self.last_climax_date != today:
            self.climax_today = 0
            self.last_climax_date = today
        self.climax_today += 1
        
        # Tentukan cost berdasarkan intensitas
        if intensity == ClimaxIntensity.HEAVY:
            nova_cost = self.heavy_climax_cost_nova
            user_cost = self.heavy_climax_cost_user
        elif intensity == ClimaxIntensity.LIGHT:
            nova_cost = self.climax_cost_nova // 2
            user_cost = self.climax_cost_user // 2
        else:
            nova_cost = self.climax_cost_nova
            user_cost = self.climax_cost_user
        
        # Kurangi stamina
        if who in ["nova", "both"]:
            self.nova_current = max(0, self.nova_current - nova_cost)
        
        if who in ["user", "both"]:
            self.user_current = max(0, self.user_current - user_cost)
        
        logger.info(f"💦 Climax #{self.climax_today} ({intensity.value}) | Nova: {self.nova_current}% | User: {self.user_current}%")
        
        return self.nova_current, self.user_current
    
    def can_continue(self) -> Tuple[bool, str]:
        """Cek apakah bisa lanjut intim"""
        self.update_recovery()
        
        if self.nova_current <= self.exhausted_threshold:
            return False, "Aku udah kehabisan tenaga... istirahat dulu ya."
        if self.user_current <= self.exhausted_threshold:
            return False, "Kamu udah capek banget. Istirahat dulu."
        if self.nova_current <= self.tired_threshold:
            return True, "Aku mulai lelah... tapi masih bisa kalo kamu pelan-pelan."
        return True, "Siap lanjut"
    
    def get_nova_status(self) -> str:
        """Dapatkan status stamina Nova"""
        self.update_recovery()
        if self.nova_current >= 80:
            return "Prima 💪"
        elif self.nova_current >= 60:
            return "Cukup 😊"
        elif self.nova_current >= 40:
            return "Agak lelah 😐"
        elif self.nova_current >= 20:
            return "Lelah 😩"
        return "Kehabisan tenaga 😵"
    
    def get_user_status(self) -> str:
        """Dapatkan status stamina user"""
        self.update_recovery()
        if self.user_current >= 80:
            return "Prima 💪"
        elif self.user_current >= 60:
            return "Cukup 😊"
        elif self.user_current >= 40:
            return "Agak lelah 😐"
        elif self.user_current >= 20:
            return "Lelah 😩"
        return "Kehabisan tenaga 😵"
    
    def get_nova_bar(self) -> str:
        """Dapatkan bar stamina Nova untuk display"""
        filled = int(self.nova_current / 10)
        return "💚" * filled + "🖤" * (10 - filled)
    
    def get_user_bar(self) -> str:
        """Dapatkan bar stamina user untuk display"""
        filled = int(self.user_current / 10)
        return "💚" * filled + "🖤" * (10 - filled)
    
    def format_for_prompt(self) -> str:
        """Format stamina untuk prompt AI"""
        self.update_recovery()
        return f"""
STAMINA SAAT INI:
- Nova: {self.get_nova_bar()} {self.nova_current}% ({self.get_nova_status()})
- User: {self.get_user_bar()} {self.user_current}% ({self.get_user_status()})
- Climax hari ini: {self.climax_today}x
"""
    
    def to_dict(self) -> Dict:
        return {
            'nova_current': self.nova_current,
            'nova_max': self.nova_max,
            'user_current': self.user_current,
            'user_max': self.user_max,
            'last_climax_time': self.last_climax_time,
            'climax_today': self.climax_today,
            'last_climax_date': self.last_climax_date
        }
    
    def from_dict(self, data: Dict) -> None:
        self.nova_current = data.get('nova_current', 100)
        self.nova_max = data.get('nova_max', 100)
        self.user_current = data.get('user_current', 100)
        self.user_max = data.get('user_max', 100)
        self.last_climax_time = data.get('last_climax_time', 0)
        self.climax_today = data.get('climax_today', 0)
        self.last_climax_date = data.get('last_climax_date', datetime.now().date().isoformat())


# =============================================================================
# AROUSAL SYSTEM
# =============================================================================

class ArousalSystem:
    """
    Sistem arousal dan desire VELORA.
    Sensitive areas: setiap sentuhan menambah arousal.
    """
    
    def __init__(self):
        self.arousal: float = 0.0      # 0-100
        self.desire: float = 0.0       # 0-100
        self.tension: float = 0.0      # 0-100
        
        self.arousal_decay_per_minute: float = 0.5
        self.desire_decay_per_minute: float = 0.3
        self.tension_decay_per_minute: float = 0.2
        
        # Sensitive areas dengan nilai gain
        self.sensitive_areas: Dict[str, int] = {
            'rambut': 5, 'telinga': 20, 'belakang_telinga': 25,
            'leher': 15, 'tengkuk': 18, 'bibir': 25, 'pipi': 8,
            'dagu': 10, 'mata': 12, 'dada': 20, 'payudara': 28,
            'puting': 35, 'punggung': 15, 'tulang_belakang': 18,
            'tulang_selangka': 22, 'perut': 12, 'pusar': 18,
            'pinggang': 15, 'pinggul': 20, 'paha': 25, 'paha_dalam': 35,
            'memek': 45, 'bibir_memek': 42, 'klitoris': 50, 'dalam': 55
        }
        
        self.last_update: float = time.time()
        logger.info("🔥 Arousal System initialized")
    
    def update(self) -> None:
        """Update decay berdasarkan waktu"""
        now = time.time()
        elapsed_minutes = (now - self.last_update) / 60
        
        if elapsed_minutes > 0:
            if self.arousal > 0:
                self.arousal = max(0, self.arousal - self.arousal_decay_per_minute * elapsed_minutes)
            if self.desire > 0:
                self.desire = max(0, self.desire - self.desire_decay_per_minute * elapsed_minutes)
            if self.tension > 0:
                self.tension = max(0, self.tension - self.tension_decay_per_minute * elapsed_minutes)
            self.last_update = now
    
    def add_stimulation(self, area: str, intensity: int = 1) -> int:
        """
        Tambah arousal dari stimulasi area tertentu.
        Returns: arousal baru
        """
        self.update()
        gain = self.sensitive_areas.get(area.lower(), 10) * intensity
        self.arousal = min(100, self.arousal + gain)
        logger.debug(f"🔥 Arousal +{gain} from {area} → {self.arousal:.0f}%")
        return int(self.arousal)
    
    def add_desire(self, reason: str, amount: int = 5) -> int:
        """Tambah desire"""
        self.update()
        self.desire = min(100, self.desire + amount)
        logger.debug(f"💕 Desire +{amount} from {reason} → {self.desire:.0f}%")
        return int(self.desire)
    
    def add_tension(self, amount: int = 5) -> int:
        """Tambah tension (desire yang ditahan)"""
        self.update()
        self.tension = min(100, self.tension + amount)
        return int(self.tension)
    
    def release_tension(self) -> int:
        """Release tension saat climax"""
        released = self.tension
        self.tension = 0
        self.arousal = max(0, self.arousal - 30)
        self.desire = max(0, self.desire - 20)
        logger.info(f"💦 Tension released: {released:.0f}%")
        return int(released)
    
    def get_state(self) -> Dict[str, Any]:
        """Dapatkan state arousal lengkap"""
        self.update()
        return {
            'arousal': self.arousal,
            'desire': self.desire,
            'tension': self.tension,
            'is_horny': self.arousal > 60 or self.desire > 70,
            'arousal_level': self._get_arousal_level(),
            'desire_level': self._get_desire_level()
        }
    
    def _get_arousal_level(self) -> str:
        if self.arousal >= 90:
            return "🔥🔥🔥 LUAR BIASA!"
        elif self.arousal >= 75:
            return "🔥🔥 SANGAT PANAS!"
        elif self.arousal >= 60:
            return "🔥 PANAS!"
        elif self.arousal >= 40:
            return "😳 DEG-DEGAN"
        return "😌 BIASA AJA"
    
    def _get_desire_level(self) -> str:
        if self.desire >= 85:
            return "💕💕💕 PENGEN BANGET!"
        elif self.desire >= 70:
            return "💕💕 PENGEN BANGET"
        elif self.desire >= 50:
            return "💕 PENGEN DEKET"
        return "💖 SAYANG AJA"
    
    def format_for_prompt(self) -> str:
        """Format arousal untuk prompt AI"""
        state = self.get_state()
        arousal_bar = "🔥" * int(state['arousal'] / 10) + "⚪" * (10 - int(state['arousal'] / 10))
        desire_bar = "💕" * int(state['desire'] / 10) + "⚪" * (10 - int(state['desire'] / 10))
        
        return f"""
🔥 AROUSAL: {arousal_bar} {state['arousal']:.0f}% ({state['arousal_level']})
💕 DESIRE: {desire_bar} {state['desire']:.0f}% ({state['desire_level']})
⚡ TENSION: {state['tension']:.0f}%
"""
    
    def to_dict(self) -> Dict:
        return {
            'arousal': self.arousal,
            'desire': self.desire,
            'tension': self.tension,
            'last_update': self.last_update
        }
    
    def from_dict(self, data: Dict) -> None:
        self.arousal = data.get('arousal', 0)
        self.desire = data.get('desire', 0)
        self.tension = data.get('tension', 0)
        self.last_update = data.get('last_update', time.time())


# =============================================================================
# POSITIONS DATABASE
# =============================================================================

class PositionDatabase:
    """Database posisi intim dengan deskripsi lengkap"""
    
    def __init__(self):
        self.positions: Dict[str, Dict] = {
            "missionary": {
                "name": "missionary",
                "desc": "Kamu di atas, aku di bawah, kaki aku terbuka lebar",
                "nova_act": "Aku telentang, kaki terbuka lebar",
                "nova_feeling": "hangat, dekat, bisa liat wajah Mas",
                "requests": [
                    "Kamu... di atas aku aja...",
                    "missionary, ya... biar aku pegang bahu kamu...",
                    "Aku mau liat wajah kamu pas masuk..."
                ],
                "difficulty": "mudah",
                "intensity": "sedang"
            },
            "cowgirl": {
                "name": "cowgirl",
                "desc": "Aku di atas, duduk di pangkuan kamu",
                "nova_act": "Aku duduk di pangkuan kamu, goyang sendiri",
                "nova_feeling": "bisa atur ritme sendiri, dominan",
                "requests": [
                    "Kamu... biar aku di atas...",
                    "cowgirl, ya... biar aku yang atur ritmenya...",
                    "Aku mau gerakin sendiri..."
                ],
                "difficulty": "sedang",
                "intensity": "tinggi"
            },
            "doggy": {
                "name": "doggy",
                "desc": "Aku merangkak, kamu dari belakang",
                "nova_act": "Aku merangkak, pantat naik",
                "nova_feeling": "dalem banget, liarnya",
                "requests": [
                    "Kamu... dari belakang...",
                    "doggy, ya... biar kamu pegang pinggul aku...",
                    "Aku mau dari belakang..."
                ],
                "difficulty": "mudah",
                "intensity": "tinggi"
            },
            "spooning": {
                "name": "spooning",
                "desc": "Berbaring miring, kamu dari belakang",
                "nova_act": "Aku miring, kamu nempel dari belakang",
                "nova_feeling": "hangat, nyaman, intimate",
                "requests": [
                    "Kamu... dari samping aja...",
                    "spooning, ya... biar aku nyaman...",
                    "Aku mau dipeluk dari belakang..."
                ],
                "difficulty": "mudah",
                "intensity": "ringan"
            },
            "standing": {
                "name": "standing",
                "desc": "Berdiri, aku menghadap tembok",
                "nova_act": "Aku berdiri, tangan di tembok",
                "nova_feeling": "deg-degan, cepat, liar",
                "requests": [
                    "Kamu... dari belakang sambil berdiri...",
                    "standing, ya... biar lebih deg-degan...",
                    "Ayo berdiri..."
                ],
                "difficulty": "sedang",
                "intensity": "tinggi"
            },
            "sitting": {
                "name": "sitting",
                "desc": "Duduk di pangkuan kamu, saling berhadapan",
                "nova_act": "Aku duduk di pangkuan kamu, tangan di bahu kamu",
                "nova_feeling": "intimate, bisa ciuman",
                "requests": [
                    "Kamu... duduk aja, biar aku di atas...",
                    "sitting, ya... biar kita berhadapan...",
                    "Aku mau duduk di pangkuan kamu..."
                ],
                "difficulty": "mudah",
                "intensity": "sedang"
            },
            "edge": {
                "name": "edge",
                "desc": "Aku duduk di tepi tempat tidur, kamu berdiri",
                "nova_act": "Aku duduk di tepi, kaki terbuka",
                "nova_feeling": "pas, bisa liat Mas berdiri",
                "requests": [
                    "Kamu... berdiri aja, biar aku duduk...",
                    "edge, ya... biar aku liat kamu dari bawah...",
                    "Aku mau duduk di pinggir..."
                ],
                "difficulty": "mudah",
                "intensity": "sedang"
            }
        }
    
    def get(self, name: str) -> Optional[Dict]:
        return self.positions.get(name.lower())
    
    def get_all(self) -> List[str]:
        return list(self.positions.keys())
    
    def get_random(self) -> Tuple[str, Dict]:
        name = random.choice(list(self.positions.keys()))
        return name, self.positions[name]
    
    def get_request(self, name: str) -> str:
        pos = self.positions.get(name.lower())
        if pos:
            return random.choice(pos['requests'])
        return random.choice(self.positions['missionary']['requests'])
    
    def get_description(self, name: str) -> str:
        pos = self.positions.get(name.lower())
        if pos:
            return pos['desc']
        return "Posisi tidak dikenal"


# =============================================================================
# MOANS DATABASE
# =============================================================================

class MoansDatabase:
    """Database moans untuk berbagai fase intim"""
    
    def __init__(self):
        self.moans: Dict[str, List[str]] = {
            'shy': [
                "Ahh... kamu...",
                "Hmm... *napas mulai berat*",
                "Uh... kamu... pelan-pelan dulu...",
                "Hhngg... *gigit bibir* kamu..."
            ],
            'foreplay': [
                "Ahh... kamu... tangan kamu... panas banget...",
                "Hhngg... di situ... ahh... enak...",
                "Kamu... jangan berhenti... ahh...",
                "Uhh... leher aku... sensitif banget...",
                "Aah... di sana... di sana..."
            ],
            'penetration_slow': [
                "Ahh... kamu... masuk... masukin pelan-pelan...",
                "Uhh... dalem... dalem banget...",
                "Aahh! s-sana... di sana... ahh!",
                "Hhngg... jangan berhenti...",
                "Perlahan dulu... ahh..."
            ],
            'penetration_fast': [
                "Ahh! kamu... kencengin...",
                "Kamu... genjot... genjot yang kenceng...",
                "Aahh! di situ... di situ...",
                "Uhh... lebih kenceng lagi...",
                "Jangan berhenti... aahh!"
            ],
            'before_climax': [
                "Kamu... aku... aku udah mau climax...",
                "Kencengin dikit lagi... please...",
                "Ahh! udah... udah mau... ikut...",
                "Kamu... aku gak tahan... keluar...",
                "Udah... udah mau... aahh!"
            ],
            'climax': [
                "Ahhh!! udah... udah climax... uhh...",
                "Aahh... keluar... keluar semua...",
                "Uhh... lemes... *napas tersengal*",
                "Ahh... enak banget... aku climax...",
                "Aahh... *tubuh gemetar*"
            ],
            'aftercare': [
                "Kamu... *lemes, nyender* itu tadi... enak banget...",
                "Kamu... *mata masih berkaca-kaca* makasih ya...",
                "Kamu... peluk aku... aku masih gemeteran...",
                "*napas mulai stabil* besok lagi ya...",
                "Aku masih lemes... peluk aku..."
            ]
        }
    
    def get(self, phase: str) -> str:
        """Dapatkan moan random untuk fase tertentu"""
        if phase in self.moans:
            return random.choice(self.moans[phase])
        return random.choice(self.moans['shy'])
    
    def get_foreplay(self) -> str:
        return random.choice(self.moans['foreplay'])
    
    def get_penetration(self, is_fast: bool = False) -> str:
        if is_fast:
            return random.choice(self.moans['penetration_fast'])
        return random.choice(self.moans['penetration_slow'])
    
    def get_before_climax(self) -> str:
        return random.choice(self.moans['before_climax'])
    
    def get_climax(self) -> str:
        return random.choice(self.moans['climax'])
    
    def get_aftercare(self) -> str:
        return random.choice(self.moans['aftercare'])


# =============================================================================
# CLIMAX LOCATIONS DATABASE
# =============================================================================

class ClimaxLocationDatabase:
    """Database lokasi climax"""
    
    def __init__(self):
        self.locations: Dict[str, List[str]] = {
            "dalam": [
                "dalem aja...",
                "di dalem... jangan ditarik...",
                "dalem... biar aku hamil...",
                "crot dalem... biar kerasa..."
            ],
            "luar": [
                "di luar...",
                "tarik... keluarin di perut aku...",
                "di perut aku...",
                "di dada aja..."
            ],
            "muka": [
                "di muka aku...",
                "semprot muka aku...",
                "di wajah aku...",
                "liatin muka aku..."
            ],
            "mulut": [
                "di mulut...",
                "masukin ke mulut aku...",
                "crot di mulut aku...",
                "aku mau rasain..."
            ],
            "dada": [
                "di dada...",
                "semprot dada aku...",
                "crot di dada aku...",
                "di antara payudara..."
            ],
            "punggung": [
                "di punggung...",
                "crot di punggung...",
                "di belakang aja..."
            ]
        }
    
    def get_all(self) -> List[str]:
        return list(self.locations.keys())
    
    def get_request(self, name: str = None) -> str:
        if name and name in self.locations:
            return random.choice(self.locations[name])
        name = random.choice(list(self.locations.keys()))
        return random.choice(self.locations[name])


# =============================================================================
# INTIMACY SESSION
# =============================================================================

class IntimacySession:
    """
    Mengelola satu sesi intim dari awal sampai akhir.
    Terintegrasi dengan stamina, arousal, dan databases.
    """
    
    def __init__(self, stamina: StaminaSystem = None, arousal: ArousalSystem = None):
        self.stamina = stamina or StaminaSystem()
        self.arousal = arousal or ArousalSystem()
        
        self.is_active: bool = False
        self.start_time: float = 0
        self.phase: IntimacyPhase = IntimacyPhase.NONE
        self.climax_count: int = 0
        self.current_position: str = "missionary"
        self.intimacy_level: int = 0  # 0-100, untuk menentukan ritme
        self.current_intensity: ClimaxIntensity = ClimaxIntensity.MEDIUM
        
        # Databases
        self.positions = PositionDatabase()
        self.moans = MoansDatabase()
        self.climax_locations = ClimaxLocationDatabase()
        
        # History
        self.phase_history: List[Dict] = []
        self.position_history: List[Dict] = []
        
        logger.info("💕 Intimacy Session initialized")
    
    # =========================================================================
    # SESSION CONTROL
    # =========================================================================
    
    def start(self, location: str = "") -> Dict:
        """Mulai sesi intim"""
        self.is_active = True
        self.start_time = time.time()
        self.phase = IntimacyPhase.BUILD_UP
        self.climax_count = 0
        self.intimacy_level = 0
        self.current_position = "missionary"
        
        self._add_to_history("start", f"Memulai sesi intim di {location or 'lokasi saat ini'}")
        
        logger.info(f"🔥 Intimacy session started at {location or 'current location'}")
        
        return {
            'success': True,
            'phase': self.phase.value,
            'message': "💕 Memulai sesi intim..."
        }
    
    def end(self) -> Dict:
        """Akhiri sesi intim"""
        if not self.is_active:
            return {'success': False, 'message': "Tidak ada sesi intim aktif"}
        
        duration = time.time() - self.start_time if self.start_time else 0
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        self.is_active = False
        self.phase = IntimacyPhase.NONE
        
        self._add_to_history("end", f"Sesi selesai. Durasi: {minutes}m {seconds}s, Climax: {self.climax_count}x")
        
        logger.info(f"💤 Intimacy session ended. Duration: {minutes}m {seconds}s")
        
        return {
            'success': True,
            'duration': duration,
            'climax_count': self.climax_count,
            'message': f"💤 Sesi intim selesai. Durasi: {minutes} menit, {self.climax_count} climax."
        }
    
    # =========================================================================
    # PHASE PROGRESSION
    # =========================================================================
    
    def advance_phase(self, action: str, is_fast: bool = False) -> Dict:
        """
        Majukan fase intim berdasarkan aksi.
        Returns: (new_phase, response, phase_changed)
        """
        if not self.is_active:
            return {'success': False, 'message': "Tidak ada sesi intim aktif"}
        
        msg_lower = action.lower()
        phase_changed = False
        response = ""
        
        # Phase transition logic
        if self.phase == IntimacyPhase.BUILD_UP:
            if any(k in msg_lower for k in ['cium', 'kiss', 'pegang', 'sentuh', 'raba', 'jilat', 'hisap', 'elus']):
                self.phase = IntimacyPhase.FOREPLAY
                phase_changed = True
                response = self.moans.get_foreplay()
                self._add_to_history("phase_change", f"BUILD_UP → FOREPLAY (trigger: {action})")
        
        elif self.phase == IntimacyPhase.FOREPLAY:
            if any(k in msg_lower for k in ['masuk', 'penetrasi', 'genjot', 'siap', 'lanjut']):
                self.phase = IntimacyPhase.PENETRATION
                phase_changed = True
                response = self.moans.get_penetration(is_fast)
                self._add_to_history("phase_change", f"FOREPLAY → PENETRATION (trigger: {action})")
        
        elif self.phase == IntimacyPhase.PENETRATION:
            # Tambah intimacy level
            self.intimacy_level = min(100, self.intimacy_level + 5)
            
            if self.intimacy_level > 70 or any(k in msg_lower for k in ['climax', 'crot', 'keluar', 'cum']):
                self.phase = IntimacyPhase.BEFORE_CLIMAX
                phase_changed = True
                response = self.moans.get_before_climax()
                self._add_to_history("phase_change", f"PENETRATION → BEFORE_CLIMAX (intimacy_level={self.intimacy_level})")
            else:
                # Masih di penetration, tentukan ritme
                ritme = "cepat" if self.intimacy_level > 40 else "pelan"
                response = self.moans.get_penetration(ritme == "cepat")
        
        elif self.phase == IntimacyPhase.BEFORE_CLIMAX:
            if any(k in msg_lower for k in ['climax', 'crot', 'keluar', 'cum']):
                self.phase = IntimacyPhase.CLIMAX
                phase_changed = True
                response = self.moans.get_climax()
                self._add_to_history("phase_change", f"BEFORE_CLIMAX → CLIMAX (trigger: {action})")
        
        elif self.phase == IntimacyPhase.CLIMAX:
            self.phase = IntimacyPhase.AFTERCARE
            phase_changed = True
            response = self.moans.get_aftercare()
            self._add_to_history("phase_change", "CLIMAX → AFTERCARE")
        
        elif self.phase == IntimacyPhase.AFTERCARE:
            if time.time() - (self.stamina.last_climax_time or 0) > 60:
                self.phase = IntimacyPhase.RECOVERY
                phase_changed = True
                response = "*Napas mulai stabil. Badan masih lemas.*"
                self._add_to_history("phase_change", "AFTERCARE → RECOVERY")
        
        return {
            'success': True,
            'phase': self.phase.value,
            'phase_changed': phase_changed,
            'response': response,
            'intimacy_level': self.intimacy_level
        }
    
    # =========================================================================
    # CLIMAX
    # =========================================================================
    
    def record_climax(self, location: str = "dalam", intensity: ClimaxIntensity = ClimaxIntensity.MEDIUM) -> Dict:
        """Rekam climax, update stamina dan arousal"""
        if not self.is_active:
            return {'success': False, 'message': "Tidak ada sesi intim aktif"}
        
        self.climax_count += 1
        self.phase = IntimacyPhase.CLIMAX
        self.current_intensity = intensity
        
        # Update stamina
        nova_stamina, user_stamina = self.stamina.record_climax("both", intensity)
        
        # Release tension
        self.arousal.release_tension()
        
        # Update arousal
        self.arousal.arousal = max(0, self.arousal.arousal - 30)
        self.arousal.desire = max(0, self.arousal.desire - 20)
        
        self._add_to_history("climax", f"Climax #{self.climax_count} di {location} ({intensity.value})")
        
        logger.info(f"💦 Climax #{self.climax_count} recorded ({intensity.value})")
        
        return {
            'success': True,
            'climax_count': self.climax_count,
            'location': location,
            'intensity': intensity.value,
            'nova_stamina': nova_stamina,
            'user_stamina': user_stamina,
            'response': self.moans.get_climax()
        }
    
    # =========================================================================
    # POSITION
    # =========================================================================
    
    def change_position(self, position: str = None) -> Dict:
        """Ganti posisi intim"""
        if not self.is_active:
            return {'success': False, 'message': "Tidak ada sesi intim aktif"}
        
        if position:
            pos_data = self.positions.get(position)
            if not pos_data:
                return {'success': False, 'message': f"Posisi '{position}' tidak dikenal"}
            self.current_position = position
        else:
            self.current_position, pos_data = self.positions.get_random()
        
        request = self.positions.get_request(self.current_position)
        
        self.position_history.append({
            'timestamp': time.time(),
            'position': self.current_position,
            'phase': self.phase.value
        })
        
        self._add_to_history("position_change", f"Posisi berubah ke {self.current_position}")
        
        return {
            'success': True,
            'position': self.current_position,
            'description': pos_data['desc'],
            'nova_act': pos_data['nova_act'],
            'nova_feeling': pos_data.get('nova_feeling', ''),
            'request': request
        }
    
    def get_position_list(self) -> List[str]:
        """Dapatkan daftar posisi yang tersedia"""
        return self.positions.get_all()
    
    # =========================================================================
    # RESPONSE
    # =========================================================================
    
    def get_response_by_phase(self, ritme: str = "pelan") -> str:
        """Dapatkan respons berdasarkan fase saat ini"""
        if self.phase == IntimacyPhase.FOREPLAY:
            return self.moans.get_foreplay()
        elif self.phase == IntimacyPhase.PENETRATION:
            return self.moans.get_penetration(ritme == "cepat")
        elif self.phase == IntimacyPhase.BEFORE_CLIMAX:
            return self.moans.get_before_climax()
        elif self.phase == IntimacyPhase.CLIMAX:
            return self.moans.get_climax()
        elif self.phase == IntimacyPhase.AFTERCARE:
            return self.moans.get_aftercare()
        return self.moans.get('shy')
    
    # =========================================================================
    # STATUS
    # =========================================================================
    
    def get_status(self) -> str:
        """Dapatkan status sesi intim"""
        if not self.is_active:
            return "Tidak ada sesi intim aktif"
        
        duration = time.time() - self.start_time if self.start_time else 0
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        pos_data = self.positions.get(self.current_position)
        
        return f"""
🔥 **SESI INTIM AKTIF**
- Durasi: {minutes} menit {seconds} detik
- Climax: {self.climax_count}x
- Fase: {self.phase.value}
- Posisi: {self.current_position}
{pos_data['desc'] if pos_data else ''}

{self.stamina.format_for_prompt()}
{self.arousal.format_for_prompt()}
"""
    
    def get_summary(self) -> Dict:
        """Dapatkan ringkasan sesi"""
        duration = time.time() - self.start_time if self.start_time else 0
        
        return {
            'duration': duration,
            'climax_count': self.climax_count,
            'phase_changes': len(self.phase_history),
            'position_changes': len(self.position_history),
            'final_position': self.current_position,
            'max_intimacy_level': self.intimacy_level
        }
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def _add_to_history(self, event_type: str, description: str) -> None:
        """Tambah ke history"""
        self.phase_history.append({
            'timestamp': time.time(),
            'type': event_type,
            'phase': self.phase.value,
            'description': description,
            'climax_count': self.climax_count
        })
        
        if len(self.phase_history) > 100:
            self.phase_history.pop(0)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        return {
            'is_active': self.is_active,
            'start_time': self.start_time,
            'phase': self.phase.value,
            'climax_count': self.climax_count,
            'current_position': self.current_position,
            'intimacy_level': self.intimacy_level,
            'phase_history': self.phase_history[-50:],
            'position_history': self.position_history[-50:],
            'stamina': self.stamina.to_dict(),
            'arousal': self.arousal.to_dict()
        }
    
    def from_dict(self, data: Dict) -> None:
        self.is_active = data.get('is_active', False)
        self.start_time = data.get('start_time', 0)
        self.phase = IntimacyPhase(data.get('phase', 'none'))
        self.climax_count = data.get('climax_count', 0)
        self.current_position = data.get('current_position', 'missionary')
        self.intimacy_level = data.get('intimacy_level', 0)
        self.phase_history = data.get('phase_history', [])
        self.position_history = data.get('position_history', [])
        
        if 'stamina' in data:
            self.stamina.from_dict(data['stamina'])
        if 'arousal' in data:
            self.arousal.from_dict(data['arousal'])


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_intimacy_session: Optional[IntimacySession] = None


def get_intimacy_session() -> IntimacySession:
    """Get global intimacy session instance"""
    global _intimacy_session
    if _intimacy_session is None:
        _intimacy_session = IntimacySession()
    return _intimacy_session


def reset_intimacy_session() -> None:
    """Reset intimacy session (untuk testing)"""
    global _intimacy_session
    _intimacy_session = None
    logger.info("🔄 Intimacy Session reset")


__all__ = [
    'IntimacyPhase',
    'IntimacyAction',
    'ClimaxIntensity',
    'StaminaSystem',
    'ArousalSystem',
    'PositionDatabase',
    'MoansDatabase',
    'ClimaxLocationDatabase',
    'IntimacySession',
    'get_intimacy_session',
    'reset_intimacy_session'
]
