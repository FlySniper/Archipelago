from enum import auto, IntFlag

GAME_NAME = "Lego Star Wars The Complete Saga"

AP_WORLD_VERSION: tuple[int, int, int] = (0, 0, 1)


# todo: These are the abilities from the manual logic, not the real abilities.
class CharacterAbility(IntFlag):
    NONE = 0
    ASTROMECH = auto()
    BLASTER = auto()
    BOUNTY_HUNTER = auto()
    DROID_OR_FLY = auto()  # Not sure what this is actually meant to be
    HIGH_JUMP = auto()
    IMPERIAL = auto()
    JEDI = auto()
    PROTOCOL_DROID = auto()
    SHORTIE = auto()
    SITH = auto()
    # todo: Lots more abilities to add to split up and replace the basic existing ones...
    # GHOST = auto()
    # DROID = auto()
    # UNTARGETABLE = auto()  # Are there any characters other than Ghosts?
    VEHICLE_IMPERIAL = auto()
    VEHICLE_TOW = auto()
    # VEHICLE_BLASTER = auto()


ASTROMECH = CharacterAbility.ASTROMECH
BLASTER = CharacterAbility.BLASTER
BOUNTY_HUNTER = CharacterAbility.BOUNTY_HUNTER
DROID_OR_FLY = CharacterAbility.DROID_OR_FLY
HIGH_JUMP = CharacterAbility.HIGH_JUMP
IMPERIAL = CharacterAbility.IMPERIAL
JEDI = CharacterAbility.JEDI
PROTOCOL_DROID = CharacterAbility.PROTOCOL_DROID
SHORTIE = CharacterAbility.SHORTIE
SITH = CharacterAbility.SITH
VEHICLE_IMPERIAL = CharacterAbility.VEHICLE_IMPERIAL
VEHICLE_TOW = CharacterAbility.VEHICLE_TOW

# todo: VEHICLE_TOW can probably be included in the future too.
# todo: GHOST can probably be included in the future too.
RARE_AND_USEFUL_ABILITIES = ASTROMECH | BOUNTY_HUNTER | HIGH_JUMP | SHORTIE | SITH | PROTOCOL_DROID

GOLD_BRICK_EVENT_NAME = "Gold Brick"
