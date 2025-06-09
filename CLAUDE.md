# SWNMU - Stars Without Number Evennia MUD

## Project Overview
This is an Evennia-based MUD implementing the Stars Without Number tabletop RPG system. The project focuses on creating a text-based multiplayer game with sci-fi themes, character progression, skills, and interactive systems.

## Key Systems

### Core Architecture
- **Base Framework**: Evennia MUD engine
- **Game Setting**: Stars Without Number (SWN) sci-fi RPG system
- **Server Name**: SWNMU
- **Python Version**: Compatible with Evennia requirements

### Character System (`typeclasses/characters.py`, `world/chargen.py`)
- Character creation menu system using EvMenu
- SWN character attributes (stats, background, class, foci)
- Background-based skill allocation with Growth/Learning options
- Class selection (Warrior, Expert, Psychic, Adventurer)
- Focus selection for special abilities
- Equipment allocation based on background/class

### Skills System (`world/skills.py`)
- `SkillHandler`: Manages character skills with persistent storage
- Skills stored as character attributes in "skills" category
- Skill-based commands (e.g., `CmdHack` for hacking systems)
- Integration with behavior and event systems

### Behavior System (`world/skills.py`, `typeclasses/objects.py`)
- `BehaviorHandler`: Manages object behaviors with persistent storage
- `HackableBehavior`: Makes objects hackable with difficulty/security levels
- Behaviors respond to events through `handle_event()` method
- Stored as object attributes in "behaviors" category

### Event System (`world/events.py`)
- `Event`: Core event class with source, target, type, and context
- `EventContext`: Manages event state (cancellation, etc.)
- `GlobalEventHandler`: Processes events through pre/during/post phases
- Event propagation to source, target, and location objects
- Event history tracking for debugging/logging

### Object Framework (`typeclasses/objects.py`)
- `ObjectParent`: Mixin for common functionality across all game objects
- `Object`: Root object class inheriting from Evennia's DefaultObject
- Integration with behaviors and event handling
- Base for all game entities (items, rooms, exits, characters)

### Data Tables (`world/tables.py`, `world/utils.py`)
- Character backgrounds with descriptions, skills, and bonuses
- Stat generation and rendering utilities
- Game tables for character creation and gameplay

## Technical Patterns

### Handler Pattern
- `SkillHandler` and `BehaviorHandler` use lazy_property for efficient loading
- Handlers manage persistent data through Evennia's attribute system
- Consistent `_load()`, `_save()`, `add()`, `remove()`, `get()`, `all()` interface

### Event-Driven Architecture
- Objects communicate through events rather than direct method calls
- Events propagate through multiple phases (pre/during/post)
- Behaviors and objects can respond to or modify events
- Event context allows cancellation and state management

### Menu System
- Character creation uses EvMenu for complex branching workflows
- Menus save progress and allow resumption
- Standard navigation patterns (next, back, abort)
- Table-based display of options and character data

## Current Implementation Status
- ✅ Basic character creation with stats, background, class, foci
- ✅ Skills system with persistent storage
- ✅ Behavior system for object interactions
- ✅ Event system for game actions
- ✅ Hack skill implementation as example
- 🔄 Equipment system (basic placeholder)
- 🔄 Combat system (not yet implemented)
- 🔄 Character sheet finalization and character object creation

## Development Guidelines

### Code Style
- Follow Evennia conventions and patterns
- Use type hints where appropriate
- Prefer composition over inheritance for behaviors
- Keep handlers lightweight and focused
- Use lazy_property for expensive operations

### Adding New Systems
1. Consider if it needs a handler (for persistent data)
2. Determine if it should use the event system
3. Create appropriate behaviors if objects need to interact
4. Add menu nodes if player interaction is required
5. Update relevant table data if needed

### Testing
- Test file: `world/test_tables.py` for table data
- Use `world/test_utils.py` for utility functions
- Test character creation flows thoroughly
- Verify event propagation and behavior responses

## Testing Framework

### Evennia Testing Integration
The project uses Evennia's built-in testing framework with custom extensions for comprehensive validation.

#### Running Tests
```bash
# Run all game-specific tests
evennia test --settings settings.py .

# Run specific test modules
evennia test --settings settings.py world.test_user_story
evennia test --settings settings.py world.test_tables
evennia test --settings settings.py world.test_utils

# Run Evennia core tests (optional)
evennia test evennia
```

#### Test Structure
- **Test Files**: Must be named `test*.py` (e.g., `test_user_story.py`)
- **Test Classes**: Inherit from `EvenniaTest` or `EvenniaCommandTest`
- **Test Methods**: Must start with `test_` prefix
- **Setup/Teardown**: Use `setUp()` and `tearDown()` for test preparation

#### Test Types
1. **Unit Tests**: Individual system components (`world/test_*.py`)
   - Use `EvenniaTest` for object testing with pre-configured `.char1`, `.room1`, etc.
   - Use `EvenniaCommandTest` for command testing with `.call()` method

2. **E2E Tests**: Complete scenario automation (`world/e2e_test_runner.py`)
   - Automated test environment setup and cleanup
   - Full user story scenario validation
   - In-game test commands for manual execution

3. **Integration Tests**: Cross-system validation
   - Event propagation testing
   - Behavior interaction validation
   - Handler persistence testing

#### Example Test Pattern
```python
from evennia.utils.test_resources import EvenniaTest

class TestSkillSystem(EvenniaTest):
    def setUp(self):
        super().setUp()
        # Test-specific setup using self.char1, self.room1, etc.
    
    def test_skill_check(self):
        # Test implementation
        result = self.char1.make_skill_check("Intimidate", 12)
        self.assertTrue(result.success)
```

#### In-Game Testing Commands
- `teste2e` - Run complete E2E user story test
- `testunit` - Run specific unit test suites
- `testsetup` - Create/cleanup test environment
- `teststatus` - Show test object status

## Common Development Tasks
- Adding new skills: Update skill tables, create command class, implement behaviors
- Creating new behaviors: Implement behavior class with `handle_event()` method
- Extending character creation: Add new menu nodes and update navigation
- Adding new events: Define event type, implement handlers in relevant objects
- Creating interactive objects: Add behaviors and event responses
- Writing tests: Use EvenniaTest base classes, follow naming conventions, test both success/failure cases

## Files to Reference
- `typeclasses/` - Core game object definitions
- `world/skills.py` - Skills and behaviors implementation
- `world/events.py` - Event system architecture
- `world/chargen.py` - Character creation menus
- `world/tables.py` - Game data and character options
- `world/test_*.py` - Unit test suites
- `world/e2e_test_runner.py` - E2E test automation
- `commands/test_commands.py` - In-game testing commands
- `server/conf/settings.py` - Game configuration

This project emphasizes modularity, extensibility, faithful adaptation of the SWN tabletop experience, and comprehensive testing to ensure system reliability.