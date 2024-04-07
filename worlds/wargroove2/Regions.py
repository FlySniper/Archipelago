from BaseClasses import Region, Entrance
from worlds.wargroove2 import Wargroove2Level
from worlds.wargroove2.Levels import region_names, FINAL_LEVEL_1, FINAL_LEVEL_2, FINAL_LEVEL_3, FINAL_LEVEL_4


def create_regions(world, player: int,
                   level_list: [Wargroove2Level],
                   first_level: Wargroove2Level,
                   final_levels: [Wargroove2Level]):
    menu_region = Region('Menu', player, world)
    menu_region.exits.append(Entrance(player, 'Menu exits to Humble Beginnings Rebirth', menu_region))
    first_level_region = first_level.define_region("Humble Beginnings Rebirth", world, exits=[region_names[0], region_names[1],
                                                                                       region_names[2], region_names[3]])
    world.regions += [menu_region, first_level_region]

    # # Define Levels 1-4
    # for level_num in range(0, 4):
    #     next_level = level_num * 4 + 4 - level_num
    #     world.regions += [level_list[level_num].define_region(level_names[level_num], exits=[level_names[next_level],
    #                                                                        level_names[next_level + 1],
    #                                                                        level_names[next_level + 2]])]

    # Define Levels 1-4
    for level_num in range(0, 4):
        next_level = level_num * 4 + 4 - level_num
        world.regions += [level_list[level_num].define_region(region_names[level_num], world, exits=[region_names[next_level],
                                                                                              region_names[
                                                                                                 next_level + 1],
                                                                                              region_names[
                                                                                                 next_level + 2]])]

    for level_num in range(4, 16):
        world.regions += [level_list[level_num].define_region(region_names[level_num], world, exits=[FINAL_LEVEL_1])]
    world.regions += [final_levels[0].define_region(FINAL_LEVEL_1, world)]
    # # Define Levels 1A-4C
    # for level_num in range(4, 16):
    #     final_level_name = f"{FINAL_LEVEL_1} Entrance from Level {level_num}"
    #     if level_num >= 13:
    #         final_level_name = f"{FINAL_LEVEL_4} Entrance from Level {level_num}"
    #     elif level_num >= 10:
    #         final_level_name = f"{FINAL_LEVEL_3} Entrance from Level {level_num}"
    #     elif level_num >= 7:
    #         final_level_name = f"{FINAL_LEVEL_2} Entrance from Level {level_num}"
    #     world.regions += [level_list[level_num].define_region(level_names[level_num], exits=[final_level_name])]
    #
    # # Define Final Levels 1-4
    # world.regions += [final_levels[0].define_region(FINAL_LEVEL_1),
    #                   final_levels[1].define_region(FINAL_LEVEL_2),
    #                   final_levels[2].define_region(FINAL_LEVEL_3),
    #                   final_levels[3].define_region(FINAL_LEVEL_4)]
    #
    # # link up our regions with the entrances
    world.get_entrance("Menu exits to Humble Beginnings Rebirth", player).connect(
        world.get_region('Humble Beginnings Rebirth', player))
    world.get_entrance(f"Humble Beginnings Rebirth exits to {region_names[0]}", player).connect(
        world.get_region(region_names[0], player))
    world.get_entrance(f"Humble Beginnings Rebirth exits to {region_names[1]}", player).connect(
        world.get_region(region_names[1], player))
    world.get_entrance(f"Humble Beginnings Rebirth exits to {region_names[2]}", player).connect(
        world.get_region(region_names[2], player))
    world.get_entrance(f"Humble Beginnings Rebirth exits to {region_names[3]}", player).connect(
        world.get_region(region_names[3], player))
    # Define Levels 1-4
    for level_num in range(0, 4):
        next_level = level_num * 4 + 4 - level_num
        world.get_entrance(f"{region_names[level_num]} exits to {region_names[next_level]}", player).connect(
            world.get_region(region_names[next_level], player))
        world.get_entrance(f"{region_names[level_num]} exits to {region_names[next_level + 1]}", player).connect(
            world.get_region(region_names[next_level + 1], player))
        world.get_entrance(f"{region_names[level_num]} exits to {region_names[next_level + 2]}", player).connect(
            world.get_region(region_names[next_level + 2], player))

    for level_num in range(4, 16):
        final_level_name = f"{region_names[level_num]} exits to {FINAL_LEVEL_1}"
        world.get_entrance(final_level_name, player).connect(
            world.get_region(FINAL_LEVEL_1, player))
    # world.get_entrance(FINAL_LEVEL_1, player).connect(world.get_region(FINAL_LEVEL_1, player))
    # for level_num in range(0, 16):
    #     world.get_entrance(level_names[level_num], player).connect(world.get_region(level_names[level_num], player))
    #
    # for level_num in range(4, 16):
    #     if level_num >= 13:
    #         final_level_name = f"{FINAL_LEVEL_4} Entrance from Level {level_num}"
    #         world.get_entrance(final_level_name, player).connect(world.get_region(FINAL_LEVEL_4, player))
    #     elif level_num >= 10:
    #         final_level_name = f"{FINAL_LEVEL_3} Entrance from Level {level_num}"
    #         world.get_entrance(final_level_name, player).connect(world.get_region(FINAL_LEVEL_3, player))
    #     elif level_num >= 7:
    #         final_level_name = f"{FINAL_LEVEL_2} Entrance from Level {level_num}"
    #         world.get_entrance(final_level_name, player).connect(world.get_region(FINAL_LEVEL_2, player))
    #     else:
    #         final_level_name = f"{FINAL_LEVEL_1} Entrance from Level {level_num}"
    #         world.get_entrance(final_level_name, player).connect(world.get_region(FINAL_LEVEL_1, player))
