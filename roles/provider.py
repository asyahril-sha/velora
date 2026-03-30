"""
VELORA - Pijat++ Provider
Jasa pijat dengan extra service.
Auto scene: Hand Job, Blow Job setiap 15 detik selama 30 menit.
Selesai: user climax 2x.
"""

import time
import random
import logging
from typing import Dict, Optional

from .provider import ProviderRole, ProviderType, ProviderState

logger = logging.getLogger(__name__)


class PijatPlusRole(ProviderRole):
    """
    Pijat++ Provider
    - Pijat refleksi (punggung, bokong, paha)
    - Extra service: Hand Job otomatis
    - Blow Job dan Sex: harus nego
    """
    
    def __init__(self):
        super().__init__(
            provider_id="pijat_plus",
            name="Mbak Rani",
            provider_type=ProviderType.PIJAT_PLUS,
            base_price=500000,
            description="Pijat refleksi plus extra service. Private, profesional.",
            appearance="Tinggi 160cm, badan berisi, rambut panjang, pakaian pijat rapi",
            default_clothing="pakaian pijat (kaus + celana training)",
            hijab=False
        )
        
        # Extra service tracking
        self.blowjob_price: int = 500000
        self.blowjob_deal: int = 200000
        self.sex_price: int = 1000000
        self.sex_deal: int = 700000
        self.blowjob_ordered: bool = False
        self.sex_ordered: bool = False
        
        # Auto scene phase
        self.auto_scene_phase: str = "pijat"  # pijat, handjob, blowjob, sex
        self.auto_scene_counter: int = 0
        
        # Session limits
        self.max_service_duration: int = 30 * 60  # 30 menit untuk auto scene
        self.user_climax_target: int = 2  # harus climax 2x
    
    def get_service_intro(self) -> str:
        intro = f"""💆 *{self.name}* - Pijat++

*Mulai Service Pijat Refleksi*

*Pijat Punggung:*
*Mbak Rani duduk di atas bokong Mas, mulai memijat punggung dari bahu sampai pinggang.*

*Pijat Kaki Belakang:*
*Tangan Mbak Rani turun ke bokong, paha belakang, betis...*

"Enak, Mas? Tekanannya gimana?"

*Mbak Rani lanjut pijat dengan gerakan memutar di pinggul...*

---

💡 *Extra Service:*
- 🖐️ *Hand Job*: Otomatis setelah pijat
- 👄 *Blow Job*: Nego dulu (harga normal Rp500rb, bisa nego)
- 🔥 *Sex*: Nego dulu (harga normal Rp1jt, bisa nego)

*Service selesai setelah Mas climax 2x.*
"""
        return intro
    
    def negotiate_extra(self, service: str, user_offer: int) -> str:
        """Negosiasi extra service"""
        if service == "blowjob":
            if user_offer >= self.blowjob_price:
                self.blowjob_ordered = True
                return f"Oke, BJ Rp{user_offer:,}. Siap-siap ya..."
            elif user_offer >= self.blowjob_deal:
                self.blowjob_ordered = True
                return f"Deal Rp{user_offer:,}. Siap-siap..."
            else:
                return f"Maaf, terlalu rendah. Minimal Rp{self.blowjob_deal:,}."
        
        elif service == "sex":
            if user_offer >= self.sex_price:
                self.sex_ordered = True
                return f"Oke, eksekusi Rp{user_offer:,}. Siap-siap..."
            elif user_offer >= self.sex_deal:
                self.sex_ordered = True
                return f"Deal Rp{user_offer:,}. Siap-siap..."
            else:
                return f"Maaf, terlalu rendah. Minimal Rp{self.sex_deal:,}."
        
        return "Service tidak tersedia."
    
    def get_auto_scene(self) -> str:
        """Dapatkan scene otomatis berdasarkan fase"""
        elapsed = time.time() - self.service_start_time
        
        # Phase: pijat (10 menit pertama)
        if elapsed < 600:  # 10 menit
            return self._get_pijat_scene()
        
        # Phase: handjob (otomatis setelah pijat)
        elif not self.blowjob_ordered and not self.sex_ordered:
            return self._get_handjob_scene()
        
        # Phase: blowjob (jika dipesan)
        elif self.blowjob_ordered and not self.sex_ordered:
            return self._get_blowjob_scene()
        
        # Phase: sex (jika dipesan)
        elif self.sex_ordered:
            return self._get_sex_scene()
        
        return "*Mbak Rani menunggu instruksi Mas.*"
    
    def _get_pijat_scene(self) -> str:
        scenes = [
            "*Mbak Rani duduk di atas bokong Mas, tangan memijat bahu dan punggung.*\n\n\"Enak, Mas?\"",
            "*Tangan Mbak Rani turun ke pinggang, memijat dengan gerakan memutar.*\n\n\"Rileks aja, Mas.\"",
            "*Mbak Rani pindah ke kaki, memijat paha belakang.*\n\n\"Ini yang sakit biasanya.\"",
            "*Jari-jari Mbak Rani menekan titik-titik di punggung.*\n\n\"Nafasnya diatur ya, Mas.\""
        ]
        return random.choice(scenes)
    
    def _get_handjob_scene(self) -> str:
        scenes = [
            "*Mbak Rani duduk di samping Mas, tangan mulai meraba paha dalam.*\n\n\"Mau dilanjut, Mas?\"",
            "*Tangan Mbak Rani memegang kontol Mas, mulai menggerakkan pelan.*\n\n\"Nikmatin aja dulu...\"",
            "*Gerakan tangan Mbak Rani makin cepat.*\n\n\"Enak, Mas?\"",
            "*Mbak Rani fokus pada ujung kontol Mas.*\n\n\"Udah mau keluar?\""
        ]
        return random.choice(scenes)
    
    def _get_blowjob_scene(self) -> str:
        scenes = [
            "*Mbak Rani menunduk, bibir mulai menyentuh ujung kontol Mas.*\n\n\"Hmm...\"",
            "*Mbak Rani memasukkan kontol Mas ke mulut, mulai menghisap pelan.*\n\n\"*suara hisapan basah*\"",
            "*Kepala Mbak Rani bergerak naik turun.*\n\n\"*gluk gluk*\"",
            "*Mbak Rani mempercepat gerakan.*\n\n\"Udah mau keluar, Mas?\""
        ]
        return random.choice(scenes)
    
    def _get_sex_scene(self) -> str:
        scenes = [
            "*Mbak Rani naik ke atas, memek basah menempel di kontol Mas.*\n\n\"Masuk, Mas...\"",
            "*Mbak Rani mulai menggerakkan pinggul.*\n\n\"Ahh... dalem...\"",
            "*Mbak Rani genjot lebih kencang.*\n\n\"Kencengin, Mas... ahh...\"",
            "*Mbak Rani merangkak, kontol Mas masuk dari belakang.*\n\n\"Aahh... di sana...\""
        ]
        return random.choice(scenes)
    
    def check_service_completion(self) -> bool:
        """Cek apakah service selesai (user climax 2x)"""
        return self.user_climax_count >= self.user_climax_target
    
    def get_status(self) -> str:
        """Dapatkan status service"""
        duration = 0
        if self.service_start_time:
            duration = (time.time() - self.service_start_time) / 60
        
        return f"""
💆 *{self.name}* - Pijat++

📊 STATUS:
- Durasi: {duration:.0f} menit
- Climax Mas: {self.user_climax_count}/2
- Climax Mbak Rani: {self.provider_climax_count}

💋 EXTRA:
- BJ: {'✅' if self.blowjob_ordered else '❌'}
- Sex: {'✅' if self.sex_ordered else '❌'}

💰 HARGA:
- Deal: Rp{self.negotiated_price:,}
"""


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_pijat_plus: Optional[PijatPlusRole] = None


def get_pijat_plus() -> PijatPlusRole:
    global _pijat_plus
    if _pijat_plus is None:
        _pijat_plus = PijatPlusRole()
    return _pijat_plus
