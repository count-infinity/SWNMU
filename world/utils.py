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
    
    print(table)