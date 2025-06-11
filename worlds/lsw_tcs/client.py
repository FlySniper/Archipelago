import asyncio
import traceback
import colorama
from enum import IntEnum

import ModuleUpdate
import Utils
from NetUtils import NetworkItem

ModuleUpdate.update()


import logging
import struct
import typing
from pymem import pymem
from pymem.exception import ProcessNotFound, ProcessError, PymemError, WinAPIError
from typing import ClassVar, AbstractSet, cast, Iterable

from CommonClient import CommonContext, server_loop, gui_enabled

from .constants import GAME_NAME
from .items import (
    ITEM_DATA,
    ITEM_DATA_BY_NAME,
    ITEM_DATA_BY_ID,
    ExtraData,
    GenericCharacterData,
    CHARACTERS_AND_VEHICLES_BY_NAME,
    EXTRAS_BY_NAME,
    GENERIC_BY_NAME,
    GenericItemData,
    CHARACTER_SHOP_SLOTS,
)
from .locations import LEVEL_COMMON_LOCATIONS, LOCATION_NAME_TO_ID
from .levels import GAME_LEVEL_AREAS, EpisodeGameLevelArea, SHORT_NAME_TO_LEVEL_AREA, BONUS_GAME_LEVEL_AREAS


logger = logging.getLogger("Client")


# FIXME/TODO: Where can we write the last received item index?
# FIXME: If an extra/character has already been unlocked, they cannot be bought from the shop.
#   A. The client detects when the shop is open and temporarily locks all unlocked extras/characters that are
#      purchasable and have yet to be purchased
# FIXME: Buying an extra from the shop will re-unlock it when entering the cantina. The client will probably have to
#  constantly disable any extras that are not unlocked according to AP.

# todo: How to detect GOG executable and offset all addresses?

# Aliases for clarity in typing.
MemoryAddress = int
MemoryOffset = int
BitMask = int
LocationId = int


PROCESS_NAME = "LEGOStarWarsSaga"

# This memory pattern was found in Dread Pony Roberts' cheat table.
VERSION_CHECK_PATTERN = b"\x0F\xBE\xAE\x7F\x10\x00\x00"
VERSION_CHECK_ADDRESS_STEAM = 0x4B894C

MEMORY_OFFSET_STEAM = 0
MEMORY_OFFSET_GOG = 0x20

# Note, this is not the in-level stud count. We don't add to that, because it is not saved.
STUD_COUNT = 0x86E4DC
MAX_STUD_COUNT = 4_000_000_000

CURRENT_GAME_MODE_ADDRESS = 0x87951C
CURRENT_GAME_MODE_STORY = 0
CURRENT_GAME_MODE_FREE_PLAY = 1
# Per-level Challenge mode as well as per-episode character bonus and Superstory.
# TODO: What do vehicle bonuses and separate bonus levels count as?
CURRENT_GAME_MODE_CHALLENGE_BONUS = 2

# The most stable byte I could find to determine the difference between the 'status' screen when using "Save and Exit
# Cantina" and when completing a level, in Free Play. What this byte controls is unknown.
# Seems to always be 0x8 when using "Save and Quit", and 0x0 when completing a level.
STATUS_LEVEL_TYPE_ADDRESS = 0x87A6D9
# STATUS_LEVEL_TYPE_SAVE_AND_EXIT = 0x8
STATUS_LEVEL_TYPE_LEVEL_COMPLETION = 0x0

CURRENT_LEVEL_ID = 0x951BA0  # 2 bytes (or more)
# While in the Cantina and in the shop room, all extras that have been received, but not purchased, must be locked,
# otherwise those extras cannot be bought from the shop.
# When entering the Cantina, all purchased extras that have not been received will need to be locked because entering
# the cantina will unlock all extras that have been purchased.
# How was this 69 before????
LEVEL_ID_CANTINA = 325

# Unsure what this is, but it changes when moving between rooms in the cantina and appears to persist while in a level,
# so this can be used to both see what room the player is in when they are in the cantina, and to see what Episode they
# are in at a glance (the current Episode can be determined exactly from the current level ID)
# 0: Main room with the shop (what we care about)
# 1: Episode 1 room
# 2: Episode 2 room
# 3: Episode 3 room
# 4: Episode 4 room
# 5: Episode 5 room
# 6: Episode 6 room
# 7: Outside courtyard
# 8: Bonuses room
# ?: Bounty Hunter missions room
CANTINA_ROOM_ID = 0x87B460
CANTINA_ROOM_WITH_SHOP = 0


class ShopType(IntEnum):
    HINTS = 0
    CHARACTERS = 1
    EXTRAS = 2
    ENTER_CODE = 3
    GOLD_BRICKS = 4
    STORY_CLIPS = 5


# Appears to be 0 while in the shop, and 1 otherwise. Remains 0 when playing a cutscene from within the shop.
SHOP_CHECK = 0x87B748  # byte
SHOP_CHECK_IS_IN_SHOP = b"\x00"
# Appears to be 1 while in the shop, and 0 otherwise. But becomes 0 when playing a cutscene from within the shop.
# SHOP_CHECK2 = 0x880474  # byte
ACTIVE_SHOP_TYPE_ADDRESS = 0x8801AC
EXTRAS_SHOP_START = 0x86E4B8
EXTRAS_SHOP_LENGTH_BYTES = 6 # 0xB8 to 0xBD
# Active slot in the shop, maybe we can use this in combination with CANTINA_ROOM_ID and LEVEL_ID_CANTINA to only
# temporarily lock unpurchased extras that are currently active?
# Note: The previous 2 and next 2 shop indices are before/after this in memory (5 on screen at once).
EXTRAS_SHOP_ACTIVE_INDEX = 0x87BF0C
EXTRAS_UNLOCKED_START = 0x86E4C8


CHARACTERS_SHOP_START = 0x86E4A8  # See CHARACTER_SHOP_SLOTS in items.py for the mapping
CHARACTERS_UNLOCKED_START = 0x86E5C0
CHARACTERS_SHOP_ACTIVE_INDEX = 0x87BDF8


CUSTOM_CHARACTER_1_NAME = 0x86E500  # char[16], null-terminated, so 15 usable characters
CUSTOM_CHARACTER_2_NAME = 0x86E538  # char[16], null-terminated, so 15 usable characters


LEVEL_STORY_MODE_COMPLETE_OFFSET = 0x1 # byte
LEVEL_TRUE_JEDI_COMPLETE_OFFSET = 0x2 # byte
LEVEL_UNKNOWN_OFFSET = 0x3 # byte  # Free play complete?
LEVEL_MINIKIT_GOLD_BRICK_OFFSET = 0x4 # byte
LEVEL_MINIKIT_COUNT_OFFSET = 0x5 # byte
LEVEL_RED_BRICK_COLLECTED_OFFSET = 0x6 # byte
LEVEL_BLUE_CANISTERS_COLLECTED_OFFSET = 0x7 # byte
LEVEL_BEST_TIME_OFFSET = 0x8  # float

BONUSES_BASE_ADDRESS = 0x86E4E4

LEVEL_ADDRESSES: dict[str, int] = {
    "1-1": 0x86E0F4,
    "1-2": 0x86E100,
    "1-3": 0x86E10C,
    "1-4": 0x86E118,
    # "Pod Race (Original)" bonus level has data in the middle here.
    "1-5": 0x86E130,
    "1-6": 0x86E13C,

    "2-1": 0x86E16C,
    "2-2": 0x86E178,
    "2-3": 0x86E184,
    "2-4": 0x86E190,
    "2-5": 0x86E19C,
    # "Gunship Cavalry" bonus level has data in the middle here.
    "2-6": 0x86E1B4,
}


# Unverified, but seems to be the case.
MINIKIT_NAME_LENGTH_BYTES = 8
# todo: Need to include location IDs somewhere
# todo: Can objects other than minikits get included in these lists? In which case, we might need to read more memory...
#   Polly on the Lego TTGames modding discord seemed to have an idea of how minikits were laid out in memory.
# todo: This dictionary will be long and will want to go in a different module.
_MINIKIT_ADDRESSES_AND_NAMES: dict[int, dict[bytes, int]] = {
    # 1-1A
    0x0: {
        b"m_pup1": 1,
        b"m_pup2": 2,
        b"m_pup3": 3,
        b"m_pup4": 4,
        b"m_pup5": 5,
        b"pup_2": 6,
    },
    # 1-1B
    0x0: {
        b"m_pup1": 7,
        b"pup2": 8,
    },
    # 1-1C
    0x0: {
        b"m_pup1": 9,
        b"m_pup2": 10,
    },

    0x0: {
        b"m_pup2": 11,
        b"m_pOOP1": 12,
        b"m_pOOP2": 13,
        b"m_pOOP3": 14,
        b"m_pup1": 15,
    },
    0x0: {
        b"m_pup1": 0,  # todo
    }
}

def _s8(b: bytes) -> bytes:
    """Null terminate and pad an 8 byte string"""
    if len(b) >= 8:
        raise AssertionError(f"String {b} is too long")
    return b + b"\x00" * (8 - len(b))
MINIKIT_ADDRESSES_AND_NAMES: dict[int, dict[bytes, int]] = {k: {_s8(k2): v2 for k2, v2 in v.items()}
                                                            for k, v in _MINIKIT_ADDRESSES_AND_NAMES.items()}


def _extras_to_shop_address() -> dict[MemoryOffset, dict[BitMask, LocationId]]:
    """Purchase <extra> shop ID -> AP Location ID"""
    per_byte: dict[MemoryOffset, dict[BitMask, LocationId]] = {}
    for extra_data in EXTRAS_BY_NAME.values():
        if extra_data.name == "Adaptive Difficulty":
            # Not present in the shop because it is always unlocked
            continue
        if extra_data.code == -1:
            # Not implemented yet
            continue
        byte_offset = extra_data.extra_number // 8
        bit_mask = 1 << (extra_data.extra_number % 8)
        if extra_data.level_shortname is not None:
            location_name = f"Purchase {extra_data.name} ({extra_data.level_shortname})"
        else:
            location_name = f"Purchase {extra_data.name}"
        assert location_name in LOCATION_NAME_TO_ID, f"ERROR: {location_name} is not a location name"
        location_id = LOCATION_NAME_TO_ID[location_name]
        per_byte.setdefault(byte_offset, {})[bit_mask] = location_id
    # todo: list[tuple[int, dict[int, int]]] for better iteration performance?
    # return list(per_byte.items())
    return per_byte


EXTRAS_SHOP_OFFSETS_TO_AP_LOCATIONS: dict[MemoryOffset, dict[BitMask, LocationId]] = _extras_to_shop_address()


def _characters_to_shop_address() -> dict[MemoryOffset, dict[BitMask, LocationId]]:
    per_byte: dict[MemoryOffset, dict[BitMask, LocationId]] = {}
    for character in CHARACTERS_AND_VEHICLES_BY_NAME.values():
        if character.shop_slot == -1:
            # Not present in the shop.
            continue
        if character.code == -1:
            # Not implemented yet.
            continue
        if character.name in ("Indiana Jones", "Princess Leia (Prisoner)", "TIE Interceptor"):
            # todo: Needs to be added as an Archipelago location
            continue
        byte_offset = character.shop_slot // 8
        bit_mask = 1 << (character.shop_slot % 8)
        location_name = f"Purchase {character.name}"
        assert location_name in LOCATION_NAME_TO_ID, f"Error: {location_name} is not a location name"
        location_id = LOCATION_NAME_TO_ID[location_name]
        per_byte.setdefault(byte_offset, {})[bit_mask] = location_id
    return per_byte


CHARACTER_SHOP_OFFSETS_TO_AP_LOCATIONS: dict[MemoryOffset, dict[BitMask, LocationId]] = _characters_to_shop_address()


def _read_extras_purchase_locations(process: pymem.Pymem) -> set[int]:
    extras_shop_bytes = process.read_bytes(EXTRAS_SHOP_START, EXTRAS_SHOP_LENGTH_BYTES)
    s = set()
    for byte_offset, bits_to_ap_locations in EXTRAS_SHOP_OFFSETS_TO_AP_LOCATIONS.items():
        byte = extras_shop_bytes[byte_offset]
        for bit_offset, ap_location_id in bits_to_ap_locations.items():
            if byte & bit_offset:
                s.add(ap_location_id)
    return s


def _read_minikit_locations(process: pymem.Pymem) -> set[int]:
    s = set()
    for address, names_to_ap_locations in MINIKIT_ADDRESSES_AND_NAMES.items():
        # Read the bytes for the number of minikit names that can be at this address (the number of minikits in this
        # particular sublevel, e.g. Negotiations_A)
        length = len(names_to_ap_locations)
        names_bytes = process.read_bytes(address, length * MINIKIT_NAME_LENGTH_BYTES)

        # Find all the names as 8-byte null-terminated strings.
        # names: set[bytes] = set(struct.unpack("8s" * length, names_bytes))
        # for name, ap_location in names_to_ap_locations.items():
        #     if name in names:
        #         s.add(ap_location)

        # Alternative. todo: Which is faster?
        # Iterate the names as 8-byte null-terminated strings.
        for unpacked in struct.unpack("8s" * length, names_bytes):
            # The names in the mapping are null-terminated and padded to 8 bytes in advance.
            # todo: Could do this. It's faster to start with, but slower once more minikits have been collected.
            # if unpacked == b"\x00\x00\x00\x00\x00\x00\x00\x00":
            #     # No more to read.
            #     break
            if unpacked in names_to_ap_locations:
                s.add(names_to_ap_locations[unpacked])
            else:
                logger.warning("Unexpected unpacked minikit name %s for sublevel address %s", unpacked, address)
    return s


class UnlockedLevelManager:
    first_time_setup_complete: bool = False
    pending_unlocks: list[EpisodeGameLevelArea]
    character_to_dependent_game_levels: dict[int, list[str]]
    remaining_level_item_requirements: dict[str, set[int]]

    def __init__(self) -> None:
        self.pending_unlocks = []

        item_id_to_level_area_short_name: dict[int, list[str]] = {}
        remaining_level_item_requirements: dict[str, set[int]] = {}
        for level_area in GAME_LEVEL_AREAS:
            item_requirements = level_area.item_requirements
            # TODO: Once Obi-Wan, Qui-Gon and TC-14 are added as real items, remove this if-statement.
            if item_requirements:
                code_requirements = set()
                for item_name in item_requirements:
                    item_code = ITEM_DATA_BY_NAME[item_name].code
                    assert item_code != -1
                    item_id_to_level_area_short_name.setdefault(item_code, []).append(level_area.short_name)
                    code_requirements.add(item_code)
                remaining_level_item_requirements[level_area.short_name] = code_requirements
            else:
                # Immediately unlocked.
                self.pending_unlocks.append(level_area)

        self.character_to_dependent_game_levels = item_id_to_level_area_short_name
        self.remaining_level_item_requirements = remaining_level_item_requirements

    def on_character_or_episode_unlocked(self, character_ap_id: int):
        dependent_levels = self.character_to_dependent_game_levels.get(character_ap_id)
        if dependent_levels is None:
            return

        for dependent_area_short_name in dependent_levels:
            remaining_requirements = self.remaining_level_item_requirements[dependent_area_short_name]
            assert remaining_requirements
            assert character_ap_id in remaining_requirements, f"{ITEM_DATA_BY_ID[character_ap_id].name} not found in {sorted([ITEM_DATA_BY_ID[code] for code in remaining_requirements])}"
            remaining_requirements.remove(character_ap_id)
            logger.info("Removed %s from %s requirements", ITEM_DATA_BY_ID[character_ap_id].name, dependent_area_short_name)
            if not remaining_requirements:
                self.pending_unlocks.append(SHORT_NAME_TO_LEVEL_AREA[dependent_area_short_name])
                del self.remaining_level_item_requirements[dependent_area_short_name]

        del self.character_to_dependent_game_levels[character_ap_id]

    def first_time_setup(self, ctx: "LegoStarWarsTheCompleteSagaContext"):
        self.first_time_setup_complete = True
        # Lock all levels to start with.
        locked = b"\x00"
        # Complete all Story Modes so that players can get straight into playing Free Play.
        # If Story Mode would to be left required for players to play through, cutscenes would likely want to be modded
        # out by unpacking and modifying the files, which is what the standalone TCS Randomizer does. Currently, this
        # TCS AP client is implemented with memory modifications only, though a one-time setup for an AP mod could be
        # viable in the near-ish future.
        story_mode_complete = b"\x01"
        to_write = locked + story_mode_complete
        for level_area in GAME_LEVEL_AREAS:
            # The first byte is whether the level is unlocked.
            # The second byte is whether Story Mode has been completed (and the Gold Brick has been obtained).
            ctx.write_bytes(level_area.address, to_write, 2)

    @staticmethod
    def unlock_level(ctx: "LegoStarWarsTheCompleteSagaContext", level_area: EpisodeGameLevelArea):
        # The first byte indicates whether the level is unlocked.
        ctx.write_byte(level_area.address, 1)
        logger.info("Unlocked level %s (%s)", level_area.name, level_area.short_name)

    async def update_game_state(self, ctx: "LegoStarWarsTheCompleteSagaContext"):
        if not self.first_time_setup_complete:
            self.first_time_setup(ctx)
        # TODO: It might be necessary to constantly re-lock locked levels because playing a story level might cause the
        #  next level to get unlocked. TODO: Try it out.
        if self.pending_unlocks:
            for level_area in self.pending_unlocks:
                self.unlock_level(ctx, level_area)
            self.pending_unlocks.clear()


# todo: Write the first 15 bytes of the multiworld seed into custom character 2's name.
# todo: Maybe write a character that is impossible to put in a name normally (e.g. lowercase letter or one of \^<>[]
#  etc. and use that to determine if a seed is 'new'. This could even go in custom character 1's name instead because
#  the world should never be receiving enough items to use up 15 digits.
CUSTOM_CHARACTER2_NAME_OFFSET = 0x86E524 + 0x14 # string[15]


class AcquiredGeneric:
    RECEIVABLE_GENERIC_BY_AP_ID: ClassVar[dict[int, GenericItemData]] = {
        item.code: item for item in GENERIC_BY_NAME.values() if item.code != -1
    }
    EPISODE_UNLOCKS: ClassVar[dict[int, int]] = {
        GENERIC_BY_NAME[f"Episode {i} Unlock"].code: i for i in range(2, 6+1)
    }
    PROGRESSIVE_BONUS_CODE: ClassVar[int] = GENERIC_BY_NAME["Progressive Bonus Level"].code
    PROGRESSIVE_SCORE_MULTIPLIER: ClassVar[int] = GENERIC_BY_NAME["Progressive Score Multiplier"].code
    SCORE_MULIPLIER_EXTRAS: ClassVar[tuple[ExtraData, ExtraData, ExtraData, ExtraData, ExtraData]] = tuple([
        EXTRAS_BY_NAME["Score x2"],
        EXTRAS_BY_NAME["Score x4"],
        EXTRAS_BY_NAME["Score x6"],
        EXTRAS_BY_NAME["Score x8"],
        EXTRAS_BY_NAME["Score x10"],
    ])
    MINIKIT_ITEMS: ClassVar[dict[int, int]] = {
        GENERIC_BY_NAME["5 Minikits"].code: 5,
    }
    # Receiving these items does nothing currently.
    NOOP_ITEMS: ClassVar[tuple[int, ...]] = tuple([
        GENERIC_BY_NAME["Restart Level Trap"].code
    ])
    BONUS_CHARACTER_REQUIREMENTS: ClassVar[dict[int, AbstractSet[int]]] = {
        1: {CHARACTERS_AND_VEHICLES_BY_NAME["Anakin's Podracer"].character_index},
        2: {CHARACTERS_AND_VEHICLES_BY_NAME["Naboo Starfighter"].character_index},
        3: {CHARACTERS_AND_VEHICLES_BY_NAME["Republic Gunship"].character_index},
        4: {CHARACTERS_AND_VEHICLES_BY_NAME[name].character_index
            for name in ("Darth Vader", "Stormtrooper", "C-3PO")},
    }
    STUDS: ClassVar[dict[int, int]] = {
        GENERIC_BY_NAME["Purple Stud"].code: 10000
    }

    unlocked_episodes: set[int]
    progressive_bonus_count: int
    progressive_score_count: int
    minikit_count: int

    def __init__(self):
        self.unlocked_episodes = set()
        self.progressive_bonus_count = 0
        self.progressive_score_count = 0
        self.minikit_count = 0

    def receive_generic(self, ctx: "LegoStarWarsTheCompleteSagaContext", ap_item_id: int):
        # Studs are handled separately as part of the game watcher.
        if ap_item_id in self.STUDS:
            pass
        # Minikits
        elif ap_item_id in self.MINIKIT_ITEMS:
            self.minikit_count += 1
        # Progressive Bonus Unlock
        elif ap_item_id == self.PROGRESSIVE_BONUS_CODE:
            # if write_to_game:
            #     # fixme: Even if a door is built, it won't open unless the player has enough gold bricks.
            #     built_gold_brick_doors = ctx.read_uchar(BONUSES_BASE_ADDRESS)
            #     built_gold_brick_doors |= (1 << self.progressive_bonus_count)
            #     ctx.write_byte(BONUSES_BASE_ADDRESS, built_gold_brick_doors)
            self.progressive_bonus_count += 1
        # Progressive Score Multiplier
        elif ap_item_id == self.PROGRESSIVE_SCORE_MULTIPLIER:
            if self.progressive_score_count < len(self.SCORE_MULIPLIER_EXTRAS):
                ctx.acquired_extras.unlock_extra(self.SCORE_MULIPLIER_EXTRAS[self.progressive_score_count])
            self.progressive_score_count += 1
        # Episode Unlocks
        elif ap_item_id in self.EPISODE_UNLOCKS:
            self.unlocked_episodes.add(self.EPISODE_UNLOCKS[ap_item_id])
            ctx.unlocked_level_manager.on_character_or_episode_unlocked(ap_item_id)
        else:
            logger.error("Unhandled ap_item_id %s for generic item", ap_item_id)

    def give_studs(self, ctx: "LegoStarWarsTheCompleteSagaContext", ap_item_id: int):
        """
        Grant Studs to the player. Unlike other items, Studs are a consumable resource, so cannot simply be set to the
        number of received studs and instead must use the last/next item index from AP to determine when a Studs item is
        newly received by the current save file.
        """
        studs_to_add = self.STUDS.get(ap_item_id)
        if studs_to_add is None:
            logger.warning("Tried to receive unknown Studs item with item ID %i", ap_item_id)
            return
        current_stud_count = ctx.read_uint(STUD_COUNT)
        new_stud_count = min(current_stud_count + studs_to_add, MAX_STUD_COUNT)
        ctx.write_uint(STUD_COUNT, new_stud_count)

    async def update_game_state(self, ctx: "LegoStarWarsTheCompleteSagaContext"):
        # TODO: Is it even possible to close the bonus door? The individual bonus doors cannot be built until the player
        #   has enough Gold Bricks, but some of the doors have the same Gold Brick requirements, so making them
        #   progressive wouldn't work unless we could control that. Forcefully unlocking a bonus level door will not
        #   work unless the player has the required amount of Gold Bricks.
        # Bonus levels. There are 6.
        # The byte controls which of the bonus doors have been built, with 1 bit for each door in order of Gold Brick
        # cost.
        # todo: This byte should be an instance attribute that is updated whenever a Progressive Bonus Level is
        #  received, and whenever a Character requirement for a Bonus level is received.
        unlocked_bonuses_byte = 0
        for i in range(1, 7):
            if i <= self.progressive_bonus_count:
                character_requirements = self.BONUS_CHARACTER_REQUIREMENTS.get(i)
                if not character_requirements or character_requirements <= ctx.acquired_characters.unlocked_characters:
                    unlocked_bonuses_byte |= (1 << (i - 1))
        ctx.write_byte(BONUSES_BASE_ADDRESS, unlocked_bonuses_byte)


class AcquiredCharacters:
    ALL_CHARACTERS = CHARACTERS_AND_VEHICLES_BY_NAME
    RECEIVABLE_CHARACTERS_BY_AP_ID: ClassVar[dict[int, GenericCharacterData]] = {
        extra.code: extra for extra in CHARACTERS_AND_VEHICLES_BY_NAME.values() if extra.code != -1
    }
    MIN_CHARACTER_NUMBER: ClassVar[int] = min(char.character_index for char in RECEIVABLE_CHARACTERS_BY_AP_ID.values())
    MAX_CHARACTER_NUMBER: ClassVar[int] = max(char.character_index for char in RECEIVABLE_CHARACTERS_BY_AP_ID.values())
    RANDOMIZED_BYTES_RANGE: ClassVar[range] = range(MIN_CHARACTER_NUMBER, MAX_CHARACTER_NUMBER + 1)
    NUM_RANDOMIZED_BYTES: ClassVar[int] = len(RANDOMIZED_BYTES_RANGE)
    START_ADDRESS: ClassVar[int] = CHARACTERS_UNLOCKED_START + MIN_CHARACTER_NUMBER
    # Each Character Shop index to the character index of the Character in that slot.
    SHOP_INDEX_TO_CHARACTER_INDEX: ClassVar[dict[int, int]] = {
        i: CHARACTERS_AND_VEHICLES_BY_NAME[name].character_index for i, name in enumerate(CHARACTER_SHOP_SLOTS.keys())
    }

    # Buying a character from the shop unlocks a character even though it shouldn't because it is supposed to be a
    # randomized location check, so unlockable characters need to be reset occasionally.
    # todo: This is probably only necessary to do while in the Cantina, but currently it is always being done.
    # Completing a story mode level will also probably unlock a character, maybe only if the story mode has not already
    # been completed.
    unlocked_characters: set[int]

    def __init__(self):
        self.unlocked_characters = set()
        self.locked_characters = {char.character_index for char in self.RECEIVABLE_CHARACTERS_BY_AP_ID.values()}

    def unlock_character(self, character: GenericCharacterData):
        self.unlocked_characters.add(character.character_index)

    def receive_character(self, ap_item_id: int):
        """Receive a Character from AP, to be given to the player the next time the game state is updated."""
        if ap_item_id not in self.RECEIVABLE_CHARACTERS_BY_AP_ID:
            logger.warning("Tried to receive unknown character with item ID %i", ap_item_id)
            return

        char = self.RECEIVABLE_CHARACTERS_BY_AP_ID[ap_item_id]

        # While there are not normally duplicate characters, receiving duplicates does nothing.
        self.unlock_character(char)

    async def update_game_state(self, ctx: "LegoStarWarsTheCompleteSagaContext") -> None:
        """
        Update the game memory that stores which Characters are unlocked, with all the currently unlocked/locked
        Characters according to Archipelago.

        This is done constantly because the game has not been modified to disable vanilla Character unlocks from Story
        completion, shop purchases and other means (see CHARS/COLLECTION.TXT in an unpacked game).

        At least already purchased Characters do not re-unlock themselves automatically like with already purchased
        Extras.
        """
        # todo: See if there is a performance hit to doing all 137 (or more once we add more vehicles) writes
        #  separately. It would technically be safer.
        chars = ctx.read_bytes(self.START_ADDRESS, self.NUM_RANDOMIZED_BYTES)
        chars_array = bytearray(chars)

        for char in self.RECEIVABLE_CHARACTERS_BY_AP_ID.values():
            character_index = char.character_index
            if character_index in self.unlocked_characters:
                chars_array[character_index - self.MIN_CHARACTER_NUMBER] = 3
            else:
                chars_array[character_index - self.MIN_CHARACTER_NUMBER] = 0

        # TC-14 is unlocked by completing Negotiations Story Mode, so we need to manually unlock them as they are
        # required to complete Negotiations Free Play (assuming C-3PO/IG-88/4-LOM have not been unlocked).
        # TODO: Once random starting level is implemented, remove this (and make TC-14 an AP item alongside Qui-Gon and
        #  Obi-Wan).
        chars_array[CHARACTERS_AND_VEHICLES_BY_NAME["TC-14"].character_index - self.MIN_CHARACTER_NUMBER] = 3

        # If the player is in the Character Shop, temporarily lock the character they have selected for purchase if that
        # Character has already been unlocked through receiving that Character from Archipelago.
        if ctx.is_in_shop(ShopType.CHARACTERS):
            current_character_shop_slot_index = ctx.read_uchar(CHARACTERS_SHOP_ACTIVE_INDEX)
            slot_byte = current_character_shop_slot_index // 8
            slot_bit_mask = 1 << (current_character_shop_slot_index % 8)

            character_index_for_slot = self.SHOP_INDEX_TO_CHARACTER_INDEX[current_character_shop_slot_index]

            # Check if the Character at the currents shop slot is in the range of bytes for randomized Characters.
            if character_index_for_slot in self.RANDOMIZED_BYTES_RANGE:
                # Check if the Character at the current shop slot is already unlocked.
                byte_index = character_index_for_slot - self.MIN_CHARACTER_NUMBER
                if chars_array[byte_index] == 3:
                    # Check if the Character at the current shop slot has not been purchased.
                    character_shop_byte = ctx.read_uchar(CHARACTERS_SHOP_START + slot_byte)
                    if not (character_shop_byte & slot_bit_mask):
                        # The Character is unlocked, but not purchased yet, so lock the character temporarily to allow
                        # purchase.
                        chars_array[byte_index] = 0

        ctx.write_bytes(self.START_ADDRESS, bytes(chars_array), self.NUM_RANDOMIZED_BYTES)


def _make_extras_randomized_bits(bytes_range: range, receivable_extras: Iterable[ExtraData]
                                 ) -> tuple[dict[int, set[int]], tuple[ExtraData, ...]]:
    # Initialize to all bits randomized, then update by removing non-randomized bits.
    non_randomized_bits_in_randomized_bytes: dict[int, set[int]] = {
        i: {1, 2, 4, 8, 16, 32, 64, 128} for i in bytes_range
    }
    # Remove bits that are randomized.
    for extra in receivable_extras:
        non_randomized_bits_in_randomized_bytes[extra.shop_slot_byte].remove(extra.shop_slot_bit_mask)
    # Remove bytes with all bits randomized.
    non_randomized_bits_in_randomized_bytes = {i: bits for i, bits in non_randomized_bits_in_randomized_bytes.items()
                                               if bits}

    randomized_extras_in_partially_randomized_bytes: tuple[ExtraData, ...] = tuple([
        extra for extra in receivable_extras
        if extra.shop_slot_byte in non_randomized_bits_in_randomized_bytes
    ])

    return non_randomized_bits_in_randomized_bytes, randomized_extras_in_partially_randomized_bytes


class AcquiredExtras:
    RECEIVABLE_EXTRAS_BY_AP_ID: ClassVar[dict[int, ExtraData]] = {
        extra.code: extra for extra in EXTRAS_BY_NAME.values() if extra.code != -1
    }
    ALL_RECEIVABLE_EXTRAS: ClassVar[list[ExtraData]] = [
        *RECEIVABLE_EXTRAS_BY_AP_ID.values(),
        # Score multipliers are applied progressively depending on the number of "Progressive Score Multiplier"
        # received.
        EXTRAS_BY_NAME["Score x2"],
        EXTRAS_BY_NAME["Score x4"],
        EXTRAS_BY_NAME["Score x6"],
        EXTRAS_BY_NAME["Score x8"],
        EXTRAS_BY_NAME["Score x10"],
    ]
    # All bytes in the UnlockedExtras
    MIN_RANDOMIZED_BYTE: ClassVar[int] = min(extra.shop_slot_byte for extra in ALL_RECEIVABLE_EXTRAS)
    MAX_RANDOMIZED_BYTE: ClassVar[int] = max(extra.shop_slot_byte for extra in ALL_RECEIVABLE_EXTRAS)
    RANDOMIZED_BYTES_RANGE: ClassVar[range] = range(MIN_RANDOMIZED_BYTE, MAX_RANDOMIZED_BYTE + 1)
    NUM_RANDOMIZED_BYTES: ClassVar[int] = len(RANDOMIZED_BYTES_RANGE)

    _t = _make_extras_randomized_bits(RANDOMIZED_BYTES_RANGE, ALL_RECEIVABLE_EXTRAS)
    NON_RANDOMIZED_BITS_IN_RANDOMIZED_BYTES: ClassVar[dict[int, set[int]]] = _t[0]
    RANDOMIZED_EXTRAS_IN_PARTIALLY_RANDOMIZED_BYTES: ClassVar[tuple[ExtraData, ...]] = _t[1]
    del _t

    START_ADDRESS: ClassVar[int] = EXTRAS_UNLOCKED_START + MIN_RANDOMIZED_BYTE

    unlocked_extras: bytearray

    def __init__(self):
        # Min and max are inclusive, so `+ 1` is needed.
        self.unlocked_extras = bytearray(self.NUM_RANDOMIZED_BYTES)

    def is_extra_unlocked(self, extra: ExtraData) -> bool:
        return (self.unlocked_extras[extra.shop_slot_byte + self.MIN_RANDOMIZED_BYTE] & extra.shop_slot_bit_mask) != 0

    # Unused, but here for reference.
    # def lock_extra(self, extra: ExtraData):
    #     self.unlocked_extras[extra.shop_slot_byte + self.MIN_RANDOMIZED_BYTE] &= ~extra.shop_slot_bit_mask

    def unlock_extra(self, extra: ExtraData):
        logger.info("Unlocking extra %s", extra.name)
        byte_index = extra.shop_slot_byte - self.MIN_RANDOMIZED_BYTE
        self.unlocked_extras[byte_index] |= extra.shop_slot_bit_mask

    def receive_extra(self, ap_item_id: int):
        """Receive an Extra from AP, to be given to the player the next time the game state is updated."""
        if ap_item_id not in self.RECEIVABLE_EXTRAS_BY_AP_ID:
            logger.warning("Tried to receive unknown extra with item ID %i", ap_item_id)
            return

        self.unlock_extra(self.RECEIVABLE_EXTRAS_BY_AP_ID[ap_item_id])

    async def update_game_state(self, ctx: "LegoStarWarsTheCompleteSagaContext"):
        """
        Update the game memory that stores which Extras are unlocked, with all the currently unlocked/locked extras
        according to Archipelago.

        This is done constantly because the game has not been modified to prevent purchasing an Extra from the shop from
        unlocking that Extra. Additionally, upon entering the Cantina, all already purchased Extras will unlock again.
        """
        # Create a copy so that `self.unlocked_extras` always represents only what has been received from Archipelago.
        unlocked_extras_copy = self.unlocked_extras.copy()

        # Retrieve the current bytes so that non-randomized bits can be maintained.
        current_unlocked_extras = ctx.read_bytes(self.START_ADDRESS, self.NUM_RANDOMIZED_BYTES)

        # Set all bytes that are only partially randomized or are not randomized at all.
        for i in self.NON_RANDOMIZED_BITS_IN_RANDOMIZED_BYTES.keys():
            byte_index = i - self.MIN_RANDOMIZED_BYTE
            unlocked_extras_copy[byte_index] = current_unlocked_extras[byte_index]

        # Merge in all bits of partially randomized bytes.
        for extra in self.RANDOMIZED_EXTRAS_IN_PARTIALLY_RANDOMIZED_BYTES:
            byte_index = extra.shop_slot_byte - self.MIN_RANDOMIZED_BYTE
            # If the bit is set:
            if self.unlocked_extras[byte_index] & extra.shop_slot_bit_mask:
                # Set the bit in `unlocked_extras_copy`.
                unlocked_extras_copy[byte_index] |= extra.shop_slot_bit_mask
            else:
                # Clear the bit in `unlocked_extras_copy`.
                unlocked_extras_copy[byte_index] &= ~extra.shop_slot_bit_mask

        # If the player is in the Extras shop in the Cantina, temporarily disable the Extra that is currently selected
        # in the Extras shop, so that it is possible to buy that extra, if it is unlocked, but not purchased.
        if ctx.is_in_shop(ShopType.EXTRAS):
            current_shop_slot = ctx.read_uchar(EXTRAS_SHOP_ACTIVE_INDEX)
            extra_byte = current_shop_slot // 8
            extra_bit_mask = 1 << (current_shop_slot % 8)

            # Check if the Extra at the current shop slot is in the range of bytes for randomized Extras.
            if extra_byte in self.RANDOMIZED_BYTES_RANGE:
                # Check if the Extra at the current shop slot is already unlocked.
                byte_index = extra_byte - self.MIN_RANDOMIZED_BYTE
                if self.unlocked_extras[byte_index] & extra_bit_mask:
                    # Check if the Extra at the current shop slot has not been purchased.
                    extras_shop_byte = ctx.read_uchar(EXTRAS_SHOP_START + extra_byte)
                    if not (extras_shop_byte & extra_bit_mask):
                        # The Extra is unlocked, but not purchased yet, so lock it temporarily to allow the purchase.
                        unlocked_extras_copy[byte_index] &= ~extra_bit_mask

        # Write the updated extras array.
        ctx.write_bytes(self.START_ADDRESS, bytes(unlocked_extras_copy), self.NUM_RANDOMIZED_BYTES)


# TODO: How quickly can a player reasonably skip through the level completion screen? Do we need to check for level
#  completion with a higher frequency than how often the game watcher is checking?
class FreePlayLevelCompletionChecker:
    """
    Check if the player has completed a free play level by looking for the ending screen that tallies up new
    studs/minikits.

    There appears to be no persistent storage in the game's memory or save data for whether a level has been completed
    in Free Play, so the client
    """
    STATUS_LEVEL_ID_TO_AP_ID = {
        area.status_level_id: LOCATION_NAME_TO_ID[LEVEL_COMMON_LOCATIONS[area.short_name]["Completion"]]
        for area in GAME_LEVEL_AREAS
    }

    sent_locations: set[LocationId]

    def __init__(self):
        self.sent_locations = set()

    async def check_completion(self, ctx: "LegoStarWarsTheCompleteSagaContext", new_location_checks: list[LocationId]):
        # Level ID should be checked first because STATUS_LEVEL_TYPE_ADDRESS can be STATUS_LEVEL_TYPE_LEVEL_COMPLETION
        # during normal gameplay, so it would be possible for STATUS_LEVEL_TYPE_ADDRESS to match and then the player
        # does 'Save and Exit', changing the Level ID to
        completion_location_id = self.STATUS_LEVEL_ID_TO_AP_ID.get(ctx.get_current_level_id())
        if (completion_location_id is not None
                and completion_location_id in ctx.missing_locations
                and ctx.read_uchar(CURRENT_GAME_MODE_ADDRESS) == CURRENT_GAME_MODE_FREE_PLAY
                and ctx.read_uchar(STATUS_LEVEL_TYPE_ADDRESS) == STATUS_LEVEL_TYPE_LEVEL_COMPLETION):
            self.sent_locations.add(completion_location_id)

        self.sent_locations.difference_update(ctx.checked_locations)

        # Locations to send to the server will be filtered to only those in ctx.missing_locations, so include everything
        # up to this point in-case one was missed in a disconnect.
        new_location_checks.extend(self.sent_locations)


class BonusLevelCompletionChecker:
    # Anakin's Flight and A New Hope support Free Play, but the rest are Story mode only.
    remaining_story_completion_checks: dict[MemoryAddress, LocationId]

    def __init__(self):
        self.remaining_story_completion_checks = {
            bonus.address + bonus.completion_offset: LOCATION_NAME_TO_ID[bonus.name] for bonus in BONUS_GAME_LEVEL_AREAS
        }

    async def check_completion(self, ctx: "LegoStarWarsTheCompleteSagaContext", new_location_checks: list[int]):
        updated_remaining_story_completion_checks = {}
        for address, ap_id in self.remaining_story_completion_checks.items():
            if ap_id in ctx.checked_locations:
                continue
            if ctx.read_uchar(address):
                new_location_checks.append(ap_id)
            updated_remaining_story_completion_checks[address] = ap_id
        self.remaining_story_completion_checks = updated_remaining_story_completion_checks


class TrueJediAndMinikitChecker:
    remaining_true_jedi_checks: list[str]
    remaining_minikit_checks: dict[str, list[tuple[int, str]]]

    def __init__(self):
        self.remaining_true_jedi_checks = list(LEVEL_COMMON_LOCATIONS.keys())
        self.remaining_minikit_checks = {
            name: list(enumerate(data["Minikits"], start=1)) for name, data in LEVEL_COMMON_LOCATIONS.items()
        }

    async def check_true_jedi_and_minikits(self,
                                           ctx: "LegoStarWarsTheCompleteSagaContext",
                                           new_location_checks: list[int]):
        # todo: More smartly read only as many bytes as necessary. So only 1 byte when either the True Jedi is complete
        #  or all Minikits have been collected.
        cached_bytes: dict[str, tuple[int, int]] = {}

        def get_bytes_for_short_name(short_name: str):
            if short_name in cached_bytes:
                return cached_bytes[short_name]
            else:
                # True Jedi seems to be at the 4th byte (maybe it is the 3rd because they both get activated?), Minikit
                # count is at the 6th byte. To reduce memory reads, both are retrieved simultaneously.
                read_bytes = ctx.read_bytes(SHORT_NAME_TO_LEVEL_AREA[short_name].address + 3, 3)
                true_jedi_byte = read_bytes[0]
                minikit_count_byte = read_bytes[2]
                new_bytes = (true_jedi_byte, minikit_count_byte)
                cached_bytes[short_name] = new_bytes
                return new_bytes

        updated_remaining_true_jedi_checks: list[str] = []
        for shortname in self.remaining_true_jedi_checks:
            location_name = LEVEL_COMMON_LOCATIONS[shortname]["True Jedi"]
            location_id = LOCATION_NAME_TO_ID[location_name]
            if location_id in ctx.checked_locations:
                continue
            true_jedi = get_bytes_for_short_name(shortname)[0]
            if true_jedi:
                new_location_checks.append(location_id)
            updated_remaining_true_jedi_checks.append(shortname)
        self.remaining_true_jedi_checks = updated_remaining_true_jedi_checks

        updated_remaining_minikit_checks: dict[str, list[tuple[int, str]]] = {}
        for shortname, remaining_minikits in self.remaining_minikit_checks.items():
            not_checked_minikit_checks: list[int] = []
            updated_remaining_minikits: list[tuple[int, str]] = []
            for count, location_name in remaining_minikits:
                location_id = LOCATION_NAME_TO_ID[location_name]
                if location_id not in ctx.checked_locations:
                    not_checked_minikit_checks.append(location_id)
                    updated_remaining_minikits.append((count, location_name))
            if updated_remaining_minikits:
                updated_remaining_minikit_checks[shortname] = updated_remaining_minikits

                minikit_count = get_bytes_for_short_name(shortname)[1]
                zipped = zip(updated_remaining_minikits, not_checked_minikit_checks, strict=True)
                for (count, _name), location_id in zipped:
                    if minikit_count >= count:
                        new_location_checks.append(location_id)
        self.remaining_minikit_checks = updated_remaining_minikit_checks


# TODO: Deduplicate the Extras and Characters checkers
class PurchasedCharactersChecker:
    remaining_character_purchases: dict[MemoryOffset, dict[BitMask, LocationId]]

    def __init__(self):
        self.remaining_character_purchases = {byte_offset: bit_mask_to_ap_id.copy() for byte_offset, bit_mask_to_ap_id
                                              in CHARACTER_SHOP_OFFSETS_TO_AP_LOCATIONS.items()}
        self.remaining_min_byte = min(self.remaining_character_purchases.keys())
        self.remaining_max_byte = max(self.remaining_character_purchases.keys())

    async def check_extra_purchases(self, ctx: "LegoStarWarsTheCompleteSagaContext", new_location_checks: list[int]):
        server_checked_locations = ctx.checked_locations
        updated_remaining_character_purchases: dict[MemoryOffset, dict[BitMask, LocationId]] = {}
        for byte_offset, bit_mask_to_ap_id in self.remaining_character_purchases.items():
            updated_bit_to_ap_id: dict[BitMask, LocationId] = {bit: ap_id for bit, ap_id in bit_mask_to_ap_id.items()
                                                               if ap_id not in server_checked_locations}
            if updated_bit_to_ap_id:
                updated_remaining_character_purchases[byte_offset] = updated_bit_to_ap_id

        if updated_remaining_character_purchases:
            min_byte_offset = min(updated_remaining_character_purchases.keys())
            max_byte_offset = max(updated_remaining_character_purchases.keys())
            num_bytes = max_byte_offset - min_byte_offset + 1
            characters_shop_bytes = ctx.read_bytes(CHARACTERS_SHOP_START + min_byte_offset, num_bytes)

            for byte_offset, bit_mask_to_ap_id in updated_remaining_character_purchases.items():
                shop_byte = characters_shop_bytes[byte_offset - min_byte_offset]
                for bit_mask, ap_id in bit_mask_to_ap_id.items():
                    if shop_byte & bit_mask:
                        new_location_checks.append(ap_id)
        self.remaining_character_purchases = updated_remaining_character_purchases


class PurchasedExtrasChecker:
    remaining_extra_purchases: dict[MemoryOffset, dict[BitMask, LocationId]]

    def __init__(self):
        self.remaining_extra_purchases = {byte_offset: bit_mask_to_ap_id.copy() for byte_offset, bit_mask_to_ap_id
                                          in EXTRAS_SHOP_OFFSETS_TO_AP_LOCATIONS.items()}
        self.remaining_min_byte = min(self.remaining_extra_purchases.keys())
        self.remaining_max_byte = max(self.remaining_extra_purchases.keys())

    async def check_extra_purchases(self, ctx: "LegoStarWarsTheCompleteSagaContext", new_location_checks: list[int]):
        server_checked_locations = ctx.checked_locations
        updated_remaining_extra_purchases: dict[MemoryOffset, dict[BitMask, LocationId]] = {}
        for byte_offset, bit_mask_to_ap_id in self.remaining_extra_purchases.items():
            updated_bit_to_ap_id: dict[BitMask, LocationId] = {bit: ap_id for bit, ap_id in bit_mask_to_ap_id.items()
                                                               if ap_id not in server_checked_locations}
            if updated_bit_to_ap_id:
                updated_remaining_extra_purchases[byte_offset] = updated_bit_to_ap_id

        if updated_remaining_extra_purchases:
            min_byte_offset = min(updated_remaining_extra_purchases.keys())
            max_byte_offset = max(updated_remaining_extra_purchases.keys())
            num_bytes = max_byte_offset - min_byte_offset + 1
            extras_shop_bytes = ctx.read_bytes(EXTRAS_SHOP_START + min_byte_offset, num_bytes)

            for byte_offset, bit_mask_to_ap_id in updated_remaining_extra_purchases.items():
                shop_byte = extras_shop_bytes[byte_offset - min_byte_offset]
                for bit_mask, ap_id in bit_mask_to_ap_id.items():
                    if shop_byte & bit_mask:
                        new_location_checks.append(ap_id)
        self.remaining_extra_purchases = updated_remaining_extra_purchases

# class PurchasedGoldBricks:
#     pass


# class PurchasedHints:
#     pass

class NoProcessError(RuntimeError):
    pass


class LegoStarWarsTheCompleteSagaContext(CommonContext):
    game = GAME_NAME
    items_handling = 0b111  # Fully remote

    game_process: pymem.Pymem | None = None
    previous_level_id: int = -1
    current_level_id: int = 0  # Title screen
    # Memory in the GOG version is offset 32 bytes. Memory in the retail version is offset ?? bytes.
    memory_offset: int = 0
    acquired_characters: AcquiredCharacters
    acquired_extras: AcquiredExtras
    acquired_generic: AcquiredGeneric
    unlocked_level_manager: UnlockedLevelManager
    client_expected_idx: int

    # Location checkers.
    free_play_completion_checker: FreePlayLevelCompletionChecker
    true_jedi_and_minikit_checker: TrueJediAndMinikitChecker
    purchased_extras_checker: PurchasedExtrasChecker
    purchased_characters_checker: PurchasedCharactersChecker
    bonus_level_completion_checker: BonusLevelCompletionChecker

    fully_connected: bool

    def __init__(self, server_address: typing.Optional[str] = None, password: typing.Optional[str] = None) -> None:
        super().__init__(server_address, password)

        # todo: These assigned values shouldn't get used, can we safely remove them?
        self.acquired_extras = AcquiredExtras()
        self.acquired_characters = AcquiredCharacters()
        self.acquired_generic = AcquiredGeneric()
        self.unlocked_level_manager = UnlockedLevelManager()
        self.free_play_completion_checker = FreePlayLevelCompletionChecker()
        self.true_jedi_and_minikit_checker = TrueJediAndMinikitChecker()
        self.purchased_extras_checker = PurchasedExtrasChecker()
        self.purchased_characters_checker = PurchasedCharactersChecker()
        self.bonus_level_completion_checker = BonusLevelCompletionChecker()
        self.client_expected_idx = 0
        self.fully_connected = False

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)
        if cmd == "Connected":
            self.reset_client()
            self.client_expected_idx = 0
            self.fully_connected = True

    def run_gui(self):
        from kvui import GameManager

        class LegoStarWarsTheCompleteSagaManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Lego Star Wars: The Complete Saga Client"

        self.ui = LegoStarWarsTheCompleteSagaManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

    async def disconnect(self, allow_autoreconnect: bool = False):
        # todo: What are the connect and disconnect methods to override?
        # todo: When receiving item index 0, we also want to destroy and re-create the 'acquired' attributes.
        # todo: Do we want to replace these when connecting instead?
        self.reset_client()
        self.fully_connected = False
        return await super().disconnect(allow_autoreconnect)

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        self.tags = set()
        await self.send_connect()

    async def shutdown(self):
        logger.info("Shutting down client")
        self.unhook_game_process()
        return await super().shutdown()

    def open_game_process(self):
        try:
            process = pymem.Pymem(PROCESS_NAME)
        except ProcessNotFound:
            logger.info(f"{PROCESS_NAME} process not found. Make sure it is running.")
            return False
        except ProcessError as err:
            logger.info(f"Unexpected error connecting to game process: {err}.")
            return False

        # Find the address of a unique pattern to determine offsets.
        found_address = pymem.pattern.pattern_scan_all(process.process_handle, VERSION_CHECK_PATTERN)
        if found_address is None:
            logger.info(f"Connected to process but could not determine memory offsets. Supported game versions are"
                        f" Steam and GOG, make sure your LegoStarWarsSaga.exe has not been modified.")
            return False

        # All memory addresses in this file are for the STEAM version, so the offset is based on the STEAM version as
        # the base.
        memory_offset = found_address - VERSION_CHECK_ADDRESS_STEAM

        if memory_offset == MEMORY_OFFSET_STEAM:
            logger.info("Connected to STEAM version successfully")
        elif memory_offset == MEMORY_OFFSET_GOG:
            logger.info("Connected to GOG version successfully")
        else:
            logger.info(f"Connected to unknown game version with memory offset {memory_offset:X}")

        self.memory_offset = found_address - VERSION_CHECK_ADDRESS_STEAM
        self.game_process = process
        return True

    def unhook_game_process(self):
        if self.game_process is not None:
            self.game_process.close_process()
            self.game_process = None
            logger.info("Unhooked game process")

    @property
    def _game_process(self) -> pymem.Pymem:
        process = self.game_process
        if process is None:
            raise NoProcessError("No process to read from")
        else:
            return process

    def read_uint(self, address: int) -> int:
        return self._game_process.read_uint(self.memory_offset + address)

    def read_ushort(self, address: int) -> int:
        return self._game_process.read_short(self.memory_offset + address)

    def read_bytes(self, address: int, length: int) -> bytes:
        return self._game_process.read_bytes(self.memory_offset + address, length)

    def read_byte(self, address: int) -> bytes:
        return self._game_process.read_bytes(self.memory_offset + address, 1)

    def read_uchar(self, address: int) -> int:
        return self._game_process.read_uchar(self.memory_offset + address)
        #return self._game_process.read_bytes(self.memory_offset + address, 1)[0]

    def write_uint(self, address: int, value: int) -> None:
        self._game_process.write_uint(self.memory_offset + address, value)

    def write_byte(self, address: int, value: int) -> None:
        self._game_process.write_uchar(self.memory_offset + address, value)

    def write_bytes(self, address: int, value: bytes, length: int) -> None:
        self._game_process.write_bytes(self.memory_offset + address, value, length)

    def get_current_level_id(self) -> int:
        return self.read_ushort(CURRENT_LEVEL_ID)

    def is_in_game(self) -> bool:
        # There are more than 255 levels, but far fewer than 65536, so assume 2 bytes.
        return (process := self.game_process) is not None and process.read_ushort(self.memory_offset + CURRENT_LEVEL_ID) != 0

    def is_in_shop(self, shop_type: ShopType) -> bool:
        """Check whether the player is currently in a shop. Does not check for being in-game."""
        # todo: Just the SHOP_CHECK is probably enough to determine whether the player is in a shop, but it is not clear
        #  if that byte is used for something more general than only the shop.
        return (self.read_byte(SHOP_CHECK) == SHOP_CHECK_IS_IN_SHOP
                and self.get_current_level_id() == LEVEL_ID_CANTINA  # Additionally check the player is in the Cantina,
                and self.read_uchar(CANTINA_ROOM_ID) == CANTINA_ROOM_WITH_SHOP  # and in the room with the shops.
                and self.read_uchar(ACTIVE_SHOP_TYPE_ADDRESS) == shop_type.value)

    def set_game_expected_idx(self, idx: int) -> None:
        # Storing this in Custom Character 1's name as a string for now.
        to_write = str(idx).encode()
        if len(to_write) > 15:
            raise RuntimeError(f"Error: cannot set expected idx to {to_write}, integer is too large. Max of 15 digits.")
        if len(to_write) < 15:
            # Null terminate.
            to_write += b"\x00" * (15 - len(to_write))
        self.write_bytes(CUSTOM_CHARACTER_1_NAME, to_write, len(to_write))

    def get_game_expected_idx(self) -> int:
        # Storing this in Custom Character 1's name as a string for now.
        as_bytestring = self.read_bytes(CUSTOM_CHARACTER_1_NAME, 15)
        # STRANGER 1
        if as_bytestring[0] not in range(b"0"[0], b"9"[0] + 1):
            return 0
        try:
            return int(as_bytestring.partition(b"\x00")[0])
        except ValueError:
            return 0

    def give_item(self, code: int) -> bool:
        if code in self.acquired_generic.STUDS:
            # Studs are directly given to the player as they are received, so it is necessary to check that the player
            # is currently in-game.
            if not self.is_in_game():
                return False
            self.acquired_generic.give_studs(self, code)
        else:
            self.receive_item(code)
        return True

    def receive_item(self, code: int):
        from . import LegoStarWarsTCSWorld
        item_name = LegoStarWarsTCSWorld.item_id_to_name.get(code, f"Unknown {code}")
        logger.info(f"Receiving item {item_name} from AP")
        if code in self.acquired_generic.RECEIVABLE_GENERIC_BY_AP_ID:
            self.acquired_generic.receive_generic(self, code)
        elif code in self.acquired_characters.RECEIVABLE_CHARACTERS_BY_AP_ID:
            self.acquired_characters.receive_character(code)
            self.unlocked_level_manager.on_character_or_episode_unlocked(code)
        elif code in self.acquired_extras.RECEIVABLE_EXTRAS_BY_AP_ID:
            self.acquired_extras.receive_extra(code)
        else:
            logger.warning(f"Received unknown item with AP ID {code}")

    def reset_client(self):
        self.acquired_extras = AcquiredExtras()
        self.acquired_characters = AcquiredCharacters()
        self.acquired_generic = AcquiredGeneric()
        self.unlocked_level_manager = UnlockedLevelManager()
        self.client_expected_idx = 0
        self.free_play_completion_checker = FreePlayLevelCompletionChecker()
        self.true_jedi_and_minikit_checker = TrueJediAndMinikitChecker()
        self.purchased_extras_checker = PurchasedExtrasChecker()
        self.purchased_characters_checker = PurchasedCharactersChecker()
        self.bonus_level_completion_checker = BonusLevelCompletionChecker()


async def give_items(ctx: LegoStarWarsTheCompleteSagaContext):
    if ctx.is_in_game():
        #logger.info("Giving items")
        # The player can enter a level, receive items, and then exit back to the Cantina without saving, reverting their
        # expected_idx to an older value and undoing any studs that were given.
        # To ensure that given studs take into account the player's score multiplier at the time the studs were given,
        # it is necessary to reset client state in this case.
        expected_idx_game = ctx.get_game_expected_idx()
        expected_idx_client = ctx.client_expected_idx

        received_items = ctx.items_received

        # Check if the game rolled back its save data, the client needs to be reset and caught back up.
        if expected_idx_game < ctx.client_expected_idx:
            logger.info("Resetting client received items due to game save data rollback")
            ctx.reset_client()
            for idx, item in enumerate(received_items[:expected_idx_game]):
                ctx.receive_item(item.item)
                ctx.client_expected_idx = idx + 1

        # Check if we are resuming a seed where the client is fresh and needs to be caught up.
        if ctx.client_expected_idx < expected_idx_game:
            logger.info("Catching up client to game state")
            for idx, item in enumerate(received_items[expected_idx_client:expected_idx_game],
                                       start=expected_idx_client):
                ctx.receive_item(item.item)
                ctx.client_expected_idx = idx + 1

        # Check if there are new items.
        if len(received_items) <= expected_idx_game:
            # There are no new items.
            return

        # Loop through items to give.
        # Give the player all items at an index greater than or equal to the expected index.
        for idx, item in enumerate(received_items[expected_idx_game:], start=expected_idx_game):
            while not ctx.give_item(item.item):
                await asyncio.sleep(0.01)

            # Increment the expected index.
            ctx.set_game_expected_idx(idx + 1)
            ctx.client_expected_idx = idx + 1


async def game_watcher(ctx: LegoStarWarsTheCompleteSagaContext):
    logger.info("Starting connection to game.")
    last_message = ""
    sleep_time = 0.0
    while not ctx.exit_event.is_set():
        if sleep_time > 0.0:
            try:
                await asyncio.wait_for(ctx.watcher_event.wait(), sleep_time)
            except asyncio.TimeoutError:
                pass
            sleep_time = 0.0
        ctx.watcher_event.clear()

        try:
            game_process = ctx.game_process
            if game_process is not None:
                if not ctx.is_in_game():
                    # Need to wait for the player to load into a save file.
                    sleep_time = 0.5 #0.1
                    # todo: Save the multiworld seed somewhere (custom character 2 name?) and check that before giving
                    #  items. Then, it won't be necessary to disconnect when not loaded into a save file.
                    if ctx.slot:
                        logger.info("Disconnected due to exiting to main menu.")
                        await ctx.disconnect()
                    else:
                        msg = "Waiting for player to load into a save file"
                        if last_message != msg:
                            logger.info(msg)
                            last_message = msg
                    continue
                if ctx.slot is not None and ctx.fully_connected:
                    #logger.info("Checking items to give")
                    # todo: Store the multiworld seed name somewhere in the save file and check it before giving any
                    #  items or checking any locations. OR can we do this check when connecting and then immediately
                    #  disconnect if the seed name does not match?
                    # todo: Can we store the slot name somewhere too and check that also?
                    await give_items(ctx)

                    # Update game state for received items.
                    await ctx.acquired_characters.update_game_state(ctx)
                    await ctx.acquired_extras.update_game_state(ctx)
                    #await ctx.acquired_generic.update_game_state(ctx)
                    await ctx.unlocked_level_manager.update_game_state(ctx)

                    # Check for newly cleared locations.
                    new_location_checks: list[int] = []
                    await ctx.free_play_completion_checker.check_completion(ctx, new_location_checks)
                    await ctx.true_jedi_and_minikit_checker.check_true_jedi_and_minikits(ctx, new_location_checks)
                    await ctx.purchased_extras_checker.check_extra_purchases(ctx, new_location_checks)
                    await ctx.purchased_characters_checker.check_extra_purchases(ctx, new_location_checks)
                    await ctx.bonus_level_completion_checker.check_completion(ctx, new_location_checks)

                    # Send newly cleared locations to the server, if there are any.
                    await ctx.check_locations(new_location_checks)
                    # todo: Should the ones below here still run even when disconnected? If they are not run, then a
                    #  player could disconnect, buy a character from the shop, and then use that character without that
                    #  character getting disabled. Similar for purchased, but not unlocked, extras becoming unlocked
                    #  when they shouldn't because the AP item for the extra has not been received.
                    # Constantly reset unlocked characters while in the Cantina room with the shop because purchasing a
                    # character from the shop will unlock it for the player, but the unlock should be randomized, so we
                    # need to reset to undo it.
                    #await reset_characters_if_in_cantina_shop_room(ctx)
                    # TODO: Check if it's just upon entering the Cantina, or if changing any level will re-unlock them.
                    # Upon entering the cantina from another level, any extras purchased from the shop will re-unlock
                    # themselves, but they should remain locked until they are received from the multiworld.
                    #await reset_characters_and_extras_if_entering_cantina(ctx)
                    # If an extra has been unlocked because it has been received, that extra cannot be purchased from
                    # the shop, even if the shop slot has not been purchased. Temporarily disable the extra in the
                    # active shop slot if the shop slot has not been purchased, but the extra has been unlocked.
                    #await temporarily_disable_extra_of_unpurchased_active_extra_in_shop(ctx)
                sleep_time = 0.5 #0.1
            else:
                if not ctx.open_game_process():
                    msg = "Connection to game failed, attempting again in 5 seconds..."
                    logger.info(msg)
                    last_message = msg
                    await ctx.disconnect()
                    sleep_time = 5
                else:
                    # No wait, start processing items/locations/etc. immediately if the client is connected to the
                    # server.
                    pass
        except Exception as e:
            ctx.unhook_game_process()
            if isinstance(e, (PymemError, WinAPIError)):
                msg = "Game connection failed, attempting again in 5 seconds..."
            else:
                msg = "Unexpected error occurred, attempting again in 5 seconds..."
            logger.info(msg)
            last_message = msg
            logger.error(traceback.format_exc())
            await ctx.disconnect()
            sleep_time = 5


async def main():
    Utils.init_logging("LegoStarWarsTheCompleteSagaClient", exception_logger="ClientException")

    ctx = LegoStarWarsTheCompleteSagaContext()
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")

    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()

    game_watcher_task = asyncio.create_task(game_watcher(ctx), name="LegoStarWarsTheCompleteSagaGameWatcher")

    await ctx.exit_event.wait()
    # Wake the game watcher task, if it is currently sleeping, so it can start shutting down when it sees that the
    # exit_event is set.
    ctx.watcher_event.set()
    ctx.server_address = None

    await game_watcher_task
    await ctx.shutdown()


def launch():
    colorama.just_fix_windows_console()
    asyncio.run(main())
    colorama.deinit()
