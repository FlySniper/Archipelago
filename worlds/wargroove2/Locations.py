from BaseClasses import Location

location_table = {
    "Humble Beginnings Rebirth: Talk to Nadia": 253001,
    "Humble Beginnings Rebirth: Victory": 253002,
    "Nuru's Vengeance: Victory": 253005,
    "Nuru's Vengeance: Destroy the Gate with a Spearman": 253006,
    "Nuru's Vengeance: Defeat all Dogs": 253007,
    'Cherrystone Landing: Defeat a Trebuchet with a Golem': 253008,
    'Cherrystone Landing: Defeat a Fortified Village with a Golem': 253009,
    'Cherrystone Landing: Victory': 253010,
    'Den-Two-Away: Victory': 253011,
    'Den-Two-Away: Commander Captures the Lumbermill': 253012,
    'Sky High: Victory': 253013,
    'Sky High: Dragon Defeats Stronghold': 253014,
    #########################################################
    'Slippery Bridge: Victory': 253300,
    'Slippery Bridge: Control all Sea Villages': 253301,
    #########################################################
    'Spire Fire: Victory': 253305,
    'Spire Fire: Kill Enemy Sky Rider': 253306,
    'Spire Fire: Win without losing your Dragon': 253307,
    'Wargroove 2 Finale: Victory': None,
}


class Wargroove2Location(Location):
    game: str = "Wargroove 2"
