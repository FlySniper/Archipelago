import settings
import string
import typing

from BaseClasses import Item, MultiWorld, Region, Location, Entrance, Tutorial, ItemClassification
from .Items import item_table
from .Locations import location_table, location_name_id
from .Regions import create_regions
from .Rules import set_rules
from ..AutoWorld import World, WebWorld
from .Options import space_engineers_options


class SpaceEngineersSettings(settings.Group):
    class RootDirectory(settings.UserFolderPath):
        """
        Locate the Space Engineers root directory on your system.
        This is used by the Space Engineers client, so it knows where to send communication files to
        """
        description = "Space Engineers root directory"

    root_directory: RootDirectory = RootDirectory("C:/Program Files (x86)/Steam/steamapps/common/SpaceEngineers")


class SpaceEngineersWeb(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Space Engineers for Archipelago.",
        "English",
        "space_engineers.md",
        "SpaceEngineers/en",
        ["Fly Sniper"]
    )]


class SpaceEngineersWorld(World):
    """
    Command an army, in this retro style turn based strategy game!
    """

    option_definitions = space_engineers_options
    settings: typing.ClassVar[SpaceEngineersSettings]
    game = "Space Engineers"
    topology_present = True
    data_version = 1
    web = SpaceEngineersWeb()

    item_name_to_id = {name: data.code for name, data in item_table.items()}
    location_name_to_id = location_name_id

    def _get_slot_data(self):
        return {
            'seed': "".join(self.multiworld.per_slot_randoms[self.player].choice(string.ascii_letters) for i in range(16)),
            "goal": self.multiworld.goal[self.player],
            "starting_planet_choice": self.multiworld.starting_planet_choice[self.player],
            "second_world_size": self.multiworld.second_world_size[self.player],
            "third_world_size": self.multiworld.third_world_size[self.player],
            "earth_like_distance": self.multiworld.earth_like_distance[self.player],
            "moon_distance": self.multiworld.moon_distance[self.player],
            "mars_distance": self.multiworld.mars_distance[self.player],
            "europa_distance": self.multiworld.europa_distance[self.player],
            "alien_planet_distance": self.multiworld.alien_planet_distance[self.player],
            "titan_distance": self.multiworld.titan_distance[self.player],
            "pertam_distance": self.multiworld.pertam_distance[self.player],
            "triton_distance": self.multiworld.triton_distance[self.player],
            "earth_like_size": self.multiworld.earth_like_size[self.player],
            "moon_size": self.multiworld.moon_size[self.player],
            "mars_size": self.multiworld.mars_size[self.player],
            "europa_size": self.multiworld.europa_size[self.player],
            "alien_planet_size": self.multiworld.alien_planet_size[self.player],
            "titan_size": self.multiworld.titan_size[self.player],
            "pertam_size": self.multiworld.pertam_size[self.player],
            "triton_size": self.multiworld.triton_size[self.player],
            "character_inventory_size": self.multiworld.character_inventory_size[self.player],
            "block_inventory_size": self.multiworld.block_inventory_size[self.player],
            "assembler_speed": self.multiworld.assembler_speed[self.player],
            "assembler_efficiency": self.multiworld.assembler_efficiency[self.player],
            "refinery_speed": self.multiworld.refinery_speed[self.player],
            "welding_speed": self.multiworld.welding_speed[self.player],
            "grinding_speed": self.multiworld.grinding_speed[self.player],
        }

    def generate_early(self):

        pass

    def create_items(self):
        # Fill out our pool with our items from the item table
        pool = []
        precollected_item_names = {item.name for item in self.multiworld.precollected_items[self.player]}
        for name, data in item_table.items():
            if data.code is not None and name not in precollected_item_names and data.type != "Inventory":
                item = SpaceEngineersItem(name, self.player)
                pool.append(item)

        pool.extend(SpaceEngineersItem("Progressive Space Size", self.player) for _ in range(0, 2))
        # Matching number of unfilled locations with filler items
        locations_remaining = len(location_table) - 1 - len(pool)
        while locations_remaining > 0:
            # Filling the pool equally with both types of filler items
            pool.append(SpaceEngineersItem("Oxygen Bottle", self.player))
            locations_remaining -= 1
            if locations_remaining > 0:
                pool.append(SpaceEngineersItem("Hydrogen Bottle", self.player))
                locations_remaining -= 1
            if locations_remaining > 0:
                pool.append(SpaceEngineersItem("Iron Ingot", self.player))
                locations_remaining -= 1
            if locations_remaining > 0:
                pool.append(SpaceEngineersItem("Nickel Ingot", self.player))
                locations_remaining -= 1
            if locations_remaining > 0:
                pool.append(SpaceEngineersItem("Silicon Ingot", self.player))
                locations_remaining -= 1
            if locations_remaining > 0:
                pool.append(SpaceEngineersItem("Gravel", self.player))
                locations_remaining -= 1

        self.multiworld.itempool += pool

        # Placing victory event at final location
        victory = SpaceEngineersItem("Space Engineers: Victory", self.player)
        self.multiworld.get_location("Space Engineers: Victory", self.player).place_locked_item(victory)

        self.multiworld.completion_condition[self.player] = lambda state: state.has("Space Engineers: Victory", self.player)

    def set_rules(self):
        set_rules(self.multiworld, self.player)

    def create_item(self, name: str) -> Item:
        return SpaceEngineersItem(name, self.player)

    def create_regions(self):
        create_regions(self.multiworld, self.player)

    def fill_slot_data(self) -> dict:
        slot_data = self._get_slot_data()
        for option_name in space_engineers_options:
            option = getattr(self.multiworld, option_name)[self.player]
            slot_data[option_name] = int(option.value)
        return slot_data

    def get_filler_item_name(self) -> str:
        return self.multiworld.random.choice(["Oxygen Bottle", "Hydrogen Bottle", "Iron Ingot", "Nickel Ingot",
                                              "Silicon Ingot", "Gravel"])


def create_region(world: MultiWorld, player: int, name: str, locations=None, exits=None):
    ret = Region(name, player, world)
    if locations:
        for location in locations:
            if location_table[location] is not None:
                loc_id = location_table[location].location_id
            else:
                loc_id = None
            location = SpaceEngineersLocation(player, location, loc_id, ret)
            ret.locations.append(location)
    if exits:
        for exit in exits:
            ret.exits.append(Entrance(player, exit, ret))

    return ret


class SpaceEngineersLocation(Location):
    game: str = "Space Engineers"

    def __init__(self, player: int, name: str, address=None, parent=None):
        super(SpaceEngineersLocation, self).__init__(player, name, address, parent)
        if address is None:
            self.event = True
            self.locked = True


class SpaceEngineersItem(Item):
    game = "Space Engineers"

    def __init__(self, name, player: int = None):
        item_data = item_table[name]
        super(SpaceEngineersItem, self).__init__(
            name,
            item_data.classification,
            item_data.code,
            player
        )
