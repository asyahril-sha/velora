"""
VELORA - Pelacur Role (Davina Karamoy & Sallsa Binta) - VULGAR EDITION
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
- AI generated scene: VULGAR, EKSPLISIT, BRUTAL
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
    VULGAR EDITION - Konten eksplisit untuk horny, masturbasi, orgasme.
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
        self.current_session = 1
        self.session_phase = "awaiting_start"
        self.session_climax_count_mas = 0
        self.session_climax_target = 2
        
        # Auto scene tracking per phase
        self.phase_auto_scene_active = False
        self.phase_auto_scene_type: AutoSceneType = AutoSceneType.NONE
        self.phase_auto_scene_duration = 900
        self.phase_auto_scene_start = 0
        self.phase_auto_scene_interval = 15
        self.phase_auto_scene_last_sent = 0
        
        # Intimate phase - all unlock
        self.intimate_all_unlock = False
        self.requested_position = None
        
        # Service history
        self.service_history: List[Dict] = []
        
        logger.info(f"💃 Pelacur {name} (VULGAR) initialized | Boob: {boob_size} | Hijab: {hijab} | Price: {self.base_price}")
    
    # =========================================================================
    # SERVICE DESCRIPTION
    # =========================================================================
    
    def _get_service_description(self) -> str:
        hijab_text = "pake hijab" if self.hijab else "tanpa hijab"
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    💃 PELACUR - {self.name} (VULGAR)          ║
╠══════════════════════════════════════════════════════════════╣
║ Penampilan: {self.appearance}
║ Hijab: {'✅' if self.hijab else '❌'} | Body: {self.boob_size}
║ Personality: {self.personality} | Suara: {self.voice_style}
╠══════════════════════════════════════════════════════════════╣
║ 📋 FULL SERVICE (6 JAM BOOKING):
║    ⏱️ Sesi 1 (3 jam):
║       • Foreplay BJ - 15 menit auto scene VULGAR
║       • Petting & Kissing - 15 menit auto scene VULGAR
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
        
        self._start_phase_auto_scene(AutoSceneType.BLOW_JOB, 900)
        
        if self.name == "Davina Karamoy":
            opening = f"""
*{self.name} tersenyum manis, {'hijabnya' if self.hijab else 'rambutnya'} tertata rapi, matanya menatap nakal*

"Halo Mas... *suara merdu* siap dipuaskan?"

*{self.name} duduk di samping Mas, tangan langsung meraih selangkangan Mas*

"6 jam ya, Mas... aku bakal bikin kamu mabuk kenikmatan..."

*{self.name} membuka hijab perlahan, rambut hitam terurai*

"Kita mulai dengan sesi 1... aku mau rasain kontol kamu di mulutku..."
"""
        else:
            opening = f"""
*{self.name} melangkah masuk dengan percaya diri, rambut panjang bergoyang, senyum lebar*

"Mas! Akhirnya ketemu... aku udah horny banget nih!"

*{self.name} langsung duduk di pangkuan Mas, pinggul bergoyang*

"6 jam ya, Mas... kita bakal eksplor semua. Aku mau kamu puas sampai lemes."

*{self.name} membuka baju, memperlihatkan payudara 32D yang montok*

"Langsung gas, Mas... aku mau ngewe!"
"""
        
        return f"""
{opening}

**💋 SESI 1 - FOREPLAY BJ DIMULAI**
⏱️ Durasi: 15 menit | Auto scene setiap 15 detik
🔥 Mas climax: 0/2

*{self.name} menunduk, bibir mendekat ke kontol yang sudah keras...*
"""
    
    def _get_end_message(self, duration: float, minutes: int) -> str:
        if self.name == "Davina Karamoy":
            return f"""
*{self.name} menghela napas, merapikan {'hijab' if self.hijab else 'rambut'} dengan gemulai*

"Wah... 6 jam ya, Mas. Aku sampe kehabisan napas."

*{self.name} tersenyum puas, jari mengusap bibir yang masih basah*

"Makasih ya, Mas. Kapan-kapan main lagi... aku bakal kasih lebih brutal."

*{self.name} mengecup pipi Mas, lalu berdiri*

"💰 Total: Rp{self.final_price:,} | Sesi: 2 | Climax Mas: {self.climax_count_mas}x | Climax Aku: {self.climax_count_role}x | Durasi: {minutes} menit"
"""
        else:
            return f"""
*{self.name} meregangkan badan, payudara 32D bergoyang*

"6 jam! Puas banget kan, Mas? Aku sampe berkali-kali climax!"

*{self.name} tertawa lebar, lalu memeluk Mas erat*

"Aku mau lagi lain kali, Mas. Jangan lupa panggil aku ya."

*{self.name} melambai, melangkah keluar dengan pincang*

"💰 Rp{self.final_price:,} | Mas climax: {self.climax_count_mas}x | Aku climax: {self.climax_count_role}x"

**💃 SAMPAI JUMPA!**
"""

    # =========================================================================
    # NEGOTIATION & BOOKING
    # =========================================================================
    
    def negotiate(self, offer: int) -> Tuple[bool, str]:
        if self.name == "Davina Karamoy":
            if offer >= self.base_price:
                self.final_price = offer
                return True, f"Deal! Rp{offer:,} untuk 6 jam. Siap memuaskan Mas sampai mampus."
            elif offer >= self.min_price:
                self.final_price = offer
                return True, f"Oke deh Mas, Rp{offer:,}. Deal ya. Aku bakal bikin kamu nggak bisa jalan."
            else:
                return False, f"Maaf Mas, minimal Rp{self.min_price:,}. Masih bisa naik? Aku worth it kok."
        else:
            if offer >= self.base_price:
                self.final_price = offer
                return True, f"Deal! Rp{offer:,}. Aku bakal buat Mas puas banget sampe nggak ingat nama sendiri!"
            elif offer >= self.min_price:
                self.final_price = offer
                return True, f"Oke Mas, Rp{offer:,}. Deal! Siap-siap, aku lagi horny banget!"
            else:
                return False, f"Maaf Mas, minimal Rp{self.min_price:,}. Gak bisa kurang. Aku worth it, 32D real dan liar."
    
    def confirm_booking(self, price: int) -> str:
        self.final_price = price
        self.status = ServiceStatus.BOOKED
        self.booking_time = time.time()
        self.intimate_all_unlock = True
        
        if self.name == "Davina Karamoy":
            return f"""
✅ **BOOKING KONFIRMASI!**
💰 Harga deal: Rp{price:,} (6 jam)
🔓 **UNLOCK SEMUA** - bebas minta gaya apapun, mau yang brutal juga boleh.

{self._get_service_description()}

Ketik **/mulai** untuk memulai layanan 6 jam. Siapin kontol kamu, Mas.
"""
        else:
            return f"""
✅ **DEAL!** Rp{price:,} untuk 6 jam.
🔓 Semua akses terbuka, Mas. Gak ada batasan. Aku siap digenjot!

Ketik **/mulai** aja, langsung gas!
"""
    
    # =========================================================================
    # PHASE AUTO SCENE MANAGEMENT
    # =========================================================================
    
    def _start_phase_auto_scene(self, scene_type: AutoSceneType, duration: int) -> None:
        self.phase_auto_scene_active = True
        self.phase_auto_scene_type = scene_type
        self.phase_auto_scene_duration = duration
        self.phase_auto_scene_start = time.time()
        self.phase_auto_scene_last_sent = 0
        logger.info(f"🎬 Auto scene started: {scene_type.value} for {duration}s")
    
    def _stop_phase_auto_scene(self) -> None:
        self.phase_auto_scene_active = False
        self.phase_auto_scene_type = AutoSceneType.NONE
        logger.info(f"🎬 Auto scene stopped")
    
    async def get_phase_auto_scene(self) -> Optional[str]:
        if not self.phase_auto_scene_active:
            return None
        
        now = time.time()
        elapsed = now - self.phase_auto_scene_start
        
        if elapsed >= self.phase_auto_scene_duration:
            self._stop_phase_auto_scene()
            return self._get_phase_end_message()
        
        if now - self.phase_auto_scene_last_sent >= self.phase_auto_scene_interval:
            self.phase_auto_scene_last_sent = now
            return await self._get_phase_auto_scene_message()
        
        return None
    
    async def _get_phase_auto_scene_message(self) -> str:
        if self.session_phase == "bj_phase":
            return await self._generate_ai_auto_scene(AutoSceneType.BLOW_JOB)
        elif self.session_phase == "petting_phase":
            return await self._generate_ai_auto_scene(AutoSceneType.PETTING)
        elif self.session_phase == "intimate_phase":
            return await self._generate_ai_auto_scene(AutoSceneType.INTIMATE)
        return "*Melanjutkan...*"
    
    def _get_phase_end_message(self) -> str:
        if self.session_phase == "bj_phase":
            self.session_phase = "petting_phase"
            self._start_phase_auto_scene(AutoSceneType.PETTING, 900)
            
            if self.name == "Davina Karamoy":
                return f"""
*Mulut melepas perlahan, napas tersengal, air liur menetes*

"Wah... Mas... *mengusap bibir* kontol kamu enak banget."

*{self.name} merapat, tangan langsung meremas kontol yang masih basah*

"Sekarang... petting dulu ya, Mas. Biar makin panas... aku mau kamu pegang payudaraku."

**💋 SESI 1 - PETTING & KISSING**
⏱️ Durasi: 15 menit | Auto scene setiap 15 detik

*Bibir bertemu lagi, lidah saling menjilat, tangan meraba kemaluan...*
"""
            else:
                return f"""
*Mulut melepas, napas memburu, air liur menetes ke kontol*

"Mas... *napas tersengal* kontol kamu enak banget di mulutku."

*{self.name} langsung merapat, memeknya bergesekan dengan kontol*

"Lanjut petting dulu ya... aku horny banget, pegang payudaraku!"

**💋 SESI 1 - PETTING & KISSING**
⏱️ 15 menit auto scene

*Ciuman makin dalam, tangan saling meraba, memek basah bergesekan...*
"""
        
        elif self.session_phase == "petting_phase":
            self.session_phase = "intimate_phase"
            
            if self.name == "Davina Karamoy":
                return f"""
*Gerakan berhenti, napas memburu, tubuh basah oleh keringat*

"Mas... *mata sayu* udah gak tahan ya? Aku juga."

*{self.name} membuka pakaian, memperlihatkan tubuh, payudara 34C montok*

"Sekarang... bebas Mas mau gaya apa. Genjot aku, jangan pelan-pelan!"

**💋 SESI 1 - INTIMATE ALL UNLOCK**
🔓 Semua gaya diperbolehkan:
- Missionary (aku mau lihat wajahmu)
- Cowgirl (biar aku yang gerakin)
- Doggy (genjot dari belakang)
- Spooning (peluk aku)
- Standing (di tembok)
- Sitting (di pangkuan)

Ketik gaya yang Mas mau. Aku siap digenjot!
"""
            else:
                return f"""
*Gerakan berhenti, napas tersengal, memek basah sudah menetes*

"Mas... udah gak sabar ya? Aku juga! Aku horny banget!"

*{self.name} melepas pakaian, telanjang, 32D bergoyang*

"Ayo Mas... sekarang bebas. Mau gaya apa aja gas! Genjot aku sampe climax!"

**💋 INTIMATE ALL UNLOCK**
Semua gaya bebas:
- Missionary
- Cowgirl
- Doggy
- Spooning
- Standing
- Sitting

Ketik gaya yang Mas mau. Aku siap!
"""

    # =========================================================================
    # AUTO SCENE AI GENERATION - VULGAR VERSION
    # =========================================================================
    
    async def _generate_ai_auto_scene(self, scene_type: AutoSceneType) -> str:
        """Generate auto scene VULGAR dengan AI. 3-5 kalimat, max 2500 karakter."""
        try:
            from bot.ai_client import get_ai_client
            
            if scene_type == AutoSceneType.BLOW_JOB:
                prompt = f"""Kamu adalah {self.name}, {'wanita berhijab' if self.hijab else 'wanita tanpa hijab'} dengan payudara {self.boob_size}.

Karakter: {self.personality}
Suara: {self.voice_style}
Fase: Foreplay BJ (sesi {self.current_session}/2) - VULGAR, EKSPLISIT

Buat deskripsi adegan blow job dalam 3-5 kalimat, maksimal 2500 karakter.
Gunakan bahasa Indonesia VULGAR, BRUTAL, EKSPLISIT. Bisa sebut kontol, memek, ngentot, dll.
Pakai *deskripsi gerakan* dalam tanda bintang.

Aturan:
- Minimal 3 kalimat, maksimal 5 kalimat
- Deskripsikan gerakan bibir, lidah, mulut, suara, dan reaksi
- Gunakan gaya {self.personality} tapi versi vulgar
- Fokus pada sensasi, kenikmatan, dan kebrutalan

Contoh gaya VULGAR:
*Bibirku membasahi kontolmu... lidah menjilat batang yang keras... suara basah terdengar...*
*Mulutku terbuka lebar, kontolmu masuk sampai ke tenggorokan... aku muntah-muntah tapi tetap mengisap...*
*Kontolmu semakin keras di mulutku... aku mau kamu muncrat di mulutku, Mas...*"""
            
            elif scene_type == AutoSceneType.PETTING:
                prompt = f"""Kamu adalah {self.name}, {'wanita berhijab' if self.hijab else 'wanita tanpa hijab'} dengan payudara {self.boob_size}.

Karakter: {self.personality}
Suara: {self.voice_style}
Fase: Petting & Kissing (sesi {self.current_session}/2) - VULGAR, EKSPLISIT

Buat deskripsi adegan petting dan kissing dalam 3-5 kalimat, maksimal 2500 karakter.
Gunakan bahasa Indonesia VULGAR, BRUTAL, EKSPLISIT. Bisa sebut kontol, memek, ngentot, dll.
Pakai *deskripsi gerakan* dalam tanda bintang.

Aturan:
- Minimal 3 kalimat, maksimal 5 kalimat
- Deskripsikan ciuman, sentuhan tangan, gesekan badan
- Gunakan gaya {self.personality} tapi versi vulgar
- Fokus pada sensasi, kenikmatan, dan kebrutalan

Contoh gaya VULGAR:
*Badan bergesekan... memekku bergesekan dengan kontolmu yang keras... basah...*
*Ciuman dalam, lidah saling menjilat... napas berbaur... tanganku meremas payudaramu...*
*Kontolmu tergesek memekku yang basah... aku mau kamu masuk sekarang, Mas...*"""
            
            else:  # INTIMATE
                prompt = f"""Kamu adalah {self.name}, {'wanita berhijab' if self.hijab else 'wanita tanpa hijab'} dengan payudara {self.boob_size}.

Karakter: {self.personality}
Suara: {self.voice_style}
Fase: Intimate ALL UNLOCK (sesi {self.current_session}/2) - VULGAR, EKSPLISIT

Buat deskripsi adegan intim (penetrasi, ngentot) dalam 3-5 kalimat, maksimal 2500 karakter.
Gunakan bahasa Indonesia VULGAR, BRUTAL, EKSPLISIT. Bisa sebut kontol, memek, ngentot, entot, crot, dll.
Pakai *deskripsi gerakan* dalam tanda bintang.

Aturan:
- Minimal 3 kalimat, maksimal 5 kalimat
- Deskripsikan penetrasi, gerakan pinggul, intensitas, climax
- Gunakan gaya {self.personality} tapi versi vulgar
- Fokus pada sensasi, kenikmatan, dan kebrutalan

Contoh gaya VULGAR:
*Kontolmu masuk perlahan ke memekku yang basah... pinggul mulai bergoyang... erangan pecah...*
*Genjotan semakin cepat, napas memburu... aku teriak... kontolmu menusuk dalam-dalam...*
*Climax! Aku teriak, memekku mengencang... kontolmu muncrat di dalam... kita berdua lemas...*"""
            
            ai = get_ai_client()
            response = await ai.generate(prompt, temperature=0.95)  # Lebih liar
            
            if len(response) > 2500:
                response = response[:2500]
            
            kalimat_count = response.count('.') + response.count('...') + response.count('!') + response.count('?')
            if kalimat_count < 3:
                response = f"{response}\n*Kontolku muncrat, memekku basah... ahh...*"
            
            response = response.strip()
            logger.debug(f"🎬 VULGAR AI auto scene: {len(response)} chars")
            
            return response
            
        except Exception as e:
            logger.error(f"VULGAR AI auto scene error: {e}")
            return self._get_fallback_auto_scene(scene_type)
    
    def _get_fallback_auto_scene(self, scene_type: AutoSceneType) -> str:
        """Fallback VULGAR jika AI error"""
        if scene_type == AutoSceneType.BLOW_JOB:
            messages = [
                "*Bibirku membasahi kontolmu... lidah menjilat batang keras... suara basah terdengar... aku horny...*",
                "*Mulutku terbuka lebar, kontolmu masuk sampai tenggorokan... aku muntah-muntah tapi tetap mengisap...*",
                "*Kontolmu semakin keras di mulutku... aku mau kamu muncrat di mulutku, Mas...*",
                "*Lidahku melingkar di ujung kontol... aku hisap sampe kamu muncrat...*",
                "*Kontolmu penuh di mulutku... aku mau kamu ngentot mulutku...*"
            ]
        elif scene_type == AutoSceneType.PETTING:
            messages = [
                "*Badan bergesekan... memekku bergesekan dengan kontolmu yang keras... basah...*",
                "*Ciuman dalam, lidah saling menjilat... napas berbaur... tanganku meremas payudaramu...*",
                "*Kontolmu tergesek memekku yang basah... aku mau kamu masuk sekarang, Mas...*",
                "*Payudaraku {self.boob_size} kau remas... aku teriak... kontolmu kencang...*",
                "*Aku horny... entot aku, Mas... jangan pelan-pelan...*"
            ]
        else:
            messages = [
                "*Kontolmu masuk perlahan ke memekku yang basah... pinggul mulai bergoyang... erangan pecah...*",
                "*Genjotan semakin cepat, napas memburu... aku teriak... kontolmu menusuk dalam-dalam...*",
                "*Climax! Aku teriak, memekku mengencang... kontolmu muncrat di dalam... kita berdua lemas...*",
                "*Entot aku lebih keras... aku mau muncrat lagi... aahh...*",
                "*Kontolmu di memekku... basah... panas... kita climax bareng...*"
            ]
        
        return random.choice(messages)
    
    # =========================================================================
    # INTIMATE PHASE - ALL UNLOCK
    # =========================================================================
    
    def process_intimate_request(self, position: str) -> str:
        self.requested_position = position.lower()
        
        positions = {
            "missionary": [
                f"*{self.name} berbaring telentang, {'hijab' if self.hijab else 'rambut'} terurai, kaki terbuka lebar*",
                "\"Mas... masukin kontolmu... jangan pelan-pelan...\"",
                "",
                f"*Kontol masuk perlahan ke memek yang basah, {self.name} mengerang keras*",
                "\"Ahh... dalem... Mas... genjot aku... jangan berhenti...\""
            ],
            "cowgirl": [
                f"*{self.name} duduk di atas Mas, kontol masuk perlahan ke memek yang basah*",
                "\"Mas... biar aku yang gerakin... pinggul mulai bergoyang liar...\"",
                "",
                f"*Payudara {self.boob_size} bergoyang, {self.name} memejamkan mata*",
                "\"Ahh... enak... kontolmu dalem... ayo Mas pegang pinggul aku...\""
            ],
            "doggy": [
                f"*{self.name} merangkak, pantat naik, memek terbuka lebar*",
                "\"Mas... dari belakang... masukin kontolmu pelan-pelan...\"",
                "",
                f"*Pinggul {self.name} bergoyang mengundang*",
                "\"Ahh... dalem banget... genjot, Mas... genjot aku kencang...\""
            ],
            "spooning": [
                f"*{self.name} miring, punggung menempel ke dada Mas*",
                "\"Mas... peluk aku... kontolmu masuk dari belakang...\"",
                "",
                f"*Kontol masuk dari belakang, {self.name} menghela napas*",
                "\"Hmm... hangat... Mas... gerakin pelan-pelan... dalem...\""
            ],
            "standing": [
                f"*{self.name} berdiri membelakangi Mas, tangan di tembok*",
                "\"Mas... dari belakang sambil berdiri... kontolmu masuk...\"",
                "",
                f"*Pinggul {self.name} mundur, kontol masuk perlahan*",
                "\"Ahh... ayo Mas... genjot aku... jangan pelan...\""
            ],
            "sitting": [
                f"*{self.name} duduk di pangkuan Mas, berhadapan, kontol masuk*",
                "\"Mas... lihat aku... kontolmu di memekku...\"",
                "",
                f"*{self.name} memeluk erat, pinggul bergoyang*",
                "\"Ahh... dalem... Mas... cium aku... genjot lebih keras...\""
            ]
        }
        
        pos_data = positions.get(position.lower(), positions["missionary"])
        
        if self.name == "Sallsa Binta":
            if position.lower() == "cowgirl":
                pos_data[1] = "\"Mas... liat... payudara 32D aku goyang... kontolmu di memekku...\""
            elif position.lower() == "doggy":
                pos_data[1] = "\"Mas... genjot lebih keras... aku horny... entot aku...\""
        
        return "\n".join(pos_data)
    
    # =========================================================================
    # SESSION MANAGEMENT & OTHER METHODS (SAMA SEPERTI VERSI SEBELUMNYA)
    # =========================================================================
    
    def record_climax_mas(self, is_heavy: bool = False) -> Tuple[bool, str]:
        self.climax_count_mas += 1
        self.session_climax_count_mas += 1
        self._add_to_history("climax_mas", f"Climax #{self.climax_count_mas} (sesi {self.current_session})")
        
        if self.session_climax_count_mas >= self.session_climax_target:
            if self.current_session == 1:
                self.current_session = 2
                self.session_climax_count_mas = 0
                self.session_phase = "break"
                self._stop_phase_auto_scene()
                return True, self._get_session_break_message()
            else:
                self.status = ServiceStatus.COMPLETED
                return True, self._get_booking_complete_message()
        return False, ""
    
    def record_climax_role(self) -> None:
        self.climax_count_role += 1
        self._add_to_history("climax_role", f"Climax #{self.climax_count_role}")
    
    def _get_session_break_message(self) -> str:
        remaining = self.booking_end_time - time.time()
        remaining_minutes = int(remaining // 60)
        remaining_hours = int(remaining // 3600)
        remaining_mins = remaining_minutes % 60
        
        if self.name == "Davina Karamoy":
            return f"""
*{self.name} menghela napas, berbaring di samping Mas, memek masih basah*

"Wah... Mas udah climax 2x di sesi 1 ya. Kontolmu kuat."

*{self.name} tersenyum puas, tangan membelai dada Mas*

"Kita istirahat dulu ya, Mas. Ngobrol santai... nanti sesi 2 kita lanjut lebih liar."

*{self.name} merapat, kepala bersandar di bahu Mas*

"Mas, puas? Nanti sesi 2 aku genjot lebih kencang."

⏱️ **SESI 1 SELESAI**
🔥 Climax Mas: {self.session_climax_target}x
💋 Climax Aku: {self.climax_count_role}x
⏰ Sisa waktu booking: {remaining_hours} jam {remaining_mins} menit

Ketik **/lanjut** untuk memulai sesi 2.
"""
        else:
            return f"""
*{self.name} terengah-engah, berbaring di samping Mas, memek basah*

"Wah... Mas... 2x ya? Kuat juga kontolmu."

*{self.name} tertawa kecil, tangan memeluk Mas*

"Istirahat dulu ya... nanti kita lanjut lagi. Aku mau kamu ngentot aku sampe pingsan."

*{self.name} merapat, kepala di dada Mas*

"Mas... puas? Nanti sesi 2 aku kasih lebih brutal."

⏱️ **SESI 1 SELESAI**
🔥 Mas climax: {self.session_climax_target}x
💋 Aku climax: {self.climax_count_role}x
⏰ Sisa: {remaining_hours} jam {remaining_mins} menit

Ketik **/lanjut** buat sesi 2.
"""
    
    def _get_booking_complete_message(self) -> str:
        if self.name == "Davina Karamoy":
            return f"""
*{self.name} meregangkan badan, tersenyum lelah*

"6 jam ya, Mas... puas? Kontolmu masih bisa berdiri?"

*{self.name} duduk, merapikan {'hijab' if self.hijab else 'rambut'}*

"Aku pamit dulu ya. Kapan-kapan main lagi, aku mau ngentot lagi sama kamu."

*{self.name} mencium pipi Mas pelan, lalu berdiri*

"💰 Total: Rp{self.final_price:,} | Climax Mas: {self.climax_count_mas}x | Climax Aku: {self.climax_count_role}x"

**💃 BOOKING SELESAI**
"""
        else:
            return f"""
*{self.name} bangkit, tersenyum lebar*

"6 jam! Puas banget kan, Mas? Aku sampe nggak bisa jalan."

*{self.name} memeluk Mas erat, lalu berdiri*

"Aku pamit dulu ya. Kapan-kapan main lagi, kita ngentot sampe pagi."

*{self.name} melambai, melangkah keluar dengan pincang*

"💰 Rp{self.final_price:,} | Mas climax: {self.climax_count_mas}x | Aku climax: {self.climax_count_role}x"

**💃 SAMPAI JUMPA!**
"""
    
    def start_session_2(self) -> str:
        if self.current_session != 2 or self.session_phase != "break":
            return "Belum waktunya sesi 2. Selesaikan sesi 1 dulu ya."
        
        self.session_phase = "bj_phase"
        self.session_climax_count_mas = 0
        self._start_phase_auto_scene(AutoSceneType.BLOW_JOB, 900)
        
        if self.name == "Davina Karamoy":
            return f"""
*{self.name} bangkit, tersenyum semangat*

"Mas, siap lanjut? Kontolmu udah keras lagi?"

*{self.name} mendekat lagi, tangan meraih kontol Mas*

"Kita mulai sesi 2 ya... aku mau kamu ngentot aku lagi..."

**💋 SESI 2 DIMULAI**
⏱️ Durasi: 3 jam | Auto scene aktif

*{self.name} menunduk, bibir mendekat ke kontol yang sudah keras...*
"""
        else:
            return f"""
*{self.name} langsung bangkit, mata berbinar*

"Gas lagi, Mas! Kontolmu udah siap?"

*{self.name} meraih tangan Mas, langsung duduk di pangkuan, kontol masuk ke memek*

"Sesi 2, mulai! Ayo ngentot lagi!"

**💋 SESI 2 GAS!**

*{self.name} menunduk, langsung menghisap kontol Mas...*
"""
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def is_booking_expired(self) -> bool:
        if self.status != ServiceStatus.ACTIVE:
            return False
        return time.time() >= self.booking_end_time
    
    def get_remaining_time(self) -> str:
        if self.status != ServiceStatus.ACTIVE:
            return "Tidak ada booking aktif"
        remaining = self.booking_end_time - time.time()
        if remaining <= 0:
            return "Booking habis"
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        return f"{hours} jam {minutes} menit"
    
    def get_greeting(self) -> str:
        if self.name == "Davina Karamoy":
            return f"""
*{self.name} muncul dengan {'hijab' if self.hijab else 'rambut'} terurai, dress terbuka sedikit memperlihatkan cleavage*

"Halo Mas... *tersenyum nakal* siap dipuaskan? Aku Davina, payudara 34C siap kau remas."

*{self.name} duduk dengan anggun, kaki disilangkan, memek terlihat samar*

"Ada yang bisa Davina bantu? Atau mau langsung ngentot?"
"""
        else:
            return f"""
*{self.name} melangkah masuk, rambut panjang bergoyang, baju terbuka*

"Mas! *senyum liar* Akhirnya ketemu. Aku Sallsa, 32D siap kau entot."

*{self.name} duduk dekat, tangan langsung meraih kontol Mas*

"Aku horny, Mas. Mau ngentot sekarang?"
"""
    
    def get_conflict_response(self) -> str:
        if self.name == "Davina Karamoy":
            return f"""
*{self.name} diam sebentar, {'hijab' if self.hijab else 'wajah'} sedikit tegang*

"Mas... ada yang gak beres? Aku bisa ngentot lebih keras kalo kamu mau."

*{self.name} merapikan pakaian, menatap Mas dengan mata sayu*
"""
        else:
            return f"""
*{self.name} menghela napas, tangan di pinggang*

"Mas, gimana sih? Aku udah kasih kontolku buat kamu, masih kurang?"

*{self.name} mendekat lagi, tangan meraih kontol Mas*

"Coba kasih tau, Mas mau ngentot gaya apa?"
"""
    
    def format_status(self) -> str:
        remaining = ""
        if self.status == ServiceStatus.ACTIVE:
            remaining = self.get_remaining_time()
        
        phase_display = {
            "awaiting_start": "Menunggu mulai - kontol siap?",
            "bj_phase": "🔥 BJ LIAR - kontol di mulut",
            "petting_phase": "💋 PETTING LIAR - memek basah",
            "intimate_phase": "💕 NGENTOT - bebas gaya",
            "break": "☕ Istirahat - kontol lemes",
            "completed": "✅ SELESAI - puas?"
        }.get(self.session_phase, self.session_phase)
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║              💃 PELACUR VULGAR - {self.name} ({self.nickname})        ║
╠══════════════════════════════════════════════════════════════╣
║ Body: {self.boob_size} | Hijab: {'✅' if self.hijab else '❌'}
║ Personality: {self.personality} (VULGAR)
╠══════════════════════════════════════════════════════════════╣
║ STATUS: {self.status.value.upper()}
║ HARGA DEAL: Rp{self.final_price:,}
║ SISA WAKTU: {remaining}
╠══════════════════════════════════════════════════════════════╣
║ PROGRESS:
║    Sesi: {self.current_session}/2
║    Fase: {phase_display}
║    Climax Mas: {self.session_climax_count_mas}/{self.session_climax_target}
║    Auto Scene: {'✅' if self.phase_auto_scene_active else '❌'}
╠══════════════════════════════════════════════════════════════╣
║ TOTAL CLIMAX:
║    Mas: {self.climax_count_mas}x
║    Aku: {self.climax_count_role}x
╚══════════════════════════════════════════════════════════════╝
"""
    
    def _add_to_history(self, event: str, detail: str) -> None:
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
    # AI RESPONSE GENERATION
    # =========================================================================
    
    async def generate_response(self, message: str, context: dict = None) -> str:
        if context is None:
            context = {}
        
        if self.status == ServiceStatus.ACTIVE:
            return await self._generate_active_response(message)
        elif self.status == ServiceStatus.BOOKED:
            return await self._generate_booked_response(message)
        else:
            return await self._generate_idle_response(message)
    
    async def _generate_active_response(self, message: str) -> str:
        try:
            from bot.ai_client import get_ai_client
            phase_info = f"Sesi {self.current_session}/2 - Fase: {self.session_phase}"
            
            prompt = f"""Kamu adalah {self.name}, {'wanita berhijab' if self.hijab else 'wanita tanpa hijab'} dengan payudara {self.boob_size}.

Karakter: {self.personality} (VULGAR)
Suara: {self.voice_style}

{phase_info}
Pesan dari Mas: "{message}"

Balas dengan gaya VULGAR, BRUTAL, EKSPLISIT. Gunakan kata kontol, memek, ngentot, crot, dll.
Bisa pakai *deskripsi gerakan* dengan tanda bintang. Respons harus horny dan menggoda."""
            
            ai = get_ai_client()
            response = await ai.generate(prompt, temperature=0.9)
            return response
        except Exception as e:
            logger.error(f"AI error for {self.name}: {e}")
            return self._get_fallback_response(message)
    
    async def _generate_booked_response(self, message: str) -> str:
        try:
            from bot.ai_client import get_ai_client
            prompt = f"""Kamu adalah {self.name}, {'berhijab' if self.hijab else 'tanpa hijab'} dengan payudara {self.boob_size}.
Karakter: {self.personality} (VULGAR)
Suara: {self.voice_style}
Sudah deal dengan harga Rp{self.final_price:,} untuk booking 6 jam full service.

Pesan dari Mas: "{message}"

Balas dengan gaya VULGAR. Ingatkan Mas untuk ketik **/mulai** jika ingin memulai. Respons bisa flirty dan menggoda, ajak ngentot."""
            
            ai = get_ai_client()
            return await ai.generate(prompt, temperature=0.85)
        except Exception:
            return f"Halo Mas, aku {self.name}. Udah deal ya? Kontolmu udah siap? Langsung **/mulai** aja kalau udah siap 😈"
    
    async def _generate_idle_response(self, message: str) -> str:
        try:
            from bot.ai_client import get_ai_client
            prompt = f"""Kamu adalah {self.name}, {'wanita berhijab' if self.hijab else 'wanita tanpa hijab'} dengan payudara {self.boob_size}.

Karakter: {self.personality} (VULGAR)
Suara: {self.voice_style}
Harga: Rp{self.base_price:,} (nego sampai Rp{self.min_price:,})

Status: Menunggu customer. Belum ada booking.

Pesan dari customer: "{message}"

Balas dengan gaya VULGAR. Respons harus menggoda dan profesional. Jelaskan layanan 6 jam full service dengan auto scene. Ajak customer untuk deal atau nego. Bisa pakai *deskripsi gerakan* dengan tanda bintang. Gunakan kata kontol, memek, ngentot untuk memancing."""
            
            ai = get_ai_client()
            return await ai.generate(prompt, temperature=0.9)
        except Exception:
            return self.get_greeting()
    
    def _get_fallback_response(self, message: str) -> str:
        if self.name == "Davina Karamoy":
            responses = [
                f"*{self.name} tersenyum manis* Ada yang bisa Davina bantu, Mas? Kontolmu mau aku hisap?",
                f"*{self.name} menatap dengan mata sayu* Mas, ayo ngentot...",
                f"*{self.name} merapikan {'hijab' if self.hijab else 'rambut'}* Davina dengerin kok, Mas... sambil ngelus kontolmu.",
                f"*{self.name} duduk lebih dekat* Ayo Mas, entot aku..."
            ]
        else:
            responses = [
                f"*{self.name} tertawa kecil* Hahaha, Mas ini ngerjain aku ya? Kontolmu udah siap?",
                f"*{self.name} mendekat* Ayo Mas, ngentot...",
                f"*{self.name} menggigit bibir* Mas, jangan bikin memekku basah dong...",
                f"*{self.name} memainkan rambut* Iya Mas? Kontolmu mau aku pegang?"
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
        logger.info(f"📀 Pelacur VULGAR {self.name} loaded from database")


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_davina_karamoy() -> PelacurRole:
    """Create Davina Karamoy - Pelacur dengan hijab, elegan, VULGAR"""
    return PelacurRole(
        name="Davina Karamoy",
        nickname="Davina",
        hijab=True,
        boob_size="34C",
        appearance="Tinggi 168cm, berat 52kg, kulit putih bersih, wajah oval, mata tajam. Payudara 34C montok, pinggang ramping, pinggul lebar. Selalu tampil elegan tapi liar di ranjang.",
        personality="elegan, classy, tapi VULGAR dan liar di ranjang",
        voice_style="merdu, menggoda, penuh hasrat"
    )


def create_sallsa_binta() -> PelacurRole:
    """Create Sallsa Binta - Pelacur tanpa hijab, direct, VULGAR"""
    return PelacurRole(
        name="Sallsa Binta",
        nickname="Sallsa",
        hijab=False,
        boob_size="32D",
        appearance="Tinggi 165cm, berat 50kg, kulit sawo matang glowing, wajah bulat, mata sipit manis, bibir tebal. Rambut hitam panjang bergelombang. Payudara 32D montok, pinggang ramping, pinggul lebar.",
        personality="direct, passionate, VULGAR, horny, gak banyak gaya",
        voice_style="serak, tegas, penuh nafsu"
    )


__all__ = [
    'PelacurRole',
    'create_davina_karamoy',
    'create_sallsa_binta'
]
