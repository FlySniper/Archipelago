from typing import List

from BaseClasses import MultiWorld, Region, Location
from . import ArchipollagoOptions
from ..AutoWorld import LogicMixin
from .Items import item_table
from ..generic.Rules import set_rule


class ArchipollagoLogic(LogicMixin):
    def _archipollago_has_item(self, player: int, item: str, count: int = 1) -> bool:
        return self.has(item, player, count)


def set_rules(world: MultiWorld, player: int, options: ArchipollagoOptions):
    # Final Level
    if options.goal.value == 0:
        set_rule(world.get_location("Archipollago Victory Location", player),
                 lambda state: state._archipollago_has_item(player, "Letter P") and
                               state._archipollago_has_item(player, "Letter O", 2) and
                               state._archipollago_has_item(player, "Letter L", 2) and
                               state._archipollago_has_item(player, "Letter A") and
                               state._archipollago_has_item(player, "Letter G"))
    else:
        set_rule(world.get_location("Archipollago Victory Location", player),
                 lambda state:
                               state._archipollago_has_item(player, "Letter A", 2) and
                               state._archipollago_has_item(player, "Letter R") and
                               state._archipollago_has_item(player, "Letter C") and
                               state._archipollago_has_item(player, "Letter H") and
                               state._archipollago_has_item(player, "Letter I") and
                               state._archipollago_has_item(player, "Letter P") and
                               state._archipollago_has_item(player, "Letter O", 2) and
                               state._archipollago_has_item(player, "Letter L", 2) and
                               state._archipollago_has_item(player, "Letter G"))

    poll_keys = options.poll_keys.value
    locations_per_key = options.locations_per_key.value
    for key_number in range(0, poll_keys + 1):
        for key_location_number in range(1, locations_per_key + 1):
            if key_number == 0:
                set_rule(world.get_location(
                    f"Option Number {locations_per_key * key_number + key_location_number}", player),
                         lambda state: True)
            else:
                set_rule(world.get_location(
                    f"Option Number {locations_per_key * key_number + key_location_number}", player),
                         lambda state, _key_number=key_number:
                         state._archipollago_has_item(player, "Progressive Poll Key", _key_number))
        if key_number != poll_keys:
            for region_exit in world.get_region(f"Poll Pool {key_number}", player).exits:
                region_exit.access_rule = lambda state, _key_number=key_number: (
                    state._archipollago_has_item(player, "Progressive Poll Key", _key_number))

