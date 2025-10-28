from . import VotipelagoOptions


def create_regions(world, player: int, options: VotipelagoOptions):
    from . import create_region

    poll_keys = options.poll_keys.value
    locations_per_key = options.locations_per_key.value
    world.regions += [create_region(world, player, "Menu", None, ["Poll Pool Exit 0"])]
    for key_number in range(0, poll_keys + 1):
        locations = []
        for key_location_number in range(1, locations_per_key + 1):
            locations += [f"Option Number {locations_per_key * key_number + key_location_number}"]
        if key_number == poll_keys:
            locations += ["Votipelago Victory Location"]
            world.regions += [create_region(world, player, f"Poll Pool {key_number}", locations,[])]
        else:
            world.regions += [create_region(world, player, f"Poll Pool {key_number}", locations,
                          [f"Poll Pool Exit {key_number + 1}",])]

    # link up our regions with the entrances
    for key_number in range(0, poll_keys + 1):
        world.get_entrance(f"Poll Pool Exit {key_number}", player).connect(
            world.get_region(f"Poll Pool {key_number}", player))
