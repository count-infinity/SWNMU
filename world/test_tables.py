import unittest
from unittest.mock import patch

from .tables import lookup, attribute_modifier_tbl


class TestTables(unittest.TestCase):
       
    tbl=attribute_modifier_tbl
    def testLookup(self):
        self.assertEqual(lookup(3,attribute_modifier_tbl), -2)
        self.assertEqual(lookup(4,attribute_modifier_tbl), -1)
        self.assertEqual(lookup(5,attribute_modifier_tbl), -1)
        self.assertEqual(lookup(6,attribute_modifier_tbl), -1)
        self.assertEqual(lookup(7,attribute_modifier_tbl), -1)
        self.assertEqual(lookup(8,attribute_modifier_tbl), 0)
        self.assertEqual(lookup(9,attribute_modifier_tbl), 0)
        self.assertEqual(lookup(10,attribute_modifier_tbl), 0)
        self.assertEqual(lookup(11,attribute_modifier_tbl), 0)
        self.assertEqual(lookup(12,attribute_modifier_tbl), 0)
        self.assertEqual(lookup(13,attribute_modifier_tbl), 0)
        self.assertEqual(lookup(14,attribute_modifier_tbl), 1)
        self.assertEqual(lookup(15,attribute_modifier_tbl), 1)
        self.assertEqual(lookup(16,attribute_modifier_tbl), 1)
        self.assertEqual(lookup(17,attribute_modifier_tbl), 1)
        self.assertEqual(lookup(18,attribute_modifier_tbl), 2)