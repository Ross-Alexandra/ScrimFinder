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
                    response_code = self._add_scrim(queue_message)
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

        map_ids = [db.select_map_id_from_name(map_name) for map_name in scrim.map_names]
        matching_scrim_ids = db.select_matching_scrims(scrim.played_at, map_ids)

        if matching_scrim_ids == []:
            print("No matching scrims found. Creating new scrim.")
            db.insert_scrim(scrim.team_name, scrim.team_contact, scrim.contact_type, scrim.played_at, scrim.map_names)
            return SystemCodes.Good
        else:
            scrim_team_data = {
                matching_scrim_id: db.select_team_from_scrim_id(matching_scrim_id) for matching_scrim_id in matching_scrim_ids
            }

            if any([contact == scrim.team_contact and contact_type == scrim.contact_type for _, _, contact, contact_type in scrim_team_data.values()]):
                return UserCodes.DoubleBooking

            for scrim_id, team_tuple in scrim_team_data.items():
                _, team_name, team_contact, _ = team_tuple

                print(f"Discovered Team Name: {team_name}, Discovered Team Contact: {team_contact}")
                matches = db.select_matches_by_scrim_id(scrim_id)
                maps = [db.select_map_name_from_id(map_id) for _, map_id, _ in matches]

                self._propose_scrim(db, Scrim(team_name, team_contact, scrim.played_at, maps), scrim_id, scrim)
            return SystemCodes.Good

    def _propose_scrim(self, db, existing_scrim, existing_scrim_id, proposed_scrim):
        team_id = db.select_team_by_name_and_contact(proposed_scrim.team_name, proposed_scrim.team_contact, proposed_scrim.contact_type)

        # If the team_id does not exist, create a new team for it.
        if team_id is None:
            team_id = db.insert_team(proposed_scrim.team_name, proposed_scrim.team_contact, proposed_scrim.contact_type)

        # Otherwise, if the team id does exist and there is already a proposal on this scrim
        # by this team, then don't create a new one.
        elif db.select_proposal_id_by_team_id_and_scrim_id(team_id, existing_scrim_id) is not None:
            print(f"Proposal already exists for this team on this scrim. Moving on to next proposal.")
            return 

        print(f"Proposing a scrim between: \n{existing_scrim}\nand\n{proposed_scrim}")
        proposal_id = db.insert_proposal(existing_scrim_id, team_id)

        total_maps = len(proposed_scrim.map_names)
        map_pool = [map_name for map_name in set(existing_scrim.map_names + proposed_scrim.map_names) if map_name != 'no preference']

        while len(map_pool) < total_maps: map_pool.append('no preference')

        print(f"Generating match proposals with condensed match pool of: {map_pool}")
        for map_name in map_pool:
            db.insert_proposed_match(db.select_map_id_from_name(map_name), proposal_id)

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
