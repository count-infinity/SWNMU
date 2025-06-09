"""
Test Commands for User Story E2E Testing

These commands allow easy execution of tests from within the game.
"""

from evennia.commands.command import Command
from world.e2e_test_runner import test_runner


class CmdRunE2ETest(Command):
    """
    Run the complete E2E user story test.
    
    Usage:
        teste2e
        teste2e quick
        
    This command will create a test environment and run through
    the complete user story scenario, testing all systems.
    
    The 'quick' option runs just a basic smoke test.
    """
    
    key = "teste2e"
    aliases = ["test_e2e", "e2etest"]
    locks = "cmd:perm(Builder)"
    help_category = "Testing"
    
    def func(self):
        caller = self.caller
        
        if "quick" in self.args.lower():
            # Run quick smoke test
            caller.msg("Running quick smoke test...")
            from world.e2e_test_runner import run_quick_test
            success = run_quick_test(caller)
            
            if success:
                caller.msg("|gQuick test completed successfully!|n")
            else:
                caller.msg("|rQuick test failed. Check logs for details.|n")
        else:
            # Run full E2E test
            caller.msg("Starting full E2E user story test...")
            caller.msg("This will create test objects and run through the complete scenario.")
            caller.msg("Please wait while the test executes...")
            
            success = test_runner.run_full_scenario(caller)
            
            if success:
                caller.msg("|gAll E2E tests passed! The user story implementation is working correctly.|n")
            else:
                caller.msg("|rSome E2E tests failed. Check the detailed report above and logs for issues.|n")


class CmdTestUnit(Command):
    """
    Run unit tests for specific systems.
    
    Usage:
        testunit
        testunit lighting
        testunit equipment  
        testunit skills
        testunit npc
        testunit environment
        
    Run unit tests for the user story implementation.
    Without arguments, runs all unit tests.
    """
    
    key = "testunit"
    aliases = ["test_unit", "unittest"]
    locks = "cmd:perm(Builder)"
    help_category = "Testing"
    
    def func(self):
        caller = self.caller
        test_type = self.args.strip().lower()
        
        caller.msg("Running unit tests...")
        
        if not test_type or test_type == "all":
            # Run all unit tests
            from world.test_user_story import *
            import unittest
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = unittest.TestSuite()
            
            # Add all test classes
            suite.addTests(loader.loadTestsFromTestCase(LightingSystemTest))
            suite.addTests(loader.loadTestsFromTestCase(EquipmentSystemTest))
            suite.addTests(loader.loadTestsFromTestCase(SkillCheckSystemTest))
            suite.addTests(loader.loadTestsFromTestCase(NPCBehaviorTest))
            suite.addTests(loader.loadTestsFromTestCase(EnvironmentalSystemTest))
            suite.addTests(loader.loadTestsFromTestCase(AirlockMechanicsTest))
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            if result.wasSuccessful():
                caller.msg(f"|gAll {result.testsRun} unit tests passed!|n")
            else:
                caller.msg(f"|r{len(result.failures)} test(s) failed, {len(result.errors)} error(s)|n")
                
        else:
            # Run specific test category
            test_classes = {
                'lighting': 'LightingSystemTest',
                'equipment': 'EquipmentSystemTest', 
                'skills': 'SkillCheckSystemTest',
                'npc': 'NPCBehaviorTest',
                'environment': 'EnvironmentalSystemTest',
                'airlock': 'AirlockMechanicsTest'
            }
            
            if test_type in test_classes:
                caller.msg(f"Running {test_type} tests...")
                # This would need to be implemented to run specific test classes
                caller.msg(f"Specific test execution for {test_type} not yet implemented.")
            else:
                caller.msg(f"Unknown test type: {test_type}")
                caller.msg(f"Available types: {', '.join(test_classes.keys())}")


class CmdTestSetup(Command):
    """
    Set up test environment manually.
    
    Usage:
        testsetup
        testsetup clean
        
    Creates all test objects needed for manual testing.
    Use 'clean' to remove test objects.
    """
    
    key = "testsetup" 
    aliases = ["test_setup"]
    locks = "cmd:perm(Builder)"
    help_category = "Testing"
    
    def func(self):
        caller = self.caller
        
        if "clean" in self.args.lower():
            # Clean up test environment
            caller.msg("Cleaning up test environment...")
            test_runner.cleanup_test_environment()
            caller.msg("Test environment cleaned up.")
        else:
            # Set up test environment
            caller.msg("Setting up test environment...")
            if test_runner.setup_test_environment():
                caller.msg("|gTest environment created successfully!|n")
                caller.msg("You can now manually test the user story scenario.")
                caller.msg("Test objects have 'test' or 't' prefixes in their names/aliases.")
            else:
                caller.msg("|rFailed to set up test environment. Check logs for details.|n")


class CmdTestStatus(Command):
    """
    Show current test environment status.
    
    Usage:
        teststatus
        
    Shows what test objects currently exist and their states.
    """
    
    key = "teststatus"
    aliases = ["test_status"]
    locks = "cmd:perm(Builder)"
    help_category = "Testing"
    
    def func(self):
        caller = self.caller
        
        caller.msg("=== TEST ENVIRONMENT STATUS ===")
        
        if not test_runner.test_objects:
            caller.msg("No test objects currently exist.")
            return
        
        for name, obj in test_runner.test_objects.items():
            if obj and not obj.db_is_deleted:
                status = f"|g{name}|n: {obj.name} (#{obj.id}) - {obj.location}"
            else:
                status = f"|r{name}|n: DELETED or MISSING"
            caller.msg(f"  {status}")
        
        caller.msg("=== END STATUS ===")


# Add these commands to the default command set by importing in default_cmdsets.py