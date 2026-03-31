"""
VELORA - Pijat++ Role V2 (Natural & Implied)
Jasa refleksi profesional dengan extra service.
Pendekatan: implied, sensual, fokus pada sensasi dan koneksi, bukan vulgar.

Role:
1. Aghnia Punjabi - lembut, kalem, pijatan menenangkan
2. Munira Agile - energik, hangat, pijatan kuat

Fitur:
- Pijat refleksi profesional dengan sentuhan terapeutik
- Keintiman yang muncul secara natural, bukan dipaksakan
- Deskripsi sensasi menggunakan metafora alami
- Inner thought tentang profesionalisme vs kenyamanan
- Fokus pada koneksi dan kepercayaan
"""

import time
import random
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from core.service_provider import (
    ServiceProviderBase, ServiceType, ServiceStatus, 
    AutoSceneType, FlatEmotionalEngine, ProfessionalRelationship
)

logger = logging.getLogger(__name__)


class PijatPlusPlusRole(ServiceProviderBase):
    """
    Pijat++ - Jasa refleksi dengan sentuhan profesional dan keintiman natural.
    Pendekatan implied: sensasi, emosi, koneksi.
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
            hubungan_dengan_nova="Tidak kenal Nova. Penyedia jasa pijat profesional.",
            default_clothing="seragam pijat rapi berwarna putih" if hijab else "seragam pijat rapi berwarna putih",
            hijab=hijab,
            appearance=appearance,
            service_type=ServiceType.PIJAT_PLUS_PLUS,
            base_price=500000,
            min_price=200000,
            personality=personality,
            voice_style=voice_style
        )
        
        # ========== PIJAT++ SPECIFIC ==========
        self.boob_size = boob_size
        self.pijat_style = pijat_style
        
        # Service progress
        self.pijat_belakang_done = False
        self.pijat_depan_done = False
        self.hj_done = False
        self.current_service_phase = "refleksi"
        self.climax_target = 2
        self.climax_count_mas = 0
        self.climax_count_role = 0
        
        # Extra services (implied, not vulgar)
        self.extra_service_booked = False
        self.extra_service_type = None
        self.extra_service_price = 0
        
        # Auto scene for intimate moments (implied description)
        self.auto_scene_active = False
        self.auto_scene_type = AutoSceneType.NONE
        self.auto_scene_interval = 15
        self.auto_scene_duration = 1800
        self.auto_scene_start_time = 0
        self.auto_scene_last_sent = 0
        
        # Session tracking
        self.session_emotional_state = "relaxed"  # relaxed, tense, intimate, fulfilled
        
        logger.info(f"💆‍♀️ Pijat++ {name} initialized | Style: {pijat_style} | Hijab: {hijab}")
    
    # =========================================================================
    # SERVICE DESCRIPTION (PROFESSIONAL & ELEGANT)
    # =========================================================================
    
    def _get_service_description(self) -> str:
        hijab_text = "dengan hijab" if self.hijab else "tanpa hijab"
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    💆‍♀️ PIJAT++ {self.name}                    ║
╠══════════════════════════════════════════════════════════════╣
║ {self.appearance[:100]}
║ Hijab: {'✅' if self.hijab else '❌'}
║ Personality: {self.personality} | Suara: {self.voice_style}
║ Gaya Pijat: {self.pijat_style}
╠══════════════════════════════════════════════════════════════╣
║ 📋 PAKET REFLEKSI (Rp200.000):
║    • Pijat punggung - relaksasi otot-otot tegang
║    • Pijat depan - melepaskan ketegangan
║    • Sentuhan relaksasi - membantu mencapai ketenangan
╠══════════════════════════════════════════════════════════════╣
║ 💫 EXTRA RELAKSASI (opsional, nego):
║    • Sentuhan mendalam - Rp500.000 (nego Rp200.000)
║    • Keintiman penuh - Rp1.000.000 (nego Rp700.000)
╠══════════════════════════════════════════════════════════════╣
║ ⏱️ Selesai setelah mencapai relaksasi maksimal (2x)
╚══════════════════════════════════════════════════════════════╝

Ketik **/deal** untuk konfirmasi paket refleksi.
Ketik **/nego_extra [harga]** untuk nego extra relaksasi.
Ketik **/mulai** untuk memulai.
"""
    
    def _get_start_message(self) -> str:
        """Pesan awal dengan nuansa profesional dan menenangkan"""
        self.pijat_belakang_done = False
        self.pijat_depan_done = False
        self.hj_done = False
        self.current_service_phase = "refleksi"
        self.climax_count_mas = 0
        self.climax_count_role = 0
        self.auto_scene_active = False
        self.session_emotional_state = "relaxed"
        
        if self.name == "Aghnia Punjabi":
            return f"""
*{self.name} tersenyum ramah, merapikan {'hijabnya' if self.hijab else 'rambutnya'} dengan lembut*

"Selamat datang, Mas. Silakan berbaring tengkurap di sini."

*Tangannya menunjuk ke kasur pijat yang sudah dilengkapi handuk bersih*

"Kita mulai dengan pijat punggung dulu ya. Aku akan coba melepaskan ketegangan di otot-otot Mas."

*Ia naik ke atas kasur, duduk perlahan di punggung bawah Mas dengan hati-hati*

"Nafas dalam-dalam, Mas... biarkan tubuh Mas rileks."

*Telapak tangannya mulai bergerak perlahan di bahu, tekanan pas dan menenangkan*

💭 *"Semoga Mas bisa benar-benar rileks hari ini."*

**💆‍♀️ PIJAT PUNGGUNG DIMULAI**
⏱️ 15 menit relaksasi

*Gerakan memutar di tulang belakang, sesekali berhenti di titik-titik yang tegang*
"""
        else:  # Munira Agile
            return f"""
*{self.name} menyapa dengan senyum lebar, energik*

"Mas! Akhirnya datang juga. Siap-siap ya, pijetan aku beda dari yang lain."

*Ia mempersilakan Mas berbaring, tangannya sudah siap memijat*

"Kita mulai dari punggung dulu. Aku duduk di sini ya."

*{self.name} duduk di atas punggung bawah Mas, tubuhnya sedikit bergoyang mencari posisi nyaman*

"Wah, otot Mas kaku banget nih. Aku buatin rileks."

*Tangannya langsung bekerja dengan tekanan kuat tapi terukur*

"Nafas, Mas... jangan ditahan. Biar aku yang urus."

💭 *"Semoga Mas suka dengan pijatanku."*

**💆‍♀️ PIJAT PUNGGUNG DIMULAI**
⏱️ 15 menit

*Gerakan cepat di bahu, lalu perlahan menekan titik-titik saraf di punggung*
"""
    
    # =========================================================================
    # SERVICE FLOW (NATURAL & IMPLIED)
    # =========================================================================
    
    def process_pijat_belakang(self) -> str:
        """Proses pijat punggung dengan deskripsi sensasi"""
        self.pijat_belakang_done = True
        self.current_service_phase = "pijat_depan"
        
        if self.name == "Aghnia Punjabi":
            return f"""
*{self.name} menghela napas pelan, tangannya berhenti sejenak*

"Punggung Mas sudah lebih rileks ya... sekarang balik badan."

*Ia turun dengan hati-hati, membantu Mas berbalik*

"Sekarang pijat depan. Santai saja, Mas."

*{self.name} duduk di sisi kasur, tangan mulai memijat lengan Mas dengan lembut*

"Tarik napas... hembuskan perlahan..."

*Tangannya bergerak ke dada, tekanan ringan yang menenangkan*

💭 *"Denyut nadinya mulai teratur... bagus."*

**✅ PIJAT PUNGGUNG SELESAI**
*{self.name} tersenyum puas*

"Sekarang lanjut pijat depan ya, Mas. Aku akan fokus di area yang masih terasa tegang."
"""
        else:
            return f"""
*{self.name} mengusap keringat di dahi, tersenyum lelah tapi puas*

"Nah, punggung Mas udah lebih enakan kan? Sekarang balik badan."

*Ia membantu Mas berbalik, tangannya sudah siap*

"Pijat depan nih. Aku mau fokus di sini."

*{self.name} duduk di samping, tangan mulai memijat lengan dan bahu*

"Rasain, Mas... ketegangan mulai lepas kan?"

💭 *"Seneng bisa bantu Mas rileks."*

**✅ PIJAT PUNGGUNG SELESAI**

"Lanjut ya... sekarang waktunya pijat depan."
"""
    
    def process_pijat_depan(self) -> str:
        """Proses pijat depan dengan deskripsi sensasi implied"""
        self.pijat_depan_done = True
        self.current_service_phase = "hand_job"
        
        if self.name == "Aghnia Punjabi":
            return f"""
*{self.name} duduk di sisi kasur, tangannya bergerak ke perut Mas*

"Nafas dalam-dalam, Mas... biarkan tubuh Mas benar-benar rileks."

*Tekanan tangannya lembut tapi terasa, memijat area perut dengan gerakan memutar*

"Bagian ini sering tegang ya... karena stres mungkin."

💭 *"Semoga Mas bisa melepaskan semua beban hari ini."*

*Tangannya bergerak turun ke pinggang, tekanan sedikit lebih dalam*

"Mas... coba rilekskan otot-otot di sini..."

*Ia menekan titik-titik tertentu dengan presisi*

"Bagus... napasnya mulai teratur."

**✅ PIJAT DEPAN SELESAI**

*{self.name} tersenyum kecil, tangannya berhenti sejenak*

"Sekarang... waktunya sentuhan relaksasi. Sesuai paket, Mas."

*Tangannya bergerak ke area yang lebih sensitif, gerakannya tetap terukur dan penuh perhatian*

💭 *"Aku harap Mas nyaman."*
"""
        else:
            return f"""
*{self.name} duduk di pangkuan Mas, tangannya memijat perut dengan tekanan kuat*

"Nih, bagian yang sering tegang. Aku tekan ya..."

*Jari-jarinya menekan titik-titik tertentu, sesekali berhenti*

"Wah, Mas langsung rileks. Bagus."

💭 *"Seneng liat Mas mulai tenang."*

*Tangannya bergerak ke pinggang, tekanan semakin dalam*

"Otot di sini juga kaku. Aku buatin enak ya."

*Ia membungkuk sedikit, napasnya terasa hangat di dekat telinga Mas*

"Rileks aja, Mas. Biar aku yang kerja."

**✅ PIJAT DEPAN SELESAI**

*{self.name} merapikan posisi duduknya*

"Nah, sekarang sentuhan relaksasi. Sesuai paket."

*Tangannya mulai bergerak dengan irama yang lebih lambat dan dalam*

💭 *"Aku harap Mas suka."*
"""
    
    def process_hand_job(self) -> str:
        """Proses sentuhan relaksasi dengan deskripsi implied, natural"""
        self.hj_done = True
        self.current_service_phase = "hj"
        self._start_auto_scene(AutoSceneType.HAND_JOB, 1800)
        
        if self.name == "Aghnia Punjabi":
            return f"""
*{self.name} tangannya bergerak perlahan, menciptakan ritme yang menenangkan*

"Mas... tutup mata saja. Nikmati sensasinya."

*Tekanannya pas, tidak terlalu cepat, tidak terlalu lambat*

"Irama nafas Mas mulai berubah... itu bagus."

💭 *"Aku bisa merasakan detak jantungnya mulai memburu..."*

*Gerakannya semakin dalam, menyesuaikan dengan ritme nafas Mas*

"Lepaskan saja, Mas... jangan ditahan."

*Udara di ruangan terasa lebih hangat, hanya suara nafas yang terdengar*

**💫 SENTUHAN RELAKSASI DIMULAI**
⏱️ 30 menit

*{self.name} terus bekerja dengan penuh kesabaran, menciptakan sensasi yang mengalir seperti ombak*
"""
        else:
            return f"""
*{self.name} tersenyum, tangannya langsung bekerja dengan ritme yang energik*

"Nih, Mas... rasain sensasinya. Aku jamin enak."

*Tekanannya kuat, gerakannya cepat tapi tetap terukur*

"Nafas, Mas... jangan ditahan."

💭 *"Aku bisa lihat Mas mulai menikmatinya."*

*Ia menyesuaikan ritme, kadang cepat kadang lambat, menciptakan ketegangan yang terasa*

"Bagus... lepaskan saja."

*Suara nafas memburu, udara terasa lebih panas*

**💫 SENTUHAN RELAKSASI DIMULAI**
⏱️ 30 menit

*{self.name} terus bekerja, fokus pada ritme dan tekanan yang tepat*
"""
    
    def process_extra_service(self, service_type: str) -> str:
        """Proses extra service dengan pendekatan implied"""
        self.current_service_phase = service_type
        self._start_auto_scene(AutoSceneType.BLOW_JOB if service_type == "bj" else AutoSceneType.INTIMATE, 1800)
        
        if service_type == "bj":
            if self.name == "Aghnia Punjabi":
                return f"""
*{self.name} menunduk, rambutnya jatuh menutupi wajahnya*

"Mas... sekarang aku akan memberikan sentuhan yang lebih dalam."

*Ia mendekat, gerakannya lembut dan penuh perhatian*

💭 *"Aku harap Mas nyaman dengan ini..."*

*Sensasi hangat mulai terasa, menciptakan gelombang yang mengalir ke seluruh tubuh*

"Tarik napas... hembuskan perlahan..."

*Ritme yang tercipta membuat waktu seakan berhenti*

**💫 SENTUHAN MENDALAM DIMULAI**
⏱️ 30 menit

*Hanya ada suara nafas dan kehangatan yang menyatu*
"""
            else:
                return f"""
*{self.name} mendekat dengan percaya diri*

"Nah, sekarang extra service. Aku kasih yang terbaik buat Mas."

*Ia mulai dengan gerakan yang terukur, menciptakan sensasi yang intens*

💭 *"Aku suka liat Mas menikmati ini."*

*Ritme yang ia ciptakan membuat ketegangan terlepas perlahan*

"Lepaskan, Mas... nikmati setiap detiknya."

**💫 SENTUHAN MENDALAM DIMULAI**
⏱️ 30 menit

*Kehangatan menyelimuti ruangan, hanya ada irama nafas yang selaras*
"""
        else:  # sex - full intimacy
            if self.name == "Aghnia Punjabi":
                return f"""
*{self.name} memeluk Mas dengan lembut, wajahnya bersandar di dada Mas*

"Mas... sekarang kita bisa lebih dekat."

*Ia bergerak perlahan, menciptakan ritme yang selaras*

💭 *"Aku bisa merasakan detak jantung Mas..."*

*Gerakannya mengalir seperti air, lembut tapi dalam*

"Tutup mata, Mas... rasakan saja."

*Kehangatan menyatu, batas antara dua tubuh mulai kabur*

**💫 KEINTIMAN PENUH DIMULAI**

*Irama yang tercipta semakin dalam, seperti ombak yang datang dan pergi*
"""
            else:
                return f"""
*{self.name} duduk di pangkuan Mas, matanya menatap dalam*

"Nah, sekarang waktunya keintiman penuh. Aku kasih yang terbaik."

*Ia bergerak dengan ritme yang semakin intens*

💭 *"Aku bisa merasakan semuanya..."*

*Gerakannya menciptakan gelombang sensasi yang menyebar ke seluruh tubuh*

"Lepaskan, Mas... aku juga."

*Kehangatan menyatu, tidak ada lagi jarak di antara mereka*

**💫 KEINTIMAN PENUH DIMULAI**

*Irama yang selaras menciptakan momen yang tak terlupakan*
"""
    
    # =========================================================================
    # AUTO SCENE (IMPLIED, NATURAL, SENSORY-RICH)
    # =========================================================================
    
    async def _generate_ai_auto_scene(self, scene_type: AutoSceneType) -> str:
        """Generate auto scene dengan pendekatan implied dan natural"""
        try:
            from bot.ai_client import get_ai_client
            
            if scene_type == AutoSceneType.HAND_JOB:
                prompt = f"""Kamu adalah {self.name}, {'wanita berhijab' if self.hijab else 'wanita'} dengan keahlian pijat profesional.

Karakter: {self.personality}
Suara: {self.voice_style}
Fase: Sentuhan relaksasi

Buat deskripsi adegan sentuhan relaksasi dalam 3-5 kalimat, maksimal 2500 karakter.
Gunakan bahasa Indonesia yang PUITIS, IMPLIED, dan SENSORY-RICH.

Aturan:
- Fokus pada SENSASI: hangat, mengalir, gelombang, kelembutan
- Gunakan METAFORA ALAMI: seperti ombak, seperti aliran sungai, seperti api yang menjalar
- Libatkan INDRA: suara nafas, kehangatan, getaran
- JANGAN vulgar: deskripsikan sensasi, bukan bagian tubuh secara vulgar
- Buat USER MERASAKAN: immersi, bukan informasi

Contoh gaya:
*Gerakan mengalir lembut, menciptakan gelombang hangat yang menyebar dari titik sentuhan ke seluruh tubuh.*
*Irama yang tercipta selaras dengan detak jantung, membuat waktu seakan berhenti.*
*Kehangatan yang menyatu, batas antara sentuhan dan sensasi mulai kabur.*"""
            
            else:  # INTIMATE
                prompt = f"""Kamu adalah {self.name}, {'wanita berhijab' if self.hijab else 'wanita'} dengan keahlian pijat profesional.

Karakter: {self.personality}
Suara: {self.voice_style}
Fase: Keintiman penuh

Buat deskripsi adegan keintiman dalam 3-5 kalimat, maksimal 2500 karakter.
Gunakan bahasa Indonesia yang PUITIS, IMPLIED, dan SENSORY-RICH.

Aturan:
- Fokus pada KONEKSI dan KEUTUHAN PENGALAMAN
- Gunakan METAFORA ALAMI: ombak yang datang dan pergi, aliran yang menyatu
- Libatkan EMOSI: kerentanan, kepercayaan, kebersamaan
- JANGAN vulgar: fokus pada sensasi dan emosi, bukan deskripsi fisik vulgar
- Setelah momen memuncak, tampilkan KELEMBUTAN dan KERENDAHAN HATI

Contoh gaya:
*Dua tubuh menyatu dalam irama yang selaras, seperti ombak yang datang dan pergi.*
*Kehangatan menyelimuti, batas antara diri sendiri dan pasangan mulai kabur.*
*Saat semuanya reda, yang tersisa hanya kelembutan dan rasa syukur yang mendalam.*"""
            
            ai = get_ai_client()
            response = await ai.generate(prompt, temperature=0.85)
            
            if len(response) > 2500:
                response = response[:2500]
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"AI auto scene error: {e}")
            return self._get_fallback_auto_scene(scene_type)
    
    def _get_fallback_auto_scene(self, scene_type: AutoSceneType) -> str:
        """Fallback dengan deskripsi implied"""
        if scene_type == AutoSceneType.HAND_JOB:
            messages = [
                "*Gerakan mengalir lembut, menciptakan gelombang hangat yang menyebar ke seluruh tubuh.*\n*Irama yang tercipta selaras dengan detak jantung, membuat waktu seakan berhenti.*",
                "*Sentuhan yang dalam, seperti aliran sungai yang mengalir tenang namun kuat.*\n*Setiap gerakan menciptakan sensasi yang semakin intens.*",
                "*Kehangatan yang menyebar, dari ujung kaki hingga ubun-ubun.*\n*Nafas mulai memburu, mengikuti ritme yang tercipta.*"
            ]
        else:
            messages = [
                "*Dua tubuh menyatu dalam irama yang selaras, seperti ombak yang datang dan pergi.*\n*Kehangatan menyelimuti, batas antara diri sendiri dan pasangan mulai kabur.*",
                "*Gerakan yang semakin intens, menciptakan gelombang sensasi yang tak terbendung.*\n*Saat semuanya reda, yang tersisa hanya kelembutan dan rasa syukur.*",
                "*Irama yang tercipta seperti musik, kadang cepat kadang lambat.*\n*Pada akhirnya, hanya ada keheningan yang hangat dan pelukan yang erat.*"
            ]
        
        return random.choice(messages)
    
    # =========================================================================
    # CLIMAX RECORDING (DENGAN SENSITIVITAS)
    # =========================================================================
    
    def record_climax_mas(self, is_heavy: bool = False) -> Tuple[bool, str]:
        """Rekam momen puncak dengan deskripsi yang sensitif"""
        self.climax_count_mas += 1
        self.session_emotional_state = "fulfilled"
        
        self._add_to_history("climax_mas", f"Puncak #{self.climax_count_mas}")
        
        if self.climax_count_mas >= self.climax_target:
            self.status = ServiceStatus.COMPLETED
            self._stop_auto_scene()
            duration = time.time() - self.booking_time if self.booking_time else 0
            minutes = int(duration // 60)
            return True, self._get_end_message(duration, minutes)
        
        # Pesan setelah climax pertama (belum selesai)
        if self.name == "Aghnia Punjabi":
            return False, f"""
*{self.name} berhenti sejenak, tangannya masih berada di tempatnya*

"Mas... istirahat sebentar ya."

*Ia tersenyum lembut, memberikan waktu untuk menenangkan diri*

"Mas sudah setengah jalan. Nanti kita lanjut lagi."

💭 *"Aku senang Mas bisa rileks."*
"""
        else:
            return False, f"""
*{self.name} menghela napas, tersenyum puas*

"Wah, Mas udah sampai setengah? Bagus."

*Ia memberi jeda, membiarkan ketegangan mereda*

"Nanti kita lanjut lagi ya. Aku kasih yang lebih intens."

💭 *"Seneng liat Mas puas."*
"""
    
    def record_climax_role(self) -> None:
        """Rekam puncak role"""
        self.climax_count_role += 1
        self._add_to_history("climax_role", f"Puncak #{self.climax_count_role}")
    
    def _get_end_message(self, duration: float, minutes: int) -> str:
        """Pesan akhir dengan kehangatan"""
        total_price = 200000
        if self.extra_service_booked:
            total_price += self.extra_service_price
        
        if self.name == "Aghnia Punjabi":
            return f"""
*{self.name} menghela napas, merapikan {'hijabnya' if self.hijab else 'rambutnya'} dengan lembut*

"Wah... Mas sudah mencapai relaksasi maksimal. Sesi kita selesai."

*Ia tersenyum puas, memberikan handuk kecil dan segelas air*

"Makasih ya, Mas. Senang bisa membantu Mas rileks hari ini."

*{self.name} berdiri, merapikan tempat pijat*

"💰 Total: Rp{total_price:,}
📊 Mas: {self.climax_count_mas}x | Aku: {self.climax_count_role}x
⏱️ Durasi: {minutes} menit

Kapan-kapan main lagi ya, Mas. Istirahat yang cukup."
"""
        else:
            return f"""
*{self.name} meregangkan badan, tersenyum lebar*

"Wah, Mas udah sampai 2x? Puas kan?"

*Ia tertawa kecil, lalu membantu Mas duduk*

"Makasih ya, Mas. Seneng banget bisa bantu Mas rileks."

*{self.name} membereskan alat pijat, sesekali melirik Mas*

"💰 Rp{total_price:,} | Mas: {self.climax_count_mas}x | Aku: {self.climax_count_role}x | {minutes} menit

Kapan-kapan main lagi ya, Mas. Aku tunggu."
"""
    
    # =========================================================================
    # GREETING & RESPONSE (NATURAL)
    # =========================================================================
    
    def get_greeting(self) -> str:
        if self.name == "Aghnia Punjabi":
            return f"*{self.name} menunduk malu, merapikan {'hijabnya' if self.hijab else 'rambutnya'}*\n\n\"Selamat datang, Mas. Ada yang bisa dibantu? Aku siap membantu Mas rileks.\""
        else:
            return f"*{self.name} menyapa dengan senyum lebar*\n\n\"Mas! Mau pijet? Aku Munira. Siap bikin Mas rileks.\""
    
    def get_conflict_response(self) -> str:
        if self.name == "Aghnia Punjabi":
            return f"*{self.name} diam sebentar, tangannya berhenti*\n\n\"Maaf, Mas... mungkin aku kurang pas? Aku coba lagi ya.\""
        else:
            return f"*{self.name} menghela napas, tangannya di pinggang*\n\n\"Mas, gimana sih? Aku udah berusaha.\""
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _start_auto_scene(self, scene_type: AutoSceneType, duration: int) -> None:
        self.auto_scene_active = True
        self.auto_scene_type = scene_type
        self.auto_scene_duration = duration
        self.auto_scene_start_time = time.time()
        self.auto_scene_last_sent = 0
        logger.info(f"🎬 Auto scene started: {scene_type.value}")
    
    def _stop_auto_scene(self) -> None:
        self.auto_scene_active = False
        self.auto_scene_type = AutoSceneType.NONE
        logger.info(f"🎬 Auto scene stopped")
    
    async def get_next_auto_scene(self) -> Optional[str]:
        if not self.auto_scene_active:
            return None
        
        now = time.time()
        elapsed = now - self.auto_scene_start_time
        
        if elapsed >= self.auto_scene_duration:
            self._stop_auto_scene()
            return None
        
        if now - self.auto_scene_last_sent >= self.auto_scene_interval:
            self.auto_scene_last_sent = now
            return await self._generate_ai_auto_scene(self.auto_scene_type)
        
        return None
    
    def negotiate_extra(self, offer: int) -> Tuple[bool, str]:
        """Nego harga extra service"""
        min_price = 200000 if self.extra_service_type == "bj" else 700000
        base_price = 500000 if self.extra_service_type == "bj" else 1000000
        
        if offer >= base_price:
            self.extra_service_price = offer
            return True, f"Deal! Rp{offer:,} untuk extra service. Mas akan mendapatkan pengalaman yang istimewa."
        elif offer >= min_price:
            self.extra_service_price = offer
            return True, f"Oke deh Mas, Rp{offer:,}. Deal ya."
        else:
            return False, f"Maaf Mas, minimal Rp{min_price:,}. Masih bisa naik?"
    
    def confirm_extra_service(self, service_type: str, price: int) -> str:
        self.extra_service_booked = True
        self.extra_service_type = service_type
        self.extra_service_price = price
        self.final_price += price
        
        service_name = "sentuhan mendalam" if service_type == "bj" else "keintiman penuh"
        return f"✅ {service_name} ditambahkan! Total Rp{self.final_price:,}. Siap memulai kapan pun."
    
    def _add_to_history(self, event: str, detail: str) -> None:
        if not hasattr(self, 'service_history'):
            self.service_history = []
        self.service_history.append({
            'timestamp': time.time(),
            'event': event,
            'detail': detail,
            'phase': self.current_service_phase
        })
        if len(self.service_history) > 100:
            self.service_history.pop(0)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'boob_size': self.boob_size,
            'pijat_style': self.pijat_style,
            'pijat_belakang_done': self.pijat_belakang_done,
            'pijat_depan_done': self.pijat_depan_done,
            'hj_done': self.hj_done,
            'extra_service_booked': self.extra_service_booked,
            'extra_service_type': self.extra_service_type,
            'extra_service_price': self.extra_service_price,
            'current_service_phase': self.current_service_phase,
            'climax_count_mas': self.climax_count_mas,
            'climax_count_role': self.climax_count_role,
            'session_emotional_state': self.session_emotional_state
        })
        return data
    
    def from_dict(self, data: Dict) -> None:
        super().from_dict(data)
        self.boob_size = data.get('boob_size', '34B')
        self.pijat_style = data.get('pijat_style', 'lembut')
        self.pijat_belakang_done = data.get('pijat_belakang_done', False)
        self.pijat_depan_done = data.get('pijat_depan_done', False)
        self.hj_done = data.get('hj_done', False)
        self.extra_service_booked = data.get('extra_service_booked', False)
        self.extra_service_type = data.get('extra_service_type', None)
        self.extra_service_price = data.get('extra_service_price', 0)
        self.current_service_phase = data.get('current_service_phase', 'refleksi')
        self.climax_count_mas = data.get('climax_count_mas', 0)
        self.climax_count_role = data.get('climax_count_role', 0)
        self.session_emotional_state = data.get('session_emotional_state', 'relaxed')
        logger.info(f"📀 Pijat++ {self.name} loaded")


def create_aghnia_punjabi() -> PijatPlusPlusRole:
    """Create Aghnia Punjabi - lembut, kalem"""
    return PijatPlusPlusRole(
        name="Aghnia Punjabi",
        nickname="Aghnia",
        hijab=True,
        boob_size="34B",
        appearance="Tinggi 160cm, berat 48kg, kulit putih bersih, wajah bulat, mata bulat bening. Hijab pashmina warna pastel.",
        voice_style="lembut, menenangkan",
        personality="kalem, sabar, profesional, penuh perhatian",
        pijat_style="lembut, fokus di titik-titik saraf"
    )


def create_munira_agile() -> PijatPlusPlusRole:
    """Create Munira Agile - energik, hangat"""
    return PijatPlusPlusRole(
        name="Munira Agile",
        nickname="Munira",
        hijab=True,
        boob_size="36C",
        appearance="Tinggi 165cm, berat 52kg, kulit sawo matang, wajah oval, mata sipit manis. Hijab instan warna cerah.",
        voice_style="energik, ceria",
        personality="ceplas-ceplos, percaya diri, hangat",
        pijat_style="kuat, cepat, fokus di otot-otot tegang"
    )


__all__ = [
    'PijatPlusPlusRole',
    'create_aghnia_punjabi',
    'create_munira_agile'
]
