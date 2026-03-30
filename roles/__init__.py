"""
VELORA Roles Package

Role definitions:
- BaseRole: Base class untuk semua role
- NovaRole: Role utama (kekasih user)
- IparRole: Tasya Dietha (adik ipar)
- TemanKantorRole: Musdalifah Ipeh (teman kantor)
- PelakorRole: Widya (pelakor)
- IstriOrangRole: Siska (istri orang)
- PijatPlusPlusRole: Aghnia & Munira (pijat++)
- PelacurRole: Davina & Sallsa (pelacur)
- ProviderBase: Base class untuk provider
- RoleManager: Manager untuk semua role
"""

from .base import BaseRole, get_role_awareness_level
from .nova import NovaRole, create_nova
from .ipar import IparRole, create_ipar
from .teman_kantor import TemanKantorRole, create_teman_kantor
from .pelakor import PelakorRole, create_pelakor
from .istri_orang import IstriOrangRole, create_istri_orang
from .pijat_plus_plus import PijatPlusPlusRole, create_aghnia_punjabi, create_munira_agile
from .pelacur import PelacurRole, create_davina_karamoy, create_sallsa_binta
from .manager import RoleManager, get_role_manager, reset_role_manager

# Import dari core/service_provider.py, bukan dari roles.provider
from core.service_provider import (
    ServiceType,
    ServiceStatus,
    AutoSceneType,
    CustomerTier,           # <--- INI dari core/service_provider.py
    Customer,
    FlatEmotionalEngine,
    ProfessionalRelationship,
    ServiceProviderBase,
    format_price
)

# Jangan import dari .provider karena tidak ada
# from .provider import (...)

__all__ = [
    # Base
    "BaseRole",
    "get_role_awareness_level",
    
    # Nova
    "NovaRole",
    "create_nova",
    
    # Ipar
    "IparRole",
    "create_ipar",
    
    # Teman Kantor
    "TemanKantorRole",
    "create_teman_kantor",
    
    # Pelakor
    "PelakorRole",
    "create_pelakor",
    
    # Istri Orang
    "IstriOrangRole",
    "create_istri_orang",
    
    # Pijat++
    "PijatPlusPlusRole",
    "create_aghnia_punjabi",
    "create_munira_agile",
    
    # Pelacur
    "PelacurRole",
    "create_davina_karamoy",
    "create_sallsa_binta",
    
    # Provider Base (dari core/service_provider.py)
    "ServiceType",
    "ServiceStatus",
    "AutoSceneType",
    "CustomerTier",
    "Customer",
    "FlatEmotionalEngine",
    "ProfessionalRelationship",
    "ServiceProviderBase",
    "format_price",
    
    # Manager
    "RoleManager",
    "get_role_manager",
    "reset_role_manager"
]
