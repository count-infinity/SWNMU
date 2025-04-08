import unittest
from unittest.mock import patch

from .utils import roll_dice, pick_stats, render_stats


class TestRollDice(unittest.TestCase):
    @patch("random.randint")
    def testRollAndModifier(self, mock_randint):

        mock_randint.side_effect = [3, 5]
        roll = roll_dice("2d6+5")

        self.assertEqual(roll.total, 13)
        self.assertEqual(roll.modifier, 5)
        self.assertEqual(roll.rolls, [3, 5])

    @patch("random.randint")
    def testNoModifier(self, mock_randint):

        mock_randint.side_effect = [3, 1]
        roll = roll_dice("2d4")

        self.assertEqual(roll.total, 4)
        self.assertEqual(roll.modifier, 0)
        self.assertEqual(roll.rolls, [3, 1])

class TestPickStatus(unittest.TestCase):
    @patch("random.randint")
    def testRollsAll(self, mock_randit):
        mock_randit.side_effect=[1,1,1,2,2,2,3,3,3,4,4,4,5,5,5,6,6,6]
        
        result=pick_stats()

        self.assertEqual(result["STRENGTH"].total,3)
        self.assertEqual(result["DEXTERITY"].total,6)
        self.assertEqual(result["CONSTITUTION"].total,9)
        self.assertEqual(result["INTELLIGENCE"].total,12)
        self.assertEqual(result["WISDOM"].total,15)
        self.assertEqual(result["CHARISMA"].total,18)

class TestRenderStats(unittest.TestCase):
    def testRenderStats(self):
        result=render_stats(pick_stats())

