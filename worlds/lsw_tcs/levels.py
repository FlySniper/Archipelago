from dataclasses import dataclass, field


@dataclass(frozen=True)
class EpisodeGameLevelArea:
    """
    Each game level within an Episode, e.g. 1-4 is represented by an Area, see AREAS.TXT.

    Does not include Character Bonus, Minikit Bonus, or Superstory.
    """

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


# GameLevelArea short_name to the set of characters needed to unlock that GameLevelArea
LEVEL_CHARACTER_REQUIREMENTS: dict[str, frozenset[str]] = {
    k: frozenset(v) for k, v in {
        # "1-1": {
        #     "Obi-Wan Kenobi",
        #     "Qui-Gon Jinn",
        #     "TC-14",
        # },
        "1-1": set(),
        "1-2": {
            "Jar Jar Binks",
        },
        "1-3": {
            "Captain Panaka",
            "Queen Amidala",
        },
        "1-4": {
            "Anakin's Podracer",
        },
        "1-5": {
            "Anakin Skywalker (Boy)",
            "Captain Panaka",
            "Queen Amidala",
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
    EpisodeGameLevelArea("Negotiations", 1, 1, 0x86E0F4),
    EpisodeGameLevelArea("Invasion of Naboo", 1, 2, 0x86E100),
    EpisodeGameLevelArea("Escape From Naboo", 1, 3, 0x86E10C),
    EpisodeGameLevelArea("Mos Espa Podrace", 1, 4, 0x86E118),
    EpisodeGameLevelArea("Retake Theed Palace", 1, 5, 0x86E130),
    EpisodeGameLevelArea("Darth Maul", 1, 6, 0x86E13C),
    EpisodeGameLevelArea("Bounty Hunter Pursuit", 2, 1, 0x86E16C),
    EpisodeGameLevelArea("Discovery On Kamino", 2, 2, 0x86E178),
    EpisodeGameLevelArea("Droid Factory", 2, 3, 0x86E184),
    EpisodeGameLevelArea("Jedi Battle", 2, 4, 0x86E190),
    EpisodeGameLevelArea("Gunship Cavalry", 2, 5, 0x86E19C),
    EpisodeGameLevelArea("Count Dooku", 2, 6, 0x86E1B4),
    EpisodeGameLevelArea("Battle Over Coruscant", 3, 1, 0x86E1E4),
    EpisodeGameLevelArea("Chancellor In Peril", 3, 2, 0x86E1F0),
    EpisodeGameLevelArea("General Grievous", 3, 3, 0x86E1FC),
    EpisodeGameLevelArea("Defense Of Kashyyyk", 3, 4, 0x86E208),
    EpisodeGameLevelArea("Ruin Of The Jedi", 3, 5, 0x86E214),
    EpisodeGameLevelArea("Darth Vader", 3, 6, 0x86E220),
    EpisodeGameLevelArea("Secret Plans", 4, 1, 0x86E25C),
    EpisodeGameLevelArea("Through The Jundland Wastes", 4, 2, 0x86E268),
    EpisodeGameLevelArea("Mos Eisley Spaceport", 4, 3, 0x86E274),
    EpisodeGameLevelArea("Rescue The Princess", 4, 4, 0x86E280),
    EpisodeGameLevelArea("Death Star Escape", 4, 5, 0x86E28C),
    EpisodeGameLevelArea("Rebel Attack", 4, 6, 0x86E298),
    EpisodeGameLevelArea("Hoth Battle", 5, 1, 0x86E2C8),
    EpisodeGameLevelArea("Escape From Echo Base", 5, 2, 0x86E2D4),
    EpisodeGameLevelArea("Falcon Flight", 5, 3, 0x86E2E0),
    EpisodeGameLevelArea("Dagobah", 5, 4, 0x86E2EC),
    EpisodeGameLevelArea("Betrayal Over Bespin", 5, 5, 0x86E2F8),
    EpisodeGameLevelArea("Cloud City Trap", 5, 6, 0x86E304),
    EpisodeGameLevelArea("Jabba's Palace", 6, 1, 0x86E334),
    EpisodeGameLevelArea("The Great Pit Of Carkoon", 6, 2, 0x86E340),
    EpisodeGameLevelArea("Speeder Showdown", 6, 3, 0x86E34C),
    EpisodeGameLevelArea("The Battle Of Endor", 6, 4, 0x86E358),
    EpisodeGameLevelArea("Jedi Destiny", 6, 5, 0x86E364),
    EpisodeGameLevelArea("Into The Death Star", 6, 6, 0x86E370),
]

SHORT_NAME_TO_LEVEL_AREA = {area.short_name: area for area in GAME_LEVEL_AREAS}
