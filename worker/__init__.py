"""
VELORA Worker Package

Background tasks:
- Rindu growth (30 menit)
- Conflict decay (30 menit)
- Mood recovery (1 jam)
- Drama decay (30 menit)
- Auto save (1 menit)
- Proactive chat (5 menit)
- Auto scene for providers (15 detik)
- Booking expiry check (1 menit)
- Session timeout (5 menit)
- Personality drift update (1 jam)
- Auto backup (6 jam)
"""

from .background import VeloraWorker, get_worker, reset_worker

__all__ = [
    "VeloraWorker",
    "get_worker",
    "reset_worker"
]
