from typing import List, Callable, Any

from BaseClasses import MultiWorld, Region, Location
from . import item_table
from ..AutoWorld import LogicMixin
from ..generic.Rules import set_rule
from .Locations import location_table, SPACE_COMPONENTS, MANUFACTURING_UPGRADE_COMPONENTS, STARTING_COMPONENTS

PLANET_SIZE_MULTIPLIER = 1.5  # The gravity wells for the planets are bigger than their radius


class SpaceEngineersLogic(LogicMixin):

    def _space_engineers_has_item(self, player: int, item: str, count=1) -> bool:
        return self.has(item, player, count=count)

    def _space_engineers_has_region(self, player: int, region: str) -> bool:
        return self.can_reach(region, 'Region', player)


def set_rules(world: MultiWorld, player: int):
    for item_name in item_table.keys():
        item_data = item_table[item_name]
        if item_data.type == "Block":
            location_data = location_table[f"Built {item_name}"]
            if any(component in location_data.component_list for component in SPACE_COMPONENTS):
                set_rule(world.get_location(f"Built {item_name}", player),
                         lambda state, item_name=item_name, player=player:
                         state._space_engineers_has_region(player, "Space: World Size 2") and
                         state._space_engineers_has_item(player, "Progressive Space Size") and
                         state._space_engineers_has_item(player, item_name))
            elif any(component in location_data.component_list for component in MANUFACTURING_UPGRADE_COMPONENTS):
                set_rule(world.get_location(f"Built {item_name}", player),
                         lambda state, item_name=item_name, player=player:
                         state._space_engineers_has_region(player,
                                                           "Starting Planet: No Flight Full Refinery and Assembler") and state._space_engineers_has_item(
                             player, item_name))
            elif any(component in location_data.component_list for component in STARTING_COMPONENTS):
                set_rule(world.get_location(f"Built {item_name}", player),
                         lambda state, item_name=item_name, player=player: state._space_engineers_has_item(player,
                                                                                                           item_name))

    set_rule(world.get_location("Stone", player),
             lambda state: True)
    set_rule(world.get_location("Iron", player),
             lambda state: True)
    set_rule(world.get_location("Nickel", player),
             lambda state: True)
    set_rule(world.get_location("Cobalt", player),
             lambda state: True)
    set_rule(world.get_location("Magnesium", player),
             lambda state: True)
    set_rule(world.get_location("Silicon", player),
             lambda state: True)
    set_rule(world.get_location("Silver", player),
             lambda state: True)
    set_rule(world.get_location("Ice", player),
             lambda state: state._space_engineers_has_region(player, "Starting Planet: Has Flight"))
    set_rule(world.get_location("Gold", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    set_rule(world.get_location("Platinum", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    set_rule(world.get_location("Uranium", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))

    set_rule(world.get_location("Assembled Flare Gun", player), lambda state: True)
    set_rule(world.get_location("Assembled Flare Gun Clip", player), lambda state: True)
    set_rule(world.get_location("Assembled Datapad", player), lambda state: True)
    set_rule(world.get_location("Assembled Grinder", player), lambda state: True)
    set_rule(world.get_location("Assembled Hand Drill", player), lambda state: True)
    set_rule(world.get_location("Assembled Welder", player), lambda state: True)
    set_rule(world.get_location("Assembled S-10 Pistol", player), lambda state: True)
    set_rule(world.get_location("Assembled S-10 Pistol Magazine", player), lambda state: True)
    set_rule(world.get_location("Assembled Fireworks", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Oxygen Bottle", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Hydrogen Bottle", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Enhanced Grinder", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Proficient Grinder", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Elite Grinder", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    set_rule(world.get_location("Assembled Enhanced Welder", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Proficient Welder", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Elite Welder", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    set_rule(world.get_location("Assembled Enhanced Hand Drill", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Proficient Hand Drill", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Elite Hand Drill", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    set_rule(world.get_location("Assembled S-20A Pistol", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled S-10E Pistol", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    set_rule(world.get_location("Assembled MR-20 Rifle", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled MR-50A Rifle", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled MR-8P Rifle", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled MR-30E Rifle", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    set_rule(world.get_location("Assembled RO-1 Rocket Launcher", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled PRO-1 Rocket Launcher", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    set_rule(world.get_location("Assembled S-20A Pistol Magazine", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled S-10E Pistol Magazine", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled MR-20 Rifle Magazine", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled MR-50A Rifle Magazine", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled MR-8P Rifle Magazine", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled MR-30E Rifle Magazine", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Gatling Ammo Box", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Autocannon Magazine", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Assault Cannon Shell", player),
             lambda state: state._space_engineers_has_region(player,
                                                             "Starting Planet: No Flight Full Refinery and Assembler"))
    set_rule(world.get_location("Assembled Artillery Shell", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    set_rule(world.get_location("Assembled Small Railgun Sabot", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    set_rule(world.get_location("Assembled Large Railgun Sabot", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    set_rule(world.get_location("Assembled Rocket", player),
             lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))

    # Earth
    planet_bound = world.earth_like_distance[player].value + world.earth_like_size[player].value * \
                   PLANET_SIZE_MULTIPLIER

    if world.starting_planet_choice[player].value == 0:
        set_rule(world.get_location("Visited Earth", player),
                 lambda state: True)
    elif world.second_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Earth", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    elif world.third_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Earth", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 3"))
    else:
        set_rule(world.get_location("Visited Earth", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 4"))

    # Triton
    planet_bound = world.triton_distance[player].value + world.triton_size[player].value * \
                   PLANET_SIZE_MULTIPLIER

    if world.starting_planet_choice[player].value == 1:
        set_rule(world.get_location("Visited Triton", player),
                 lambda state: True)
    elif world.second_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Triton", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    elif world.third_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Triton", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 3"))
    else:
        set_rule(world.get_location("Visited Triton", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 4"))

    # Mars
    planet_bound = world.mars_distance[player].value + world.mars_size[player].value * \
                   PLANET_SIZE_MULTIPLIER

    if world.starting_planet_choice[player].value == 2:
        set_rule(world.get_location("Visited Mars", player),
                 lambda state: True)
    elif world.second_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Mars", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    elif world.third_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Mars", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 3"))
    else:
        set_rule(world.get_location("Visited Mars", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 4"))

    # Alien
    planet_bound = world.alien_planet_distance[player].value + world.alien_planet_size[player].value * \
                   PLANET_SIZE_MULTIPLIER

    if world.starting_planet_choice[player].value == 3:
        set_rule(world.get_location("Visited Alien", player),
                 lambda state: True)
    elif world.second_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Alien", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    elif world.third_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Alien", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 3"))
    else:
        set_rule(world.get_location("Visited Alien", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 4"))

    # Pertam
    planet_bound = world.pertam_distance[player].value + world.pertam_size[player].value * \
                   PLANET_SIZE_MULTIPLIER

    if world.starting_planet_choice[player].value == 4:
        set_rule(world.get_location("Visited Pertam", player),
                 lambda state: True)
    elif world.second_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Pertam", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    elif world.third_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Pertam", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 3"))
    else:
        set_rule(world.get_location("Visited Pertam", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 4"))

    # Moon
    planet_bound = world.moon_distance[player].value + world.moon_size[player].value * \
                   PLANET_SIZE_MULTIPLIER

    if world.second_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Moon", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    elif world.third_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Moon", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 3"))
    else:
        set_rule(world.get_location("Visited Moon", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 4"))

    # Europa
    planet_bound = world.europa_distance[player].value + world.europa_size[player].value * \
                   PLANET_SIZE_MULTIPLIER

    if world.second_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Europa", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    elif world.third_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Europa", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 3"))
    else:
        set_rule(world.get_location("Visited Europa", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 4"))

    # Titan
    planet_bound = world.titan_distance[player].value + world.titan_size[player].value * \
                   PLANET_SIZE_MULTIPLIER

    if world.second_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Titan", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 2"))
    elif world.third_world_size[player].value > planet_bound:
        set_rule(world.get_location("Visited Titan", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 3"))
    else:
        set_rule(world.get_location("Visited Titan", player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 4"))

    # Victory Condition
    if world.goal[player].value == 0:  # Build a Jump Drive
        set_rule(world.get_location('Space Engineers: Victory', player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 2") and
                               state._space_engineers_has_item(player, "Jump Drive") and
                               state._space_engineers_has_item(player, "Progressive Space Size", 1))
    if world.goal[player].value == 1:  # Visit every Planet
        set_rule(world.get_location('Space Engineers: Victory', player),
                 lambda state: state._space_engineers_has_region(player, "Space: World Size 4") and
                               state._space_engineers_has_item(player, "Progressive Space Size", 3))
    # Start
    set_region_exit_rules(world.get_region('Starting Planet: No Flight Survival Kit', player),
                          [], items=[("Refinery", 1), ("Assembler", 1), ("Renewable Energy Sources", 1)],
                          player=player, operator='and')

    # Has flight
    set_region_exit_rules(world.get_region('Starting Planet: No Flight Full Refinery and Assembler', player),
                          [],
                          items=[("Atmospheric Thrusters", 1), ("Gyroscope", 1), ("Control Seat", 1),
                                 ("Cargo Containers", 1), ("Small Conveyor Tube", 1),
                                 ("Large Conveyor Tube", 1), ("Turreted Weapons", 1)],
                          player=player, operator='and')

    # Can reach space
    set_region_exit_rules(world.get_region('Starting Planet: Has Flight', player),
                          [], items=[("Progressive Space Size", 1), ("Hydrogen Thrusters", 1), ("O2/H2 Generator", 1),
                                     ("Medical Blocks", 1), ("Gas Tanks", 1)],
                          player=player, operator='and')

    # Space is larger
    set_region_exit_rules(world.get_region('Space: World Size 2', player),
                          [], items=[("Progressive Space Size", 2)],
                          player=player, operator='and')

    # Space is even larger
    set_region_exit_rules(world.get_region('Space: World Size 3', player), [],
                          items=[("Progressive Space Size", 3)], player=player, operator="and")
    set_region_exit_rules(world.get_region('Space: World Size 4', player),
                          [], operator="and")


def set_region_exit_rules(region: Region, locations: List[Location], items: list[tuple[str, int]] = [],
                          player: int = -1, operator: str = "or"):
    if operator == "or":
        exit_rule = lambda state: any(location.access_rule(state) for location in locations) or \
                                  any(state._space_engineers_has_item(player, item[0], item[1]) for item in items)
    else:
        exit_rule = lambda state: all(location.access_rule(state) for location in locations) and \
                                  all(state._space_engineers_has_item(player, item[0], item[1]) for item in items)
    for region_exit in region.exits:
        region_exit.access_rule = exit_rule
