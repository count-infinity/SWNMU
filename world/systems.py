"""
Centralized game systems implementing ECS-style architecture.

This module contains the core systems that handle game mechanics in a
centralized, reusable way. Systems operate on data from behaviors and
character attributes to provide consistent game mechanics.
"""

import random
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
from world.tables import attribute_modifier_tbl, lookup


@dataclass
class SkillCheckResult:
    """Result of a skill check with detailed information."""
    success: bool
    roll: int
    target_number: int
    skill_level: int
    attribute_modifier: int
    difficulty_modifier: int
    total_modifier: int
    margin: int  # How much over/under the target


class SkillSystem:
    """
    Centralized system for handling all skill-based mechanics.
    
    Provides unified skill resolution using SWN mechanics:
    - Roll 2d6 + skill level + attribute modifier + situational modifiers
    - Compare against difficulty number
    """
    
    # Standard difficulty numbers for SWN
    DIFFICULTY_TRIVIAL = 6
    DIFFICULTY_EASY = 8
    DIFFICULTY_MODERATE = 10
    DIFFICULTY_HARD = 12
    DIFFICULTY_EXTREME = 14
    DIFFICULTY_IMPOSSIBLE = 16
    
    @classmethod
    def make_skill_check(
        cls, 
        character, 
        skill_name: str, 
        difficulty: int = DIFFICULTY_MODERATE,
        attribute: str = None,
        modifiers: Dict[str, int] = None
    ) -> SkillCheckResult:
        """
        Make a skill check using SWN mechanics.
        
        Args:
            character: Character making the check
            skill_name: Name of the skill to check
            difficulty: Target difficulty number
            attribute: Override attribute (if None, uses skill's default)
            modifiers: Dict of situational modifiers {"source": value}
            
        Returns:
            SkillCheckResult with detailed information about the check
        """
        modifiers = modifiers or {}
        
        # Get skill level (0 if untrained)
        skill_level = cls._get_skill_level(character, skill_name)
        
        # Get attribute modifier
        attribute_modifier = cls._get_attribute_modifier(character, skill_name, attribute)
        
        # Calculate total modifier
        difficulty_modifier = sum(modifiers.values())
        total_modifier = skill_level + attribute_modifier + difficulty_modifier
        
        # Roll 2d6
        roll = random.randint(1, 6) + random.randint(1, 6)
        
        # Calculate result
        total_roll = roll + total_modifier
        success = total_roll >= difficulty
        margin = total_roll - difficulty
        
        return SkillCheckResult(
            success=success,
            roll=roll,
            target_number=difficulty,
            skill_level=skill_level,
            attribute_modifier=attribute_modifier,
            difficulty_modifier=difficulty_modifier,
            total_modifier=total_modifier,
            margin=margin
        )
    
    @classmethod
    def _get_skill_level(cls, character, skill_name: str) -> int:
        """Get character's skill level, defaulting to 0 if untrained."""
        if not hasattr(character, 'skills'):
            return 0
        
        skill_data = character.skills.get(skill_name)
        if not skill_data:
            return 0
            
        return skill_data.get('level', 0)
    
    @classmethod
    def _get_attribute_modifier(cls, character, skill_name: str, override_attr: str = None) -> int:
        """Get the attribute modifier for a skill check."""
        # Skill-to-attribute mapping (SWN defaults)
        skill_attributes = {
            'Hack': 'int',
            'Program': 'int',
            'Fix': 'int',
            'Know': 'int',
            'Notice': 'wis',
            'Survive': 'wis',
            'Connect': 'wis',
            'Heal': 'int',
            'Talk': 'cha',
            'Lead': 'cha',
            'Trade': 'cha',
            'Perform': 'cha',
            'Exert': 'str',
            'Punch': 'str',
            'Stab': 'dex',
            'Shoot': 'dex',
            'Sneak': 'dex',
            'Pilot': 'dex',
        }
        
        # Use override or default attribute
        attr_name = override_attr or skill_attributes.get(skill_name, 'int')
        
        # Get character's attribute value
        attr_value = getattr(character.db, attr_name, 10)  # Default to 10
        
        # Look up modifier from SWN table
        modifier = lookup(attr_value, attribute_modifier_tbl) or 0
        
        return modifier


class HackableSystem:
    """
    System for handling hacking attempts using the SkillSystem.
    
    Provides consistent hacking mechanics that can be extended
    for different types of hackable systems.
    """
    
    @classmethod
    def attempt_hack(cls, hacker, target, hackable_config, event=None) -> Dict[str, Any]:
        """
        Attempt to hack a target using unified skill mechanics.
        
        Args:
            hacker: Character attempting the hack
            target: Object being hacked  
            hackable_config: HackableBehavior instance with configuration
            event: Optional event for context/history
            
        Returns:
            Dict with hack result information
        """
        print("Attempting to hack.")
        # Build modifiers based on hackable configuration
        modifiers = {}
        
        # Security level affects difficulty
        if hasattr(hackable_config, 'security_level'):
            security_modifier = -(hackable_config.security_level - 1) * 2
            modifiers['security'] = security_modifier
        
        # Check for special equipment/circumstances
        if cls._has_hacking_tools(hacker):
            modifiers['tools'] = 2
        
        if cls._target_is_powered_down(target):
            modifiers['powered_down'] = 4
            
        # Make the skill check
        result = SkillSystem.make_skill_check(
            character=hacker,
            skill_name='Hack',
            difficulty=hackable_config.difficulty,
            modifiers=modifiers
        )
        
        # Handle hack consequences
        hack_result = {
            'skill_result': result,
            'hacker': hacker,
            'target': target,
            'time_taken': getattr(hackable_config, 'hack_time', 5),
            'security_triggered': False
        }
        
        if result.success:
            cls._handle_successful_hack(hack_result, hackable_config)
        else:
            cls._handle_failed_hack(hack_result, hackable_config)
        
        print("Adding to event history")
        # Add to event history if provided
        if event:
            print("Appending to event history")
            event.history.append(
                f"Hack {'succeeded' if result.success else 'failed'} - "
                f"Roll: {result.roll}, Target: {result.target_number}, "
                f"Total: {result.roll + result.total_modifier}, "
                f"Margin: {result.margin}"
            )
        
        return hack_result
    
    @classmethod
    def _has_hacking_tools(cls, hacker) -> bool:
        """Check if hacker has specialized hacking equipment."""
        # This could check for specific items in inventory
        # For now, simplified check
        return False
    
    @classmethod
    def _target_is_powered_down(cls, target) -> bool:
        """Check if target system is powered down (easier to hack)."""
        # This could check target's power state
        return False
    
    @classmethod
    def _handle_successful_hack(cls, hack_result: Dict[str, Any], config):
        """Handle the consequences of a successful hack."""
        hacker = hack_result['hacker']
        target = hack_result['target']
        margin = hack_result['skill_result'].margin
        
        # Better success with higher margin
        if margin >= 6:
            hacker.msg(f"Exceptional hack of {target.name}! You gain admin access.")
            hack_result['access_level'] = 'admin'
        elif margin >= 3:
            hacker.msg(f"Clean hack of {target.name}. You gain user access.")
            hack_result['access_level'] = 'user'
        else:
            hacker.msg(f"You successfully hack {target.name}, but it's noticed.")
            hack_result['access_level'] = 'user'
            hack_result['security_triggered'] = True
            
        # Notify target (if it can receive messages)
        if hasattr(target, 'msg') and not hack_result.get('access_level') == 'admin':
            target.msg(f"SECURITY ALERT: Unauthorized access detected from {hacker.name}")
    
    @classmethod
    def _handle_failed_hack(cls, hack_result: Dict[str, Any], config):
        """Handle the consequences of a failed hack."""
        hacker = hack_result['hacker']
        target = hack_result['target']
        margin = hack_result['skill_result'].margin
        
        # Worse failure with larger negative margin
        if margin <= -6:
            hacker.msg(f"Critical failure hacking {target.name}! You trigger security alerts.")
            hack_result['security_triggered'] = True
            hack_result['detected'] = True
            # Could trigger additional consequences here
        elif margin <= -3:
            hacker.msg(f"Failed to hack {target.name}. Security systems notice the attempt.")
            hack_result['security_triggered'] = True
        else:
            hacker.msg(f"Failed to hack {target.name}, but the attempt goes unnoticed.")
            
        # Notify target of security breach
        if hack_result.get('security_triggered') and hasattr(target, 'msg'):
            target.msg(f"SECURITY BREACH: Failed hack attempt from {hacker.name}")


class CombatSystem:
    """
    Placeholder for future combat system implementation.
    Would follow similar patterns to SkillSystem and HackableSystem.
    """
    pass


class SocialSystem:
    """
    Placeholder for social interaction system (persuasion, intimidation, etc.).
    Would use SkillSystem for core mechanics with social-specific consequences.
    """
    pass