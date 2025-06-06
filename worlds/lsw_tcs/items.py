from dataclasses import dataclass, field
from typing import Protocol, Optional, TYPE_CHECKING, ClassVar, Literal

from BaseClasses import Item, ItemClassification
from .constants import (
    CharacterAbility,
    VehicleAbility,
    GAME_NAME,
    ASTROMECH,
    BLASTER,
    BOUNTY_HUNTER,
    DROID_OR_FLY,
    HIGH_JUMP,
    IMPERIAL,
    JEDI,
    PROTOCOL_DROID,
    SHORTIE,
    SITH,
)

if TYPE_CHECKING:
    from . import LegoStarWarsTCSWorld
else:
    LegoStarWarsTCSWorld = object


ItemType = Literal["Character", "Vehicle", "Extra", "Generic"]


class LegoStarWarsTCSItem(Item):
    game = GAME_NAME
    # Most Progression items collect their abilities into the state through a world.collect() override.
    collect_extras: tuple[str, ...] | None

    def __init__(self, name: str, classification: ItemClassification, code: Optional[int], player: int,
                 collect_extras: tuple[str, ...] | None = None):
        super().__init__(name, classification, code, player)
        self.collect_extras = collect_extras


@dataclass(frozen=True)
class GenericItemData:
    code: int
    name: str
    item_type: ClassVar[ItemType] = "Generic"


@dataclass(frozen=True)
class GenericCharacterData(GenericItemData):
    character_number: int
    shop_slot: int = -1


@dataclass(frozen=True)
class CharacterData(GenericCharacterData):
    abilities: CharacterAbility = CharacterAbility.NONE
    item_type: ClassVar[ItemType] = "Character"


@dataclass(frozen=True)
class VehicleData(GenericCharacterData):
    abilities: VehicleAbility = VehicleAbility.NONE
    item_type: ClassVar[ItemType] = "Vehicle"


@dataclass(frozen=True)
class ExtraData(GenericItemData):
    extra_number: int
    item_type: ClassVar[ItemType] = "Extra"
    shop_slot_byte: int = field(init=False)
    shop_slot_bit: int = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "shop_slot_byte", self.extra_number // 8)
        object.__setattr__(self, "shop_slot_bit", 1 << (self.extra_number % 8))


_generic = GenericItemData
_char = CharacterData
_vehicle = VehicleData
_extra = ExtraData


ITEM_DATA: list[GenericItemData] = [
    _generic(1, "5 Minikits"),
    _char(2, "Jar Jar Binks", 100, abilities=HIGH_JUMP),
    _char(3, "Queen Amidala", 81, abilities=BLASTER),
    _char(4, "Captain Panaka", 99, abilities=BLASTER),
    _char(5, "Padmé (Battle)", 78, abilities=BLASTER),
    _char(6, "R2-D2", 9, abilities=ASTROMECH),
    _char(7, "Anakin Skywalker (Boy)", 94, abilities=SHORTIE),
    _char(8, "Obi-Wan Kenobi (Jedi Master)", 76, abilities=JEDI),
    _char(9, "R4-P17", 67, abilities=ASTROMECH),
    _char(10, "Anakin Skywalker (Padawan)", 98, abilities=JEDI),
    _char(11, "Padmé (Geonosis)", 80, abilities=BLASTER),
    _char(12, "C-3PO", 13, abilities=PROTOCOL_DROID),
    _char(13, "Mace Windu", 63, abilities=JEDI),
    _char(14, "Padmé (Clawed)", 79, abilities=BLASTER),
    _char(15, "Yoda", 11, abilities=JEDI),
    _char(16, "Obi-Wan Kenobi (Episode 3)", 75, abilities=JEDI),
    _char(17, "Anakin Skywalker (Jedi)", 97, abilities=JEDI),
    _char(18, "Chancellor Palpatine", 74),
    _char(19, "Commander Cody", 90, abilities=BLASTER | IMPERIAL),
    _char(20, "Chewbacca", 17, abilities=BLASTER),
    _char(21, "Princess Leia", 24, abilities=BLASTER),
    _char(22, "Captain Antilles", 208, abilities=BLASTER),
    _char(23, "Rebel Friend", 191, abilities=BLASTER),
    _char(24, "Luke Skywalker (Tatooine)", 29, abilities=BLASTER),
    _char(25, "Ben Kenobi", 57, abilities=JEDI),
    _char(26, "Han Solo", 34, abilities=BLASTER),
    _char(27, "Luke Skywalker (Stormtrooper)", 30, abilities=BLASTER),
    _char(28, "Han Solo (Stormtrooper)", 35, abilities=BLASTER),
    _char(29, "Han Solo (Hoth)", 144, abilities=BLASTER),
    _char(30, "Princess Leia (Hoth)", 25, abilities=BLASTER),
    _char(31, "Luke Skywalker (Pilot)", 157, abilities=BLASTER),  # Ability missing from manual
    _char(32, "Luke Skywalker (Dagobah)", 158, abilities=JEDI),  # Ability missing from manual
    _char(33, "Luke Skywalker (Bespin)", 26, abilities=JEDI),  # Ability missing from manual
    _char(34, "Princess Leia (Boushh)", 130, abilities=BLASTER),
    _char(35, "Luke Skywalker (Jedi)", 28, abilities=JEDI),
    _char(36, "Han Solo (Skiff)", 142, abilities=BLASTER),
    _char(37, "Lando Calrissian (Palace Guard)", 202, abilities=BLASTER),
    _char(38, "Princess Leia (Slave)", 162, abilities=BLASTER),
    _char(39, "Luke Skywalker (Endor)", 27, abilities=JEDI),
    _char(40, "Princess Leia (Endor)", 163, abilities=BLASTER),
    _char(41, "Han Solo (Endor)", 207, abilities=BLASTER),
    _char(42, "Wicket", 224, abilities=SHORTIE),
    _char(43, "Darth Vader", 41, abilities=IMPERIAL | JEDI | SITH),
    _char(44, "Lando Calrissian", 36, abilities=BLASTER),
    _char(45, "Princess Leia (Bespin)", 58, abilities=BLASTER),
    _char(46, "Gonk Droid", 18),
    _char(47, "PK Droid", 101),
    _char(48, "Battle Droid", 68, abilities=BLASTER),  # ! Cannot grapple !
    _char(49, "Battle Droid (Security)", 71, abilities=BLASTER),  # ! Cannot grapple !
    _char(50, "Battle Droid (Commander)", 69, abilities=BLASTER),  # ! Cannot grapple !
    _char(51, "Droideka", 66, abilities=BLASTER),  # ! Cannot grapple !
    _char(52, "Captain Tarpals", 277, abilities=BLASTER),
    _char(53, "Boss Nass", 255),
    _char(54, "Royal Guard", 102, abilities=BLASTER),
    _char(55, "Watto", 270),
    _char(56, "Pit Droid", 269),
    _char(57, "Darth Maul", 62, abilities=JEDI | SITH),
    _char(58, "Zam Wesell", 306, abilities=BOUNTY_HUNTER | BLASTER),
    _char(59, "Dexter Jettster", 305),
    _char(60, "Clone", 87, abilities=IMPERIAL | BLASTER),
    _char(61, "Lama Su", 281),
    _char(62, "Taun We", 282),
    _char(63, "Geonosian", 96, abilities=BLASTER),  # ? Can these grapple ?
    _char(64, "Battle Droid (Geonosis)", 70, abilities=BLASTER),  # ! Cannot grapple !
    _char(65, "Super Battle Droid", 82, abilities=BLASTER),  # ? Can these grapple ?
    _char(66, "Jango Fett", 60, abilities=BOUNTY_HUNTER | BLASTER),
    _char(67, "Boba Fett (Boy)", 95, abilities=SHORTIE),
    _char(68, "Luminara", 85, abilities=JEDI),
    _char(69, "Ki-Adi Mundi", 83, abilities=JEDI),
    _char(70, "Kit Fisto", 84, abilities=JEDI),
    _char(71, "Shaak Ti", 86, abilities=JEDI),
    _char(72, "Aayla Secura", 316, abilities=JEDI),
    _char(73, "Plo Kloon", 317, abilities=JEDI),
    _char(74, "Count Dooku", 104, abilities=JEDI | SITH),
    _char(75, "Grievous' Bodyguard", 65, abilities=HIGH_JUMP),
    _char(76, "General Grievous", 61, abilities=HIGH_JUMP),
    _char(77, "Wookiee", 73, abilities=BLASTER),
    _char(78, "Clone (Episode 3)", 88, abilities=IMPERIAL | BLASTER),
    _char(79, "Clone (Episode 3, Pilot)", 89, abilities=IMPERIAL | BLASTER),
    _char(80, "Clone (Episode 3, Swamp)", 91, abilities=IMPERIAL | BLASTER),
    _char(81, "Clone (Episode 3, Walker)", 92, abilities=IMPERIAL | BLASTER),
    _char(82, "Mace Windu (Episode 3)", 64, abilities=JEDI),
    _char(83, "Disguised Clone", 93, abilities=IMPERIAL | BLASTER),
    _char(84, "Rebel Trooper", 14, abilities=BLASTER),
    _char(85, "Stormtrooper", 21, abilities=IMPERIAL | BLASTER),
    _char(86, "Imperial Shuttle Pilot", 54, abilities=IMPERIAL | BLASTER),
    _char(87, "Tusken Raider", 10, abilities=BLASTER),
    _char(88, "Jawa", 23, abilities=SHORTIE),
    _char(89, "Sandtrooper", 52, abilities=IMPERIAL | BLASTER),
    _char(90, "Greedo", 172, abilities=BOUNTY_HUNTER | BLASTER),
    _char(91, "Imperial Spy", 173, abilities=IMPERIAL),
    _char(92, "Beach Trooper", 49, abilities=IMPERIAL | BLASTER),
    _char(93, "Death Star Trooper", 50, abilities=IMPERIAL | BLASTER),
    _char(94, "TIE Fighter Pilot", 51, abilities=IMPERIAL | BLASTER),
    _char(95, "Imperial Officer", 15, abilities=IMPERIAL | BLASTER),
    _char(96, "Grand Moff Tarkin", 132, abilities=IMPERIAL | BLASTER),
    _char(97, "Han Solo (Hood)", 143, abilities=BLASTER),
    _char(98, "Rebel Trooper (Hoth)", 108, abilities=BLASTER),
    _char(99, "Rebel Pilot", 59, abilities=BLASTER),
    _char(100, "Snowtrooper", 46, abilities=IMPERIAL | BLASTER),
    _char(101, "Lobot", 193),
    _char(102, "Ugnaught", 159, abilities=SHORTIE),
    _char(103, "Bespin Guard", 194, abilities=BLASTER),
    _char(104, "Gamorrean Guard", 103),
    _char(105, "Bib Fortuna", 186),
    _char(106, "Palace Guard", 197, abilities=BLASTER),
    _char(107, "Bossk", 213, abilities=BOUNTY_HUNTER | BLASTER),
    _char(108, "Skiff Guard", 187, abilities=BLASTER),
    _char(109, "Boba Fett", 8, abilities=BOUNTY_HUNTER | BLASTER),
    _char(110, "Ewok", 200, abilities=SHORTIE | BLASTER),  # ! Cannot blast most targets !
    _char(111, "Imperial Guard", 195, abilities=IMPERIAL | BLASTER),  # ! No blaster !
    _char(112, "The Emperor", 7, abilities=JEDI | SITH | IMPERIAL),
    _char(113, "Admiral Ackbar", 212, abilities=BLASTER),
    _char(114, "IG-88", 198, abilities=BOUNTY_HUNTER | BLASTER | ASTROMECH | PROTOCOL_DROID),
    _char(115, "Dengar", 214, abilities=BOUNTY_HUNTER | BLASTER),
    _char(116, "4-LOM", 226, abilities=BOUNTY_HUNTER | BLASTER | ASTROMECH | PROTOCOL_DROID),
    _char(117, "Ben Kenobi (Ghost)", 196, abilities=JEDI),
    _char(118, "Yoda (Ghost)", 228, abilities=JEDI),
    _char(119, "R2-Q5", 315, abilities=ASTROMECH),
    _char(120, "Padmé", 77, abilities=BLASTER),
    _char(121, "Luke Skywalker (Hoth)", 205, abilities=BLASTER),  # Ability missing from manual
    _extra(122, "Super Gonk", 0x8),
    _extra(123, "Poo Money", 0x9),  # "Fertilizer" in manual
    _extra(124, "Walkie Talkie Disable", 0xA),
    _extra(125, "Red Brick Detector", 0xB),
    _extra(126, "Super Slap", 0xC),
    _extra(127, "Force Grapple Leap", 0xD),
    _extra(128, "Stud Magnet", 0xE),
    _extra(129, "Disarm Troopers", 0xF),
    _extra(130, "Character Studs", 0x10),
    _extra(131, "Perfect Deflect", 0x11),
    _extra(132, "Exploding Blaster Bolts", 0x12),
    _extra(133, "Force Pull", 0x13),
    _extra(134, "Vehicle Smart Bomb", 0x14),
    _extra(135, "Super Astromech", 0x15),
    _extra(136, "Super Jedi Slam", 0x16),
    _extra(137, "Super Thermal Detonator", 0x17),
    _extra(138, "Deflect Bolts", 0x18),
    _extra(139, "Dark Side", 0x19),
    _extra(140, "Super Blasters", 0x1A),
    _extra(141, "Fast Force", 0x1B),
    _extra(142, "Super Lightsabers", 0x1C),
    _extra(143, "Tractor Beam", 0x1D),
    _extra(144, "Invincibility", 0x1E),
    _generic(145, "Progressive Score Multiplier"),
    _extra(-1, "Score x2", 0x1F),
    _extra(146, "Self Destruct", 0x20),
    _extra(147, "Fast Build", 0x21),
    _extra(-1, "Score x4", 0x22),
    _extra(148, "Regenerate Hearts", 0x23),
    _extra(149, "Minikit Detector", 0x24),
    _extra(-1, "Score x6", 0x25),
    _extra(150, "Super Zapper", 0x26),
    _extra(151, "Bounty Hunter Rockets", 0x27),
    _extra(-1, "Score x8", 0x28),
    _extra(152, "Super Ewok Catapult", 0x29),
    _extra(153, "Infinite Torpedos", 0x2A),
    _extra(-1, "Score x10", 0x2B),
    _generic(154, "Progressive Bonus Level"),
    _generic(155, "Restart Level Trap"),
    _generic(156, "Episode 2 Unlock"),
    _generic(157, "Episode 3 Unlock"),
    _generic(158, "Episode 4 Unlock"),
    _generic(159, "Episode 5 Unlock"),
    _generic(160, "Episode 6 Unlock"),
    _char(161, "Anakin Skywalker (Ghost)", 227, abilities=JEDI),
    _char(162, "Indiana Jones", 318, abilities=BLASTER),
    _char(163, "Princess Leia (Prisoner)", 206, abilities=BLASTER),
    _vehicle(164, "Anakin's Podracer", 260),
    _vehicle(165, "Naboo Starfighter", 273),
    _vehicle(166, "Republic Gunship", 286),
    _vehicle(167, "Anakin's Starfighter", 222),
    _vehicle(168, "Obi-Wan's Starfighter", 292),
    _vehicle(169, "X-Wing", 37),
    _vehicle(170, "Y-Wing", 40),
    _vehicle(171, "Millenium Falcon", 39),
    _vehicle(172, "TIE-Interceptor", 129),
    _vehicle(173, "Snowspeeder", 33),
    _vehicle(174, "Speeder", 4),
    _generic(175, "Purple Stud"),
    # NEW. Items below here did not exist in the manual.
    # TODO: Redo all the item IDs to make more sense. Either internal order in chars.txt, or in character grid order.
    # TODO: Add in all the missing vehicles.
    _char(-1, "Qui-Gon Jinn", 105, abilities=JEDI),
    _char(-1, "Obi-Wan Kenobi", 2, abilities=JEDI),
    _char(-1, "TC-14", 72, abilities=PROTOCOL_DROID),
    _extra(-1, "Extra Toggle", 0x0),
    _extra(-1, "Fertilizer", 0x1),
    _extra(-1, "Disguise", 0x2),
    _extra(-1, "Daisy Chains", 0x3),
    _extra(-1, "Chewbacca Carrying C-3PO", 0x4),
    _extra(-1, "Tow Death Star", 0x5),
    _extra(-1, "Silhouettes", 0x6),
    _extra(-1, "Beep Beep", 0x7),
    _extra(-1, "Adaptive Difficulty", 0x2C),  # Effectively a difficulty setting, so not randomized.
]

ITEM_DATA_BY_NAME: dict[str, GenericItemData] = {data.name: data for data in ITEM_DATA}
EXTRAS_BY_NAME: dict[str, ExtraData] = {data.name: data for data in ITEM_DATA if isinstance(data, ExtraData)}
CHARACTERS_AND_VEHICLES_BY_NAME: dict[str, GenericCharacterData] = {data.name: data for data in ITEM_DATA
                                                                    if isinstance(data, GenericCharacterData)}
GENERIC_BY_NAME: dict[str, GenericItemData] = {data.name: data for data in ITEM_DATA if data.item_type == "Generic"}

ITEM_NAME_TO_ID: dict[str, int] = {name: item.code for name, item in ITEM_DATA_BY_NAME.items() if item.code != -1}