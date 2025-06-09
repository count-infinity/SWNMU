"""
Room

Rooms with integrated lighting system that supports:
- Dynamic light levels based on time, weather, events
- Light sources (torches, flashlights, etc.)
- Different vision types (normal, night vision, etc.)
- Environmental lighting changes

"""

from evennia.objects.objects import DefaultRoom
from evennia.utils.utils import lazy_property

from .objects import ObjectParent
from world.lighting import LightingHandler


class Room(ObjectParent, DefaultRoom):
    """
    Room with dynamic lighting support.
    
    This room class integrates the lighting system to provide:
    - Dynamic light levels based on time, weather, events
    - Light sources (torches, flashlights, etc.)
    - Different vision types (normal, night vision, etc.)
    - Environmental lighting changes
    
    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """
    
    @lazy_property
    def lighting(self):
        """Lighting handler for this room."""
        return LightingHandler(self)
    
    def return_appearance(self, looker, **kwargs):
        """
        Override to respect lighting conditions.
        
        This is the core integration point - it modifies what players
        see based on current lighting and their vision capabilities.
        """
        
        # Check lighting conditions for this character
        visibility, color_code = self.lighting.get_visibility_description(looker)
        
        if visibility == "too_dark":
            # Character can't see anything
            return "|KIt's too dark to see anything.|n"
        
        # Get the normal room appearance
        appearance = super().return_appearance(looker, **kwargs)
        
        # Apply color coding for special vision types
        if color_code:
            # Wrap the entire appearance in color codes
            lines = appearance.split('\n')
            colored_lines = [f"{color_code}{line}|n" if line.strip() else line for line in lines]
            appearance = '\n'.join(colored_lines)
        
        # Add lighting context information
        lighting_context = self._get_lighting_context(visibility)
        if lighting_context:
            appearance += f"\n{lighting_context}"
        
        return appearance
    
    def _get_lighting_context(self, visibility):
        """Get contextual information about current lighting."""
        context_messages = {
            "night_vision": "|g(Night vision active - everything has a green tint)|n",
            "dim": "|y(The area is dimly lit)|n", 
            "dark": "|K(You can barely make out shapes in the darkness)|n",
        }
        return context_messages.get(visibility, "")
    
    def at_object_creation(self):
        """Set up default lighting when room is created."""
        super().at_object_creation()
        self._setup_default_lighting()
    
    def _setup_default_lighting(self):
        """Configure default lighting based on room characteristics."""
        name_lower = self.name.lower()
        desc_lower = (self.db.desc or "").lower()
        
        # Determine lighting type from name/description
        if any(keyword in name_lower or keyword in desc_lower 
               for keyword in ["space", "vacuum", "void"]):
            self.lighting.set_lighting_type("space")
            self.lighting.set_base_light_level(0)
            
        elif any(keyword in name_lower or keyword in desc_lower 
                 for keyword in ["outdoor", "outside", "street", "plaza"]):
            self.lighting.set_lighting_type("outdoor")
            self.lighting.set_base_light_level(3)
            
        elif any(keyword in name_lower or keyword in desc_lower 
                 for keyword in ["underground", "cave", "tunnel", "mine"]):
            self.lighting.set_lighting_type("underground")  
            self.lighting.set_base_light_level(1)
            
        elif any(keyword in name_lower or keyword in desc_lower 
                 for keyword in ["dark", "shadows", "dim"]):
            self.lighting.set_lighting_type("indoor")
            self.lighting.set_base_light_level(1)
            
        else:
            # Default indoor lighting
            self.lighting.set_lighting_type("indoor")
            self.lighting.set_base_light_level(5)
    
    def handle_event(self, event):
        """Handle lighting-related events."""
        super().handle_event(event)
        
        if event.event_type == "lighting_change":
            self._on_lighting_change(event)
        elif event.event_type == "time_change":
            self._on_time_change(event)
        elif event.event_type == "weather_change":
            self._on_weather_change(event)
    
    def _on_lighting_change(self, event):
        """Handle when lighting changes in the room."""
        new_level = event.new_light_level
        
        # Notify characters if lighting changed significantly
        old_level = getattr(event, 'old_light_level', new_level)
        
        if abs(new_level - old_level) >= 2:
            if new_level > old_level:
                self.msg_contents("The area becomes brighter.")
            else:
                self.msg_contents("The area becomes darker.")
    
    def _on_time_change(self, event):
        """Handle time of day changes for outdoor areas."""
        if self.lighting.lighting_type == "outdoor":
            # Trigger lighting recalculation
            self.lighting._trigger_lighting_change_event()
    
    def _on_weather_change(self, event):
        """Handle weather changes affecting lighting."""
        weather = event.weather_type
        
        if self.lighting.lighting_type == "outdoor":
            if weather == "storm":
                self.lighting.add_light_modifier("storm", -2, duration=3600)
            elif weather == "fog":
                self.lighting.add_light_modifier("fog", -1, duration=1800)
            elif weather == "clear":
                self.lighting.remove_light_modifier("storm")
                self.lighting.remove_light_modifier("fog")


class DarkRoom(Room):
    """
    A room that's specifically designed to be dark.
    
    This is an example of how you can create specialized room types
    while still using the flexible lighting system.
    """
    
    def _setup_default_lighting(self):
        """Dark rooms start with no light."""
        self.lighting.set_lighting_type("indoor")
        self.lighting.set_base_light_level(0)
        
        # Add some atmosphere
        if not self.db.desc:
            self.db.desc = "This room is shrouded in complete darkness."


class SpaceRoom(Room):
    """
    A room representing the vacuum of space.
    
    Space rooms are extremely dark and have environmental hazards.
    """
    
    def _setup_default_lighting(self):
        """Space is very dark."""
        self.lighting.set_lighting_type("space")
        self.lighting.set_base_light_level(0)
        
        if not self.db.desc:
            self.db.desc = "The infinite void of space stretches out in all directions, dotted with distant stars."
    
    def at_object_creation(self):
        """Set up space room with environmental hazards."""
        super().at_object_creation()
        
        # Space rooms have vacuum environment
        self.db.environment_type = "vacuum"
        self.db.breathable = False
        
        # Start environmental effects script
        self._start_environmental_script()
    
    def _start_environmental_script(self):
        """Start script that applies environmental damage."""
        from evennia.scripts.scripts import DefaultScript
        
        class SpaceEnvironmentScript(DefaultScript):
            def at_script_creation(self):
                self.key = f"space_env_{self.obj.id}"
                self.desc = "Space environmental effects"
                self.interval = 10  # Check every 10 seconds
                self.persistent = True
            
            def at_repeat(self):
                self.obj.apply_environmental_effects()
        
        # Only create if doesn't exist
        if not self.scripts.get("space_env"):
            SpaceEnvironmentScript.create(key="space_env", obj=self)
    
    def apply_environmental_effects(self):
        """Apply space environment effects to contents."""
        for obj in self.contents:
            if hasattr(obj, 'take_environmental_damage'):
                if not getattr(obj.db, 'has_life_support', False):
                    obj.take_environmental_damage("vacuum", 2)


class AirlockRoom(Room):
    """
    An airlock room with special cycling mechanics.
    """
    
    def _setup_default_lighting(self):
        """Airlocks have emergency lighting."""
        self.lighting.set_lighting_type("indoor")
        self.lighting.set_base_light_level(3)
        
        # Add emergency lighting modifier
        self.lighting.add_light_modifier("emergency_lighting", 1)
        
        if not self.db.desc:
            self.db.desc = "A sterile airlock chamber with reinforced walls and emergency lighting."
    
    def at_object_creation(self):
        """Set up airlock-specific attributes."""
        super().at_object_creation()
        
        self.db.is_cycling = False
        self.db.cycle_time = 10  # 10 seconds to cycle
        self.db.environment_type = "normal"
    
    def cycle_airlock(self):
        """Cycle the airlock, ejecting contents to space."""
        if self.db.is_cycling:
            return False, "Airlock is already cycling!"
        
        # Check for safety protocols
        characters_present = [obj for obj in self.contents 
                            if hasattr(obj, 'has_account') and obj.has_account]
        
        if characters_present:
            # Warning message
            self.msg_contents("|rWARNING: Characters detected in airlock! Cycling will commence in 5 seconds.|n")
            
            # Delay before cycling
            from evennia.utils import delay
            delay(5, self._execute_cycle)
        else:
            self._execute_cycle()
        
        return True, "Airlock cycling initiated..."
    
    def _execute_cycle(self):
        """Execute the actual airlock cycle."""
        self.db.is_cycling = True
        
        # Lighting effects during cycling
        self.lighting.add_light_modifier("cycling_lights", -2, duration=self.db.cycle_time)
        
        self.msg_contents("|rAIRLOCK CYCLING! Emergency lighting activated.|n")
        self.msg_contents("|rKlaxons blare as the outer door begins to open...|n")
        
        # Eject contents after cycle time
        from evennia.utils import delay
        delay(self.db.cycle_time, self._eject_contents)
    
    def _eject_contents(self):
        """Eject all contents to space."""
        # Find space exit
        space_exit = None
        for exit_obj in self.exits:
            if hasattr(exit_obj.destination, 'lighting') and \
               exit_obj.destination.lighting.lighting_type == "space":
                space_exit = exit_obj
                break
        
        if not space_exit:
            self.msg_contents("|rError: No space exit found!|n")
            self.db.is_cycling = False
            return
        
        # Move all contents except exits and built-in objects
        ejected_objects = []
        for obj in self.contents[:]:  # Copy list to avoid modification during iteration
            if not obj.destination:  # Not an exit
                obj.move_to(space_exit.destination, quiet=True)
                ejected_objects.append(obj.name)
        
        if ejected_objects:
            self.msg_contents(f"|rEjected to space: {', '.join(ejected_objects)}|n")
            
            # Notify space room
            space_exit.destination.msg_contents(
                f"|rObjects ejected from airlock: {', '.join(ejected_objects)}|n"
            )
        
        # Reset airlock
        self.db.is_cycling = False
        self.lighting.remove_light_modifier("cycling_lights")
        self.msg_contents("|gAirlock cycle complete. Chamber sealed.|n")
