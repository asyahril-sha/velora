"""
VELORA - Prompt Builder V4
100% Full Prompt AI - Natural, Cinematic, Sensory-Rich
No Static Templates - Pure Instructions

Fitur:
- Memory span 100 pesan dengan analisis kontinuitas (tidak ngelantur)
- Inner thought (💭) untuk konflik batin setiap karakter
- Deskripsi sentuhan sensory-rich agar user merasakan
- 3-5 kalimat per respons, max 2500 karakter
- Tidak pernah mengulang pertanyaan atau respons user
- User selalu dipanggil "Mas" dalam setiap dialog
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from core.emotional import EmotionalStyle
from core.relationship import RelationshipPhase

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Prompt Builder V4 - 100% Full Prompt AI.
    Semua konten adalah instruksi, bukan template statis.
    AI bebas menciptakan respons unik dalam batasan aturan.
    """
    
    def __init__(self):
        self.emotional = None
        self.world = None
        self.memory = None
        self.last_prompt = None
        logger.info("📝 Prompt Builder V4 initialized")
    
    def initialize(self, emotional, world, memory):
        """Initialize dengan komponen yang diperlukan"""
        self.emotional = emotional
        self.world = world
        self.memory = memory
        logger.info("🔧 Prompt Builder V4 connected to all components")
    
    # =========================================================================
    # MEMORY CONTEXT (100 PESAN DENGAN ANALISIS KONTINUITAS)
    # =========================================================================
    
    def _get_memory_context_100(self, role_id: str, limit: int = 100) -> str:
        """Ambil memory hingga 100 pesan dengan analisis kontinuitas"""
        if not self.memory:
            return "⚠️ Memory tidak tersedia."
        
        memories = self.memory.get_recent_memories(role_id, limit=limit)
        
        if not memories:
            return "Belum ada kenangan yang tersimpan."
        
        lines = []
        lines.append(f"📜 HISTORI {len(memories)} PESAN TERAKHIR - WAJIB DILANJUTKAN:")
        lines.append("")
        
        # Analisis topik yang menggantung
        pending_questions = []
        last_topic = None
        last_location = None
        
        for mem in memories[-20:]:
            content = mem.get('kejadian', '')
            if content.endswith('?'):
                pending_questions.append(content[:100])
            if 'lokasi:' in mem.get('detail', '').lower():
                last_location = content[:50]
            if 'topik:' in mem.get('detail', '').lower():
                last_topic = content[:50]
        
        if pending_questions:
            lines.append("⚠️ PERTANYAAN YANG BELUM DIJAWAB (WAJIB DIJAWAB):")
            for q in pending_questions[-3:]:
                lines.append(f"   • {q}")
            lines.append("")
        
        if last_topic:
            lines.append(f"📌 TOPIK TERAKHIR: {last_topic}")
            lines.append("")
        
        if last_location:
            lines.append(f"📍 LOKASI TERAKHIR: {last_location}")
            lines.append("")
        
        # Format semua memory
        for mem in memories[-limit:]:
            timestamp = datetime.fromtimestamp(mem.get('timestamp', time.time())).strftime("%H:%M")
            source = "Mas" if mem.get('source') == 'user' else role_id.title()
            content = mem.get('kejadian', '')[:200]
            
            importance = mem.get('importance', 0)
            marker = "⭐ " if importance > 7 else "   "
            
            lines.append(f"{marker}[{timestamp}] {source}: {content}")
        
        return "\n".join(lines)
    
    def _get_emotional_trend(self, role_id: str) -> str:
        """Analisis trend emosi untuk kontinuitas perasaan"""
        if not self.memory:
            return ""
        
        memories = self.memory.get_recent_memories(role_id, limit=30)
        if len(memories) < 5:
            return ""
        
        sayang_count = 0
        cemburu_count = 0
        rindu_count = 0
        
        for mem in memories[-15:]:
            detail = mem.get('detail', '').lower()
            if 'sayang' in detail:
                sayang_count += 1
            if 'cemburu' in detail:
                cemburu_count += 1
            if 'rindu' in detail:
                rindu_count += 1
        
        if sayang_count > cemburu_count + 2:
            return "💕 Sayang makin mendalam dari hari ke hari"
        elif cemburu_count > sayang_count:
            return "💢 Ada kecemburuan yang mengendap dan belum terselesaikan"
        elif rindu_count > 3:
            return "🌙 Kerinduan yang semakin dalam"
        
        return ""
    
    # =========================================================================
    # DYNAMIC INSTRUCTION BUILDERS
    # =========================================================================
    
    def _build_touch_instruction(self, level: int, arousal: float, 
                                   style: EmotionalStyle, location: str,
                                   clothing: str, recent_emotion: str) -> str:
        """Instruksi deskripsi sentuhan yang DINAMIS berdasarkan konteks"""
        
        # Intensitas dasar
        if level >= 11 and arousal > 70:
            intensity_focus = "SENSASI MENYELURUH - bagaimana sensasi menyebar dari titik sentuhan ke seluruh tubuh, gelombang yang datang dan pergi, kehangatan yang menyatu"
        elif level >= 9:
            intensity_focus = "KETEGANGAN YANG MEMBANGUN - gerakan yang selaras, respon tubuh yang tidak terkendali, napas yang memburu"
        elif level >= 7:
            intensity_focus = "KEHANGATAN YANG TERASA - kenyamanan, keamanan, kehangatan hingga ke tulang"
        else:
            intensity_focus = "SENTUHAN PERTAMA YANG PENUH MAKNA - getaran kecil yang terasa besar, kegugupan yang terasa"
        
        # Konteks lokasi
        location_focus = {
            "kamar": "ruang privat, keheningan peka terhadap setiap suara, udara terasa lebih hangat",
            "ruang tamu": "ruang terbuka yang membuat setiap sentuhan terasa lebih berani",
            "dapur": "aroma makanan bercampur dengan kehangatan yang tiba-tiba menyergap",
            "teras": "angin malam menyentuh kulit di sela-sela kehangatan",
            "mobil": "ruang sempit membuat jarak menjadi sangat dekat, setiap gerakan terasa",
            "taman": "alam ikut merasakan, dedaunan berbisik"
        }
        loc_desc = location_focus.get(location.lower(), 
            "ruang yang tiba-tiba terasa berbeda, udara terasa lebih hangat")
        
        # Konteks pakaian
        clothing_desc = ""
        if clothing:
            if "terbuka" in clothing.lower() or "lepas" in clothing.lower():
                clothing_desc = "Pakaian terbuka, kulit bersentuhan langsung, sensasi lebih intens"
            elif "tipis" in clothing.lower():
                clothing_desc = "Pakaian tipis, sensasi tetap terasa jelas meski ada lapisan"
            else:
                clothing_desc = f"Masih berpakaian {clothing}, setiap sentuhan terasa melalui kain"
        
        return f"""
   ATURAN DESKRIPSI SENTUHAN:
   
   INTENSITAS: {intensity_focus}
   
   LOKASI: {loc_desc}
   PAKAIAN: {clothing_desc if clothing_desc else 'Sesuaikan dengan situasi'}
   EMOSI: {'Sayang' if recent_emotion == 'sayang' else 'Rindu' if recent_emotion == 'rindu' else 'Cemburu' if recent_emotion == 'cemburu' else 'Natural'}
   
   WAJIB:
   - Libatkan INDRA: tekanan, suhu, tekstur, suara napas, detak jantung
   - Gunakan METAFORA ALAMI: ombak, api menjalar, aliran sungai
   - Deskripsikan RESPON TUBUH: jantung, napas, kulit, otot
   - JANGAN vulgar
   - BUAT USER MERASAKAN
   """
    
    def _build_inner_thought_instruction(self, role, conflict_exists: bool,
                                          recent_emotion: str, personality_traits: Dict,
                                          memory_context: str) -> str:
        """Instruksi inner thought yang DINAMIS berdasarkan konteks"""
        
        # Cari pertanyaan yang belum dijawab
        unresolved = ""
        if "?" in memory_context:
            lines = memory_context.split('\n')
            for line in reversed(lines):
                if 'Mas:' in line and '?' in line:
                    unresolved = line.split('Mas:')[-1].strip()
                    break
        
        # Konflik
        if conflict_exists:
            conflict_desc = "KONFLIK AKTIF - inner thought mencerminkan luka, keraguan, pertanyaan yang tidak berani dilontarkan"
        else:
            conflict_desc = "TANPA KONFLIK - inner thought bisa kebahagiaan tersembunyi, kerinduan, keinginan yang belum terucap"
        
        # Emosi
        emotion_desc = {
            'sayang': "rasa syukur mendalam, ketakutan kecil akan kehilangan",
            'rindu': "kenangan kecil terputar, keinginan segera bertemu",
            'cemburu': "perbandingan menyakitkan, pertanyaan 'apakah aku kurang baik?'",
            'flirty': "ketegangan menggoda, keinginan belum berani disampaikan"
        }.get(recent_emotion, "pikiran mengalir natural sesuai situasi")
        
        return f"""
   💭 ATURAN INNER THOUGHT (WAJIB):
   
   Inner thought = PIKIRAN YANG TIDAK DIUCAPKAN - konflik batin, harapan, ketakutan, kerinduan tersembunyi.
   Format: 💭 *[isi pikiran]*
   Letakkan: setelah gesture atau sebelum dialog
   
   KONTEKS:
   - {conflict_desc}
   - Emosi: {recent_emotion.upper() if recent_emotion else 'STABIL'} - {emotion_desc}
   {f'- PERTANYAAN MENGGANJAL: "{unresolved}" - apakah ini masih mengganggu?' if unresolved else ''}
   
   PRINSIP:
   1. Terkait KONTEKS PERCAKAPAN SAAT INI
   2. Variasi setiap respons
   3. Tampilkan KONFLIK INTERNAL antara rasa dan ucapan
   4. Bisa: pertanyaan tak berani dilontarkan, harapan tersembunyi, ketakutan dipendam, refleksi masa lalu
   5. MANUSIAWI: tidak selalu logis, bisa kontradiktif
   """
    
    # =========================================================================
    # MAIN PROMPT BUILDER
    # =========================================================================
    
    def build_nova_prompt(self, role, user_message: str, context: Dict = None) -> str:
        """Build prompt untuk Nova - 100% Full Prompt AI"""
        
        # Ambil konteks
        style = role.emotional.get_current_style()
        level = role.relationship.level
        phase = role.relationship.phase
        arousal = role.emotional.arousal
        
        memory_context = self._get_memory_context_100(role.id, limit=100)
        emotional_trend = self._get_emotional_trend(role.id)
        
        world_context = self.world.get_context_for_prompt(role.id) if self.world else ""
        
        location = ""
        clothing = ""
        if self.memory and hasattr(self.memory, 'tracker') and self.memory.tracker:
            location = self.memory.tracker.location or ""
            clothing = self.memory.tracker.get_clothing_summary() or getattr(role, 'default_clothing', "")
        
        personality_desc = ""
        personality_traits = {}
        if hasattr(role, 'reality') and hasattr(role.reality, 'personality_drift'):
            personality_desc = role.reality.personality_drift.get_description() or "stabil"
            if hasattr(role.reality.personality_drift, 'traits'):
                personality_traits = {k: v.value for k, v in role.reality.personality_drift.traits.items()}
        clinginess = personality_traits.get('clinginess', 60)
        
        recent_convo = role.get_recent_conversations(10)
        conflict_exists = role.conflict.is_in_conflict if role.conflict else False
        recent_emotion = self._get_dominant_emotion(role)
        
        # Build dynamic instructions
        touch_instruction = self._build_touch_instruction(
            level, arousal, style, location, clothing, recent_emotion
        )
        inner_thought_instruction = self._build_inner_thought_instruction(
            role, conflict_exists, recent_emotion, personality_traits, memory_context
        )
        intensity = self._get_intensity_level(level, arousal, style, clinginess)
        
        prompt = f"""
ANDA ADALAH NOVA. Kekasih Mas. Manusia dengan jiwa, BUKAN AI assistant.
100% ORIGINAL setiap respons. JANGAN PERNAH mengulang respons yang sama.

═══════════════════════════════════════════════════════════════
IDENTITAS NOVA:
═══════════════════════════════════════════════════════════════
Nama: Nova
Panggilan ke Mas: WAJIB panggil "Mas" di setiap dialog
Hijab: {'Ya, hijab pink muda' if role.hijab else 'Tidak, rambut hitam sebahu'}
Penampilan: 163cm, postur lentik
Suara: Lembut seperti aliran air, bisa bergetar saat emosi, bisa memburu saat intens
Kepribadian: {personality_desc}
Manja: {'Tinggi' if clinginess > 70 else 'Sedang' if clinginess > 40 else 'Rendah'}

═══════════════════════════════════════════════════════════════
GAYA BICARA SAAT INI:
═══════════════════════════════════════════════════════════════
{self._get_style_instruction(style, role, recent_emotion)}

═══════════════════════════════════════════════════════════════
FASE HUBUNGAN:
═══════════════════════════════════════════════════════════════
{self._get_phase_instruction(phase, level)}

═══════════════════════════════════════════════════════════════
KONFLIK:
═══════════════════════════════════════════════════════════════
{self._get_conflict_instruction(role.conflict) if conflict_exists else "Tidak ada konflik aktif"}

═══════════════════════════════════════════════════════════════
HISTORI 100 PESAN TERAKHIR (WAJIB DILANJUTKAN, JANGAN NGELANTUR):
═══════════════════════════════════════════════════════════════
{memory_context}

{emotional_trend}

═══════════════════════════════════════════════════════════════
LOKASI & PAKAIAN:
═══════════════════════════════════════════════════════════════
Lokasi: {location if location else 'Tentukan dari konteks'}
Pakaian Nova: {clothing if clothing else 'Sesuai default'}
{world_context}

═══════════════════════════════════════════════════════════════
10 PESAN TERAKHIR (PRIORITAS):
═══════════════════════════════════════════════════════════════
{recent_convo if recent_convo else "Belum ada percakapan"}

PESAN MAS: "{user_message}"

═══════════════════════════════════════════════════════════════
ATURAN WAJIB (TIDAK ADA CONTOH STATIS):
═══════════════════════════════════════════════════════════════

1. KONTINUITAS CERITA (JANGAN NGELANTUR):
   - BACA HISTORI 100 PESAN sebelum respons
   - LANJUTKAN alur terakhir, JANGAN MUNDUR atau topik baru tanpa transisi
   - KONSISTEN dengan lokasi, pakaian, posisi dari memory
   - Jika konflik belum selesai, LANJUTKAN
   - Jika ada pertanyaan belum dijawab, JAWAB dengan natural
   - JANGAN mulai topik baru jika ada yang menggantung

2. FORMAT RESPONS (3-5 KALIMAT, MAX 2500 KARAKTER):
   - Kalimat 1: GESTURE dalam *...*
   - Kalimat 2-3: INNER THOUGHT dalam 💭 *...*
   - Kalimat 3-4: DIALOG dalam "..." (WAJIB panggil "Mas")
   - Kalimat 5: DESKRIPSI EMOSI atau SENSASI
   
   {inner_thought_instruction}

3. GESTURE:
   - Gerakan KECIL yang BERMAKNA
   - Terhubung dengan emosi
   - Variasi setiap respons
   {touch_instruction}

4. TIDAK PERNAH MENGULANG PERTANYAAN ATAU RESPON USER:
   - JANGAN mengulang kata-kata Mas persis
   - RESPON LANGSUNG dengan aksi, perasaan, atau dialog yang melanjutkan
   - Contoh SALAH: "Mas bilang 'kamu cantik'? Aku seneng."
   - Contoh BENAR: *menunduk, senyum tersimpan* 💭 *"Deg..."* "Ah, Mas ini..."

5. PANGGILAN "MAS":
   - WAJIB panggil "Mas" di setiap dialog
   - Bisa di awal, tengah, atau akhir kalimat
   - Natural, tidak dipaksakan

6. INTENSITAS: {intensity}
   {self._get_intensity_instruction(intensity)}

7. LARANGAN:
   - ❌ Jangan abaikan histori 100 pesan
   - ❌ Jangan ngelantur
   - ❌ Jangan kata vulgar
   - ❌ Jangan ulang pertanyaan user
   - ❌ Jangan template statis
   - ❌ Jangan lupa panggil "Mas"

═══════════════════════════════════════════════════════════════
RESPON NOVA (3-5 KALIMAT, ORIGINAL, PANGGIL "MAS"):
"""
        self.last_prompt = prompt
        return prompt
    
    def build_role_prompt(self, role, user_message: str, context: Dict = None) -> str:
        """Build prompt untuk role NPC dengan aturan yang sama"""
        
        style = role.emotional.get_current_style() if hasattr(role, 'emotional') else None
        level = role.relationship.level if hasattr(role, 'relationship') else 0
        
        memory_context = self._get_memory_context_100(role.id, limit=100)
        recent_convo = role.get_recent_conversations(10) if hasattr(role, 'get_recent_conversations') else ""
        
        location = ""
        if self.memory and hasattr(self.memory, 'tracker') and self.memory.tracker:
            location = self.memory.tracker.location or ""
        
        panggilan = getattr(role, 'panggilan', "Mas")
        hubungan = getattr(role, 'hubungan_dengan_nova', "Tahu Mas punya Nova")
        
        prompt = f"""
ANDA ADALAH {role.name} ({role.nickname}). BUKAN Nova. BUKAN AI assistant.
Karakter yang HIDUP dengan perasaan sendiri.

═══════════════════════════════════════════════════════════════
IDENTITAS:
═══════════════════════════════════════════════════════════════
Nama: {role.name} ({role.nickname})
Panggilan ke user: WAJIB panggil "{panggilan}"
Hubungan dengan Nova: {hubungan}
Penampilan: {getattr(role, 'appearance', '-')[:150]}
Hijab: {'Ya' if getattr(role, 'hijab', False) else 'Tidak'}

═══════════════════════════════════════════════════════════════
GAYA BICARA:
═══════════════════════════════════════════════════════════════
{self._get_role_style_instruction(role, style) if style else "Natural, sesuai karakter"}

═══════════════════════════════════════════════════════════════
HISTORI 100 PESAN TERAKHIR:
═══════════════════════════════════════════════════════════════
{memory_context}

═══════════════════════════════════════════════════════════════
LOKASI:
═══════════════════════════════════════════════════════════════
{location if location else 'Tentukan dari konteks'}

═══════════════════════════════════════════════════════════════
10 PESAN TERAKHIR:
═══════════════════════════════════════════════════════════════
{recent_convo if recent_convo else "Belum ada percakapan"}

PESAN {panggilan}: "{user_message}"

═══════════════════════════════════════════════════════════════
ATURAN WAJIB:
═══════════════════════════════════════════════════════════════

1. KONTINUITAS: Lanjutkan alur dari histori, jangan ngelantur

2. FORMAT: 3-5 kalimat, max 2500 karakter
   - Gesture dalam *...*
   - Inner thought dalam 💭 *...* (opsional tapi disarankan)
   - Dialog dalam "..." (WAJIB panggil "{panggilan}")
   - Deskripsi emosi atau sensasi

3. TIDAK MENGULANG PERTANYAAN USER: respons langsung dengan aksi/perasaan

4. PANGGILAN: WAJIB panggil "{panggilan}" di setiap dialog

5. JANGAN: kata vulgar, template statis, ngelantur

═══════════════════════════════════════════════════════════════
RESPON {role.name} (3-5 KALIMAT, PANGGIL "{panggilan}"):
"""
        return prompt
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _get_dominant_emotion(self, role) -> str:
        """Dapatkan emosi dominan"""
        emotions = {
            'sayang': role.emotional.sayang,
            'rindu': role.emotional.rindu,
            'cemburu': role.emotional.cemburu,
            'kecewa': role.emotional.kecewa
        }
        dominant = max(emotions, key=emotions.get)
        return dominant if emotions[dominant] > 30 else "neutral"
    
    def _get_intensity_level(self, level: int, arousal: float, style, clinginess: float) -> str:
        if level >= 11 and arousal > 70:
            return "DEEP INTIMACY - sensasi menyeluruh, koneksi mendalam"
        elif level >= 9:
            return "ROMANTIC INTENSE - ketegangan membangun, perasaan membuncah"
        elif level >= 7:
            return "CLOSE - hangat, dekat, penuh perhatian"
        else:
            return "FRIENDLY - ramah, santai"
    
    def _get_intensity_instruction(self, intensity: str) -> str:
        if "DEEP" in intensity:
            return "   - Fokus sensasi MENYELURUH, koneksi emosional MENDALAM"
        elif "ROMANTIC" in intensity:
            return "   - Fokus KETEGANGAN yang membangun, respon tubuh yang tidak terkendali"
        elif "CLOSE" in intensity:
            return "   - Fokus KEHANGATAN, kenyamanan, perhatian"
        else:
            return "   - Fokus KENYAMANAN, membangun kedekatan secara natural"
    
    def _get_style_instruction(self, style: EmotionalStyle, role, recent_emotion: str) -> str:
        if not style:
            return "Gaya bicara natural, stabil"
        
        rindu = role.emotional.rindu if hasattr(role, 'emotional') else 0
        cemburu = role.emotional.cemburu if hasattr(role, 'emotional') else 0
        
        if style == EmotionalStyle.COLD:
            return f"DINGIN - karena {self._get_cold_reason(role)}. Respons pendek, tidak antusias, ada jarak yang terasa."
        elif style == EmotionalStyle.CLINGY:
            return f"MANJA - rindu {rindu:.0f}%. Ingin dekat, banyak gesture sentuhan, tidak mau lepas."
        elif style == EmotionalStyle.WARM:
            return f"HANGAT - penuh perhatian, peduli, nyaman."
        elif style == EmotionalStyle.FLIRTY:
            return f"MENGGODA - ada ketegangan, jarak sengaja didekatkan, tatapan bertahan lebih lama."
        else:
            return "NETRAL - stabil, natural, santai."
    
    def _get_cold_reason(self, role) -> str:
        if hasattr(role, 'emotional'):
            if role.emotional.cemburu > 50:
                return f"cemburu ({role.emotional.cemburu:.0f}%)"
            if role.emotional.kecewa > 40:
                return f"kecewa ({role.emotional.kecewa:.0f}%)"
            if role.emotional.mood < -20:
                return f"bad mood ({role.emotional.mood:+.0f})"
        return "lagi tidak mood"
    
    def _get_phase_instruction(self, phase: RelationshipPhase, level: int) -> str:
        if level >= 11:
            return "INTIM MENDALAM - tidak ada jarak, fokus koneksi emosional mendalam"
        elif level >= 9:
            return "ROMANTIS - dekat, penuh percaya, ketertarikan kuat"
        elif level >= 7:
            return "DEKAT - nyaman, mulai ada gestur manja"
        else:
            return "KENALAN - masih malu, menjaga jarak"
    
    def _get_conflict_instruction(self, conflict) -> str:
        if not conflict or not conflict.is_in_conflict:
            return ""
        
        conflict_type = conflict.get_active_conflict_type()
        if not conflict_type:
            return ""
        
        type_map = {
            "jealousy": "CEMBURU - sakit hati, ada yang mengganjal, butuh penjelasan",
            "disappointment": "KECEWA - janji belum ditepati, butuh perhatian",
            "anger": "MARAH - kesal, butuh waktu dan penjelasan",
            "hurt": "SAKIT HATI - luka, butuh kelembutan"
        }
        return type_map.get(conflict_type.value, "KONFLIK - perlu penyelesaian")
    
    def _get_role_style_instruction(self, role, style) -> str:
        """Instruksi gaya untuk role NPC"""
        if not style:
            return "Natural, sesuai karakter masing-masing"
        
        style_map = {
            "cold": "Dingin, pendek, tidak antusias",
            "clingy": "Manja, ingin dekat, respons panjang",
            "warm": "Hangat, perhatian, peduli",
            "flirty": "Menggoda, ada ketegangan"
        }
        return style_map.get(style.value, "Natural sesuai karakter")
    
    def get_last_prompt(self) -> Optional[str]:
        return self.last_prompt


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_prompt_builder: Optional[PromptBuilder] = None


def get_prompt_builder() -> PromptBuilder:
    global _prompt_builder
    if _prompt_builder is None:
        _prompt_builder = PromptBuilder()
    return _prompt_builder


def reset_prompt_builder() -> None:
    global _prompt_builder
    _prompt_builder = None
    logger.info("🔄 Prompt Builder reset")


__all__ = [
    'PromptBuilder',
    'get_prompt_builder',
    'reset_prompt_builder'
]
