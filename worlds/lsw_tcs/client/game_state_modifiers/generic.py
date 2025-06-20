import logging
from typing import Mapping, Sequence, AbstractSet

from ..type_aliases import TCSContext
from ...items import GENERIC_BY_NAME, ExtraData, EXTRAS_BY_NAME, CHARACTERS_AND_VEHICLES_BY_NAME, GenericItemData
from . import ItemReceiver

RECEIVABLE_GENERIC_BY_AP_ID: Mapping[int, GenericItemData] = {
    item.code: item for item in GENERIC_BY_NAME.values() if item.code != -1 and not item.name.endswith("Stud")
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

BONUSES_BASE_ADDRESS = 0x86E4E4

# Goal progress is written into Custom Character 2's name until a better place for this information is found.
CUSTOM_CHARACTER2_NAME_OFFSET = 0x86E524 + 0x14  # string[15]


logger = logging.getLogger("Client")


class AcquiredGeneric(ItemReceiver):
    receivable_ap_ids = RECEIVABLE_GENERIC_BY_AP_ID

    unlocked_episodes: set[int]
    progressive_bonus_count: int
    progressive_score_count: int
    minikit_count: int
    goal_minikit_count: int = 54  # todo: to be controlled by an option in the future

    def __init__(self):
        # TODO: Allow Episode 1 to be randomized.
        # TODO: Allow all Episodes to be unlocked from the start.
        self.unlocked_episodes = {1}
        self.progressive_bonus_count = 0
        self.progressive_score_count = 0
        self.minikit_count = 0

    def receive_generic(self, ctx: TCSContext, ap_item_id: int):
        # Minikits
        if ap_item_id in MINIKIT_ITEMS:
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

    def _update_goal_display(self, ctx: TCSContext):
        goal_count = str(self.goal_minikit_count * 5)
        digits_to_display = len(goal_count)

        # noinspection PyStringFormat
        current_minikit_count = f"{{:0{digits_to_display}d}}".format(self.minikit_count * 5)

        # There are few available characters. The player is limited to "0-9A-Z -", but the names are capable of
        # displaying more punctuation and lowercase letters. A few characters with ligatures are supported as part of
        # localisation for other languages.
        goal_display_text = f"{current_minikit_count}/{goal_count} GOAL".encode("ascii")
        # The maximum size is 16 bytes, but the string must be null-terminated, so there are 15 usable bytes.
        goal_display_text = goal_display_text[:15] + b"\x00"
        ctx.write_bytes(CUSTOM_CHARACTER2_NAME_OFFSET, goal_display_text, len(goal_display_text))

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
