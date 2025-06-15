"""
Tests for the refactored systems architecture.
"""

from evennia.utils.test_resources import EvenniaTest
from world.systems import SkillSystem, HackableSystem
from world.skills import HackableBehavior
from world.events import Event, EventContext


class TestSkillSystem(EvenniaTest):
    """Test the centralized SkillSystem."""
    
    def setUp(self):
        super().setUp()
        # Set up a character with some attributes and skills
        self.char1.db.int = 14  # +1 modifier
        self.char1.db.dex = 12  # +0 modifier
        self.char1.db.wis = 10  # +0 modifier
        
        # Add Hack skill
        if not hasattr(self.char1, 'skills'):
            from world.skills import SkillHandler
            from evennia.utils.utils import lazy_property
            # Manually add skills property for testing
            self.char1.skills = SkillHandler(self.char1)
        
        # Add a hack skill
        self.char1.skills.add({
            'key': 'Hack', 
            'level': 2
        })
    
    def test_skill_check_basic(self):
        """Test basic skill check mechanics."""
        result = SkillSystem.make_skill_check(
            self.char1, 
            'Hack', 
            difficulty=10  # Moderate difficulty
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.skill_level, 2)
        self.assertEqual(result.attribute_modifier, 1)  # INT 14 = +1
        self.assertEqual(result.target_number, 10)
        self.assertTrue(2 <= result.roll <= 12)  # 2d6 range
    
    def test_skill_check_with_modifiers(self):
        """Test skill check with situational modifiers."""
        result = SkillSystem.make_skill_check(
            self.char1,
            'Hack',
            difficulty=12,
            modifiers={'tools': 2, 'rushed': -2}
        )
        
        self.assertEqual(result.difficulty_modifier, 0)  # 2 + (-2) = 0
        self.assertEqual(result.total_modifier, 3)  # skill(2) + attr(1) + mods(0)
    
    def test_untrained_skill(self):
        """Test using an untrained skill."""
        result = SkillSystem.make_skill_check(
            self.char1,
            'Pilot',  # Not trained in this
            difficulty=10
        )
        
        self.assertEqual(result.skill_level, 0)
        self.assertEqual(result.attribute_modifier, 0)  # DEX 12 = +0
        self.assertEqual(result.total_modifier, 0)


class TestHackableSystem(EvenniaTest):
    """Test the HackableSystem and integration with behaviors."""
    
    def setUp(self):
        super().setUp()
        # Set up hacker character
        self.char1.db.int = 14  # +1 modifier
        
        if not hasattr(self.char1, 'skills'):
            from world.skills import SkillHandler
            self.char1.skills = SkillHandler(self.char1)
        
        self.char1.skills.add({'key': 'Hack', 'level': 3})
        
        # Set up hackable target
        if not hasattr(self.room1, 'behaviors'):
            from world.skills import BehaviorHandler
            self.room1.behaviors = BehaviorHandler(self.room1)
        
        # Add hackable behavior to target
        hackable_behavior = HackableBehavior(
            difficulty=10,
            security_level=2,
            hack_time=3
        )
        self.room1.behaviors.add(hackable_behavior)
    
    def test_hackable_system_integration(self):
        """Test that HackableSystem works with behaviors."""
        hackable_config = self.room1.behaviors.get('hackable')
        self.assertIsNotNone(hackable_config)
        
        result = HackableSystem.attempt_hack(
            self.char1,
            self.room1,
            hackable_config
        )
        
        self.assertIn('skill_result', result)
        self.assertIn('hacker', result)
        self.assertIn('target', result)
        self.assertEqual(result['hacker'], self.char1)
        self.assertEqual(result['target'], self.room1)
    
    def test_hackable_behavior_event_handling(self):
        """Test that HackableBehavior properly delegates to HackableSystem."""
        event = Event(
            event_type='hack',
            source=self.char1,
            target=self.room1,
            context=EventContext()
        )
        
        hackable_behavior = self.room1.behaviors.get('hackable')
        hackable_behavior.handle_event(event)
        
        # Event should have history from the hack attempt
        self.assertTrue(len(event.history) > 0)
        self.assertIn('Hack', event.history[0])


class TestArchitectureIntegration(EvenniaTest):
    """Test the overall integration of the new architecture."""
    
    def setUp(self):
        super().setUp()
        # Set up similar to other tests
        self.char1.db.int = 16  # +2 modifier
        
        if not hasattr(self.char1, 'skills'):
            from world.skills import SkillHandler
            self.char1.skills = SkillHandler(self.char1)
        
        self.char1.skills.add({'key': 'Hack', 'level': 1})
        
        if not hasattr(self.room1, 'behaviors'):
            from world.skills import BehaviorHandler
            self.room1.behaviors = BehaviorHandler(self.room1)
        
        hackable_behavior = HackableBehavior(
            difficulty=8,  # Easy target
            security_level=1,
            system_type="terminal"
        )
        self.room1.behaviors.add(hackable_behavior)
        self.char1.location=self.room1
    
    def test_full_hack_event_flow(self):
        """Test the complete flow from event creation to resolution."""
        from world.events import GlobalEventHandler
        
        event = Event(
            event_type='hack',
            source=self.char1,
            target=self.room1,
            context=EventContext()
        )
        
        # Process the event through the global handler
        GlobalEventHandler.handleEvent(event)
        
        # Verify event was processed
        self.assertTrue(len(event.history) > 0)
        
        # Verify the behavior was invoked (should have history)
        hack_info = event.history[0]
        self.assertIn('Hack', hack_info)
        self.assertIn('succeeded' or 'failed', hack_info.lower())
    
    def test_system_extensibility(self):
        """Test that the system can be easily extended."""
        # Create a custom hackable behavior with different settings
        custom_behavior = HackableBehavior(
            difficulty=14,  # Hard
            security_level=5,  # High security
            system_type="military",
            hack_time=10
        )
        
        # Test that it works with the same system
        result = HackableSystem.attempt_hack(
            self.char1,
            self.room1, 
            custom_behavior
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['time_taken'], 10)
        # High security should apply negative modifiers
        modifiers = result['skill_result'].difficulty_modifier
        self.assertTrue(modifiers < 0, "High security should impose penalties")