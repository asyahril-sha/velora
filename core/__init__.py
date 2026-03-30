"""
VELORA Core Package

Core systems:
- tracker: State Tracker (clothing, intimacy, timeline)
- emotional: Emotional Engine (9 dimensi emosi)
- relationship: Relationship Manager (5 fase, level 1-12)
- conflict: Conflict Engine (cemburu, kecewa, cold war)
- world: World System (global reality, drama level)
- intimacy: Intimacy Core (stamina, arousal, positions)
- service_provider: Service Provider Base (pijat++, pelacur)
- memory: Memory Manager (short-term, long-term)
- orchestrator: Role Orchestrator (pusat kendali)
- reality_engine: Reality Engine (realism 9.9 features)
"""

from .tracker import (
    PhysicalCondition,
    IntimacyPhase,
    ClothingLayer,
    Position,
    Activity,
    StateTracker,
    get_state_tracker,
    reset_state_tracker
)

from .emotional import (
    EmotionalStyle,
    EmotionalEngine,
    get_emotional_engine,
    reset_emotional_engine
)

from .relationship import (
    RelationshipPhase,
    PhaseUnlock,
    Milestone,
    RelationshipManager,
    get_relationship_manager,
    reset_relationship_manager
)

from .conflict import (
    ConflictType,
    ConflictSeverity,
    ConflictResolution,
    Conflict,
    ConflictEngine,
    get_conflict_engine,
    reset_conflict_engine
)

from .world import (
    GlobalRelationshipStatus,
    AwarenessLevel,
    DramaLevel,
    PublicKnowledge,
    RoleAwareness,
    WorldState,
    get_world_state,
    reset_world_state
)

from .intimacy import (
    IntimacyPhase as IntimacyPhaseCore,
    IntimacyAction,
    ClimaxIntensity,
    StaminaSystem,
    ArousalSystem,
    PositionDatabase,
    MoansDatabase,
    ClimaxLocationDatabase,
    IntimacySession,
    get_intimacy_session,
    reset_intimacy_session
)

from .service_provider import (
    ServiceType,
    ServiceStatus,
    AutoSceneType,
    CustomerTier,
    Customer,
    FlatEmotionalEngine,
    ProfessionalRelationship,
    ServiceProviderBase,
    format_price
)

from .memory import (
    MemoryEvent,
    LongTermMemory,
    MemoryManager,
    get_memory_manager,
    reset_memory_manager
)

from .orchestrator import (
    RoutingResult,
    RoleOrchestrator,
    get_orchestrator,
    reset_orchestrator
)

from .reality_engine import (
    IntentScorer,
    EmotionDelaySystem,
    MemoryPrioritySystem,
    SceneEngine,
    ImperfectionSystem,
    KnowledgeLeakSystem,
    InnerThoughtSystem,
    PersonalityDriftSystem,
    RealityEngine,
    get_reality_engine,
    reset_reality_engine
)

__all__ = [
    # Tracker
    "PhysicalCondition",
    "IntimacyPhase",
    "ClothingLayer",
    "Position",
    "Activity",
    "StateTracker",
    "get_state_tracker",
    "reset_state_tracker",
    
    # Emotional
    "EmotionalStyle",
    "EmotionalEngine",
    "get_emotional_engine",
    "reset_emotional_engine",
    
    # Relationship
    "RelationshipPhase",
    "PhaseUnlock",
    "Milestone",
    "RelationshipManager",
    "get_relationship_manager",
    "reset_relationship_manager",
    
    # Conflict
    "ConflictType",
    "ConflictSeverity",
    "ConflictResolution",
    "Conflict",
    "ConflictEngine",
    "get_conflict_engine",
    "reset_conflict_engine",
    
    # World
    "GlobalRelationshipStatus",
    "AwarenessLevel",
    "DramaLevel",
    "PublicKnowledge",
    "RoleAwareness",
    "WorldState",
    "get_world_state",
    "reset_world_state",
    
    # Intimacy
    "IntimacyPhaseCore",
    "IntimacyAction",
    "ClimaxIntensity",
    "StaminaSystem",
    "ArousalSystem",
    "PositionDatabase",
    "MoansDatabase",
    "ClimaxLocationDatabase",
    "IntimacySession",
    "get_intimacy_session",
    "reset_intimacy_session",
    
    # Service Provider
    "ServiceType",
    "ServiceStatus",
    "AutoSceneType",
    "CustomerTier",
    "Customer",
    "FlatEmotionalEngine",
    "ProfessionalRelationship",
    "ServiceProviderBase",
    "format_price",
    
    # Memory
    "MemoryEvent",
    "LongTermMemory",
    "MemoryManager",
    "get_memory_manager",
    "reset_memory_manager",
    
    # Orchestrator
    "RoutingResult",
    "RoleOrchestrator",
    "get_orchestrator",
    "reset_orchestrator",
    
    # Reality Engine
    "IntentScorer",
    "EmotionDelaySystem",
    "MemoryPrioritySystem",
    "SceneEngine",
    "ImperfectionSystem",
    "KnowledgeLeakSystem",
    "InnerThoughtSystem",
    "PersonalityDriftSystem",
    "RealityEngine",
    "get_reality_engine",
    "reset_reality_engine"
]
