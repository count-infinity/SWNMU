from dataclasses import dataclass
from commands.command import Command
from evennia.utils import evmenu, evtable
from typing import List, Dict, Any, Optional
import random

from world.utils import pick_stats, render_stats
from world import tables


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
        # Initialize sheet if needed
        if not hasattr(self.caller.db, "sheet") or self.caller.db.sheet is None:
            self.caller.db.sheet = {}
        
        # Get the current node or default to start
        current_node = self.caller.db.sheet.get('current_node', 'start')
        if not current_node:
            current_node='start'
        create_char_menu(self.caller, current_node)


def create_char_menu(caller, start):
    """Creates and starts the character generation menu."""
    evmenu.EvMenu(
        caller,
        {
            "start": node_chargen_start,
            "background": node_background,
            "background_select": node_background_select,
            "background_skills": node_background_skills,
            "select_growth": node_select_growth,
            "select_learning": node_select_learning,
            "class_select": node_class_select,
            "class_skills": node_class_skills,
            "foci_select": node_foci_select,
            "equipment": node_equipment,
            "name_character": node_name_character,
            "review": node_review,
            "confirm": node_confirm,
            "end": node_end,
        },
        startnode=start
    )


def abortOpt():
    """Standard abort option for menus."""
    return {
        "key": ("[A]bort", "abort", "a"),
        "desc": "Abort character creation.",
        "goto": "end",
    }


def nextOpt(desc, goto, **kwargs):
    """Standard next option for menus."""
    return {
        "key": ("[N]ext", "next", "n"),
        "desc": desc,
        "goto": (goto, kwargs),
    }


def backOpt(desc, goto, **kwargs):
    """Standard back option for menus."""
    return {
        "key": ("[B]ack", "back", "b"), 
        "desc": desc, 
        "goto": (goto, kwargs)
    }


def node_chargen_start(caller, raw_text, **kwargs):
    """First node: Roll or reroll stats."""
    if not caller.db.sheet.get('stats'):
        caller.db.sheet['stats'] = pick_stats()

    caller.db.sheet['current_node'] = "start"
    
    if raw_text == "r":
        caller.db.sheet['stats'] = pick_stats()
        
    # Render the character's stats
    tbl = render_stats(caller.db.sheet['stats'])
    
    text = f"""
|cSTARS WITHOUT NUMBER CHARACTER CREATION|n

Roll your character's attributes:
{tbl}

You can reroll your stats or proceed to background selection.
    """
    
    options = [
        {"key": ("[R]eroll", "reroll", "r"), "desc": "Roll again", "goto": "start"},
        nextOpt("Continue to background selection", "background"),
        abortOpt(),
        {"key": "_default", "goto": "start"},
    ]
    
    return text, options


def node_background(caller, raw_input, **kwargs):
    """Choose character background."""
    caller.db.sheet['current_node'] = "background"
    
    # Create a table to display backgrounds
    bgs=tables.background_list
    
    bg_table = evtable.EvTable("Background", "Description", table=
                               [
                                   [bg for bg in bgs],
                                   [tables.backgrounds[bg].description for bg in bgs]
                               ], border="table")
    
    text = """
|cBACKGROUND SELECTION|n

Your character's background represents their life before becoming an adventurer.
Each background provides skill bonuses and training options.

Choose a background:
    
{}
    """.format(bg_table)

    options = [
        {
            "key": bg_name,
            "desc": f"Select {bg_name} background",
            "goto": ("background_select", {"selected_background": tables.backgrounds[bg_name]})
        }
        for bg_name in tables.background_list
    ]
    
    options.extend([backOpt("Back to stats", "start"), abortOpt()])

    return text, options


def node_background_select(caller, raw_input, **kwargs):
    """Display details of selected background and confirm choice."""
    picked_bg = kwargs["selected_background"]

    max_range=max(len(picked_bg.growth),len(picked_bg.learning))
    
    # Create tables for Growth and Learning options
    skill_choice_table = evtable.EvTable(
        "Option", "Growth Bonus", "Learning Bonus",
        table=[
            [f"{idx+1}" for idx in range(max_range)],
            [f"+{g.value} {g.stat}" for g in picked_bg.growth],
            [f"+{g.value} {g.stat}" for g in picked_bg.learning]
        ]
    )

    
    txt = f"""
|cBACKGROUND: {picked_bg.name.upper()}|n

{picked_bg.description}

Free Skill: {', '.join(picked_bg.free_skill)}
Quick Skills: {', '.join(picked_bg.quick_skills)}

|cSkill Options|n
{skill_choice_table} 

Do you want to select this background?
    """
    
    options = [
        backOpt("Back to background list", "background"),
        {
            "key": ("Select", "select", "s"),
            "desc": f"Select {picked_bg.name} background",
            "goto": (_apply_background, {"selected_background": picked_bg})
        },
        abortOpt()
    ]

    return txt, options


def _apply_background(caller, raw_input, selected_background=None, **kwargs):
    """Apply the selected background to the character sheet."""
    # Store background info
    caller.db.sheet['background'] = selected_background.name
    
    # Initialize skills dict if it doesn't exist
    if 'skills' not in caller.db.sheet:
        caller.db.sheet['skills'] = {}
    
    # Apply free skill
    for skill in selected_background.free_skill:
        caller.db.sheet['skills'][skill] = caller.db.sheet['skills'].get(skill, 0) + 1
    
    return "background_skills"


def node_background_skills(caller, raw_input, **kwargs):
    """Choose how to allocate background skills."""
    caller.db.sheet['current_node'] = "background_skills"
    
    # Get background info
    bg_name = caller.db.sheet['background']
    bg = tables.backgrounds[bg_name]
    
    # Display current skills
    skill_display = ""
    if caller.db.sheet.get('skills'):
        skill_col=[]
        level_col=[]

        for skill, level in caller.db.sheet['skills'].items():
            skill_col.append(skill)
            level_col.append(level)
        
        if skill_col:
            skill_table = evtable.EvTable("Skill", "Level", table=[
                                                                skill_col,
                                                                level_col                
                                                            ]
                                          )
            skill_display = f"\nCurrent Skills:\n{skill_table}"
    
    # Create tables for Growth and Learning options
    
    growth_table = evtable.EvTable(
        "Option", "Growth Bonus", 
        table=[[f"{i+1}" for i in range(len(bg.growth))],[f"+{g.value} {g.stat}" for g in bg.growth]]
    )
    
    learning_table = evtable.EvTable(
        "Option", "Learning Bonus",
        table=[[f"{i+1}" for i in range(len(bg.learning))],[f"+{g.value} {g.stat}" for g in bg.learning]]
    )
    
    txt = f"""
|cBACKGROUND SKILLS|n

How would you like to allocate background skills for your {bg.name} background?

You can choose one of the following options:
1. Select one Growth option
2. Select one Learning option 
3. Use the Quick Skills package
4. Choose individual skills from the tables

{skill_display}

|cGROWTH OPTIONS:|n
{growth_table}

|cLEARNING OPTIONS:|n
{learning_table}

|cQUICK SKILLS:|n
{', '.join(bg.quick_skills)}
    """
    
    options = [
        {
            "key": ("Growth", "growth", "g"),
            "desc": "Select a Growth option",
            "goto": ("select_growth", {})
        },
        {
            "key": ("Learning", "learning", "l"),
            "desc": "Select a Learning option",
            "goto": ("select_learning", {})
        },
        {
            "key": ("Quick", "quick", "q"),
            "desc": f"Quick pick ({', '.join(bg.quick_skills)})",
            "goto": (_quick_select, {"quick_skills": bg.quick_skills})
        },
        backOpt("Choose another background", "background"),
        nextOpt("Continue to class selection", "class_select"),
        abortOpt()
    ]
    
    return txt, options


def node_select_growth(caller, raw_input, **kwargs):
    """Select a growth option from the background."""
    bg_name = caller.db.sheet['background']
    bg = tables.backgrounds[bg_name]
    
    growth_options = []
    for idx, growth in enumerate(bg.growth):
        growth_options.append([f"{idx+1}", f"+{growth.value} {growth.stat}"])
    
    growth_table = evtable.EvTable("Option", "Growth Bonus", table=growth_options)
    
    txt = f"""
|cSELECT GROWTH OPTION|n

Choose one growth option for your {bg_name} background:

{growth_table}

Enter the number of the growth option you want to select.
    """
    
    options = [
        {
            "key": str(idx+1),
            "desc": f"Select +{growth.value} {growth.stat}",
            "goto": (_apply_growth, {"growth_idx": idx})
        }
        for idx, growth in enumerate(bg.growth)
    ]
    
    options.extend([
        backOpt("Back to background skills", "background_skills"),
        abortOpt()
    ])
    
    return txt, options


def _apply_growth(caller, raw_input, growth_idx=None, **kwargs):
    """Apply the selected growth option."""
    bg_name = caller.db.sheet['background']
    bg = tables.backgrounds[bg_name]
    
    growth = bg.growth[growth_idx]
    
    # TODO: Implement stat increases or skill increases based on the growth option
    # This will need to be customized based on what the growth options actually do
    # For now, we'll just store that this option was selected
    
    caller.db.sheet['selected_growth'] = {
        'stat': growth.stat,
        'value': growth.value
    }
    
    # If the growth is for a specific skill, add it
    if growth.stat not in ["Any Stat", "Physical", "Mental", "Any Skill"]:
        if 'skills' not in caller.db.sheet:
            caller.db.sheet['skills'] = {}
        
        caller.db.sheet['skills'][growth.stat] = caller.db.sheet['skills'].get(growth.stat, 0) + growth.value
    
    return "background_skills"


def node_select_learning(caller, raw_input, **kwargs):
    """Select a learning option from the background."""
    bg_name = caller.db.sheet['background']
    bg = tables.backgrounds[bg_name]
    
    learning_options = []
    for idx, learning in enumerate(bg.learning):
        learning_options.append([f"{idx+1}", f"+{learning.value} {learning.stat}"])
    
    learning_table = evtable.EvTable("Option", "Learning Bonus", table=learning_options)
    
    txt = f"""
|cSELECT LEARNING OPTION|n

Choose one learning option for your {bg_name} background:

{learning_table}

Enter the number of the learning option you want to select.
    """
    
    options = [
        {
            "key": str(idx+1),
            "desc": f"Select +{learning.value} {learning.stat}",
            "goto": (_apply_learning, {"learning_idx": idx})
        }
        for idx, learning in enumerate(bg.learning)
    ]
    
    options.extend([
        backOpt("Back to background skills", "background_skills"),
        abortOpt()
    ])
    
    return txt, options


def _apply_learning(caller, raw_input, learning_idx=None, **kwargs):
    """Apply the selected learning option."""
    bg_name = caller.db.sheet['background']
    bg = tables.backgrounds[bg_name]
    
    learning = bg.learning[learning_idx]
    
    # Add the skill to the character sheet
    if 'skills' not in caller.db.sheet:
        caller.db.sheet['skills'] = {}
    
    caller.db.sheet['skills'][learning.stat] = caller.db.sheet['skills'].get(learning.stat, 0) + learning.value
    
    return "background_skills"


def _quick_select(caller, raw_input, quick_skills=None, **kwargs):
    """Apply the quick skills selection."""
    if 'skills' not in caller.db.sheet:
        caller.db.sheet['skills'] = {}
    
    for skill in quick_skills:
        # Handle the "Any-Combat" special case
        if skill == "Any-Combat":
            # TODO: Let the player choose which combat skill to add
            # For now, we'll default to "Shoot"
            skill = "Shoot"
        
        caller.db.sheet['skills'][skill] = caller.db.sheet['skills'].get(skill, 0) + 1
    
    return "class_select"


def node_class_select(caller, raw_input, **kwargs):
    """Choose character class."""
    caller.db.sheet['current_node'] = "class_select"
    
    # For now, we'll just have placeholder classes
    # In a full implementation, you'd load these from your tables module
    classes = {
        "Warrior": "Combat specialist with weapon expertise",
        "Expert": "Skilled professional with broad training",
        "Psychic": "Mentalist with psychic powers",
        "Adventurer": "Hybrid class combining aspects of other classes"
    }
    
    name, desc=zip(*classes.items())
    class_table = evtable.EvTable("Class", "Description", table=[list(name),list(desc)])
    
    txt = f"""
|cCLASS SELECTION|n

Choose your character's class:

{class_table}

Your class determines your hit points, saving throws, and special abilities.
    """
    
    options = [
        {
            "key": name.lower(),
            "desc": f"Select {name} class",
            "goto": (_apply_class, {"class_name": name})
        }
        for name in classes.keys()
    ]
    
    options.extend([
        backOpt("Back to background skills", "background_skills"),
        abortOpt()
    ])
    
    return txt, options


def _apply_class(caller, raw_input, class_name=None, **kwargs):
    """Apply the selected class."""
    caller.db.sheet['class'] = class_name
    
    # TODO: Apply class-specific bonuses, hit points, etc.
    
    return "class_skills"


def node_class_skills(caller, raw_input, **kwargs):
    """Choose class skills."""
    caller.db.sheet['current_node'] = "class_skills"
    
    class_name = caller.db.sheet['class']
    
    # Display current skills
    skill_display = ""
    if caller.db.sheet.get('skills'):
        skill, level=zip(*caller.db.sheet['skills'].items())
       
        
        if skill:
            skill_table = evtable.EvTable("Skill", "Level", table=[list(skill),list(level)])
            skill_display = f"\nCurrent Skills:\n{skill_table}"
    
    # This would need to be customized with actual class skill options
    txt = f"""
|cCLASS SKILLS: {class_name.upper()}|n

Your {class_name} class grants you additional skill points.
{skill_display}

TODO: Implement class skill selection based on SWN rules.
For now, we'll proceed to the next step.
    """
    
    options = [
        nextOpt("Continue to Focus selection", "foci_select"),
        backOpt("Back to class selection", "class_select"),
        abortOpt()
    ]
    
    return txt, options


def node_foci_select(caller, raw_input, **kwargs):
    """Choose character Foci (special abilities)."""
    caller.db.sheet['current_node'] = "foci_select"
    
    # Placeholder for foci
    foci = {
        "Alert": "Improved initiative and perception",
        "Assassin": "Deadly sneak attacks",
        "Close Combatant": "Melee combat specialist",
        "Connected": "Social connections and contacts",
        "Gunslinger": "Ranged combat specialist"
    }
    
    name, desc = map(list, zip(*foci.items()))
    foci_table = evtable.EvTable("Focus", "Description", table=[name,desc])
    
    txt = f"""
|cFOCUS SELECTION|n

Foci are special abilities that further customize your character:

{foci_table}

You can select one Focus at first level.
    """
    
    options = [
        {
            "key": name.lower(),
            "desc": f"Select {name} focus",
            "goto": (_apply_focus, {"focus_name": name})
        }
        for name in foci.keys()
    ]
    
    options.extend([
        backOpt("Back to class skills", "class_skills"),
        abortOpt()
    ])
    
    return txt, options


def _apply_focus(caller, raw_input, focus_name=None, **kwargs):
    """Apply the selected focus."""
    if 'foci' not in caller.db.sheet:
        caller.db.sheet['foci'] = []
    
    caller.db.sheet['foci'].append(focus_name)
    
    return "equipment"


def node_equipment(caller, raw_input, **kwargs):
    """Choose starting equipment."""
    caller.db.sheet['current_node'] = "equipment"
    
    txt = """
|cSTARTING EQUIPMENT|n

Based on your background and class, you receive the following starting equipment:

TODO: Implement equipment selection based on SWN rules.
For now, we'll give you a standard equipment package.

- Laser Pistol (1d6 damage)
- Melee Weapon (1d6 damage)
- Standard Clothing
- Compad (communicator/computer pad)
- 500 credits
    """
    
    # In a full implementation, you'd have equipment packages or choices
    caller.db.sheet['equipment'] = [
        "Laser Pistol (1d6 damage)",
        "Melee Weapon (1d6 damage)",
        "Standard Clothing",
        "Compad",
        "500 credits"
    ]
    
    options = [
        nextOpt("Continue to name your character", "name_character"),
        backOpt("Back to Focus selection", "foci_select"),
        abortOpt()
    ]
    
    return txt, options


def node_name_character(caller, raw_input, **kwargs):
    """Choose character name."""
    caller.db.sheet['current_node'] = "name_character"
    
    txt = """
|cCHARACTER NAME|n

What would you like to name your character?

Enter a name for your character.
    """
    
    options = [
        {
            "key": "_default",
            "goto": (_apply_name, {})
        },
        backOpt("Back to equipment selection", "equipment"),
        abortOpt()
    ]
    
    return txt, options


def _apply_name(caller, raw_input, **kwargs):
    """Apply the character name."""
    name = raw_input.strip()
    
    if not name:
        caller.msg("|rPlease enter a valid name.|n")
        return "name_character"
    
    caller.db.sheet['name'] = name
    
    return "review"


def node_review(caller, raw_input, **kwargs):
    """Review the completed character."""
    caller.db.sheet['current_node'] = "review"
    
    # Gather character info
    name = caller.db.sheet.get('name', "Unnamed")
    background = caller.db.sheet.get('background', "Unknown")
    char_class = caller.db.sheet.get('class', "Unknown")
    
    # Format skills
    skills_str = ""
    if caller.db.sheet.get('skills'):
        name, level=map(list,zip(*caller.db.sheet['skills'].items()))       
        
        if name:
            skill_table = evtable.EvTable("Skill", "Level", table=[name,level])
            skills_str = f"\n|cSKILLS:|n\n{skill_table}"
    
    # Format stats
    stats_str = render_stats(caller.db.sheet['stats'])
    
    # Format foci
    foci_str = "None"
    if caller.db.sheet.get('foci'):
        foci_str = ", ".join(caller.db.sheet['foci'])
    
    # Format equipment
    equipment_str = "None"
    if caller.db.sheet.get('equipment'):
        equipment_str = "\n- " + "\n- ".join(caller.db.sheet['equipment'])
    
    txt = f"""
|cCHARACTER REVIEW|n

Name: {name}
Background: {background}
Class: {char_class}

|cATTRIBUTES:|n
{stats_str}

{skills_str}

|cFOCI:|n
{foci_str}

|cEQUIPMENT:|n
{equipment_str}

Please review your character. You can go back to make changes or confirm to complete character creation.
    """
    
    options = [
        {
            "key": ("Confirm", "confirm", "c"),
            "desc": "Confirm and complete character creation",
            "goto": "confirm"
        },
        backOpt("Back to name selection", "name_character"),
        # Could add more back options to different sections here
        abortOpt()
    ]
    
    return txt, options


def node_confirm(caller, raw_input, **kwargs):
    """Confirm and complete character creation."""
    # Here you would actually create the character in the game
    # For now, we'll just display a success message
    
    txt = f"""
|cCHARACTER CREATION COMPLETE!|n

Congratulations! Your character {caller.db.sheet.get('name', 'Unnamed')} has been created.

To begin playing, type |wic|n to enter the game world.
    """
    
    # Reset current_node so the menu doesn't restart at this point
    caller.db.sheet['current_node'] = None
    
    # You could add code here to actually create the character object
    # or apply the sheet to the caller if they're already a character
    
    return txt, None  # No options ends the menu


def node_end(caller, raw_input, **kwargs):
    """End character creation without completing."""
    txt = "Character creation aborted. Your progress has been saved."
    return txt, None  # No options ends the menu