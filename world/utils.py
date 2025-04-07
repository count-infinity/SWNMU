from dataclasses import dataclass
from typing import List
import re
import random

@dataclass
class DiceResult:
    rolls: List[int]
    modifier: int
    total: int

def roll_dice(dice_string: str) -> DiceResult:
    # Pattern to match dice notation like "2d8+4", "1d20-2", "3d6", etc.
    pattern = r'(\d+)d(\d+)([+-]\d+)?'
    match = re.match(pattern, dice_string)
    
    if not match:
        raise ValueError(f"Invalid dice notation: {dice_string}")
    
    num_dice = int(match.group(1))
    dice_sides = int(match.group(2))
    modifier = int(match.group(3) or "+0")

    rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
    total = sum(rolls) + modifier
    

    return DiceResult(rolls=rolls, modifier=modifier, total=total)

