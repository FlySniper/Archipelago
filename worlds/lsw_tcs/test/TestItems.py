from unittest import TestCase

from ..items import ITEM_DATA, GenericCharacterData

class TestItems(TestCase):
    def test_item_code_uniqueness(self):
        found_codes = set()
        for item in ITEM_DATA:
            if item.code == -1:
                continue
            self.assertGreater(item.code, 0)
            self.assertNotIn(item.code, found_codes)
            found_codes.add(item.code)

    def test_item_name_uniqueness(self):
        found_names = set()
        for item in ITEM_DATA:
            self.assertNotIn(item.name, found_names)
            found_names.add(item.name)

    def test_character_number_uniqueness(self):
        found_character_numbers = set()
        for item in ITEM_DATA:
            if not isinstance(item, GenericCharacterData):
                continue
            self.assertNotIn(item.character_number, found_character_numbers)
            self.assertGreater(item.character_number, 0)
            found_character_numbers.add(item.character_number)