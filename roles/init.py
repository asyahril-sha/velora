"""
VELORA Roles Package
Role definitions: Nova, Ipar, TemanKantor, Pelakor, IstriOrang, Pijat++, Pelacur
"""

from .base import BaseRole
from .manager import RoleManager, get_role_manager

# Main Roles (akan dibuat di fase selanjutnya)
# from .nova import NovaRole
# from .ipar import IparRole
# from .teman_kantor import TemanKantorRole
# from .pelakor import PelakorRole
# from .istri_orang import IstriOrangRole

# Fantasy Liar Roles
from .pijat_plus_plus import (
    PijatPlusPlusRole,
    create_aghnia_punjabi,
    create_munira_agile
)

from .pelacur import (
    PelacurRole,
    create_davina_karamoy,
    create_sallsa_binta
)

__all__ = [
    # Base
    'BaseRole',
    'RoleManager',
    'get_role_manager',
    
    # Main Roles (akan ditambahkan)
    # 'NovaRole',
    # 'IparRole',
    # 'TemanKantorRole',
    # 'PelakorRole',
    # 'IstriOrangRole',
    
    # Fantasy Liar - Pijat++
    'PijatPlusPlusRole',
    'create_aghnia_punjabi',
    'create_munira_agile',
    
    # Fantasy Liar - Pelacur
    'PelacurRole',
    'create_davina_karamoy',
    'create_sallsa_binta',
]
