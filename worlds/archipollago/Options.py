from dataclasses import dataclass
from Options import Choice, Range, PerGameCommonOptions, StartInventoryPool, OptionGroup, Toggle


class PollKeys(Range):
    """How many keys items are available."""
    display_name = "Poll Keys"
    range_start = 0
    range_end = 10
    default = 3


class LocationsPerKey(Range):
    """How many locations are unlocked per key found.
    If no keys are found, then this value will also be the starting amount of locations."""
    display_name = "Locations Per Key"
    range_start = 2
    range_end = 100
    default = 10


class TimeBetweenPolls(Range):
    """The time in seconds between polls."""
    display_name = "Time Between Polls"
    range_start = 30
    range_end = 86400
    default = 300


class PollLength(Range):
    """The time in seconds a poll is active for."""
    display_name = "Poll Length"
    range_start = 15
    range_end = 1800
    default = 60


class MinorTimeSkip(Range):
    """When found, shortens the time until the next poll by these many seconds."""
    display_name = "Minor Time Skip"
    range_start = 0
    range_end = 600
    default = 30


class MajorTimeSkip(Range):
    """When found, shortens the time until the next poll by these many seconds."""
    display_name = "Major Time Skip"
    range_start = 0
    range_end = 86400
    default = 300

class MinorMajorRatio(Range):
    """The percent of minor time skip items in the pool. The rest of the items are filled with major time skips.
    The higher the number the more minor times are in the pool.
    The lower the number the more major times are in the pool."""
    display_name = "Minor/Major Time Skip Ratio"
    range_start = 0
    range_end = 100
    default = 90


class NumberOfChoices(Range):
    """How many choices are available to the viewers."""
    display_name = "Number of Choices"
    range_start = 2
    range_end = 5
    default = 4


class ChannelPointVoting(Toggle):
    """Enable to turn on voting using channel points."""
    display_name = "Channel Point Voting"
    option_false = 0
    option_true = 1
    default = 0


class FreeChannelPointsPerVote(Range):
    """How many free channel points per vote."""
    display_name = "Free Channel Points Per Vote"
    range_start = 0
    range_end = 1000000
    default = 10


class Goal(Choice):
    """Select the goal for completing this world:
    - Short Macguffin Hunt: Find the letters P.O.L.L.A.G.O (Duplicate letters must be found twice).
    - Long Macguffin Hunt: Find the letters A.R.C.H.I.P.O.L.L.A.G.O (Duplicate letters must be found twice)."""
    display_name = "Goal"
    option_short_macguffin_hunt= 0
    option_long_macguffin_hunt= 1


archipollago_option_groups = [
        OptionGroup("Progression Options", [
            PollKeys,
            LocationsPerKey,
            TimeBetweenPolls,
            Goal,
        ]),
        OptionGroup("Filler Options", [
            MinorTimeSkip,
            MajorTimeSkip,
            MinorMajorRatio,
        ]),
        OptionGroup("Bot Options", [
            PollLength,
            ChannelPointVoting,
            FreeChannelPointsPerVote,
            NumberOfChoices,
        ]),

]

@dataclass
class ArchipollagoOptions(PerGameCommonOptions):
    poll_keys: PollKeys
    locations_per_key: LocationsPerKey
    time_between_polls: TimeBetweenPolls
    minor_time_skip: MinorTimeSkip
    major_time_skip: MajorTimeSkip
    minor_major_ratio: MinorMajorRatio
    poll_length: PollLength
    channel_point_voting: ChannelPointVoting
    free_channel_points_per_vote: FreeChannelPointsPerVote
    number_of_choices: NumberOfChoices
    goal: Goal
    start_inventory_from_pool: StartInventoryPool
