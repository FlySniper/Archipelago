import itertools
from dataclasses import dataclass
from typing import Mapping, AbstractSet

from Options import (
    PerGameCommonOptions,
    StartInventoryPool,
    Choice,
    Range,
    NamedRange,
    OptionSet,
    DefaultOnToggle,
    Toggle,
)

from .locations import LEVEL_SHORT_NAMES_SET


CHAPTER_OPTION_KEYS: Mapping[str, AbstractSet[str]] = {
    **{chapter: {chapter} for chapter in LEVEL_SHORT_NAMES_SET},
    "All": LEVEL_SHORT_NAMES_SET,
    "Prequel Trilogy": {chapter for chapter in LEVEL_SHORT_NAMES_SET if chapter[0] in "123"},
    "Original Trilogy": {chapter for chapter in LEVEL_SHORT_NAMES_SET if chapter[0] in "456"},
    **{f"Episode {s}": {chapter for chapter in LEVEL_SHORT_NAMES_SET if chapter[0] == s} for s in "123456"},
}


class ChapterOptionSet(OptionSet):
    valid_keys = set(CHAPTER_OPTION_KEYS.keys())

    @property
    def value_ungrouped(self) -> set[str]:
        """Ungroup all grouped chapters in .value into a single set of individual chapters."""
        return set().union(*(CHAPTER_OPTION_KEYS[key] for key in self.value))


class MinikitGoalAmount(NamedRange):
    """
    The number of Minikits required to goal.

    Each enabled episode chapter shuffles 10 Minikits into the item pool, which may be bundled to reduce the number
    Minikit items in the item pool.

    Setting this option to "use_percentage_option" will use the Minikit Goal Amount Percentage option's value to
    determine how many Minikit's are required to goal.
    """
    display_name = "Goal Minikits"
    range_start = 10
    range_end = 360
    special_range_names = {
        "use_percentage_option": -1,
    }
    default = -1


class MinikitGoalAmountPercentage(Range):
    """
    The percentage of Minikits in the item pool that are required to goal.

    10 Minikits are added to the item pool for each enabled episode chapter, which may be bundled to reduce the number
    of individual items.

    This does nothing unless the Minikit Goal Amount option is set to "use_percentage_option" instead of a number.

    The final number of Minikits required to goal is rounded to the nearest integer, but will always be at least 1.
    """
    range_start = 1
    range_end = 100
    default = 75


class MinikitBundleSize(Choice):
    """
    Minikit items in the item pool are bundled into items individually worth this number of Minikits.

    Low bundle sizes can cause generation times to increase and are more likely to result in generation failing with a
    FillError when generating Lego Star Wars: The Complete Saga on its own, or with other games that can struggle to
    place all items.

    Low bundle sizes also mean fewer filler studs in the item pool.
    """
    display_name = "Minikit Bundle Size"
    option_individual = 1
    alias_1 = 1
    option_2 = 2
    option_5 = 5
    option_10 = 10
    default = 5


class EnabledChaptersCount(Range):
    """Choose how many randomly picked chapters from Enabled Chapters Choice should be enabled.

    If there are fewer allowed chapters than the count to enable, all the allowed chapters will be enabled.

    3 Gold Bricks can be logically acquired per Chapter (Completion + True Jedi + 10/10 Minikits). If there are not
    enough Gold Bricks available to open a Bonus Level, that Bonus Level will be disabled.

    All 36 chapters enabled
    """
    range_start = 1
    range_end = 36
    default = 18


class AllowedChapterTypes(Choice):
    """Specify additional filtering of the allowed chapters that can be enabled.

    - All: No additional filtering, all chapters specified in Allowed Chapters Choice are allowed.
    - No Vehicles: No vehicle chapters (1-4, 2-1, 2-5, 3-1, 4-6, 5-1, 5-3, 6-6) will be allowed.
    """
    option_all = 0
    option_no_vehicles = 1
    default = 0


class AllowedChapters(ChapterOptionSet):
    """Choose the chapter levels that are allowed to be picked when choosing which chapters will be enabled.

    Individual chapters can be specified, e.g. "1-1", "5-4".

    Special values:
    - "All": All chapters will be allowed.
    - "Prequel Trilogy": All chapters in episodes 1, 2 and 3 will be allowed.
    - "Original Trilogy": All chapters in episode 4, 5 and 6 will be allowed.
    - "Episode {number}": e.g. "Episode 3" will allow all chapters in Episode 3, so 3-1 through to 3-6.

    Examples:
    # Enable only 1-1 (Negotiations)
    allowed_chapters: ["1-1"]

    # Enable only 1-1 (Negotiations) (alt.)
    allowed_chapters:
      - 1-1

    # Enable all
    allowed_chapters: ["All"]

    # Enable all (alt.)
    allowed_chapters:
      - All

    # Enable only vehicle levels
    allowed_chapters:
      - 1-4
      - 2-2
      - 2-5
      - 3-1
      - 4-6
      - 5-1
      - 5-3
      - 6-6

    # A mix of values
    allowed_chapters:
      - Prequel Trilogy
      - Episode 4
      - 5-2
      - 5-3
      - 6-5
    """
    default = frozenset({"All"})


class PreferredChapters(ChapterOptionSet):
    """
    When the generator is picking which chapters should be enabled, pick from these preferred chapters first.

    If a preferred chapter is not allowed to be picked because it is not included in the Allowed Chapters option, it
    will not be picked.

    This option can be used to guarantee that certain chapters are present in a generated world.

    Individual chapters can be specified, e.g. "1-1", "5-4".

    Special values:
    - "Prequel Trilogy": All chapters in episodes 1, 2 and 3 will be preferred.
    - "Original Trilogy": All chapters in episode 4, 5 and 6 will be preferred.
    - "Episode {number}": e.g. "Episode 3" will make all chapters in Episode 3, so 3-1 through to 3-6, be preferred.

    Examples:
    # Prefer 1-1 (Negotiations)
    preferred_chapters: ["1-1"]

    # Prefer 1-1 (Negotiations) (alt.)
    preferred_chapters:
      - 1-1

    # Prefer vehicle levels
    preferred_chapters:
      - 1-4
      - 2-2
      - 2-5
      - 3-1
      - 4-6
      - 5-1
      - 5-3
      - 6-6

    # A mix of values
    preferred_chapters:
      - Prequel Trilogy
      - Episode 4
      - 5-2
      - 5-3
      - 6-5
    """
    # There is no point to using "All" for Preferred Chapters, so remove it from the valid_keys.
    valid_keys = set(ChapterOptionSet.valid_keys) - {"All"}
    default = frozenset()


class PreferEntireEpisodes(DefaultOnToggle):
    """
    When enabled, after the generator has picked a chapter to be enabled out of the allowed chapters, it will continue
    picking additional chapters from the same episode until it runs out of allowed chapters in that episode.

    For example, if the generator picks 3-2 as the first enabled chapter, its next picked chapters will be guaranteed to
    be picked from the allowed chapters out of 3-1, 3-3, 3-4, 3-5 and 3-6.

    The Starting Chapter is always the first picked enabled chapter.

    With all chapters allowed to be enabled and an Enabled Chapters Count set to a multiple of 6, this option will
    result in whole episodes being enabled.

    When combined with the Preferred Chapters option, this option can be used to guarantee entire episodes.
    """


class EnableBonusLocations(Toggle):
    """
    The Bonuses Door in the Cantina has a number of levels that require Gold Bricks to access. When this option is
    enabled, completing each of these levels (in Story Mode if they have a Story mode) will be a location to check.

    Additionally, watching the Lego Indiana Jones trailer, and purchasing Indiana Jones from the shop are added as
    locations to check.

    Gold Brick logic currently only counts Gold Bricks earned from Chapter completion, True Jedi, 10/10 Minikits in a
    Chapter, and the singular Gold Bricks awarded for completing Bonus levels.

    Depending on other options, not all Chapters could be enabled, so if there are not enough Gold Bricks available for
    a Bonus level to be accessed, that Bonus level will not be included in the multiworld.
    """


class ChapterUnlockRequirement(Choice):
    """Choose how Chapters within an Episode are unlocked.

    The requirements to access your starting Chapter will be given to you at the start.

    - Story Characters: A Chapter unlocks once its Story mode characters have been unlocked.
    - Chapter Item: A Chapter unlocks after receiving an unlock item specific to that Chapter, e.g.
    "Chapter 2-3 Unlock".
    """
    option_story_characters = 0
    option_chapter_item = 1
    # option_random_characters = 2
    # option_open = 3  # Needs the ability to limit characters to only being usable within a specific episode/
    default = 0


class EpisodeUnlockRequirement(Choice):
    """Choose how Episodes are unlocked.

    The Episode of your starting Chapter will be unlocked from the start.

    - Open: All Episodes will be unlocked from the start.
    - Episode Item: Each Episode will unlock after receiving an unlock item for that Episode, e.g. "Episode 5 Unlock".
    """
    option_open = 0
    option_episode_item = 1
    default = 0


class AllEpisodesCharacterPurchaseRequirements(Choice):
    """The vanilla unlock requirements for purchasing IG-88, Dengar, 4-LOM, Ben Kenobi (Ghost), Anakin Skywalker
    (Ghost), Yoda (Ghost) and R2-Q5 from the shop, are completing every Story mode chapter. The randomizer changes this
    unlock condition because completing every Story mode chapter is unreasonable in most multiworlds and is impossible
    if not all chapters are enabled.

    - Episodes Unlocked: The shop purchases will unlock when the "Episode # Unlock" item for each Episode with enabled
    Chapters has been received. If the Episode Unlock Requirement is set to Open or there is only 1 enabled Episode,
    this will be forcefully changed to "Episodes Tokens" instead.
    - Episodes Tokens: A number of "Episode Complete Token" items will be added to the item pool, equal to the number of
    enabled Episodes. All of these "Episode Complete Token" items will need to be received to unlock the characters for
    purchase.
    - Locations Disabled: The shop purchase locations will not be included in the multiworld.

    """
    option_locations_disabled = 0
    option_episodes_unlocked = 1
    option_episodes_tokens = 2
    default = 2


# Ideally wants Extra Toggle to be randomized, and needs support for per-chapter abilities because different chapters
# have access to different extra characters. I think most of the logic relevant characters are the blaster/grapple ones.
# class ExtraToggleLogic(DefaultOnToggle):
#     """Extra Toggle characters are included in logic"""


class StartingChapter(Choice):
    """Choose the starting chapter. The Episode the starting level belongs to will be accessible from the start.

    Due to the way the logic currently assumes the player has access to a Jedi and a Protocol Droid, if access to the
    chosen starting chapter does not include a Jedi and Protocol Droid in its requirements, a Jedi character and/or
    TC-14 will be added to the starting inventory.

    Due to the character requirements being shared between some levels, some starting levels will result in additional
    levels being open from the start:

    Starting with 1-1 will also open 1-6.
    Starting with 1-2 will also open 1-6.
    Starting with 1-3 will also open 1-6.
    Starting with 1-5 will also open 1-6.
    Starting with 3-2 will also open 3-6.
    Starting with 4-3 will also open 4-2."""
    display_name = "Starting Level"
    # todo: Try setting the attributes for specific levels such that they use 1-1 format rather than 1_1.
    # Variable names cannot use hyphens, so the options for specific levels are set programmatically.
    # option_1-1 = 11
    # option_1-2 = 12
    # etc.
    locals().update({f"option_{episode}-{chapter}": int(f"{episode}{chapter}")
                     for episode, chapter in itertools.product(range(1, 7), range(1, 7))})
    # option_1_1 = 11
    # option_1_2 = 12
    # option_1_3 = 13
    # option_1_4 = 14
    # option_1_5 = 15
    # option_1_6 = 16
    # option_2_1 = 21
    # option_2_2 = 22
    # option_2_3 = 23
    # option_2_4 = 24
    # option_2_5 = 25
    # option_2_6 = 26
    # option_3_1 = 31
    # option_3_2 = 32
    # option_3_3 = 33
    # option_3_4 = 34
    # option_3_5 = 35
    # option_3_6 = 36
    # option_4_1 = 41
    # option_4_2 = 42
    # option_4_3 = 43
    # option_4_4 = 44
    # option_4_5 = 45
    # option_4_6 = 46
    # option_5_1 = 51
    # option_5_2 = 52
    # option_5_3 = 53
    # option_5_4 = 54
    # option_5_5 = 55
    # option_5_6 = 56
    # option_6_1 = 61
    # option_6_2 = 62
    # option_6_3 = 63
    # option_6_4 = 64
    # option_6_5 = 65
    # option_6_6 = 66
    option_random_chapter = -1
    option_random_non_vehicle = -2
    option_random_vehicle = -3
    option_random_episode_1 = 1
    option_random_episode_2 = 2
    option_random_episode_3 = 3
    option_random_episode_4 = 4
    option_random_episode_5 = 5
    option_random_episode_6 = 6
    default = 11


class RandomStartingLevelMaxStartingCharacters(Range):
    """Specify the maximum number of starting characters allowed when picking a random starting level.

    1 Character: 1-4, 2-1, 2-5, 5-1 (all vehicle levels)
    2 Characters: 1-6, 2-2, 3-1 (v), 3-3, 3-4, 3-5, 3-6, 4-6 (v), 5-3 (v), 5-5, 6-3, 6-5, 6-6 (v)
    3 Characters: 1-1, 1-2, 2-6
    4 Characters: 1-3, 2-3, 2-4, 3-2, 4-2, 5-2, 5-4, 5-6
    5 Characters: 4-1
    6 Characters: 1-5, 4-3, 4-4, 4-5, 6-1, 6-4
    7 Characters: 6-2"""
    display_name = "Random Starting Level Max Starting Characters",
    range_start = 2
    range_end = 7
    default = 7


class StartWithDetectors(DefaultOnToggle):
    """Start with the Minikit Detector and Power Brick Detector unlocked.

    When these Extras are enabled, the locations of Minikits and Power Bricks in the current level are shown with
    arrows."""
    display_name = "Start With Detector Extras"


class MostExpensivePurchaseWithNoScoreMultiplier(Range):
    """
    The most expensive individual purchase the player can be expected to make without any score multipliers, *in
    thousands of Studs*.

    For example, an option value of 100 means that purchases up to 100,000 studs in price can be expected to be
    purchased without any score multipliers.

    The logical requirements for expensive purchases will scale with this value. For example, if a purchase of up to
    100,000 Studs is expected with no score multipliers, then a purchase of 100,001 up to 200,000 Studs is expected with
    a score multiplier of 2x.

    "Score x2" costs 1.25 million studs (1250 * 1000) in vanilla, so, for a more vanilla experience with potentially
    more farming for Studs, set this option to 1250.

    The most expensive purchase is "Score x10", which costs 20 million studs (20000 * 1000). Setting this options to
    20000 means that all purchases are logically expected without score multipliers.
    """
    display_name = "Most Expensive Purchase Without Score Multipliers"
    default = 100
    # Max purchase cost is 20_000_000
    # 5 * 1000 * 3840 = 19_200_000 -> 5 is too low
    # 6 * 1000 * 3840 = 23_040_000 -> 6 is the minimum allowed
    range_start = 6
    range_end = 20000


class ReceivedItemMessages(Choice):
    """
    Determines whether an in-game notification is displayed when receiving an item.

    Note: Dying while a message is displayed results in losing studs as normal, but the lost studs do not drop, so
    cannot be recovered.
    Note: Collecting studs while a message is displayed plays the audio for collecting Blue/Purple studs, but this has
    no effect on the received value of the studs collected.

    - All: Every item shows a message
    - None: All items are received silently.
    """
    display_name = "Received Item Messages"
    default = 0
    option_all = 0
    option_none = 1
    # option_progression = 2  # Not Yet Implemented


class CheckedLocationMessages(Choice):
    """
    Determines whether an in-game notification is displayed when checking a location.

    Note: Dying while a message is displayed results in losing studs as normal, but the lost studs do not drop, so
    cannot be recovered.
    Note: Collecting studs while a message is displayed plays the audio for collecting Blue/Purple studs, but this has
    no effect on the received value of the studs collected.

    - All: Every checked location shows a message
    - None: No checked locations show a message
    """
    display_name = "Checked Location Messages"
    default = 0
    option_all = 0
    option_none = 1


@dataclass
class LegoStarWarsTCSOptions(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool

    # Goals.
    minikit_goal_amount: MinikitGoalAmount
    minikit_goal_amount_percentage: MinikitGoalAmountPercentage
    minikit_bundle_size: MinikitBundleSize

    # Enabled/Available locations.
    # Chapters.
    enabled_chapters_count: EnabledChaptersCount
    allowed_chapter_types: AllowedChapterTypes
    allowed_chapters: AllowedChapters
    starting_chapter: StartingChapter
    preferred_chapters: PreferredChapters
    prefer_entire_episodes: PreferEntireEpisodes
    enable_bonus_locations: EnableBonusLocations

    # Logic.
    # logic_difficulty: LogicDifficulty
    episode_unlock_requirement: EpisodeUnlockRequirement
    # todo: Requires logic rewrite
    # chapter_unlock_requirement: ChapterUnlockRequirement
    most_expensive_purchase_with_no_multiplier: MostExpensivePurchaseWithNoScoreMultiplier
    all_episodes_character_purchase_requirements: AllEpisodesCharacterPurchaseRequirements

    # Start inventory helpers.
    start_with_detectors: StartWithDetectors

    # Client behaviour.
    received_item_messages: ReceivedItemMessages
    checked_location_messages: CheckedLocationMessages
    # Future options, not implemented yet.
    # random_starting_level_max_starting_characters: RandomStartingLevelMaxStartingCharacters
