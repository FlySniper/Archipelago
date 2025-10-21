import string

from BaseClasses import Location, Item, Tutorial, Region, Entrance, MultiWorld, ItemClassification
from .Locations import location_table
from .Items import item_table
from .Options import ArchipollagoOptions, archipollago_option_groups
from .Regions import create_regions
from .Rules import set_rules
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import components, Component, Type, launch as launch_component


def launch_client(*args: str):
    from .Client import launch
    launch_component(launch, name="ArchipollagoClient", args=args)


components.append(Component("Archipollago Client", game_name="Archipollago", func=launch_client,
                            component_type=Type.CLIENT))

class ArchipollagoWeb(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Archipollago for Archipelago.",
        "English",
        "archipollago_en.md",
        "archipollago/en",
        ["Fly Hyping"]
    )]

    option_groups = archipollago_option_groups


class ArchipollagoWorld(World):
    """
    A live stream polling bot. Viewers can vote on which items are sent to the multiworld!
    """

    options: ArchipollagoOptions
    options_dataclass = ArchipollagoOptions
    game = "Archipollago"
    topology_present = True
    web = ArchipollagoWeb()

    item_name_to_id = {name: data.code for name, data in item_table.items()}
    location_name_to_id = location_table

    def _get_slot_data(self):
        return {
            "poll_keys": self.options.poll_keys.value,
            "locations_per_key": self.options.locations_per_key.value,
            "time_between_polls": self.options.time_between_polls.value,
            "minor_time_skip": self.options.minor_time_skip.value,
            "major_time_skip": self.options.major_time_skip.value,
            "minor_major_ratio": self.options.minor_major_ratio.value,
            "channel_point_voting": self.options.channel_point_voting.value,
            "free_channel_points_per_vote": self.options.free_channel_points_per_vote.value,
            "number_of_choices": self.options.number_of_choices.value,
            "goal": self.options.goal.value,
        }

    def generate_early(self):
        pass

    def create_items(self):
        # Fill out our pool with our items from the item table
        pool = []
        precollected_item_names = {item.name for item in self.multiworld.precollected_items[self.player]}
        long_macguffin_items = self.options.goal.value == 1
        for name, data in item_table.items():
            if data.code is not None and name not in precollected_item_names and not data.classification == ItemClassification.filler:
                if name == "Progressive Poll Key":
                    for _ in range(0, self.options.poll_keys.value):
                        item = ArchipollagoItem(name, self.player)
                        pool.append(item)
                elif name == "Letter O" or name == "Letter L":
                    for _ in range(0, 2):
                        item = ArchipollagoItem(name, self.player)
                        pool.append(item)
                elif not long_macguffin_items and (name == "Letter R" or name == "Letter C" or name == "Letter H" or
                                                   name == "Letter I"):
                    continue
                elif long_macguffin_items and name == "Letter A":
                    for _ in range(0, 2):
                        item = ArchipollagoItem(name, self.player)
                        pool.append(item)
                else:
                    item = ArchipollagoItem(name, self.player)
                    pool.append(item)

        # Matching number of unfilled locations with filler items
        total_locations = (self.options.poll_keys.value + 1) * self.options.locations_per_key
        locations_remaining = total_locations - len(pool)
        minor_time_skip_weight = self.options.minor_major_ratio
        major_time_skip_weight = 100 - self.options.minor_major_ratio
        while locations_remaining > 0:
            if minor_time_skip_weight >= major_time_skip_weight:
                pool.append(ArchipollagoItem("Minor Time Skip", self.player))
                major_time_skip_weight += (100 - self.options.minor_major_ratio)
            else:
                pool.append(ArchipollagoItem("Major Time Skip", self.player))
                minor_time_skip_weight += self.options.minor_major_ratio
            locations_remaining -= 1

        self.multiworld.itempool += pool

        # Placing victory event at final location
        victory = ArchipollagoItem("Archipollago Victory", self.player)
        self.multiworld.get_location("Archipollago Victory Location", self.player).place_locked_item(victory)

        self.multiworld.completion_condition[self.player] = lambda state: state.has("Archipollago Victory", self.player)

    def set_rules(self):
        set_rules(self.multiworld, self.player, self.options)

    def create_item(self, name: str) -> Item:
        return ArchipollagoItem(name, self.player)

    def create_regions(self):
        create_regions(self.multiworld, self.player, self.options)

    def fill_slot_data(self) -> dict:
        slot_data = self._get_slot_data()
        return slot_data

    def get_filler_item_name(self) -> str:
        return "Minor Time Skip"


def create_region(world: MultiWorld, player: int, name: str, locations=None, exits=None):
    ret = Region(name, player, world)
    if locations:
        for location in locations:
            loc_id = location_table.get(location, 0)
            location = ArchipollagoLocation(player, location, loc_id, ret)
            ret.locations.append(location)
    if exits:
        for exit in exits:
            ret.exits.append(Entrance(player, exit, ret))

    return ret


class ArchipollagoLocation(Location):
    game: str = "Archipollago"


class ArchipollagoItem(Item):
    game = "Archipollago"

    def __init__(self, name, player: int = None):
        item_data = item_table[name]
        super(ArchipollagoItem, self).__init__(
            name,
            item_data.classification,
            item_data.code,
            player
        )
