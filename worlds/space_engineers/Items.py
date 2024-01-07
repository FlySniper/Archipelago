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
    # Includes all light armor variants
    "Light Armor Block": ItemData(38800, "Block", PROGRESSION, "Light Armor Block"),
    # Includes all heavy armor variants
    "Heavy Armor Block": ItemData(38801, "Block", PROGRESSION, "Heavy Armor Block"),
    # "Round Armor Slope": ItemData(38802, "Block", PROGRESSION, "Round Armor Slope"),
    # "Heavy Armor Round Slope": ItemData(38803, "Block", PROGRESSION, "Heavy Armor Round Slope"),
    # "Light Armor Ramps": ItemData(38804, "Block", PROGRESSION, "Light Armor Ramps"),
    #    "Light Armor Ramp Corners": ItemData(38805, "Block", PROGRESSION),
    # "Heavy Armor Ramps": ItemData(38806, "Block", PROGRESSION, "Heavy Armor Ramps"),
    #    "Heavy Armor Ramp Corners": ItemData(38807, "Block", PROGRESSION),
    #    "Light Armor Sloped Corners": ItemData(38808, "Block", PROGRESSION),
    #    "Heavy Armor Sloped Corners": ItemData(38809, "Block", PROGRESSION),
    #    "DisplayName_BlockGroup_LightArmorTransitionBlocks": ItemData(38810, "Block"),
    #    "DisplayName_BlockGroup_HeavyArmorTransitionBlocks": ItemData(38811, "Block"),
    #    "DisplayName_Block_LightArmorPanel": ItemData(38812, "Block"),
    #    "DisplayName_Block_heavyArmorPanel": ItemData(38813, "Block"),
    "Projector": ItemData(38814, "Block", PROGRESSION, "Projector"),
    "Target Dummy": ItemData(38815, "Block", PROGRESSION, "Target Dummy"),
    "Sound Block": ItemData(38816, "Block", PROGRESSION, "Sound Block"),
    "Button Panel": ItemData(38817, "Block", PROGRESSION, "Button Panel"),
    "Programmable Blocks": ItemData(38818, "Block", PROGRESSION, "Automation Blocks"),
    "AI Blocks": ItemData(38819, "Block", PROGRESSION, "AI Flight (Move)"),
    "Communication Blocks": ItemData(38820, "Block", PROGRESSION, "Communication Blocks"),
    "Remote Control": ItemData(38821, "Block", PROGRESSION, "Remote Control"),
    #    "Control Station": ItemData(38822, "Block", PROGRESSION),
    "Gyroscope": ItemData(38823, "Block", PROGRESSION, "Gyroscope"),
    "Control Seat": ItemData(38824, "Block", PROGRESSION, "Control Seat"),
    "Door": ItemData(38825, "Block", PROGRESSION, "Door"),
    "Airtight Hangar Door": ItemData(38826, "Block", PROGRESSION, "Airtight Hangar Door"),
    "Blast Doors": ItemData(38827, "Block", PROGRESSION, "Blast Doors"),
    #    "Store": ItemData(38828, "Block"),
    "Battery": ItemData(38829, "Block", PROGRESSION, "Battery"),
    "Fueled Energy Sources": ItemData(38830, "Block", PROGRESSION, "Fueled Energy Sources"),
    "Renewable Energy Sources": ItemData(38831, "Block", PROGRESSION, "Renewable Energy Sources"),
    # "Engineer Plushie": ItemData(38832, "Block", PROGRESSION, "Engineer Plushie"),
    # "Saberoid Plushie": ItemData(38833, "Block", PROGRESSION, "Saberoid Plushie"),
    "Anniversary Statue": ItemData(38834, "Block", PROGRESSION, "Anniversary Statue"),
    "Gravity Blocks": ItemData(38835, "Block", PROGRESSION, "Gravity Blocks"),
    "Passage": ItemData(38836, "Block", PROGRESSION, "Passage"),
    "Steel Catwalk": ItemData(38837, "Block", PROGRESSION, "Steel Catwalk"),
    "Stairs": ItemData(38838, "Block", PROGRESSION, "Stairs"),
    #    "DisplayName_Block_AirDucts": ItemData(38839, "Block", PROGRESSION),
    #    "Corner LCD Screens": ItemData(38840, "Block"),
    "LCD Screens": ItemData(38841, "Block", PROGRESSION, "LCD Screens"),
    "Lighting": ItemData(38842, "Block", PROGRESSION, "Lighting"),
    "Gas Tanks": ItemData(38843, "Block", PROGRESSION, "Gas Tanks"),
    "Air Vent": ItemData(38844, "Block", PROGRESSION, "Air Vent"),
    "Cargo Containers": ItemData(38845, "Block", PROGRESSION, "Cargo Containers"),
    "Small Conveyor Tube": ItemData(38846, "Block", PROGRESSION, "Small Conveyor Tube"),
    "Large Conveyor Tube": ItemData(38847, "Block", PROGRESSION, "Conveyor Junction"),
    "Connector": ItemData(38848, "Block", PROGRESSION, "Inputs/Outputs"),
    "Piston": ItemData(38849, "Block", PROGRESSION, "Piston"),
    "Rotor": ItemData(38850, "Block", PROGRESSION, "Rotor"),
    "Hinge": ItemData(38851, "Block", PROGRESSION, "DisplayName_Block_Hinge"),
    "Medical Blocks": ItemData(38852, "Block", PROGRESSION, "Medical Blocks"),
    "Refinery": ItemData(38853, "Block", PROGRESSION, "Refinery"),
    "O2/H2 Generator": ItemData(38854, "Block", PROGRESSION, "O2/H2 Generator"),
    "Assembler": ItemData(38855, "Block", PROGRESSION, "Assembler"),
    "Oxygen Farm": ItemData(38856, "Block", PROGRESSION, "Oxygen Farm"),
    "Upgrade Modules": ItemData(38857, "Block", PROGRESSION, "Upgrade Modules"),
    #    "letters A to H": ItemData(38858, "Block", PROGRESSION),
    #    "DisplayName_BlockGroup_Numbers": ItemData(38859, "Block"),
    #    "Symbols": ItemData(38860, "Block"),
    "Ion Thrusters": ItemData(38861, "Block", PROGRESSION, "Large Ion Thruster"),
    "Hydrogen Thrusters": ItemData(38862, "Block", PROGRESSION, "Large Hydrogen Thruster"),
    "Atmospheric Thrusters": ItemData(38863, "Block", PROGRESSION, "Large Atmospheric Thruster"),
    "Ship Tools": ItemData(38864, "Block", PROGRESSION, "Ship Tools"),
    "Ore Detector": ItemData(38865, "Block", PROGRESSION, "Ore Detector"),
    "Landing Gear": ItemData(38866, "Block", PROGRESSION, "Landing Gear"),
    "Jump Drive": ItemData(38867, "Block", PROGRESSION, "Jump Drive"),
    "Parachute Hatch": ItemData(38868, "Block", PROGRESSION, "Parachute Hatch"),
    "Warhead": ItemData(38869, "Block", PROGRESSION, "Warhead"),
    "Decoy": ItemData(38870, "Block", PROGRESSION, "Decoy"),
    "Turreted Weapons": ItemData(38871, "Block", PROGRESSION, "Turreted Weapons"),
    "Stationary Weapons": ItemData(38872, "Block", PROGRESSION, "Stationary Weapons"),
    #    "Wheel Suspension 3x3 Right": ItemData(38873, "Block"),
    #    "Wheel Suspension 3x3 Left": ItemData(38874, "Block"),
    "Wheels": ItemData(38875, "Block", PROGRESSION, "Static Wheels"),
    "Windows": ItemData(38876, "Block", PROGRESSION, "Shutters"),
    #    "Medium Corner Windows": ItemData(38877, "Block"),
    #    "Small Corner Windows": ItemData(38878, "Block"),
    #    "Medium Windows": ItemData(38879, "Block", PROGRESSION),
    #    "Small Windows": ItemData(38880, "Block", PROGRESSION),
    #    "Large Windows": ItemData(38881, "Block", PROGRESSION),
    #    "Round Windows": ItemData(38882, "Block", PROGRESSION),

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

item_table_ids: Dict[int, ItemData] = {data.code: data for item, data in item_table.items()}
