"""
VELORA - Command Handlers
Semua handler untuk command Telegram bot.
- Command handlers (start, help, nova, status, flashback, roleplay, pindah, role, dll)
- User mode tracking
- Role switching
- Session management
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from config import get_settings
from core.orchestrator import get_orchestrator
from core.world import get_world_state
from core.memory import get_memory_manager
from roles.manager import get_role_manager
from worker.background import get_worker
from telegram.helpers import escape_markdown


logger = logging.getLogger(__name__)

# =============================================================================
# HELPER - SAFE REPLY
# =============================================================================

def safe_markdown(text: str) -> str:
    """Escape text for Telegram MarkdownV2"""
    if not text:
        return ""
    return escape_markdown(text, version=2)


async def safe_reply(update: Update, text: str, parse_mode: str = "MarkdownV2"):
    """Safe reply with markdown escape"""
    if not text:
        return
    try:
        safe_text = escape_markdown(text, version=2)
        await update.message.reply_text(safe_text, parse_mode=parse_mode)
    except Exception as e:
        logger.warning(f"Markdown error, sending plain: {e}")
        await update.message.reply_text(text)
        
# =============================================================================
# USER MODE TRACKING
# =============================================================================

_user_modes: Dict[int, Dict] = {}


def get_user_mode(user_id: int) -> str:
    """Dapatkan mode user saat ini"""
    return _user_modes.get(user_id, {}).get("mode", "chat")


def set_user_mode(user_id: int, mode: str, active_role: Optional[str] = None):
    """Set mode user"""
    _user_modes[user_id] = {"mode": mode, "active_role": active_role}
    logger.info(f"👤 User {user_id} mode set to: {mode} | active_role={active_role}")


def get_active_role(user_id: int) -> Optional[str]:
    """Dapatkan role aktif user"""
    return _user_modes.get(user_id, {}).get("active_role")


def clear_user_mode(user_id: int):
    """Clear mode user (kembali ke chat normal)"""
    if user_id in _user_modes:
        del _user_modes[user_id]
    logger.info(f"👤 User {user_id} mode cleared")


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /start"""
    if not update or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    settings = get_settings()
    
    logger.info(f"📨 /start from user {user_id}")
    
    if user_id != settings.admin_id:
        await update.message.reply_text(
            "💜 Halo! Bot ini untuk Mas.\n\nKirim /help untuk melihat perintah."
        )
        return
    
    clear_user_mode(user_id)
    
    world = get_world_state()
    memory = get_memory_manager()
    
    text = f"""💜 VELORA - AI Drama Engine 💜

Selamat datang, Mas.

🌍 Drama Level: {world.drama_level:.0f}%
📝 Memory Events: {memory.total_events}

Gunakan /help untuk melihat semua perintah.
Ketik /nova untuk memanggil Nova."""
    
    await safe_reply(update, text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /help"""
    if not update or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        await update.message.reply_text("Bot ini untuk Mas. 💜")
        return
    
    help_text = """
📖 BANTUAN VELORA

Command Utama:
• /nova - Memanggil Nova
• /status - Status lengkap VELORA
• /flashback - Flashback momen indah

Roleplay:
• /roleplay - Mode roleplay dengan Nova
• /role - Lihat daftar role
• /role <id> - Switch ke role tertentu
• /statusrole - Status role aktif
• /batal - Kembali ke Nova

Lokasi:
• /pindah <tempat> - Pindah lokasi

Sesi:
• /pause - Hentikan sesi sementara
• /resume - Lanjutkan sesi
• /batal - Batalkan sesi

System:
• /backup - Backup manual database
• /stats - Statistik sistem
• /help - Bantuan ini

Role yang Tersedia:
• nova - Nova (kekasih)
• ipar - Dietha (adik ipar)
• teman_kantor - Ipeh (teman kantor)
• pelakor - Wid (pelakor)
• istri_orang - Sika (istri orang)
• pijat_aghnia - Aghnia (pijat++)
• pijat_munira - Munira (pijat++)
• pelacur_davina - Davina (pelacur)
• pelacur_sallsa - Sallsa (pelacur)

Gunakan /role <id> untuk memanggil role tertentu.
"""
    await safe_reply(update, help_text)


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nova - Panggil Nova"""
    if not update or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    clear_user_mode(user_id)
    set_user_mode(user_id, "chat")
    
    # ========== TAMBAHKAN UPDATE ACTIVE SESSION ==========
    orchestrator = await get_orchestrator()
    orchestrator.active_sessions[user_id] = "nova"
    # ====================================================
    
    role_manager = get_role_manager()
    
    if not role_manager:
        await update.message.reply_text("Role manager error.")
        return
    
    response = role_manager.switch_role("nova", user_id)
    
    worker = get_worker()
    if worker:
        worker.update_activity(user_id)
    
    await safe_reply(update, response)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /status - Status lengkap VELORA"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    # Dapatkan semua status
    world = get_world_state()
    memory = get_memory_manager()
    worker = get_worker()
    orchestrator = await get_orchestrator()
    role_manager = get_role_manager()
    
    active_role = get_active_role(user_id)
    active_role_name = active_role if active_role else "Nova"
    
    status_text = f"""
╔══════════════════════════════════════════════════════════════╗
║                    💜 VELORA STATUS                          ║
╠══════════════════════════════════════════════════════════════╣
║ ACTIVE ROLE: {active_role_name.upper()}
║ MODE: {get_user_mode(user_id).upper()}
╠══════════════════════════════════════════════════════════════╣
{world.format_status() if world else ''}
{worker.format_status() if worker else ''}
╠══════════════════════════════════════════════════════════════╣
║ MEMORY STATS:
║   Total Events: {memory.total_events}
║   Short-term: {len(memory.short_term)}/50
║   Global Timeline: {len(memory.global_timeline)}
╠══════════════════════════════════════════════════════════════╣
║ ORCHESTRATOR STATS:
{orchestrator.format_status() if orchestrator else ''}
╚══════════════════════════════════════════════════════════════╝
"""
    await update.message.reply_text(status_text, parse_mode="Markdown")


async def flashback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /flashback - Flashback momen indah"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    # Cek apakah Nova aktif
    active_role = get_active_role(user_id)
    if active_role and active_role != "nova":
        await update.message.reply_text(
            "💜 Flashback hanya bisa dilakukan saat bersama Nova.\n\n"
            "Ketik /batal untuk kembali ke Nova, atau /nova untuk memanggil Nova."
        )
        return
    
    # Dapatkan Nova role
    role_manager = get_role_manager()
    nova = role_manager.get_role("nova")
    
    if nova and hasattr(nova, 'get_flashback'):
        flashback = nova.get_flashback()
        await update.message.reply_text(flashback, parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "💜 *Flashback...*\n\n"
            "Mas, inget gak waktu pertama kali kita makan bakso bareng?\n\n"
            "*Nova tersenyum sendiri mengingatnya*",
            parse_mode="Markdown"
        )
    
    # Update activity
    worker = get_worker()
    worker.update_activity(user_id)


async def roleplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /roleplay - Mode roleplay dengan Nova"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode == "paused":
        await update.message.reply_text(
            "⏸️ Sesi sedang di-pause.\n\n"
            "Ketik /resume untuk melanjutkan, atau /batal untuk mulai baru."
        )
        return
    
    clear_user_mode(user_id)
    set_user_mode(user_id, "roleplay")
    
    # Switch ke Nova dan mulai roleplay
    role_manager = get_role_manager()
    response = role_manager.switch_role("nova", user_id)
    
    # Update activity
    worker = get_worker()
    worker.update_activity(user_id)
    
    await update.message.reply_text(
        f"🎭 **Mode Roleplay Aktif**\n\n{response}",
        parse_mode="Markdown"
    )


async def pindah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pindah - Pindah lokasi"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        await update.message.reply_text(
            "📍 Gunakan: `/pindah <tempat>`\n\n"
            "Tempat yang tersedia:\n"
            "• kamar, ruang tamu, dapur, teras\n"
            "• apartemen, mobil\n"
            "• pantai, hutan, toilet mall, bioskop, taman",
            parse_mode="Markdown"
        )
        return
    
    tujuan = " ".join(args)
    
    # Dapatkan orchestrator dan world
    orchestrator = await get_orchestrator()
    world = get_world_state()
    
    # Pindah lokasi (melalui memory)
    memory = get_memory_manager()
    if memory.tracker:
        # Update lokasi di tracker
        memory.tracker.location = tujuan
        memory.tracker.location_detail = tujuan
        
        # Catat ke timeline
        memory.add_event(
            kejadian=f"Pindah ke {tujuan}",
            detail=f"User pindah lokasi",
            source="user",
            role_id="nova",
            drama_impact=0
        )
        
        # Simpan ke location visits
        from memory.persistent import get_persistent
        persistent = await get_persistent()
        await persistent.save_location_visit(tujuan, tujuan)
        
        # Update activity
        worker = get_worker()
        worker.update_activity(user_id)
        
        await update.message.reply_text(
            f"📍 **Pindah ke {tujuan}**\n\n"
            f"*{memory.tracker.location_detail}*\n\n"
            f"🌍 Drama Level: {world.drama_level:.0f}%",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"📍 Pindah ke {tujuan}.")


async def role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /role - List role atau switch ke role tertentu"""
    if not update or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    role_manager = get_role_manager()
    if not role_manager:
        await update.message.reply_text("Role manager error.")
        return
    
    args = context.args
    
    if not args:
        roles = role_manager.get_all_roles()
        lines = ["📋 DAFTAR ROLE VELORA", ""]
        
        main_roles = [r for r in roles if r['role_type'] in ['nova', 'ipar', 'teman_kantor', 'pelakor', 'istri_orang']]
        provider_roles = [r for r in roles if r['role_type'] in ['pijat_plus_plus', 'pelacur']]
        
        if main_roles:
            lines.append("MAIN ROLES:")
            for r in main_roles:
                lines.append(f"• /role {r['id']} - {r['nama']} (Level {r['level']})")
            lines.append("")
        
        if provider_roles:
            lines.append("PROVIDER:")
            for r in provider_roles:
                hijab_text = "hijab" if r['hijab'] else "tanpa hijab"
                lines.append(f"• /role {r['id']} - {r['nama']} ({r['boob_size']}, {hijab_text})")
        
        lines.append("")
        lines.append("Ketik /batal untuk kembali ke Nova.")
        
        await update.message.reply_text("\n".join(lines))
        return
    
    role_id = args[0].lower()
    
    role = role_manager.get_role(role_id)
    if not role:
        await update.message.reply_text(f"Role '{role_id}' tidak ditemukan.")
        return
    
    clear_user_mode(user_id)
    set_user_mode(user_id, "role", role_id)
    
    # ========== TAMBAHKAN UPDATE ACTIVE SESSION ==========
    orchestrator = await get_orchestrator()
    orchestrator.active_sessions[user_id] = role_id
    # ====================================================
    
    response = role_manager.switch_role(role_id, user_id)
    
    worker = get_worker()
    if worker:
        worker.update_activity(user_id)
    
    # Kirim dengan fallback jika Markdown error
    try:
        await safe_reply(update, response)
    except Exception as e:
        logger.warning(f"Error sending response for role {role_id}: {e}")
        await update.message.reply_text(response)


async def statusrole_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /statusrole - Status role aktif"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != "role":
        await update.message.reply_text(
            "💜 Tidak ada role yang sedang aktif.\n\n"
            "Gunakan `/role` untuk melihat daftar role, atau `/nova` untuk memanggil Nova.",
            parse_mode="Markdown"
        )
        return
    
    active_role_id = get_active_role(user_id)
    if not active_role_id:
        await update.message.reply_text("Tidak ada role aktif.")
        return
    
    role_manager = get_role_manager()
    role = role_manager.get_role(active_role_id)
    
    if not role:
        await update.message.reply_text("Role tidak ditemukan.")
        return
    
    status = role.format_status()
    await update.message.reply_text(status, parse_mode="Markdown")


async def back_to_nova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /batal - Kembali ke Nova"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    clear_user_mode(user_id)
    
    # Reset orchestrator session
    orchestrator = await get_orchestrator()
    orchestrator.active_sessions.pop(user_id, None)  # Hapus active session
    orchestrator.clear_session(user_id)               # Clear session lama
    
    # Switch ke Nova
    role_manager = get_role_manager()
    response = role_manager.switch_role("nova", user_id)
    
    # Update activity
    worker = get_worker()
    worker.update_activity(user_id)
    
    await update.message.reply_text(response, parse_mode="Markdown")


async def pause_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pause - Hentikan sesi sementara"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    current_mode = get_user_mode(user_id)
    if current_mode == "paused":
        await update.message.reply_text("💜 Sesi sudah dalam keadaan pause.")
        return
    
    set_user_mode(user_id, "paused")
    
    # Save state menggunakan method yang tersedia
    try:
        from memory.persistent import get_persistent
        persistent = await get_persistent()
        
        # Dapatkan semua engine
        from core.emotional import get_emotional_engine
        from core.relationship import get_relationship_manager
        from core.conflict import get_conflict_engine
        from core.memory import get_memory_manager
        from core.world import get_world_state
        from roles.manager import get_role_manager  # <-- PERBAIKI IMPORT
        
        emo = get_emotional_engine()
        rel = get_relationship_manager()
        conflict = get_conflict_engine()
        memory = get_memory_manager()
        world = get_world_state()
        role_manager = get_role_manager()
        
        # 1. Save world state (method ini ada di persistent.py)
        await persistent.save_world_state(world)
        
        # 2. Save role states (method ini ada di role_manager)
        await role_manager.save_all(persistent)
        
        # 3. Save emotional, relationship, conflict via set_state
        import json
        await persistent.set_state("emotional_engine", json.dumps(emo.to_dict()))
        await persistent.set_state("relationship_manager", json.dumps(rel.to_dict()))
        await persistent.set_state("conflict_engine", json.dumps(conflict.to_dict()))
        await persistent.set_state("memory_manager", json.dumps(memory.to_dict()))
        
        # 4. Simpan juga role flags dan conversation terakhir
        for role_id, role in role_manager.roles.items():
            await persistent.set_state(f"role_{role_id}_conversations", json.dumps(role.conversations[-20:]))
        
        logger.info(f"💾 Session paused for user {user_id}, all states saved")
        
    except ImportError as e:
        logger.error(f"Import error during pause: {e}")
        await update.message.reply_text(
            "❌ **Error: Module tidak ditemukan.**\n\n"
            "Pastikan semua file sudah lengkap.",
            parse_mode="Markdown"
        )
        return
    except Exception as e:
        logger.error(f"Error saving state during pause: {e}")
        await update.message.reply_text(
            "⚠️ **Gagal menyimpan sesi.**\n\n"
            f"Error: {str(e)[:100]}\n\n"
            "Progress mungkin tidak tersimpan sepenuhnya.",
            parse_mode="Markdown"
        )
        return
    
    await update.message.reply_text(
        "⏸️ **Sesi Dihentikan Sementara**\n\n"
        "Semua progress tersimpan.\n"
        "Ketik **/resume** untuk melanjutkan.\n"
        "Ketik **/batal** untuk memulai baru.",
        parse_mode="Markdown"
    )


async def resume_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /resume - Lanjutkan sesi"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    current_mode = get_user_mode(user_id)
    if current_mode != "paused":
        await update.message.reply_text("💜 Tidak ada sesi yang di-pause.")
        return
    
    # Load state yang tersimpan
    try:
        from memory.persistent import get_persistent
        from core.emotional import get_emotional_engine
        from core.relationship import get_relationship_manager
        from core.conflict import get_conflict_engine
        from core.memory import get_memory_manager
        from core.world import get_world_state
        from roles.manager import get_role_manager
        import json
        
        persistent = await get_persistent()
        
        # Load emotional engine
        emo_data = await persistent.get_state("emotional_engine")
        if emo_data:
            emo = get_emotional_engine()
            emo.from_dict(json.loads(emo_data))
        
        # Load relationship manager
        rel_data = await persistent.get_state("relationship_manager")
        if rel_data:
            rel = get_relationship_manager()
            rel.from_dict(json.loads(rel_data))
        
        # Load conflict engine
        conflict_data = await persistent.get_state("conflict_engine")
        if conflict_data:
            conflict = get_conflict_engine()
            conflict.from_dict(json.loads(conflict_data))
        
        # Load memory manager
        memory_data = await persistent.get_state("memory_manager")
        if memory_data:
            memory = get_memory_manager()
            memory.from_dict(json.loads(memory_data), None, get_world_state())
        
        # Load world state
        world = get_world_state()
        await persistent.load_world_state(world)
        
        # Load role states
        role_manager = get_role_manager()
        await role_manager.load_all(persistent)
        
        logger.info(f"💾 Session resumed for user {user_id}, states loaded")
        
    except Exception as e:
        logger.error(f"Error loading state during resume: {e}")
        await update.message.reply_text(
            "⚠️ **Gagal memuat sesi.**\n\n"
            "Memulai sesi baru.",
            parse_mode="Markdown"
        )
    
    clear_user_mode(user_id)
    
    # Update activity
    worker = get_worker()
    worker.update_activity(user_id)
    
    await update.message.reply_text(
        "▶️ **Sesi Dilanjutkan!**\n\n"
        "Ketik **/roleplay** untuk mode roleplay.\n"
        "Ketik **/nova** untuk chat dengan Nova.",
        parse_mode="Markdown"
    )

async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /backup - Backup manual database"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    try:
        from memory.persistent import get_persistent
        from pathlib import Path
        from datetime import datetime
        
        persistent = await get_persistent()
        db_path = persistent.db_path
        
        if not db_path.exists():
            await update.message.reply_text("❌ Database tidak ditemukan!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path("data/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"velora_manual_{timestamp}.db"
        
        import shutil
        shutil.copy(db_path, backup_path)
        
        size_kb = db_path.stat().st_size / 1024
        
        await update.message.reply_text(
            f"✅ **Backup Berhasil!**\n\n"
            f"📁 File: `{backup_path.name}`\n"
            f"📦 Size: {size_kb:.2f} KB\n"
            f"🕐 Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Backup error: {e}")
        await update.message.reply_text(f"❌ Backup gagal: {e}")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /stats - Statistik sistem"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    try:
        from memory.persistent import get_persistent
        
        persistent = await get_persistent()
        db_stats = await persistent.get_stats()
        
        world = get_world_state()
        memory = get_memory_manager()
        worker = get_worker()
        orchestrator = await get_orchestrator()
        role_manager = get_role_manager()
        
        stats_text = f"""
📊 **VELORA STATISTICS**

**System:**
• Total Memory Events: {memory.total_events}
• Active Sessions: {orchestrator.get_stats()['active_sessions']}
• Worker Uptime: {'Running' if worker.is_running else 'Stopped'}

**Database:**
• Size: {db_stats.get('db_size_mb', 0)} MB
• Timeline: {db_stats.get('timeline_count', 0)}
• Conversations: {db_stats.get('conversation_count', 0)}
• Long-term Memories: {db_stats.get('long_term_memory_count', 0)}

**World:**
• Drama Level: {world.drama_level:.0f}%
• Relationship Status: {world.relationship_status.value}

**Roles:**
• Total Roles: {len(role_manager.roles)}
• Active Role: {get_active_role(user_id) or 'Nova'}

**Worker Stats:**
• Proactive Sent: {worker._proactive_sent}
• Auto Saves: {worker._auto_saves}
• Backups: {worker._backups_created}
"""
        await update.message.reply_text(stats_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await update.message.reply_text(f"❌ Gagal mengambil statistik: {e}")

# =============================================================================
# COMMAND HANDLERS - LAYANAN (DEAL, MULAI, NEGO, DLL)
# =============================================================================

async def nego_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nego [harga] - Nego harga"""
    user_id = update.effective_user.id
    args = context.args
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not args:
        await update.message.reply_text(
            "❌ Masukkan harga.\n\n"
            "Contoh: `/nego 3000000`\n\n"
            "Harga minimal: Rp3.000.000 untuk pelacur, Rp200.000 untuk pijat."
        )
        return
    
    try:
        harga = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ Harga harus angka. Contoh: `/nego 3000000`")
        return
    
    # Dapatkan role aktif
    active_role_id = get_active_role(user_id)
    if not active_role_id:
        await update.message.reply_text("❌ Pilih role dulu dengan `/role`")
        return
    
    role_manager = get_role_manager()
    role = role_manager.get_role(active_role_id)
    
    if not role:
        await update.message.reply_text("❌ Role tidak ditemukan.")
        return
    
    # Cek apakah role punya method negotiate
    if hasattr(role, 'negotiate'):
        success, response = role.negotiate(harga)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ Role ini tidak support nego.")


async def deal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /deal - Konfirmasi deal"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    # Dapatkan role aktif
    active_role_id = get_active_role(user_id)
    if not active_role_id:
        await update.message.reply_text("❌ Pilih role dulu dengan `/role`")
        return
    
    role_manager = get_role_manager()
    role = role_manager.get_role(active_role_id)
    
    if not role:
        await update.message.reply_text("❌ Role tidak ditemukan.")
        return
    
    # Cek apakah role punya method confirm_booking
    if hasattr(role, 'confirm_booking'):
        response = role.confirm_booking(role.final_price if hasattr(role, 'final_price') else 0)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ Role ini tidak support booking.")


async def mulai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /mulai - Mulai layanan"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    # Dapatkan role aktif
    active_role_id = get_active_role(user_id)
    if not active_role_id:
        await update.message.reply_text("❌ Pilih role dulu dengan `/role`")
        return
    
    role_manager = get_role_manager()
    role = role_manager.get_role(active_role_id)
    
    if not role:
        await update.message.reply_text("❌ Role tidak ditemukan.")
        return
    
    # Cek apakah role punya method start_service atau _get_start_message
    if hasattr(role, 'start_service'):
        response = role.start_service()
        await update.message.reply_text(response)
    elif hasattr(role, '_get_start_message'):
        response = role._get_start_message()
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ Role ini belum siap dimulai.")


async def lanjut_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /lanjut - Lanjut sesi 2 (pelacur)"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    # Dapatkan role aktif
    active_role_id = get_active_role(user_id)
    if not active_role_id:
        await update.message.reply_text("❌ Pilih role dulu dengan `/role`")
        return
    
    role_manager = get_role_manager()
    role = role_manager.get_role(active_role_id)
    
    if not role:
        await update.message.reply_text("❌ Role tidak ditemukan.")
        return
    
    # Cek apakah role punya method start_session_2
    if hasattr(role, 'start_session_2'):
        response = role.start_session_2()
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ Role ini tidak memiliki sesi 2.")


async def nego_bj_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nego_bj [harga] - Nego BJ (pijat++)"""
    user_id = update.effective_user.id
    args = context.args
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not args:
        await update.message.reply_text(
            "❌ Masukkan harga.\n\n"
            "Contoh: `/nego_bj 200000`\n\n"
            "Harga minimal: Rp200.000"
        )
        return
    
    try:
        harga = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ Harga harus angka. Contoh: `/nego_bj 200000`")
        return
    
    # Dapatkan role aktif
    active_role_id = get_active_role(user_id)
    if not active_role_id:
        await update.message.reply_text("❌ Pilih role dulu dengan `/role`")
        return
    
    role_manager = get_role_manager()
    role = role_manager.get_role(active_role_id)
    
    if not role:
        await update.message.reply_text("❌ Role tidak ditemukan.")
        return
    
    # Cek apakah role punya method negotiate_bj
    if hasattr(role, 'negotiate_bj'):
        success, response = role.negotiate_bj(harga)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ Role ini tidak support nego BJ.")


async def nego_sex_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nego_sex [harga] - Nego Sex (pijat++)"""
    user_id = update.effective_user.id
    args = context.args
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not args:
        await update.message.reply_text(
            "❌ Masukkan harga.\n\n"
            "Contoh: `/nego_sex 700000`\n\n"
            "Harga minimal: Rp700.000"
        )
        return
    
    try:
        harga = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ Harga harus angka. Contoh: `/nego_sex 700000`")
        return
    
    # Dapatkan role aktif
    active_role_id = get_active_role(user_id)
    if not active_role_id:
        await update.message.reply_text("❌ Pilih role dulu dengan `/role`")
        return
    
    role_manager = get_role_manager()
    role = role_manager.get_role(active_role_id)
    
    if not role:
        await update.message.reply_text("❌ Role tidak ditemukan.")
        return
    
    # Cek apakah role punya method negotiate_sex
    if hasattr(role, 'negotiate_sex'):
        success, response = role.negotiate_sex(harga)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ Role ini tidak support nego sex.")
        
# =============================================================================
# REGISTER HANDLERS
# =============================================================================

def register_handlers(application):
    """Register semua command handlers ke application"""
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("nova", nova_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("flashback", flashback_command))
    application.add_handler(CommandHandler("roleplay", roleplay_command))
    application.add_handler(CommandHandler("pindah", pindah_command))
    application.add_handler(CommandHandler("role", role_command))
    application.add_handler(CommandHandler("statusrole", statusrole_command))
    application.add_handler(CommandHandler("batal", back_to_nova))
    application.add_handler(CommandHandler("pause", pause_session))
    application.add_handler(CommandHandler("resume", resume_session))
    application.add_handler(CommandHandler("backup", backup_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # ========== TAMBAHKAN HANDLER LAYANAN ==========
    application.add_handler(CommandHandler("nego", nego_command))
    application.add_handler(CommandHandler("deal", deal_command))
    application.add_handler(CommandHandler("mulai", mulai_command))
    application.add_handler(CommandHandler("lanjut", lanjut_command))
    application.add_handler(CommandHandler("nego_bj", nego_bj_command))
    application.add_handler(CommandHandler("nego_sex", nego_sex_command))
    # ==============================================
    
    logger.info("✅ All command handlers registered")
    
    return application


__all__ = [
    'get_user_mode',
    'set_user_mode',
    'get_active_role',
    'clear_user_mode',
    'register_handlers',
    'safe_reply',
    'safe_markdown'
]
