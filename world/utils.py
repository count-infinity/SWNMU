from dataclasses import dataclass
from typing import List, Dict
import re
import random
from evennia.utils import evtable
from .tables import lookup, attribute_modifier_tbl

@dataclass
class DiceResult:
    rolls: List[int]
    modifier: int
    total: int


def roll_dice(dice_string: str) -> DiceResult:
    # Pattern to match dice notation like "2d8+4", "1d20-2", "3d6", etc.
    pattern = r"(\d+)d(\d+)([+-]\d+)?"
    match = re.match(pattern, dice_string)

    if not match:
        raise ValueError(f"Invalid dice notation: {dice_string}")

    num_dice = int(match.group(1))
    dice_sides = int(match.group(2))
    modifier = int(match.group(3) or "+0")

    rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
    total = sum(rolls) + modifier

    return DiceResult(rolls=rolls, modifier=modifier, total=total)


BASE_STATS=["STRENGTH","DEXTERITY","CONSTITUTION","INTELLIGENCE","WISDOM","CHARISMA"]

def pick_stats() -> Dict[str, DiceResult]:
    result: Dict[str, DiceResult]={}
    for stat in BASE_STATS:
        result[stat]=roll_dice("3d6")

    return result


def render_stats(stats):

    statTbl=[]
    for stat in BASE_STATS:
        statTbl.append([stat,stats[stat].total,lookup(stats[stat].total,attribute_modifier_tbl)])


    table = evtable.EvTable("Stat", "Value","Mod",border="cells")
    for row in statTbl:
        table.add_row(*[str(item) for item in row])
    
    return table

# world/utils.py
from evennia.utils import evtable
import random
from typing import Dict, List, Any

def roll_ability_score() -> int:
    """Roll 3d6 for an ability score."""
    return sum(random.randint(1, 6) for _ in range(3))

def get_ability_modifier(score: int) -> int:
    """Get the ability score modifier."""
    if score <= 3:
        return -2
    elif score <= 7:
        return -1
    elif score <= 13:
        return 0
    elif score <= 17:
        return 1
    else:  # 18
        return 2


def get_physical_stats() -> List[str]:
    """Return the physical stats."""
    return ["STR", "DEX", "CON"]

def get_mental_stats() -> List[str]:
    """Return the mental stats."""
    return ["INT", "WIS", "CHA"]

def apply_stat_increase(stats: Dict[str, int], stat: str, value: int) -> Dict[str, int]:
    """
    Apply a stat increase.
    
    Args:
        stats: Current stats dictionary
        stat: Stat to increase or special category
        value: Amount to increase
        
    Returns:
        Updated stats dictionary
    """
    new_stats = stats.copy()
    
    if stat == "Any Stat":
        # Let the player choose which stat to increase
        # For now, we'll just increase the lowest stat
        lowest_stat = min(stats.items(), key=lambda x: x[1])[0]
        new_stats[lowest_stat] = min(18, new_stats[lowest_stat] + value)
    
    elif stat == "Physical":
        # Increase a physical stat
        physical_stats = get_physical_stats()
        lowest_physical = min((stats[s], s) for s in physical_stats)[1]
        new_stats[lowest_physical] = min(18, new_stats[lowest_physical] + value)
    
    elif stat == "Mental":
        # Increase a mental stat
        mental_stats = get_mental_stats()
        lowest_mental = min((stats[s], s) for s in mental_stats)[1]
        new_stats[lowest_mental] = min(18, new_stats[lowest_mental] + value)
    
    elif stat in stats:
        # Increase a specific stat
        new_stats[stat] = min(18, new_stats[stat] + value)
    
    return new_stats

def calculate_hit_points(char_class: str, con_mod: int) -> int:
    """
    Calculate starting hit points based on class and CON modifier.
    
    Args:
        char_class: Character class name
        con_mod: Constitution modifier
        
    Returns:
        Starting hit points
    """
    base_hp = {
        "Warrior": 6,
        "Expert": 4,
        "Psychic": 4,
        "Adventurer": 5  # Hybrid class
    }
    
    return max(1, base_hp.get(char_class, 4) + con_mod)

def calculate_saving_throws(char_class: str, level: int, stats: Dict[str, int]) -> Dict[str, int]:
    """
    Calculate saving throws based on class, level and stats.
    
    Args:
        char_class: Character class name
        level: Character level
        stats: Character stats
        
    Returns:
        Dictionary of saving throws
    """
    # Base saving throws by class
    class_saves = {
        "Warrior": {"Physical": 15, "Evasion": 16, "Mental": 16, "Tech": 17, "Luck": 18},
        "Expert": {"Physical": 16, "Evasion": 15, "Mental": 15, "Tech": 14, "Luck": 18},
        "Psychic": {"Physical": 16, "Evasion": 16, "Mental": 14, "Tech": 16, "Luck": 18},
        "Adventurer": {"Physical": 16, "Evasion": 16, "Mental": 15, "Tech": 16, "Luck": 18}
    }
    
    # Add stat modifiers
    base_saves = class_saves.get(char_class, class_saves["Expert"])
    
    saves = {
        "Physical": base_saves["Physical"] - get_ability_modifier(stats["STR"]),
        "Evasion": base_saves["Evasion"] - get_ability_modifier(stats["DEX"]),
        "Mental": base_saves["Mental"] - get_ability_modifier(stats["WIS"]),
        "Tech": base_saves["Tech"] - get_ability_modifier(stats["INT"]),
        "Luck": base_saves["Luck"]  #
    }