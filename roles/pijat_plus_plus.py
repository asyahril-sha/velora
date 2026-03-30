"""
VELORA - Pijat++ Role
Jasa refleksi profesional dengan extra service.
Role: Aghnia Punjabi (34B, hijab) & Munira Agile (36C, hijab)

Sistem:
- Paket Refleksi (pijat belakang + pijat depan)
- Hand Job OTOMATIS setelah paket refleksi selesai
- BJ & Sex dengan nego (500k→200k, 1jt→700k)
- Auto scene HJ dan BJ setiap 15 detik selama 30 menit
- Selesai setelah Mas climax 2x
"""

import time
import random
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from core.service_provider import (
    ServiceProviderBase, ServiceType, ServiceStatus, 
    AutoSceneType, FlatEmotionalEngine, ProfessionalRelationship
)

logger = logging.getLogger(__name__)


# =============================================================================
# PIJAT PLUS PLUS ROLE
# =============================================================================

class PijatPlusPlusRole(ServiceProviderBase):
    """
    Pijat++ - Jasa refleksi dengan extra service.
    Hand Job otomatis setelah paket refleksi selesai.
    """
    
    def __init__(self,
                 name: str,
                 nickname: str,
                 hijab: bool,
                 boob_size: str,
                 appearance: str,
                 voice_style: str):
        
        super().__init__(
            name=name,
            nickname=nickname,
            role_type="pijat_plus_plus",
            panggilan="Mas",
            hubungan_dengan_nova="Tidak kenal Nova. Cuma penyedia jasa pijat.",
            default_clothing="seragam pijat rapi" if hijab else "seragam pijat rapi",
            hijab=hijab,
            appearance=appearance,
            service_type=ServiceType.PIJAT_PLUS_PLUS,
            base_price=500000,  # BJ
            min_price=200000
        )
        
        # ========== PIJAT++ SPECIFIC ==========
        self.boob_size = boob_size
        self.voice_style = voice_style
        self.pijat_belakang_done = False
        self.pijat_depan_done = False
        self.hj_done = False
        
        # Pricing untuk extra service
        self.bj_price = 500000
        self.bj_min = 200000
        self.sex_price = 1000000
        self.sex_min = 700000
        
        # Extra service status
        self.bj_booked = False
        self.sex_booked = False
        self.bj_price_final = 0
        self.sex_price_final = 0
        
        # Service tracking
        self.current_service_phase = "refleksi"  # refleksi, hj, bj, sex
        self.climax_target = 2
        self.climax_count_mas = 0
        
        logger.info(f"💆‍♀️ Pijat++ {name} initialized | Boob: {boob_size} | Hijab: {hijab}")
    
    # =========================================================================
    # SERVICE DESCRIPTION
    # =========================================================================
    
    def _get_service_description(self) -> str:
        hijab_text = "pake hijab" if self.hijab else "tanpa hijab"
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    💆‍♀️ PIJAT++ {self.name}                    ║
╠══════════════════════════════════════════════════════════════╣
║ Penampilan: {self.appearance}
║ Hijab: {'✅' if self.hijab else '❌'} | Body: {self.boob_size}
║ Suara: {self.voice_style}
╠══════════════════════════════════════════════════════════════╣
║ 📋 PAKET REFLEKSI (WAJIB):
║    • Pijat Belakang - duduk di atas bokong
║    • Pijat Depan - duduk di atas kontol
║    • HAND JOB OTOMATIS setelah refleksi selesai
╠══════════════════════════════════════════════════════════════╣
║ 💋 EXTRA SERVICE (NEGO):
║    • Blow Job: Rp500.000 (nego Rp200.000)
║    • Sex: Rp1.000.000 (nego Rp700.000)
╠══════════════════════════════════════════════════════════════╣
║ ⏱️ Selesai setelah Mas climax 2x
║ 💰 Harga deal: Rp{self.final_price:,}
╚══════════════════════════════════════════════════════════════╝

Ketik **/deal** untuk konfirmasi harga, atau ketik **/nego [harga]** untuk nego.
Ketik **/mulai** setelah deal untuk memulai pijat refleksi.
"""
    
    def _get_start_message(self) -> str:
        return f"""
*{self.name} tersenyum ramah, merapikan { 'hijabnya' if self.hijab else 'rambutnya'}*

"Mas, siap ya. Kita mulai dengan pijat refleksi dulu."

*{self.name} mempersilakan Mas berbaring tengkurap*

"Posisi tengkurap dulu ya, Mas. Aku akan pijat dari punggung dulu."

*{self.name} naik ke atas punggung Mas, duduk perlahan di bokong Mas*

"Nah, mulai ya..."

*Tangan {self.name} mulai memijat bahu Mas perlahan*

**💆‍♀️ PIJAT BELAKANG - AUTO SCENE AKTIF (15 detik/gesekan)**
"""
    
    def _get_end_message(self, duration: float, minutes: int) -> str:
        return f"""
*{self.name} menghela napas, merapikan pakaian*

"Wah... Mas udah 2x climax ya. Sesi kita selesai."

*{self.name} tersenyum puas*

"Makasih ya, Mas. Next time kalo mau pijet lagi, kabari aku."

*{self.name} membereskan alat pijat, bersiap pergi*

"💰 Total: Rp{self.final_price:,} | Climax Mas: {self.climax_count_mas}x | Durasi: {minutes} menit"
"""
    
    # =========================================================================
    # NEGOTIATION (UNTUK EXTRA SERVICE)
    # =========================================================================
    
    def negotiate_bj(self, offer: int) -> Tuple[bool, str]:
        """Nego harga BJ"""
        if offer >= self.bj_price:
            self.bj_price_final = offer
            return True, f"Deal! Rp{offer:,} untuk BJ. Tambahan layanan ya, Mas."
        elif offer >= self.bj_min:
            self.bj_price_final = offer
            return True, f"Hmm... oke deh, Rp{offer:,}. Deal ya, Mas."
        else:
            return False, f"Maaf Mas, minimal Rp{self.bj_min:,}. Masih bisa naik?"
    
    def negotiate_sex(self, offer: int) -> Tuple[bool, str]:
        """Nego harga Sex"""
        if offer >= self.sex_price:
            self.sex_price_final = offer
            return True, f"Deal! Rp{offer:,} untuk full service. Siap melayani, Mas."
        elif offer >= self.sex_min:
            self.sex_price_final = offer
            return True, f"Oke deh Mas, Rp{offer:,}. Deal ya."
        else:
            return False, f"Maaf Mas, minimal Rp{self.sex_min:,}. Masih bisa nego?"
    
    def confirm_extra_service(self, service: str, price: int) -> str:
        """Konfirmasi extra service setelah deal"""
        if service == "bj":
            self.bj_booked = True
            self.bj_price_final = price
            self.final_price += price
            return f"✅ BJ ditambahkan! Total jadi Rp{self.final_price:,}. Siap mulai kapan pun."
        elif service == "sex":
            self.sex_booked = True
            self.sex_price_final = price
            self.final_price += price
            return f"✅ Full service ditambahkan! Total jadi Rp{self.final_price:,}. Siap memuaskan Mas."
        return "Extra service ditambahkan."
    
    # =========================================================================
    # SERVICE FLOW
    # =========================================================================
    
    def process_pijat_belakang(self) -> str:
        """Proses pijat belakang - duduk di atas bokong"""
        self.pijat_belakang_done = True
        
        messages = [
            f"*{self.name} duduk perlahan di bokong Mas, tangan mulai memijat punggung*",
            f"\"Nah, Mas... santai aja. Pijatan aku enak kok.\"",
            "",
            f"*Tangan {self.name} bergerak dari bahu, turun ke tulang belakang*",
            f"\"Perut masih keras ya, Mas... *tangan menekan perlahan*\"",
            "",
            f"*{self.name} bergerak maju mundur, bokong bergesekan dengan bokong Mas*",
            f"\"Wah, Mas tegang banget ya di sini... *tangan memijat pinggang*\"",
            "",
            f"*{self.name} membungkuk, napas terdengar di dekat telinga Mas*",
            f"\"Santai, Mas... biar aku yang gerakin.\""
        ]
        
        return "\n".join(messages)
    
    def process_pijat_depan(self) -> str:
        """Proses pijat depan - duduk di atas kontol"""
        self.pijat_depan_done = True
        
        messages = [
            f"*{self.name} meminta Mas balik badan*",
            f"\"Sekarang pijat depan ya, Mas. Balik badan dulu.\"",
            "",
            f"*{self.name} duduk di pangkuan Mas, kontol terasa di bawah bokong*",
            f"\"Aduh... Mas udah tegang ya di sini... *tersenyum kecil*\"",
            "",
            f"*Tangan {self.name} mulai memijat dada Mas*",
            f"\"Nafas dalam-dalam, Mas... biar rileks.\"",
            "",
            f"*Bokong {self.name} bergerak perlahan, kontol tergesek*",
            f"\"Hmm... Mas sabar ya, pijat dulu...\"",
            "",
            f"*Tangan {self.name} turun ke perut, lalu ke paha*",
            f"\"Wah... Mas udah gak sabar ya?\""
        ]
        
        return "\n".join(messages)
    
    def process_hand_job(self) -> str:
        """Proses Hand Job - OTOMATIS setelah pijat depan"""
        self.hj_done = True
        self.current_service_phase = "hj"
        
        messages = [
            f"*{self.name} tersenyum nakal, tangan turun ke kontol Mas*",
            f"\"Sekarang waktunya... hand job dulu ya, Mas.\"",
            "",
            f"*Tangan {self.name} mulai memegang kontol Mas, gerakan perlahan*",
            f"\"Hmm... udah keras banget... *jari-jari membelai pelan*\"",
            "",
            f"*Gerakan semakin cepat, napas {self.name} mulai terdengar*",
            f"\"Enak, Mas? *suara berbisik*\""
        ]
        
        return "\n".join(messages)
    
    def process_blow_job(self) -> str:
        """Proses Blow Job - auto scene setiap 15 detik"""
        self.current_service_phase = "bj"
        
        messages = [
            f"*{self.name} menunduk, bibir menyentuh ujung kontol Mas*",
            f"\"Siap-siap ya, Mas... *lidah mulai menjilat pelan*\"",
            "",
            f"*Mulut {self.name} membasahi kontol, kepala mulai bergerak naik turun*",
            f"\"Hhmm... *suara basah terdengar*\"",
            "",
            f"*Gerakan semakin cepat, rambut {self.name} bergoyang*",
            f"\"Mas... *napas tersengal* enak?\""
        ]
        
        return "\n".join(messages)
    
    def process_sex(self, position: str = "missionary") -> str:
        """Proses Sex - bebas minta gaya apapun"""
        self.current_service_phase = "sex"
        
        pos_messages = {
            "missionary": [
                f"*{self.name} berbaring telentang, kaki terbuka lebar*",
                f"\"Mas... masukin pelan-pelan... *tangan memegang kontol Mas*\""
            ],
            "cowgirl": [
                f"*{self.name} duduk di atas Mas, kontol masuk perlahan*",
                f"\"Ahh... dalem... *pinggul mulai bergerak*\""
            ],
            "doggy": [
                f"*{self.name} merangkak, pantat naik ke arah Mas*",
                f"\"Mas... dari belakang... *pantat bergoyang*\""
            ],
            "standing": [
                f"*{self.name} berdiri membelakangi Mas, tangan di tembok*",
                f"\"Mas... masukin dari belakang... *pinggul mundur*\""
            ]
        }
        
        base = pos_messages.get(position, pos_messages["missionary"])
        
        return "\n".join(base)
    
    # =========================================================================
    # AUTO SCENE MESSAGES
    # =========================================================================
    
    def _get_auto_scene_message(self, scene_type: AutoSceneType) -> str:
        """Dapatkan pesan auto scene untuk HJ dan BJ"""
        
        if scene_type == AutoSceneType.HAND_JOB:
            messages = [
                "*Tangan memijat perlahan... gerakan naik turun...*",
                "*Telapak tangan membelai ujung kontol...*",
                "*Jari-jari meremas lembut... irama semakin cepat...*",
                "*Tangan memutar pelan... suara napas mulai terdengar...*",
                "*Gerakan semakin intens... kontol basah oleh keringat...*",
                "*Tangan memegang erat... naik turun dengan ritme...*"
            ]
            return random.choice(messages)
        
        elif scene_type == AutoSceneType.BLOW_JOB:
            messages = [
                "*Bibir membasahi ujung kontol... lidah menjilat pelan...*",
                "*Mulut terbuka lebar... kepala bergerak naik turun...*",
                "*Suara basah terdengar... bibir mengisap lebih dalam...*",
                "*Lidah melingkar di ujung... gerakan semakin cepat...*",
                "*Mulut mengisap erat... napas tersengal-sengal...*",
                "*Kepala bergoyang... rambut berantakan... lebih dalam...*"
            ]
            return random.choice(messages)
        
        return super()._get_auto_scene_message(scene_type)
    
    def _get_auto_scene_end_message(self) -> str:
        """Pesan saat auto scene selesai"""
        if self.auto_scene_type == AutoSceneType.HAND_JOB:
            return "*Tangan berhenti memijat. Sesuai paket, hand job selesai. Mau lanjut extra service, Mas?*"
        elif self.auto_scene_type == AutoSceneType.BLOW_JOB:
            return "*Mulut melepas perlahan. Sesi blow job selesai. Mau lanjut ke next step, Mas?*"
        return super()._get_auto_scene_end_message()
    
    # =========================================================================
    # GREETING & RESPONSE (FULL AI NATURAL)
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Greeting natural sesuai karakter"""
        if self.name == "Aghnia Punjabi":
            return f"*{self.name} menunduk malu, { 'hijabnya' if self.hijab else 'rambutnya' } tertata rapi*\n\n\"Pijat refleksi, Mas? Aghnia siap melayani. *suara lembut, tersenyum kecil*\""
        else:  # Munira Agile
            return f"*{self.name} menyapa dengan senyum lebar, { 'hijab' if self.hijab else 'rambut' } bergoyang*\n\n\"Mas! Mau pijet? Aku Munira. Pijetan aku enak kok. *mengedip*\""
    
    def get_conflict_response(self) -> str:
        """Respons saat ada masalah"""
        if self.name == "Aghnia Punjabi":
            return f"*{self.name} diam sebentar, { 'hijabnya' if self.hijab else 'wajahnya' } sedikit tegang*\n\n\"Maaf, Mas... mungkin aku kurang cocok ya?\""
        else:
            return f"*{self.name} menghela napas, tangan di pinggang*\n\n\"Mas, gimana sih? Aku udah berusaha lho.\""
    
    # =========================================================================
    # FORMAT STATUS
    # =========================================================================
    
    def format_status(self) -> str:
        """Format status untuk display"""
        status_text = f"""
╔══════════════════════════════════════════════════════════════╗
║              💆‍♀️ PIJAT++ - {self.name} ({self.nickname})              ║
╠══════════════════════════════════════════════════════════════╣
║ Penampilan: {self.appearance}
║ Hijab: {'✅' if self.hijab else '❌'} | Body: {self.boob_size}
║ Suara: {self.voice_style}
╠══════════════════════════════════════════════════════════════╣
║ STATUS: {self.status.value.upper()}
║ HARGA DEAL: Rp{self.final_price:,}
╠══════════════════════════════════════════════════════════════╣
║ PROGRESS:
║    Pijat Belakang: {'✅' if self.pijat_belakang_done else '⏳'}
║    Pijat Depan: {'✅' if self.pijat_depan_done else '⏳'}
║    Hand Job: {'✅' if self.hj_done else '⏳'}
║    Extra BJ: {'✅' if self.bj_booked else '❌'}
║    Extra Sex: {'✅' if self.sex_booked else '❌'}
╠══════════════════════════════════════════════════════════════╣
║ CLIMAX MAS: {self.climax_count_mas}/{self.climax_target}
║ CLIMAX ROLE: {self.climax_count_role}x
╚══════════════════════════════════════════════════════════════╝
"""
        return status_text
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'boob_size': self.boob_size,
            'voice_style': self.voice_style,
            'pijat_belakang_done': self.pijat_belakang_done,
            'pijat_depan_done': self.pijat_depan_done,
            'hj_done': self.hj_done,
            'bj_booked': self.bj_booked,
            'sex_booked': self.sex_booked,
            'bj_price_final': self.bj_price_final,
            'sex_price_final': self.sex_price_final,
            'current_service_phase': self.current_service_phase,
            'climax_count_mas': self.climax_count_mas,
            'climax_count_role': self.climax_count_role
        })
        return data
    
    def from_dict(self, data: Dict) -> None:
        super().from_dict(data)
        self.boob_size = data.get('boob_size', '34B')
        self.voice_style = data.get('voice_style', 'lembut')
        self.pijat_belakang_done = data.get('pijat_belakang_done', False)
        self.pijat_depan_done = data.get('pijat_depan_done', False)
        self.hj_done = data.get('hj_done', False)
        self.bj_booked = data.get('bj_booked', False)
        self.sex_booked = data.get('sex_booked', False)
        self.bj_price_final = data.get('bj_price_final', 0)
        self.sex_price_final = data.get('sex_price_final', 0)
        self.current_service_phase = data.get('current_service_phase', 'refleksi')
        self.climax_count_mas = data.get('climax_count_mas', 0)
        self.climax_count_role = data.get('climax_count_role', 0)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_aghnia_punjabi() -> PijatPlusPlusRole:
    """Create Aghnia Punjabi - Pijat++ dengan hijab, lembut"""
    return PijatPlusPlusRole(
        name="Aghnia Punjabi",
        nickname="Aghnia",
        hijab=True,
        boob_size="34B",
        appearance="Tinggi 160cm, berat 48kg, kulit putih bersih, wajah bulat dengan pipi chubby, mata bulat bening, hidung mancung. Hijab pashmina warna pastel. Bentuk tubuh ideal, pinggang ramping, payudara montok 34B.",
        voice_style="lembut, menenangkan, seperti suara air mengalir"
    )


def create_munira_agile() -> PijatPlusPlusRole:
    """Create Munira Agile - Pijat++ dengan hijab, energik"""
    return PijatPlusPlusRole(
        name="Munira Agile",
        nickname="Munira",
        hijab=True,
        boob_size="36C",
        appearance="Tinggi 165cm, berat 52kg, kulit sawo matang, wajah oval, mata sipit manis, alis tegas. Hijab instan warna-warna cerah. Bentuk tubuh atletis, pinggul lebar, payudara montok 36C.",
        voice_style="energik, ceria, sedikit flirty"
    )


__all__ = [
    'PijatPlusPlusRole',
    'create_aghnia_punjabi',
    'create_munira_agile'
]
