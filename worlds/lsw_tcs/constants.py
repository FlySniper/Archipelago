from enum import Enum, auto, IntFlag

GAME_NAME = "Lego Star Wars The Complete Saga"

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


# todo: Unused currently
class VehicleAbility(Enum):
    NONE = 0
    IMPERIAL = auto()
    TOW = auto()
    BLASTER = auto()


V_IMPERIAL = VehicleAbility.IMPERIAL
V_TOW = VehicleAbility.TOW
V_BLASTER = VehicleAbility.BLASTER