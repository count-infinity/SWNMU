"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent

from evennia.utils.utils import lazy_property
from world.skills import BehaviorHandler


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    @lazy_property 
    def behaviors(self):
        return BehaviorHandler(self)

    def handle_event(self, event):
        event.source.msg("Handle event in object")        
        self.behaviors.handle_event(event)
