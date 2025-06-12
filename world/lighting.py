
"""
Dynamic Lighting System

A flexible lighting system that supports:
- Dynamic light levels based on time, weather, events
- Multiple light sources (torches, flashlights, etc.)
- Different vision types (normal, night vision, etc.)
- Environmental lighting changes
"""

from evennia.utils.utils import lazy_property
from world.events import Event, GlobalEventHandler
import random


class LightingHandler:
    """
    Manages lighting for a room with dynamic light sources and modifiers.
    """
    
    def __init__(self, room):
        self.room = room
        self._load()
    
    def _load(self):
        """Load lighting data from room attributes."""
        # Base light level (0-10 scale)
        # 0 = Pitch black, 5 = Normal indoor, 10 = Bright daylight
        self.base_light_level = self.room.attributes.get(
            "base_light_level", default=5, category="lighting"
        )
        
        # Current light modifiers (temporary effects)
        self.light_modifiers = self.room.attributes.get(
            "light_modifiers", default={}, category="lighting"
        )
        
        # Room lighting type affects base calculations
        self.lighting_type = self.room.attributes.get(
            "lighting_type", default="indoor", category="lighting"
        )
    
    def _save(self):
        """Save lighting data to room attributes."""
        self.room.attributes.add(
            "base_light_level", self.base_light_level, category="lighting"
        )
        self.room.attributes.add(
            "light_modifiers", self.light_modifiers, category="lighting"
        )
        self.room.attributes.add(
            "lighting_type", self.lighting_type, category="lighting"
        )
    
    def get_current_light_level(self):
        """
        Calculate the current effective light level in the room.
        Combines base lighting, light sources, and modifiers.
        """
        total_light = self.base_light_level
        
        # Add light from portable and fixed sources
        total_light += self._calculate_light_sources()
        
        # Apply temporary modifiers
        total_light += self._calculate_light_modifiers()
        
        # Apply environmental effects
        total_light += self._calculate_environmental_lighting()
        
        # Clamp to valid range
        return max(0, min(10, total_light))
    
    def _calculate_light_sources(self):
        """Calculate light contribution from objects in the room."""
        light_bonus = 0
        
        # Check all objects in room for light source behaviors
        for obj in self.room.contents:
            if hasattr(obj, 'behaviors'):
                light_behavior = obj.behaviors.get('light_source')
                if light_behavior:
                    light_output = light_behavior.get_light_output(obj)
                    light_bonus += light_output
        
        return light_bonus
    
    def _calculate_light_modifiers(self):
        """Calculate light from temporary modifiers."""
        modifier_total = 0
        expired_modifiers = []
        
        for modifier_name, modifier_data in self.light_modifiers.items():
            # Check if modifier has expired
            if 'expires_at' in modifier_data:
                from evennia.utils import gametime
                if gametime.gametime() > modifier_data['expires_at']:
                    expired_modifiers.append(modifier_name)
                    continue
            
            modifier_total += modifier_data.get('light_change', 0)
        
        # Remove expired modifiers
        for modifier in expired_modifiers:
            del self.light_modifiers[modifier]
        
        if expired_modifiers:
            self._save()
        
        return modifier_total
    
    def _calculate_environmental_lighting(self):
        """Calculate environmental lighting effects (time of day, weather, etc.)."""
        if self.lighting_type == "outdoor":
            return self._get_outdoor_lighting()
        elif self.lighting_type == "space":
            return -8  # Space is very dark
        elif self.lighting_type == "underground":
            return -3  # Underground is darker
        else:
            return 0  # Indoor lighting is stable
    
    def _get_outdoor_lighting(self):
        """Calculate outdoor lighting based on time of day."""
        from evennia.utils import gametime
        
        # Simple day/night cycle (could be expanded)
        current_time = gametime.gametime()
        hour = (current_time // 3600) % 24  # Hours in 24-hour cycle
        
        if 6 <= hour <= 18:  # Daytime
            return 3  # Bright outdoor light
        elif 19 <= hour <= 21 or 5 <= hour <= 6:  # Dawn/dusk
            return -1  # Dim light
        else:  # Nighttime
            return -4  # Dark but not pitch black (stars/moon)
    
    def add_light_modifier(self, name, light_change, duration=None):
        """Add a temporary lighting modifier."""
        modifier_data = {'light_change': light_change}
        
        if duration:
            from evennia.utils import gametime
            modifier_data['expires_at'] = gametime.gametime() + duration
        
        self.light_modifiers[name] = modifier_data
        self._save()
        
        # Notify room of lighting change
        self._trigger_lighting_change_event()
    
    def remove_light_modifier(self, name):
        """Remove a lighting modifier."""
        if name in self.light_modifiers:
            del self.light_modifiers[name]
            self._save()
            self._trigger_lighting_change_event()
    
    def set_base_light_level(self, level):
        """Set the base light level for the room."""
        self.base_light_level = max(0, min(10, level))
        self._save()
        self._trigger_lighting_change_event()
    
    def set_lighting_type(self, lighting_type):
        """Set the room's lighting type (indoor, outdoor, space, underground)."""
        self.lighting_type = lighting_type
        self._save()
        self._trigger_lighting_change_event()
    
    def _trigger_lighting_change_event(self):
        """Trigger an event when lighting changes."""
        lighting_event = Event(
            event_type="lighting_change",
            source=self.room,
            target=self.room,
            new_light_level=self.get_current_light_level()
        )
        GlobalEventHandler.handleEvent(lighting_event)
    
    def can_see_normally(self, character, required_light_level=3):
        """Check if a character can see normally in current lighting."""
        current_light = self.get_current_light_level()
        character_vision = character.get_vision_capability()
        
        effective_light = current_light + character_vision.get('light_bonus', 0)
        return effective_light >= required_light_level
    
    def get_visibility_description(self, character):
        """Get description of visibility for a character."""
        current_light = self.get_current_light_level()
        vision_type = character.get_vision_type()
        
        if current_light >= 7:
            return "bright", ""
        elif current_light >= 4:
            return "normal", ""
        elif current_light >= 1:
            if vision_type == "night_vision":
                return "night_vision", "|g"  # Green tint for night vision
            elif vision_type == "low_light":
                return "dim", "|y"  # Yellow tint for low light
            else:
                return "dark", ""
        else:  # current_light == 0
            if vision_type == "night_vision":
                return "night_vision", "|g"
            else:
                return "too_dark", ""


class LightSourceHandler:
    """
    Handler for objects that can provide light. Uses composition instead of inheritance.
    """
    
    def __init__(self, obj):
        self.obj = obj
        self._load()
    
    def _load(self):
        """Load light source data from object attributes."""
        self.is_active = self.obj.attributes.get(
            "is_light_active", default=False, category="light_source"
        )
        self.light_intensity = self.obj.attributes.get(
            "light_intensity", default=1, category="light_source"
        )
        self.fuel_remaining = self.obj.attributes.get(
            "fuel_remaining", default=None, category="light_source"
        )
        self.battery_remaining = self.obj.attributes.get(
            "battery_remaining", default=None, category="light_source"
        )
    
    def _save(self):
        """Save light source data to object attributes."""
        self.obj.attributes.add(
            "is_light_active", self.is_active, category="light_source"
        )
        self.obj.attributes.add(
            "light_intensity", self.light_intensity, category="light_source"
        )
        if self.fuel_remaining is not None:
            self.obj.attributes.add(
                "fuel_remaining", self.fuel_remaining, category="light_source"
            )
        if self.battery_remaining is not None:
            self.obj.attributes.add(
                "battery_remaining", self.battery_remaining, category="light_source"
            )
    
    def get_light_output(self):
        """Calculate how much light this object provides."""
        if not self.is_active:
            return 0
        
        # Check fuel/battery depletion
        if self.fuel_remaining is not None and self.fuel_remaining <= 0:
            self.is_active = False
            self._save()
            return 0
        
        if self.battery_remaining is not None and self.battery_remaining <= 0:
            self.is_active = False
            self._save()
            return 0
        
        # Battery level affects brightness for battery-powered items
        if self.battery_remaining is not None:
            battery_factor = max(0.3, self.battery_remaining / 100.0)
            return int(self.light_intensity * battery_factor)
        
        return self.light_intensity
    
    def activate(self):
        """Turn on the light source."""
        # Check fuel/battery
        if self.fuel_remaining is not None and self.fuel_remaining <= 0:
            return False, "The light source has no fuel remaining."
        
        if self.battery_remaining is not None and self.battery_remaining <= 0:
            return False, "The battery is dead."
        
        self.is_active = True
        self._save()
        
        # Trigger lighting change in current location
        if self.obj.location and hasattr(self.obj.location, 'lighting'):
            self.obj.location.lighting._trigger_lighting_change_event()
        
        return True, f"You activate the {self.obj.name}."
    
    def deactivate(self):
        """Turn off the light source."""
        self.is_active = False
        self._save()
        
        # Trigger lighting change in current location
        if self.obj.location and hasattr(self.obj.location, 'lighting'):
            self.obj.location.lighting._trigger_lighting_change_event()
        
        return True, f"You deactivate the {self.obj.name}."
    
    def consume_fuel(self, amount=1):
        """Consume fuel/battery power."""
        if self.fuel_remaining is not None:
            self.fuel_remaining = max(0, self.fuel_remaining - amount)
            
            if self.fuel_remaining <= 0 and self.is_active:
                self.deactivate()
                if self.obj.location:
                    self.obj.location.msg_contents(f"The {self.obj.name} flickers and goes out.")
        
        if self.battery_remaining is not None:
            self.battery_remaining = max(0, self.battery_remaining - amount)
            
            if self.battery_remaining <= 0 and self.is_active:
                self.deactivate()
                if self.obj.location:
                    self.obj.location.msg_contents(f"The {self.obj.name}'s battery dies.")
        
        self._save()
    
    def set_light_intensity(self, intensity):
        """Set the light intensity."""
        self.light_intensity = max(0, intensity)
        self._save()
    
    def set_fuel(self, amount):
        """Set fuel amount."""
        self.fuel_remaining = max(0, amount)
        self._save()
    
    def set_battery(self, amount):
        """Set battery amount."""
        self.battery_remaining = max(0, min(100, amount))
        self._save()


class VisionHandler:
    """
    Manages character vision capabilities.
    """
    
    def __init__(self, character):
        self.character = character
        self._load()
    
    def _load(self):
        """Load vision data from character attributes."""
        self.vision_type = self.character.attributes.get(
            "vision_type", default="normal", category="vision"
        )
        self.vision_modifiers = self.character.attributes.get(
            "vision_modifiers", default={}, category="vision"
        )
    
    def _save(self):
        """Save vision data to character attributes."""
        self.character.attributes.add(
            "vision_type", self.vision_type, category="vision"
        )
        self.character.attributes.add(
            "vision_modifiers", self.vision_modifiers, category="vision"
        )
    
    def get_vision_type(self):
        """Get the character's current vision type."""
        # Check for temporary vision changes from equipment
        if self.character.db.night_vision_active:
            return "night_vision"
        elif self.character.db.low_light_active:
            return "low_light"
        else:
            return self.vision_type
    
    def get_vision_capability(self):
        """Get the character's vision capabilities."""
        vision_type = self.get_vision_type()
        
        capabilities = {
            "normal": {"light_bonus": 0, "min_light": 3},
            "low_light": {"light_bonus": 2, "min_light": 2},
            "night_vision": {"light_bonus": 5, "min_light": 0},
            "thermal": {"light_bonus": 3, "min_light": 1},
        }
        
        return capabilities.get(vision_type, capabilities["normal"])
    
    def add_vision_modifier(self, name, modifier_type, duration=None):
        """Add a temporary vision modifier."""
        modifier_data = {'type': modifier_type}
        
        if duration:
            from evennia.utils import gametime
            modifier_data['expires_at'] = gametime.gametime() + duration
        
        self.vision_modifiers[name] = modifier_data
        self._save()


class LightSourceBehavior:
    """
    Behavior that makes any object a light source.
    Add this to an object's behaviors to make it emit light.
    """
    
    key = "light_source"
    
    def __init__(self, light_intensity=2, fuel_type=None, fuel_amount=None, battery_amount=None):
        """
        Initialize light source behavior.
        
        Args:
            light_intensity (int): How much light this source provides (1-5)
            fuel_type (str): Type of fuel ("fuel", "battery", or None for permanent)
            fuel_amount (int): Starting fuel amount (for fuel-based)
            battery_amount (int): Starting battery amount (0-100 for battery-based)
        """
        self.light_intensity = light_intensity
        self.fuel_type = fuel_type
        self.fuel_amount = fuel_amount
        self.battery_amount = battery_amount
        self.is_active = False
    
    def get_light_output(self, obj):
        """Calculate how much light this object provides."""
        if not self.is_active:
            return 0
        
        # Check fuel/battery depletion
        if self.fuel_type == "fuel" and self.fuel_amount is not None:
            if self.fuel_amount <= 0:
                self.is_active = False
                return 0
        
        if self.fuel_type == "battery" and self.battery_amount is not None:
            if self.battery_amount <= 0:
                self.is_active = False
                return 0
            # Battery level affects brightness
            battery_factor = max(0.3, self.battery_amount / 100.0)
            return int(self.light_intensity * battery_factor)
        
        return self.light_intensity
    
    def activate(self, obj, user=None):
        """Turn on the light source."""
        # Check fuel/battery
        if self.fuel_type == "fuel" and self.fuel_amount is not None and self.fuel_amount <= 0:
            return False, f"The {obj.name} has no fuel remaining."
        
        if self.fuel_type == "battery" and self.battery_amount is not None and self.battery_amount <= 0:
            return False, f"The {obj.name}'s battery is dead."
        
        self.is_active = True
        
        # Start fuel consumption for fuel-based items
        if self.fuel_type == "fuel" and self.fuel_amount is not None:
            self._start_fuel_consumption(obj)
        
        # Trigger lighting change in current location
        if obj.location and hasattr(obj.location, 'lighting'):
            obj.location.lighting._trigger_lighting_change_event()
        
        return True, f"You activate the {obj.name}."
    
    def deactivate(self, obj, user=None):
        """Turn off the light source."""
        self.is_active = False
        
        # Stop fuel consumption
        if hasattr(obj, 'scripts') and obj.scripts.get(f"fuel_burn_{obj.id}"):
            obj.scripts.get(f"fuel_burn_{obj.id}").stop()
        
        # Trigger lighting change in current location
        if obj.location and hasattr(obj.location, 'lighting'):
            obj.location.lighting._trigger_lighting_change_event()
        
        return True, f"You deactivate the {obj.name}."
    
    def _start_fuel_consumption(self, obj):
        """Start fuel consumption script for fuel-based light sources."""
        from evennia.scripts.scripts import DefaultScript
        
        class FuelBurnScript(DefaultScript):
            def at_script_creation(self):
                self.key = f"fuel_burn_{self.obj.id}"
                self.desc = "Fuel burning script"
                self.interval = 60  # Consume fuel every minute
                self.persistent = True
            
            def at_repeat(self):
                behavior = self.obj.behaviors.get('light_source')
                if behavior:
                    behavior.consume_fuel(self.obj, 1)
                    if behavior.fuel_amount <= 0:
                        self.stop()
        
        # Only create if doesn't exist
        if hasattr(obj, 'scripts') and not obj.scripts.get(f"fuel_burn_{obj.id}"):
            FuelBurnScript.create(key=f"fuel_burn_{obj.id}", obj=obj)
    
    def consume_fuel(self, obj, amount=1):
        """Consume fuel/battery power."""
        if self.fuel_type == "fuel" and self.fuel_amount is not None:
            self.fuel_amount = max(0, self.fuel_amount - amount)
            
            if self.fuel_amount <= 0 and self.is_active:
                self.deactivate(obj)
                if obj.location:
                    obj.location.msg_contents(f"The {obj.name} flickers and goes out.")
        
        if self.fuel_type == "battery" and self.battery_amount is not None:
            self.battery_amount = max(0, self.battery_amount - amount)
            
            if self.battery_amount <= 0 and self.is_active:
                self.deactivate(obj)
                if obj.location:
                    obj.location.msg_contents(f"The {obj.name}'s battery dies.")
    
    def handle_event(self, event):
        """Handle events like 'use' commands."""
        if event.event_type == "use":
            obj = event.target
            user = event.source
            
            if self.is_active:
                success, message = self.deactivate(obj, user)
            else:
                success, message = self.activate(obj, user)
            
            user.msg(message)


class NightVisionBehavior:
    """
    Behavior that provides night vision enhancement.
    Add this to goggles or cybernetic implants.
    """
    
    key = "night_vision"
    
    def __init__(self, battery_life=100, equipment_slot="head"):
        """
        Initialize night vision behavior.
        
        Args:
            battery_life (int): Battery life (0-100)
            equipment_slot (str): Where this must be equipped to work
        """
        self.battery_life = battery_life
        self.equipment_slot = equipment_slot
        self.is_active = False
    
    def activate(self, obj, user):
        """Activate night vision."""
        if self.battery_life <= 0:
            return False, f"The {obj.name}'s battery is dead."
        
        # Check if equipped properly
        if hasattr(user, 'equipment'):
            equipped_item = user.equipment.get_slot(self.equipment_slot)
            if equipped_item != obj:
                return False, f"You must be wearing the {obj.name} to use it."
        
        user.db.night_vision_active = True
        self.is_active = True
        
        return True, f"The {obj.name} activates with a soft hum. Everything takes on a green tint."
    
    def deactivate(self, obj, user):
        """Deactivate night vision."""
        if hasattr(user, 'db'):
            user.db.night_vision_active = False
        self.is_active = False
        
        return True, f"The {obj.name} powers down. The green tint fades."
    
    def handle_event(self, event):
        """Handle events like 'use' commands."""
        if event.event_type == "use":
            obj = event.target
            user = event.source
            
            if self.is_active:
                success, message = self.deactivate(obj, user)
            else:
                success, message = self.activate(obj, user)
            
            user.msg(message)


# Example: How to create objects with lighting behaviors
def create_light_source_examples():
    """
    Examples of creating objects with light source behaviors.
    No subclassing required - just add behaviors to any object!
    """
    from evennia import create_object
    
    # Create a basic torch
    torch = create_object("typeclasses.objects.Object", key="torch")
    torch.db.desc = "A wooden torch wrapped with oil-soaked cloth."
    
    # Add light source behavior
    torch_light = LightSourceBehavior(
        light_intensity=2,
        fuel_type="fuel", 
        fuel_amount=30  # 30 minutes
    )
    torch.behaviors.add(torch_light)
    
    # Create a flashlight
    flashlight = create_object("typeclasses.objects.Object", key="flashlight") 
    flashlight.db.desc = "A sturdy LED flashlight with a bright beam."
    
    # Add light source behavior
    flashlight_light = LightSourceBehavior(
        light_intensity=3,
        fuel_type="battery",
        battery_amount=100  # 100% battery
    )
    flashlight.behaviors.add(flashlight_light)
    
    # Create night vision goggles
    goggles = create_object("typeclasses.objects.Object", key="night vision goggles")
    goggles.db.desc = "High-tech night vision goggles that amplify available light."
    goggles.db.equipment_slot = "head"
    
    # Add night vision behavior
    night_vision = NightVisionBehavior(battery_life=100, equipment_slot="head")
    goggles.behaviors.add(night_vision)
    
    # Create emergency lights (permanent, no fuel)
    emergency_light = create_object("typeclasses.objects.Object", key="emergency light")
    emergency_light.db.desc = "A red emergency light mounted on the wall."
    
    # Add light source behavior (no fuel needed)
    emergency_light_behavior = LightSourceBehavior(light_intensity=1)
    emergency_light.behaviors.add(emergency_light_behavior)
    
    # Create a lantern with both light source AND night vision enhancement
    cyber_lantern = create_object("typeclasses.objects.Object", key="cyber lantern")
    cyber_lantern.db.desc = "A high-tech lantern with built-in night vision enhancement."
    
    # Add both behaviors to the same object!
    lantern_light = LightSourceBehavior(light_intensity=2, fuel_type="battery", battery_amount=80)
    lantern_vision = NightVisionBehavior(battery_life=80, equipment_slot="hand")
    cyber_lantern.behaviors.add(lantern_light)
    cyber_lantern.behaviors.add(lantern_vision)
    
    return {
        'torch': torch,
        'flashlight': flashlight, 
        'goggles': goggles,
        'emergency_light': emergency_light,
        'cyber_lantern': cyber_lantern
    }


def demonstrate_behavior_usage():
    """
    Show how the behavior system works in practice.
    """
    examples = create_light_source_examples()
    
    print("=== BEHAVIOR-BASED LIGHTING EXAMPLES ===")
    print()
    
    # Example 1: Simple torch usage
    torch = examples['torch']
    print(f"1. Torch Light Output (off): {torch.behaviors.get('light_source').get_light_output(torch)}")
    
    # Activate torch
    light_behavior = torch.behaviors.get('light_source')
    success, message = light_behavior.activate(torch)
    print(f"   Activate torch: {message}")
    print(f"   Torch Light Output (on): {light_behavior.get_light_output(torch)}")
    
    # Example 2: Battery-powered flashlight
    flashlight = examples['flashlight']
    light_behavior = flashlight.behaviors.get('light_source')
    light_behavior.activate(flashlight)
    print(f"2. Flashlight at 100% battery: {light_behavior.get_light_output(flashlight)}")
    
    # Simulate battery drain
    light_behavior.battery_amount = 30
    print(f"   Flashlight at 30% battery: {light_behavior.get_light_output(flashlight)}")
    
    # Example 3: Multi-behavior object
    cyber_lantern = examples['cyber_lantern']
    print(f"3. Cyber lantern behaviors: {list(cyber_lantern.behaviors.all().keys())}")
    
    print()
    print("=== USAGE PATTERNS ===")
    print()
    print("# Create any object as a light source:")
    print("obj = create_object('typeclasses.objects.Object', key='my light')")
    print("light_behavior = LightSourceBehavior(light_intensity=3)")
    print("obj.behaviors.add(light_behavior)")
    print()
    print("# Use the light source:")
    print("light_behavior = obj.behaviors.get('light_source')")
    print("success, message = light_behavior.activate(obj)")
    print()
    print("# Check light output in room:")
    print("for obj in room.contents:")
    print("    light_behavior = obj.behaviors.get('light_source')")
    print("    if light_behavior:")
    print("        light += light_behavior.get_light_output(obj)")


# Integration with existing Room class
def add_lighting_to_room():
    """
    Example of how to add lighting to the existing Room class.
    This would go in typeclasses/rooms.py
    """
    
    class Room:  # This would extend your existing Room class
        
        @lazy_property
        def lighting(self):
            return LightingHandler(self)
        
        def return_appearance(self, looker, **kwargs):
            """Override to respect lighting conditions."""
            
            # Check lighting conditions
            visibility, color_code = self.lighting.get_visibility_description(looker)
            
            if visibility == "too_dark":
                return "It's too dark to see anything."
            
            # Get normal appearance
            appearance = super().return_appearance(looker, **kwargs)
            
            # Apply color coding for special vision
            if color_code:
                # Add color code to the description
                appearance = f"{color_code}{appearance}|n"
            
            # Add lighting flavor text
            if visibility == "night_vision":
                appearance += "\n|g(Night vision active - everything has a green tint)|n"
            elif visibility == "dim":
                appearance += "\n|y(The area is dimly lit)|n"
            elif visibility == "dark":
                appearance += "\n|K(You can barely make out shapes in the darkness)|n"
            
            return appearance
        
        def at_object_creation(self):
            """Set up default lighting when room is created."""
            super().at_object_creation()
            
            # Set default lighting based on room type
            if "space" in self.name.lower():
                self.lighting.set_lighting_type("space")
                self.lighting.set_base_light_level(0)
            elif "outdoor" in self.name.lower():
                self.lighting.set_lighting_type("outdoor")
                self.lighting.set_base_light_level(3)
            elif "underground" in self.name.lower() or "cave" in self.name.lower():
                self.lighting.set_lighting_type("underground")
                self.lighting.set_base_light_level(1)
            else:
                self.lighting.set_lighting_type("indoor")
                self.lighting.set_base_light_level(5)


# Example usage and testing
def example_lighting_scenarios():
    """Examples of how the lighting system would work."""
    
    # Scenario 1: Dark room with flashlight
    dark_room = Room()
    dark_room.lighting.set_base_light_level(0)
    
    character = Character()
    flashlight = Flashlight()
    
    print(f"Light level: {dark_room.lighting.get_current_light_level()}")  # 0
    print(f"Can see: {dark_room.lighting.can_see_normally(character)}")    # False
    
    flashlight.activate_light()
    print(f"Light level with flashlight: {dark_room.lighting.get_current_light_level()}")  # 3
    
    # Scenario 2: Outdoor room with day/night cycle
    outdoor_room = Room()
    outdoor_room.lighting.set_lighting_type("outdoor")
    outdoor_room.lighting.set_base_light_level(2)
    
    # During day: base(2) + outdoor_lighting(3) = 5
    # During night: base(2) + outdoor_lighting(-4) = -2 -> 0 (clamped)
    
    # Scenario 3: Emergency lighting
    room = Room()
    room.lighting.add_light_modifier("emergency_lights", -3, duration=3600)  # Dim for 1 hour
    
    # Scenario 4: Night vision in dark space
    space_room = Room()
    space_room.lighting.set_lighting_type("space")  # Very dark
    
    character.db.night_vision_active = True
    visibility, color = space_room.lighting.get_visibility_description(character)
    print(f"Space visibility with night vision: {visibility}")  # "night_vision"