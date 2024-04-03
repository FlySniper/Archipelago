from typing import List

from BaseClasses import Region, Location
from .Levels import Wargroove2Level
from ..AutoWorld import LogicMixin


class WargrooveLogic(LogicMixin):
    pass


def set_rules(level_list: [Wargroove2Level],
              first_level: Wargroove2Level,
              final_levels: [Wargroove2Level]):
    # Level 0
    first_level.define_access_rules()

    # Levels 1-28 (Top 28 of the list)
    for i in range(0, 13):
        level_list[i].define_access_rules()

    # Final Levels (Top 4 of the list)
    for i in range(0, 1):
        final_levels[i].define_access_rules()

