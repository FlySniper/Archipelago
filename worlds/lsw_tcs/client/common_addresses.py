from enum import IntEnum

CHARACTERS_SHOP_START = 0x86E4A8  # See CHARACTER_SHOP_SLOTS in items.py for the mapping
EXTRAS_SHOP_START = 0x86E4B8


class ShopType(IntEnum):
    HINTS = 0
    CHARACTERS = 1
    EXTRAS = 2
    ENTER_CODE = 3
    GOLD_BRICKS = 4
    STORY_CLIPS = 5
