"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from evennia.utils.utils import lazy_property
from .objects import ObjectParent

from world.skills import SkillHandler


class Character(ObjectParent, DefaultCharacter):
    @lazy_property 
    def skills(self):
        return SkillHandler(self)
