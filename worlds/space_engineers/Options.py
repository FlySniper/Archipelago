import typing
from Options import Choice, Option, Range


class WorldSize2Distance(Range):
    """Increase the world size to this amount after receiving the first world size increase.
    The starting world size is automatically generated based on the starting planet's size.
    The final world size is infinite."""
    display_name = "Second World Size"
    range_start = 200
    range_end = 10000
    default = 200


class WorldSize3Distance(Range):
    """Increase the world size to this amount after receiving the second world size increase.
    The starting world size is automatically generated based on the starting planet's size.
    The final world size is infinite."""
    display_name = "Third World Size"
    range_start = 200
    range_end = 10000
    default = 3500


class EarthLikeDistance(Range):
    """How far the Earth Like planet is from the center of the world.
    Only used when Earth Like is not the starting planet"""
    display_name = "Earth Like Planet's Distance"
    range_start = 200
    range_end = 10000
    default = 200


class MoonDistance(Range):
    """How far the moon is from the center of the world."""
    display_name = "Moon's Distance"
    range_start = 200
    range_end = 10000
    default = 200


class MarsDistance(Range):
    """How far Mars is from the center of the world.
    Only used when Mars is not the starting planet"""
    display_name = "Mar's Distance"
    range_start = 200
    range_end = 10000
    default = 1750


class EuropaDistance(Range):
    """How far Europa is from the center of the world."""
    display_name = "Europa's Distance"
    range_start = 200
    range_end = 10000
    default = 1835


class TritonDistance(Range):
    """How far Triton is from the center of the world."""
    display_name = "Triton's Distance"
    range_start = 200
    range_end = 10000
    default = 2550


class PertamDistance(Range):
    """How far Pertam is from the center of the world.
    Only used when Pertam is not the starting planet"""
    display_name = "Pertam's Distance"
    range_start = 200
    range_end = 10000
    default = 4080


class AlienDistance(Range):
    """How far the Alien planet is from the center of the world.
    Only used when the Alien planet is not the starting planet"""
    display_name = "Alien planet's Distance"
    range_start = 200
    range_end = 10000
    default = 5600


class TitanDistance(Range):
    """How far Titan is from the center of the world.
    Only used when Titan is not the starting planet"""
    display_name = "Titan's Distance"
    range_start = 200
    range_end = 10000
    default = 5780


class EarthLikeSize(Range):
    """How large the earth like planet's radius is in Kilometers."""
    display_name = "Earth Like Planet's size"
    range_start = 20
    range_end = 120
    default = 120


class MoonSize(Range):
    """How large the Moon's radius is in Kilometers."""
    display_name = "Moon's Size"
    range_start = 20
    range_end = 120
    default = 20


class MarsSize(Range):
    """How large Mar's radius is in Kilometers."""
    display_name = "Mar's Size"
    range_start = 20
    range_end = 120
    default = 120


class EuropaSize(Range):
    """How large Europa's radius is in Kilometers."""
    display_name = "Europa's Size"
    range_start = 20
    range_end = 120
    default = 20


class TritonSize(Range):
    """How large Triton's radius is in Kilometers."""
    display_name = "Triton's Size"
    range_start = 20
    range_end = 120
    default = 80


class PertamSize(Range):
    """How large Pertam's radius is in Kilometers."""
    display_name = "Pertam's Size"
    range_start = 20
    range_end = 120
    default = 60


class AlienSize(Range):
    """How large the Alien's planet radius is in Kilometers."""
    display_name = "Alien Planet's Size"
    range_start = 20
    range_end = 120
    default = 120


class TitanSize(Range):
    """How large Titan's radius is in Kilometers."""
    display_name = "Titan's Size"
    range_start = 20
    range_end = 120
    default = 20


class CharacterInventorySize(Range):
    """The Character Inventory Size multiplier."""
    display_name = "Character Inventory Size"
    range_start = 1
    range_end = 10
    default = 5


class BlockInventorySize(Range):
    """The Block Inventory Size multiplier."""
    display_name = "Block Inventory Size"
    range_start = 1
    range_end = 10
    default = 3


class AssemblerSpeed(Range):
    """How fast an assembler takes to build components."""
    display_name = "Assembler Speed"
    range_start = 1
    range_end = 20
    default = 10


class AssemblerEfficiency(Range):
    """How many ingots an assembler takes to build a component.
    A higher multiplier means less ingots to make a component."""
    display_name = "Assembler Efficiency"
    range_start = 1
    range_end = 20
    default = 10


class RefinerySpeed(Range):
    """How fast a refinery takes to refine ore."""
    display_name = "Refinery Speed"
    range_start = 1
    range_end = 20
    default = 10


class WeldingSpeed(Range):
    """How fast a welder takes to weld a block."""
    display_name = "Welder Speed"
    range_start = 1
    range_end = 5
    default = 5


class GrindingSpeed(Range):
    """How fast a grinder takes to grind a block."""
    display_name = "Grinder Speed"
    range_start = 1
    range_end = 5
    default = 5


class StartingPlanetChoice(Choice):
    """The planet that the player starts on at the center of the world.
    Earth Like: Start on the Earth Like planet. (Easy)
    Triton: Start on the planet Triton. (Easy)
    Mars: Start on the planet Mars. (Normal)
    Alien: Start on the Alien planet. (Normal)
    Pertam: Start on the planet Pertam. (Hard)"""
    display_name = "Starting Planet"
    option_earth_like = 0
    option_triton = 1
    option_mars = 2
    option_alien = 3
    option_pertam = 4


class Goal(Choice):
    """The player's end goal.
    Build Jump Drive: Construct a jump drive to win. (Easy)
    Visit Every Planet: Visit every planet, moon and experience 0g to win. (Normal)
    Defeat Boss: Beat an AI mothership to win. (Hard)"""
    display_name = "Goal"
    option_build_jump_drive = 0
    option_visit_every_planet = 1
    option_defeat_boss = 2

space_engineers_options: typing.Dict[str, type(Option)] = {
    "goal": Goal,
    "starting_planet_choice": StartingPlanetChoice,
    "second_world_size": WorldSize2Distance,
    "third_world_size": WorldSize3Distance,
    "earth_like_distance": EarthLikeDistance,
    "moon_distance": MoonDistance,
    "mars_distance": MarsDistance,
    "europa_distance": EuropaDistance,
    "alien_planet_distance": AlienDistance,
    "titan_distance": TitanDistance,
    "pertam_distance": PertamDistance,
    "triton_distance": TritonDistance,
    "earth_like_size": EarthLikeSize,
    "moon_size": MoonSize,
    "mars_size": MarsSize,
    "europa_size": EuropaSize,
    "alien_planet_size": AlienSize,
    "titan_size": TitanSize,
    "pertam_size": PertamSize,
    "triton_size": TritonSize,
    "character_inventory_size": CharacterInventorySize,
    "block_inventory_size": BlockInventorySize,
    "assembler_speed": AssemblerSpeed,
    "assembler_efficiency": AssemblerEfficiency,
    "refinery_speed": RefinerySpeed,
    "welding_speed": WeldingSpeed,
    "grinding_speed": GrindingSpeed,
}
