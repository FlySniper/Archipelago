import logging
from typing import Mapping, Any

from .text_replacer import TextId
from ..type_aliases import TCSContext, AreaId
from ...items import MINIKITS_BY_COUNT
from ...levels import SHORT_NAME_TO_CHAPTER_AREA
from ...options import OnlyUniqueBossesCountTowardsGoal
from . import GameStateUpdater

MINIKIT_ITEMS: Mapping[int, int] = {item.code: count for count, item in MINIKITS_BY_COUNT.items()}

# Goal progress is written into Custom Character 2's name until a better place for this information is found.
CUSTOM_CHARACTER2_NAME_OFFSET = 0x86E524 + 0x14  # string[15]


logger = logging.getLogger("Client")


class GoalManager(GameStateUpdater):
    receivable_ap_ids = MINIKIT_ITEMS

    goal_minikit_count: int = 999_999_999  # Set by an option and read from slot data.
    _goal_text_needs_update: bool = True

    goal_bosses_count: int = 999_999_999  # Set by an option and read from slot data.
    goal_bosses_must_be_unique: bool = False
    goal_bosses_anakin_as_vader: bool = False
    enabled_boss_chapters: set[AreaId]
    enabled_unique_bosses: dict[str, set[AreaId]]

    def __init__(self):
        self.enabled_boss_chapters = set()

    def init_from_slot_data(self, ctx: TCSContext, slot_data: dict[str, Any]) -> None:
        self.goal_minikit_count = slot_data["minikit_goal_amount"]

        if self.goal_minikit_count > 0:
            enabled_chapter_count = len(slot_data["enabled_chapters"])
            minimum_minikits_in_the_multiworld = 10 * enabled_chapter_count
            minikit_goal_info_text = (f"{self.goal_minikit_count} Minikits are needed to goal. There are a minimum of"
                                      f" {minimum_minikits_in_the_multiworld} Minikits to be found in the multiworld.")
        else:
            minikit_goal_info_text = "Minikit items are not needed to goal."

        server_apworld_version = tuple(slot_data["apworld_version"])
        if server_apworld_version < (1, 1, 0):
            # Minikit goal was the only goal at this point.
            self.goal_bosses_count = 0
            self.enabled_boss_chapters = set()
            self.enabled_unique_bosses = {}
            boss_goal_info_text = "Bosses do not need to be defeated to goal."
        else:
            self.goal_bosses_count = slot_data["defeat_bosses_goal_amount"]
            enabled_boss_chapters = set(slot_data["enabled_bosses"])
            self.enabled_boss_chapters = {SHORT_NAME_TO_CHAPTER_AREA[chapter].area_id
                                          for chapter in enabled_boss_chapters}
            only_unique_bosses_count = slot_data["only_unique_bosses_count"]
            self.goal_bosses_must_be_unique = (
                    only_unique_bosses_count != OnlyUniqueBossesCountTowardsGoal.option_disabled)
            self.goal_bosses_anakin_as_vader = (
                    only_unique_bosses_count
                    == OnlyUniqueBossesCountTowardsGoal.option_enabled_and_count_anakin_as_vader)
            if self.goal_bosses_must_be_unique:
                unique_bosses: dict[str, set[AreaId]] = {}
                unique_bosses_to_chapters: dict[str, list[str]] = {}
                for chapter in enabled_boss_chapters:
                    area = SHORT_NAME_TO_CHAPTER_AREA[chapter]
                    boss = area.boss
                    if self.goal_bosses_anakin_as_vader and boss == "Anakin Skywalker":
                        boss = "Darth Vader"
                    unique_bosses.setdefault(boss, set()).add(area.area_id)
                    unique_bosses_to_chapters.setdefault(boss, []).append(area.short_name)
                self.enabled_unique_bosses = unique_bosses
                sorted_bosses = sorted(unique_bosses_to_chapters.items(), key=lambda t: min(t[1]))
                boss_strings = []
                for boss, chapters in sorted_bosses:
                    chapters.sort()
                    chapters_string = ", ".join(chapters)
                    boss_string = f"{boss} ({chapters_string})"
                    boss_strings.append(boss_string)

                if len(boss_strings) == 1:
                    boss_goal_info_text = (f"{self.goal_bosses_count} unique boss need to be defeated. There is 1 boss"
                                           f" enabled: {boss_strings[0]}")
                else:
                    boss_chapters_text = ", ".join(boss_strings[:-1])
                    boss_chapters_text += f" and {boss_strings[-1]}"
                    boss_goal_info_text = (f"{self.goal_bosses_count} unique bosses need to be defeated. There are"
                                           f" {len(unique_bosses)} bosses enabled: {boss_chapters_text}")
            else:
                self.enabled_unique_bosses = {}
                sorted_boss_chapters = sorted(enabled_boss_chapters)
                if len(sorted_boss_chapters) == 1:
                    boss_chapters_text = sorted_boss_chapters[0]
                    boss_goal_info_text = (f"{self.goal_bosses_count} boss needs to be defeated. There is"
                                           f" {len(self.enabled_boss_chapters)} boss enabled, in {boss_chapters_text}")
                else:
                    boss_chapters_text = ", ".join(sorted_boss_chapters[:-1])
                    boss_chapters_text += f" and {sorted_boss_chapters[-1]}"
                    boss_goal_info_text = (f"{self.goal_bosses_count} bosses need to be defeated. There are"
                                           f" {len(self.enabled_boss_chapters)} bosses enabled, in"
                                           f" {boss_chapters_text}")
        ctx.text_replacer.write_custom_string(TextId.SHOP_UNLOCKED_HINT_2, minikit_goal_info_text)
        ctx.text_replacer.write_custom_string(TextId.SHOP_UNLOCKED_HINT_3, boss_goal_info_text)

        self.tag_for_update()
        assert isinstance(self.goal_minikit_count, int)

    def _update_minikit_goal_display(self, ctx: TCSContext):
        if self.goal_minikit_count > 0:
            goal_count = str(self.goal_minikit_count)
            # Display the current count with as many digits as the goal count.
            leading_digits_to_display = len(goal_count)

            # PyCharm does not like the fact that an f-string is being used to format a format string.
            # noinspection PyStringFormat
            current_minikit_count = f"{{:0{leading_digits_to_display}d}}".format(ctx.acquired_minikits.minikit_count)

            # There are few available characters. The player is limited to "0-9A-Z -", but the names are capable of
            # displaying more punctuation and lowercase letters. A few characters with ligatures are supported as part
            # of localisation for other languages.
            goal_display_text = f"{current_minikit_count}/{goal_count} GOAL".encode("ascii")
            # The maximum size is 16 bytes, but the string must be null-terminated, so there are 15 usable bytes.
            goal_display_text = goal_display_text[:15] + b"\x00"
            ctx.write_bytes(CUSTOM_CHARACTER2_NAME_OFFSET, goal_display_text, len(goal_display_text))

    def _get_bosses_defeated_count(self, ctx: TCSContext) -> int:
        completed_free_play = ctx.free_play_completion_checker.completed_free_play
        if self.goal_bosses_must_be_unique:
            count = 0
            for area_ids in self.enabled_unique_bosses.values():
                if not area_ids.isdisjoint(completed_free_play):
                    count += 1
            return count
        else:
            return len(self.enabled_boss_chapters.intersection(completed_free_play))

    def _update_paused_text_goal_display(self, ctx: TCSContext):
        """
        Replace the current "Paused" text, displayed in the UI under the Player that paused the game, with current goal
        progress.
        """
        vanilla_text = ctx.text_replacer.get_vanilla_string(TextId.PAUSED).decode(errors="replace")
        custom_message = f"{vanilla_text} - Goal: "
        goals: list[str] = []
        if self.goal_minikit_count > 0:
            minikit_goal = f"{ctx.acquired_minikits.minikit_count}/{self.goal_minikit_count} Minikits"
            goals.append(minikit_goal)
        if self.goal_bosses_count > 0:
            defeated_count = self._get_bosses_defeated_count(ctx)
            if self.goal_bosses_must_be_unique:
                bosses_goal = f"{defeated_count}/{self.goal_bosses_count} Unique Bosses Defeated"
            else:
                bosses_goal = f"{defeated_count}/{self.goal_bosses_count} Bosses Defeated"
            goals.append(bosses_goal)
        if not goals:
            goals.append("Error, no goal found")
        custom_message += ", ".join(goals)
        ctx.text_replacer.write_custom_string(TextId.PAUSED, custom_message)

    async def update_game_state(self, ctx: TCSContext):
        if self._goal_text_needs_update:
            self._goal_text_needs_update = False
            self._update_minikit_goal_display(ctx)
            self._update_paused_text_goal_display(ctx)

    def tag_for_update(self):
        self._goal_text_needs_update = True

    def _is_bosses_goal_complete(self, completed_area_ids: set[int]):
        required_count = self.goal_bosses_count
        if self.goal_bosses_must_be_unique:
            for area_ids in self.enabled_unique_bosses.values():
                for area_id in area_ids:
                    if area_id in completed_area_ids:
                        required_count -= 1
                        if required_count <= 0:
                            return True
                        break
        else:
            for area_id in self.enabled_boss_chapters:
                if area_id in completed_area_ids:
                    required_count -= 1
                    if required_count <= 0:
                        return True
        return False

    def is_goal_complete(self, ctx: TCSContext):
        # todo: Cache and re-stale after tag_for_update() is called instead of constantly re-checking.
        if self.goal_minikit_count > 0:
            if ctx.acquired_minikits.minikit_count < self.goal_minikit_count:
                return False
        if self.goal_bosses_count > 0:
            # todo: Once a boss has been defeated, reduce a remaining count and remove the boss from a set of remaining
            #  bosses. That way, the check becomes more efficient over time.
            if not self._is_bosses_goal_complete(ctx.free_play_completion_checker.completed_free_play):
                return False

        return True
