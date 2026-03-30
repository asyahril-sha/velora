"""
VELORA - Comprehensive Test Suite
Run all tests in one command: python test_all.py
Tests: Emotional, Relationship, Memory, World, Roles, Integration
"""

import os
import sys
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-5s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("VELORA-TEST")

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"


def print_header(text: str, color: str = BLUE):
    """Print section header"""
    print(f"\n{color}{'='*70}{RESET}")
    print(f"{color}{text:^70}{RESET}")
    print(f"{color}{'='*70}{RESET}")


def print_pass(text: str):
    print(f"{GREEN}✅ {text}{RESET}")


def print_fail(text: str):
    print(f"{RED}❌ {text}{RESET}")


def print_warn(text: str):
    print(f"{YELLOW}⚠️ {text}{RESET}")


def print_info(text: str):
    print(f"{BLUE}ℹ️ {text}{RESET}")


def print_subtest(name: str, passed: bool):
    status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    print(f"   {name:40} : {status}")


# =============================================================================
# TEST 1: EMOTIONAL ENGINE
# =============================================================================

class TestEmotionalEngine:
    """Test Emotional Engine functionality"""

    @staticmethod
    def run() -> Dict[str, bool]:
        results = {}
        
        print_header("🧠 TEST 1: EMOTIONAL ENGINE", MAGENTA)
        
        try:
            from core.emotional import EmotionalEngine, EmotionalStyle
            
            # Test 1: Initial values
            try:
                emo = EmotionalEngine()
                assert emo.sayang == 50
                assert emo.rindu == 0
                assert emo.trust == 50
                assert emo.mood == 0
                results['initial_values'] = True
            except Exception as e:
                results['initial_values'] = False
                print(f"   Initial values error: {e}")
            
            # Test 2: Positive triggers
            try:
                emo = EmotionalEngine()
                changes = emo.update_from_message("aku sayang kamu", 5)
                assert changes.get('sayang', 0) > 0
                assert emo.sayang > 50
                results['positive_triggers'] = True
            except Exception as e:
                results['positive_triggers'] = False
                print(f"   Positive triggers error: {e}")
            
            # Test 3: Negative triggers (pending)
            try:
                emo = EmotionalEngine()
                changes = emo.update_from_message("aku cerita tentang cewek kemarin", 5)
                assert changes.get('cemburu_pending', 0) > 0
                results['negative_triggers'] = True
            except Exception as e:
                results['negative_triggers'] = False
                print(f"   Negative triggers error: {e}")
            
            # Test 4: Style determination
            try:
                emo = EmotionalEngine()
                style = emo.get_current_style()
                assert style == EmotionalStyle.NEUTRAL
                
                emo.rindu = 80
                style = emo.get_current_style()
                assert style == EmotionalStyle.CLINGY
                
                emo.rindu = 0
                emo.arousal = 70
                style = emo.get_current_style()
                assert style == EmotionalStyle.FLIRTY
                results['style_determination'] = True
            except Exception as e:
                results['style_determination'] = False
                print(f"   Style determination error: {e}")
            
            # Test 5: Apply pending emotion
            try:
                emo = EmotionalEngine()
                changes = emo.apply_pending_emotion("cemburu", 20)
                assert changes.get('cemburu', 0) > 0
                results['pending_emotion'] = True
            except Exception as e:
                results['pending_emotion'] = False
                print(f"   Pending emotion error: {e}")
            
            # Test 6: Serialization
            try:
                emo = EmotionalEngine()
                emo.sayang = 75
                emo.rindu = 60
                data = emo.to_dict()
                new_emo = EmotionalEngine()
                new_emo.from_dict(data)
                assert new_emo.sayang == 75
                assert new_emo.rindu == 60
                results['serialization'] = True
            except Exception as e:
                results['serialization'] = False
                print(f"   Serialization error: {e}")
            
            # Print results
            for name, passed in results.items():
                print_subtest(f"Emotional: {name}", passed)
            
            return results
            
        except Exception as e:
            print_fail(f"Emotional Engine import error: {e}")
            return {}


# =============================================================================
# TEST 2: RELATIONSHIP MANAGER
# =============================================================================

class TestRelationshipManager:
    """Test Relationship Manager functionality"""

    @staticmethod
    def run() -> Dict[str, bool]:
        results = {}
        
        print_header("💕 TEST 2: RELATIONSHIP MANAGER", MAGENTA)
        
        try:
            from core.relationship import RelationshipManager, RelationshipPhase
            
            # Test 1: Initial values
            try:
                rel = RelationshipManager()
                assert rel.level == 1
                assert rel.phase == RelationshipPhase.STRANGER
                results['initial_values'] = True
            except Exception as e:
                results['initial_values'] = False
                print(f"   Initial values error: {e}")
            
            # Test 2: Level progression
            try:
                rel = RelationshipManager()
                rel.interaction_count = 50
                rel.update_level(70, 70, ['first_kiss'])
                assert rel.level >= 7
                results['level_progression'] = True
            except Exception as e:
                results['level_progression'] = False
                print(f"   Level progression error: {e}")
            
            # Test 3: Milestone achievement
            try:
                rel = RelationshipManager()
                result = rel.achieve_milestone('first_kiss')
                assert result is True
                result = rel.achieve_milestone('first_kiss')
                assert result is False
                results['milestone'] = True
            except Exception as e:
                results['milestone'] = False
                print(f"   Milestone error: {e}")
            
            # Test 4: Unlock progression
            try:
                rel = RelationshipManager()
                rel.level = 2
                unlock = rel.get_current_unlock()
                assert unlock.boleh_flirt is False
                
                rel.level = 5
                unlock = rel.get_current_unlock()
                assert unlock.boleh_flirt is True
                
                rel.level = 11
                unlock = rel.get_current_unlock()
                assert unlock.boleh_intim is True
                results['unlock_progression'] = True
            except Exception as e:
                results['unlock_progression'] = False
                print(f"   Unlock progression error: {e}")
            
            # Test 5: can_do_action
            try:
                rel = RelationshipManager()
                rel.level = 2
                allowed, _ = rel.can_do_action('flirt')
                assert allowed is False
                
                rel.level = 5
                allowed, _ = rel.can_do_action('flirt')
                assert allowed is True
                results['can_do_action'] = True
            except Exception as e:
                results['can_do_action'] = False
                print(f"   can_do_action error: {e}")
            
            # Test 6: Serialization
            try:
                rel = RelationshipManager()
                rel.level = 7
                rel.interaction_count = 80
                data = rel.to_dict()
                new_rel = RelationshipManager()
                new_rel.from_dict(data)
                assert new_rel.level == 7
                results['serialization'] = True
            except Exception as e:
                results['serialization'] = False
                print(f"   Serialization error: {e}")
            
            # Print results
            for name, passed in results.items():
                print_subtest(f"Relationship: {name}", passed)
            
            return results
            
        except Exception as e:
            print_fail(f"Relationship Manager import error: {e}")
            return {}


# =============================================================================
# TEST 3: MEMORY MANAGER
# =============================================================================

class TestMemoryManager:
    """Test Memory Manager functionality"""

    @staticmethod
    def run() -> Dict[str, bool]:
        results = {}
        
        print_header("🧠 TEST 3: MEMORY MANAGER", MAGENTA)
        
        try:
            from core.memory import MemoryManager
            
            # Test 1: Initial values
            try:
                memory = MemoryManager()
                assert memory.total_events == 0
                results['initial_values'] = True
            except Exception as e:
                results['initial_values'] = False
                print(f"   Initial values error: {e}")
            
            # Test 2: Add event
            try:
                memory = MemoryManager()
                memory.add_event("Test event", "Test detail", "test", "nova")
                assert memory.total_events == 1
                assert len(memory.short_term) == 1
                results['add_event'] = True
            except Exception as e:
                results['add_event'] = False
                print(f"   Add event error: {e}")
            
            # Test 3: Add long-term memory
            try:
                memory = MemoryManager()
                memory.add_long_term_memory("momen_penting", "Test moment", "Test content", role_id="nova")
                memories = memory.get_long_term("nova")
                assert len(memories) > 0
                results['long_term'] = True
            except Exception as e:
                results['long_term'] = False
                print(f"   Long-term memory error: {e}")
            
            # Test 4: Short-term sliding window
            try:
                memory = MemoryManager()
                for i in range(60):
                    memory.add_event(f"Event {i}", "", "test", "nova")
                assert len(memory.short_term) <= 50
                results['sliding_window'] = True
            except Exception as e:
                results['sliding_window'] = False
                print(f"   Sliding window error: {e}")
            
            # Test 5: Add role knowledge
            try:
                memory = MemoryManager()
                memory.add_role_knowledge("nova", "User suka kopi")
                knowledge = memory.get_role_knowledge("nova")
                assert "User suka kopi" in knowledge
                results['role_knowledge'] = True
            except Exception as e:
                results['role_knowledge'] = False
                print(f"   Role knowledge error: {e}")
            
            # Print results
            for name, passed in results.items():
                print_subtest(f"Memory: {name}", passed)
            
            return results
            
        except Exception as e:
            print_fail(f"Memory Manager import error: {e}")
            return {}


# =============================================================================
# TEST 4: WORLD SYSTEM
# =============================================================================

class TestWorldSystem:
    """Test World System functionality"""

    @staticmethod
    def run() -> Dict[str, bool]:
        results = {}
        
        print_header("🌍 TEST 4: WORLD SYSTEM", MAGENTA)
        
        try:
            from core.world import WorldState, GlobalRelationshipStatus, AwarenessLevel
            
            # Test 1: Initial values
            try:
                world = WorldState()
                assert world.drama_level == 0
                assert world.relationship_status == GlobalRelationshipStatus.PACARAN
                results['initial_values'] = True
            except Exception as e:
                results['initial_values'] = False
                print(f"   Initial values error: {e}")
            
            # Test 2: Add drama
            try:
                world = WorldState()
                world.add_drama(10, "test", "test reason")
                assert world.drama_level == 10
                results['add_drama'] = True
            except Exception as e:
                results['add_drama'] = False
                print(f"   Add drama error: {e}")
            
            # Test 3: Register role
            try:
                world = WorldState()
                world.register_role("nova", AwarenessLevel.FULL)
                assert "nova" in world.role_awareness
                results['register_role'] = True
            except Exception as e:
                results['register_role'] = False
                print(f"   Register role error: {e}")
            
            # Test 4: Cross-role effect
            try:
                world = WorldState()
                world.register_role("nova", AwarenessLevel.FULL)
                effects = world.propagate_interaction("pelakor", "test message", {})
                assert effects.get('drama_change', 0) > 0
                assert 'nova' in effects.get('affected_roles', [])
                results['cross_role'] = True
            except Exception as e:
                results['cross_role'] = False
                print(f"   Cross-role effect error: {e}")
            
            # Test 5: Get knowledge for role
            try:
                world = WorldState()
                world.register_role("nova", AwarenessLevel.FULL)
                knowledge = world.get_knowledge_for_role("nova")
                assert knowledge is not None
                results['knowledge'] = True
            except Exception as e:
                results['knowledge'] = False
                print(f"   Knowledge error: {e}")
            
            # Print results
            for name, passed in results.items():
                print_subtest(f"World: {name}", passed)
            
            return results
            
        except Exception as e:
            print_fail(f"World System import error: {e}")
            return {}


# =============================================================================
# TEST 5: ROLES SYSTEM
# =============================================================================

class TestRolesSystem:
    """Test Roles System functionality"""

    @staticmethod
    def run() -> Dict[str, bool]:
        results = {}
        
        print_header("👤 TEST 5: ROLES SYSTEM", MAGENTA)
        
        try:
            from roles.nova import create_nova
            from roles.ipar import create_ipar
            from roles.teman_kantor import create_teman_kantor
            from roles.pelakor import create_pelakor
            from roles.istri_orang import create_istri_orang
            from roles.pijat_plus_plus import create_aghnia_punjabi, create_munira_agile
            from roles.pelacur import create_davina_karamoy, create_sallsa_binta
            from roles.manager import get_role_manager
            
            # Test 1: Create Nova
            try:
                nova = create_nova()
                assert nova.name == "Nova"
                assert nova.role_type == "nova"
                results['nova'] = True
            except Exception as e:
                results['nova'] = False
                print(f"   Nova creation error: {e}")
            
            # Test 2: Create Ipar
            try:
                ipar = create_ipar()
                assert ipar.name == "Tasya Dietha"
                results['ipar'] = True
            except Exception as e:
                results['ipar'] = False
                print(f"   Ipar creation error: {e}")
            
            # Test 3: Create Teman Kantor
            try:
                teman_kantor = create_teman_kantor()
                assert teman_kantor.name == "Musdalifah"
                results['teman_kantor'] = True
            except Exception as e:
                results['teman_kantor'] = False
                print(f"   Teman Kantor creation error: {e}")
            
            # Test 4: Create Pelakor
            try:
                pelakor = create_pelakor()
                assert pelakor.name == "Widya"
                results['pelakor'] = True
            except Exception as e:
                results['pelakor'] = False
                print(f"   Pelakor creation error: {e}")
            
            # Test 5: Create Istri Orang
            try:
                istri_orang = create_istri_orang()
                assert istri_orang.name == "Siska"
                results['istri_orang'] = True
            except Exception as e:
                results['istri_orang'] = False
                print(f"   Istri Orang creation error: {e}")
            
            # Test 6: Create Pijat++ roles
            try:
                aghnia = create_aghnia_punjabi()
                assert aghnia.name == "Aghnia Punjabi"
                munira = create_munira_agile()
                assert munira.name == "Munira Agile"
                results['pijat_plus_plus'] = True
            except Exception as e:
                results['pijat_plus_plus'] = False
                print(f"   Pijat++ creation error: {e}")
            
            # Test 7: Create Pelacur roles
            try:
                davina = create_davina_karamoy()
                assert davina.name == "Davina Karamoy"
                sallsa = create_sallsa_binta()
                assert sallsa.name == "Sallsa Binta"
                results['pelacur'] = True
            except Exception as e:
                results['pelacur'] = False
                print(f"   Pelacur creation error: {e}")
            
            # Test 8: Role Manager
            try:
                role_manager = get_role_manager()
                roles = role_manager.get_all_roles()
                assert len(roles) == 9
                results['role_manager'] = True
            except Exception as e:
                results['role_manager'] = False
                print(f"   Role Manager error: {e}")
            
            # Test 9: Nova greeting
            try:
                nova = create_nova()
                greeting = nova.get_greeting()
                assert greeting is not None
                assert len(greeting) > 0
                results['nova_greeting'] = True
            except Exception as e:
                results['nova_greeting'] = False
                print(f"   Nova greeting error: {e}")
            
            # Print results
            for name, passed in results.items():
                print_subtest(f"Roles: {name}", passed)
            
            return results
            
        except Exception as e:
            print_fail(f"Roles System import error: {e}")
            return {}


# =============================================================================
# TEST 6: INTEGRATION FLOW
# =============================================================================

class TestIntegrationFlow:
    """Test integration flow between components"""

    @staticmethod
    def run() -> Dict[str, bool]:
        results = {}
        
        print_header("🔄 TEST 6: INTEGRATION FLOW", MAGENTA)
        
        try:
            from core.memory import MemoryManager
            from core.world import WorldState
            from roles.nova import create_nova
            from roles.manager import get_role_manager
            
            # Test 1: Memory + World integration
            try:
                memory = MemoryManager()
                world = WorldState()
                memory.initialize(None, world)
                assert memory.world is not None
                results['memory_world'] = True
            except Exception as e:
                results['memory_world'] = False
                print(f"   Memory-World integration error: {e}")
            
            # Test 2: Nova update from message
            try:
                nova = create_nova()
                changes = nova.update_from_message("aku sayang kamu")
                assert changes is not None
                results['nova_update'] = True
            except Exception as e:
                results['nova_update'] = False
                print(f"   Nova update error: {e}")
            
            # Test 3: Nova status format
            try:
                nova = create_nova()
                status = nova.format_status()
                assert status is not None
                assert "Nova" in status
                results['nova_status'] = True
            except Exception as e:
                results['nova_status'] = False
                print(f"   Nova status error: {e}")
            
            # Test 4: Role switch
            try:
                role_manager = get_role_manager()
                response = role_manager.switch_role("ipar")
                assert "Tasya Dietha" in response
                results['role_switch'] = True
            except Exception as e:
                results['role_switch'] = False
                print(f"   Role switch error: {e}")
            
            # Test 5: World drama change
            try:
                world = WorldState()
                world.add_drama(10, "test", "test")
                assert world.drama_level == 10
                results['world_drama'] = True
            except Exception as e:
                results['world_drama'] = False
                print(f"   World drama error: {e}")
            
            # Test 6: Memory event add
            try:
                memory = MemoryManager()
                memory.add_event("Test", "Detail", "test", "nova")
                assert memory.total_events == 1
                results['memory_event'] = True
            except Exception as e:
                results['memory_event'] = False
                print(f"   Memory event error: {e}")
            
            # Print results
            for name, passed in results.items():
                print_subtest(f"Integration: {name}", passed)
            
            return results
            
        except Exception as e:
            print_fail(f"Integration Flow error: {e}")
            return {}


# =============================================================================
# TEST 7: REALITY ENGINE (if available)
# =============================================================================

class TestRealityEngine:
    """Test Reality Engine functionality"""

    @staticmethod
    def run() -> Dict[str, bool]:
        results = {}
        
        print_header("✨ TEST 7: REALITY ENGINE", MAGENTA)
        
        try:
            from core.reality_engine import (
                IntentScorer, EmotionDelaySystem, MemoryPrioritySystem,
                SceneEngine, ImperfectionSystem, KnowledgeLeakSystem,
                InnerThoughtSystem, PersonalityDriftSystem
            )
            
            # Test 1: IntentScorer
            try:
                scorer = IntentScorer()
                scores = scorer.score("aku kangen nova")
                assert scores.get('nova', 0) > 0
                results['intent_scorer'] = True
            except Exception as e:
                results['intent_scorer'] = False
                print(f"   IntentScorer error: {e}")
            
            # Test 2: SceneEngine
            try:
                scene = SceneEngine()
                body = scene.get_body_language("horny", 0.8)
                assert body is not None
                results['scene_engine'] = True
            except Exception as e:
                results['scene_engine'] = False
                print(f"   SceneEngine error: {e}")
            
            # Test 3: ImperfectionSystem
            try:
                imperfection = ImperfectionSystem()
                text = imperfection.add_imperfections("Halo", 0.5)
                assert text is not None
                results['imperfection'] = True
            except Exception as e:
                results['imperfection'] = False
                print(f"   ImperfectionSystem error: {e}")
            
            # Test 4: KnowledgeLeakSystem
            try:
                leak = KnowledgeLeakSystem()
                knows, misunderstood = leak.should_know("nova", "general")
                results['knowledge_leak'] = True
            except Exception as e:
                results['knowledge_leak'] = False
                print(f"   KnowledgeLeakSystem error: {e}")
            
            # Print results
            for name, passed in results.items():
                print_subtest(f"Reality: {name}", passed)
            
            return results
            
        except ImportError:
            print_warn("Reality Engine not available (optional)")
            return {}
        except Exception as e:
            print_fail(f"Reality Engine error: {e}")
            return {}


# =============================================================================
# TEST 8: CONFIGURATION
# =============================================================================

class TestConfiguration:
    """Test configuration loading"""

    @staticmethod
    def run() -> Dict[str, bool]:
        results = {}
        
        print_header("⚙️ TEST 8: CONFIGURATION", MAGENTA)
        
        try:
            from config import get_settings
            
            # Test 1: Config loads
            try:
                settings = get_settings()
                results['config_load'] = True
            except Exception as e:
                results['config_load'] = False
                print(f"   Config load error: {e}")
            
            # Test 2: Required vars check
            try:
                settings = get_settings()
                required = ['deepseek_api_key', 'telegram_token', 'admin_id']
                for var in required:
                    value = getattr(settings, var, None)
                    if value and value != f"your_{var}_here":
                        results[f'has_{var}'] = True
                    else:
                        results[f'has_{var}'] = False
            except Exception as e:
                print(f"   Required vars error: {e}")
                for var in ['deepseek_api_key', 'telegram_token', 'admin_id']:
                    results[f'has_{var}'] = False
            
            # Print results
            for name, passed in results.items():
                print_subtest(f"Config: {name}", passed)
            
            return results
            
        except Exception as e:
            print_fail(f"Configuration error: {e}")
            return {}


# =============================================================================
# MAIN
# =============================================================================

async def run_all_tests() -> Dict[str, Dict[str, bool]]:
    """Run all test suites"""
    
    print_header("💜 VELORA - COMPREHENSIVE TEST SUITE", CYAN)
    print_info(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Testing all components...")
    
    all_results = {}
    
    # Run all test suites
    all_results['emotional'] = TestEmotionalEngine.run()
    all_results['relationship'] = TestRelationshipManager.run()
    all_results['memory'] = TestMemoryManager.run()
    all_results['world'] = TestWorldSystem.run()
    all_results['roles'] = TestRolesSystem.run()
    all_results['integration'] = TestIntegrationFlow.run()
    all_results['reality'] = TestRealityEngine.run()
    all_results['config'] = TestConfiguration.run()
    
    return all_results


def calculate_summary(results: Dict[str, Dict[str, bool]]) -> Dict[str, Any]:
    """Calculate test summary"""
    total_tests = 0
    passed_tests = 0
    
    for suite_name, suite_results in results.items():
        for test_name, passed in suite_results.items():
            total_tests += 1
            if passed:
                passed_tests += 1
    
    return {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': total_tests - passed_tests,
        'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
        'suites_passed': sum(1 for suite in results.values() if any(v for v in suite.values())),
        'total_suites': len(results)
    }


def print_summary(results: Dict[str, Dict[str, bool]], summary: Dict[str, Any]):
    """Print test summary"""
    
    print_header("📊 TEST SUMMARY", CYAN)
    
    # Suite results
    print(f"\n{BLUE}SUITE RESULTS:{RESET}")
    for suite_name, suite_results in results.items():
        suite_passed = all(v for v in suite_results.values()) if suite_results else False
        status = f"{GREEN}✓ PASS{RESET}" if suite_passed else f"{RED}✗ FAIL{RESET}"
        total = len(suite_results)
        passed = sum(1 for v in suite_results.values() if v)
        print(f"   {suite_name:15} : {status} ({passed}/{total})")
    
    # Overall stats
    print(f"\n{BLUE}OVERALL STATISTICS:{RESET}")
    print(f"   Total Tests      : {summary['total_tests']}")
    print(f"   Passed           : {GREEN}{summary['passed_tests']}{RESET}")
    print(f"   Failed           : {RED}{summary['failed_tests']}{RESET}")
    print(f"   Pass Rate        : {GREEN}{summary['pass_rate']:.1f}%{RESET}")
    
    # Final verdict
    print(f"\n{BLUE}{'='*70}{RESET}")
    if summary['failed_tests'] == 0:
        print(f"{GREEN}{'🎉 ALL TESTS PASSED! VELORA IS READY FOR DEPLOYMENT! 🎉':^70}{RESET}")
    else:
        print(f"{YELLOW}{'⚠️ SOME TESTS FAILED. PLEASE REVIEW BEFORE DEPLOYMENT. ⚠️':^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")


def main():
    """Main entry point"""
    try:
        results = asyncio.run(run_all_tests())
        summary = calculate_summary(results)
        print_summary(results, summary)
        
        # Return exit code
        return 0 if summary['failed_tests'] == 0 else 1
        
    except KeyboardInterrupt:
        print_warn("\nTest interrupted by user")
        return 1
    except Exception as e:
        print_fail(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
