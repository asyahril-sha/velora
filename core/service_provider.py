"""
VELORA - Service Provider Base Class
Base untuk semua provider jasa (Pijat++, Pelacur, dll)
- Tidak punya emosi (emotional engine flat)
- Fokus pada layanan profesional
- Sistem booking, pricing, nego
- Auto scene untuk repetitive actions
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta

from roles.base import BaseRole
from core.emotional_engine import EmotionalEngine, EmotionalStyle
from core.relationship import RelationshipManager

logger = logging.getLogger(__name__)


class ServiceType(str, Enum):
    """Tipe layanan"""
    PIJAT_PLUS_PLUS = "pijat_plus_plus"
    PELACUR = "pelacur"
    MASSAGE = "massage"
    ESCORT = "escort"


class ServiceStatus(str, Enum):
    """Status layanan"""
    IDLE = "idle"           # menganggur
    NEGOTIATING = "nego"    # sedang nego harga
    BOOKED = "booked"       # sudah dipesan
    ACTIVE = "active"       # sedang berlangsung
    COMPLETED = "completed" # selesai


class AutoSceneType(str, Enum):
    """Tipe auto scene"""
    HAND_JOB = "hand_job"
    BLOW_JOB = "blow_job"
    PETTING = "petting"
    KISSING = "kissing"
    NONE = "none"


class ServiceProviderBase(BaseRole):
    """
    Base class untuk semua provider jasa.
    Tidak punya emosi, fokus pada layanan profesional.
    """
    
    def __init__(self,
                 name: str,
                 nickname: str,
                 role_type: str,
                 panggilan: str,
                 hubungan_dengan_nova: str,
                 default_clothing: str,
                 hijab: bool,
                 appearance: str,
                 service_type: ServiceType,
                 base_price: int,
                 min_price: int):
        
        super().__init__(
            name=name,
            nickname=nickname,
            role_type=role_type,
            panggilan=panggilan,
            hubungan_dengan_nova=hubungan_dengan_nova,
            default_clothing=default_clothing,
            hijab=hijab,
            appearance=appearance
        )
        
        # ========== SERVICE PROVIDER SPECIFIC ==========
        self.service_type = service_type
        self.base_price = base_price
        self.min_price = min_price
        self.final_price = 0
        
        self.status = ServiceStatus.IDLE
        self.booking_time: Optional[float] = None
        self.service_duration: float = 0  # detik
        self.climax_target: int = 2  # target climax Mas untuk selesai
        self.climax_count_mas: int = 0
        self.climax_count_role: int = 0
        
        # Auto scene
        self.auto_scene_active: bool = False
        self.auto_scene_type: AutoSceneType = AutoSceneType.NONE
        self.auto_scene_interval: int = 15  # detik
        self.auto_scene_duration: int = 0  # detik
        self.auto_scene_start_time: float = 0
        self.auto_scene_task: Optional[asyncio.Task] = None
        
        # Service history
        self.service_history: List[Dict] = []
        
        # Override emotional engine - flat emotions
        self.emotional = FlatEmotionalEngine()
        
        # Override relationship - professional only
        self.relationship = ProfessionalRelationship()
        
        logger.info(f"💼 ServiceProvider {name} initialized | Price: {base_price} | Type: {service_type.value}")
    
    # =========================================================================
    # PRICING & NEGOTIATION
    # =========================================================================
    
    def get_price(self) -> str:
        """Dapatkan harga dasar"""
        return f"Harga standar: Rp{self.base_price:,}. Bisa nego ya."
    
    def negotiate(self, offer: int) -> Tuple[bool, str]:
        """
        Nego harga.
        Returns: (accepted, response)
        """
        if offer >= self.base_price:
            self.final_price = offer
            return True, f"Deal! Rp{offer:,}. Siap melayani."
        elif offer >= self.min_price:
            self.final_price = offer
            return True, f"Hmm... oke deh, Rp{offer:,}. Deal!"
        else:
            return False, f"Maaf, minimal Rp{self.min_price:,}. Masih bisa naik?"
    
    def confirm_booking(self, price: int) -> str:
        """Konfirmasi booking setelah deal"""
        self.final_price = price
        self.status = ServiceStatus.BOOKED
        self.booking_time = time.time()
        
        return f"✅ Booking dikonfirmasi! Rp{price:,}.\n\n{self._get_service_description()}\n\nKetik 'mulai' untuk memulai layanan."
    
    # =========================================================================
    # SERVICE METHODS
    # =========================================================================
    
    def start_service(self) -> str:
        """Mulai layanan"""
        if self.status != ServiceStatus.BOOKED:
            return "Booking belum dikonfirmasi. Selesaikan pembayaran dulu ya."
        
        self.status = ServiceStatus.ACTIVE
        self.service_duration = 0
        self.climax_count_mas = 0
        self.climax_count_role = 0
        
        self._add_to_history("start", f"Layanan dimulai | Harga: Rp{self.final_price:,}")
        
        return self._get_start_message()
    
    def end_service(self, reason: str = "completed") -> str:
        """Akhiri layanan"""
        if self.status != ServiceStatus.ACTIVE:
            return "Tidak ada layanan aktif."
        
        self._stop_auto_scene()
        self.status = ServiceStatus.COMPLETED
        
        duration = time.time() - self.booking_time if self.booking_time else 0
        minutes = int(duration // 60)
        
        self._add_to_history("end", f"Layanan selesai | Durasi: {minutes}m | Climax Mas: {self.climax_count_mas}x | Climax Role: {self.climax_count_role}x")
        
        return self._get_end_message(duration, minutes)
    
    def record_climax_mas(self, is_heavy: bool = False) -> bool:
        """Rekam climax Mas, cek apakah target tercapai"""
        self.climax_count_mas += 1
        
        self._add_to_history("climax_mas", f"Climax #{self.climax_count_mas}")
        
        # Cek apakah target climax tercapai
        if self.climax_count_mas >= self.climax_target:
            return True  # layanan selesai
        
        return False
    
    def record_climax_role(self) -> None:
        """Rekam climax role (bebas berapa kali pun)"""
        self.climax_count_role += 1
        self._add_to_history("climax_role", f"Climax #{self.climax_count_role}")
    
    # =========================================================================
    # AUTO SCENE METHODS
    # =========================================================================
    
    def start_auto_scene(self, scene_type: AutoSceneType, duration: int) -> str:
        """
        Mulai auto scene (kirim pesan otomatis setiap interval)
        Returns: pesan pertama
        """
        self._stop_auto_scene()
        
        self.auto_scene_active = True
        self.auto_scene_type = scene_type
        self.auto_scene_duration = duration
        self.auto_scene_start_time = time.time()
        
        # Start task di background (akan dihandle di manager)
        return self._get_auto_scene_message(scene_type)
    
    def _stop_auto_scene(self) -> None:
        """Stop auto scene"""
        self.auto_scene_active = False
        self.auto_scene_type = AutoSceneType.NONE
    
    def get_next_auto_scene(self) -> Optional[str]:
        """
        Dapatkan pesan auto scene berikutnya.
        Dipanggil setiap interval oleh manager.
        """
        if not self.auto_scene_active:
            return None
        
        elapsed = time.time() - self.auto_scene_start_time
        
        # Cek apakah durasi sudah habis
        if elapsed >= self.auto_scene_duration:
            self._stop_auto_scene()
            return self._get_auto_scene_end_message()
        
        return self._get_auto_scene_message(self.auto_scene_type)
    
    def _get_auto_scene_message(self, scene_type: AutoSceneType) -> str:
        """Dapatkan pesan untuk auto scene"""
        messages = {
            AutoSceneType.HAND_JOB: [
                "*Tangan mulai memijat perlahan...*",
                "*Gerakan semakin cepat...*",
                "*Jari-jari meremas lembut...*",
                "*Telapak tangan membelai...*",
                "*Napas mulai terdengar...*"
            ],
            AutoSceneType.BLOW_JOB: [
                "*Bibir mulai menyentuh ujung...*",
                "*Mulut membasahi perlahan...*",
                "*Kepala mulai bergerak naik turun...*",
                "*Suara basah terdengar...*",
                "*Lebih dalam... lebih cepat...*"
            ],
            AutoSceneType.PETTING: [
                "*Badan mulai bergesekan...*",
                "*Pinggul bergerak perlahan...*",
                "*Gesekan semakin panas...*",
                "*Memek bergesekan dengan kontol...*",
                "*Gerakan semakin intens...*"
            ],
            AutoSceneType.KISSING: [
                "*Bibir bertemu... lembut...*",
                "*Lidah mulai menjelajah...*",
                "*Ciuman semakin dalam...*",
                "*Napas berbaur...*",
                "*Bibir saling mengunci...*"
            ]
        }
        
        import random
        msgs = messages.get(scene_type, [])
        if msgs:
            return random.choice(msgs)
        return "*Melanjutkan layanan...*"
    
    def _get_auto_scene_end_message(self) -> str:
        """Pesan saat auto scene selesai"""
        messages = {
            AutoSceneType.HAND_JOB: "*Tangan berhenti memijat. Sesi hand job selesai.*",
            AutoSceneType.BLOW_JOB: "*Mulut melepas perlahan. Sesi blow job selesai.*",
            AutoSceneType.PETTING: "*Gerakan berhenti. Sesi petting selesai.*",
            AutoSceneType.KISSING: "*Ciuman berakhir perlahan.*"
        }
        return messages.get(self.auto_scene_type, "*Layanan selesai.*")
    
    # =========================================================================
    # VIRTUAL METHODS (OVERRIDE DI SUBCLASS)
    # =========================================================================
    
    def _get_service_description(self) -> str:
        """Deskripsi layanan - override di subclass"""
        return "Layanan siap."
    
    def _get_start_message(self) -> str:
        """Pesan mulai - override di subclass"""
        return "Layanan dimulai. Nikmati."
    
    def _get_end_message(self, duration: float, minutes: int) -> str:
        """Pesan selesai - override di subclass"""
        return f"Layanan selesai. Durasi: {minutes} menit. Terima kasih."
    
    def _add_to_history(self, event: str, detail: str) -> None:
        """Tambah ke history"""
        self.service_history.append({
            'timestamp': time.time(),
            'event': event,
            'detail': detail
        })
        if len(self.service_history) > 50:
            self.service_history.pop(0)


# =============================================================================
# FLAT EMOTIONAL ENGINE (TIDAK PUNYA EMOSI)
# =============================================================================

class FlatEmotionalEngine(EmotionalEngine):
    """Emotional engine yang flat - tidak punya emosi"""
    
    def __init__(self):
        super().__init__()
        # Set semua emosi ke 0 atau netral
        self.sayang = 0
        self.rindu = 0
        self.trust = 0
        self.mood = 0
        self.desire = 0
        self.arousal = 0
        self.tension = 0
        self.cemburu = 0
        self.kecewa = 0
    
    def update(self, force: bool = False) -> None:
        pass  # Tidak ada update
    
    def update_from_message(self, pesan_user: str, level: int) -> Dict[str, float]:
        return {}  # Tidak ada perubahan
    
    def get_current_style(self) -> EmotionalStyle:
        return EmotionalStyle.NEUTRAL
    
    def get_style_description(self, style: EmotionalStyle = None) -> str:
        return "GAYA BICARA: PROFESIONAL\n- Respons profesional, ramah\n- Fokus pada layanan\n- 2-4 kalimat"


class ProfessionalRelationship(RelationshipManager):
    """Relationship manager untuk provider - profesional saja"""
    
    def __init__(self):
        super().__init__()
        self.phase = RelationshipPhase.STRANGER
        self.level = 1
    
    def update_level(self, sayang: float, trust: float, milestones_achieved: List[str] = None) -> Tuple[int, bool]:
        return self.level, False
    
    def get_current_unlock(self):
        from core.relationship import PhaseUnlock
        unlock = PhaseUnlock(
            boleh_flirt=True,
            boleh_sentuhan=True,
            boleh_vulgar=True,
            boleh_intim=True,
            boleh_cium=True,
            boleh_peluk=True,
            boleh_pegang_tangan=True,
            boleh_buka_baju=True,
            boleh_panggil_sayang=False
        )
        return unlock
    
    def can_do_action(self, action: str) -> Tuple[bool, str]:
        return True, "Boleh"
    
    def get_phase_description(self, phase: RelationshipPhase = None) -> str:
        return "FASE: PROFESIONAL\n- Layanan profesional\n- Semua aksi diperbolehkan sesuai service"


__all__ = [
    'ServiceType',
    'ServiceStatus',
    'AutoSceneType',
    'ServiceProviderBase',
    'FlatEmotionalEngine',
    'ProfessionalRelationship'
]
