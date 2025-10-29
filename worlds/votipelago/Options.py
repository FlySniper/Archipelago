from dataclasses import dataclass
from Options import Choice, Range, PerGameCommonOptions, StartInventoryPool, OptionGroup, Toggle, DeathLink


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


class ChannelPointsPerExtraVote(Range):
    """How many channel points per extra vote."""
    display_name = "Channel Points Per Extra Vote"
    range_start = 0
    range_end = 1000000
    default = 100


class Goal(Choice):
    """Select the goal for completing this world:
    - Short Macguffin Hunt: Find the letters V.O.T.E.
    - Long Macguffin Hunt: Find the letters V.O.T.I.P.E.L.A.G.O (Duplicate letters must be found twice)."""
    display_name = "Goal"
    option_short_macguffin_hunt= 0
    option_long_macguffin_hunt= 1

class StartingDeathLinkPool(Range):
    """How many death links are in the voting options at the start.
    A death link option is removed from the pool when it is chosen."""
    display_name = "Starting Death Link Pool"
    range_start = 0
    range_end = 100
    default = 5

class DeathLinkTimeStretch(Range):
    """How much time in seconds receiving a death link adds until the next poll."""
    display_name = "Death Link Time Stretch"
    range_start = 0
    range_end = 86400
    default = 30

class DeathLinkAddToPool(Range):
    """How many death links are added to the pool when a death link is received.
    WARNING:
        If there are multiple worlds with this option enabled, death links could propagate endlessly and never diminish.
    """
    display_name = "Death Links to Add to Pool"
    range_start = 0
    range_end = 5
    default = 0

votipelago_option_groups = [
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
            ChannelPointsPerExtraVote,
            NumberOfChoices,
        ]),
        OptionGroup("Deathlink Options", [
            DeathLink,
            StartingDeathLinkPool,
            DeathLinkTimeStretch,
            DeathLinkAddToPool,
        ]),

]

@dataclass
class VotipelagoOptions(PerGameCommonOptions):
    poll_keys: PollKeys
    locations_per_key: LocationsPerKey
    time_between_polls: TimeBetweenPolls
    minor_time_skip: MinorTimeSkip
    major_time_skip: MajorTimeSkip
    minor_major_ratio: MinorMajorRatio
    poll_length: PollLength
    channel_point_voting: ChannelPointVoting
    channel_points_per_extra_vote: ChannelPointsPerExtraVote
    number_of_choices: NumberOfChoices
    goal: Goal
    starting_deathlink_pool: StartingDeathLinkPool
    death_link_time_stretch: DeathLinkTimeStretch
    death_link_add_to_pool: DeathLinkAddToPool
    death_link: DeathLink
    start_inventory_from_pool: StartInventoryPool
