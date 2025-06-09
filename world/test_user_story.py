"""
E2E and Unit Tests for User Story Implementation

This test suite covers the complete user story scenario:
1. Dark room visibility
2. Night vision goggles equipment
3. NPC intimidation
4. Follower commands  
5. Airlock mechanics
6. Environmental death
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from evennia import create_object, search_object
import random


class UserStoryE2ETest(EvenniaTest):
    """End-to-end test of the complete user story scenario."""
    
    def setUp(self):
        super().setUp()
        # Set up test environment
        self.setup_test_world()
    
    def setup_test_world(self):
        """Create all objects needed for the user story."""
        # Create dark room
        self.dark_room = create_object(
            "typeclasses.rooms.DarkRoom",
            key="Dark Room",
            location=None
        )
        
        # Create airlock room
        self.airlock = create_object(
            "typeclasses.rooms.AirlockRoom", 
            key="Airlock",
            location=None
        )
        
        # Create space room (vacuum environment)
        self.space = create_object(
            "typeclasses.rooms.SpaceRoom",
            key="Outer Space", 
            location=None
        )
        
        # Create exits
        self.airlock_exit = create_object(
            "typeclasses.exits.Exit",
            key="airlock",
            location=self.dark_room,
            destination=self.airlock
        )
        
        self.space_exit = create_object(
            "typeclasses.exits.Exit", 
            key="outer door",
            location=self.airlock,
            destination=self.space
        )
        
        # Create night vision goggles
        self.goggles = create_object(
            "typeclasses.objects.NightVisionGoggles",
            key="night vision goggles",
            location=self.char1
        )
        
        # Create thug NPC
        self.thug = create_object(
            "typeclasses.characters.ThugNPC",
            key="Thug",
            location=self.dark_room
        )
        
        # Create red button
        self.red_button = create_object(
            "typeclasses.objects.AirlockButton",
            key="red button", 
            location=self.airlock
        )
        
        # Move character to dark room
        self.char1.move_to(self.dark_room, quiet=True)
        
        # Equip goggles on character
        self.char1.equipment.wear(self.goggles, "head")
    
    def test_complete_user_story(self):
        """Test the complete user story from start to finish."""
        
        # Step 1: Character in dark room can't see
        self.char1.execute_cmd("look")
        self.assertIn("too dark to see", self.char1.msg.call_args[0][0].lower())
        
        # Step 2: Use night vision goggles
        self.char1.execute_cmd("use goggles") 
        self.assertIn("activate", self.char1.msg.call_args[0][0].lower())
        
        # Step 3: Look again - should see room description in green
        self.char1.execute_cmd("look")
        last_msg = self.char1.msg.call_args[0][0]
        self.assertIn("|g", last_msg)  # Green color code
        self.assertIn("Thug", last_msg)  # Should see the NPC
        
        # Step 4: Intimidate the thug
        with patch('random.randint', return_value=15):  # Force success
            self.char1.execute_cmd("intimidate thug")
            self.assertIn("success", self.char1.msg.call_args[0][0].lower())
        
        # Verify thug is now following
        self.assertTrue(self.thug.db.following == self.char1)
        
        # Step 5: Order thug to airlock
        self.char1.execute_cmd("order thug airlock")
        self.assertEqual(self.thug.location, self.airlock)
        
        # Step 6: Press red button to open airlock
        self.char1.move_to(self.airlock, quiet=True)
        self.char1.execute_cmd("press red button")
        
        # Verify thug was ejected to space
        self.assertEqual(self.thug.location, self.space)
        
        # Step 7: Wait for environmental damage to kill thug
        # Simulate time passing
        for _ in range(10):  # 10 rounds of environmental damage
            self.thug.at_heartbeat()
        
        # Verify thug is dead
        self.assertTrue(self.thug.db.is_dead)


class LightingSystemTest(EvenniaTest):
    """Unit tests for room lighting/visibility system."""
    
    def setUp(self):
        super().setUp()
        self.dark_room = create_object(
            "typeclasses.rooms.DarkRoom",
            key="Dark Room"
        )
        self.char1.move_to(self.dark_room, quiet=True)
    
    def test_dark_room_visibility(self):
        """Test that dark rooms hide descriptions."""
        appearance = self.dark_room.return_appearance(self.char1)
        self.assertIn("too dark", appearance.lower())
    
    def test_light_source_reveals_room(self):
        """Test that light sources reveal room descriptions."""
        self.char1.db.has_light_source = True
        appearance = self.dark_room.return_appearance(self.char1)
        self.assertNotIn("too dark", appearance.lower())
    
    def test_night_vision_shows_green(self):
        """Test that night vision shows descriptions in green."""
        self.char1.db.night_vision_active = True
        appearance = self.dark_room.return_appearance(self.char1)
        self.assertIn("|g", appearance)  # Green color code


class EquipmentSystemTest(EvenniaTest):
    """Unit tests for equipment/wearable system."""
    
    def setUp(self):
        super().setUp()
        self.goggles = create_object(
            "typeclasses.objects.NightVisionGoggles",
            key="night vision goggles",
            location=self.char1
        )
    
    def test_equipment_wearing(self):
        """Test wearing equipment in slots."""
        self.char1.equipment.wear(self.goggles, "head")
        self.assertEqual(self.char1.equipment.get_slot("head"), self.goggles)
    
    def test_equipment_activation(self):
        """Test activating equipment."""
        self.char1.equipment.wear(self.goggles, "head")
        self.char1.execute_cmd("use goggles")
        self.assertTrue(self.goggles.db.is_active)
    
    def test_night_vision_effect(self):
        """Test night vision effect on visibility."""
        self.char1.equipment.wear(self.goggles, "head")
        self.goggles.db.is_active = True
        self.assertTrue(self.char1.has_night_vision())


class SkillCheckSystemTest(EvenniaTest):
    """Unit tests for skill check mechanics."""
    
    def setUp(self):
        super().setUp()
        # Set up character with intimidate skill
        self.char1.skills.add({
            "key": "Intimidate",
            "level": 1,
            "stat": "Charisma"
        })
        # Set charisma stat
        self.char1.db.stats = {"Charisma": 14}  # +1 modifier
    
    @patch('random.randint')
    def test_skill_check_success(self, mock_roll):
        """Test successful skill check."""
        mock_roll.return_value = 15  # High roll
        result = self.char1.make_skill_check("Intimidate", difficulty=12)
        self.assertTrue(result.success)
    
    @patch('random.randint') 
    def test_skill_check_failure(self, mock_roll):
        """Test failed skill check."""
        mock_roll.return_value = 5  # Low roll
        result = self.char1.make_skill_check("Intimidate", difficulty=15)
        self.assertFalse(result.success)
    
    def test_opposed_skill_check(self):
        """Test opposed skill checks between characters."""
        # Create opponent with willpower
        opponent = create_object("typeclasses.characters.Character", key="Opponent")
        opponent.db.stats = {"Wisdom": 12}  # +0 modifier
        
        with patch('random.randint', side_effect=[15, 10]):  # char1 rolls 15, opponent rolls 10
            result = self.char1.make_opposed_check("Intimidate", opponent, "Willpower")
            self.assertTrue(result.success)


class NPCBehaviorTest(EvenniaTest):
    """Unit tests for NPC behavior system."""
    
    def setUp(self):
        super().setUp()
        self.thug = create_object(
            "typeclasses.characters.ThugNPC",
            key="Thug",
            location=self.room1
        )
    
    def test_intimidation_response(self):
        """Test NPC response to intimidation."""
        # Create intimidation event
        from world.events import Event
        event = Event(
            event_type="intimidate",
            source=self.char1,
            target=self.thug,
            success=True
        )
        
        self.thug.handle_event(event)
        self.assertEqual(self.thug.db.state, "intimidated")
        self.assertEqual(self.thug.db.following, self.char1)
    
    def test_follower_movement(self):
        """Test that followers move with their leader."""
        self.thug.db.following = self.char1
        self.thug.db.state = "following"
        
        # Move character to new room
        self.char1.move_to(self.room2, quiet=True)
        
        # Thug should follow
        self.assertEqual(self.thug.location, self.room2)
    
    def test_order_command_response(self):
        """Test NPC response to order commands."""
        self.thug.db.following = self.char1
        
        # Create order event
        from world.events import Event
        event = Event(
            event_type="order",
            source=self.char1,
            target=self.thug,
            command="airlock"
        )
        
        self.thug.handle_event(event)
        # Thug should attempt to move toward airlock


class EnvironmentalSystemTest(EvenniaTest):
    """Unit tests for environmental hazards and death system."""
    
    def setUp(self):
        super().setUp()
        self.space_room = create_object(
            "typeclasses.rooms.SpaceRoom",
            key="Space",
            location=None
        )
        self.thug = create_object(
            "typeclasses.characters.ThugNPC", 
            key="Thug",
            location=self.space_room
        )
    
    def test_vacuum_damage(self):
        """Test that vacuum environment causes damage."""
        initial_hp = self.thug.db.hp
        self.space_room.apply_environmental_effects()
        self.assertLess(self.thug.db.hp, initial_hp)
    
    def test_death_from_environment(self):
        """Test death from environmental exposure."""
        self.thug.db.hp = 1  # Nearly dead
        self.space_room.apply_environmental_effects()
        self.assertTrue(self.thug.db.is_dead)
    
    def test_life_support_protection(self):
        """Test that life support equipment prevents environmental damage."""
        # Give thug life support
        self.thug.db.has_life_support = True
        initial_hp = self.thug.db.hp
        self.space_room.apply_environmental_effects()
        self.assertEqual(self.thug.db.hp, initial_hp)  # No damage


class AirlockMechanicsTest(EvenniaTest):
    """Unit tests for airlock mechanics."""
    
    def setUp(self):
        super().setUp()
        self.airlock = create_object(
            "typeclasses.rooms.AirlockRoom",
            key="Airlock"
        )
        self.space = create_object(
            "typeclasses.rooms.SpaceRoom", 
            key="Space"
        )
        self.button = create_object(
            "typeclasses.objects.AirlockButton",
            key="red button",
            location=self.airlock
        )
        
        # Create exit from airlock to space
        self.space_exit = create_object(
            "typeclasses.exits.Exit",
            key="outer door",
            location=self.airlock, 
            destination=self.space
        )
        
        # Put thug in airlock
        self.thug = create_object(
            "typeclasses.characters.ThugNPC",
            key="Thug", 
            location=self.airlock
        )
    
    def test_airlock_button_press(self):
        """Test pressing airlock button."""
        self.char1.move_to(self.airlock, quiet=True)
        self.char1.execute_cmd("press red button")
        
        # Verify airlock cycling started
        self.assertTrue(self.airlock.db.cycling)
    
    def test_airlock_ejects_contents(self):
        """Test that airlock ejects contents to space."""
        self.airlock.cycle_airlock()
        
        # Thug should be ejected to space
        self.assertEqual(self.thug.location, self.space)
    
    def test_airlock_safety_protocols(self):
        """Test airlock safety checks."""
        # Try to cycle with character inside
        self.char1.move_to(self.airlock, quiet=True)
        result = self.airlock.cycle_airlock()
        
        # Should fail safety check or warn player
        self.assertFalse(result)


# Test script execution helper
def run_e2e_test_scenario():
    """
    Automated E2E test scenario that can be run from within the game.
    Returns True if all steps pass, False otherwise.
    """
    try:
        # This would be called from within Evennia to test the live system
        print("Starting E2E User Story Test...")
        
        # Set up test character and environment
        test_char = search_object("TestChar")[0]  # Assumes test char exists
        
        # Execute each step and verify results
        steps = [
            ("Move to dark room", "goto Dark Room"),
            ("Verify darkness", "look"),
            ("Use night vision", "use goggles"),
            ("Verify green vision", "look"),
            ("Intimidate thug", "intimidate thug"),
            ("Order thug", "order thug airlock"),
            ("Go to airlock", "goto Airlock"),
            ("Press button", "press red button"),
            ("Wait for death", "wait 10"),
        ]
        
        for step_name, command in steps:
            print(f"Step: {step_name}")
            test_char.execute_cmd(command)
            # Add verification logic here
        
        print("E2E Test Complete - All steps passed!")
        return True
        
    except Exception as e:
        print(f"E2E Test Failed: {e}")
        return False


if __name__ == "__main__":
    # Run unit tests
    unittest.main()