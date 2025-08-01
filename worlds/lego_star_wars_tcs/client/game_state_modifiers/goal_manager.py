import logging
from typing import Mapping, Any

from .text_replacer import TextId
from ..type_aliases import TCSContext
from ...items import MINIKITS_BY_COUNT
from . import GameStateUpdater

MINIKIT_ITEMS: Mapping[int, int] = {item.code: count for count, item in MINIKITS_BY_COUNT.items()}

# Goal progress is written into Custom Character 2's name until a better place for this information is found.
CUSTOM_CHARACTER2_NAME_OFFSET = 0x86E524 + 0x14  # string[15]


logger = logging.getLogger("Client")


class GoalManager(GameStateUpdater):
    receivable_ap_ids = MINIKIT_ITEMS

    goal_minikit_count: int = 999_999_999  # Set by an option and read from slot data.

    def init_from_slot_data(self, ctx: TCSContext, slot_data: dict[str, Any]) -> None:
        self.goal_minikit_count = slot_data["minikit_goal_amount"]
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

    async def update_game_state(self, ctx: TCSContext):
        self._update_minikit_goal_display(ctx)

    def is_goal_complete(self, ctx: TCSContext):
        return ctx.acquired_minikits.minikit_count >= self.goal_minikit_count
