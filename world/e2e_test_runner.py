"""
E2E Test Runner for User Story

This script can be executed within Evennia to automatically test 
the complete user story scenario. It creates all necessary objects,
runs through each step, and verifies the results.

Usage:
  From within Evennia: py exec(open('world/e2e_test_runner.py').read())
  Or via command: @py world.e2e_test_runner.run_full_scenario()
"""

from evennia import create_object, search_object
from evennia.utils import logger
import time

class E2ETestRunner:
    """Automated test runner for the user story scenario."""
    
    def __init__(self):
        self.test_objects = {}
        self.test_character = None
        self.step_results = []
        
    def setup_test_environment(self):
        """Create all objects needed for testing."""
        logger.log_info("Setting up test environment...")
        
        try:
            # Create dark room
            self.test_objects['dark_room'] = create_object(
                "typeclasses.rooms.DarkRoom",
                key="Test Dark Room",
                aliases=["test_dark"]
            )
            
            # Create airlock
            self.test_objects['airlock'] = create_object(
                "typeclasses.rooms.AirlockRoom", 
                key="Test Airlock",
                aliases=["test_airlock"]
            )
            
            # Create space room
            self.test_objects['space'] = create_object(
                "typeclasses.rooms.SpaceRoom",
                key="Test Space",
                aliases=["test_space"]
            )
            
            # Create exits
            self.test_objects['airlock_exit'] = create_object(
                "typeclasses.exits.Exit",
                key="test airlock",
                aliases=["tairlock"],
                location=self.test_objects['dark_room'],
                destination=self.test_objects['airlock']
            )
            
            self.test_objects['space_exit'] = create_object(
                "typeclasses.exits.Exit",
                key="test outer door", 
                aliases=["touter"],
                location=self.test_objects['airlock'],
                destination=self.test_objects['space']
            )
            
            # Create night vision goggles
            self.test_objects['goggles'] = create_object(
                "typeclasses.objects.NightVisionGoggles",
                key="test night vision goggles",
                aliases=["tgoggles"],
                location=self.test_objects['dark_room']
            )
            
            # Create thug NPC
            self.test_objects['thug'] = create_object(
                "typeclasses.characters.ThugNPC",
                key="Test Thug",
                aliases=["tthug"],
                location=self.test_objects['dark_room']
            )
            
            # Create red button
            self.test_objects['button'] = create_object(
                "typeclasses.objects.AirlockButton",
                key="test red button",
                aliases=["tbutton"],
                location=self.test_objects['airlock']
            )
            
            logger.log_info("Test environment setup complete!")
            return True
            
        except Exception as e:
            logger.log_err(f"Failed to setup test environment: {e}")
            return False
    
    def prepare_test_character(self, character):
        """Prepare a character for testing."""
        self.test_character = character
        
        # Move to dark room
        character.move_to(self.test_objects['dark_room'], quiet=True)
        
        # Give character the goggles
        self.test_objects['goggles'].move_to(character, quiet=True)
        
        # Ensure character has intimidate skill
        if not hasattr(character, 'skills'):
            from world.skills import SkillHandler
            character.skills = SkillHandler(character)
        
        character.skills.add({
            "key": "Intimidate", 
            "level": 1,
            "stat": "Charisma"
        })
        
        # Set character stats if not present
        if not character.db.stats:
            character.db.stats = {
                "Charisma": 14,  # +1 modifier
                "Strength": 12,
                "Dexterity": 12,
                "Constitution": 12, 
                "Intelligence": 12,
                "Wisdom": 12
            }
        
        logger.log_info(f"Character {character.name} prepared for testing")
        return True
    
    def execute_step(self, step_num, description, command, expected_result=None):
        """Execute a single test step and verify results."""
        logger.log_info(f"Step {step_num}: {description}")
        
        try:
            # Capture messages before command
            old_msg_count = len(getattr(self.test_character, '_msg_buffer', []))
            
            # Execute command
            self.test_character.execute_cmd(command)
            
            # Give time for async operations
            time.sleep(0.1)
            
            # Check for expected result if provided
            success = True
            if expected_result:
                # This would need to be customized based on how you want to verify results
                success = self.verify_step_result(expected_result)
            
            result = {
                'step': step_num,
                'description': description,
                'command': command,
                'success': success,
                'error': None
            }
            
            self.step_results.append(result)
            logger.log_info(f"Step {step_num} {'PASSED' if success else 'FAILED'}")
            return success
            
        except Exception as e:
            error_result = {
                'step': step_num,
                'description': description, 
                'command': command,
                'success': False,
                'error': str(e)
            }
            self.step_results.append(error_result)
            logger.log_err(f"Step {step_num} FAILED: {e}")
            return False
    
    def verify_step_result(self, expected_result):
        """Verify that a step produced the expected result."""
        # This is a simplified verification - you'd extend this based on specific needs
        
        if expected_result == "darkness":
            # Check if character sees darkness message
            return self.test_objects['dark_room'].db.is_dark
        
        elif expected_result == "green_vision":
            # Check if night vision is active
            return self.test_character.db.night_vision_active
        
        elif expected_result == "thug_following":
            # Check if thug is following character
            return (self.test_objects['thug'].db.following == self.test_character)
        
        elif expected_result == "thug_in_airlock":
            # Check if thug moved to airlock
            return (self.test_objects['thug'].location == self.test_objects['airlock'])
        
        elif expected_result == "thug_in_space":
            # Check if thug was ejected to space
            return (self.test_objects['thug'].location == self.test_objects['space'])
        
        elif expected_result == "thug_dead":
            # Check if thug is dead
            return self.test_objects['thug'].db.is_dead
        
        return True
    
    def run_full_scenario(self, character):
        """Run the complete user story scenario."""
        logger.log_info("Starting E2E User Story Test Scenario...")
        
        # Setup
        if not self.setup_test_environment():
            return False
        
        if not self.prepare_test_character(character):
            return False
        
        # Execute test steps
        steps = [
            (1, "Character sees darkness in dark room", "look", "darkness"),
            (2, "Character gets night vision goggles", "get tgoggles", None),
            (3, "Character wears night vision goggles", "wear tgoggles", None),
            (4, "Character activates night vision", "use tgoggles", None),
            (5, "Character sees room in green with night vision", "look", "green_vision"),
            (6, "Character intimidates thug", "intimidate tthug", "thug_following"),
            (7, "Character orders thug to airlock", "order tthug tairlock", "thug_in_airlock"),
            (8, "Character goes to airlock", "tairlock", None),
            (9, "Character presses red button", "press tbutton", "thug_in_space"),
            (10, "Wait for thug to die from exposure", "wait 10", "thug_dead")
        ]
        
        passed_steps = 0
        for step_data in steps:
            if self.execute_step(*step_data):
                passed_steps += 1
        
        # Generate report
        self.generate_test_report(passed_steps, len(steps))
        
        # Cleanup
        self.cleanup_test_environment()
        
        success = (passed_steps == len(steps))
        logger.log_info(f"E2E Test {'PASSED' if success else 'FAILED'} - {passed_steps}/{len(steps)} steps successful")
        return success
    
    def generate_test_report(self, passed, total):
        """Generate a detailed test report."""
        report = f"""
=== E2E USER STORY TEST REPORT ===
Total Steps: {total}
Passed: {passed}
Failed: {total - passed}
Success Rate: {(passed/total)*100:.1f}%

Step Details:
"""
        
        for result in self.step_results:
            status = "PASS" if result['success'] else "FAIL"
            error_info = f" - Error: {result['error']}" if result['error'] else ""
            report += f"  {result['step']:2d}. {status} - {result['description']}{error_info}\n"
        
        report += "\n=== END REPORT ===\n"
        
        logger.log_info(report)
        
        # Also send report to character if available
        if self.test_character:
            self.test_character.msg(report)
    
    def cleanup_test_environment(self):
        """Clean up test objects after testing."""
        logger.log_info("Cleaning up test environment...")
        
        try:
            for obj_name, obj in self.test_objects.items():
                if obj and not obj.db_is_deleted:
                    obj.delete()
            
            self.test_objects.clear()
            logger.log_info("Test environment cleanup complete")
            
        except Exception as e:
            logger.log_err(f"Error during cleanup: {e}")


# Global test runner instance
test_runner = E2ETestRunner()

def run_full_scenario(character=None):
    """
    Run the full E2E test scenario.
    
    Args:
        character: Character object to use for testing. If None, will try to find caller.
    """
    if not character:
        # Try to get character from current session (if called from in-game)
        try:
            character = caller  # This works when called from @py command
        except NameError:
            logger.log_err("No character provided for testing")
            return False
    
    return test_runner.run_full_scenario(character)

def run_quick_test(character=None):
    """Run a quick smoke test of key functionality."""
    if not character:
        try:
            character = caller
        except NameError:
            logger.log_err("No character provided for testing")
            return False
    
    logger.log_info("Running quick smoke test...")
    
    # Just test basic functionality without full scenario
    try:
        # Test object creation
        test_room = create_object("typeclasses.rooms.Room", key="Quick Test Room")
        
        # Test character movement
        character.move_to(test_room, quiet=True)
        
        # Cleanup
        test_room.delete()
        
        logger.log_info("Quick test PASSED")
        character.msg("Quick test completed successfully!")
        return True
        
    except Exception as e:
        logger.log_err(f"Quick test FAILED: {e}")
        character.msg(f"Quick test failed: {e}")
        return False

# Usage examples:
# From @py command: world.e2e_test_runner.run_full_scenario(me)
# From script: exec(open('world/e2e_test_runner.py').read()); run_full_scenario(me)