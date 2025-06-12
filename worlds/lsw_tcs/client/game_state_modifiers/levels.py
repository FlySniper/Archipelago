import logging

from ..type_aliases import TCSContext
from ...items import ITEM_DATA_BY_NAME, ITEM_DATA_BY_ID
from ...levels import EpisodeGameLevelArea, GAME_LEVEL_AREAS, SHORT_NAME_TO_LEVEL_AREA


debug_logger = logging.getLogger("TCS Debug")


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
            debug_logger.info("Removed %s from %s requirements", ITEM_DATA_BY_ID[character_ap_id].name, dependent_area_short_name)
            if not remaining_requirements:
                self.pending_unlocks.append(SHORT_NAME_TO_LEVEL_AREA[dependent_area_short_name])
                del self.remaining_level_item_requirements[dependent_area_short_name]

        del self.character_to_dependent_game_levels[character_ap_id]

    def first_time_setup(self, ctx: TCSContext):
        self.first_time_setup_complete = True
        # Lock all levels to start with.
        locked = b"\x00"
        # FIXME: Story mode being completed results in the characters being unlocked in the shop.
        #  Either going into the shop needs to clear Story Mode completion, or Story Mode completion needs to be added
        #  when unlocking a level, ideally only temporarily until Free Play has been completed.
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
    def unlock_level(ctx: TCSContext, level_area: EpisodeGameLevelArea):
        # The first byte indicates whether the level is unlocked.
        ctx.write_byte(level_area.address, 1)
        debug_logger.info("Unlocked level %s (%s)", level_area.name, level_area.short_name)

    async def update_game_state(self, ctx: TCSContext):
        if not self.first_time_setup_complete:
            self.first_time_setup(ctx)
        # TODO: It might be necessary to constantly re-lock locked levels because playing a story level might cause the
        #  next level to get unlocked. TODO: Try it out.
        # TODO: The "All Episode" character purchases in the shop (4-LOM/Ghosts/etc.) might need all levels to be
        #  temporarily set as completed when trying to buy the characters while the client has received all episode
        #  unlocks, so that the characters can actually be purchased without completing every level.
        if self.pending_unlocks:
            for level_area in self.pending_unlocks:
                self.unlock_level(ctx, level_area)
            self.pending_unlocks.clear()
