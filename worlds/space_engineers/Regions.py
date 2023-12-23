def create_regions(world, player: int):
    from . import create_region
    from .Locations import location_table, STARTING_COMPONENTS, MANUFACTURING_UPGRADE_COMPONENTS, \
        SPACE_COMPONENTS
    from .Rules import PLANET_SIZE_MULTIPLIER

    starting_locations: [str] = []
    buildable_block_locations: [str] = []
    manufacturing_locations: [str] = []
    space_locations_size_2: [str] = []
    space_locations_size_3: [str] = []
    space_locations_size_4: [str] = []

    for location_name in location_table:
        location_data = location_table[location_name]
        if location_data is not None:
            if location_data.type == "Block":
                if any(component in location_data.component_list for component in SPACE_COMPONENTS):
                    space_locations_size_2.append(location_name)
                elif any(component in location_data.component_list for component in MANUFACTURING_UPGRADE_COMPONENTS):
                    manufacturing_locations.append(location_name)
                elif any(component in location_data.component_list for component in STARTING_COMPONENTS):
                    buildable_block_locations.append(location_name)
            else:
                if location_name == "Visited Earth":
                    planet_bound = world.earth_like_distance[player].value + world.earth_like_size[player].value * \
                                   PLANET_SIZE_MULTIPLIER
                    if world.starting_planet_choice[player].value == 0:
                        starting_locations.append(location_name)
                    elif world.second_world_size[player].value > planet_bound:
                        space_locations_size_2.append(location_name)
                    elif world.third_world_size[player].value > planet_bound:
                        space_locations_size_3.append(location_name)
                    else:
                        space_locations_size_4.append(location_data)
                elif location_name == "Visited Triton":
                    planet_bound = world.triton_distance[player].value + world.triton_size[player].value * \
                                   PLANET_SIZE_MULTIPLIER
                    if world.starting_planet_choice[player].value == 1:
                        starting_locations.append(location_name)
                    elif world.second_world_size[player].value > planet_bound:
                        space_locations_size_2.append(location_name)
                    elif world.third_world_size[player].value > planet_bound:
                        space_locations_size_3.append(location_name)
                    else:
                        space_locations_size_4.append(location_name)
                elif location_name == "Visited Mars":
                    planet_bound = world.mars_distance[player].value + world.mars_size[player].value * \
                                   PLANET_SIZE_MULTIPLIER
                    if world.starting_planet_choice[player].value == 2:
                        starting_locations.append(location_name)
                    elif world.second_world_size[player].value > planet_bound:
                        space_locations_size_2.append(location_name)
                    elif world.third_world_size[player].value > planet_bound:
                        space_locations_size_3.append(location_name)
                    else:
                        space_locations_size_4.append(location_name)
                elif location_name == "Visited Alien":
                    planet_bound = world.alien_planet_distance[player].value + world.alien_planet_size[player].value * \
                                   PLANET_SIZE_MULTIPLIER
                    if world.starting_planet_choice[player].value == 3:
                        starting_locations.append(location_name)
                    elif world.second_world_size[player].value > planet_bound:
                        space_locations_size_2.append(location_name)
                    elif world.third_world_size[player].value > planet_bound:
                        space_locations_size_3.append(location_name)
                    else:
                        space_locations_size_4.append(location_name)
                elif location_name == "Visited Pertam":
                    planet_bound = world.pertam_distance[player].value + world.pertam_size[player].value * \
                                   PLANET_SIZE_MULTIPLIER
                    if world.starting_planet_choice[player].value == 4:
                        starting_locations.append(location_name)
                    elif world.second_world_size[player].value > planet_bound:
                        space_locations_size_2.append(location_name)
                    elif world.third_world_size[player].value > planet_bound:
                        space_locations_size_3.append(location_name)
                    else:
                        space_locations_size_4.append(location_name)
                elif location_name == "Visited Moon":
                    planet_bound = world.moon_distance[player].value + world.moon_size[player].value * \
                                   PLANET_SIZE_MULTIPLIER
                    if world.second_world_size[player].value > planet_bound:
                        space_locations_size_2.append(location_name)
                    elif world.third_world_size[player].value > planet_bound:
                        space_locations_size_3.append(location_name)
                    else:
                        space_locations_size_4.append(location_name)
                elif location_name == "Visited Europa":
                    planet_bound = world.europa_distance[player].value + world.europa_size[player].value * \
                                   PLANET_SIZE_MULTIPLIER
                    if world.second_world_size[player].value > planet_bound:
                        space_locations_size_2.append(location_name)
                    elif world.third_world_size[player].value > planet_bound:
                        space_locations_size_3.append(location_name)
                    else:
                        space_locations_size_4.append(location_name)
                elif location_name == "Visited Titan":
                    planet_bound = world.titan_distance[player].value + world.titan_size[player].value * \
                                   PLANET_SIZE_MULTIPLIER
                    if world.second_world_size[player].value > planet_bound:
                        space_locations_size_2.append(location_name)
                    elif world.third_world_size[player].value > planet_bound:
                        space_locations_size_3.append(location_name)
                    else:
                        space_locations_size_4.append(location_name)

    starting_locations.extend(["Stone", "Iron", "Nickel",
                               "Cobalt", "Magnesium", "Silicon",
                               "Silver", "Assembled Flare Gun",
                               "Assembled Flare Gun Clip",
                               "Assembled Datapad",
                               "Assembled Grinder",
                               "Assembled Hand Drill",
                               "Assembled Welder",
                               "Assembled S-10 Pistol",
                               "Assembled S-10 Pistol Magazine"])

    manufacturing_locations.extend(["Assembled Fireworks",
                                    #"Assembled Oxygen Bottle",
                                    #"Assembled Hydrogen Bottle",
                                    "Assembled Enhanced Grinder",
                                    "Assembled Proficient Grinder",
                                    "Assembled Enhanced Welder",
                                    "Assembled Proficient Welder",
                                    "Assembled Enhanced Hand Drill",
                                    "Assembled Proficient Hand Drill",
                                    "Assembled S-20A Pistol",
                                    "Assembled MR-20 Rifle",
                                    "Assembled MR-50A Rifle",
                                    "Assembled MR-8P Rifle",
                                    "Assembled RO-1 Rocket Launcher",
                                    "Assembled S-20A Pistol Magazine",
                                    "Assembled S-10E Pistol Magazine",
                                    "Assembled MR-20 Rifle Magazine",
                                    "Assembled MR-50A Rifle Magazine",
                                    "Assembled MR-8P Rifle Magazine",
                                    "Assembled MR-30E Rifle Magazine",
                                    "Assembled Gatling Ammo Box",
                                    "Assembled Autocannon Magazine",
                                    "Assembled Assault Cannon Shell"])

    space_locations_size_2.extend(["Platinum", "Uranium", "Gold",
                                   "Assembled Artillery Shell",
                                   "Assembled Small Railgun Sabot",
                                   "Assembled Large Railgun Sabot",
                                   "Assembled PRO-1 Rocket Launcher",
                                   "Assembled MR-30E Rifle",
                                   "Assembled S-10E Pistol",
                                   "Assembled Elite Hand Drill",
                                   "Assembled Elite Welder",
                                   "Assembled Elite Grinder",
                                   "Assembled Rocket"])
    flight_locations: [str] = ["Ice"]
    world_regions = [
        create_region(world, player, 'Menu', None, ['Starting Planet: No Materials']),
        create_region(world, player, 'Starting Planet: No Materials', starting_locations,
                      ['Starting Planet: No Flight Survival Kit']),
        create_region(world, player, 'Starting Planet: No Flight Survival Kit', buildable_block_locations,
                      ['Starting Planet: No Flight Full Refinery and Assembler']),

        create_region(world, player, 'Starting Planet: No Flight Full Refinery and Assembler',
                      manufacturing_locations,
                      ['Starting Planet: Has Flight']),

        create_region(world, player, 'Starting Planet: Has Flight',
                      flight_locations,
                      ['Space: World Size 2', 'Space Engineers Finale']),

    ]
    # Goal is to Build a Jump Drive
    if world.goal[player].value == 0:
        world_regions.append(create_region(world, player, 'Space: World Size 2',
                                           space_locations_size_2,
                                           ['Space: World Size 3']))
    else:
        world_regions.append(create_region(world, player, 'Space: World Size 2',
                                           space_locations_size_2,
                                           ['Space: World Size 3']))

    world_regions.append(create_region(world, player, 'Space: World Size 3',
                                       space_locations_size_3,
                                       ['Space: World Size 4']))

    # Goal is to visit every planet, or defeat the mothership
    if world.goal[player].value == 1 or world.goal[player].value == 2:
        world_regions.append(create_region(world, player, 'Space: World Size 4',
                                           space_locations_size_4,
                                           ['Space Engineers Finale']))
    else:
        world_regions.append(create_region(world, player, 'Space: World Size 4',
                                           space_locations_size_4,
                                           []))

    world_regions.append(create_region(world, player, 'Space Engineers Finale', [
        'Space Engineers: Victory'
    ]))

    world.regions += world_regions

    # link up our regions with the entrances
    world.get_entrance('Starting Planet: No Materials', player).connect(
        world.get_region('Starting Planet: No Materials', player))

    world.get_entrance('Starting Planet: No Flight Survival Kit', player).connect(
        world.get_region('Starting Planet: No Flight Survival Kit', player))
    # world.get_entrance('Starting Planet: No Flight Survival Kit', player).connect(
    #     world.get_region('Starting Planet: No Materials', player))

    world.get_entrance('Starting Planet: No Flight Full Refinery and Assembler', player).connect(
        world.get_region('Starting Planet: No Flight Full Refinery and Assembler', player))
    # world.get_entrance('Starting Planet: No Flight Full Refinery and Assembler', player).connect(
    #    world.get_region('Starting Planet: No Flight Survival Kit', player))

    world.get_entrance('Starting Planet: Has Flight', player).connect(
        world.get_region('Starting Planet: Has Flight', player))
    # world.get_entrance('Starting Planet: Has Flight', player).connect(
    #    world.get_region('Starting Planet: No Flight Full Refinery and Assembler', player))

    world.get_entrance('Space: World Size 2', player).connect(world.get_region('Space: World Size 2', player))
    # world.get_entrance('Space: World Size 2', player).connect(world.get_region('Starting Planet: Has Flight', player))

    world.get_entrance('Space: World Size 3', player).connect(world.get_region('Space: World Size 3', player))
    # world.get_entrance('Space: World Size 3', player).connect(world.get_region('Space: World Size 2', player))

    world.get_entrance('Space: World Size 4', player).connect(world.get_region('Space: World Size 4', player))
    # world.get_entrance('Space: World Size 4', player).connect(world.get_region('Space: World Size 3', player))

    world.get_entrance('Space Engineers Finale', player).connect(world.get_region('Space Engineers Finale', player))
