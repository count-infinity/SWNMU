"""
Lighting System Commands

Commands for managing and interacting with the dynamic lighting system.
"""

from evennia.commands.command import Command
from world.lighting import LightSource


class CmdLighting(Command):
    """
    Check or modify room lighting.
    
    Usage:
        lighting
        lighting info
        lighting set <level>
        lighting type <type>
        lighting modifier <name> <change> [duration]
        lighting remove <modifier>
        
    Shows current lighting conditions or allows builders to modify them.
    Light levels range from 0 (pitch black) to 10 (bright daylight).
    Types: indoor, outdoor, space, underground
    """
    
    key = "lighting"
    aliases = ["light"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        
        if not args or args[0] == "info":
            self._show_lighting_info(caller)
        elif args[0] == "set" and len(args) >= 2:
            self._set_light_level(caller, args[1])
        elif args[0] == "type" and len(args) >= 2:
            self._set_lighting_type(caller, args[1])
        elif args[0] == "modifier" and len(args) >= 3:
            duration = int(args[3]) if len(args) >= 4 else None
            self._add_modifier(caller, args[1], args[2], duration)
        elif args[0] == "remove" and len(args) >= 2:
            self._remove_modifier(caller, args[1])
        else:
            caller.msg("Usage: lighting [info|set <level>|type <type>|modifier <name> <change> [duration]|remove <modifier>]")
    
    def _show_lighting_info(self, caller):
        """Show detailed lighting information."""
        room = caller.location
        if not hasattr(room, 'lighting'):
            caller.msg("This room doesn't support lighting.")
            return
        
        lighting = room.lighting
        current_level = lighting.get_current_light_level()
        visibility, color_code = lighting.get_visibility_description(caller)
        
        info = f"""
|cLIGHT INFORMATION|n
Current Light Level: {current_level}/10
Base Light Level: {lighting.base_light_level}
Lighting Type: {lighting.lighting_type}
Your Visibility: {visibility}
Vision Type: {caller.get_vision_type() if hasattr(caller, 'get_vision_type') else 'normal'}

|cLight Sources:|n"""
        
        # Show light sources in room
        sources_found = False
        for obj in room.contents:
            if hasattr(obj, 'light_output') and obj.db.is_light_active:
                output = obj.light_output()
                info += f"  {obj.name}: +{output} light"
                sources_found = True
        
        if not sources_found:
            info += "  None active"
        
        # Show light modifiers
        info += "\n\n|cLight Modifiers:|n"
        if lighting.light_modifiers:
            for name, data in lighting.light_modifiers.items():
                change = data.get('light_change', 0)
                sign = "+" if change >= 0 else ""
                info += f"  {name}: {sign}{change} light"
                if 'expires_at' in data:
                    from evennia.utils import gametime
                    remaining = data['expires_at'] - gametime.gametime()
                    info += f" ({remaining}s remaining)"
                info += "\n"
        else:
            info += "  None"
        
        caller.msg(info)
    
    def _set_light_level(self, caller, level_str):
        """Set base light level (builders only)."""
        if not caller.check_permstring("builders"):
            caller.msg("You don't have permission to modify lighting.")
            return
        
        try:
            level = int(level_str)
            caller.location.lighting.set_base_light_level(level)
            caller.msg(f"Base light level set to {level}.")
        except ValueError:
            caller.msg("Light level must be a number between 0 and 10.")
    
    def _set_lighting_type(self, caller, lighting_type):
        """Set lighting type (builders only)."""
        if not caller.check_permstring("builders"):
            caller.msg("You don't have permission to modify lighting.")
            return
        
        valid_types = ["indoor", "outdoor", "space", "underground"]
        if lighting_type not in valid_types:
            caller.msg(f"Invalid lighting type. Valid types: {', '.join(valid_types)}")
            return
        
        caller.location.lighting.set_lighting_type(lighting_type)
        caller.msg(f"Lighting type set to {lighting_type}.")
    
    def _add_modifier(self, caller, name, change_str, duration):
        """Add light modifier (builders only)."""
        if not caller.check_permstring("builders"):
            caller.msg("You don't have permission to modify lighting.")
            return
        
        try:
            change = int(change_str)
            caller.location.lighting.add_light_modifier(name, change, duration)
            duration_text = f" for {duration} seconds" if duration else ""
            caller.msg(f"Added lighting modifier '{name}': {change:+d} light{duration_text}.")
        except ValueError:
            caller.msg("Light change must be a number.")
    
    def _remove_modifier(self, caller, name):
        """Remove light modifier (builders only)."""
        if not caller.check_permstring("builders"):
            caller.msg("You don't have permission to modify lighting.")
            return
        
        caller.location.lighting.remove_light_modifier(name)
        caller.msg(f"Removed lighting modifier '{name}'.")


class CmdUse(Command):
    """
    Use/activate an object.
    
    Usage:
        use <object>
        
    Activates equipment or interactive objects. For light sources,
    this turns them on or off.
    """
    
    key = "use"
    aliases = ["activate"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"
    help_category = "General"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Use what? Usage: use <object>")
            return
        
        # Search for the object
        target = caller.search(self.args.strip())
        if not target:
            return
        
        # Check if it has light source or night vision behaviors
        if hasattr(target, 'behaviors'):
            light_behavior = target.behaviors.get('light_source')
            vision_behavior = target.behaviors.get('night_vision')
            
            if light_behavior:
                self._use_light_source(caller, target, light_behavior)
            elif vision_behavior:
                self._use_vision_enhancement(caller, target, vision_behavior)
            elif hasattr(target, 'use'):
                # Generic use method
                result = target.use(caller)
                if isinstance(result, tuple):
                    success, message = result
                    caller.msg(message)
                else:
                    caller.msg(f"You use the {target.name}.")
            else:
                caller.msg(f"You can't use the {target.name}.")
        else:
            caller.msg(f"You can't use the {target.name}.")
    
    def _use_light_source(self, caller, target, light_behavior):
        """Use a light source (toggle on/off)."""
        if light_behavior.is_active:
            # Turn off
            success, message = light_behavior.deactivate(target, caller)
        else:
            # Turn on
            success, message = light_behavior.activate(target, caller)
        
        caller.msg(message)
    
    def _use_vision_enhancement(self, caller, target, vision_behavior):
        """Use vision enhancement (toggle on/off)."""
        if vision_behavior.is_active:
            # Turn off
            success, message = vision_behavior.deactivate(target, caller)
        else:
            # Turn on
            success, message = vision_behavior.activate(target, caller)
        
        caller.msg(message)


class CmdPress(Command):
    """
    Press a button or switch.
    
    Usage:
        press <button>
        
    Activates buttons, switches, and other pressable objects.
    """
    
    key = "press"
    aliases = ["push", "activate"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"
    help_category = "General"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Press what? Usage: press <button>")
            return
        
        # Search for the object
        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return
        
        # Check if it has a press method
        if hasattr(target, 'press'):
            result = target.press(caller)
            if isinstance(result, tuple):
                success, message = result
                caller.msg(message)
            else:
                caller.msg(f"You press the {target.name}.")
        elif hasattr(target, 'use'):
            # Fall back to generic use
            result = target.use(caller)
            if isinstance(result, tuple):
                success, message = result
                caller.msg(message)
            else:
                caller.msg(f"You press the {target.name}.")
        else:
            caller.msg(f"You can't press the {target.name}.")


# Example usage and scenarios
def create_lighting_examples():
    """
    Examples of how the lighting system works in practice.
    """
    
    examples = """
# LIGHTING SYSTEM EXAMPLES

## Scenario 1: Dark Room with Flashlight
```
> look
It's too dark to see anything.

> get flashlight
You pick up a sturdy LED flashlight.

> use flashlight
You activate the flashlight. A bright beam cuts through the darkness.

> look
Dark Storage Room (lit by flashlight)
This room is shrouded in complete darkness, but your flashlight reveals
old storage containers and dusty shelves lining the walls.
```

## Scenario 2: Night Vision Goggles
```
> wear goggles
You put on the night vision goggles.

> use goggles
The night vision goggles activate with a soft hum. Everything takes on a green tint.

> look
Dark Storage Room (night vision active)
This room is shrouded in complete darkness. Through your night vision goggles,
you can see old storage containers and dusty shelves lining the walls.
(Night vision active - everything has a green tint)
```

## Scenario 3: Outdoor Day/Night Cycle
```
# During the day:
> look
Spaceport Plaza
A bustling plaza outside the main spaceport terminal. Ships come and go
overhead while travelers hurry between buildings.

# At night:
> look  
Spaceport Plaza (dimly lit)
A plaza outside the main spaceport terminal. The area is dimly lit by
scattered streetlights, with ships visible as lights moving overhead.
(The area is dimly lit)
```

## Scenario 4: Emergency Lighting
```
> lighting modifier power_failure -4 3600
Added lighting modifier 'power_failure': -4 light for 3600 seconds.

The area becomes darker.

> look
Engineering Bay (emergency lighting)
The main lighting has failed, leaving only red emergency lights casting
eerie shadows throughout the engineering bay.
```

## Scenario 5: Environmental Effects
```
# Space room without life support:
> look
It's too dark to see anything.

> use night vision goggles
The night vision goggles activate with a soft hum. Everything takes on a green tint.

> look
Outer Space (night vision active)
The infinite void of space stretches out in all directions, dotted with
distant stars. Without proper life support, you won't survive long here.
(Night vision active - everything has a green tint)

You are taking environmental damage from vacuum exposure!
```

## Builder Commands:
```
> lighting info
Current Light Level: 2/10
Base Light Level: 0  
Lighting Type: indoor
Your Visibility: night_vision
Vision Type: normal

Light Sources:
  flashlight: +3 light
  
Light Modifiers:
  emergency_lights: +1 light

> lighting set 5
Base light level set to 5.

> lighting type outdoor  
Lighting type set to outdoor.

> lighting modifier storm -3 1800
Added lighting modifier 'storm': -3 light for 1800 seconds.
```
"""
    
    return examples


def test_lighting_scenarios():
    """
    Test function showing lighting system in action.
    """
    from evennia import create_object
    from typeclasses.rooms import DarkRoom, SpaceRoom, AirlockRoom
    from world.lighting import NightVisionGoggles, Flashlight, Torch
    
    print("Creating test lighting scenario...")
    
    # Create rooms
    dark_room = create_object(DarkRoom, key="Test Dark Room")
    space_room = create_object(SpaceRoom, key="Test Space")
    airlock = create_object(AirlockRoom, key="Test Airlock")
    
    # Create light sources
    flashlight = create_object(Flashlight, key="flashlight", location=dark_room)
    goggles = create_object(NightVisionGoggles, key="night vision goggles", location=dark_room)
    torch = create_object(Torch, key="torch", location=dark_room)
    
    print("Test objects created successfully!")
    print("Light levels:")
    print(f"  Dark room: {dark_room.lighting.get_current_light_level()}")
    print(f"  Space room: {space_room.lighting.get_current_light_level()}")
    print(f"  Airlock: {airlock.lighting.get_current_light_level()}")
    
    # Test light source
    flashlight.activate_light()
    print(f"  Dark room with flashlight: {dark_room.lighting.get_current_light_level()}")
    
    # Test modifiers
    dark_room.lighting.add_light_modifier("test", 2, 60)
    print(f"  Dark room with modifier: {dark_room.lighting.get_current_light_level()}")
    
    return dark_room, space_room, airlock, flashlight, goggles, torch