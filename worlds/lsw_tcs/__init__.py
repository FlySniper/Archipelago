from worlds.AutoWorld import WebWorld, World

from . import constants
from .items import ITEM_NAME_TO_ID
from .options import LegoStarWarsTCSOptions


class LegoStarWarsTCSWebWorld(WebWorld):
    theme = "partyTime"


class LegoStarWarsTCSWorld(World):
    """Lego Star Wars: The Complete Saga"""

    game = constants.GAME_NAME
    web = LegoStarWarsTCSWebWorld()
    options: LegoStarWarsTCSOptions
    options_dataclass = LegoStarWarsTCSOptions

    item_name_to_id = ITEM_NAME_TO_ID
    location_name_to_id = {}