import asyncio
import traceback

import colorama

import ModuleUpdate
import Utils

ModuleUpdate.update()


import logging
import struct
import typing
from pymem import pymem
from pymem.exception import ProcessNotFound, ProcessError, PymemError, WinAPIError
from typing import ClassVar

from CommonClient import CommonContext, server_loop, gui_enabled

from .constants import GAME_NAME
from .items import (
    ITEM_DATA,
    ExtraData,
    GenericCharacterData,
    CHARACTERS_AND_VEHICLES_BY_NAME,
    EXTRAS_BY_NAME,
    GENERIC_BY_NAME,
    GenericItemData,
)
from .locations import EXTRA_SHOP_LOCATION_START


logger = logging.getLogger("LSWTCSClient")


# FIXME/TODO: Where can we write the last received item index?
# FIXME: If an extra/character has already been unlocked, they cannot be bought from the shop.
#   A. The client detects when the shop is open and temporarily locks all unlocked extras/characters that are
#      purchasable and have yet to be purchased
# FIXME: Buying an extra from the shop will re-unlock it when entering the cantina. The client will probably have to
#  constantly disable any extras that are not unlocked according to AP.

# todo: How to detect GOG executable and offset all addresses?


PROCESS_NAME = "LEGOStarWarsSaga"

# This memory pattern was found in Dread Pony Roberts' cheat table.
VERSION_CHECK_PATTERN = b"\x0F\xBE\xAE\x7F\x10\x00\x00"
VERSION_CHECK_ADDRESS_STEAM = 0x4B894C

MEMORY_OFFSET_STEAM = 0
MEMORY_OFFSET_GOG = 0x20

# Note, this is not the in-level stud count. We don't add to that, because it is not saved.
STUD_COUNT = 0x86E4DC
MAX_STUD_COUNT = 4_000_000_000

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

EXTRAS_SHOP_START = 0x86E4B8
EXTRAS_SHOP_LENGTH_BYTES = 6 # 0xB8 to 0xBD
# Active slot in the shop, maybe we can use this in combination with CANTINA_ROOM_ID and LEVEL_ID_CANTINA to only
# temporarily lock unpurchased extras that are currently active?
# Note: The previous 2 and next 2 shop indices are before/after this in memory (5 on screen at once).
EXTRAS_SHOP_ACTIVE_INDEX = 0x87BDF8
EXTRAS_UNLOCKED_START = 0x86E4C8


CHARACTERS_SHOP_START = 0x86E4A8 # todo: Not mapped yet
CHARACTERS_UNLOCKED_START = 0x86E5C0


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
        b"m_pup1",
    }
}

def _s8(b: bytes) -> bytes:
    """Null terminate and pad an 8 byte string"""
    if len(b) >= 8:
        raise AssertionError(f"String {b} is too long")
    return b + b"\x00" * (8 - len(b))
MINIKIT_ADDRESSES_AND_NAMES: dict[int, dict[bytes, int]] = {k: {_s8(k2): v2 for k2, v2 in v.items()}
                                                            for k, v in _MINIKIT_ADDRESSES_AND_NAMES.items()}


def _extras_to_shop_address() -> dict[int, dict[int, int]]:
    """Purchase <extra> shop ID -> AP Location ID"""
    per_byte: dict[int, dict[int, int]] = {}
    for item_data in ITEM_DATA:
        if not isinstance(item_data, ExtraData):
            continue
        if item_data.name == "Adaptive Difficulty":
            # Not present in the shop because it is always unlocked
            continue
        byte_offset = item_data.extra_number // 8
        bit = 1 << (item_data.extra_number % 8)
        location_id = item_data.extra_number + EXTRA_SHOP_LOCATION_START
        per_byte.setdefault(byte_offset, {})[bit] = location_id
    # todo: list[tuple[int, dict[int, int]]] for better iteration performance?
    # return list(per_byte.items())
    return per_byte


EXTRAS_SHOP_OFFSETS_TO_AP_LOCATIONS = _extras_to_shop_address()


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





# todo: Write the first 15 bytes of the multiworld seed into custom character 2's name.
CUSTOM_CHARACTER2_NAME_OFFSET = 0x86E524 + 0x14 # string[15]


class AcquiredGeneric:
    RECEIVABLE_GENERIC_BY_AP_ID: ClassVar[dict[int, GenericItemData]] = {
        item.code: item for item in GENERIC_BY_NAME.values() if item.code != -1
    }
    EPISODE_UNLOCKS: ClassVar[dict[int, int]] = {
        GENERIC_BY_NAME[f"Episode {i} Unlock"].code: i for i in range(2, 6+1)
    }
    STUDS: ClassVar[dict[int, int]] = {
        GENERIC_BY_NAME["Purple Stud"].code: 10000
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

    unlocked_episodes: set[int]
    progressive_bonus_count: int
    progressive_score_count: int
    minikit_count: int

    def __init__(self):
        self.unlocked_episodes = set()
        self.progressive_bonus_count = 0
        self.progressive_score_count = 0
        self.minikit_count = 0

    def give_generic(self, ctx: "LegoStarWarsTheCompleteSagaContext", ap_item_id: int, write_to_game: bool) -> bool:
        # Studs
        if ap_item_id in self.STUDS:
            if write_to_game:
                studs_to_add = self.STUDS[ap_item_id]
                current_stud_count = ctx.read_uint(STUD_COUNT)
                new_stud_count = min(current_stud_count + studs_to_add, MAX_STUD_COUNT)
                ctx.write_uint(STUD_COUNT, new_stud_count)
        # Minikits
        elif ap_item_id in self.MINIKIT_ITEMS:
            self.minikit_count += 1
        # Progressive Bonus Unlock
        elif ap_item_id == self.PROGRESSIVE_BONUS_CODE:
            if write_to_game:
                # fixme: Even if a door is built, it won't open unless the player has enough gold bricks.
                built_gold_brick_doors = ctx.read_byte(BONUSES_BASE_ADDRESS)
                built_gold_brick_doors |= (1 << self.progressive_bonus_count)
                ctx.write_byte(BONUSES_BASE_ADDRESS, built_gold_brick_doors)
            self.progressive_bonus_count += 1
        # Progressive Score Multiplier
        elif ap_item_id == self.PROGRESSIVE_SCORE_MULTIPLIER:
            self.progressive_score_count += 1
            if self.progressive_score_count < len(self.SCORE_MULIPLIER_EXTRAS):
                ctx.acquired_extras.give_extra_from_obj(ctx, self.SCORE_MULIPLIER_EXTRAS[self.progressive_score_count],
                                                        write_to_game)
        # Episode Unlocks
        elif ap_item_id in self.EPISODE_UNLOCKS:
            self.unlocked_episodes.add(self.EPISODE_UNLOCKS[ap_item_id])
        else:
            logger.error("Unhandled ap_item_id %s for generic item", ap_item_id)
            return False

        return True


class AcquiredCharacters:
    ALL_CHARACTERS = CHARACTERS_AND_VEHICLES_BY_NAME
    RECEIVABLE_CHARACTERS_BY_AP_ID: ClassVar[dict[int, GenericCharacterData]] = {
        extra.code: extra for extra in CHARACTERS_AND_VEHICLES_BY_NAME.values() if extra.code != -1
    }
    MIN_CHARACTER_NUMBER: ClassVar[int] = min(char.character_number for char in RECEIVABLE_CHARACTERS_BY_AP_ID.values())
    MAX_CHARACTER_NUMBER: ClassVar[int] = max(char.character_number for char in RECEIVABLE_CHARACTERS_BY_AP_ID.values())
    RANDOMIZED_BYTES_RANGE: ClassVar[range] = range(MIN_CHARACTER_NUMBER, MAX_CHARACTER_NUMBER + 1)
    NUM_RANDOMIZED_BYTES: ClassVar[int] = len(RANDOMIZED_BYTES_RANGE)

    # Buying a character from the shop unlocks a character even though it shouldn't because it is supposed to be a
    # randomized location check, so unlockable characters need to be reset occasionally, though probably only while in
    # the Cantina.
    # Completing a story mode level will also probably unlock a character.
    unlocked_characters: set[int]

    def __init__(self):
        self.unlocked_characters = set()
        self.locked_characters = {char.character_number for char in self.RECEIVABLE_CHARACTERS_BY_AP_ID.values()}

    def give_character(self, ctx: "LegoStarWarsTheCompleteSagaContext", ap_item_id: int) -> bool:
        char = self.RECEIVABLE_CHARACTERS_BY_AP_ID[ap_item_id]
        character_number = char.character_number
        if character_number in self.unlocked_characters:
            # Nothing to do.
            return True
        # 0 = locked
        # 1 = ???
        # 2 = ???
        # 3 = unlocked
        ctx.write_byte(CHARACTERS_UNLOCKED_START + character_number, 3)
        self.unlocked_characters.add(character_number)
        return True

    def write_all_characters(self, ctx: "LegoStarWarsTheCompleteSagaContext") -> None:
        """Call repeatedly while in the Cantina room with the shop to undo shop character purchases."""
        # todo: See if there is a performance hit to doing all 137 (or more once we add more vehicles) writes
        #  separately. It would technically be safer.
        chars = ctx.read_bytes(CHARACTERS_UNLOCKED_START + self.MIN_CHARACTER_NUMBER, self.NUM_RANDOMIZED_BYTES)
        chars_array = bytearray(chars)

        for char in self.RECEIVABLE_CHARACTERS_BY_AP_ID.values():
            character_number = char.character_number
            if character_number in self.unlocked_characters:
                chars_array[character_number + self.MIN_CHARACTER_NUMBER] = 3
            else:
                chars_array[character_number + self.MIN_CHARACTER_NUMBER] = 0

        ctx.write_bytes(CHARACTERS_UNLOCKED_START + self.MIN_CHARACTER_NUMBER, bytes(chars_array), self.NUM_RANDOMIZED_BYTES)



class AcquiredExtras:
    RECEIVABLE_EXTRAS_BY_AP_ID: ClassVar[dict[int, ExtraData]] = {
        extra.code: extra for extra in EXTRAS_BY_NAME.values() if extra.code != -1
    }
    # All bytes in the UnlockedExtras
    MIN_RANDOMIZED_BYTE: ClassVar[int] = min(extra.shop_slot_byte for extra in RECEIVABLE_EXTRAS_BY_AP_ID.values())
    MAX_RANDOMIZED_BYTE: ClassVar[int] = max(extra.shop_slot_byte for extra in RECEIVABLE_EXTRAS_BY_AP_ID.values())
    RANDOMIZED_BYTES_RANGE: ClassVar[range] = range(MIN_RANDOMIZED_BYTE, MAX_RANDOMIZED_BYTE + 1)
    NUM_RANDOMIZED_BYTES: ClassVar[int] = len(RANDOMIZED_BYTES_RANGE)

    # Initialize to all bits randomized, then update by removing non-randomized bits.
    NON_RANDOMIZED_BITS_IN_RANDOMIZED_BYTES: ClassVar[dict[int, set[int]]] = {
        i: {1, 2, 4, 8, 16, 32, 64, 128} for i in RANDOMIZED_BYTES_RANGE
    }
    # Remove bits that are randomized.
    extra_ = None
    for extra_ in RECEIVABLE_EXTRAS_BY_AP_ID.values():
        NON_RANDOMIZED_BITS_IN_RANDOMIZED_BYTES[extra_.shop_slot_byte].remove(extra_.shop_slot_bit)
    del extra_
    # Remove bytes with all bits randomized.
    NON_RANDOMIZED_BITS_IN_RANDOMIZED_BYTES = {i: bits for i, bits in NON_RANDOMIZED_BITS_IN_RANDOMIZED_BYTES.items()
                                               if bits}

    RANDOMIZED_EXTRAS_IN_PARTIALLY_RANDOMIZED_BYTES: ClassVar[tuple[ExtraData, ...]] = tuple([
        extra for extra in RECEIVABLE_EXTRAS_BY_AP_ID.values()
        if extra.shop_slot_byte in NON_RANDOMIZED_BITS_IN_RANDOMIZED_BYTES
    ])

    START_ADDRESS: ClassVar[int] = EXTRAS_UNLOCKED_START + MIN_RANDOMIZED_BYTE

    unlocked_extras: bytearray

    def __init__(self):
        # Min and max are inclusive, so `+ 1` is needed.
        self.unlocked_extras = bytearray(self.NUM_RANDOMIZED_BYTES)

    def give_extra_from_obj(self,
                            ctx: "LegoStarWarsTheCompleteSagaContext",
                            extra: ExtraData,
                            write_to_game: bool) -> bool:
        if write_to_game:
            # Because the extra is stored in a single bit, we need to read the current byte, set the bit and then write the
            # byte again.
            current_byte = ctx.read_byte(EXTRAS_SHOP_START + extra.shop_slot_byte)
            current_byte |= extra.shop_slot_bit
            ctx.write_byte(EXTRAS_SHOP_START + extra.shop_slot_byte, current_byte)

        self.unlocked_extras[extra.shop_slot_byte] |= extra.shop_slot_bit
        return True


    def give_extra(self, ctx: "LegoStarWarsTheCompleteSagaContext", ap_item_id: int, write_to_game: bool) -> bool:
        if ap_item_id not in self.RECEIVABLE_EXTRAS_BY_AP_ID:
            logger.warning("Tried to receive unknown extra with item ID %i", ap_item_id)
            return False

        return self.give_extra_from_obj(ctx, self.RECEIVABLE_EXTRAS_BY_AP_ID[ap_item_id], write_to_game)

    def write_all_extras(self, ctx: "LegoStarWarsTheCompleteSagaContext"):
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
            # If the bit is set:
            if self.unlocked_extras[extra.shop_slot_byte] & extra.shop_slot_bit:
                # Set the bit in `unlocked_extras_copy`.
                unlocked_extras_copy[extra.shop_slot_byte] |= extra.shop_slot_bit
            else:
                # Clear the bit in `unlocked_extras_copy`.
                unlocked_extras_copy[extra.shop_slot_byte] &= ~extra.shop_slot_bit

        # Write the updated extras array.
        ctx.write_bytes(self.START_ADDRESS, bytes(unlocked_extras_copy), self.NUM_RANDOMIZED_BYTES)


class PurchasedCharacters:
    pass


class PurchasedExtras:
    ALL_PURCHASABLE_EXTRAS = EXTRAS_BY_NAME.copy()
    del ALL_PURCHASABLE_EXTRAS["Adaptive Difficulty"]

    data: bytearray

    # def __init__(self):
    #     start_byte_index = 1
    #     assert self.ALL_PURCHASABLE_EXTRAS["Super Gonk"].shop_slot_byte == start_byte_index
    #     end_byte_index_inclusive =


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


    def __init__(self, server_address: typing.Optional[str] = None, password: typing.Optional[str] = None) -> None:
        super().__init__(server_address, password)

        self.acquired_extras = AcquiredExtras()
        self.acquired_characters = AcquiredCharacters()
        self.acquired_generic = AcquiredGeneric()

    async def disconnect(self, allow_autoreconnect: bool = False):
        # todo: What are the connect and disconnect methods to override?
        # todo: When receiving item index 0, we also want to destroy and re-create the 'acquired' attributes.
        self.acquired_extras = AcquiredExtras()
        self.acquired_characters = AcquiredCharacters()
        self.acquired_generic = AcquiredGeneric()
        return await super().disconnect(allow_autoreconnect)

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
        self.game_process = None

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

    def read_byte(self, address: int) -> int:
        return self._game_process.read_uchar(self.memory_offset + address)
        #return self._game_process.read_bytes(self.memory_offset + address, 1)[0]

    def write_uint(self, address: int, value: int) -> None:
        self._game_process.write_uint(self.memory_offset + address, value)

    def write_byte(self, address: int, value: int) -> None:
        self._game_process.write_uchar(self.memory_offset + address, value)

    def write_bytes(self, address: int, value: bytes, length: int) -> None:
        self._game_process.write_bytes(self.memory_offset + address, value, length)

    def get_current_level_id(self) -> int:
        return self.read_ushort(CURRENT_LEVEL_ID) != 0

    def is_in_game(self) -> bool:
        # There are more than 255 levels, but far fewer than 65536, so assume 2 bytes.
        return (process := self.game_process) is not None and process.read_ushort(self.memory_offset + CURRENT_LEVEL_ID) != 0

    def set_expected_idx(self, idx: int) -> None:
        # Storing this in Custom Character 1's name as a string for now.
        to_write = str(idx).encode()
        if len(to_write) > 15:
            raise RuntimeError(f"Error: cannot set expected idx to {to_write}, integer is too large. Max of 15 digits.")
        if len(to_write) < 15:
            # Null terminate.
            to_write += b"\x00" * (15 - len(to_write))
        self.write_bytes(CUSTOM_CHARACTER_1_NAME, to_write, len(to_write))

    def get_expected_idx(self) -> int:
        # Storing this in Custom Character 1's name as a string for now.
        as_bytestring = self.read_bytes(CUSTOM_CHARACTER_1_NAME, 15)
        return int(as_bytestring.partition(b"\x00")[0])

    def give_item(self, code: int) -> bool:
        if not self.is_in_game():
            return False

        if code in self.acquired_extras.RECEIVABLE_EXTRAS_BY_AP_ID:
            return self.acquired_extras.give_extra(self, code)
        elif code in self.acquired_characters.RECEIVABLE_CHARACTERS_BY_AP_ID:
            return self.acquired_characters.give_character(self, code)
        elif code in self.acquired_generic.RECEIVABLE_GENERIC_BY_AP_ID:
            return self.acquired_generic.give_generic(self, code)
        else:
            logger.warning(f"Received item with code %s not recognized.", code)
            return True


async def give_items(ctx: LegoStarWarsTheCompleteSagaContext):
    if ctx.is_in_game():
        expected_idx = ctx.get_expected_idx()

        # Check if there are new items.
        received_items = ctx.items_received
        if len(received_items) <= expected_idx:
            # There are no new items.
            return

        # Loop through items to give.
        # Give the player all items at an index greater than or equal to the expected index.
        for idx, item in enumerate(received_items[expected_idx:], start=expected_idx):
            while not ctx.give_item(item.item):
                await asyncio.sleep(0.01)

            # Increment the expected index.
            ctx.set_expected_idx(idx + 1)



async def game_watcher(ctx: LegoStarWarsTheCompleteSagaContext):
    logger.info("Starting connection to game.")
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
                    sleep_time = 0.1
                    continue
                if ctx.slot is not None:
                    # todo: Store the multiworld seed name somewhere in the save file and check it before giving any
                    #  items or checking any locations. OR can we do this check when connecting and then immediately
                    #  disconnect if the seed name does not match?
                    # todo: Can we store the slot name somewhere too and check that also?
                    await give_items(ctx)
                    #await check_locations(ctx)
                    #await _read_extras_purchase_locations(ctx.game_process)
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
                sleep_time = 0.1
            else:
                if not ctx.open_game_process():
                    logger.info("Connection to game failed, attempting again in 5 seconds...")
                    await ctx.disconnect()
                    sleep_time = 5
                else:
                    # No wait, start processing items/locations/etc. immediately if the client is connected to the
                    # server.
                    pass
        except PymemError | WinAPIError:
            ctx.unhook_game_process()
            logger.info("Game connection failed, attempting again in 5 seconds...")
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
    ctx.server_address = None

    await game_watcher_task

    await ctx.shutdown()


def launch():
    colorama.just_fix_windows_console()
    asyncio.run(main())
    colorama.deinit()