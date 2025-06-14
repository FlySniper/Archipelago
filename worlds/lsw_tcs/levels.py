from collections import Counter
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass(frozen=True)
class EpisodeGameLevelArea:
    """
    Each game level within an Episode, e.g. 1-4 is represented by an Area, see AREAS.TXT.

    Does not include Character Bonus, Minikit Bonus, or Superstory.
    """
    # Used as a bool or as `value > 0`. The bits other than the first get preserved, so it appears to be safe to store
    # arbitrary data in the remaining 7 bits.
    UNLOCKED_OFFSET: ClassVar[int] = 0

    # Used as a bool or as `value > 0`. The bits other than the first get preserved, so it appears to be safe to store
    # arbitrary data in the remaining 7 bits, which is where the client stores Free Play completion.
    STORY_COMPLETE_OFFSET: ClassVar[int] = 1

    # Used as a bool or as `value > 0`. The bits other than the first get preserved, so it appears to be safe to store
    # arbitrary data in the remaining 7 bits.
    TRUE_JEDI_COMPLETE_OFFSET: ClassVar[int] = 2

    # The 3rd byte also gets set when True Jedi is completed. Having either the second byte or the second byte as
    # nonzero counts for True Jedi being completed.
    # Maybe one of the two bytes is a leftover from having separate True Jedi for Story and Free Play originally, like
    # in some later, non-Star Wars games?
    TRUE_JEDI_COMPLETE_2_OFFSET: ClassVar[int] = 3

    # Used as a bool or as `value > 0`. The bits other than the first get preserved, so it appears to be safe to store
    # arbitrary data in the remaining 7 bits.
    MINIKIT_GOLD_BRICK_OFFSET: ClassVar[int] = 4

    # Setting this to 10 or higher will prevent newly collected minikits from being saved as collected.
    MINIKIT_COUNT_OFFSET: ClassVar[int] = 5

    # Must be exactly `1`
    POWER_BRICK_COLLECTED_OFFSET: ClassVar[int] = 6

    # Used as a bool or as `value > 0`. The bits other than the first get preserved, so it appears to be safe to store
    # arbitrary data in the remaining 7 bits.
    CHALLENGE_COMPLETE_OFFSET: ClassVar[int] = 7

    # Unused, 4-byte float that preserves NaN signal bits and appears to never be written to normally, so can be used to
    # store arbitrary data.
    UNUSED_CHALLENGE_BEST_TIME_OFFSET: ClassVar[int] = 8

    name: str
    # The episode this Area is in.
    episode: int
    # The number within the episode that this Area is in.
    number_in_episode: int
    # # Level IDs, see the order of the levels defined in LEVELS.TXT.
    # # These are the individual playable 'levels' within a game level, and also include intros, outros and the 'status'
    # # screen at the end of a game level.
    # level_ids: set[int]
    # The address in the in-memory save data that stores most of the Area information.
    address: int
    # The level ID of the 'status' screen used when tallying up collected studs/minikits/etc., either from
    # "Save and Exit to Cantina", or from completing the level.
    status_level_id: int
    ## The address of each level in the area with minikits, and the names of the minikits in that level.
    #minikit_address_to_names: dict[int, set[str]]
    short_name: str = field(init=False)
    item_requirements: frozenset[str] = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "short_name", f"{self.episode}-{self.number_in_episode}")
        character_requirements = LEVEL_CHARACTER_REQUIREMENTS[self.short_name]
        if self.episode == 1:
            item_requirements = frozenset(character_requirements)
        else:
            item_requirements = frozenset(character_requirements.union({f"Episode {self.episode} Unlock"}))
        object.__setattr__(self, "item_requirements", item_requirements)


@dataclass(frozen=True)
class BonusGameLevelArea:
    name: str
    address: int
    completion_offset: int
    """
    The cheat table listing the addresses listed a base address with unknown purpose for the bonus levels, and then an
    offset from that address for the completion byte, so that is why there is an offset separate from the address.
    """
    status_level_id: int  # todo: probably not needed
    item_requirements: Counter[str]


# GameLevelArea short_name to the set of characters needed to unlock that GameLevelArea
# To find characters, grep the LEVELS directory for non-binary files, searching for '" player'. Note that vehicle levels
# typically have an alternate color scheme vehicle for Player 2 which may not be collectable.
LEVEL_CHARACTER_REQUIREMENTS: dict[str, frozenset[str]] = {
    k: frozenset(v) for k, v in {
        # "1-1": {
        #     "Obi-Wan Kenobi",
        #     "Qui-Gon Jinn",
        #     "TC-14",
        # },
        "1-1": set(),
        "1-2": {
            # "Obi-Wan Kenobi",
            # "Qui-Gon Jinn",
            "Jar Jar Binks",
        },
        "1-3": {
            # "Obi-Wan Kenobi",
            # "Qui-Gon Jinn",
            "Captain Panaka",
            "Queen Amidala",
        },
        "1-4": {
            "Anakin's Podracer",
        },
        "1-5": {
            # "Obi-Wan Kenobi",
            # "Qui-Gon Jinn",
            "Anakin Skywalker (Boy)",
            "Captain Panaka",
            "Queen Amidala",  # FIXME: Should be Padmé (Battle) instead?
            "R2-D2",
        },
        "1-6": set(),
        # "1-6": {
        #     "Obi-Wan Kenobi",
        #     "Qui-Gon Jinn",
        # },
        "2-1": {
            "Anakin's Speeder",
        },
        "2-2": {
            "Obi-Wan Kenobi (Jedi Master)",
            "R4-P17",
        },
        "2-3": {
            "Anakin Skywalker (Padawan)",
            "C-3PO",
            "Padmé (Geonosis)",
            "R2-D2",
        },
        "2-4": {
            "Anakin Skywalker (Padawan)",
            "Mace Windu",
            "Padmé (Clawed)",
            "Obi-Wan Kenobi (Jedi Master)",
            # R2-D2  # FIXME?: Missing R2-D2?
        },
        "2-5": {
            "Republic Gunship",
        },
        "2-6": {
            "Anakin Skywalker (Padawan)",
            "Obi-Wan Kenobi (Jedi Master)",
            "Yoda",
        },
        "3-1": {
            "Anakin's Starfighter",
            "Obi-Wan's Starfighter",
            # FIXME?: These non-vehicle characters are also listed as player characters in the file. Should they be
            #  required?
            # "Obi-Wan Kenobi (Episode 3)",
            # "Anakin Skywalker (Jedi)",
        },
        "3-2": {
            "Anakin Skywalker (Jedi)",
            "Chancellor Palpatine",
            "Obi-Wan Kenobi (Episode 3)",
            "R2-D2",
        },
        "3-3": {
            "Commander Cody",
            "Obi-Wan Kenobi (Episode 3)",
        },
        "3-4": {
            "Chewbacca",
            "Yoda",
        },
        "3-5": {
            "Obi-Wan Kenobi (Episode 3)",
            "Yoda",
        },
        "3-6": {
            "Anakin Skywalker (Jedi)",
            "Obi-Wan Kenobi (Episode 3)",
        },
        "4-1": {
            "Captain Antilles",
            "C-3PO",
            "Princess Leia",
            "R2-D2",
            "Rebel Friend",
        },
        "4-2": {
            "Ben Kenobi",
            "C-3PO",
            "Luke Skywalker (Tatooine)",
            "R2-D2",
        },
        "4-3": {
            "Ben Kenobi",
            "C-3PO",
            "Chewbacca",
            "Han Solo",
            "Luke Skywalker (Tatooine)",
            "R2-D2",
        },
        "4-4": {
            "Ben Kenobi",
            "C-3PO",
            "Chewbacca",
            "Han Solo (Stormtrooper)",
            "Luke Skywalker (Stormtrooper)",
            "R2-D2",
        },
        "4-5": {
            "C-3PO",
            "Chewbacca",
            "Han Solo",
            "Luke Skywalker (Tatooine)",
            "Princess Leia",
            "R2-D2",
        },
        "4-6": {
            "X-Wing",
            "Y-Wing",
        },
        "5-1": {
            "Snowspeeder",
        },
        "5-2": {
            "C-3PO",
            "Chewbacca",
            "Han Solo (Hoth)",
            "Princess Leia (Hoth)",
        },
        "5-3": {
            "Millennium Falcon",
            "X-Wing",
        },
        "5-4": {
            "Luke Skywalker (Dagobah)",
            "Luke Skywalker (Pilot)",
            "R2-D2",
            "Yoda",
        },
        "5-5": {
            "Luke Skywalker (Bespin)",
            "R2-D2",
        },
        "5-6": {
            "C-3PO",
            "Lando Calrissian",
            "Princess Leia (Bespin)",
            "R2-D2",
            # "Chewbacca",  # FIXME?: Missing Chewbacca?
        },
        "6-1": {
            "Chewbacca",
            "C-3PO",
            "Han Solo (Skiff)",
            "Princess Leia (Boushh)",
            "Luke Skywalker (Jedi)",
            "R2-D2",
        },
        "6-2": {
            "Chewbacca",
            "C-3PO",
            "Han Solo (Skiff)",
            "Princess Leia (Slave)",
            "Lando Calrissian (Palace Guard)",
            "Luke Skywalker (Jedi)",
            "R2-D2",
        },
        "6-3": {
            "Luke Skywalker (Endor)",
            "Princess Leia (Endor)",
        },
        "6-4": {
            "Chewbacca",
            "C-3PO",
            "Han Solo (Endor)",
            "Princess Leia (Endor)",
            "R2-D2",
            "Wicket",
        },
        "6-5": {
            "Darth Vader",
            "Luke Skywalker (Jedi)",
        },
        "6-6": {
            "Millennium Falcon",
            "X-Wing",
        }
    }.items()
}

# TODO: Record level IDs, these would mostly be there to help make map switching in the tracker easier, and would serve
#  as a record of data that might be useful for others.
GAME_LEVEL_AREAS = [
    EpisodeGameLevelArea("Negotiations", 1, 1, 0x86E0F4, 7),
    EpisodeGameLevelArea("Invasion of Naboo", 1, 2, 0x86E100, 15),
    EpisodeGameLevelArea("Escape From Naboo", 1, 3, 0x86E10C, 24),
    EpisodeGameLevelArea("Mos Espa Pod Race", 1, 4, 0x86E118, 37),
    EpisodeGameLevelArea("Retake Theed Palace", 1, 5, 0x86E130, 48),
    EpisodeGameLevelArea("Darth Maul", 1, 6, 0x86E13C, 55),
    EpisodeGameLevelArea("Bounty Hunter Pursuit", 2, 1, 0x86E16C, 68),
    EpisodeGameLevelArea("Discovery On Kamino", 2, 2, 0x86E178, 78),
    EpisodeGameLevelArea("Droid Factory", 2, 3, 0x86E184, 88),
    EpisodeGameLevelArea("Jedi Battle", 2, 4, 0x86E190, 92),
    EpisodeGameLevelArea("Gunship Cavalry", 2, 5, 0x86E19C, 95),
    EpisodeGameLevelArea("Count Dooku", 2, 6, 0x86E1B4, 103),
    EpisodeGameLevelArea("Battle Over Coruscant", 3, 1, 0x86E1E4, 111),
    EpisodeGameLevelArea("Chancellor In Peril", 3, 2, 0x86E1F0, 121),
    EpisodeGameLevelArea("General Grievous", 3, 3, 0x86E1FC, 123),
    EpisodeGameLevelArea("Defense Of Kashyyyk", 3, 4, 0x86E208, 128),
    EpisodeGameLevelArea("Ruin Of The Jedi", 3, 5, 0x86E214, 134),
    EpisodeGameLevelArea("Darth Vader", 3, 6, 0x86E220, 139),
    EpisodeGameLevelArea("Secret Plans", 4, 1, 0x86E25C, 159),
    EpisodeGameLevelArea("Through The Jundland Wastes", 4, 2, 0x86E268, 167),
    EpisodeGameLevelArea("Mos Eisley Spaceport", 4, 3, 0x86E274, 177),
    EpisodeGameLevelArea("Rescue The Princess", 4, 4, 0x86E280, 185),
    EpisodeGameLevelArea("Death Star Escape", 4, 5, 0x86E28C, 192),
    EpisodeGameLevelArea("Rebel Attack", 4, 6, 0x86E298, 203),
    EpisodeGameLevelArea("Hoth Battle", 5, 1, 0x86E2C8, 219),
    EpisodeGameLevelArea("Escape From Echo Base", 5, 2, 0x86E2D4, 228),
    EpisodeGameLevelArea("Falcon Flight", 5, 3, 0x86E2E0, 236),
    EpisodeGameLevelArea("Dagobah", 5, 4, 0x86E2EC, 244),
    EpisodeGameLevelArea("Betrayal Over Bespin", 5, 5, 0x86E2F8, 251),
    EpisodeGameLevelArea("Cloud City Trap", 5, 6, 0x86E304, 257),
    EpisodeGameLevelArea("Jabba's Palace", 6, 1, 0x86E334, 271),
    EpisodeGameLevelArea("The Great Pit Of Carkoon", 6, 2, 0x86E340, 277),
    EpisodeGameLevelArea("Speeder Showdown", 6, 3, 0x86E34C, 279),
    EpisodeGameLevelArea("The Battle Of Endor", 6, 4, 0x86E358, 286),
    EpisodeGameLevelArea("Jedi Destiny", 6, 5, 0x86E364, 301),
    EpisodeGameLevelArea("Into The Death Star", 6, 6, 0x86E370, 297),
]

BONUS_GAME_LEVEL_AREAS = [
    BonusGameLevelArea("Mos Espa Pod Race (Original)", 0x86E124, 0x1, 35, Counter({
        "Anakin's Podracer": 1,
        "Progressive Bonus Level": 1,
    })),
    # There are a number of test levels in LEVELS.TXT that seem to not be counted, so the level IDs for Anakin's Flight
    # do not match what is expected:
    # Intro = 327
    # A = 328
    # B = 329
    # C = 330
    # Outro1 = 331
    # Outro2 = 332
    # Status = 333
    BonusGameLevelArea("Anakin's Flight", 0x86E3AC, 0x1, 333, Counter({
        "Naboo Starfighter": 1,
        "Progressive Bonus Level": 2,
    })),
    BonusGameLevelArea("Gunship Cavalry (Original)", 0x86E1A8, 0x1, 98, Counter({
        "Republic Gunship": 1,
        "Progressive Bonus Level": 3,
    })),
    BonusGameLevelArea("A New Hope (Bonus Level)", 0x86E3B8, 0x8, 150, Counter({
        "Darth Vader": 1,
        "Stormtrooper": 1,
        "C-3PO": 1,
        "Progressive Bonus Level": 4,
    })),
    BonusGameLevelArea("LEGO City", 0x86E3B8, 0x1, 311, Counter({
        "Progressive Bonus Level": 5,
    })),
    BonusGameLevelArea("New Town", 0x86E3A0, 0x1, 309, Counter({
        "Progressive Bonus Level": 6,
    })),
    # The bonus level was never completed, so there is just the trailer to watch (which can be skipped immediately).
    BonusGameLevelArea("Indiana Jones: Trailer", 0x86E4E5, 0x0, -1, Counter({
        "Progressive Bonus Level": 1,
    }))
]

SHORT_NAME_TO_LEVEL_AREA = {area.short_name: area for area in GAME_LEVEL_AREAS}
