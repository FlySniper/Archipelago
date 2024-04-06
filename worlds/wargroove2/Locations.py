from BaseClasses import Location

location_table = {
    "Humble Beginnings Rebirth: Talk to Nadia": 253001,
    "Humble Beginnings Rebirth: Victory": 253002,
    "Humble Beginnings Rebirth: Good Dog": 253003,
    #########################################################
    "Nuru's Vengeance: Victory": 253005,
    "Nuru's Vengeance: Spearman Destroys the Gate": 253006,
    "Nuru's Vengeance: Defeat all Dogs": 253007,
    'Cherrystone Landing: Smacked a Trebuchet': 253008,
    'Cherrystone Landing: Smacked a Fortified Village': 253009,
    'Cherrystone Landing: Victory': 253010,
    'Den-Two-Away: Victory': 253011,
    'Den-Two-Away: Commander Captures the Lumbermill': 253012,
    'Sky High: Victory': 253013,
    'Sky High: Dragon Defeats Stronghold': 253014,
    "Terrible Tributaries: Victory": 253015,
    "Terrible Tributaries: Swimming Knights": 253016,
    "Terrible Tributaries: Steal Code Names": 253017,
    "Beached: Victory": 253018,
    "Beached: Turtle Power": 253019,
    "Beached: Happy Turtle": 253020,
    "Riflemen Blockade: Victory": 253021,
    "Riflemen Blockade: From the Mountains": 253022,
    "Riflemen Blockade: To the Road": 253023,
    "Wagon Freeway: Victory": 253024,
    "Wagon Freeway: All Mine Now": 253025,
    "Wagon Freeway: Pigeon Carrier": 253026,
    "Kraken Strait: Victory": 253027,
    "Kraken Strait: Well Defended": 253028,
    "Kraken Strait: Clipped Wings": 253029,
    #########################################################
    'Slippery Bridge: Victory': 253300,
    'Slippery Bridge: Control all Sea Villages': 253301,
    #########################################################
    'Spire Fire: Victory': 253305,
    'Spire Fire: Kill Enemy Sky Rider': 253306,
    'Spire Fire: Win without losing your Dragon': 253307,
    #########################################################
    'Sunken Forest: Victory': 253310,
    'Sunken Forest: High Ground': 253311,
    'Sunken Forest: Coastal Siege': 253312,
    #########################################################
    'Tenri\'s Mistake: Victory': 253315,
    'Tenri\'s Mistake: Mighty Barracks': 253316,
    'Tenri\'s Mistake: Commander Arrives': 253317,
    #########################################################
    "Enmity Cliffs: Victory": 253320,
    "Enmity Cliffs: Spear Flood": 253321,
    "Enmity Cliffs: Across the Gap": 253322,
    #########################################################
    "Portal Peril: Victory": 253325,
    "Portal Peril: Unleash the Hounds": 253326,
    "Portal Peril: Overcharged": 253327,
    #########################################################
    "Towers of the Abyss: Victory": 253330,
    "Towers of the Abyss: Siege Master": 253331,
    "Towers of the Abyss: Perfect Defense": 253332,
    'Wargroove 2 Finale: Victory': None,
}

location_id_name: {int, str} = {}
for name, id in location_table:
    if id is not None:
        location_id_name[id] = name

class Wargroove2Location(Location):
    game: str = "Wargroove 2"
