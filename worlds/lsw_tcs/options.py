from dataclasses import dataclass

from Options import PerGameCommonOptions, StartInventoryPool


@dataclass
class LegoStarWarsTCSOptions(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
