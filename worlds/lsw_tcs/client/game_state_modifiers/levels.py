import logging
from typing import AbstractSet

from ..type_aliases import TCSContext
from ...items import ITEM_DATA_BY_NAME, ITEM_DATA_BY_ID
from ...levels import EpisodeGameLevelArea, GAME_LEVEL_AREAS, SHORT_NAME_TO_LEVEL_AREA


debug_logger = logging.getLogger("TCS Debug")

ALL_GAME_LEVEL_AREAS_SET = frozenset(GAME_LEVEL_AREAS)


class UnlockedLevelManager:
    character_to_dependent_game_levels: dict[int, list[str]]
    remaining_level_item_requirements: dict[str, set[int]]

    unlocked_levels_per_episode: dict[int, set[EpisodeGameLevelArea]]

    def __init__(self) -> None:
        self.unlocked_levels_per_episode = {}
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
                self.unlocked_levels_per_episode.setdefault(level_area.episode, set()).add(level_area)

        self.character_to_dependent_game_levels = item_id_to_level_area_short_name
        self.remaining_level_item_requirements = remaining_level_item_requirements

    def on_character_or_episode_unlocked(self, character_ap_id: int):
        dependent_levels = self.character_to_dependent_game_levels.get(character_ap_id)
        if dependent_levels is None:
            return

        for dependent_area_short_name in dependent_levels:
            remaining_requirements = self.remaining_level_item_requirements[dependent_area_short_name]
            assert remaining_requirements
            assert character_ap_id in remaining_requirements, (f"{ITEM_DATA_BY_ID[character_ap_id].name} not found in"
                                                               f" {sorted([ITEM_DATA_BY_ID[code] for code in remaining_requirements], key=lambda data: data.name)}")
            remaining_requirements.remove(character_ap_id)
            debug_logger.info("Removed %s from %s requirements", ITEM_DATA_BY_ID[character_ap_id].name, dependent_area_short_name)
            if not remaining_requirements:
                self.unlock_level(SHORT_NAME_TO_LEVEL_AREA[dependent_area_short_name])
                del self.remaining_level_item_requirements[dependent_area_short_name]

        del self.character_to_dependent_game_levels[character_ap_id]

    def unlock_level(self, level_area: EpisodeGameLevelArea):
        self.unlocked_levels_per_episode.setdefault(level_area.episode, set()).add(level_area)
        debug_logger.info("Unlocked level %s (%s)", level_area.name, level_area.short_name)

    async def update_game_state(self, ctx: TCSContext):
        temporary_story_completion: AbstractSet[EpisodeGameLevelArea]
        if (len(ctx.acquired_generic.unlocked_episodes) == 6
                and ctx.acquired_characters.is_all_episodes_character_selected_in_shop(ctx)):
            # In vanilla, the 'all episodes' characters unlock for purchase in the shop when the player has completed
            # every level in Story mode. In the AP randomizer, they need to be unlocked once all Episode Unlocks have
            # been acquired instead because completing all levels in Story mode would basically never happen in a
            # playthrough of the randomized world.
            # Unfortunately, levels being completed in Story mode is also what unlocks most other Character purchases in
            # the shop.
            # To work around this, all Story mode completions are temporarily set when all Episode Unlocks have been
            # acquired and the player has selected one of the 'all episodes' characters for purchase in the shop.
            temporary_story_completion = ALL_GAME_LEVEL_AREAS_SET
        else:
            cantina_room = ctx.get_current_cantina_room()
            if cantina_room.value in self.unlocked_levels_per_episode:
                # If the player is in an Episode's room, Story mode needs to be completed for all the player's unlocked
                # levels so that the player can skip playing through Story mode and go straight to Free Play.
                temporary_story_completion = self.unlocked_levels_per_episode[cantina_room.value]
            else:
                # Do not temporarily complete any Story modes.
                temporary_story_completion = set()

        completed_free_play = ctx.free_play_completion_checker.completed_free_play

        # 36 writes on each game state update is undesirable, but necessary to easily allow for temporarily completing
        # Story modes.
        for area in GAME_LEVEL_AREAS:
            if area in completed_free_play:
                # Set the level as unlocked and Story mode completed because Free Play has been completed.
                # The second bit in the third byte is custom to the AP client and signifies that Free Play has been
                # completed.
                ctx.write_bytes(area.address, b"\x03\x01", 2)
            elif area in temporary_story_completion:
                # Set the level as unlocked and Story mode completed because Story mode for this level needs to be
                # temporarily set as completed for some purpose.
                ctx.write_bytes(area.address, b"\x01\x01", 2)
            else:
                if area in self.unlocked_levels_per_episode[area.episode]:
                    # Set the level as unlocked, but with Story mode incomplete because Free Play has not been
                    # completed. This prevents characters being for sale in the shop without completing Free Play for
                    # the level that unlocks those shop slots.
                    ctx.write_bytes(area.address, b"\x01\x00", 2)
                else:
                    # Set the level as locked, with Story mode incomplete.
                    ctx.write_bytes(area.address, b"\x00\x00", 2)
