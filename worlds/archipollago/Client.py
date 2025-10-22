import asyncio
import logging
import random
import time
from random import Random
from typing import Any, Optional

from twitchAPI.chat import Chat, EventData, ChatCommand  # type: ignore
from twitchAPI.helper import first
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.object.api import Poll, TwitchUser
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope, PollStatus, TwitchAPIException, UnauthorizedException, MissingScopeException, \
    TwitchAuthorizationException, TwitchBackendException, ChatEvent

import Utils
from CommonClient import server_loop, CommonContext, get_base_parser, gui_enabled
from NetUtils import NetworkItem, ClientStatus
from . import ArchipollagoWorld
from .Items import item_table

if __name__ == "__main__":
    Utils.init_logging("ArchipollagoClient", exception_logger="Client")

apoll_logger = logging.getLogger("APollago")


class ArchipollagoContext(CommonContext):
    game = "Archipollago"
    items_handling = 0b111  # full remote
    twitch_bot_running: bool = False

    slot_data = []
    poll_keys: int
    locations_per_key: int
    time_between_polls: int
    minor_time_skip: int
    major_time_skip: int
    minor_major_ratio: int
    poll_length: int
    channel_point_voting: bool
    free_channel_points_per_vote: int
    number_of_choices: int
    goal: int

    random: Random = Random()
    time_til_next_poll: float = -1
    finished_game: bool = False
    victory: bool = False

    twitch_username_text: str = ""
    app_id_text: str = ""
    app_secret_text: str = ""

    chat_votes: dict[int, set[str]] = {1: set(), 2: set(), 3: set(), 4: set(), 5: set(), }
    chat_voters: set[str] = set()

    def __init__(self, server_address: Optional[str] = None, password: Optional[str] = None):
        super().__init__(server_address, password)

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(ArchipollagoContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect(game=self.game)

    def on_package(self, cmd: str, args: dict):
        if cmd in {"Connected"}:
            self.victory = False
            self.finished_game = False
            self.slot_data = args["slot_data"]
            self.poll_keys = self.slot_data.get("poll_keys", 1)
            self.locations_per_key = self.slot_data.get("locations_per_key", 3)
            self.time_between_polls = self.slot_data.get("time_between_polls", 0)
            self.minor_time_skip = self.slot_data.get("minor_time_skip", 0)
            self.major_time_skip = self.slot_data.get("major_time_skip", 0)
            self.minor_major_ratio = self.slot_data.get("minor_major_ratio", 0)
            self.poll_length = self.slot_data.get("poll_length", 60)
            self.channel_point_voting = self.slot_data.get("channel_point_voting", False)
            self.free_channel_points_per_vote = self.slot_data.get("free_channel_points_per_vote", 0)
            self.number_of_choices = self.slot_data.get("number_of_choices", 0)
            self.goal = self.slot_data.get("goal", 0)

            self.time_til_next_poll = time.time() + self.time_between_polls
            self.check_victory()

        elif cmd == "LocationInfo":
            for item in [NetworkItem(*item) for item in args["locations"]]:
                self.locations_info[item.location] = item
        elif cmd in {"ReceivedItems"}:
            for item in args['items']:
                network_item = NetworkItem(*item)
                if network_item.item == item_table["Major Time Skip"].code:
                    self.time_til_next_poll -= self.major_time_skip
                if network_item.item == item_table["Minor Time Skip"].code:
                    self.time_til_next_poll -= self.minor_time_skip
            self.check_victory()

    def check_victory(self):
        victory_items_count = 0
        for recieved_item in self.items_received:
            if recieved_item.item == item_table["Letter R"].code:
                victory_items_count += 1
            if recieved_item.item == item_table["Letter C"].code:
                victory_items_count += 1
            if recieved_item.item == item_table["Letter H"].code:
                victory_items_count += 1
            if recieved_item.item == item_table["Letter I"].code:
                victory_items_count += 1
            if recieved_item.item == item_table["Letter P"].code:
                victory_items_count += 1
            if recieved_item.item == item_table["Letter O"].code:
                victory_items_count += 1
            if recieved_item.item == item_table["Letter L"].code:
                victory_items_count += 1
            if recieved_item.item == item_table["Letter A"].code:
                victory_items_count += 1
            if recieved_item.item == item_table["Letter G"].code:
                victory_items_count += 1

        if self.goal == 0 and victory_items_count >= 7:
            apoll_logger.info("Goal Reached (POLLAGO)!")
            self.victory = True
        elif self.goal == 1 and victory_items_count >= 12:
            apoll_logger.info("Goal Reached (ARCHIPOLLAGO)!")
            self.victory = True

    async def disconnect(self, allow_autoreconnect: bool = False):
        self.stop_bot()
        await super().disconnect(allow_autoreconnect)

    def stop_bot(self):
        apoll_logger.info("Stopping Twitch Bot (May wait until the current poll is done)")
        self.twitch_bot_running = False
        self.twitch_username_text = ""
        self.app_id_text = ""
        self.app_secret_text = ""

    def run_gui(self):
        """Import kivy UI system and start running it as self.ui_task."""
        from kvui import GameManager
        from kivy.uix.button import Button
        from kivymd.uix.tab import MDTabsItem, MDTabsItemText
        from kivy.lang import Builder
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.textinput import TextInput
        import pkgutil

        class LoginLayout(BoxLayout):
            pass

        class TwitchUserName(TextInput):
            pass

        class AppSecret(TextInput):
            pass

        class AppID(TextInput):
            pass

        class AppStart(Button):
            pass

        class AppStop(Button):
            pass

        class TwitchUserNameLabel(Label):
            pass

        class AppSecretLabel(Label):
            pass

        class AppIDLabel(Label):
            pass

        class ArchipollagoManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago"),
                ("APollago", "APollago Console"),
            ]
            base_title = "Archipelago Archipollago Client"
            ctx: ArchipollagoContext
            twitch_username: TwitchUserName
            app_id: AppID
            app_secret: AppSecret

            def build(self):
                container = super().build()
                self.add_client_tab("Archipollago Settings", self.build_login())
                return container

            def build_login(self) -> LoginLayout:
                try:
                    login_layout = LoginLayout(orientation="vertical")
                    login_layout.add_widget(TwitchUserNameLabel(text="Twitch Username"))
                    self.twitch_username = TwitchUserName()
                    login_layout.add_widget(self.twitch_username)
                    login_layout.add_widget(AppIDLabel(text="Twitch Application ID"))
                    self.app_id = AppID()
                    login_layout.add_widget(self.app_id)
                    login_layout.add_widget(AppSecretLabel(text="Twitch Application Secret"))
                    self.app_secret = AppSecret()
                    login_layout.add_widget(self.app_secret)
                    app_start = AppStart()
                    app_start.bind(on_press=lambda instance: self.start_bot())
                    login_layout.add_widget(app_start)
                    app_stop = AppStop()
                    app_stop.bind(on_press=lambda instance: self.ctx.stop_bot())
                    login_layout.add_widget(app_stop)
                    self.update_login_tab()
                    return login_layout
                except Exception as e:
                    print(e)

            def start_bot(self):
                apoll_logger.info("Starting Twitch Bot")
                self.ctx.twitch_bot_running = True
                self.ctx.twitch_username_text = self.twitch_username.text
                self.ctx.app_id_text = self.app_id.text
                self.ctx.app_secret_text = self.app_secret.text

            def update_login_tab(self):
                pass

        self.ui = ArchipollagoManager(self)
        data = pkgutil.get_data(ArchipollagoWorld.__module__, "Archipollago.kv").decode()
        Builder.load_string(data)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


async def twitch_loop(ctx: ArchipollagoContext):
    target_scope = [AuthScope.CHANNEL_MANAGE_POLLS, AuthScope.CHANNEL_READ_POLLS,
                    AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
    twitch = None
    while not ctx.exit_event.is_set():
        try:
            if ctx.twitch_bot_running and ctx.server and ctx.server.socket:
                if twitch is None:
                    await ctx.send_msgs([{"cmd": "LocationScouts", "locations": list(range(1, ctx.total_locations + 1)),
                                          "create_as_hint": 0}])
                    try:
                        twitch = await Twitch(ctx.app_id_text, ctx.app_secret_text, target_app_auth_scope=target_scope)
                        auth = UserAuthenticator(twitch, target_scope, force_verify=False)
                        token, refresh_token = await auth.authenticate()
                        await twitch.set_user_authentication(token, target_scope, refresh_token)
                        twitch_user = await first(twitch.get_users(logins=ctx.twitch_username_text))
                    except (TwitchAPIException, UnauthorizedException,
                            MissingScopeException, TwitchAuthorizationException,
                            TwitchBackendException, ValueError):
                        ctx.stop_bot()
                        continue
                    if twitch_user is None:
                        ctx.stop_bot()
                        await twitch.close()
                        continue
                if ctx.time_til_next_poll < time.time() and len(ctx.missing_locations) > 0:
                    number_of_keys = 0
                    for item in ctx.items_received:
                        if item.item == item_table["Progressive Poll Key"].code:
                            number_of_keys += 1
                    total_available_locations = set(range(1,
                                                          number_of_keys * ctx.locations_per_key + ctx.locations_per_key + 1))
                    available_locations = total_available_locations.intersection(ctx.missing_locations)
                    number_of_choices = ctx.number_of_choices
                    if len(available_locations) < ctx.number_of_choices:
                        number_of_choices = len(available_locations)
                    location_choices = random.choices(list(available_locations), k=number_of_choices)
                    item_choices = [(ctx.locations_info[location_choice], location_choice)
                                    for location_choice in location_choices]
                    choices = [f"{index + 1}. " \
                               f"{ctx.item_names.lookup_in_game(item_choice[0].item, ctx.slot_info[item_choice[0].player].game)[:20]}"
                               for index, item_choice in enumerate(item_choices)]
                    await create_twitch_poll(ctx, choices, item_choices, twitch, twitch_user)
                    await twitch.close()
                    ctx.time_til_next_poll = time.time() + ctx.time_between_polls
            else:
                twitch = None
                ctx.time_til_next_poll = 0
            if not ctx.finished_game and ctx.victory:
                await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                ctx.finished_game = True
            await asyncio.sleep(1.0)
        except Exception as err:
            apoll_logger.warning("Exception in twitch thread, the client may need to be restarted: " + str(err))
            await asyncio.sleep(1.0)


async def create_text_poll(ctx: ArchipollagoContext, choices: list[str], item_choices: list[tuple[NetworkItem, Any]],
                           twitch: Twitch):
    async def on_chat_bot_ready(ready_event: EventData):
        await ready_event.chat.join_room(ctx.twitch_username_text)
        await ready_event.chat.send_message(ctx.twitch_username_text, f"An Archipollago Poll has started and "
                                                                      f"will last for {ctx.poll_length} seconds!")
        await ready_event.chat.send_message(
            ctx.twitch_username_text,
            "Use the !ap <number> command to vote for an item to send the multiworld.")
        for choice in choices:
            await ready_event.chat.send_message(ctx.twitch_username_text, choice)

    async def ap_chat_bot_command(cmd: ChatCommand):
        if len(cmd.parameter) == 1:
            try:
                vote = int(cmd.parameter.strip())
                if 0 < vote <= ctx.number_of_choices and cmd.user.id not in ctx.chat_voters:
                    ctx.chat_votes[vote].add(cmd.user.id)
                    ctx.chat_voters.add(cmd.user.id)
            except ValueError:
                pass

    poll_end_time = time.time() + ctx.poll_length
    chat = await Chat(twitch)
    chat.register_event(ChatEvent.READY, on_chat_bot_ready)
    chat.register_command("ap", ap_chat_bot_command)
    chat.start()
    while ctx.twitch_bot_running and poll_end_time > time.time():
        await asyncio.sleep(1.0)

    winning_option = 1
    highest_number_of_votes = 0
    for i in range(1, ctx.number_of_choices + 1):
        votes = len(ctx.chat_votes[i])
        if votes > highest_number_of_votes:
            highest_number_of_votes = votes
            winning_option = i
    ctx.chat_votes = {1: set(), 2: set(), 3: set(), 4: set(), 5: set()}
    ctx.chat_voters = set()
    await chat.send_message(ctx.twitch_username_text, f"{choices[winning_option - 1]} will be sent to the multiworld!")
    chat.stop()
    try:
        item = item_choices[winning_option - 1]
        message = [{"cmd": 'LocationChecks', "locations": [item[1]]}]
        await ctx.send_msgs(message)
    except ValueError:
        pass


async def create_twitch_poll(ctx: ArchipollagoContext, choices: list[str], item_choices: list[tuple[NetworkItem, Any]],
                             twitch: Twitch, twitch_user: TwitchUser):
    if len(item_choices) == 0:
        return
    if len(item_choices) == 1:
        message = [{"cmd": 'LocationChecks', "locations": [item_choices[0][1]]}]
        await ctx.send_msgs(message)
    try:
        poll: Poll = await twitch.create_poll(twitch_user.id, "Vote for an item to send!", choices, ctx.poll_length,
                                              ctx.channel_point_voting, ctx.free_channel_points_per_vote)
    except Exception as e:
        # twitch.create_poll has thrown some undocumented exceptions, let's catch them here.
        await create_text_poll(ctx, choices, item_choices, twitch)
        return
    while ctx.twitch_bot_running and poll is not None and poll.status.value == PollStatus.ACTIVE.value:
        try:
            poll = await first(twitch.get_polls(twitch_user.id, poll.id, first=1))
        except Exception as e:
            logging.error(f"Unable to get poll {e}")
        await asyncio.sleep(1.0)
    if poll is not None and poll.status.value == PollStatus.COMPLETED.value:
        highest_choice = poll.choices[0]
        for choice in poll.choices:
            if highest_choice.votes < choice.votes:
                highest_choice = choice
        try:
            choice_id = int(highest_choice.title[0]) - 1
            item = item_choices[choice_id]
            message = [{"cmd": 'LocationChecks', "locations": [item[1]]}]
            await ctx.send_msgs(message)
        except ValueError:
            pass
    else:
        if poll is None:
            apoll_logger.error("Poll is None type!")
        else:
            apoll_logger.warning(f"Poll ended with status {poll.status.value}")


def launch(*launch_args: str):
    async def main(args):
        ctx = ArchipollagoContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        ctx.twitch_task = asyncio.create_task(twitch_loop(ctx), name="twitch loop")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()
        await ctx.twitch_task
        await ctx.shutdown()

    import colorama

    parser = get_base_parser(description="Archipollago Client, for text interfacing.")

    colorama.just_fix_windows_console()
    asyncio.run(main(parser.parse_args(launch_args)))
    colorama.deinit()
