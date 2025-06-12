import logging
from typing import Mapping, Sequence

from ..type_aliases import TCSContext
from ...items import GENERIC_BY_NAME, ExtraData, EXTRAS_BY_NAME, CHARACTERS_AND_VEHICLES_BY_NAME, GenericItemData

RECEIVABLE_GENERIC_BY_AP_ID: Mapping[int, GenericItemData] = {
    item.code: item for item in GENERIC_BY_NAME.values() if item.code != -1
}
EPISODE_UNLOCKS: Mapping[int, int] = {
    GENERIC_BY_NAME[f"Episode {i} Unlock"].code: i for i in range(2, 6+1)
}
PROGRESSIVE_BONUS_CODE: int = GENERIC_BY_NAME["Progressive Bonus Level"].code
PROGRESSIVE_SCORE_MULTIPLIER: int = GENERIC_BY_NAME["Progressive Score Multiplier"].code
SCORE_MULIPLIER_EXTRAS: Sequence[ExtraData] = (
    EXTRAS_BY_NAME["Score x2"],
    EXTRAS_BY_NAME["Score x4"],
    EXTRAS_BY_NAME["Score x6"],
    EXTRAS_BY_NAME["Score x8"],
    EXTRAS_BY_NAME["Score x10"],
)
MINIKIT_ITEMS: Mapping[int, int] = {
    GENERIC_BY_NAME["5 Minikits"].code: 5,
}
# Receiving these items does nothing currently.
NOOP_ITEMS: tuple[int, ...] = tuple([
    GENERIC_BY_NAME["Restart Level Trap"].code
])
BONUS_CHARACTER_REQUIREMENTS: Mapping[int, AbstractSet[int]] = {
    1: {CHARACTERS_AND_VEHICLES_BY_NAME["Anakin's Podracer"].character_index},
    2: {CHARACTERS_AND_VEHICLES_BY_NAME["Naboo Starfighter"].character_index},
    3: {CHARACTERS_AND_VEHICLES_BY_NAME["Republic Gunship"].character_index},
    4: {CHARACTERS_AND_VEHICLES_BY_NAME[name].character_index
        for name in ("Darth Vader", "Stormtrooper", "C-3PO")},
}
STUDS: Mapping[int, int] = {
    GENERIC_BY_NAME["Purple Stud"].code: 10000
}


# Note, this is not the in-level stud count. We don't add to that, because it is not saved.
STUD_COUNT_ADDRESS = 0x86E4DC
MAX_STUD_COUNT = 4_000_000_000

BONUSES_BASE_ADDRESS = 0x86E4E4


logger = logging.getLogger("Client")


class AcquiredGeneric:
    unlocked_episodes: set[int]
    progressive_bonus_count: int
    progressive_score_count: int
    minikit_count: int

    def __init__(self):
        self.unlocked_episodes = set()
        self.progressive_bonus_count = 0
        self.progressive_score_count = 0
        self.minikit_count = 0

    def receive_generic(self, ctx: TCSContext, ap_item_id: int):
        # Studs are handled separately as part of the game watcher.
        if ap_item_id in STUDS:
            pass
        # Minikits
        elif ap_item_id in MINIKIT_ITEMS:
            self.minikit_count += 1
        # Progressive Bonus Unlock
        elif ap_item_id == PROGRESSIVE_BONUS_CODE:
            # if write_to_game:
            #     # fixme: Even if a door is built, it won't open unless the player has enough gold bricks.
            #     built_gold_brick_doors = ctx.read_uchar(BONUSES_BASE_ADDRESS)
            #     built_gold_brick_doors |= (1 << self.progressive_bonus_count)
            #     ctx.write_byte(BONUSES_BASE_ADDRESS, built_gold_brick_doors)
            self.progressive_bonus_count += 1
        # Progressive Score Multiplier
        elif ap_item_id == PROGRESSIVE_SCORE_MULTIPLIER:
            if self.progressive_score_count < len(SCORE_MULIPLIER_EXTRAS):
                ctx.acquired_extras.unlock_extra(SCORE_MULIPLIER_EXTRAS[self.progressive_score_count])
            self.progressive_score_count += 1
        # Episode Unlocks
        elif ap_item_id in EPISODE_UNLOCKS:
            self.unlocked_episodes.add(EPISODE_UNLOCKS[ap_item_id])
            ctx.unlocked_level_manager.on_character_or_episode_unlocked(ap_item_id)
        else:
            logger.error("Unhandled ap_item_id %s for generic item", ap_item_id)

    def give_studs(self, ctx: TCSContext, ap_item_id: int):
        """
        Grant Studs to the player. Unlike other items, Studs are a consumable resource, so cannot simply be set to the
        number of received studs and instead must use the last/next item index from AP to determine when a Studs item is
        newly received by the current save file.
        """
        studs_to_add = STUDS.get(ap_item_id)
        if studs_to_add is None:
            logger.warning("Tried to receive unknown Studs item with item ID %i", ap_item_id)
            return
        current_stud_count = ctx.read_uint(STUD_COUNT_ADDRESS)
        new_stud_count = min(current_stud_count + studs_to_add, MAX_STUD_COUNT)
        ctx.write_uint(STUD_COUNT_ADDRESS, new_stud_count)

    async def update_game_state(self, ctx: TCSContext):
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
                character_requirements = BONUS_CHARACTER_REQUIREMENTS.get(i)
                if not character_requirements or character_requirements <= ctx.acquired_characters.unlocked_characters:
                    unlocked_bonuses_byte |= (1 << (i - 1))
        ctx.write_byte(BONUSES_BASE_ADDRESS, unlocked_bonuses_byte)
