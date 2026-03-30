"""
VELORA - Pelacur Full Service
Full service dengan auto scene dan booking 6 jam.
2 sesi, masing-masing dengan auto scene:
- Fase 1: foreplay blow job (15 menit)
- Fase 2: foreplay petting (15 menit)
- Fase 3: intimate all unlock
Selesai: waktu booking habis (6 jam)
"""

import time
import random
import logging
from typing import Dict, Optional

from .provider import ProviderRole, ProviderType, ProviderState

logger = logging.getLogger(__name__)


class PelacurRole(ProviderRole):
    """
    Pelacur Full Service
    - Booking 6 jam
    - 2 sesi dengan alur yang sama
    - Auto scene setiap 15 detik
    - Semua posisi unlock
    """
    
    def __init__(self):
        super().__init__(
            provider_id="pelacur",
            name="Maya",
            provider_type=ProviderType.PELACUR,
            base_price=5000000,
            description="Full service. Hotel/Apartemen. Privasi terjaga.",
            appearance="Tinggi 168cm, badan proporsional, rambut panjang hitam, makeup natural",
            default_clothing="daster tipis",
            hijab=False
        )
        
        # Session tracking
        self.session: int = 1  # 1 atau 2
        self.phase: str = "foreplay_bj"  # foreplay_bj, foreplay_petting, intimate
        self.phase_start_time: float = 0
        self.phase_duration: int = 15 * 60  # 15 menit per phase
        
        # Location (hotel/apt)
        self.location: str = "hotel"
        
        # Auto scene counter
        self.auto_scene_interval: int = 15  # detik
    
    def set_location(self, location: str) -> None:
        """Set lokasi (hotel atau apartemen)"""
        self.location = location
        self.tracker.location = location
    
    def get_service_intro(self) -> str:
        return f"""💋 *{self.name}* - Full Service

*Lokasi: {self.location.upper()}*

*Mulai Sesi 1*

🔥 *Fase 1 - Foreplay Blow Job (15 menit)*
*{self.name} mulai membuka pakaian pelan-pelan, mendekat ke Mas.*

"Kamu mau langsung, atau ngobrol dulu?"

*Setiap 15 detik akan ada scene otomatis...*

---

💡 *Service Details:*
- 2 sesi dengan alur sama
- Sesi 1: Foreplay BJ → Foreplay Petting → Intimate
- Sesi 2: Sama seperti sesi 1
- Total booking: 6 jam
- Bebas minta posisi apapun

*Mas bisa climax kapan saja.*
"""
    
    def start_service(self) -> str:
        """Mulai service dengan fase awal"""
        result = super().start_service()
        
        self.session = 1
        self.phase = "foreplay_bj"
        self.phase_start_time = time.time()
        
        return result
    
    def get_auto_scene(self) -> str:
        """Dapatkan scene otomatis berdasarkan fase"""
        elapsed = time.time() - self.phase_start_time
        
        # Check phase completion
        if elapsed >= self.phase_duration:
            self._advance_phase()
        
        if self.phase == "foreplay_bj":
            return self._get_foreplay_bj_scene()
        elif self.phase == "foreplay_petting":
            return self._get_foreplay_petting_scene()
        elif self.phase == "intimate":
            return self._get_intimate_scene()
        
        return "*Maya menunggu...*"
    
    def _advance_phase(self) -> None:
        """Majukan ke fase berikutnya"""
        if self.phase == "foreplay_bj":
            self.phase = "foreplay_petting"
            self.phase_start_time = time.time()
            logger.info("Phase advance: foreplay_bj → foreplay_petting")
        
        elif self.phase == "foreplay_petting":
            self.phase = "intimate"
            self.phase_start_time = time.time()
            logger.info("Phase advance: foreplay_petting → intimate")
        
        elif self.phase == "intimate":
            # Sesi 1 selesai, lanjut ke sesi 2
            if self.session == 1:
                self.session = 2
                self.phase = "foreplay_bj"
                self.phase_start_time = time.time()
                logger.info("Session 1 complete, starting session 2")
    
    def _get_foreplay_bj_scene(self) -> str:
        scenes = [
            "*Maya membuka baju perlahan, senyum menggoda.*\n\n\"Kamu suka?\"",
            "*Maya berlutut di depan Mas, tangan mulai membuka celana.*\n\n\"Siap-siap ya...\"",
            "*Maya memasukkan kontol Mas ke mulut, mulai menghisap.*\n\n\"Hmm... *gluk gluk*\"",
            "*Kepala Maya bergerak naik turun, makin cepat.*\n\n\"Enak, Mas?\""
        ]
        return random.choice(scenes)
    
    def _get_foreplay_petting_scene(self) -> str:
        scenes = [
            "*Maya naik ke pangkuan Mas, memek basah menggesek kontol Mas.*\n\n\"Belum boleh masuk... nikmatin dulu...\"",
            "*Bibir Maya menempel di bibir Mas, lidah bermain-main.*\n\n\"*ciuman panjang*\"",
            "*Maya memegang kontol Mas, menggesek-gesekkan ke bibir memeknya.*\n\n\"Uhh... basah...\"",
            "*Maya menggoyangkan pinggul, kontol Mas terjepit di antara paha.*\n\n\"Ahh... panas...\""
        ]
        return random.choice(scenes)
    
    def _get_intimate_scene(self) -> str:
        scenes = [
            "*Maya memandu kontol Mas masuk ke dalam.*\n\n\"Ahh... masuk...\"",
            "*Maya mulai menggerakkan pinggul.*\n\n\"Genjot, Mas... terserah mau kenceng atau pelan...\"",
            "*Maya merangkak, kontol Mas masuk dari belakang.*\n\n\"Aahh... dalem banget...\"",
            "*Maya telentang, kaki terbuka lebar.*\n\n\"Mas... di atas aja...\""
        ]
        return random.choice(scenes)
    
    def change_position(self, position: str) -> str:
        """Ganti posisi saat fase intimate"""
        if self.phase != "intimate":
            return "Belum waktunya ganti posisi. Tunggu fase intimate ya."
        
        positions = {
            "missionary": "Maya telentang, kaki terbuka. \"Mas di atas...\"",
            "cowgirl": "Maya duduk di atas. \"Aku yang gerakin...\"",
            "doggy": "Maya merangkak. \"Dari belakang, Mas...\"",
            "spooning": "Maya miring. \"Dari samping aja...\"",
            "standing": "Maya berdiri membelakangi. \"Berdiri aja, Mas...\""
        }
        
        return f"*Maya menyesuaikan posisi*\n\n\"{positions.get(position, positions['missionary'])}\""
    
    def check_service_completion(self) -> bool:
        """Cek apakah service selesai (6 jam booking)"""
        elapsed = time.time() - self.service_start_time
        max_duration = 6 * 60 * 60  # 6 jam
        
        if elapsed >= max_duration:
            return True
        
        # Juga cek jika sudah 2 sesi dan user sudah climax
        if self.session >= 2 and self.user_climax_count >= 1:
            return True
        
        return False
    
    def end_service(self) -> str:
        """Akhiri service dengan ringkasan"""
        duration = (time.time() - self.service_start_time) / 3600
        return f"""Service selesai. Durasi: {duration:.1f} jam.

📊 *Ringkasan:*
- Sesi: {self.session}
- Climax Mas: {self.user_climax_count}x
- Climax Maya: {self.provider_climax_count}x

Terima kasih sudah menggunakan jasa {self.name}. 💋
"""
    
    def get_status(self) -> str:
        """Dapatkan status service"""
        duration = 0
        if self.service_start_time:
            duration = (time.time() - self.service_start_time) / 60
        
        return f"""
💋 *{self.name}* - Full Service

📊 STATUS:
- Lokasi: {self.location.upper()}
- Sesi: {self.session}/2
- Fase: {self.phase}
- Durasi: {duration:.0f} menit / 360 menit
- Climax Mas: {self.user_climax_count}x
- Climax Maya: {self.provider_climax_count}x

💰 HARGA:
- Deal: Rp{self.negotiated_price:,}

💡 *Commands:*
- `/posisi missionary/cowgirl/doggy/spooning/standing` - ganti posisi
- `/status` - lihat status
- `/selesai` - akhiri service lebih awal
"""

async def generate_response(self, pesan_user: str, context: str = None) -> str:
    """
    Generate response untuk Pelacur dengan full service attitude.
    """
    from bot.prompt import get_prompt_builder
    from bot.ai_client import get_ai_client
    
    try:
        prompt_builder = get_prompt_builder()
        prompt = prompt_builder.build_role_prompt(self, pesan_user, context)
        
        ai_client = get_ai_client()
        response = await ai_client.generate_with_context(prompt, pesan_user)
        
        if not response:
            return self.get_greeting()
        
        return response
        
    except Exception as e:
        logger.error(f"Pelacur AI error: {e}")
        return self.get_greeting()


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_pelacur: Optional[PelacurRole] = None


def get_pelacur() -> PelacurRole:
    global _pelacur
    if _pelacur is None:
        _pelacur = PelacurRole()
    return _pelacur
