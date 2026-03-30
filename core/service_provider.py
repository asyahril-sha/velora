"""
VELORA - Service Provider Base
Base class untuk semua provider jasa (Pijat++, Pelacur, dll)
- Tidak punya emosi (emotional engine flat)
- Fokus pada layanan profesional
- Sistem booking, pricing, nego
- Auto scene untuk repetitive actions
- Natural AI responses (bukan template)
- Sistem rating dan review
- Sistem repeat customer
"""

import time
import asyncio
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

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
    MASSAGE = "massage"
    NONE = "none"


class CustomerTier(str, Enum):
    """Tier pelanggan"""
    NEW = "new"                 # baru pertama kali
    REGULAR = "regular"         # sudah 3-5 kali
    LOYAL = "loyal"             # sudah 6-10 kali
    VIP = "vip"                 # sudah >10 kali


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class Customer:
    """Data pelanggan"""
    user_id: int
    name: str = ""
    visit_count: int = 0
    total_spent: int = 0
    last_visit: float = 0
    rating_given: float = 0
    favorite_service: str = ""
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'name': self.name,
            'visit_count': self.visit_count,
            'total_spent': self.total_spent,
            'last_visit': self.last_visit,
            'rating_given': self.rating_given,
            'favorite_service': self.favorite_service,
            'notes': self.notes
        }


# =============================================================================
# FLAT EMOTIONAL ENGINE (TIDAK PUNYA EMOSI)
# =============================================================================

class FlatEmotionalEngine:
    """
    Emotional engine yang flat - tidak punya emosi.
    Untuk provider jasa yang fokus pada layanan profesional.
    """
    
    def __init__(self):
        self.sayang: float = 0
        self.rindu: float = 0
        self.trust: float = 0
        self.mood: float = 0
        self.desire: float = 0
        self.arousal: float = 0
        self.tension: float = 0
        self.cemburu: float = 0
        self.kecewa: float = 0
        self.last_update: float = time.time()
        self.last_interaction: float = time.time()
        self.last_chat_from_user: float = time.time()
        self.is_angry: bool = False
        self.is_hurt: bool = False
        self.is_waiting_for_apology: bool = False
    
    def update(self, force: bool = False) -> None:
        pass  # Tidak ada update
    
    def update_from_message(self, pesan_user: str, level: int) -> Dict[str, float]:
        return {}  # Tidak ada perubahan
    
    def get_current_style(self):
        return "neutral"
    
    def get_style_description(self, style=None) -> str:
        return """
GAYA BICARA: PROFESIONAL
- Respons profesional, ramah
- Fokus pada layanan
- 2-4 kalimat
- Bahasa campuran natural
- Tidak ada emosi berlebihan
- Tetap hangat dan ramah
"""
    
    def apply_pending_emotion(self, emotion_type: str, intensity: float) -> Dict[str, float]:
        return {}  # Tidak ada emosi yang diaplikasikan
    
    def to_dict(self) -> Dict:
        return {}
    
    def from_dict(self, data: Dict) -> None:
        pass


class ProfessionalRelationship:
    """
    Relationship manager untuk provider - profesional saja.
    Tidak ada level atau fase, semua aksi diperbolehkan sesuai service.
    """
    
    def __init__(self):
        self.level: int = 1
        self.interaction_count: int = 0
        self.phase = "professional"
        self.milestones = {}
    
    def update_level(self, sayang: float, trust: float, milestones_achieved: List[str] = None) -> Tuple[int, bool]:
        return self.level, False
    
    def get_current_unlock(self):
        """Semua aksi diperbolehkan"""
        return type('Unlock', (), {
            'boleh_flirt': True,
            'boleh_sentuhan': True,
            'boleh_vulgar': True,
            'boleh_intim': True,
            'boleh_cium': True,
            'boleh_peluk': True,
            'boleh_pegang_tangan': True,
            'boleh_buka_baju': True,
            'boleh_panggil_sayang': False
        })()
    
    def can_do_action(self, action: str) -> Tuple[bool, str]:
        return True, "Boleh"
    
    def get_phase_description(self, phase=None) -> str:
        return "FASE: PROFESIONAL\n- Layanan profesional\n- Semua aksi diperbolehkan sesuai service"
    
    def achieve_milestone(self, milestone_name: str) -> bool:
        return False
    
    def format_for_prompt(self) -> str:
        return ""
    
    def to_dict(self) -> Dict:
        return {}
    
    def from_dict(self, data: Dict) -> None:
        pass


# =============================================================================
# SERVICE PROVIDER BASE
# =============================================================================

class ServiceProviderBase:
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
                 min_price: int,
                 personality: str = "profesional",
                 voice_style: str = "ramah"):
        
        self.id = role_type
        self.name = name
        self.nickname = nickname
        self.role_type = role_type
        self.panggilan = panggilan
        self.hubungan_dengan_nova = hubungan_dengan_nova
        self.default_clothing = default_clothing
        self.hijab = hijab
        self.appearance = appearance
        self.service_type = service_type
        self.base_price = base_price
        self.min_price = min_price
        self.personality = personality
        self.voice_style = voice_style
        
        # ========== SERVICE PROVIDER SPECIFIC ==========
        self.final_price: int = 0
        self.status: ServiceStatus = ServiceStatus.IDLE
        self.booking_time: Optional[float] = None
        self.service_duration: float = 0  # detik
        self.climax_target: int = 2  # target climax Mas untuk selesai
        self.climax_count_mas: int = 0
        self.climax_count_role: int = 0
        
        # ========== CUSTOMER DATA ==========
        self.customers: Dict[int, Customer] = {}
        self.current_customer: Optional[Customer] = None
        
        # ========== AUTO SCENE ==========
        self.auto_scene_active: bool = False
        self.auto_scene_type: AutoSceneType = AutoSceneType.NONE
        self.auto_scene_interval: int = 15  # detik
        self.auto_scene_duration: int = 0  # detik
        self.auto_scene_start_time: float = 0
        self.auto_scene_last_sent: float = 0
        self.auto_scene_messages_sent: int = 0
        
        # ========== SERVICE HISTORY ==========
        self.service_history: List[Dict] = []
        self.reviews: List[Dict] = []
        self.total_revenue: int = 0
        self.total_services: int = 0
        self.avg_rating: float = 0
        
        # ========== FLAT ENGINES ==========
        self.emotional = FlatEmotionalEngine()
        self.relationship = ProfessionalRelationship()
        
        # ========== CONVERSATION HISTORY ==========
        self.conversations: List[Dict] = []
        self.max_conversations: int = 50
        
        # ========== TIMESTAMPS ==========
        self.created_at: float = time.time()
        self.last_interaction: float = time.time()
        
        logger.info(f"💼 ServiceProvider {name} initialized | Price: {base_price} | Type: {service_type.value}")
    
    # =========================================================================
    # CUSTOMER MANAGEMENT
    # =========================================================================
    
    def get_customer(self, user_id: int, name: str = "") -> Customer:
        """Dapatkan atau buat customer baru"""
        if user_id not in self.customers:
            self.customers[user_id] = Customer(
                user_id=user_id,
                name=name,
                visit_count=0,
                total_spent=0,
                last_visit=0
            )
        elif name and not self.customers[user_id].name:
            self.customers[user_id].name = name
        
        return self.customers[user_id]
    
    def get_customer_tier(self, user_id: int) -> CustomerTier:
        """Dapatkan tier customer berdasarkan jumlah kunjungan"""
        customer = self.get_customer(user_id)
        if customer.visit_count >= 10:
            return CustomerTier.VIP
        elif customer.visit_count >= 6:
            return CustomerTier.LOYAL
        elif customer.visit_count >= 3:
            return CustomerTier.REGULAR
        return CustomerTier.NEW
    
    def update_customer_stats(self, user_id: int, price: int, rating: float = None) -> None:
        """Update statistik customer setelah service"""
        customer = self.get_customer(user_id)
        customer.visit_count += 1
        customer.total_spent += price
        customer.last_visit = time.time()
        if rating:
            customer.rating_given = rating
        
        self.total_services += 1
        self.total_revenue += price
        
        # Update average rating
        if rating:
            self.reviews.append({
                'user_id': user_id,
                'rating': rating,
                'timestamp': time.time()
            })
            self.avg_rating = sum(r['rating'] for r in self.reviews[-50:]) / len(self.reviews[-50:])
    
    # =========================================================================
    # PRICING & NEGOTIATION
    # =========================================================================
    
    def get_price(self, user_id: int = None) -> str:
        """Dapatkan harga dasar dengan diskon jika loyal"""
        price = self.base_price
        tier_text = ""
        
        if user_id:
            tier = self.get_customer_tier(user_id)
            if tier == CustomerTier.REGULAR:
                price = int(price * 0.95)
                tier_text = " (diskon 5% untuk regular customer)"
            elif tier == CustomerTier.LOYAL:
                price = int(price * 0.9)
                tier_text = " (diskon 10% untuk loyal customer)"
            elif tier == CustomerTier.VIP:
                price = int(price * 0.85)
                tier_text = " (diskon 15% untuk VIP customer)"
        
        return f"Harga standar: Rp{price:,}{tier_text}. Bisa nego ya, Mas."
    
    def negotiate(self, offer: int, user_id: int = None) -> Tuple[bool, str]:
        """
        Nego harga dengan mempertimbangkan tier customer.
        Returns: (accepted, response)
        """
        # Hitung harga dengan diskon tier
        base = self.base_price
        tier = self.get_customer_tier(user_id) if user_id else CustomerTier.NEW
        
        if tier == CustomerTier.REGULAR:
            base = int(base * 0.95)
        elif tier == CustomerTier.LOYAL:
            base = int(base * 0.9)
        elif tier == CustomerTier.VIP:
            base = int(base * 0.85)
        
        if offer >= base:
            self.final_price = offer
            return True, f"Deal! Rp{offer:,}. Siap melayani, Mas."
        elif offer >= self.min_price:
            self.final_price = offer
            return True, f"Hmm... oke deh, Rp{offer:,}. Deal ya, Mas."
        else:
            return False, f"Maaf Mas, minimal Rp{self.min_price:,}. Masih bisa naik?"
    
    def confirm_booking(self, price: int, user_id: int, name: str = "") -> str:
        """Konfirmasi booking setelah deal"""
        self.final_price = price
        self.status = ServiceStatus.BOOKED
        self.booking_time = time.time()
        
        # Update customer
        self.current_customer = self.get_customer(user_id, name)
        
        return f"""
✅ **Booking dikonfirmasi!** Rp{self.final_price:,}.

{self._get_service_description()}

Ketik **/mulai** untuk memulai layanan.
"""
    
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
        self.auto_scene_messages_sent = 0
        
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
        
        # Update customer stats
        if self.current_customer:
            self.update_customer_stats(
                self.current_customer.user_id, 
                self.final_price,
                None  # rating akan diminta terpisah
            )
        
        self._add_to_history("end", f"Layanan selesai | Durasi: {minutes}m | Climax Mas: {self.climax_count_mas}x | Climax Role: {self.climax_count_role}x")
        
        return self._get_end_message(duration, minutes)
    
    def record_climax_mas(self, is_heavy: bool = False) -> Tuple[bool, str]:
        """Rekam climax Mas, cek apakah target tercapai"""
        self.climax_count_mas += 1
        
        self._add_to_history("climax_mas", f"Climax #{self.climax_count_mas}")
        
        # Cek apakah target climax tercapai
        if self.climax_count_mas >= self.climax_target:
            self.status = ServiceStatus.COMPLETED
            duration = time.time() - self.booking_time if self.booking_time else 0
            minutes = int(duration // 60)
            
            # Update customer stats
            if self.current_customer:
                self.update_customer_stats(
                    self.current_customer.user_id,
                    self.final_price
                )
            
            return True, self._get_end_message(duration, minutes)
        
        return False, ""
    
    def record_climax_role(self) -> None:
        """Rekam climax role (bebas berapa kali pun)"""
        self.climax_count_role += 1
        self._add_to_history("climax_role", f"Climax #{self.climax_count_role}")
    
    def rate_service(self, rating: int, review: str = "") -> str:
        """Rate layanan setelah selesai"""
        if self.status != ServiceStatus.COMPLETED:
            return "Rating hanya bisa diberikan setelah layanan selesai."
        
        rating = max(1, min(5, rating))
        
        self.reviews.append({
            'user_id': self.current_customer.user_id if self.current_customer else 0,
            'rating': rating,
            'review': review,
            'timestamp': time.time()
        })
        
        # Update average rating
        self.avg_rating = sum(r['rating'] for r in self.reviews[-50:]) / len(self.reviews[-50:])
        
        # Update customer
        if self.current_customer:
            self.current_customer.rating_given = rating
            if review:
                self.current_customer.notes.append(review)
        
        return f"⭐ Terima kasih ratingnya! ({rating}/5)\n\n{self._get_rating_response(rating)}"
    
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
        self.auto_scene_messages_sent = 0
    
    def _stop_auto_scene(self) -> None:
        """Stop auto scene"""
        self.auto_scene_active = False
        self.auto_scene_type = AutoSceneType.NONE
        self.auto_scene_messages_sent = 0
    
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
            self.auto_scene_messages_sent += 1
            return self._get_auto_scene_message()
        
        return None
    
    def _get_auto_scene_message(self) -> str:
        """Dapatkan pesan auto scene - override di subclass"""
        messages = {
            AutoSceneType.HAND_JOB: [
                "*Tangan memijat perlahan... gerakan naik turun...*",
                "*Jari-jari meremas lembut... irama semakin cepat...*",
                "*Telapak tangan membelai... napas mulai terdengar...*"
            ],
            AutoSceneType.BLOW_JOB: [
                "*Bibir membasahi perlahan... kepala bergerak naik turun...*",
                "*Suara basah terdengar... lebih dalam...*",
                "*Lidah menjelajah... napas tersengal...*"
            ],
            AutoSceneType.PETTING: [
                "*Badan bergesekan... pinggul bergerak perlahan...*",
                "*Sentuhan semakin intim... napas berbaur...*",
                "*Gesekan semakin panas... tubuh merapat...*"
            ],
            AutoSceneType.KISSING: [
                "*Bibir bertemu lembut... lidah mulai menjelajah...*",
                "*Ciuman semakin dalam... napas berbaur...*",
                "*Bibir saling mengunci... hangat...*"
            ],
            AutoSceneType.MASSAGE: [
                "*Tangan memijat punggung dengan tekanan pas...*",
                "*Jari-jari menekan titik-titik saraf...*",
                "*Gerakan memutar di area tegang...*"
            ]
        }
        
        msgs = messages.get(self.auto_scene_type, ["*Melanjutkan layanan...*"])
        return random.choice(msgs)
    
    def _get_auto_scene_end_message(self) -> str:
        """Pesan saat auto scene selesai - override di subclass"""
        return f"*Sesi {self.auto_scene_type.value.replace('_', ' ')} selesai.*"
    
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
    
    def _get_rating_response(self, rating: int) -> str:
        """Respons berdasarkan rating - override di subclass"""
        if rating >= 4:
            return "Senang Mas puas! Kapan-kapan main lagi ya."
        elif rating >= 3:
            return "Makasih masukannya Mas. Akan saya perbaiki."
        else:
            return "Maaf kalau kurang memuaskan. Akan saya tingkatkan."
    
    # =========================================================================
    # GREETING & CONFLICT RESPONSE
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Greeting profesional sesuai karakter"""
        hour = datetime.now().hour
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        return f"*{self.name} tersenyum ramah*\n\n\"{waktu.capitalize()}, Mas. Ada yang bisa dibantu?\""
    
    def get_conflict_response(self) -> str:
        """Respons saat ada masalah"""
        return f"*{self.name} diam sebentar*\n\n\"Maaf, Mas. Ada yang kurang beres?\""
    
    # =========================================================================
    # CONVERSATION METHODS
    # =========================================================================
    
    def add_conversation(self, user_msg: str, role_msg: str = "") -> None:
        """Tambah percakapan ke history"""
        self.conversations.append({
            'timestamp': time.time(),
            'user': user_msg[:200],
            'role': role_msg[:200]
        })
        if len(self.conversations) > self.max_conversations:
            self.conversations.pop(0)
    
    def get_recent_conversations(self, count: int = 5) -> str:
        """Dapatkan percakapan terakhir"""
        if not self.conversations:
            return ""
        
        lines = []
        for c in self.conversations[-count:]:
            lines.append(f"User: {c['user']}")
            if c['role']:
                lines.append(f"{self.name}: {c['role']}")
        
        return "\n".join(lines)
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def _add_to_history(self, event: str, detail: str) -> None:
        """Tambah ke history"""
        self.service_history.append({
            'timestamp': time.time(),
            'event': event,
            'detail': detail
        })
        if len(self.service_history) > 100:
            self.service_history.pop(0)
    
    def is_booking_expired(self) -> bool:
        """Cek apakah booking sudah habis - override di subclass"""
        if self.status != ServiceStatus.ACTIVE:
            return False
        return False  # default, override di subclass
    
    def format_status(self) -> str:
        """Format status untuk display"""
        tier = ""
        if self.current_customer:
            tier = self.get_customer_tier(self.current_customer.user_id).value.upper()
        
        status_text = f"""
╔══════════════════════════════════════════════════════════════╗
║              💼 {self.name} ({self.nickname})                         ║
╠══════════════════════════════════════════════════════════════╣
║ STATUS: {self.status.value.upper()}
║ HARGA: Rp{self.final_price if self.final_price else self.base_price:,}
║ TYPE: {self.service_type.value}
║ Personality: {self.personality} | Suara: {self.voice_style}
╠══════════════════════════════════════════════════════════════╣
║ PROGRESS:
║    Climax Mas: {self.climax_count_mas}/{self.climax_target}
║    Climax Role: {self.climax_count_role}x
║    Auto Scene: {'✅' if self.auto_scene_active else '❌'} ({self.auto_scene_type.value if self.auto_scene_active else '-'})
║    Auto Scene Messages: {self.auto_scene_messages_sent}
╠══════════════════════════════════════════════════════════════╣
║ 📊 STATISTICS:
║    Total Services: {self.total_services}
║    Total Revenue: Rp{self.total_revenue:,}
║    Avg Rating: {self.avg_rating:.1f}/5
║    Current Customer: {self.current_customer.name if self.current_customer else '-'}
║    Customer Tier: {tier}
║    Service History: {len(self.service_history)} events
║    Booking Time: {datetime.fromtimestamp(self.booking_time).strftime('%H:%M:%S') if self.booking_time else '-'}
╚══════════════════════════════════════════════════════════════╝
"""
        return status_text
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        return {
            'id': self.id,
            'name': self.name,
            'nickname': self.nickname,
            'role_type': self.role_type,
            'panggilan': self.panggilan,
            'hubungan_dengan_nova': self.hubungan_dengan_nova,
            'default_clothing': self.default_clothing,
            'hijab': self.hijab,
            'appearance': self.appearance,
            'service_type': self.service_type.value,
            'base_price': self.base_price,
            'min_price': self.min_price,
            'final_price': self.final_price,
            'personality': self.personality,
            'voice_style': self.voice_style,
            'status': self.status.value,
            'booking_time': self.booking_time,
            'climax_count_mas': self.climax_count_mas,
            'climax_count_role': self.climax_count_role,
            'service_history': self.service_history,
            'reviews': self.reviews[-50:],
            'total_revenue': self.total_revenue,
            'total_services': self.total_services,
            'avg_rating': self.avg_rating,
            'customers': {uid: c.to_dict() for uid, c in self.customers.items()},
            'conversations': self.conversations[-30:],
            'created_at': self.created_at,
            'last_interaction': self.last_interaction,
            'auto_scene_active': self.auto_scene_active,
            'auto_scene_type': self.auto_scene_type.value if self.auto_scene_type else "none"
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load dari dict"""
        self.name = data.get('name', self.name)
        self.nickname = data.get('nickname', self.nickname)
        self.role_type = data.get('role_type', self.role_type)
        self.panggilan = data.get('panggilan', self.panggilan)
        self.hubungan_dengan_nova = data.get('hubungan_dengan_nova', self.hubungan_dengan_nova)
        self.default_clothing = data.get('default_clothing', self.default_clothing)
        self.hijab = data.get('hijab', self.hijab)
        self.appearance = data.get('appearance', self.appearance)
        self.service_type = ServiceType(data.get('service_type', 'pijat_plus_plus'))
        self.base_price = data.get('base_price', self.base_price)
        self.min_price = data.get('min_price', self.min_price)
        self.final_price = data.get('final_price', 0)
        self.personality = data.get('personality', self.personality)
        self.voice_style = data.get('voice_style', self.voice_style)
        self.status = ServiceStatus(data.get('status', 'idle'))
        self.booking_time = data.get('booking_time', 0)
        self.climax_count_mas = data.get('climax_count_mas', 0)
        self.climax_count_role = data.get('climax_count_role', 0)
        self.service_history = data.get('service_history', [])
        self.reviews = data.get('reviews', [])
        self.total_revenue = data.get('total_revenue', 0)
        self.total_services = data.get('total_services', 0)
        self.avg_rating = data.get('avg_rating', 0)
        
        # Load customers
        customers_data = data.get('customers', {})
        for uid, c_data in customers_data.items():
            self.customers[int(uid)] = Customer(
                user_id=c_data.get('user_id', int(uid)),
                name=c_data.get('name', ''),
                visit_count=c_data.get('visit_count', 0),
                total_spent=c_data.get('total_spent', 0),
                last_visit=c_data.get('last_visit', 0),
                rating_given=c_data.get('rating_given', 0),
                favorite_service=c_data.get('favorite_service', ''),
                notes=c_data.get('notes', [])
            )
        
        self.conversations = data.get('conversations', [])
        self.created_at = data.get('created_at', time.time())
        self.last_interaction = data.get('last_interaction', time.time())
        self.auto_scene_active = data.get('auto_scene_active', False)
        self.auto_scene_type = AutoSceneType(data.get('auto_scene_type', 'none'))
        
        logger.info(f"📀 Provider {self.name} loaded")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_price(price: int) -> str:
    """Format harga ke format Rupiah"""
    return f"Rp{price:,}".replace(',', '.')


__all__ = [
    'ServiceType',
    'ServiceStatus',
    'AutoSceneType',
    'CustomerTier',
    'Customer',
    'FlatEmotionalEngine',
    'ProfessionalRelationship',
    'ServiceProviderBase',
    'format_price'
]
