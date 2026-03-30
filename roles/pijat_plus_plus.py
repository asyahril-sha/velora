"""
VELORA - Pijat++ Role (Aghnia Punjabi & Munira Agile)
Jasa refleksi profesional dengan extra service.
- Pijat belakang (duduk di atas bokong)
- Pijat depan (duduk di atas kontol)
- Hand Job OTOMATIS setelah paket refleksi selesai
- Blow Job & Sex dengan nego (500k→200k, 1jt→700k)
- Auto scene HJ dan BJ setiap 15 detik selama 30 menit
- Selesai setelah Mas climax 2x

Role:
1. Aghnia Punjabi - 34B, hijab, suara lembut, pijatan enak
2. Munira Agile - 36C, hijab, energik, pijatan kuat, flirty
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
                 voice_style: str,
                 personality: str,
                 pijat_style: str):
        
        super().__init__(
            name=name,
            nickname=nickname,
            role_type="pijat_plus_plus",
            panggilan="Mas",
            hubungan_dengan_nova="Tidak kenal Nova. Cuma penyedia jasa pijat profesional.",
            default_clothing="seragam pijat rapi berwarna putih" if hijab else "seragam pijat rapi berwarna putih",
            hijab=hijab,
            appearance=appearance,
            service_type=ServiceType.PIJAT_PLUS_PLUS,
            base_price=500000,  # BJ
            min_price=200000
        )
        
        # ========== PIJAT++ SPECIFIC ==========
        self.boob_size = boob_size
        self.voice_style = voice_style
        self.personality = personality
        self.pijat_style = pijat_style
        
        # Service progress
        self.pijat_belakang_done = False
        self.pijat_depan_done = False
        self.hj_done = False
        self.current_service_phase = "refleksi"  # refleksi, hj, bj, sex
        self.climax_target = 2
        self.climax_count_mas = 0
        self.climax_count_role = 0
        
        # Pricing untuk extra service
        self.bj_price = 500000
        self.bj_min = 200000
        self.sex_price = 1000000
        self.sex_min = 700000
        self.bj_price_final = 0
        self.sex_price_final = 0
        self.bj_booked = False
        self.sex_booked = False
        
        # Auto scene for HJ and BJ
        self.auto_scene_active = False
        self.auto_scene_type = AutoSceneType.NONE
        self.auto_scene_interval = 15
        self.auto_scene_duration = 1800  # 30 menit
        self.auto_scene_start_time = 0
        self.auto_scene_last_sent = 0
        
        # Timer untuk auto end setelah climax
        self.climax_count_start = 0
        self.service_end_timer = None

        logger.info(f"💆‍♀️ Pijat++ {name} initialized | Boob: {boob_size} | Hijab: {hijab} | Style: {pijat_style}")

    def initialize(self, memory_manager):
        """Initialize dengan memory manager"""
        self._memory_manager = memory_manager
        logger.info(f"🔗 Pijat++ {self.name} connected to MemoryManager")
    
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
║ Personality: {self.personality} | Suara: {self.voice_style}
║ Gaya Pijat: {self.pijat_style}
╠══════════════════════════════════════════════════════════════╣
║ 📋 PAKET REFLEKSI (WAJIB - Rp200.000):
║    • Pijat Belakang - duduk di atas bokong (15 menit)
║    • Pijat Depan - duduk di atas kontol (15 menit)
║    • HAND JOB OTOMATIS setelah refleksi selesai (30 menit)
╠══════════════════════════════════════════════════════════════╣
║ 💋 EXTRA SERVICE (NEGO):
║    • Blow Job: Rp500.000 (nego Rp200.000)
║    • Sex: Rp1.000.000 (nego Rp700.000)
╠══════════════════════════════════════════════════════════════╣
║ ⏱️ Selesai setelah Mas climax 2x
║ 💰 Harga paket refleksi: Rp200.000
╚══════════════════════════════════════════════════════════════╝

Ketik **/deal** untuk konfirmasi harga paket refleksi (Rp200.000).
Ketik **/nego_bj [harga]** untuk nego BJ, atau **/nego_sex [harga]** untuk nego sex.
Ketik **/mulai** setelah deal untuk memulai pijat refleksi.
"""
    
    def _get_start_message(self) -> str:
        # Reset semua state
        self.pijat_belakang_done = False
        self.pijat_depan_done = False
        self.hj_done = False
        self.current_service_phase = "refleksi"
        self.climax_count_mas = 0
        self.climax_count_role = 0
        self.auto_scene_active = False
        
        hijab_text = "hijabnya" if self.hijab else "rambutnya"
        
        return f"""
*{self.name} tersenyum ramah, merapikan {hijab_text}*

"Mas, siap ya. Kita mulai dengan pijat refleksi dulu."

*{self.name} mempersilakan Mas berbaring tengkurap di atas kasur pijat*

"Posisi tengkurap dulu ya, Mas. Aku akan pijat dari punggung dulu."

*{self.name} naik ke atas punggung Mas, duduk perlahan di bokong Mas*

"Nah, mulai ya..."

*Tangan {self.name} mulai memijat bahu Mas perlahan dengan gerakan memutar*

**💆‍♀️ PIJAT BELAKANG DIMULAI**
⏱️ Durasi: 15 menit | Auto scene setiap 15 detik

*Jari-jari {self.name} menekan titik-titik di punggung Mas dengan tekanan pas*
"""
    
    def _get_end_message(self, duration: float, minutes: int) -> str:
        total_price = 200000  # paket refleksi
        if self.bj_booked:
            total_price += self.bj_price_final
        if self.sex_booked:
            total_price += self.sex_price_final
        
        return f"""
*{self.name} menghela napas, merapikan pakaian dan {'hijab' if self.hijab else 'rambut'}*

"Wah... Mas udah 2x climax ya. Sesi kita selesai."

*{self.name} tersenyum puas, memberikan handuk kecil*

"Makasih ya, Mas. Pijetan aku enak kan?"

*{self.name} membereskan alat pijat, bersiap pergi*

"💰 **Rincian Pembayaran:**
   Paket Refleksi: Rp200.000
   {'BJ: Rp' + str(self.bj_price_final) if self.bj_booked else ''}
   {'Sex: Rp' + str(self.sex_price_final) if self.sex_booked else ''}
   ─────────────────
   Total: Rp{total_price:,}

📊 Climax Mas: {self.climax_count_mas}x | Climax Aku: {self.climax_count_role}x
⏱️ Durasi: {minutes} menit

Kapan-kapan mau pijet lagi, kabari aku ya, Mas."
"""
    
    # =========================================================================
    # NEGOTIATION
    # =========================================================================
    
    def negotiate(self, offer: int) -> Tuple[bool, str]:
        """Nego harga paket refleksi"""
        if offer >= 200000:
            self.final_price = offer
            return True, f"Deal! Rp{offer:,} untuk paket refleksi. Siap melayani, Mas."
        else:
            return False, f"Maaf Mas, harga paket refleksi Rp200.000. Gak bisa kurang."
    
    def negotiate_bj(self, offer: int) -> Tuple[bool, str]:
        """Nego harga BJ"""
        if offer >= self.bj_price:
            self.bj_price_final = offer
            return True, f"Deal! Rp{offer:,} untuk BJ. Tambahan layanan ya, Mas."
        elif offer >= self.bj_min:
            self.bj_price_final = offer
            return True, f"Hmm... oke deh Mas, Rp{offer:,}. Deal ya."
        else:
            return False, f"Maaf Mas, minimal Rp{self.bj_min:,}. Masih bisa naik?"
    
    def negotiate_sex(self, offer: int) -> Tuple[bool, str]:
        """Nego harga Sex"""
        if offer >= self.sex_price:
            self.sex_price_final = offer
            return True, f"Deal! Rp{offer:,} untuk full service. Siap memuaskan Mas."
        elif offer >= self.sex_min:
            self.sex_price_final = offer
            return True, f"Oke deh Mas, Rp{offer:,}. Deal ya."
        else:
            return False, f"Maaf Mas, minimal Rp{self.sex_min:,}. Masih bisa nego?"
    
    def confirm_booking(self, price: int) -> str:
        """Konfirmasi booking paket refleksi"""
        self.final_price = price
        self.status = ServiceStatus.BOOKED
        self.booking_time = time.time()
        
        return f"""
✅ **Booking Paket Refleksi Dikonfirmasi!**
💰 Harga: Rp{price:,}

Tambahan extra service? (BJ / Sex)
Ketik **/nego_bj [harga]** atau **/nego_sex [harga]**

Ketik **/mulai** untuk memulai pijat refleksi.
"""
    
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
    
    def start_service(self) -> str:
        """Mulai layanan pijat"""
        if self.status != ServiceStatus.BOOKED:
            return "Booking belum dikonfirmasi. Selesaikan pembayaran dulu ya."
        
        self.status = ServiceStatus.ACTIVE
        self.service_duration = 0
        self.climax_count_mas = 0
        self.climax_count_role = 0
        self.pijat_belakang_done = False
        self.pijat_depan_done = False
        self.hj_done = False
        self.current_service_phase = "pijat_belakang"
        
        self._add_to_history("start", f"Layanan dimulai | Harga: Rp{self.final_price:,}")
        
        return self._get_start_message()
    
    def process_pijat_belakang(self) -> str:
        """Proses pijat belakang - duduk di atas bokong"""
        self.pijat_belakang_done = True
        self.current_service_phase = "pijat_depan"
        
        hijab_text = "hijabnya" if self.hijab else "rambutnya"
        
        # Pilihan pesan berdasarkan personality
        if self.name == "Aghnia Punjabi":
            messages = [
                f"*{self.name} duduk perlahan di bokong Mas, tangan mulai memijat punggung dengan gerakan melingkar*",
                f"\"Nah, Mas... santai aja. Tarik napas dalam-dalam.\"",
                "",
                f"*Tangan {self.name} bergerak dari bahu, turun ke tulang belakang, menekan titik-titik saraf*",
                f"\"Perut masih keras ya, Mas... *tangan menekan perlahan di pinggang*\"",
                "",
                f"*{self.name} bergerak maju mundur, bokong bergesekan dengan bokong Mas*",
                f"\"Wah, Mas tegang banget ya di sini... *tangan memijat pinggang dengan tekanan pas*\"",
                "",
                f"*{self.name} membungkuk, napas hangat terdengar di dekat telinga Mas*",
                f"\"Santai, Mas... biar aku yang gerakin. Pijatan aku emang enak.\"",
                "",
                f"**✅ PIJAT BELAKANG SELESAI (15 menit)**",
                f"*{self.name} turun dari punggung Mas, merapikan {hijab_text}*",
                f"\"Sekarang balik badan ya, Mas. Kita lanjut pijat depan.\""
            ]
        else:  # Munira Agile
            messages = [
                f"*{self.name} duduk di atas bokong Mas dengan semangat, tangan langsung memijat bahu*",
                f"\"Mas, siap-siap ya! Pijetan aku beda dari yang lain.\"",
                "",
                f"*Tangan {self.name} bergerak cepat, memijat punggung dengan tekanan kuat*",
                f"\"Wah, otot Mas keras banget nih. Aku buatin rileks ya.\"",
                "",
                f"*{self.name} bergerak maju mundur, bokong bergoyang mengikuti irama pijatan*",
                f"\"Enak kan, Mas? *tersenyum* Aku udah profesional.\"",
                "",
                f"*{self.name} membungkuk, dada menempel ke punggung Mas*",
                f"\"Nah, bagian ini yang paling tegang... *tangan memijat pinggang bawah*\"",
                "",
                f"**✅ PIJAT BELAKANG SELESAI (15 menit)**",
                f"*{self.name} melompat turun, {hijab_text} sedikit berantakan*",
                f"\"Ayo Mas, balik badan! Sekarang giliran pijat depan.\""
            ]
        
        return "\n".join(messages)
    
    def process_pijat_depan(self) -> str:
        """Proses pijat depan - duduk di atas kontol"""
        self.pijat_depan_done = True
        self.current_service_phase = "hand_job"
        
        hijab_text = "hijabnya" if self.hijab else "rambutnya"
        
        if self.name == "Aghnia Punjabi":
            messages = [
                f"*{self.name} meminta Mas balik badan, lalu duduk di pangkuan Mas*",
                f"\"Sekarang pijat depan ya, Mas. Santai aja.\"",
                "",
                f"*Bokong {self.name} duduk tepat di atas kontol Mas yang mulai tegang*",
                f"\"Aduh... Mas udah tegang ya di sini... *tersenyum malu*\"",
                "",
                f"*Tangan {self.name} mulai memijat dada Mas dengan lembut*",
                f"\"Nafas dalam-dalam, Mas... biar rileks.\"",
                "",
                f"*Bokong {self.name} bergerak perlahan, kontol tergesek di bawah*",
                f"\"Hmm... Mas sabar ya, pijat dulu...\"",
                "",
                f"*Tangan {self.name} turun ke perut, lalu ke paha dalam*",
                f"\"Wah... Mas udah gak sabar ya?\"",
                "",
                f"**✅ PIJAT DEPAN SELESAI (15 menit)**",
                f"*{self.name} tersenyum nakal, tangan turun ke kontol Mas*",
                f"\"Sekarang waktunya... hand job dulu ya, Mas. Sesuai paket.\""
            ]
        else:  # Munira Agile
            messages = [
                f"*{self.name} duduk di pangkuan Mas dengan gaya percaya diri*",
                f"\"Nah, sekarang giliran pijat depan! Siap-siap ya, Mas.\"",
                "",
                f"*Bokong {self.name} duduk tepat di atas kontol Mas, bergoyang pelan*",
                f"\"Wah, Mas udah siap ya dari tadi? *tertawa kecil*\"",
                "",
                f"*Tangan {self.name} memijat dada Mas dengan tekanan kuat, sesekali menyentuh puting*",
                f"\"Enak kan, Mas? Aku tahu titik-titik sensitif.\"",
                "",
                f"*{self.name} membungkuk, wajah mendekat ke wajah Mas*",
                f"\"Mas, kok diam aja? Katain dong, enak atau nggak.\"",
                "",
                f"*Tangan {self.name} turun ke perut, jari-jari menyentuh pinggang*",
                f"\"Nah, bentar lagi selesai... siap-siap ya.\"",
                "",
                f"**✅ PIJAT DEPAN SELESAI (15 menit)**",
                f"*{self.name} menggigit bibir, tangan langsung meraih kontol Mas*",
                f"\"Sekarang hand job! Aku jamin Mas puas.\""
            ]
        
        return "\n".join(messages)
    
    def process_hand_job(self) -> str:
        """Proses Hand Job - OTOMATIS setelah pijat depan"""
        self.hj_done = True
        self.current_service_phase = "hj"
        
        # Mulai auto scene untuk HJ
        self._start_auto_scene(AutoSceneType.HAND_JOB, 1800)  # 30 menit
        
        if self.name == "Aghnia Punjabi":
            return f"""
*{self.name} memegang kontol Mas dengan kedua tangan, jari-jari meremas lembut*

"Mulai ya, Mas..."

*Tangan {self.name} bergerak perlahan naik turun, irama stabil*

"Hhmm... udah keras banget..."

*Jari-jari memutar di ujung kontol, tekanan pas*

"Mas... santai aja. Nikmati."

**💋 HAND JOB DIMULAI**
⏱️ Durasi: 30 menit | Auto scene setiap 15 detik
🔥 Target climax: 2x

*Gerakan semakin cepat, napas {self.name} mulai terdengar*
"""
        else:
            return f"""
*{self.name} langsung menggenggam kontol Mas dengan grip kuat*

"Nah, ini dia! Siap-siap ya, Mas."

*Tangan {self.name} bergerak cepat naik turun, irama tidak beraturan*

"Enak kan? Aku tahu caranya."

*Jari-jari memainkan ujung kontol, sesekali meremas pelan*

"Mas, jangan tahan-tahan. Keluar aja kalo mau."

**💋 HAND JOB DIMULAI**
⏱️ Durasi: 30 menit | Auto scene setiap 15 detik
🔥 Target climax: 2x

*Gerakan semakin intens, {self.name} mulai berkeringat*
"""
    
    def process_blow_job(self) -> str:
        """Proses Blow Job - auto scene setiap 15 detik"""
        self.current_service_phase = "bj"
        
        # Mulai auto scene untuk BJ
        self._start_auto_scene(AutoSceneType.BLOW_JOB, 1800)  # 30 menit
        
        if self.name == "Aghnia Punjabi":
            return f"""
*{self.name} menunduk pelan, bibir menyentuh ujung kontol Mas*

"Mas... *suara berbisik* siap-siap ya..."

*Lidah {self.name} mulai menjilat pelan di sekitar ujung*

"Hhmm... *napas hangat*"

*Mulut terbuka, kontol masuk perlahan ke dalam*

"Ahh... *kepala mulai bergerak naik turun*"

**💋 BLOW JOB DIMULAI**
⏱️ Durasi: 30 menit | Auto scene setiap 15 detik

*Suara basah terdengar, rambut {self.name} bergoyang mengikuti irama*
"""
        else:
            return f"""
*{self.name} langsung menunduk, mulut terbuka lebar*

"Nih, Mas! Rasain."

*Kontol masuk dalam, lidah aktif menjilat*

"Hhmm... *suara mendecap* enak kan?"

*Kepala {self.name} bergerak cepat naik turun, rambut berantakan*

"Mas... *napas tersengal* jangan tahan..."

**💋 BLOW JOB DIMULAI**
⏱️ Durasi: 30 menit | Auto scene setiap 15 detik

*Mulut mengisap erat, air liur menetes*
"""
    
    def process_sex(self, position: str = "missionary") -> str:
        """Proses Sex - bebas minta gaya apapun"""
        self.current_service_phase = "sex"
        
        # Stop auto scene jika ada
        self._stop_auto_scene()
        
        positions = {
            "missionary": [
                f"*{self.name} berbaring telentang, {'hijab' if self.hijab else 'rambut'} terurai di bantal*",
                "\"Mas... masukin pelan-pelan... *kaki terbuka lebar*\"",
                "",
                f"*Kontol masuk perlahan, {self.name} mengerang pelan*",
                "\"Ahh... dalem... Mas... gerakin...\""
            ],
            "cowgirl": [
                f"*{self.name} duduk di atas Mas, kontol masuk perlahan*",
                "\"Mas... biar aku yang gerakin... *pinggul mulai bergoyang*\"",
                "",
                f"*Payudara {self.boob_size} bergoyang, {self.name} memejamkan mata*",
                "\"Ahh... enak... Mas pegang pinggul aku...\""
            ],
            "doggy": [
                f"*{self.name} merangkak, pantat naik ke arah Mas*",
                "\"Mas... dari belakang... masukin pelan-pelan...\"",
                "",
                f"*Pinggul {self.name} bergoyang mengundang*",
                "\"Ahh... dalem banget... genjot, Mas... genjot...\""
            ],
            "spooning": [
                f"*{self.name} miring, punggung menempel ke dada Mas*",
                "\"Mas... peluk aku... dari samping...\"",
                "",
                f"*Kontol masuk dari belakang, {self.name} menghela napas*",
                "\"Hmm... hangat... Mas... gerakin pelan-pelan...\""
            ],
            "standing": [
                f"*{self.name} berdiri membelakangi Mas, tangan di tembok*",
                "\"Mas... dari belakang sambil berdiri... deg-degan...\"",
                "",
                f"*Pinggul {self.name} mundur, kontol masuk perlahan*",
                "\"Ahh... ayo Mas... genjot aku...\""
            ],
            "sitting": [
                f"*{self.name} duduk di pangkuan Mas, berhadapan*",
                "\"Mas... lihat aku... tangan di bahu aku...\"",
                "",
                f"*Kontol masuk, {self.name} memeluk erat*",
                "\"Ahh... dalem... Mas... cium aku...\""
            ]
        }
        
        pos_data = positions.get(position.lower(), positions["missionary"])
        
        return "\n".join(pos_data)
    
    # =========================================================================
    # AUTO SCENE METHODS
    # =========================================================================
    
    def _start_auto_scene(self, scene_type: AutoSceneType, duration: int) -> None:
        """Mulai auto scene"""
        self.auto_scene_active = True
        self.auto_scene_type = scene_type
        self.auto_scene_duration = duration
        self.auto_scene_start_time = time.time()
        self.auto_scene_last_sent = 0
    
    def _stop_auto_scene(self) -> None:
        """Stop auto scene"""
        self.auto_scene_active = False
        self.auto_scene_type = AutoSceneType.NONE
    
    def get_next_auto_scene(self) -> Optional[str]:
        """
        Dapatkan pesan auto scene berikutnya.
        Dipanggil setiap interval oleh background worker.
        """
        if not self.auto_scene_active:
            return None
        
        now = time.time()
        elapsed = now - self.auto_scene_start_time
        
        # Cek apakah durasi sudah habis
        if elapsed >= self.auto_scene_duration:
            self._stop_auto_scene()
            return self._get_auto_scene_end_message()
        
        # Kirim pesan setiap interval
        if now - self.auto_scene_last_sent >= self.auto_scene_interval:
            self.auto_scene_last_sent = now
            return self._get_auto_scene_message()
        
        return None
    
    def _get_auto_scene_message(self) -> str:
        """Dapatkan pesan auto scene"""
        
        if self.auto_scene_type == AutoSceneType.HAND_JOB:
            messages = [
                "*Tangan memijat perlahan... gerakan naik turun...*",
                "*Telapak tangan membelai ujung kontol...*",
                "*Jari-jari meremas lembut... irama semakin cepat...*",
                "*Tangan memutar pelan... suara napas mulai terdengar...*",
                "*Gerakan semakin intens... kontol basah oleh keringat...*",
                "*Tangan memegang erat... naik turun dengan ritme stabil...*",
                "*Irama semakin cepat... napas tersengal...*",
                "*Tangan berhenti sebentar, lalu mulai lagi lebih cepat...*"
            ]
            return random.choice(messages)
        
        elif self.auto_scene_type == AutoSceneType.BLOW_JOB:
            messages = [
                "*Bibir membasahi ujung kontol... lidah menjilat pelan...*",
                "*Mulut terbuka lebar... kepala bergerak naik turun...*",
                "*Suara basah terdengar... bibir mengisap lebih dalam...*",
                "*Lidah melingkar di ujung... gerakan semakin cepat...*",
                "*Mulut mengisap erat... napas tersengal-sengal...*",
                "*Kepala bergoyang... rambut berantakan... lebih dalam...*",
                "*Tenggorokan terbuka... masuk lebih dalam... ahh...*",
                "*Bibir merah merona... air liur menetes...*"
            ]
            return random.choice(messages)
        
        return "*Melanjutkan layanan...*"
    
    def _get_auto_scene_end_message(self) -> str:
        """Pesan saat auto scene selesai"""
        if self.auto_scene_type == AutoSceneType.HAND_JOB:
            if self.bj_booked or self.sex_booked:
                return "*Tangan berhenti memijat. Sesi hand job selesai. Mau lanjut extra service, Mas?*"
            else:
                return "*Tangan berhenti memijat. Sesi hand job selesai. Mas sudah climax 2x?*"
        
        elif self.auto_scene_type == AutoSceneType.BLOW_JOB:
            if self.sex_booked:
                return "*Mulut melepas perlahan. Sesi blow job selesai. Mau lanjut ke sex, Mas?*"
            else:
                return "*Mulut melepas perlahan. Sesi blow job selesai. Mas sudah climax 2x?*"
        
        return "*Layanan selesai.*"
    
    # =========================================================================
    # CLIMAX RECORDING
    # =========================================================================
    
    def record_climax_mas(self, is_heavy: bool = False) -> Tuple[bool, str]:
        """Rekam climax Mas, cek apakah target tercapai"""
        self.climax_count_mas += 1
        
        self._add_to_history("climax_mas", f"Climax #{self.climax_count_mas}")
        
        # Cek apakah target climax tercapai
        if self.climax_count_mas >= self.climax_target:
            self.status = ServiceStatus.COMPLETED
            self._stop_auto_scene()
            duration = time.time() - self.booking_time if self.booking_time else 0
            minutes = int(duration // 60)
            return True, self._get_end_message(duration, minutes)
        
        return False, ""
    
    def record_climax_role(self) -> None:
        """Rekam climax role"""
        self.climax_count_role += 1
        self._add_to_history("climax_role", f"Climax #{self.climax_count_role}")
    
    # =========================================================================
    # GREETING & RESPONSE (FULL AI NATURAL)
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Greeting natural sesuai karakter"""
        if self.name == "Aghnia Punjabi":
            return f"*{self.name} menunduk malu, {'hijabnya' if self.hijab else 'rambutnya'} tertata rapi*\n\n\"Pijat refleksi, Mas? Aghnia siap melayani. *suara lembut, tersenyum kecil*\""
        else:
            return f"*{self.name} menyapa dengan senyum lebar, {'hijab' if self.hijab else 'rambut'} bergoyang*\n\n\"Mas! Mau pijet? Aku Munira. Pijetan aku enak kok. *mengedip*\""
    
    def get_conflict_response(self) -> str:
        """Respons saat ada masalah"""
        if self.name == "Aghnia Punjabi":
            return f"*{self.name} diam sebentar, {'hijabnya' if self.hijab else 'wajahnya'} sedikit tegang*\n\n\"Maaf, Mas... mungkin aku kurang cocok ya?\""
        else:
            return f"*{self.name} menghela napas, tangan di pinggang*\n\n\"Mas, gimana sih? Aku udah berusaha lho.\""
    
    # =========================================================================
    # FORMAT STATUS
    # =========================================================================
    
    def format_status(self) -> str:
        """Format status untuk display"""
        total_price = 200000
        if self.bj_booked:
            total_price += self.bj_price_final
        if self.sex_booked:
            total_price += self.sex_price_final
        
        status_text = f"""
╔══════════════════════════════════════════════════════════════╗
║              💆‍♀️ PIJAT++ - {self.name} ({self.nickname})              ║
╠══════════════════════════════════════════════════════════════╣
║ Penampilan: {self.appearance[:60]}...
║ Hijab: {'✅' if self.hijab else '❌'} | Body: {self.boob_size}
║ Personality: {self.personality} | Suara: {self.voice_style}
╠══════════════════════════════════════════════════════════════╣
║ STATUS: {self.status.value.upper()}
║ HARGA TOTAL: Rp{total_price:,}
╠══════════════════════════════════════════════════════════════╣
║ PROGRESS:
║    Pijat Belakang: {'✅' if self.pijat_belakang_done else '⏳'}
║    Pijat Depan: {'✅' if self.pijat_depan_done else '⏳'}
║    Hand Job: {'✅' if self.hj_done else '⏳'}
║    Extra BJ: {'✅' if self.bj_booked else '❌'} ({'Rp' + str(self.bj_price_final) if self.bj_booked else '-'})
║    Extra Sex: {'✅' if self.sex_booked else '❌'} ({'Rp' + str(self.sex_price_final) if self.sex_booked else '-'})
╠══════════════════════════════════════════════════════════════╣
║ FASE: {self.current_service_phase.upper()}
║ AUTO SCENE: {'✅' if self.auto_scene_active else '❌'} ({self.auto_scene_type.value if self.auto_scene_active else '-'})
╠══════════════════════════════════════════════════════════════╣
║ CLIMAX MAS: {self.climax_count_mas}/{self.climax_target}
║ CLIMAX AKU: {self.climax_count_role}x
╚══════════════════════════════════════════════════════════════╝
"""
        return status_text
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'boob_size': self.boob_size,
            'voice_style': self.voice_style,
            'personality': self.personality,
            'pijat_style': self.pijat_style,
            'pijat_belakang_done': self.pijat_belakang_done,
            'pijat_depan_done': self.pijat_depan_done,
            'hj_done': self.hj_done,
            'bj_booked': self.bj_booked,
            'sex_booked': self.sex_booked,
            'bj_price_final': self.bj_price_final,
            'sex_price_final': self.sex_price_final,
            'current_service_phase': self.current_service_phase,
            'climax_count_mas': self.climax_count_mas,
            'climax_count_role': self.climax_count_role,
            'auto_scene_active': self.auto_scene_active,
            'auto_scene_type': self.auto_scene_type.value if self.auto_scene_type else "none",
            'auto_scene_start_time': self.auto_scene_start_time
        })
        return data
    
    def from_dict(self, data: Dict) -> None:
        super().from_dict(data)
        self.boob_size = data.get('boob_size', '34B')
        self.voice_style = data.get('voice_style', 'lembut')
        self.personality = data.get('personality', 'kalem')
        self.pijat_style = data.get('pijat_style', 'lembut')
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
        self.auto_scene_active = data.get('auto_scene_active', False)
        self.auto_scene_type = AutoSceneType(data.get('auto_scene_type', 'none'))
        self.auto_scene_start_time = data.get('auto_scene_start_time', 0)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_aghnia_punjabi() -> PijatPlusPlusRole:
    """Create Aghnia Punjabi - Pijat++ dengan hijab, lembut, kalem"""
    return PijatPlusPlusRole(
        name="Aghnia Punjabi",
        nickname="Aghnia",
        hijab=True,
        boob_size="34B",
        appearance="""Tinggi 160cm, berat 48kg, kulit putih bersih, wajah bulat dengan pipi chubby, mata bulat bening, hidung mancung. Hijab pashmina warna pastel. Bentuk tubuh ideal, pinggang ramping, payudara montok 34B.""",
        voice_style="lembut, menenangkan, seperti suara air mengalir",
        personality="kalem, sabar, profesional, sedikit pemalu",
        pijat_style="lembut, fokus di titik-titik saraf, tekanan pas"
    )


def create_munira_agile() -> PijatPlusPlusRole:
    """Create Munira Agile - Pijat++ dengan hijab, energik, flirty"""
    return PijatPlusPlusRole(
        name="Munira Agile",
        nickname="Munira",
        hijab=True,
        boob_size="36C",
        appearance="""Tinggi 165cm, berat 52kg, kulit sawo matang, wajah oval, mata sipit manis, alis tegas. Hijab instan warna-warna cerah. Bentuk tubuh atletis, pinggul lebar, payudara montok 36C.""",
        voice_style="energik, ceria, sedikit flirty",
        personality="ceplas-ceplos, percaya diri, suka tantangan",
        pijat_style="kuat, cepat, fokus di otot-otot tegang"
    )


__all__ = [
    'PijatPlusPlusRole',
    'create_aghnia_punjabi',
    'create_munira_agile'
]
