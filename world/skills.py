class SkillHandler:
    def __init__(self, obj):
        self.obj = obj
        self._load()

    def _load(self):
        self.skill_data = self.obj.attributes.get(
            "skill_data", default={}, category="skills")

    def _save(self):
        self.obj.attributes.add(
            "skill_data", self.skill_data, category="skills")
        self._load()

    def all(self):
        return self.skill_data
    
    def get(self, skill_key):
        return self.skill_data.get(skill_key)
    
    def add(self, skill):
        self.skill_data[skill["key"]]=skill
        self._save()
    def remove(self, skill_key):
        del self.skill_data[skill_key]
        self._save()


from evennia.commands.command import Command as BaseCommand


class CmdHack(BaseCommand):
    """
    Use the Hack skill to attempt to hack a target.
    
    Usage:
        hack <target>
        
    This command allows you to use your Hack skill against a target
    that has Hackable behavior. Uses the centralized SkillSystem
    for consistent mechanics and detailed feedback.
    """
    
    key = "hack"
    locks = "cmd:all()"
    arg_regex = r"\s|$"
    help_category = "Skills"

    def func(self):
        from world.events import Event, GlobalEventHandler
        from world.systems import SkillSystem
        
        caller = self.caller
        
        if not self.args:
            caller.msg("Hack what? Usage: hack <target>")
            return
            
        target = caller.search(self.args.strip())
        if not target:
            return
            
        # Check if caller has Hack skill (allow untrained attempts)
        skill_level = SkillSystem._get_skill_level(caller, 'Hack')
        if skill_level == 0:
            caller.msg("You attempt to hack without proper training (untrained penalty applies).")
            
        # Check if target is hackable
        if not hasattr(target, 'behaviors') or not target.behaviors.get('hackable'):
            caller.msg(f"{target.name} is not hackable.")
            return
            
        # Create and handle the Hack event
        hack_event = Event(
            event_type="hack",
            source=caller,
            target=target,
            skill_name="Hack"
        )
        
        GlobalEventHandler.handleEvent(hack_event)
        
        # The event handling now provides detailed feedback through the systems
        # No need for additional messages here as HackableSystem handles it


class BehaviorHandler:
    def __init__(self, obj):
        self.obj = obj
        self._load()

    def _load(self):
        self.behavior_data = self.obj.attributes.get(
            "behavior_data", default={}, category="behaviors")

    def _save(self):
        self.obj.attributes.add(
            "behavior_data", self.behavior_data, category="behaviors")
        self._load()

    def all(self):
        return self.behavior_data
    
    def get(self, behavior_key):
        return self.behavior_data.get(behavior_key)
    
    def add(self, behavior):
        self.behavior_data[behavior.key] = behavior
        self._save()
        
    def remove(self, behavior_key):
        del self.behavior_data[behavior_key]
        self._save()
        
    def handle_event(self, event):
        """Loop through all behaviors and let them handle the event."""
        for behavior_key, behavior in self.behavior_data.items():
            if hasattr(behavior, 'handle_event'):
                behavior.handle_event(event)


class HackableBehavior:
    """
    Lean behavior that configures an object to be hackable.
    Contains only configuration data - logic is handled by HackableSystem.
    """
    
    key = "hackable"
    
    def __init__(self, difficulty=10, hack_time=5, security_level=1, system_type="generic"):
        """
        Initialize hackable behavior with security parameters.
        
        Args:
            difficulty (int): SWN difficulty number for hacking (6-16)
            hack_time (int): Time in seconds required to complete hack
            security_level (int): Security level (1-10, affects modifiers)
            system_type (str): Type of system (affects available actions)
        """
        self.difficulty = difficulty
        self.hack_time = hack_time
        self.security_level = security_level
        self.system_type = system_type
    
    def handle_event(self, event):
        """Handle events by delegating to appropriate system."""
        if event.event_type == "hack":
            from world.systems import HackableSystem
            hack_result = HackableSystem.attempt_hack(
                event.source, event.target, self, event
            )
            
            # Set event cancellation based on result
            if not hack_result['skill_result'].success:
                event.context.cancelled = True