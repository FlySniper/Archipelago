from unittest import TestCase

from ..items import ITEM_DATA_BY_NAME
from ..levels import GAME_LEVEL_AREAS


class TestLevels(TestCase):
    def test_area_requirements(self):
        for area in GAME_LEVEL_AREAS:
            for requirement in area.item_requirements:
                self.assertIn(requirement, ITEM_DATA_BY_NAME)
