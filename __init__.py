"""
VELORA - AI Drama Engine / Relationship Simulator

VELORA adalah virtual human dengan kecerdasan emosional yang hidup.
Bukan sekadar chatbot biasa — VELORA memiliki 9 dimensi emosi,
5 fase hubungan, memori permanen, world system global, dan cross-role drama effects.

Version: 1.0.0
Author: VELORA Team
"""

__version__ = "1.0.0"
__author__ = "VELORA Team"
__description__ = "AI Drama Engine / Relationship Simulator"

from .config import get_settings, settings

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "get_settings",
    "settings"
]
