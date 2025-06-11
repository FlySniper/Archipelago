from ...levels import GAME_LEVEL_AREAS
from ...locations import LOCATION_NAME_TO_ID, LEVEL_COMMON_LOCATIONS
from ..type_aliases import ApLocationId, LevelId, TCSContext


# The most stable byte I could find to determine the difference between the 'status' screen when using "Save and Exit
# Cantina" and when completing a level, in Free Play. What this byte controls is unknown.
# Seems to always be 0x8 when using "Save and Quit", and 0x0 when completing a level. Can be 0x8 when playing through a
# normal game level with control of a character.
STATUS_LEVEL_TYPE_ADDRESS = 0x87A6D9
# STATUS_LEVEL_TYPE_SAVE_AND_EXIT = 0x8
STATUS_LEVEL_TYPE_LEVEL_COMPLETION = 0x0


CURRENT_GAME_MODE_ADDRESS = 0x87951C
"""Byte that stores the current game mode."""

# CURRENT_GAME_MODE_STORY = 0
CURRENT_GAME_MODE_FREE_PLAY = 1
# Per-level Challenge mode as well as per-episode character bonus and Superstory.
# TODO: What do vehicle bonuses and separate bonus levels count as? Separate bonus levels can have both Story and Free
#  Play modes (Anakin's Flight), but can also be only Free Play (New Town).
# CURRENT_GAME_MODE_CHALLENGE_BONUS = 2


def is_in_free_play(ctx: TCSContext) -> bool:
    """
    Return whether the player is currently in Free Play.

    The result is undefined if the player is not currently in a game level Area.
    """
    return ctx.read_uchar(CURRENT_GAME_MODE_ADDRESS) == CURRENT_GAME_MODE_FREE_PLAY


def is_status_level_completion(ctx: TCSContext) -> bool:
    """
    Return whether the current status Level is being shown as part of level completion.

    The status Level for each game level Area is used when tallying up Studs/Minikits etc. when returning to the
    Cantina, both for level completion and for 'Save and Exit'.

    The result is undefined if the player is not currently in a status Level.
    """
    return ctx.read_uchar(STATUS_LEVEL_TYPE_ADDRESS) == STATUS_LEVEL_TYPE_LEVEL_COMPLETION


# TODO: How quickly can a player reasonably skip through the level completion screen? Do we need to check for level
#  completion with a higher frequency than how often the game watcher is checking?
class FreePlayLevelCompletionChecker:
    """
    Check if the player has completed a free play level by looking for the ending screen that tallies up new
    studs/minikits.

    There appears to be no persistent storage in the game's memory or save data for whether a level has been completed
    in Free Play, so the client must poll the game state and track completions itself in the case of disconnecting from
    the server.
    """
    STATUS_LEVEL_ID_TO_AP_ID: dict[LevelId, ApLocationId] = {
        area.status_level_id: LOCATION_NAME_TO_ID[LEVEL_COMMON_LOCATIONS[area.short_name]["Completion"]]
        for area in GAME_LEVEL_AREAS
    }

    sent_locations: set[ApLocationId]

    def __init__(self):
        self.sent_locations = set()

    async def check_completion(self, ctx: TCSContext, new_location_checks: list[ApLocationId]):
        # Level ID should be checked first because STATUS_LEVEL_TYPE_ADDRESS can be STATUS_LEVEL_TYPE_LEVEL_COMPLETION
        # during normal gameplay, so it would be possible for STATUS_LEVEL_TYPE_ADDRESS to match and then the player
        # does 'Save and Exit', changing the Level ID to
        completion_location_id = self.STATUS_LEVEL_ID_TO_AP_ID.get(ctx.get_current_level_id())
        if (completion_location_id is not None
                and completion_location_id in ctx.missing_locations
                and is_in_free_play(ctx)
                and is_status_level_completion(ctx)):
            self.sent_locations.add(completion_location_id)

        # Not required because only the intersection of ctx.missing_locations will be sent to the server, but removing
        # checked locations (server state) here helps with debugging by reducing self.sent_locations to only new checks.
        self.sent_locations.difference_update(ctx.checked_locations)

        # Locations to send to the server will be filtered to only those in ctx.missing_locations, so include everything
        # up to this point in-case one was missed in a disconnect.
        new_location_checks.extend(self.sent_locations)
