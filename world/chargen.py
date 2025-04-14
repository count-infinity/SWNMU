from dataclasses import dataclass
from commands.command import Command
from evennia.utils import evmenu
from world.utils import pick_stats, render_stats
from world import tables

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
        create_char_menu(self.caller, self.args)


# class SWNChargenCmdSet(CmdSet):
#     key = "Contrib Chargen CmdSet"

#     def at_cmdset_creation(self):
#         super().at_cmdset_creation()
#         self.add(ContribCmdIC)
#         self.add(ContribCmdCharCreate)


def create_char_menu(caller, args):
    evmenu.EvMenu(
        caller,
        {
            "start": node_chargen_start,
            "end": node_end,
            "background": node_background,
            "background_select": node_background_select,
        },
    )


def abortOpt():
    return {
        "key": ("[A]bort", "abort", "a"),
        "desc": "Answer neither, and abort.",
        "goto": "end",
    }


def nextOpt(desc, goto, **kwargs):
    return {
            "key": ("[N]ext", "next", "n"),
            "desc": desc,
            "goto": (goto, kwargs),
        }


def backOpt(desc, goto, **kwargs):

    return {"key": ("[B]ack", "back", "b"), "desc": desc, "goto": (goto, kwargs)}


def node_chargen_start(caller, raw_text, **kwargs):
    if not (
        hasattr(caller.db, "sheet") and caller.db.sheet is not None
    ):
        caller.db.sheet = {}
        caller.db.sheet['stats'] = pick_stats()

    if raw_text == "r":
        caller.db.sheet['stats'] = pick_stats()
        
    tbl = render_stats(caller.db.sheet['stats'])
    text = f"""
{tbl}
    """
    options = [
        {"key": ("[R]eroll", "reroll", "r"), "desc": "Roll again", "goto": "start"},
        nextOpt("Background", "background", test=1),
        abortOpt(),
        {"key": "_default", "goto": "start"},
    ]
    return text, options


def node_background(caller, raw_input, **kwargs):
    text = """
    Choose a background    
    """

    options = [
        {
            "desc": f"{tables.backgrounds[background].name} - {tables.backgrounds[background].description}",
            "goto": ("background_select", {"selected_background": tables.backgrounds[background]}),
        }
        for background in tables.background_list
    ]
    options.extend([backOpt("Back to stats.", "start"), abortOpt()])

    return text, options  # empty options ends the menu


def node_background_select(caller, raw_input, **kwargs):
    picked_bg = kwargs["selected_background"]
    txt = f"{picked_bg}"
    options = [backOpt("Back to backgrounds.", "background")]

    return txt, options


def node_end(caller, raw_input, **kwargs):
    text = "Thanks for your answer. Goodbye!"
    return text, None  # empty options ends the menu
