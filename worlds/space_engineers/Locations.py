class LocationData:
    location_name: str
    location_id: int = 0
    component_list: [str] = []
    se_group_name: str
    type: str = ""

    def __init__(self, location_id: int, component_list: [str], se_group_name: str, type: str = 'Block',
                 location_name: str = None):
        if location_name is None:
            self.location_name = se_group_name
        else:
            self.location_name = location_name
        self.location_id = location_id
        self.component_list = component_list
        self.se_group_name = se_group_name
        self.type = type


BULLET_PROOF_GLASS = "BULLET_PROOF_GLASS"
DETECTOR_COMPONENTS = "DETECTOR_COMPONENTS"
LARGE_TUBE = "LARGE_TUBE"
MEDICAL_COMPONENTS = "MEDICAL_COMPONENTS"
METAL_GRID = "METAL_GRID"
MOTOR = "MOTOR"
BATTERY_COMPONENTS = "BATTERY_COMPONENTS"
RADIO_COMPONENTS = "RADIO_COMPONENTS"
SMALL_TUBE = "SMALL_TUBE"
EXPLOSIVES = "EXPLOSIVES"
GRAVITY_COMPONENTS = "GRAVITY_COMPONENTS"
REACTOR_COMPONENTS = "REACTOR_COMPONENTS"
SUPER_CONDUCTOR_COMPONENTS = "SUPER_CONDUCTOR_COMPONENTS"
THRUSTER_COMPONENTS = "THRUSTER_COMPONENTS"
COMPUTER = "COMPUTER"
CONSTRUCTION_COMPONENTS = "CONSTRUCTION_COMPONENTS"
DISPLAY = "DISPLAY"
GIRDER = "GIRDER"
INTERIOR_PLATE = "INTERIOR_PLATE"
MOTOR = "MOTOR"
SOLAR_CELL = "SOLAR_CELL"
STEEL_PLATE = "STEEL_PLATE"

STARTING_COMPONENTS = [STEEL_PLATE, SOLAR_CELL, MOTOR, INTERIOR_PLATE, GIRDER, DISPLAY, CONSTRUCTION_COMPONENTS,
                       COMPUTER]
MANUFACTURING_UPGRADE_COMPONENTS = [BULLET_PROOF_GLASS, DETECTOR_COMPONENTS, LARGE_TUBE, MEDICAL_COMPONENTS, METAL_GRID,
                                    BATTERY_COMPONENTS, RADIO_COMPONENTS, SMALL_TUBE,
                                    EXPLOSIVES, REACTOR_COMPONENTS]
SPACE_COMPONENTS = [THRUSTER_COMPONENTS, SUPER_CONDUCTOR_COMPONENTS, GRAVITY_COMPONENTS]

location_table: {str, LocationData} = {
    # Includes all light armor variants
    "Built Light Armor Block": LocationData(3883300, [STEEL_PLATE], "Built Light Armor Block"),
    # Includes all heavy armor variants
    "Built Heavy Armor Block": LocationData(3883301, [STEEL_PLATE, METAL_GRID], "Built Heavy Armor Block"),
    # "Built Round Armor Slope": LocationData(3883302, [STEEL_PLATE], "Built Round Armor Slope"),
    # "Built Heavy Armor Round Slope": LocationData(3883303, [STEEL_PLATE, METAL_GRID],
    # "Built Heavy Armor Round Slope"),
    # "Built Light Armor Ramps": LocationData(3883304, [STEEL_PLATE], "Built Light Armor Ramps"),
    # "Built Heavy Armor Ramps": LocationData(3883306, [STEEL_PLATE, METAL_GRID], "Built Heavy Armor Ramps"),
    "Built Projector": LocationData(3883314, [COMPUTER, MOTOR, LARGE_TUBE, CONSTRUCTION_COMPONENTS, STEEL_PLATE],
                                    "Built Projector"),
    "Built Target Dummy": LocationData(3883315, [STEEL_PLATE, DISPLAY, COMPUTER, MOTOR, SMALL_TUBE],
                                       "Built Target Dummy"),
    "Built Sound Block": LocationData(3883316, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS, COMPUTER],
                                      "Built Sound Block"),
    "Built Button Panel": LocationData(3883317, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS, COMPUTER],
                                       "Built Button Panel"),
    "Built Programmable Blocks": LocationData(3883318, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS],
                                              "Built Automation Blocks", location_name="Built Programmable Blocks"),
    "Built AI Blocks": LocationData(3883319, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS, DETECTOR_COMPONENTS, MOTOR,
                                              COMPUTER, STEEL_PLATE], "Built AI Flight Move",
                                    location_name="Built AI Blocks"),
    "Built Communication Blocks": LocationData(3883320, [RADIO_COMPONENTS, COMPUTER, LARGE_TUBE,
                                                         CONSTRUCTION_COMPONENTS, STEEL_PLATE],
                                               "Built Communication Blocks"),
    "Built Remote Control": LocationData(3883321, [STEEL_PLATE, COMPUTER], "Built Remote Control"),
    "Built Gyroscope": LocationData(3883323, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, LARGE_TUBE, MOTOR, COMPUTER],
                                    "Built Gyroscope"),
    "Built Control Seat": LocationData(3883324, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS], "Built Control Seat"),
    "Built Door": LocationData(3883325, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS, SMALL_TUBE, MOTOR, DISPLAY, COMPUTER,
                                         STEEL_PLATE], "Built Door"),
    "Built Airtight Hangar Door": LocationData(3883326, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, SMALL_TUBE, MOTOR,
                                                         COMPUTER], "Built Airtight Hangar Door"),
    "Built Blast Doors": LocationData(3883327, [STEEL_PLATE], "Built Blast Doors"),
    "Built Battery": LocationData(3883329, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, BATTERY_COMPONENTS, COMPUTER],
                                  "Built Battery"),
    "Built Fueled Energy Sources": LocationData(3883330, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, METAL_GRID, LARGE_TUBE,
                                                          REACTOR_COMPONENTS, MOTOR, COMPUTER],
                                                "Built Fueled Energy Sources"),
    "Built Renewable Energy Sources": LocationData(3883331, [INTERIOR_PLATE, MOTOR, CONSTRUCTION_COMPONENTS, GIRDER,
                                                             COMPUTER], "Built Renewable Energy Sources"),
    # These plushies cannot be built
    # "Built Engineer Plushie": LocationData(3883332, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS],
    #                                        "Built Engineer Plushie"),
    # "Built Saberoid Plushie": LocationData(3883333, [STEEL_PLATE], "Built Saberoid Plushie"),
    "Built Anniversary Statue": LocationData(3883334, [GIRDER, STEEL_PLATE, CONSTRUCTION_COMPONENTS],
                                             "Built Anniversary Statue"),
    "Built Gravity Blocks": LocationData(3883335, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, COMPUTER, GRAVITY_COMPONENTS],
                                         "Built Gravity Blocks"),
    "Built Passage": LocationData(3883336, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS, SMALL_TUBE], "Built Passage"),
    "Built Steel Catwalk": LocationData(3883337, [CONSTRUCTION_COMPONENTS, INTERIOR_PLATE, SMALL_TUBE],
                                        "Built Steel Catwalk"),
    "Built Stairs": LocationData(3883338, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS], "Built Stairs"),
    "Built LCD Screens": LocationData(3883341, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS, COMPUTER, DISPLAY,
                                                BULLET_PROOF_GLASS], "Built LCD Screens"),
    "Built Lighting": LocationData(3883342, [CONSTRUCTION_COMPONENTS], "Built Lighting"),
    "Built Gas Tanks": LocationData(3883343, [STEEL_PLATE, LARGE_TUBE, SMALL_TUBE, COMPUTER, CONSTRUCTION_COMPONENTS],
                                    "Built Gas Tanks"),
    "Built Air Vent": LocationData(3883344, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, MOTOR, COMPUTER],
                                   "Built Air Vent"),
    "Built Cargo Containers": LocationData(3883345, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS, COMPUTER, MOTOR, DISPLAY],
                                           "Built Cargo Containers"),
    "Built Small Conveyor Tube": LocationData(3883346, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS, MOTOR],
                                              "Built Small Conveyor Tube"),
    "Built Large Conveyor Tube": LocationData(3883347, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS, SMALL_TUBE, MOTOR],
                                              "Built Conveyor Junction", location_name="Built Large Conveyor Tube"),
    "Built Connector": LocationData(3883348, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, SMALL_TUBE, MOTOR, COMPUTER],
                                    "Built Inputs/Outputs", location_name="Built Connector"),
    "Built Piston": LocationData(3883349, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, SMALL_TUBE, MOTOR, COMPUTER],
                                 "Built Piston"),
    "Built Rotor": LocationData(3883350, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, SMALL_TUBE, MOTOR, COMPUTER],
                                "Built Rotor"),
    "Built Hinge": LocationData(3883351, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, SMALL_TUBE, MOTOR, COMPUTER],
                                "Built DisplayName_Block_Hinge", location_name="Built Hinge"),
    "Built Medical Blocks": LocationData(3883352, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS, MOTOR, DISPLAY,
                                                   MEDICAL_COMPONENTS, COMPUTER, BULLET_PROOF_GLASS],
                                         "Built Medical Blocks"),
    "Built Refinery": LocationData(3883353, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, MOTOR, COMPUTER], "Built Refinery"),
    "Built O2/H2 Generator": LocationData(3883354, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, LARGE_TUBE, MOTOR, COMPUTER],
                                          "Built O2/H2 Generator"),
    "Built Assembler": LocationData(3883355, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, MOTOR, DISPLAY, COMPUTER],
                                    "Built Assembler"),
    "Built Oxygen Farm": LocationData(3883356, [STEEL_PLATE, BULLET_PROOF_GLASS, LARGE_TUBE, SMALL_TUBE,
                                                CONSTRUCTION_COMPONENTS, COMPUTER], "Built Oxygen Farm"),
    "Built Upgrade Modules": LocationData(3883357, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, SMALL_TUBE, COMPUTER,
                                                    MOTOR], "Built Upgrade Modules"),
    "Built Ion Thrusters": LocationData(3883361, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, LARGE_TUBE,
                                                  THRUSTER_COMPONENTS], "Built Large Ion Thruster",
                                        location_name="Built Ion Thrusters"),
    "Built Hydrogen Thrusters": LocationData(3883362, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, METAL_GRID,
                                                       LARGE_TUBE], "Built Large Hydrogen Thruster",
                                             location_name="Built Hydrogen Thrusters"),
    "Built Atmospheric Thrusters": LocationData(3883363, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, LARGE_TUBE,
                                                          METAL_GRID, MOTOR], "Built Large Atmospheric Thruster",
                                                location_name="Built Atmospheric Thrusters"),
    "Built Ship Tools": LocationData(3883364, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, LARGE_TUBE, MOTOR, COMPUTER],
                                     "Built Ship Tools"),
    "Built Ore Detector": LocationData(3883365, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, MOTOR, COMPUTER,
                                                 DETECTOR_COMPONENTS], "Built Ore Detector"),
    "Built Landing Gear": LocationData(3883366, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, MOTOR], "Built Landing Gear"),
    "Built Jump Drive": LocationData(3883367, [STEEL_PLATE, METAL_GRID, GRAVITY_COMPONENTS, DETECTOR_COMPONENTS,
                                               BATTERY_COMPONENTS, SUPER_CONDUCTOR_COMPONENTS, COMPUTER,
                                               CONSTRUCTION_COMPONENTS], "Built Jump Drive"),
    "Built Parachute Hatch": LocationData(3883368, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, SMALL_TUBE, MOTOR, COMPUTER],
                                          "Built Parachute Hatch"),
    "Built Warhead": LocationData(3883369, [STEEL_PLATE, GIRDER, CONSTRUCTION_COMPONENTS, SMALL_TUBE, COMPUTER,
                                            EXPLOSIVES], "Built Warhead"),
    "Built Decoy": LocationData(3883370, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, COMPUTER, RADIO_COMPONENTS, LARGE_TUBE],
                                "Built Decoy"),
    "Built Turreted Weapons": LocationData(3883371, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS, SMALL_TUBE, MOTOR,
                                                     COMPUTER, STEEL_PLATE], "Built Turreted Weapons"),
    "Built Stationary Weapons": LocationData(3883372, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, METAL_GRID, SMALL_TUBE,
                                                       MOTOR, COMPUTER], "Built Stationary Weapons"),
    "Built Wheels": LocationData(3883375, [STEEL_PLATE, CONSTRUCTION_COMPONENTS, LARGE_TUBE],
                                 "Built Wheels", location_name="Built Wheels"),
    "Built Windows": LocationData(3883376, [INTERIOR_PLATE, CONSTRUCTION_COMPONENTS, SMALL_TUBE], "Built Windows",
                                  location_name="Built Windows"),
    # Ores
    "Stone": LocationData(3883383, [], "Stone", 'Ore', location_name="MyObjectBuilder_Ore:Stone"),
    "Iron": LocationData(3883384, [], "Iron", 'Ore', location_name="MyObjectBuilder_Ore:Iron"),
    "Nickel": LocationData(3883385, [], "Nickel", 'Ore', location_name="MyObjectBuilder_Ore:Nickel"),
    "Cobalt": LocationData(3883386, [], "Cobalt", 'Ore', location_name="MyObjectBuilder_Ore:Cobalt"),
    "Magnesium": LocationData(3883387, [], "Magnesium", 'Ore', location_name="MyObjectBuilder_Ore:Magnesium"),
    "Silicon": LocationData(3883388, [], "Silicon", 'Ore', location_name="MyObjectBuilder_Ore:Silicon"),
    "Silver": LocationData(3883389, [], "Silver", 'Ore', location_name="MyObjectBuilder_Ore:Silver"),
    "Gold": LocationData(3883390, [], "Gold", 'Ore', location_name="MyObjectBuilder_Ore:Gold"),
    "Platinum": LocationData(3883391, [], "Platinum", 'Ore', location_name="MyObjectBuilder_Ore:Platinum"),
    "Uranium": LocationData(3883392, [], "Uranium", 'Ore', location_name="MyObjectBuilder_Ore:Uranium"),
    "Ice": LocationData(3883393, [], "Ice", 'Ore', location_name="MyObjectBuilder_Ore:Ice"),

    # Destinations
    "Visited Earth": LocationData(3883394, [], "Visited Earth", 'Destination'),
    "Visited Moon": LocationData(3883395, [], "Visited Moon", 'Destination'),
    "Visited Mars": LocationData(3883396, [], "Visited Mars", 'Destination'),
    "Visited Europa": LocationData(3883397, [], "Visited Europa", 'Destination'),
    "Visited Alien": LocationData(3883398, [], "Visited Alien", 'Destination'),
    "Visited Titan": LocationData(3883399, [], "Visited Titan", 'Destination'),
    "Visited Pertam": LocationData(3883400, [], "Visited Pertam", 'Destination'),
    "Visited Space": LocationData(3883401, [], "Visited Space", 'Destination'),
    "Visited Triton": LocationData(3883402, [], "Visited Triton", 'Destination'),

    # Construction
    "Assembled Flare Gun": LocationData(3883403, [], "Assembled Flare Gun", 'Construction',
                                        location_name="MyObjectBuilder_PhysicalGunObject:FlareGunItem"),
    "Assembled Flare Gun Clip": LocationData(3883404, [], "Assembled Flare Gun Clip", 'Construction',
                                             location_name="MyObjectBuilder_AmmoMagazine:FlareClip"),
    "Assembled Datapad": LocationData(3883405, [], "Assembled Datapad", 'Construction',
                                      location_name="MyObjectBuilder_Datapad:Datapad"),
    "Assembled Grinder": LocationData(3883406, [], "Assembled Grinder", 'Construction',
                                      location_name="MyObjectBuilder_PhysicalGunObject:AngleGrinderItem"),
    "Assembled Hand Drill": LocationData(3883407, [], "Assembled Hand Drill", 'Construction',
                                         location_name="MyObjectBuilder_PhysicalGunObject:HandDrillItem"),
    "Assembled Welder": LocationData(3883408, [], "Assembled Welder", 'Construction',
                                     location_name="MyObjectBuilder_PhysicalGunObject:WelderItem"),
    "Assembled S-10 Pistol": LocationData(3883409, [], "Assembled S-10 Pistol", 'Construction',
                                          location_name="MyObjectBuilder_PhysicalGunObject:SemiAutoPistolItem"),
    "Assembled S-10 Pistol Magazine": LocationData(3883410, [], "Assembled S-10 Pistol Magazine", 'Construction',
                                                   location_name="MyObjectBuilder_AmmoMagazine:SemiAutoPistolMagazine"),
    "Assembled Fireworks": LocationData(3883411, [], "Assembled Fireworks", 'Construction'),
    # Bottles are filler items.
    # "Assembled Oxygen Bottle": LocationData(3883412, [], "Assembled Oxygen Bottle", 'Construction',
    #                                         location_name="MyObjectBuilder_OxygenContainerObject:OxygenBottle"),
    # "Assembled Hydrogen Bottle": LocationData(3883413, [], "Assembled Hydrogen Bottle", 'Construction',
    #                                           location_name="MyObjectBuilder_GasContainerObject:HydrogenBottle"),
    "Assembled Enhanced Grinder": LocationData(3883414, [], "Assembled Enhanced Grinder", 'Construction',
                                               location_name="MyObjectBuilder_PhysicalGunObject:AngleGrinder2Item"),
    "Assembled Proficient Grinder": LocationData(3883415, [], "Assembled Proficient Grinder", 'Construction',
                                                 location_name="MyObjectBuilder_PhysicalGunObject:AngleGrinder3Item"),
    "Assembled Elite Grinder": LocationData(3883416, [], "Assembled Elite Grinder", 'Construction',
                                            location_name="MyObjectBuilder_PhysicalGunObject:AngleGrinder4Item"),
    "Assembled Enhanced Welder": LocationData(3883417, [], "Assembled Enhanced Welder", 'Construction',
                                              location_name="MyObjectBuilder_PhysicalGunObject:Welder2Item"),
    "Assembled Proficient Welder": LocationData(3883418, [], "Assembled Proficient Welder", 'Construction',
                                                location_name="MyObjectBuilder_PhysicalGunObject:Welder3Item"),
    "Assembled Elite Welder": LocationData(3883419, [], "Assembled Elite Welder", 'Construction',
                                           location_name="MyObjectBuilder_PhysicalGunObject:Welder4Item"),
    "Assembled Enhanced Hand Drill": LocationData(3883420, [], "Assembled Enhanced Hand Drill", 'Construction',
                                                  location_name="MyObjectBuilder_PhysicalGunObject:HandDrill2Item"),
    "Assembled Proficient Hand Drill": LocationData(3883421, [], "Assembled Proficient Hand Drill", 'Construction',
                                                    location_name="MyObjectBuilder_PhysicalGunObject:HandDrill3Item"),
    "Assembled Elite Hand Drill": LocationData(3883422, [], "Assembled Elite Hand Drill", 'Construction',
                                               location_name="MyObjectBuilder_PhysicalGunObject:HandDrill4Item"),
    "Assembled S-20A Pistol": LocationData(3883423, [], "Assembled S-20A Pistol", 'Construction',
                                           location_name="MyObjectBuilder_PhysicalGunObject:FullAutoPistolItem"),
    "Assembled S-10E Pistol": LocationData(3883424, [], "Assembled S-10E Pistol", 'Construction',
                                           location_name="MyObjectBuilder_PhysicalGunObject:ElitePistolItem"),
    "Assembled MR-20 Rifle": LocationData(3883425, [], "Assembled MR-20 Rifle", 'Construction',
                                          location_name="MyObjectBuilder_PhysicalGunObject:AutomaticRifleItem"),
    "Assembled MR-50A Rifle": LocationData(3883426, [], "Assembled MR-50A Rifle", 'Construction',
                                           location_name="MyObjectBuilder_PhysicalGunObject:RapidFireAutomaticRifleItem"),
    "Assembled MR-8P Rifle": LocationData(3883427, [], "Assembled MR-8P Rifle", 'Construction',
                                          location_name="MyObjectBuilder_PhysicalGunObject:PreciseAutomaticRifleItem"),
    "Assembled MR-30E Rifle": LocationData(3883428, [], "Assembled MR-30E Rifle", 'Construction',
                                           location_name="MyObjectBuilder_PhysicalGunObject:UltimateAutomaticRifleItem"),
    "Assembled RO-1 Rocket Launcher": LocationData(3883429, [], "Assembled RO-1 Rocket Launcher", 'Construction',
                                                   location_name="MyObjectBuilder_PhysicalGunObject:BasicHandHeldLauncherItem"),
    "Assembled PRO-1 Rocket Launcher": LocationData(3883430, [], "Assembled PRO-1 Rocket Launcher", 'Construction',
                                                    location_name="MyObjectBuilder_PhysicalGunObject:AdvancedHandHeldLauncherItem"),
    "Assembled S-20A Pistol Magazine": LocationData(3883431, [], "Assembled S-20A Pistol Magazine", 'Construction',
                                                    location_name="MyObjectBuilder_AmmoMagazine:FullAutoPistolMagazine"),
    "Assembled S-10E Pistol Magazine": LocationData(3883432, [], "Assembled S-10E Pistol Magazine", 'Construction',
                                                    location_name="MyObjectBuilder_AmmoMagazine:ElitePistolMagazine"),
    "Assembled MR-20 Rifle Magazine": LocationData(3883433, [], "Assembled MR-20 Rifle Magazine", 'Construction',
                                                   location_name="MyObjectBuilder_AmmoMagazine:AutomaticRifleGun_Mag_20rd"),
    "Assembled MR-50A Rifle Magazine": LocationData(3883434, [], "Assembled MR-50A Rifle Magazine", 'Construction',
                                                    location_name="MyObjectBuilder_AmmoMagazine:RapidFireAutomaticRifleGun_Mag_50rd"),
    "Assembled MR-8P Rifle Magazine": LocationData(3883435, [], "Assembled MR-8P Rifle Magazine", 'Construction',
                                                   location_name="MyObjectBuilder_AmmoMagazine:PreciseAutomaticRifleGun_Mag_5rd"),
    "Assembled MR-30E Rifle Magazine": LocationData(3883436, [], "Assembled MR-30E Rifle Magazine", 'Construction',
                                                    location_name="MyObjectBuilder_AmmoMagazine:UltimateAutomaticRifleGun_Mag_30rd"),
    "Assembled Gatling Ammo Box": LocationData(3883437, [], "Assembled Gatling Ammo Box", 'Construction',
                                               location_name="MyObjectBuilder_AmmoMagazine:NATO_25x184mm"),
    "Assembled Autocannon Magazine": LocationData(3883438, [], "Assembled Autocannon Magazine", 'Construction',
                                                  location_name="MyObjectBuilder_AmmoMagazine:AutocannonClip"),
    "Assembled Assault Cannon Shell": LocationData(3883439, [], "Assembled Assault Cannon Shell", 'Construction',
                                                   location_name="MyObjectBuilder_AmmoMagazine:MediumCalibreAmmo"),
    "Assembled Artillery Shell": LocationData(3883440, [], "Assembled Artillery Shell", 'Construction',
                                              location_name="MyObjectBuilder_AmmoMagazine:LargeCalibreAmmo"),
    "Assembled Small Railgun Sabot": LocationData(3883441, [], "Assembled Small Railgun Sabot", 'Construction',
                                                  location_name="MyObjectBuilder_AmmoMagazine:SmallRailgunAmmo"),
    "Assembled Large Railgun Sabot": LocationData(3883442, [], "Assembled Large Railgun Sabot", 'Construction',
                                                  location_name="MyObjectBuilder_AmmoMagazine:LargeRailgunAmmo"),
    "Assembled Rocket": LocationData(3883443, [], "Assembled Rocket", 'Construction',
                                     location_name="MyObjectBuilder_AmmoMagazine:Missile200mm"),
    'Space Engineers: Victory': None
}

location_name_id: {str, int} = {}
location_id_name: {int, str} = {}
for location_name, location_data in location_table.items():
    if location_data is not None:
        location_name_id[location_name] = location_data.location_id
        location_id_name[location_data.location_id] = location_name

location_name_id['Space Engineers: Victory'] = None
