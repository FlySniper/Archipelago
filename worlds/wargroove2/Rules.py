from typing import List

from BaseClasses import Region, Location
from .Levels import Wargroove2Level
from ..AutoWorld import LogicMixin


class Wargroove2Logic(LogicMixin):
    def _wg2_has_victory(self, player: int, finales_required: int) -> bool:
        finales_completed = 4
        if self.has("Final North", player):
            finales_completed += 1
        if self.has("Final East", player):
            finales_completed += 1
        if self.has("Final South", player):
            finales_completed += 1
        if self.has("Final West", player):
            finales_completed += 1
        return finales_completed >= finales_required and self.has("Final Center", player)


def set_rules(world, level_list: [Wargroove2Level],
              first_level: Wargroove2Level,
              final_levels: [Wargroove2Level]):
    # Level 0
    first_level.define_access_rules(world)

    # Levels 1-28 (Top 28 of the list)
    for i in range(0, 16):
        level_list[i].define_access_rules(world)

    # Final Levels (Top 4 of the list)
    for i in range(0, 1):
        final_levels[i].define_access_rules(world)

