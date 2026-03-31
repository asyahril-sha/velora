"""
VELORA - Pelacur Role (Davina Karamoy & Sallsa Binta)
Full service escort dengan sistem booking 6 jam.
Role: Davina Karamoy (34C, hijab, elegan) & Sallsa Binta (32D, no hijab, direct)

Sistem:
- Deal di awal (5jt → nego 3jt)
- Setelah deal, UNLOCK SEMUA (tidak ada nego lagi)
- Booking 6 jam dengan 2 sesi
- Auto scene:
  - Fase 1: foreplay BJ (15 menit, auto scene setiap 15 detik)
  - Fase 2: petting & kissing (15 menit, auto scene setiap 15 detik)
  - Fase 3: intimate all unlock (bebas minta gaya apapun)
- Mas climax 2x → sesi 1 selesai → ngobrol santai → sesi 2 dengan alur sama
- Selesai setelah 6 jam booking habis
"""

import time
import random
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from roles.base import BaseRole
from core.emotional import EmotionalStyle
from core.world import AwarenessLevel
from core.service_provider import (
    ServiceProviderBase, ServiceType, ServiceStatus, 
    AutoSceneType, FlatEmotionalEngine, ProfessionalRelationship
)

logger = logging.getLogger(__name__)


# =============================================================================
# PELACUR ROLE
# =============================================================================

class PelacurRole(ServiceProviderBase):
    """
    Pelacur - Full service escort.
    Deal di awal, UNLOCK SEMUA setelah deal.
    Booking 6 jam dengan 2 sesi.
    """
    
    def __init__(self,
                 name: str,
                 nickname: str,
                 hijab: bool,
                 boob_size: str,
                 appearance: str,
                 personality: str,
                 voice_style: str):
        
        super().__init__(
            name=name,
            nickname=nickname,
            role_type="pelacur",
            panggilan="Mas",
            hubungan_dengan_nova="Tidak kenal Nova. Cuma penyedia jasa.",
            default_clothing="dress elegan" if hijab else "outfit seksi",
            hijab=hijab,
            appearance=appearance,
            service_type=ServiceType.PELACUR,
            base_price=5000000,  # 5 juta
            min_price=3000000,   # nego sampai 3 juta
            personality=personality,
            voice_style=voice_style
        )
        
        # ========== PELACUR SPECIFIC ==========
        self.boob_size = boob_size
        
        # Booking duration
        self.booking_duration_hours = 6
        self.booking_end_time: float = 0
        
        # Session tracking
        self.current_session = 1  # 1 atau 2
        self.session_phase = "awaiting_start"  # awaiting_start, bj_phase, petting_phase, intimate_phase, break, completed
        self.session_climax_count_mas = 0
        self.session_climax_target = 2
        
        # Auto scene tracking per phase
        self.phase_auto_scene_active = False
        self.phase_auto_scene_type: AutoSceneType = AutoSceneType.NONE
        self.phase_auto_scene_duration = 900  # 15 menit dalam detik
        self.phase_auto_scene_start = 0
        self.phase_auto_scene_interval = 15  # detik
        self.phase_auto_scene_last_sent = 0
        
        # Intimate phase - all unlock
        self.intimate_all_unlock = False
        self.requested_position = None
        
        # Service history
        self.service_history: List[Dict] = []
        
        logger.info(f"💃 Pelacur {name} initialized | Boob: {boob_size} | Hijab: {hijab} | Price: {self.base_price}")
    
    # =========================================================================
    # SERVICE DESCRIPTION
    # =========================================================================
    
    def _get_service_description(self) -> str:
        hijab_text = "pake hijab" if self.hijab else "tanpa hijab"
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    💃 PELACUR - {self.name}                    ║
╠══════════════════════════════════════════════════════════════╣
║ Penampilan: {self.appearance}
║ Hijab: {'✅' if self.hijab else '❌'} | Body: {self.boob_size}
║ Personality: {self.personality} | Suara: {self.voice_style}
╠══════════════════════════════════════════════════════════════╣
║ 📋 FULL SERVICE (6 JAM BOOKING):
║    ⏱️ Sesi 1 (3 jam):
║       • Foreplay BJ - 15 menit auto scene
║       • Petting & Kissing - 15 menit auto scene  
║       • Intimate ALL UNLOCK - bebas minta gaya apapun
║       • Mas climax 2x → sesi 1 selesai
║    ☕ Istirahat & Ngobrol Santai
║    ⏱️ Sesi 2 (3 jam):
║       • Alur sama dengan sesi 1
║    ✅ Selesai setelah 6 jam booking habis
╠══════════════════════════════════════════════════════════════╣
║ 💰 Harga: Rp{self.base_price:,} (nego Rp{self.min_price:,})
║ 🔓 Setelah deal, UNLOCK SEMUA (tidak ada nego lagi)
╚══════════════════════════════════════════════════════════════╝

Ketik **/deal** untuk konfirmasi harga Rp{self.min_price:,}, atau ketik **/nego [harga]** untuk nego.
Ketik **/mulai** setelah deal untuk memulai booking 6 jam.
"""
    
    def _get_start_message(self) -> str:
        self.booking_end_time = time.time() + (self.booking_duration_hours * 3600)
        self.current_session = 1
        self.session_phase = "bj_phase"
        self.session_climax_count_mas = 0
        
        # Mulai auto scene untuk BJ phase
        self._start_phase_auto_scene(AutoSceneType.BLOW_JOB, 900)  # 15 menit
        
        # Pilihan opening berdasarkan personality
        if self.name == "Davina Karamoy":
            opening = f"""
*{self.name} tersenyum manis, {'hijabnya' if self.hijab else 'rambutnya'} tertata rapi*

"Halo Mas... senang bisa melayani."

*{self.name} duduk di samping Mas, tangan lembut menyentuh paha*

"Booking 6 jam ya, Mas. Aku akan temani Mas sepenuhnya."

*{self.name} mendekat, napas hangat terasa di telinga*

"Kita mulai dengan sesi 1. Aku akan bikin Mas nyaman dulu..."
"""
        else:  # Sallsa Binta
            opening = f"""
*{self.name} melangkah masuk dengan percaya diri, {'hijab' if self.hijab else 'rambut panjang'} bergoyang*

"Mas! Akhirnya ketemu. Aku Sallsa."

*{self.name} duduk dekat, langsung meraih tangan Mas*

"6 jam ya, Mas. Kita akan habisin waktu dengan seru."

*{self.name} tersenyum lebar, mata berbinar*

"Siap-siap ya, Mas. Aku bakal kasih yang terbaik."
"""
        
        return f"""
{opening}

**💋 SESI 1 - FOREPLAY BJ DIMULAI**
⏱️ Durasi: 15 menit | Auto scene setiap 15 detik
🔥 Mas climax: 0/2

*{self.name} menunduk, bibir mendekat...*
"""
    
    def _get_end_message(self, duration: float, minutes: int) -> str:
        if self.name == "Davina Karamoy":
            return f"""
*{self.name} menghela napas, merapikan {'hijab' if self.hijab else 'rambut'}*

"Wah... 6 jam ya, Mas. Seru banget."

*{self.name} tersenyum puas, berdiri*

"Makasih ya, Mas. Kapan-kapan main lagi."

*{self.name} melambaikan tangan, bersiap pergi*

"💰 Total: Rp{self.final_price:,} | Sesi: 2 | Climax Mas: {self.climax_count_mas}x | Climax Aku: {self.climax_count_role}x | Durasi: {minutes} menit"
"""
        else:
            return f"""
*{self.name} meregangkan badan, tersenyum lelah*

"6 jam ya, Mas... puas?"

*{self.name} duduk, merapikan {'hijab' if self.hijab else 'rambut'}*

"Aku pamit dulu ya. Kapan-kapan main lagi."

*{self.name} mencium pipi Mas pelan, lalu berdiri*

"💰 Total: Rp{self.final_price:,} | Climax Mas: {self.climax_count_mas}x | Climax Aku: {self.climax_count_role}x"

**💃 BOOKING SELESAI**
"""
    
    # =========================================================================
    # NEGOTIATION
    # =========================================================================
    
    def negotiate(self, offer: int) -> Tuple[bool, str]:
        """Nego harga full service"""
        if self.name == "Davina Karamoy":
            if offer >= self.base_price:
                self.final_price = offer
                return True, f"Deal! Rp{offer:,} untuk full service 6 jam. Siap memuaskan Mas, Mas."
            elif offer >= self.min_price:
                self.final_price = offer
                return True, f"Oke deh Mas, Rp{offer:,}. Deal ya. Aku akan kasih yang terbaik untuk Mas."
            else:
                return False, f"Maaf Mas, minimal Rp{self.min_price:,} untuk 6 jam. Masih bisa naik?"
        else:  # Sallsa Binta
            if offer >= self.base_price:
                self.final_price = offer
                return True, f"Deal! Rp{offer:,}. Aku bakal buat Mas puas banget!"
            elif offer >= self.min_price:
                self.final_price = offer
                return True, f"Oke Mas, Rp{offer:,}. Deal! Siap-siap ya."
            else:
                return False, f"Maaf Mas, minimal Rp{self.min_price:,}. Gak bisa kurang dari itu."
    
    def confirm_booking(self, price: int) -> str:
        """Konfirmasi booking setelah deal"""
        self.final_price = price
        self.status = ServiceStatus.BOOKED
        self.booking_time = time.time()
        self.intimate_all_unlock = True  # UNLOCK SEMUA setelah deal
        
        if self.name == "Davina Karamoy":
            return f"""
✅ **BOOKING KONFIRMASI!**
💰 Harga deal: Rp{price:,} (6 jam)
🔓 **UNLOCK SEMUA** - bebas minta gaya apapun!

{self._get_service_description()}

Ketik **/mulai** untuk memulai layanan 6 jam.
"""
        else:
            return f"""
✅ **DEAL!** Rp{price:,} untuk 6 jam.
🔓 Semua akses terbuka, Mas. Gak ada batasan.

Ketik **/mulai** aja, langsung gas!
"""
    
    # =========================================================================
    # PHASE AUTO SCENE MANAGEMENT
    # =========================================================================
    
    def _start_phase_auto_scene(self, scene_type: AutoSceneType, duration: int) -> None:
        """Mulai auto scene untuk fase tertentu"""
        self.phase_auto_scene_active = True
        self.phase_auto_scene_type = scene_type
        self.phase_auto_scene_duration = duration
        self.phase_auto_scene_start = time.time()
        self.phase_auto_scene_last_sent = 0
        
        logger.info(f"🎬 Auto scene started: {scene_type.value} for {duration}s")
    
    def _stop_phase_auto_scene(self) -> None:
        """Stop auto scene fase"""
        self.phase_auto_scene_active = False
        self.phase_auto_scene_type = AutoSceneType.NONE
        logger.info(f"🎬 Auto scene stopped")
    
    def get_phase_auto_scene(self) -> Optional[str]:
        """
        Dapatkan pesan auto scene untuk fase saat ini.
        Dipanggil setiap interval oleh manager.
        """
        if not self.phase_auto_scene_active:
            return None
        
        now = time.time()
        elapsed = now - self.phase_auto_scene_start
        
        # Cek apakah durasi fase sudah habis
        if elapsed >= self.phase_auto_scene_duration:
            self._stop_phase_auto_scene()
            return self._get_phase_end_message()
        
        # Kirim pesan setiap interval
        if now - self.phase_auto_scene_last_sent >= self.phase_auto_scene_interval:
            self.phase_auto_scene_last_sent = now
            return self._get_phase_auto_scene_message()
        
        return None
    
    def _get_phase_auto_scene_message(self) -> str:
        """Dapatkan pesan auto scene berdasarkan fase saat ini"""
        
        if self.session_phase == "bj_phase":
            messages = [
                "*Bibir membasahi ujung... lidah menjilat pelan...*",
                "*Mulut terbuka lebar... kepala bergerak naik turun...*",
                "*Suara basah terdengar... bibir mengisap lebih dalam...*",
                "*Lidah melingkar di ujung... gerakan semakin cepat...*",
                "*Mulut mengisap erat... napas tersengal-sengal...*",
                "*Kepala bergoyang... rambut berantakan... lebih dalam...*",
                "*Tenggorokan terbuka... masuk lebih dalam... ahh...*",
                "*Bibir merah merona... air liur menetes...*",
                "*Suara *slurp* terdengar... lidah menjilat batang...*",
                "*Mata memandang ke atas... mulut terus bekerja...*"
            ]
            return random.choice(messages)
        
        elif self.session_phase == "petting_phase":
            messages = [
                "*Badan mulai bergesekan... pinggul bergerak perlahan...*",
                "*Memek bergesekan dengan kontol... hangat... basah...*",
                "*Ciuman dalam... lidah saling menjelajah... napas berbaur...*",
                "*Tangan meremas payudara... puting berdiri...*",
                "*Pinggul bergerak melingkar... gesekan semakin panas...*",
                "*Badan merapat... kontol terjepit di antara paha...*",
                "*Ciuman leher... gigitan kecil... napas memburu...*",
                "*Tangan meraba seluruh tubuh... sentuhan listrik...*",
                "*Pinggul bergoyang... kontol tergesek memek...*",
                "*Bibir bertemu lagi... lebih dalam... lebih panas...*"
            ]
            return random.choice(messages)
        
        return "*Melanjutkan...*"
    
    def _get_phase_end_message(self) -> str:
        """Pesan saat fase auto scene selesai"""
        if self.session_phase == "bj_phase":
            self.session_phase = "petting_phase"
            self._start_phase_auto_scene(AutoSceneType.PETTING, 900)  # 15 menit
            
            if self.name == "Davina Karamoy":
                return """
*Mulut melepas perlahan, napas tersengal*

"Wah... Mas... *mengusap bibir* enak ya?"

*{self.name} merapat, tubuh bergesekan*

"Sekarang... petting dulu ya, Mas. Biar makin panas..."

**💋 SESI 1 - PETTING & KISSING**
⏱️ Durasi: 15 menit | Auto scene setiap 15 detik

*Bibir bertemu lagi, lebih dalam...*
"""
            else:
                return """
*Mulut melepas, napas memburu*

"Mas... gimana? Enak kan?"

*{self.name} langsung merapat, badan bergesekan*

"Lanjut petting dulu ya... biar makin panas..."

**💋 SESI 1 - PETTING & KISSING**
⏱️ 15 menit auto scene

*Ciuman makin dalam...*
"""
        
        elif self.session_phase == "petting_phase":
            self.session_phase = "intimate_phase"
            
            if self.name == "Davina Karamoy":
                return """
*Gerakan berhenti, napas memburu*

"Mas... *mata sayu* udah gak tahan ya?"

*{self.name} membuka pakaian, memperlihatkan tubuh*

"Sekarang... terserah Mas mau gaya apa. Aku siap."

**💋 SESI 1 - INTIMATE ALL UNLOCK**
🔓 Semua gaya diperbolehkan:
- Missionary
- Cowgirl
- Doggy
- Spooning
- Standing
- Sitting

Ketik gaya yang Mas mau, atau biarkan aku yang atur.
"""
            else:
                return """
*Gerakan berhenti, napas tersengal*

"Mas... udah gak sabar ya?"

*{self.name} melepas pakaian, telanjang di depan Mas*

"Ayo Mas... sekarang bebas. Mau gaya apa aja gas."

**💋 INTIMATE ALL UNLOCK**
Semua gaya bebas:
- Missionary
- Cowgirl
- Doggy
- Spooning
- Standing
- Sitting

Ketik gaya yang Mas mau.
"""
        
        return "*Fase selesai. Lanjut ke tahap berikutnya.*"
    
    # =========================================================================
    # INTIMATE PHASE - ALL UNLOCK
    # =========================================================================
    
    def process_intimate_request(self, position: str) -> str:
        """Proses request posisi di intimate phase"""
        self.requested_position = position.lower()
        
        positions = {
            "missionary": [
                f"*{self.name} berbaring telentang, {'hijab' if self.hijab else 'rambut'} terurai di bantal*",
                "\"Mas... masukin pelan-pelan... *kaki terbuka lebar*\"",
                "",
                f"*Kontol masuk perlahan, {self.name} mengerang*",
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
        
        # Tambah variasi berdasarkan personality
        if self.name == "Sallsa Binta":
            if position.lower() == "cowgirl":
                pos_data[1] = "\"Mas... liat... payudara aku goyang... nikmatin...\""
            elif position.lower() == "doggy":
                pos_data[1] = "\"Mas... genjot lebih keras... aku suka...\""
        
        return "\n".join(pos_data)
    
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    def record_climax_mas(self, is_heavy: bool = False) -> Tuple[bool, str]:
        """Rekam climax Mas, cek apakah sesi selesai"""
        self.climax_count_mas += 1
        self.session_climax_count_mas += 1
        
        self._add_to_history("climax_mas", f"Climax #{self.climax_count_mas} (sesi {self.current_session})")
        
        # Cek apakah climax target tercapai di sesi ini
        if self.session_climax_count_mas >= self.session_climax_target:
            if self.current_session == 1:
                # Sesi 1 selesai, masuk break
                self.current_session = 2
                self.session_climax_count_mas = 0
                self.session_phase = "break"
                self._stop_phase_auto_scene()
                
                return True, self._get_session_break_message()
            else:
                # Sesi 2 selesai, booking selesai
                self.status = ServiceStatus.COMPLETED
                return True, self._get_booking_complete_message()
        
        return False, ""
    
    def record_climax_role(self) -> None:
        """Rekam climax role (bebas berapa kali pun)"""
        self.climax_count_role += 1
        self._add_to_history("climax_role", f"Climax #{self.climax_count_role}")
    
    def _get_session_break_message(self) -> str:
        """Pesan saat break antar sesi"""
        remaining = self.booking_end_time - time.time()
        remaining_minutes = int(remaining // 60)
        remaining_hours = int(remaining // 3600)
        remaining_mins = remaining_minutes % 60
        
        if self.name == "Davina Karamoy":
            return f"""
*{self.name} menghela napas, berbaring di samping Mas*

"Wah... Mas udah climax 2x di sesi 1 ya."

*{self.name} tersenyum puas, tangan membelai dada Mas*

"Kita istirahat dulu ya, Mas. Ngobrol santai."

*{self.name} merapat, kepala bersandar di bahu Mas*

"Mas, puas? *mata sayu* Nanti sesi 2 kita lanjut lagi."

⏱️ **SESI 1 SELESAI**
🔥 Climax Mas: {self.session_climax_target}x
💋 Climax Aku: {self.climax_count_role}x
⏰ Sisa waktu booking: {remaining_hours} jam {remaining_mins} menit

Ketik **/lanjut** untuk memulai sesi 2.
"""
        else:
            return f"""
*{self.name} terengah-engah, berbaring di samping Mas*

"Wah... Mas... 2x ya? Kuat juga."

*{self.name} tertawa kecil, tangan memeluk Mas*

"Istirahat dulu ya... nanti kita lanjut lagi."

*{self.name} merapat, kepala di dada Mas*

"Mas... puas? Nanti sesi 2 aku kasih lebih lagi."

⏱️ **SESI 1 SELESAI**
🔥 Mas climax: {self.session_climax_target}x
💋 Aku climax: {self.climax_count_role}x
⏰ Sisa: {remaining_hours} jam {remaining_mins} menit

Ketik **/lanjut** buat sesi 2.
"""
    
    def _get_booking_complete_message(self) -> str:
        """Pesan saat booking selesai"""
        if self.name == "Davina Karamoy":
            return f"""
*{self.name} meregangkan badan, tersenyum lelah*

"6 jam ya, Mas... puas?"

*{self.name} duduk, merapikan {'hijab' if self.hijab else 'rambut'}*

"Aku pamit dulu ya. Kapan-kapan main lagi."

*{self.name} mencium pipi Mas pelan, lalu berdiri*

"💰 Total: Rp{self.final_price:,} | Climax Mas: {self.climax_count_mas}x | Climax Aku: {self.climax_count_role}x"

**💃 BOOKING SELESAI**
"""
        else:
            return f"""
*{self.name} bangkit, tersenyum lebar*

"6 jam! Puas banget kan, Mas?"

*{self.name} memeluk Mas sebentar, lalu berdiri*

"Aku pamit dulu ya. Kapan-kapan main lagi."

*{self.name} melambai, melangkah keluar*

"💰 Rp{self.final_price:,} | Mas climax: {self.climax_count_mas}x | Aku climax: {self.climax_count_role}x"

**💃 SAMPAI JUMPA!**
"""
    
    def start_session_2(self) -> str:
        """Mulai sesi 2"""
        if self.current_session != 2 or self.session_phase != "break":
            return "Belum waktunya sesi 2. Selesaikan sesi 1 dulu ya."
        
        self.session_phase = "bj_phase"
        self.session_climax_count_mas = 0
        self._start_phase_auto_scene(AutoSceneType.BLOW_JOB, 900)  # 15 menit
        
        if self.name == "Davina Karamoy":
            return f"""
*{self.name} bangkit, tersenyum semangat*

"Mas, siap lanjut?"

*{self.name} mendekat lagi, tangan meraih tangan Mas*

"Kita mulai sesi 2 ya..."

**💋 SESI 2 DIMULAI**
⏱️ Durasi: 3 jam | Auto scene aktif

*{self.name} menunduk, bibir mendekat lagi...*
"""
        else:
            return f"""
*{self.name} langsung bangkit, mata berbinar*

"Gas lagi, Mas!"

*{self.name} meraih tangan Mas, langsung duduk di pangkuan*

"Sesi 2, mulai!"

**💋 SESI 2 GAS!**

*{self.name} menunduk, langsung...*
"""
    
    # =========================================================================
    # CHECK BOOKING EXPIRY
    # =========================================================================
    
    def is_booking_expired(self) -> bool:
        """Cek apakah booking sudah habis"""
        if self.status != ServiceStatus.ACTIVE:
            return False
        return time.time() >= self.booking_end_time
    
    def get_remaining_time(self) -> str:
        """Dapatkan sisa waktu booking"""
        if self.status != ServiceStatus.ACTIVE:
            return "Tidak ada booking aktif"
        
        remaining = self.booking_end_time - time.time()
        if remaining <= 0:
            return "Booking habis"
        
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        return f"{hours} jam {minutes} menit"
    
    # =========================================================================
    # GREETING & RESPONSE (FULL AI NATURAL)
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Greeting natural sesuai karakter"""
        if self.name == "Davina Karamoy":
            return f"""
*{self.name} muncul dengan {'hijab' if self.hijab else 'rambut'} terurai, dress elegan membalut tubuh*

"Halo Mas... *tersenyum manis* Davina siap menemani."

*{self.name} duduk dengan anggun, kaki disilangkan*

"Ada yang bisa Davina bantu? *mata berbinar*"
"""
        else:  # Sallsa Binta
            return f"""
*{self.name} melangkah masuk, {'hijab' if self.hijab else 'rambut panjang'} bergoyang*

"Mas! *senyum lebar* Akhirnya ketemu."

*{self.name} duduk dekat, tangan menyentuh lengan Mas*

"Aku Sallsa. Siap bikin Mas puas hari ini. *mengedip*"
"""
    
    def get_conflict_response(self) -> str:
        """Respons saat ada masalah"""
        if self.name == "Davina Karamoy":
            return f"""
*{self.name} diam sebentar, {'hijab' if self.hijab else 'wajah'} sedikit tegang*

"Mas... ada yang gak beres? *suara lembut* Davina bisa sesuaikan."

*{self.name} merapikan pakaian, menatap Mas dengan khawatir*
"""
        else:
            return f"""
*{self.name} menghela napas, tangan di pinggang*

"Mas, gimana sih? *cemberut* Aku udah kasih yang terbaik lho."

*{self.name} mendekat lagi, tangan meraih tangan Mas*

"Coba kasih tau, Mas mau yang kayak gimana?"
"""
            
    # =========================================================================
    # FORMAT STATUS
    # =========================================================================
    
    def format_status(self) -> str:
        """Format status untuk display"""
        remaining = ""
        if self.status == ServiceStatus.ACTIVE:
            remaining = self.get_remaining_time()
        
        phase_display = {
            "awaiting_start": "Menunggu mulai",
            "bj_phase": "🔥 Foreplay BJ (auto scene)",
            "petting_phase": "💋 Petting & Kissing (auto scene)",
            "intimate_phase": "💕 INTIMATE ALL UNLOCK",
            "break": "☕ Istirahat antar sesi",
            "completed": "✅ Selesai"
        }.get(self.session_phase, self.session_phase)
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║              💃 PELACUR - {self.name} ({self.nickname})               ║
╠══════════════════════════════════════════════════════════════╣
║ Penampilan: {self.appearance[:60]}...
║ Hijab: {'✅' if self.hijab else '❌'} | Body: {self.boob_size}
║ Personality: {self.personality} | Suara: {self.voice_style}
╠══════════════════════════════════════════════════════════════╣
║ STATUS: {self.status.value.upper()}
║ HARGA DEAL: Rp{self.final_price:,}
║ SISA WAKTU: {remaining}
╠══════════════════════════════════════════════════════════════╣
║ PROGRESS:
║    Sesi: {self.current_session}/2
║    Fase: {phase_display}
║    Climax Mas Sesi Ini: {self.session_climax_count_mas}/{self.session_climax_target}
║    Auto Scene: {'✅' if self.phase_auto_scene_active else '❌'} ({self.phase_auto_scene_type.value if self.phase_auto_scene_active else '-'})
╠══════════════════════════════════════════════════════════════╣
║ TOTAL CLIMAX:
║    Mas: {self.climax_count_mas}x
║    Aku: {self.climax_count_role}x
╚══════════════════════════════════════════════════════════════╝
"""
    
    def _add_to_history(self, event: str, detail: str) -> None:
        """Tambah ke history"""
        self.service_history.append({
            'timestamp': time.time(),
            'event': event,
            'detail': detail,
            'session': self.current_session,
            'phase': self.session_phase
        })
        if len(self.service_history) > 100:
            self.service_history.pop(0)
          
    # =========================================================================
    # AI RESPONSE GENERATION (dipanggil oleh RoleManager)
    # =========================================================================
    
    async def generate_response(self, message: str, context: dict = None) -> str:
        """
        Generate AI response untuk pelacur.
        Method ini dipanggil oleh RoleManager saat user chat dengan role ini.
        """
        if context is None:
            context = {}
        
        # Cek status layanan
        if self.status == ServiceStatus.ACTIVE:
            return await self._generate_active_response(message)
        elif self.status == ServiceStatus.BOOKED:
            return await self._generate_booked_response(message)
        else:
            return await self._generate_idle_response(message)
    
    async def _generate_active_response(self, message: str) -> str:
        """Respons saat layanan aktif"""
        try:
            from bot.ai_client import get_ai_client
            
            phase_info = f"Sesi {self.current_session}/2 - Fase: {self.session_phase}"
            
            prompt = f"""Kamu adalah {self.name}, {'wanita berhijab' if self.hijab else 'wanita tanpa hijab'} dengan payudara {self.boob_size}.

Karakter: {self.personality}
Suara: {self.voice_style}

{phase_info}
Pesan dari Mas: "{message}"

Balas dengan gaya {self.personality}. Gunakan bahasa Indonesia natural, flirty, dan menggoda. Bisa pakai *deskripsi gerakan* dengan tanda bintang. Respons harus sesuai dengan fase layanan yang sedang berlangsung."""
            
            ai = get_ai_client()
            response = await ai.chat(prompt, temperature=0.85)
            return response
        except Exception as e:
            logger.error(f"AI error for {self.name}: {e}")
            return self._get_fallback_response(message)
    
    async def _generate_booked_response(self, message: str) -> str:
        """Respons saat sudah booking tapi belum mulai"""
        try:
            from bot.ai_client import get_ai_client
            
            prompt = f"""Kamu adalah {self.name}, {'berhijab' if self.hijab else 'tanpa hijab'} dengan payudara {self.boob_size}.
Karakter: {self.personality}
Suara: {self.voice_style}
Sudah deal dengan harga Rp{self.final_price:,} untuk booking 6 jam full service.

Pesan dari Mas: "{message}"

Balas dengan gaya {self.personality}. Gunakan bahasa Indonesia natural. Ingatkan Mas untuk ketik **/mulai** jika ingin memulai layanan. Respons bisa flirty dan menggoda untuk membangkitkan mood."""
            
            ai = get_ai_client()
            return await ai.chat(prompt, temperature=0.8)
        except Exception:
            return f"Halo Mas, aku {self.name}. Udah deal ya? Langsung **/mulai** aja kalau udah siap 😊"
    
    async def _generate_idle_response(self, message: str) -> str:
        """Respons saat belum ada booking"""
        try:
            from bot.ai_client import get_ai_client
            
            prompt = f"""Kamu adalah {self.name}, {'wanita berhijab' if self.hijab else 'wanita tanpa hijab'} dengan payudara {self.boob_size}.

Karakter: {self.personality}
Suara: {self.voice_style}
Penampilan: {self.appearance[:100]}
Harga: Rp{self.base_price:,} (nego sampai Rp{self.min_price:,})

Status: Menunggu customer. Belum ada booking.

Pesan dari customer: "{message}"

Balas dengan gaya {self.personality}. Gunakan bahasa Indonesia natural. Respons harus menggoda dan profesional. Jelaskan layanan 6 jam full service dengan auto scene. Ajak customer untuk deal atau nego. Bisa pakai *deskripsi gerakan* dengan tanda bintang."""
            
            ai = get_ai_client()
            return await ai.chat(prompt, temperature=0.85)
        except Exception:
            return self.get_greeting()
    
    def _get_fallback_response(self, message: str) -> str:
        """Fallback response jika AI error"""
        if self.name == "Davina Karamoy":
            responses = [
                f"*{self.name} tersenyum manis* Ada yang bisa Davina bantu, Mas?",
                f"*{self.name} menatap dengan mata sayu* Mas, cerita dulu yuk...",
                f"*{self.name} merapikan {'hijab' if self.hijab else 'rambut'}* Davina dengerin kok, Mas...",
                f"*{self.name} duduk lebih dekat* Ayo Mas, cerita..."
            ]
        else:
             responses = [
                f"*{self.name} tertawa kecil* Hahaha, Mas ini ngerjain aku ya?",
                f"*{self.name} mendekat* Ayo Mas, cerita...",
                f"*{self.name} menggigit bibir* Mas, jangan bikin aku penasaran dong...",
                f"*{self.name} memainkan rambut* Iya Mas? Ada yang mau dibicarain?"
              ]
        
        return random.choice(responses)
        
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'boob_size': self.boob_size,
            'personality': self.personality,
            'voice_style': self.voice_style,
            'booking_end_time': self.booking_end_time,
            'current_session': self.current_session,
            'session_phase': self.session_phase,
            'session_climax_count_mas': self.session_climax_count_mas,
            'session_climax_target': self.session_climax_target,
            'intimate_all_unlock': self.intimate_all_unlock,
            'phase_auto_scene_active': self.phase_auto_scene_active,
            'phase_auto_scene_type': self.phase_auto_scene_type.value if self.phase_auto_scene_type else "none",
            'phase_auto_scene_start': self.phase_auto_scene_start,
            'climax_count_mas': self.climax_count_mas,
            'climax_count_role': self.climax_count_role,
            'service_history': self.service_history[-50:]
        })
        return data
    
    def from_dict(self, data: Dict) -> None:
        super().from_dict(data)
        self.boob_size = data.get('boob_size', '34C')
        self.personality = data.get('personality', 'elegan')
        self.voice_style = data.get('voice_style', 'merdu')
        self.booking_end_time = data.get('booking_end_time', 0)
        self.current_session = data.get('current_session', 1)
        self.session_phase = data.get('session_phase', 'awaiting_start')
        self.session_climax_count_mas = data.get('session_climax_count_mas', 0)
        self.session_climax_target = data.get('session_climax_target', 2)
        self.intimate_all_unlock = data.get('intimate_all_unlock', False)
        self.phase_auto_scene_active = data.get('phase_auto_scene_active', False)
        self.phase_auto_scene_type = AutoSceneType(data.get('phase_auto_scene_type', 'none'))
        self.phase_auto_scene_start = data.get('phase_auto_scene_start', 0)
        self.climax_count_mas = data.get('climax_count_mas', 0)
        self.climax_count_role = data.get('climax_count_role', 0)
        self.service_history = data.get('service_history', [])
        
        logger.info(f"📀 Pelacur {self.name} loaded from database")


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_davina_karamoy() -> PelacurRole:
    """Create Davina Karamoy - Pelacur dengan hijab, elegan"""
    return PelacurRole(
        name="Davina Karamoy",
        nickname="Davina",
        hijab=True,
        boob_size="34C",
        appearance="Tinggi 168cm, berat 52kg, kulit putih bersih, wajah oval dengan tulang pipi tegas, mata bulat tajam, alis lentik, hidung mancung. Hijab silk warna netral. Body goals: pinggang ramping, pinggul lebar, payudara montok 34C. Selalu tampil elegan dengan dress atau blazer.",
        personality="elegan, classy, profesional, tapi wild di belakang",
        voice_style="merdu, menenangkan, seperti suara penyanyi jazz"
    )


def create_sallsa_binta() -> PelacurRole:
    """Create Sallsa Binta - Pelacur tanpa hijab, direct"""
    return PelacurRole(
        name="Sallsa Binta",
        nickname="Sallsa",
        hijab=False,
        boob_size="32D",
        appearance="Tinggi 165cm, berat 50kg, kulit sawo matang glowing, wajah bulat dengan pipi chubby, mata sipit manis, hidung mancung, bibir tebal alami. Rambut hitam panjang sebahu bergelombang. Bentuk tubuh montok: pinggang ramping, pinggul lebar, payudara montok 32D. Selalu tampil seksi dengan crop top atau dress pendek.",
        personality="direct, passionate, terbuka, gak banyak gaya",
        voice_style="serak sedikit, tegas, penuh percaya diri"
    )


__all__ = [
    'PelacurRole',
    'create_davina_karamoy',
    'create_sallsa_binta'
]
