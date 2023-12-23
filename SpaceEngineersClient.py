from __future__ import annotations

import atexit
import os
import re
import sys
import asyncio
import random
import shutil
from typing import Tuple, List, Iterable, Dict, TextIO

from worlds.space_engineers import SpaceEngineersWorld
from worlds.space_engineers.Items import item_table, item_table_ids, ItemData
from worlds.space_engineers.Locations import location_id_name, location_name_id
from worlds.space_engineers.Options import *

import ModuleUpdate

ModuleUpdate.update()

import Utils
import json
import logging

if __name__ == "__main__":
    Utils.init_logging("SpaceEngineersClient", exception_logger="Client")

from NetUtils import NetworkItem, ClientStatus
from CommonClient import gui_enabled, logger, get_base_parser, ClientCommandProcessor, \
    CommonContext, server_loop

se_logger = logging.getLogger("SpaceEngineers")


class SpaceEngineersClientCommandProcessor(ClientCommandProcessor):
    def _cmd_resync(self):
        """Manually trigger a resync."""
        self.output(f"Syncing items.")
        self.ctx.syncing = True


def write_settings_file(file: TextIO, slot_data: dict):
    file_contents = ""
    for option, value in slot_data.items():
        file_contents += f"{option}:{value}\n"
    file.write(file_contents)


class SpaceEngineersContext(CommonContext):
    command_processor: int = SpaceEngineersClientCommandProcessor
    game = "Space Engineers"
    items_handling = 0b111  # full remote
    ap_settings_file = "APSettings.txt"
    items_file = "ArchipelagoMultiworldItems.txt"
    goal = Goal.default
    starting_planet_choice = StartingPlanetChoice.default
    second_world_size = WorldSize2Distance.default
    third_world_size = WorldSize3Distance.default
    earth_like_distance = EarthLikeDistance.default
    moon_distance = MoonDistance.default
    mars_distance = MarsDistance.default
    europa_distance = EuropaDistance.default
    alien_planet_distance = AlienDistance.default
    titan_distance = TitanDistance.default
    pertam_distance = PertamDistance.default
    triton_distance = TritonDistance.default
    earth_like_size = EarthLikeSize.default
    moon_size = MoonSize.default
    mars_size = MarsSize.default
    europa_size = EuropaSize.default
    alien_planet_size = AlienSize.default
    titan_size = TitanSize.default
    pertam_size = PertamSize.default
    triton_size = TritonSize.default
    character_inventory_size = CharacterInventorySize.default
    block_inventory_size = BlockInventorySize.default
    assembler_speed = AssemblerSpeed.default
    assembler_efficiency = AssemblerEfficiency.default
    refinery_speed = RefinerySpeed.default
    welding_speed = WeldingSpeed.default
    grinding_speed = GrindingSpeed.default
    item_names_to_se_names = {name: item.se_item_name for name, item in item_table.items()}

    def __init__(self, server_address, password):
        super(SpaceEngineersContext, self).__init__(server_address, password)
        self.send_index: int = 0
        self.syncing = False
        self.awaiting_bridge = False
        self.game_communication_path = ""
        self.se_saves_directory = ""
        self.save_directory = ""
        # self.game_communication_path: files go in this path to pass data between us and the actual game
        if "appdata" in os.environ:
            save_directory = os.path.join("lib", "worlds", "space_engineers", "data", "save")
            dev_save_directory = os.path.join("worlds", "space_engineers", "data", "save")
            appdata_se = os.path.expandvars(os.path.join("%APPDATA%", "SpaceEngineers"))
            if not os.path.isdir(appdata_se):
                print_error_and_close("SpaceEngineersClient couldn't find SpaceEngineers in appdata!"
                                      "Boot Space Engineers and then close it to attempt to fix this error")
            if not os.path.isdir(save_directory):
                save_directory = dev_save_directory
            if not os.path.isdir(save_directory):
                print_error_and_close("SpaceEngineersClient couldn't find the Space Engineers save files in install!")
            self.game_communication_path = os.path.join(appdata_se, "Storage")
            self.remove_communication_files()
            atexit.register(self.remove_communication_files)
            self.se_saves_directory = os.path.join(appdata_se, "Saves")
            self.save_directory = save_directory
        else:
            print_error_and_close("SpaceEngineersClient couldn't detect system type. "
                                  "Unable to infer required game_communication_path")

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(SpaceEngineersContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    async def connection_closed(self):
        await super(SpaceEngineersContext, self).connection_closed()
        self.remove_communication_files()
        self.checked_locations.clear()
        self.server_locations.clear()
        self.finished_game = False

    @property
    def endpoints(self):
        if self.server:
            return [self.server]
        else:
            return []

    async def shutdown(self):
        await super(SpaceEngineersContext, self).shutdown()
        self.remove_communication_files()
        self.checked_locations.clear()
        self.server_locations.clear()
        self.finished_game = False

    def remove_communication_files(self):
        #
        settings = os.path.join(self.game_communication_path, self.ap_settings_file)
        items = os.path.join(self.game_communication_path, self.items_file)
        victory = os.path.join(self.game_communication_path, "apVictory")
        if os.path.isfile(settings):
            os.remove(settings)
        if os.path.isfile(items):
            os.remove(items)
        if os.path.isfile(victory):
            os.remove(victory)
        for root, dirs, files in os.walk(self.game_communication_path):
            for file in files:
                if file.startswith("apSend"):
                    os.remove(os.path.join(root, file))

    def write_locations_files(self):
        for id in self.checked_locations:
            with open(os.path.join(self.game_communication_path, f"apSend{id}"), 'w') as f:
                pass

    def write_items_file(self, file: TextIO):
        file_contents = ""
        item_codes_received = [item.item for item in self.items_received]
        for id, data in item_table_ids.items():
            num_items = item_codes_received.count(id)
            if id is not None:
                file_contents += f"{data.se_item_name}::{id}:true:{num_items}\n"
        file.write(file_contents)

    def apply_world_settings(self, save_path: str, save_name: str):
        sandbox_path = os.path.join(save_path, "Sandbox.sbc")
        sandbox_config_path = os.path.join(save_path, "Sandbox_config.sbc")
        with open(sandbox_path, "r+") as sandbox_file:
            text = sandbox_file.read()
            text = self.apply_world_settings_to_file(text, save_name)
        with open(sandbox_path, "w") as sandbox_file:
            sandbox_file.write(text)
        with open(sandbox_config_path, "r+") as sandbox_config_file:
            text = sandbox_config_file.read()
            text = self.apply_world_settings_to_file(text, save_name)
        with open(sandbox_config_path, "w") as sandbox_config_file:
            sandbox_config_file.write(text)

    def apply_world_settings_to_file(self, text: str, save_name: str):
        match = re.search("<InventorySizeMultiplier>[0-9]+</InventorySizeMultiplier>", text)
        text = text[:match.start()] + \
               f"<InventorySizeMultiplier>{self.character_inventory_size}</InventorySizeMultiplier>" + \
               text[match.end():]
        match = re.search("<BlocksInventorySizeMultiplier>[0-9]+</BlocksInventorySizeMultiplier>", text)
        text = text[:match.start()] + \
               f"<BlocksInventorySizeMultiplier>{self.block_inventory_size}</BlocksInventorySizeMultiplier>" + \
               text[match.end():]
        match = re.search("<AssemblerSpeedMultiplier>[0-9]+</AssemblerSpeedMultiplier>", text)
        text = text[:match.start()] + \
               f"<AssemblerSpeedMultiplier>{self.assembler_speed}</AssemblerSpeedMultiplier>" + \
               text[match.end():]
        match = re.search("<AssemblerEfficiencyMultiplier>[0-9]+</AssemblerEfficiencyMultiplier>", text)
        text = text[:match.start()] + \
               f"<AssemblerEfficiencyMultiplier>{self.assembler_efficiency}</AssemblerEfficiencyMultiplier>" + \
               text[match.end():]
        match = re.search("<RefinerySpeedMultiplier>[0-9]+</RefinerySpeedMultiplier>", text)
        text = text[:match.start()] + \
               f"<RefinerySpeedMultiplier>{self.refinery_speed}</RefinerySpeedMultiplier>" + \
               text[match.end():]
        match = re.search("<WelderSpeedMultiplier>[0-9]+</WelderSpeedMultiplier>", text)
        text = text[:match.start()] + \
               f"<WelderSpeedMultiplier>{self.welding_speed}</WelderSpeedMultiplier>" + \
               text[match.end():]
        match = re.search("<GrinderSpeedMultiplier>[0-9]+</GrinderSpeedMultiplier>", text)
        text = text[:match.start()] + \
               f"<GrinderSpeedMultiplier>{self.grinding_speed}</GrinderSpeedMultiplier>" + \
               text[match.end():]
        match = re.search("<SessionName>AP-TEMPLATE</SessionName>", text)
        text = text[:match.start()] + \
               f"<SessionName>{save_name}</SessionName>" + \
               text[match.end():]
        return text

    def on_package(self, cmd: str, args: dict):
        if cmd in {"Connected"}:
            ap_save_name = f"AP-{self.slot}-{args['slot_data']['seed']}"
            with open(os.path.join(self.game_communication_path, self.ap_settings_file), 'w') as f:
                slot_data = args["slot_data"]
                write_settings_file(f, slot_data)
                self.goal = slot_data["goal"]
                self.starting_planet_choice = slot_data["starting_planet_choice"]
                self.second_world_size = slot_data["second_world_size"]
                self.third_world_size = slot_data["third_world_size"]
                self.earth_like_distance = slot_data["earth_like_distance"]
                self.moon_distance = slot_data["moon_distance"]
                self.mars_distance = slot_data["mars_distance"]
                self.europa_distance = slot_data["europa_distance"]
                self.alien_planet_distance = slot_data["alien_planet_distance"]
                self.titan_distance = slot_data["titan_distance"]
                self.pertam_distance = slot_data["pertam_distance"]
                self.triton_distance = slot_data["triton_distance"]
                self.earth_like_size = slot_data["earth_like_size"]
                self.moon_size = slot_data["moon_size"]
                self.mars_size = slot_data["mars_size"]
                self.europa_size = slot_data["europa_size"]
                self.alien_planet_size = slot_data["alien_planet_size"]
                self.titan_size = slot_data["titan_size"]
                self.pertam_size = slot_data["pertam_size"]
                self.triton_size = slot_data["triton_size"]
                self.character_inventory_size = slot_data["character_inventory_size"]
                self.block_inventory_size = slot_data["block_inventory_size"]
                self.assembler_speed = slot_data["assembler_speed"]
                self.assembler_efficiency = slot_data["assembler_efficiency"]
                self.refinery_speed = slot_data["refinery_speed"]
                self.welding_speed = slot_data["welding_speed"]
                self.grinding_speed = slot_data["grinding_speed"]
            self.write_locations_files()
            with open(os.path.join(self.game_communication_path, self.items_file), 'w') as file:
                self.write_items_file(file)
            # self.ui.update_tracker()

            random.seed(self.seed_name + str(self.slot))
            for directory in os.listdir(self.se_saves_directory):
                ap_save_path = os.path.join(self.se_saves_directory, directory, ap_save_name)
                if not os.path.exists(ap_save_path):
                    shutil.copytree(self.save_directory, os.path.join(self.se_saves_directory, directory),
                                    dirs_exist_ok=True)
                    os.rename(os.path.join(self.se_saves_directory, directory, "AP-TEMPLATE"),
                              os.path.join(ap_save_path))
                    self.apply_world_settings(ap_save_path, ap_save_name)

        if cmd in {"RoomInfo"}:
            self.seed_name = args["seed_name"]

        if cmd in {"ReceivedItems"}:
            path = os.path.join(self.game_communication_path, self.items_file)
            with open(path, 'w') as file:
                self.write_items_file(file)
            # self.ui.update_tracker()

        if cmd in {"RoomUpdate"}:
            self.write_locations_files()

    def run_gui(self):
        """Import kivy UI system and start running it as self.ui_task."""
        from kvui import GameManager, HoverBehavior, ServerToolTip
        from kivy.uix.tabbedpanel import TabbedPanelItem
        from kivy.lang import Builder
        from kivy.uix.button import Button
        from kivy.uix.togglebutton import ToggleButton
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.image import AsyncImage, Image
        from kivy.uix.stacklayout import StackLayout
        from kivy.uix.label import Label
        from kivy.properties import ColorProperty
        from kivy.uix.image import Image
        import pkgutil

        class TrackerLayout(BoxLayout):
            pass

        class CommanderSelect(BoxLayout):
            pass

        class CommanderButton(ToggleButton):
            pass

        class FactionBox(BoxLayout):
            pass

        class CommanderGroup(BoxLayout):
            pass

        class ItemTracker(BoxLayout):
            pass

        class ItemLabel(Label):
            pass

        class SpaceEngineersManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago"),
                ("SE", "SE Console"),
            ]
            base_title = "Archipelago Space Engineers Client"
            ctx: SpaceEngineersContext

            def build(self):
                container = super().build()
                panel = TabbedPanelItem(text="Space Engineers")
                panel.content = self.build_tracker()
                self.tabs.add_widget(panel)
                return container

            def build_tracker(self):
                pass

        self.ui = SpaceEngineersManager(self)
        # data = pkgutil.get_data(SpaceEngineersWorld.__module__, "Wargroove.kv").decode()
        # Builder.load_string(data)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


async def game_watcher(ctx: SpaceEngineersContext):
    from worlds.wargroove.Locations import location_table
    while not ctx.exit_event.is_set():
        if ctx.syncing == True:
            sync_msg = [{'cmd': 'Sync'}]
            if ctx.locations_checked:
                sync_msg.append({"cmd": "LocationChecks", "locations": list(ctx.locations_checked)})
            await ctx.send_msgs(sync_msg)
            ctx.syncing = False
        sending = []
        victory = False
        for root, dirs, files in os.walk(ctx.game_communication_path):
            for file in files:
                if file.find("apSend") > -1:
                    st = file.split("apSend", -1)[1]
                    sending = sending + [(int(st))]
                if file.find("apVictory") > -1:
                    victory = True
        ctx.locations_checked = sending
        message = [{"cmd": 'LocationChecks', "locations": sending}]
        await ctx.send_msgs(message)
        if not ctx.finished_game and victory:
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True
        await asyncio.sleep(0.1)


def print_error_and_close(msg):
    logger.error("Error: " + msg)
    Utils.messagebox("Error", msg, error=True)
    sys.exit(1)


if __name__ == '__main__':
    async def main(args):
        ctx = SpaceEngineersContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        progression_watcher = asyncio.create_task(
            game_watcher(ctx), name="SpaceEngineersProgressionWatcher")

        await ctx.exit_event.wait()
        ctx.server_address = None

        await progression_watcher

        await ctx.shutdown()


    import colorama

    parser = get_base_parser(description="Space Engineers Client, for text interfacing.")

    args, rest = parser.parse_known_args()
    colorama.init()
    asyncio.run(main(args))
    colorama.deinit()
