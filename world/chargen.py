from commands.command import Command
from evennia.utils import evmenu
from world.utils import pick_stats, render_stats

class TemporaryCharacterSheet:
    pass


class SWNCmdCharCreate(Command):
    """
    create a new character

    Begin creating a new character, or resume character creation for
    an existing in-progress character.

    You can stop character creation at any time and resume where
    you left off later.
    """

    key = "charcreate"
    locks = "cmd:pperm(Player) and is_ooc()"
    help_category = "General"

    def func(self):
        create_char_menu(self.caller,self.args)
    

# class SWNChargenCmdSet(CmdSet):
#     key = "Contrib Chargen CmdSet"

#     def at_cmdset_creation(self):
#         super().at_cmdset_creation()
#         self.add(ContribCmdIC)
#         self.add(ContribCmdCharCreate)


def create_char_menu(caller, args):
     print(f"Args: {args}")
     evmenu.EvMenu(caller, {"start": node_chargen_start, "end": node_end})


def node_chargen_start(caller, raw_text, **kwargs):
    stats = pick_stats()
    tbl=render_stats(stats)
    text=f"""
{tbl}
    """
    options = (
        {"key": ("[A]bort", "abort", "a"),
         "desc": "Answer neither, and abort.",
         "goto": "end"},
        {"key": ("[R]eroll", "reroll", "r"),
         "desc": "Roll again",
         "goto": "start"},
         {"key": "_default",
         "goto": "start"}
    )
    return text, options

def node_end(caller, raw_input, **kwargs):
    text="Thanks for your answer. Goodbye!"
    return text, None  # empty options ends the menu

