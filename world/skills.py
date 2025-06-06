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
    that has Hackable behavior. The event will be propagated to the
    target for handling.
    """
    
    key = "hack"
    locks = "cmd:all()"
    arg_regex = r"\s|$"
    help_category = "Skills"

    def func(self):
        from world.events import Event, GlobalEventHandler
        
        caller = self.caller
        
        if not self.args:
            caller.msg("Hack what? Usage: hack <target>")
            return
            
        target = caller.search(self.args.strip())
        if not target:
            return
            
        # Check if caller has Hack skill
        if not hasattr(caller, 'skills') or not caller.skills.all().get('Hack'):
            caller.msg("You don't have the Hack skill.")
            return
            
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
        
        if not hack_event.context.cancelled:
            caller.msg(f"You attempt to hack {target.name}.")
        else:
            caller.msg(f"Your hack attempt on {target.name} was blocked.")


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
    Behavior that allows objects to be hacked.
    Add this to an object's behaviors to make it hackable.
    """
    
    key = "hackable"
    
    def __init__(self, difficulty=10, hack_time=5, security_level=1):
        """
        Initialize hackable behavior with security parameters.
        
        Args:
            difficulty (int): Base difficulty for hacking (higher = harder)
            hack_time (int): Time in seconds required to complete hack
            security_level (int): Security level (1-10, higher = more secure)
        """
        self.difficulty = difficulty
        self.hack_time = hack_time
        self.security_level = security_level
    
    def handle_event(self, event):
        """Handle events, specifically hack events."""
        if event.event_type == "hack":
            self.handle_hack_event(event)
    
    def handle_hack_event(self, event):
        """
        Handle a hack event. Override this method in subclasses
        to implement specific hack behavior.
        """
        hacker = event.source
        target = event.target
        
        # Calculate success chance based on difficulty and security level
        base_success = 0.7  # Base 70% success rate
        difficulty_modifier = self.difficulty * 0.05  # 5% per difficulty point
        security_modifier = self.security_level * 0.08  # 8% per security level
        
        success_chance = max(0.1, base_success - difficulty_modifier - security_modifier)
        
        import random
        if random.random() < success_chance:
            hacker.msg(f"You successfully hack {target.name}! (Difficulty: {self.difficulty}, Security: {self.security_level})")
            target.msg(f"You have been hacked by {hacker.name}!")
            event.history.append(f"Hack successful - Difficulty: {self.difficulty}, Time: {self.hack_time}s")
        else:
            hacker.msg(f"Your hack attempt on {target.name} fails. (Difficulty: {self.difficulty}, Security: {self.security_level})")
            target.msg(f"{hacker.name} attempted to hack you but failed.")
            event.history.append(f"Hack failed - Difficulty: {self.difficulty}, Security: {self.security_level}")
            event.context.cancelled = True