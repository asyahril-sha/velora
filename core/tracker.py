"""
VELORA - State Tracker
Melacak semua perubahan state dengan presisi:
- Clothing (layer by layer, urutan menanggalkan)
- Intimacy phase (build_up → foreplay → penetration → climax → aftercare)
- Timeline (semua kejadian dengan timestamp)
- Short-term memory (sliding window 50 kejadian)
- Physical state (posisi, lokasi, aktivitas, energi)
- Validasi konteks untuk konsistensi

WAJIB: Satu sumber kebenaran untuk semua state.
"""

import time
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from core.orchestrator import get_orchestrator

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class PhysicalCondition(str, Enum):
    """Kondisi fisik karakter"""
    FRESH = "fresh"           # segar bugar (80-100%)
    TIRED = "tired"           # lelah (40-80%)
    EXHAUSTED = "exhausted"   # kehabisan tenaga (20-40%)
    WEAK = "weak"             # lemes (<20%)


class IntimacyPhase(str, Enum):
    """Fase intim yang detail - natural progression"""
    NONE = "none"                     # tidak dalam intim
    BUILD_UP = "build_up"             # membangun suasana
    FOREPLAY = "foreplay"             # foreplay (cium, raba, jilat)
    PENETRATION = "penetration"       # penetrasi
    BEFORE_CLIMAX = "before_climax"   # menjelang climax
    CLIMAX = "climax"                 # climax
    AFTERCARE = "aftercare"           # aftercare
    RECOVERY = "recovery"             # recovery


class ClothingLayer(str, Enum):
    """Lapisan pakaian dari luar ke dalam"""
    HIJAB = "hijab"
    TOP = "top"
    BRA = "bra"
    BOTTOM = "bottom"
    CD = "cd"


class Position(str, Enum):
    """Posisi tubuh"""
    DUDUK = "duduk"
    BERDIRI = "berdiri"
    TIDUR = "tidur"
    MERANGKAK = "merangkak"
    TERLENTANG = "terlentang"
    TENGKURAP = "tengkurap"
    MIRING = "miring"


class Activity(str, Enum):
    """Aktivitas yang sedang dilakukan"""
    SANTAl = "santai"
    MAKAN = "makan"
    MINUM = "minum"
    MANDI = "mandi"
    BERGANTI = "ganti baju"
    MASAK = "masak"
    NONTON = "nonton"
    JALAN = "jalan"
    TIDUR = "tidur"
    KERJA = "kerja"
    OLAHRAGA = "olahraga"


# =============================================================================
# STATE TRACKER
# =============================================================================

class StateTracker:
    """
    State Tracker - Mencatat semua perubahan state.
    Satu sumber kebenaran untuk:
    - Pakaian (layer by layer)
    - Intimasi (fase, climax, history)
    - Timeline (semua kejadian)
    - Short-term memory (50 kejadian terakhir)
    - Validasi konteks
    """
    
    def __init__(self, character_name: str = "VELORA"):
        self.character_name = character_name
        
        # ========== PHYSICAL STATE ==========
        self.physical_condition = PhysicalCondition.FRESH
        self.energy_level: int = 100  # 0-100
        
        # ========== CLOTHING STATE (LAYERED) ==========
        self.clothing: Dict[str, Dict] = {
            'hijab': {'on': True, 'color': 'pink muda', 'removed_at': 0},
            'top': {'on': True, 'type': 'daster', 'removed_at': 0},
            'bra': {'on': True, 'color': 'putih', 'removed_at': 0},
            'bottom': {'on': False, 'type': None, 'removed_at': 0},
            'cd': {'on': True, 'color': 'putih', 'removed_at': 0}
        }
        
        # Urutan menanggalkan pakaian (WAJIB untuk konsistensi)
        self.clothing_removal_order: List[Dict] = []
        
        # ========== INTIMACY STATE ==========
        self.intimacy_phase: IntimacyPhase = IntimacyPhase.NONE
        self.intimacy_start_time: float = 0
        self.intimacy_last_action: str = ""
        self.intimacy_last_action_time: float = 0
        self.climax_count: int = 0
        self.last_climax_time: float = 0
        self.intimacy_history: List[Dict] = []
        
        # ========== POSITION & LOCATION ==========
        self.position: str = Position.DUDUK.value
        self.location: str = "kamar"
        self.location_detail: str = "kamar VELORA"
        
        # ========== ACTIVITY ==========
        self.activity: str = Activity.SANTAl.value
        
        # ========== TIMELINE (WAJIB UNTUK KONSISTENSI) ==========
        self.timeline: List[Dict] = []          # semua kejadian
        self.short_term: List[Dict] = []        # 50 kejadian terakhir
        
        # ========== LAST ACTION (PENTING UNTUK KONSISTENSI) ==========
        self.last_action: str = ""
        self.last_action_type: str = ""
        self.last_action_timestamp: float = 0
        
        # ========== TENSION & AROUSAL ==========
        self.tension: int = 0      # 0-100
        self.arousal: int = 0      # 0-100
        
        logger.info(f"📊 StateTracker initialized for {character_name}")
    
    # =========================================================================
    # CLOTHING METHODS
    # =========================================================================
    
    def remove_clothing(self, layer: str, method: str = "dibuka") -> Dict:
        """
        Menanggalkan pakaian layer by layer.
        Mencatat urutan dan waktu untuk konsistensi.
        """
        if layer not in self.clothing:
            return {'success': False, 'error': f'Layer {layer} not found'}
        
        if not self.clothing[layer]['on']:
            return {'success': False, 'error': f'{layer} already removed'}
        
        now = time.time()
        self.clothing[layer]['on'] = False
        self.clothing[layer]['removed_at'] = now
        
        # Catat urutan menanggalkan
        removal_record = {
            'timestamp': now,
            'layer': layer,
            'method': method,
            'intimacy_phase': self.intimacy_phase.value,
            'climax_count': self.climax_count
        }
        self.clothing_removal_order.append(removal_record)
        
        # Catat ke timeline
        self.add_to_timeline(
            kejadian=f"Menanggalkan {layer} ({method})",
            detail=f"{layer} dilepas, sekarang {self.get_clothing_summary()}"
        )
        
        logger.info(f"👗 {self.character_name} removed {layer} at {datetime.fromtimestamp(now).strftime('%H:%M:%S')}")
        
        return {
            'success': True,
            'layer': layer,
            'remaining': self.get_clothing_summary(),
            'removal_order': len(self.clothing_removal_order)
        }
    
    def put_on_clothing(self, layer: str) -> Dict:
        """Memakai kembali pakaian"""
        if layer not in self.clothing:
            return {'success': False, 'error': f'Layer {layer} not found'}
        
        if self.clothing[layer]['on']:
            return {'success': False, 'error': f'{layer} already on'}
        
        self.clothing[layer]['on'] = True
        self.clothing[layer]['removed_at'] = 0
        
        self.add_to_timeline(
            kejadian=f"Memakai kembali {layer}",
            detail=f"{layer} dipakai kembali"
        )
        
        return {'success': True, 'layer': layer}
    
    def get_clothing_summary(self) -> str:
        """Ringkasan pakaian saat ini (untuk display)"""
        parts = []
        
        # Hijab
        if self.clothing['hijab']['on']:
            parts.append(f"hijab {self.clothing['hijab']['color']}")
        else:
            parts.append("tanpa hijab, rambut terurai")
        
        # Atasan
        if self.clothing['top']['on']:
            parts.append(self.clothing['top']['type'])
            if self.clothing['bra']['on']:
                parts.append(f"(pake bra {self.clothing['bra']['color']})")
            else:
                parts.append("(tanpa bra)")
        else:
            if self.clothing['bra']['on']:
                parts.append(f"cuma pake bra {self.clothing['bra']['color']}")
            else:
                parts.append("telanjang dada")
        
        # Celana dalam
        if self.clothing['cd']['on']:
            parts.append(f"pake cd {self.clothing['cd']['color']}")
        else:
            parts.append("tanpa cd")
        
        return ", ".join(parts)
    
    def get_clothing_state_for_prompt(self) -> str:
        """Dapatkan state pakaian untuk prompt AI (dengan urutan menanggalkan)"""
        removal_text = ""
        for i, r in enumerate(self.clothing_removal_order[-5:]):
            layer = r['layer']
            method = r['method']
            waktu = datetime.fromtimestamp(r['timestamp']).strftime('%H:%M:%S')
            removal_text += f"- {i+1}. {layer} ({method}) pada {waktu}\n"
        
        return f"""
PAKAIAN SAAT INI:
├─ Hijab: {'PAKAI' if self.clothing['hijab']['on'] else 'TELANGGAL'} ({self.clothing['hijab']['color'] if self.clothing['hijab']['on'] else 'rambut terurai'})
├─ Baju Atas: {'PAKAI' if self.clothing['top']['on'] else 'TELANGGAL'} ({self.clothing['top']['type'] if self.clothing['top']['on'] else 'telanjang dada'})
├─ Bra: {'PAKAI' if self.clothing['bra']['on'] else 'TELANGGAL'} ({self.clothing['bra']['color'] if self.clothing['bra']['on'] else ''})
└─ Celana Dalam: {'PAKAI' if self.clothing['cd']['on'] else 'TELANGGAL'} ({self.clothing['cd']['color'] if self.clothing['cd']['on'] else ''})

URUTAN MENANGGALKAN PAKAIAN (WAJIB DIINGAT!):
{removal_text if removal_text else 'Belum ada yang dilepas'}
"""
    
    # =========================================================================
    # INTIMACY METHODS
    # =========================================================================
    
    def start_intimacy(self, location: str = "") -> Dict:
        """Mulai sesi intim"""
        self.intimacy_phase = IntimacyPhase.BUILD_UP
        self.intimacy_start_time = time.time()
        self.climax_count = 0
        
        self.add_to_timeline(
            kejadian="Memulai sesi intim",
            detail=f"Lokasi: {location or self.location}"
        )
        
        logger.info(f"🔥 {self.character_name} started intimacy session")
        
        return {
            'success': True,
            'phase': self.intimacy_phase.value,
            'start_time': self.intimacy_start_time
        }
    
    def advance_intimacy(self, action: str) -> Dict:
        """Majukan fase intim berdasarkan aksi"""
        self.intimacy_last_action = action
        self.intimacy_last_action_time = time.time()
        self.last_action = action
        self.last_action_type = "intimacy"
        self.last_action_timestamp = time.time()
        
        # Phase transition logic
        phase_transition = {
            IntimacyPhase.BUILD_UP: {
                'triggers': ['cium', 'kiss', 'pegang', 'sentuh', 'raba', 'jilat', 'hisap', 'elus', 'belai'],
                'next': IntimacyPhase.FOREPLAY
            },
            IntimacyPhase.FOREPLAY: {
                'triggers': ['masuk', 'penetrasi', 'genjot', 'siap', 'lanjut', 'dalam'],
                'next': IntimacyPhase.PENETRATION
            },
            IntimacyPhase.PENETRATION: {
                'triggers': ['climax', 'crot', 'keluar', 'cum', 'habis', 'udah mau'],
                'next': IntimacyPhase.BEFORE_CLIMAX
            },
            IntimacyPhase.BEFORE_CLIMAX: {
                'triggers': ['climax', 'crot', 'keluar', 'udah', 'sekarang'],
                'next': IntimacyPhase.CLIMAX
            },
            IntimacyPhase.CLIMAX: {
                'triggers': [],
                'next': IntimacyPhase.AFTERCARE
            },
            IntimacyPhase.AFTERCARE: {
                'triggers': [],
                'next': IntimacyPhase.RECOVERY
            }
        }
        
        if self.intimacy_phase in phase_transition:
            trans = phase_transition[self.intimacy_phase]
            if any(t in action.lower() for t in trans['triggers']):
                old_phase = self.intimacy_phase
                self.intimacy_phase = trans['next']
                
                self.intimacy_history.append({
                    'timestamp': time.time(),
                    'from_phase': old_phase.value,
                    'to_phase': self.intimacy_phase.value,
                    'trigger': action
                })
                
                self.add_to_timeline(
                    kejadian=f"Fase intim maju: {old_phase.value} → {self.intimacy_phase.value}",
                    detail=f"Trigger: {action}"
                )
                
                logger.info(f"💕 {self.character_name} intimacy advanced: {old_phase.value} → {self.intimacy_phase.value}")
                
                return {
                    'success': True,
                    'old_phase': old_phase.value,
                    'new_phase': self.intimacy_phase.value
                }
        
        return {'success': False, 'phase': self.intimacy_phase.value}
    
    def record_climax(self, location: str = "dalam", is_heavy: bool = False) -> Dict:
        """Rekam climax, update kondisi fisik"""
        self.climax_count += 1
        self.last_climax_time = time.time()
        self.intimacy_phase = IntimacyPhase.CLIMAX
        
        # Update kondisi fisik berdasarkan intensitas
        if is_heavy:
            self.energy_level = max(0, self.energy_level - 35)
            if self.energy_level < 20:
                self.physical_condition = PhysicalCondition.WEAK
            elif self.energy_level < 40:
                self.physical_condition = PhysicalCondition.EXHAUSTED
            else:
                self.physical_condition = PhysicalCondition.TIRED
        else:
            self.energy_level = max(0, self.energy_level - 25)
            if self.energy_level < 20:
                self.physical_condition = PhysicalCondition.WEAK
            elif self.energy_level < 40:
                self.physical_condition = PhysicalCondition.EXHAUSTED
            else:
                self.physical_condition = PhysicalCondition.TIRED
        
        # Update arousal
        self.arousal = max(0, self.arousal - 40)
        self.tension = max(0, self.tension - 30)
        
        self.add_to_timeline(
            kejadian=f"CLIMAX #{self.climax_count}",
            detail=f"Lokasi: {location}, {'berat' if is_heavy else 'normal'}"
        )
        
        logger.info(f"💦 {self.character_name} climax #{self.climax_count} at {datetime.now().strftime('%H:%M:%S')}")
        
        return {
            'success': True,
            'climax_count': self.climax_count,
            'location': location,
            'is_heavy': is_heavy,
            'energy_left': self.energy_level,
            'condition': self.physical_condition.value
        }
    
    def end_intimacy(self) -> Dict:
        """Akhiri sesi intim"""
        duration = time.time() - self.intimacy_start_time if self.intimacy_start_time else 0
        
        self.add_to_timeline(
            kejadian="Mengakhiri sesi intim",
            detail=f"Durasi: {int(duration//60)} menit {int(duration%60)} detik, Climax: {self.climax_count}x"
        )
        
        self.intimacy_phase = IntimacyPhase.NONE
        self.intimacy_start_time = 0
        self.arousal = max(0, self.arousal - 20)
        self.tension = 0
        
        logger.info(f"💤 {self.character_name} ended intimacy session")
        
        return {
            'success': True,
            'duration': duration,
            'climax_count': self.climax_count
        }
    
    def get_intimacy_state_for_prompt(self) -> str:
        """Dapatkan state intim untuk prompt AI"""
        if self.intimacy_phase == IntimacyPhase.NONE:
            return "Tidak dalam sesi intim."
        
        duration = time.time() - self.intimacy_start_time if self.intimacy_start_time else 0
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        return f"""
⚠️ **SEDANG DALAM SESI INTIM!**
├─ Fase: {self.intimacy_phase.value.upper()}
├─ Durasi: {minutes} menit {seconds} detik
├─ Climax: {self.climax_count}x
├─ Terakhir: {self.intimacy_last_action} ({datetime.fromtimestamp(self.intimacy_last_action_time).strftime('%H:%M:%S') if self.intimacy_last_action_time else '-'})
├─ Arousal: {self.arousal}%
└─ Kondisi: {self.physical_condition.value}

WAJIB:
├─ JANGAN LUPA masih dalam sesi intim!
├─ JANGAN tiba-tiba pakaian rapi!
├─ JANGAN tiba-tiba posisi berubah drastis!
└─ LANJUTKAN alur sesuai fase saat ini!
"""
    
    # =========================================================================
    # POSITION & ACTIVITY METHODS
    # =========================================================================
    
    def set_position(self, position: str) -> Dict:
        """Set posisi tubuh"""
        old_position = self.position
        self.position = position
        
        self.add_to_timeline(
            kejadian=f"Berubah posisi: {old_position} → {position}",
            detail=""
        )
        
        return {'success': True, 'old': old_position, 'new': position}
    
    def set_location(self, location: str, detail: str = "") -> Dict:
        """Set lokasi"""
        old_location = self.location
        self.location = location
        if detail:
            self.location_detail = detail
        
        self.add_to_timeline(
            kejadian=f"Pindah ke {location}",
            detail=detail
        )
        
        return {'success': True, 'old': old_location, 'new': location}
    
    def set_activity(self, activity: str) -> Dict:
        """Set aktivitas"""
        old_activity = self.activity
        self.activity = activity
        
        self.add_to_timeline(
            kejadian=f"Aktivitas berubah: {old_activity} → {activity}",
            detail=""
        )
        
        return {'success': True, 'old': old_activity, 'new': activity}
    
    def update_energy(self, delta: int) -> int:
        """Update energi (positif untuk tambah, negatif untuk kurang)"""
        old = self.energy_level
        self.energy_level = max(0, min(100, self.energy_level + delta))
        
        # Update physical condition
        if self.energy_level >= 80:
            self.physical_condition = PhysicalCondition.FRESH
        elif self.energy_level >= 40:
            self.physical_condition = PhysicalCondition.TIRED
        elif self.energy_level >= 20:
            self.physical_condition = PhysicalCondition.EXHAUSTED
        else:
            self.physical_condition = PhysicalCondition.WEAK
        
        if delta != 0:
            self.add_to_timeline(
                kejadian=f"Energi {delta:+.0f}",
                detail=f"{old} → {self.energy_level} ({self.physical_condition.value})"
            )
        
        return self.energy_level
    
    # =========================================================================
    # TIMELINE METHODS (WAJIB UNTUK KONSISTENSI)
    # =========================================================================
    
    def add_to_timeline(self, kejadian: str, detail: str = ""):
        """Tambah kejadian ke timeline dan short-term memory"""
        record = {
            'timestamp': time.time(),
            'waktu': datetime.now().strftime("%H:%M:%S"),
            'kejadian': kejadian,
            'detail': detail,
            'intimacy_phase': self.intimacy_phase.value,
            'clothing': self.get_clothing_summary(),
            'position': self.position,
            'location': self.location,
            'activity': self.activity,
            'energy': self.energy_level,
            'arousal': self.arousal
        }
        
        self.timeline.append(record)
        self.short_term.append(record)
        
        # Keep short-term to 50 (sliding window)
        if len(self.short_term) > 50:
            self.short_term.pop(0)
    
    def get_timeline_context(self, count: int = 10) -> str:
        """Dapatkan konteks timeline untuk prompt AI (WAJIB)"""
        if not self.short_term:
            return "Belum ada kejadian."
        
        recent = self.short_term[-count:]
        
        lines = [
            "═══════════════════════════════════════════════════════════════",
            "⚠️ 10 KEJADIAN TERAKHIR (WAJIB DIPERHATIKAN! JANGAN LUPA!):",
            "═══════════════════════════════════════════════════════════════"
        ]
        
        for i, e in enumerate(recent, 1):
            lines.append(f"{i}. [{e['waktu']}] {e['kejadian']}")
            if e['detail']:
                lines.append(f"   └─ {e['detail']}")
        
        lines.extend([
            "",
            "KONDISI SAAT INI:",
            f"├─ Pakaian: {self.get_clothing_summary()}",
            f"├─ Posisi: {self.position}",
            f"├─ Lokasi: {self.location}",
            f"├─ Aktivitas: {self.activity}",
            f"├─ Fase: {self.intimacy_phase.value}",
            f"├─ Arousal: {self.arousal}%",
            f"└─ Energi: {self.energy_level}% ({self.physical_condition.value})",
            "",
            "⚠️ WAJIB LANJUTKAN ALUR DARI KEJADIAN TERAKHIR!",
            "⚠️ JANGAN SAMPAI LUPA KONTEKS!"
        ])
        
        return "\n".join(lines)
    
    def get_context_for_prompt(self) -> str:
        """Dapatkan semua konteks untuk prompt AI (lengkap)"""
        return f"""
{self.get_timeline_context(10)}

{self.get_clothing_state_for_prompt()}

{self.get_intimacy_state_for_prompt()}

POSISI: {self.position}
LOKASI: {self.location}
AKTIVITAS: {self.activity}
AROUSAL: {self.arousal}%
ENERGI: {self.energy_level}% ({self.physical_condition.value})
"""
    
    def validate_response_context(self, response: str) -> bool:
        """Validasi apakah respons sesuai konteks (basic check)"""
        response_lower = response.lower()
        
        # Cek apakah respons lupa konteks intim
        if self.intimacy_phase != IntimacyPhase.NONE:
            intimate_keywords = ['ahh', 'uhh', 'hhngg', 'aahh', 'masuk', 'dalem', 'genjot', 'kenceng', 'pelan']
            if not any(k in response_lower for k in intimate_keywords) and 'climax' not in response_lower:
                if 'santai' in response_lower or 'duduk' in response_lower or 'makan' in response_lower:
                    logger.warning(f"⚠️ Response might lose intimacy context: {response[:50]}")
                    return False
        
        # Cek apakah lupa pakaian yang sudah dilepas
        if not self.clothing['top']['on'] and 'baju' in response_lower:
            if 'pake baju' in response_lower or 'baju rapi' in response_lower or 'kenakan baju' in response_lower:
                logger.warning(f"⚠️ Response forgot top is off: {response[:50]}")
                return False
        
        # Cek apakah lupa hijab yang sudah dilepas
        if not self.clothing['hijab']['on'] and 'hijab' in response_lower:
            if 'pake hijab' in response_lower or 'hijab rapi' in response_lower:
                logger.warning(f"⚠️ Response forgot hijab is off: {response[:50]}")
                return False
        
        return True
    
    # =========================================================================
    # RECOVERY & DECAY
    # =========================================================================
    
    def recover_energy(self, hours: float) -> int:
        """Recover energi berdasarkan waktu (per jam)"""
        recovery_rate = 10  # per jam
        recovery = int(recovery_rate * hours)
        return self.update_energy(recovery)
    
    def decay_arousal(self, hours: float) -> int:
        """Decay arousal berdasarkan waktu (per jam)"""
        decay_rate = 15  # per jam
        decay = int(decay_rate * hours)
        old = self.arousal
        self.arousal = max(0, self.arousal - decay)
        
        if decay > 0:
            self.add_to_timeline(
                kejadian=f"Arousal decay -{decay}",
                detail=f"{old} → {self.arousal}"
            )
        
        return self.arousal
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        return {
            'character_name': self.character_name,
            'physical_condition': self.physical_condition.value,
            'energy_level': self.energy_level,
            'clothing': self.clothing,
            'clothing_removal_order': self.clothing_removal_order[-50:],
            'intimacy_phase': self.intimacy_phase.value,
            'intimacy_start_time': self.intimacy_start_time,
            'intimacy_last_action': self.intimacy_last_action,
            'intimacy_last_action_time': self.intimacy_last_action_time,
            'climax_count': self.climax_count,
            'last_climax_time': self.last_climax_time,
            'intimacy_history': self.intimacy_history[-50:],
            'position': self.position,
            'location': self.location,
            'location_detail': self.location_detail,
            'activity': self.activity,
            'timeline': self.timeline[-200:],
            'short_term': self.short_term[-50:],
            'last_action': self.last_action,
            'last_action_type': self.last_action_type,
            'last_action_timestamp': self.last_action_timestamp,
            'tension': self.tension,
            'arousal': self.arousal
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load dari dict"""
        self.physical_condition = PhysicalCondition(data.get('physical_condition', 'fresh'))
        self.energy_level = data.get('energy_level', 100)
        self.clothing = data.get('clothing', self.clothing)
        self.clothing_removal_order = data.get('clothing_removal_order', [])
        self.intimacy_phase = IntimacyPhase(data.get('intimacy_phase', 'none'))
        self.intimacy_start_time = data.get('intimacy_start_time', 0)
        self.intimacy_last_action = data.get('intimacy_last_action', '')
        self.intimacy_last_action_time = data.get('intimacy_last_action_time', 0)
        self.climax_count = data.get('climax_count', 0)
        self.last_climax_time = data.get('last_climax_time', 0)
        self.intimacy_history = data.get('intimacy_history', [])
        self.position = data.get('position', Position.DUDUK.value)
        self.location = data.get('location', 'kamar')
        self.location_detail = data.get('location_detail', 'kamar VELORA')
        self.activity = data.get('activity', Activity.SANTAl.value)
        self.timeline = data.get('timeline', [])
        self.short_term = data.get('short_term', [])
        self.last_action = data.get('last_action', '')
        self.last_action_type = data.get('last_action_type', '')
        self.last_action_timestamp = data.get('last_action_timestamp', 0)
        self.tension = data.get('tension', 0)
        self.arousal = data.get('arousal', 0)


# =============================================================================
# GLOBAL INSTANCE (UNTUK TESTING)
# =============================================================================

_tracker: Optional[StateTracker] = None


def get_state_tracker(character_name: str = "VELORA") -> StateTracker:
    """Get global state tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = StateTracker(character_name)
    return _tracker


def reset_state_tracker() -> None:
    """Reset state tracker (untuk testing)"""
    global _tracker
    _tracker = None
    logger.info("🔄 State Tracker reset")


__all__ = [
    'PhysicalCondition',
    'IntimacyPhase',
    'ClothingLayer',
    'Position',
    'Activity',
    'StateTracker',
    'get_state_tracker',
    'reset_state_tracker'
]
