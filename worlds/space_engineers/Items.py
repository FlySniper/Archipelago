import typing

from BaseClasses import Item, ItemClassification
from typing import Dict, List

PROGRESSION = ItemClassification.progression
PROGRESSION_SKIP_BALANCING = ItemClassification.progression_skip_balancing
USEFUL = ItemClassification.useful
FILLER = ItemClassification.filler


class ItemData(typing.NamedTuple):
    code: typing.Optional[int]
    type: str
    classification: ItemClassification = PROGRESSION
    se_item_name: str = ""


item_table: Dict[str, ItemData] = {
    # Blocks
    "Light Armor Block": ItemData(38800, "Block", USEFUL, "Light Armor Block"),
    "Heavy Armor Block": ItemData(38801, "Block", USEFUL, "Heavy Armor Block"),
    "Round Armor Slope": ItemData(38802, "Block", FILLER, "Round Armor Slope"),
    "Heavy Armor Round Slope": ItemData(38803, "Block", FILLER, "Heavy Armor Round Slope"),
    "Light Armor Ramps": ItemData(38804, "Block", FILLER, "Light Armor Ramps"),
#    "Light Armor Ramp Corners": ItemData(38805, "Block", FILLER),
    "Heavy Armor Ramps": ItemData(38806, "Block", FILLER, "Heavy Armor Ramps"),
#    "Heavy Armor Ramp Corners": ItemData(38807, "Block", FILLER),
#    "Light Armor Sloped Corners": ItemData(38808, "Block", FILLER),
#    "Heavy Armor Sloped Corners": ItemData(38809, "Block", FILLER),
#    "DisplayName_BlockGroup_LightArmorTransitionBlocks": ItemData(38810, "Block"),
#    "DisplayName_BlockGroup_HeavyArmorTransitionBlocks": ItemData(38811, "Block"),
#    "DisplayName_Block_LightArmorPanel": ItemData(38812, "Block"),
#    "DisplayName_Block_heavyArmorPanel": ItemData(38813, "Block"),
    "Projector": ItemData(38814, "Block", FILLER, "Projector"),
    "Target Dummy": ItemData(38815, "Block", FILLER, "Target Dummy"),
    "Sound Block": ItemData(38816, "Block", FILLER, "Sound Block"),
    "Button Panel": ItemData(38817, "Block", FILLER, "Button Panel"),
#    "Automation Blocks": ItemData(38818, "Block", FILLER),
    "AI Blocks": ItemData(38819, "Block", FILLER, "AI Flight Move"),
    "Communication Blocks": ItemData(38820, "Block", USEFUL, "Communication Blocks"),
    "Remote Control": ItemData(38821, "Block", FILLER, "Remote Control"),
#    "Control Station": ItemData(38822, "Block", FILLER),
    "Gyroscope": ItemData(38823, "Block", PROGRESSION, "Gyroscope"),
    "Control Seat": ItemData(38824, "Block", PROGRESSION, "Control Seat"),
    "Door": ItemData(38825, "Block", FILLER, "Door"),
    "Airtight Hangar Door": ItemData(38826, "Block", FILLER, "Airtight Hangar Door"),
    "Blast Doors": ItemData(38827, "Block", FILLER, "Blast Doors"),
#    "Store": ItemData(38828, "Block"),
    "Battery": ItemData(38829, "Block", USEFUL, "Battery"),
    "Fueled Energy Sources": ItemData(38830, "Block", PROGRESSION, "Fueled Energy Sources"),
    "Renewable Energy Sources": ItemData(38831, "Block", PROGRESSION, "Renewable Energy Sources"),
    "Engineer Plushie": ItemData(38832, "Block", FILLER, "Engineer Plushie"),
    "Saberoid Plushie": ItemData(38833, "Block", FILLER, "Saberoid Plushie"),
    "Anniversary Statue": ItemData(38834, "Block", FILLER, "Anniversary Statue"),
    "Gravity Blocks": ItemData(38835, "Block", USEFUL, "Gravity Blocks"),
    "Passage": ItemData(38836, "Block", FILLER, "Passage"),
    "Steel Catwalk": ItemData(38837, "Block", FILLER, "Steel Catwalk"),
    "Stairs": ItemData(38838, "Block", FILLER, "Stairs"),
#    "DisplayName_Block_AirDucts": ItemData(38839, "Block", FILLER),
#    "Corner LCD Screens": ItemData(38840, "Block"),
    "LCD Screens": ItemData(38841, "Block", FILLER, "LCD Screens"),
    "Lighting": ItemData(38842, "Block", FILLER, "Lighting"),
    "Gas Tanks": ItemData(38843, "Block", PROGRESSION, "Gas Tanks"),
    "Air Vent": ItemData(38844, "Block", USEFUL, "Air Vent"),
    "Cargo Containers": ItemData(38845, "Block", PROGRESSION, "Cargo Containers"),
    "Small Conveyor Tube": ItemData(38846, "Block", PROGRESSION, "Small Conveyor Tube"),
    "Large Conveyor Tube": ItemData(38847, "Block", PROGRESSION, "Conveyor Junction"),
    "Connector": ItemData(38848, "Block", FILLER, "Inputs/Outputs"),
    "Piston": ItemData(38849, "Block", FILLER, "Piston"),
    "Rotor": ItemData(38850, "Block", FILLER, "Rotor"),
    "Hinge": ItemData(38851, "Block", FILLER, "DisplayName_Block_Hinge"),
    "Medical Blocks": ItemData(38852, "Block", PROGRESSION, "Medical Blocks"),
    "Refinery": ItemData(38853, "Block", PROGRESSION, "Refinery"),
    "O2/H2 Generator": ItemData(38854, "Block", PROGRESSION, "O2/H2 Generator"),
    "Assembler": ItemData(38855, "Block", PROGRESSION, "Assembler"),
    "Oxygen Farm": ItemData(38856, "Block", USEFUL, "Oxygen Farm"),
    "Upgrade Modules": ItemData(38857, "Block", USEFUL, "Upgrade Modules"),
#    "letters A to H": ItemData(38858, "Block", FILLER),
#    "DisplayName_BlockGroup_Numbers": ItemData(38859, "Block"),
#    "Symbols": ItemData(38860, "Block"),
    "Ion Thrusters": ItemData(38861, "Block", PROGRESSION, "Large Ion Thruster"),
    "Hydrogen Thrusters": ItemData(38862, "Block", PROGRESSION, "Large Hydrogen Thruster"),
    "Atmospheric Thrusters": ItemData(38863, "Block", PROGRESSION, "Large Atmospheric Thruster"),
    "Ship Tools": ItemData(38864, "Block", USEFUL, "Ship Tools"),
    "Ore Detector": ItemData(38865, "Block", USEFUL, "Ore Detector"),
    "Landing Gear": ItemData(38866, "Block", USEFUL, "Landing Gear"),
    "Jump Drive": ItemData(38867, "Block", PROGRESSION, "Jump Drive"),
    "Parachute Hatch": ItemData(38868, "Block", FILLER, "Parachute Hatch"),
    "Warhead": ItemData(38869, "Block", FILLER, "Warhead"),
    "Decoy": ItemData(38870, "Block", FILLER, "Decoy"),
    "Turreted Weapons": ItemData(38871, "Block", PROGRESSION, "Turreted Weapons"),  # Might be progression if trying to fight enemies
    "Stationary Weapons": ItemData(38872, "Block", FILLER, "Stationary Weapons"),  # Might be progression if trying to fight enemies
#    "Wheel Suspension 3x3 Right": ItemData(38873, "Block"),
#    "Wheel Suspension 3x3 Left": ItemData(38874, "Block"),
    "Wheels": ItemData(38875, "Block", FILLER, "Static Wheels"),
    "Windows": ItemData(38876, "Block", FILLER, "Shutters"),
#    "Medium Corner Windows": ItemData(38877, "Block"),
#    "Small Corner Windows": ItemData(38878, "Block"),
#    "Medium Windows": ItemData(38879, "Block", FILLER),
#    "Small Windows": ItemData(38880, "Block", FILLER),
#    "Large Windows": ItemData(38881, "Block", FILLER),
#    "Round Windows": ItemData(38882, "Block", FILLER),

    # Filler Items

    "Oxygen Bottle": ItemData(38883, "Inventory", FILLER, "Oxygen Bottle"),
    "Hydrogen Bottle": ItemData(38884, "Inventory", FILLER, "Hydrogen Bottle"),
    "Iron Ingot": ItemData(38885, "Inventory", FILLER, "Iron Ingot"),
    "Nickel Ingot": ItemData(38886, "Inventory", FILLER, "Nickel Ingot"),
    "Silicon Ingot": ItemData(38887, "Inventory", FILLER, "Silicon Ingot"),
    "Gravel": ItemData(38888, "Inventory", FILLER, "Gravel"),

    # World Event Items

    "Progressive Space Size": ItemData(38889, "World Event", PROGRESSION, "Progressive Space Size"),

    # Victory
    'Space Engineers: Victory': ItemData(None, 'Goal')

}
