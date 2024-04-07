import settings
import string
import typing

from BaseClasses import Item, MultiWorld, Region, Location, Entrance, Tutorial, ItemClassification
from .Items import item_table, faction_table, Wargroove2Item
from .Levels import Wargroove2Level, get_level_table, get_first_level, get_final_levels, region_names, FINAL_LEVEL_1, \
    FINAL_LEVEL_2, FINAL_LEVEL_3, FINAL_LEVEL_4, LEVEL_COUNT, FINAL_LEVEL_COUNT
from .Locations import location_table
from .Regions import create_regions
from .Rules import set_rules
from ..AutoWorld import World, WebWorld
from .Options import wargroove2_options


class Wargroove2Settings(settings.Group):
    class RootDirectory(settings.UserFolderPath):
        """
        Locate the Wargroove 2 root directory on your system.
        This is used by the Wargroove 2 client, so it knows where to send communication files to
        """
        description = "Wargroove 2 root directory"

    root_directory: RootDirectory = RootDirectory("C:/Program Files (x86)/Steam/steamapps/common/Wargroove2")


class Wargroove2Web(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Wargroove 2 for Archipelago.",
        "English",
        "wargroove2_en.md",
        "wargroove2/en",
        ["Fly Sniper"]
    )]


class Wargroove2World(World):
    """
    Command an army, in the sequel to the hit turn based strategy game Wargroove!
    """

    option_definitions = wargroove2_options
    settings: typing.ClassVar[Wargroove2Settings]
    game = "Wargroove 2"
    topology_present = True
    data_version = 1
    web = Wargroove2Web()
    level_list: [Wargroove2Level] = None
    first_level: Wargroove2Level = None
    final_levels: [Wargroove2Level] = None

    item_name_to_id = {name: data.code for name, data in item_table.items()}
    location_name_to_id = location_table

    def _get_slot_data(self):
        return {
            'seed': "".join(self.multiworld.per_slot_randoms[self.player].choice(string.ascii_letters) for i in range(16)),
            'income_boost': self.multiworld.income_boost[self.player],
            'commander_defense_boost': self.multiworld.commander_defense_boost[self.player],
            'can_choose_commander': self.multiworld.commander_choice[self.player] != 0,
            'starting_groove_multiplier': 20  # Backwards compatibility in case this ever becomes an option
        }

    def generate_early(self):
        self.first_level = get_first_level(self.player)
        self.level_list = get_level_table(self.player)
        self.final_levels = get_final_levels(self.player)
        self.multiworld.random.shuffle(self.level_list)
        self.multiworld.random.shuffle(self.final_levels)
        # Selecting a random starting faction
        if self.multiworld.commander_choice[self.player] == 2:
            factions = [faction for faction in faction_table.keys() if faction != "Starter"]
            starting_faction = Wargroove2Item(self.multiworld.random.choice(factions) + ' Commanders', self.player)
            self.multiworld.push_precollected(starting_faction)

    def create_items(self):
        # Fill out our pool with our items from the item table
        pool = []
        precollected_item_names = {item.name for item in self.multiworld.precollected_items[self.player]}
        ignore_faction_items = self.multiworld.commander_choice[self.player] == 0
        for name, data in item_table.items():
            if data.code is not None and name not in precollected_item_names and not data.classification == ItemClassification.filler:
                if name.endswith(' Commanders') and ignore_faction_items:
                    continue
                item = Wargroove2Item(name, self.player)
                pool.append(item)

        # Matching number of unfilled locations with filler items
        locations_remaining = len(location_table) - 1 - len(pool)
        while locations_remaining > 0:
            # Filling the pool equally with both types of filler items
            pool.append(Wargroove2Item("Commander Defense Boost", self.player))
            locations_remaining -= 1
            if locations_remaining > 0:
                pool.append(Wargroove2Item("Income Boost", self.player))
                locations_remaining -= 1

        self.multiworld.itempool += pool

        # Placing victory event at final location
        victory = Wargroove2Item("Wargroove 2 Victory", self.player)
        self.multiworld.get_location("Wargroove 2 Finale: Victory", self.player).place_locked_item(victory)

        self.multiworld.completion_condition[self.player] = lambda state: state.has("Wargroove 2 Victory", self.player)

    def set_rules(self):
        set_rules(self.multiworld, self.level_list, self.first_level, self.final_levels)

    def create_item(self, name: str) -> Item:
        return Wargroove2Item(name, self.player)

    def create_regions(self):
        create_regions(self.multiworld, self.player, self.level_list, self.first_level, self.final_levels)

    def fill_slot_data(self) -> dict:
        slot_data = self._get_slot_data()
        for option_name in wargroove2_options:
            option = getattr(self.multiworld, option_name)[self.player]
            slot_data[option_name] = int(option.value)
        for i in range(0, min(LEVEL_COUNT, len(self.level_list))):
            slot_data[f"Level File #{i}"] = self.level_list[i].file_name
            slot_data[region_names[i]] = self.level_list[i].name
            for location_name in self.level_list[i].location_rules.keys():
                slot_data[location_name] = region_names[i]
        for i in range(0, min(FINAL_LEVEL_COUNT, len(self.final_levels))):
            slot_data[f"Final Level File #{i}"] = self.final_levels[i].file_name
        slot_data[FINAL_LEVEL_1] = self.final_levels[0].name
        # slot_data[FINAL_LEVEL_2] = self.final_levels[1].name
        # slot_data[FINAL_LEVEL_3] = self.final_levels[2].name
        # slot_data[FINAL_LEVEL_4] = self.final_levels[3].name
        return slot_data

    def get_filler_item_name(self) -> str:
        return self.multiworld.random.choice(["Commander Defense Boost", "Income Boost"])

