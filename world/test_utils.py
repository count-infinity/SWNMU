import unittest
from unittest.mock import patch

from .utils import roll_dice


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
