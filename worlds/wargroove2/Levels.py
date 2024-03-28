from typing import List

from BaseClasses import Region, Entrance, MultiWorld, Location
from .Locations import location_table, Wargroove2Location
from ..generic.Rules import set_rule

level_names: [str] = ["Level 1", "Level 2", "Level 3", "Level 4",
                      "Level 1A", "Level 1B", "Level 1C",
                      "Level 2A", "Level 2B", "Level 2C",
                      "Level 3A", "Level 3B", "Level 3C",
                      "Level 4A", "Level 4B", "Level 4C"]
FINAL_LEVEL_1 = "Finale 1"
FINAL_LEVEL_2 = "Finale 2"
FINAL_LEVEL_3 = "Finale 3"
FINAL_LEVEL_4 = "Finale 4"


def set_region_exit_rules(region: Region, world: MultiWorld, player: int, locations: List[str], operator: str = "or"):
    if operator == "or":
        exit_rule = lambda state: any(world.get_location(location, player).access_rule(state) for location in locations)
    else:
        exit_rule = lambda state: all(world.get_location(location, player).access_rule(state) for location in locations)
    for region_exit in region.exits:
        region_exit.access_rule = exit_rule


class Wargroove2Level:
    world: MultiWorld
    player: int
    name: str
    file_name: str
    location_rules: dict
    region: Region
    victory_locations: List[str]

    def __init__(self, name: str, file_name: str, location_rules: dict, victory_locations: List[str] = []):
        if victory_locations is None:
            victory_locations = []
        self.name = name
        self.file_name = file_name
        self.location_rules = location_rules
        if victory_locations:
            self.victory_locations = victory_locations
        else:
            self.victory_locations = [name + ': Victory']

    def define_access_rules(self):
        for location_name, rule in self.location_rules.items():
            set_rule(self.world.get_location(location_name, self.player), lambda state:
            state.can_reach(self.region, 'Region', self.player) and rule(state))
        set_region_exit_rules(self.region, self.world, self.player, self.victory_locations)

    def define_region(self, name: str, exits=None) -> Region:
        self.region = Region(name, self.player, self.world)
        if self.location_rules.keys():
            for location in self.location_rules.keys():
                loc_id = location_table.get(location, 0)
                location = Wargroove2Location(self.player, location, loc_id, self.region)
                self.region.locations.append(location)
        if exits:
            for exit in exits:
                self.region.exits.append(Entrance(self.player, f"{name} exits to {exit}", self.region))

        return self.region


def get_level_table(player: int, world: MultiWorld) -> List[Wargroove2Level]:
    levels = [
        Wargroove2Level(
            name="Spire Fire",
            file_name="Spire_Fire.json",
            location_rules={
                "Spire Fire: Victory": lambda state: state.has_any({"Mage", "Witch"}, player),
                "Spire Fire: Kill Enemy Sky Rider": lambda state: state.has("Witch", player),
                "Spire Fire: Win without losing your Dragon": lambda state: state.has_any({"Mage", "Witch"}, player)
            }
        ),
        Wargroove2Level(
            name="Nuru's Vengeance",
            file_name="Nuru_Vengeance.json",
            location_rules={
                "Nuru's Vengeance: Victory": lambda state: state.has("Knight", player),
                "Nuru's Vengeance: Defeat all Dogs": lambda state: state.has("Knight", player),
                "Nuru's Vengeance: Destroy the Gate with a Spearman": lambda state: state.has_all(
                    {"Knight", "Spearman"}, player)
            }
        ),
        Wargroove2Level(
            name="Cherrystone Landing",
            file_name="Cherrystone_Landing.json",
            location_rules={
                "Cherrystone Landing: Victory": lambda state: state.has_all({"Warship", "Barge", "Landing Event"},
                                                                            player),
                "Cherrystone Landing: Defeat a Trebuchet with a Golem": lambda state: state.has_all(
                    {"Warship", "Barge", "Landing Event", "Golem"}, player),
                "Cherrystone Landing: Defeat a Fortified Village with a Golem": lambda state: state.has_all(
                    {"Barge", "Landing Event", "Golem"}, player)
            }
        ),
        Wargroove2Level(
            name="Slippery Bridge",
            file_name="Slippery_Bridge.json",
            location_rules={
                "Slippery Bridge: Victory": lambda state: state.has("Frog", player),
                "Slippery Bridge: Control all Sea Villages": lambda state: state.has("Merfolk", player),
            }
        ),
        Wargroove2Level(
            name="Den-Two-Away",
            file_name="Den-Two-Away.json",
            location_rules={
                "Den-Two-Away: Victory": lambda state: state.has("Harpy", player),
                "Den-Two-Away: Commander Captures the Lumbermill": lambda state: state.has_all({"Harpy", "Balloon"},
                                                                                               player),
            }
        ),
        Wargroove2Level(
            name="Sky High",
            file_name="Sky_High.json",
            location_rules={
                "Sky High: Victory": lambda state: state.has_all({"Balloon", "Airstrike Event"}, player),
                "Sky High: Dragon Defeats Stronghold": lambda state: state.has_all({"Balloon", "Airstrike Event", "Dragon"}, player),
            }
        ),
    ]
    for level in levels:
        level.world = world
        level.player = player
    return levels


def get_final_levels(player: int, world: MultiWorld) -> List[Wargroove2Level]:
    levels = [
        Wargroove2Level(
            name="Wargroove 2 Finale",
            file_name="Nuru_Vengeance.json",
            location_rules={
                "Wargroove 2 Finale: Victory": lambda state: True,  # True for now, so it generates
            }
        ),
    ]
    for level in levels:
        level.world = world
        level.player = player
    return levels


def get_first_level(player: int, world: MultiWorld) -> Wargroove2Level:
    first_level = Wargroove2Level(
        name="Humble Beginnings Rebirth",
        file_name="",
        location_rules={
            "Humble Beginnings Rebirth: Victory": lambda state: True,
            "Humble Beginnings Rebirth: Talk to Nadia": lambda state: True
        }
    )
    first_level.world = world
    first_level.player = player
    return first_level
