import discord
from multiprocessing.connection import Listener
import re
import sched
from time import sleep
from threading import Thread
import traceback

import scrim_finder.nasc_bot.bot_settings as bot_settings

from scrim_finder.api.codes import SystemCodes, UserCodes
from scrim_finder.api.queue_objects import INTER_PROCESS_AUTH_KEY, Scrim
from scrim_finder.db import ScrimFinderDB
from scrim_finder.nasc_bot.command import CommandParser

class NASCBot(discord.Client):

    # =========== External Utilities =========== #
    def spawn_listener(self):
        self.__thread__ = Thread(target=self._on_queue_receive)
        self.__thread__.daemon = True
        self.__thread__.start()

    # =========== Bot Hooks =========== #
    def _on_queue_receive(self):
        """ A special method spawned in a different thread.
            This method will fire whenever the multiprocessing
            Listener gets a new message.
        """

        # Sleep to ensure no race conditions where we spawn a listener while
        # the other listener is still spinning down.
        sleep(.1)

        listener = Listener(('localhost', 34365), authkey=INTER_PROCESS_AUTH_KEY)
        listener_connection = listener.accept()

        print("New listener was created on NASC Bot.")

        try:
            response_code = SystemCodes.Good
            queue_message = listener_connection.recv()
            print(f"Received a message on the queue: {queue_message}")

            if isinstance(queue_message, Scrim):
                if self._user_in_guilds(queue_message.team_contact):
                    self._add_scrim(queue_message)
                else:
                    response_code = UserCodes.BadContact
            else:
                print(f"Unrecognized object found in queue. Type: {queue_message.__class__}, value: {queue_message}")
                response_code = SystemCodes.CommunicationError
        except (ConnectionResetError, EOFError) as e:
            print("Connection was terminated from the other side. Respawning listener.")

        except Exception as e:
            print("Error occurred in NASC Bot's listening Thread. This is a critical error and the service may now stop operating.")
            print(f"Exception was: {e.__class__}: {e}")
            traceback.print_tb(e.__traceback__)
            print("Attempting recovery with no knowledge of outcome.")
            response_code = SystemCodes.ExceptionError

        finally:
            try:
                listener_connection.send(response_code)
                listener_connection.close()
            except Exception:
                pass
            self.spawn_listener()
        
    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")
        print("I am in the following servers: ")
        for guild in self.guilds:
            print(f"{guild.name}: {guild.id}")

    async def on_guild_join(self, guild):
        pass

    async def on_message(self, message: discord.Message):
        # If AnalyticsBot has not been mentioned, then ignore the message.
        if 'SchedulerBot' not in [mention.name for mention in message.mentions]:
            return

        cp = CommandParser(message)
        await cp.run()

    # =========== Bot Utilities =========== #
    def _add_scrim(self, scrim):
        db = ScrimFinderDB()
        matching_scrims = db.select_matching_scrims(scrim.played_at, scrim.map_names)

        if matching_scrims == []:
            db.insert_scrim(scrim.team_name, scrim.team_contact, scrim.contact_type, scrim.played_at, scrim.map_names)
        else:
            for matching_scrim in matching_scrims:
                _, team_name, team_contact, _ = db.select_team_from_scrim_id(matching_scrim)
                matches = db.select_matches_by_scrim_id(matching_scrim)
                maps = [db.select_map_name_from_id(map_id) for match_id, map_id, scrim_id in matches]

                self._propose_scrim(Scrim(team_name, team_contact, scrim.played_at, maps), scrim)

    def _propose_scrim(self, existing_scrim, proposed_scrim):
        print(f"I would be attempting to propose a scrim between: \n{existing_scrim}\nand\n{proposed_scrim}")

    def _user_in_guilds(self, user_name):
        for guild in self.guilds:
            if guild.get_member_named(user_name) is not None:
                return True
        return False

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True

    client = NASCBot(intents=intents)
    client.spawn_listener()
    client.run(bot_settings.bot_token)
