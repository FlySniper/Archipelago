from ..type_aliases import MemoryAddress, ApLocationId, TCSContext
from ...levels import BONUS_GAME_LEVEL_AREAS
from ...locations import LOCATION_NAME_TO_ID


class BonusLevelCompletionChecker:
    # Anakin's Flight and A New Hope support Free Play, but the rest are Story mode only.
    remaining_story_completion_checks: dict[MemoryAddress, ApLocationId]

    def __init__(self):
        self.remaining_story_completion_checks = {
            bonus.address + bonus.completion_offset: LOCATION_NAME_TO_ID[bonus.name] for bonus in BONUS_GAME_LEVEL_AREAS
        }

    async def check_completion(self, ctx: TCSContext, new_location_checks: list[int]):
        updated_remaining_story_completion_checks = {}
        for address, ap_id in self.remaining_story_completion_checks.items():
            if ap_id in ctx.checked_locations:
                continue
            if ctx.read_uchar(address):
                # The bonus has been completed, or viewed in the case of the Indiana Jones trailer.
                new_location_checks.append(ap_id)
            updated_remaining_story_completion_checks[address] = ap_id
        self.remaining_story_completion_checks = updated_remaining_story_completion_checks
