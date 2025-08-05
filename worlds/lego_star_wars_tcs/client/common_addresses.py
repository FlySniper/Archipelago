from enum import IntEnum

CHARACTERS_SHOP_START = 0x86E4A8  # See CHARACTER_SHOP_SLOTS in items.py for the mapping
EXTRAS_SHOP_START = 0x86E4B8

# 0 when a menu is not open, 1 when a menu is open (pause screen, shop, custom character creator, select mode after
# entering a level door). Increases to 2 when opening a submenu in the pause screen.
OPENED_MENU_DEPTH_ADDRESS = 0x800944


# Byte
# 255: Cutscene
# 1: Playing, Indy trailer, loading into Cantina, Title crawl
# 2: In-level 'cutscene' where non-playable characters play an animation and the player has no control
# 6: Bounty Hunter missions select
# 7: In custom character creator
# 8: In Cantina shop
# 9: Minikits display on outside scrapyard
# There is another address at 0x925395
GAME_STATE_ADDRESS = 0x925394


class ShopType(IntEnum):
    NONE = 255  # -1 as a `signed char`
    HINTS = 0
    CHARACTERS = 1
    EXTRAS = 2
    ENTER_CODE = 3
    GOLD_BRICKS = 4
    STORY_CLIPS = 5


class CantinaRoom(IntEnum):
    UNKNOWN = -2
    NOT_IN_CANTINA = -1
    SHOP_ROOM = 0
    EPISODE_1 = 1
    EPISODE_2 = 2
    EPISODE_3 = 3
    EPISODE_4 = 4
    EPISODE_5 = 5
    EPISODE_6 = 6
    COURTYARD = 7
    BONUSES = 8
    BOUNTY_HUNTER_MISSIONS = 9
