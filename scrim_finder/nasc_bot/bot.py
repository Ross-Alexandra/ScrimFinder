import asyncio

from discord import channel, message
from scrim_finder.db.queries import Matches
import discord
from multiprocessing.connection import Listener
import schedule
from time import sleep
from threading import Thread
import traceback

import scrim_finder.nasc_bot.bot_settings as bot_settings

from scrim_finder.api.codes import SystemCodes, UserCodes
from scrim_finder.api.queue_objects import INTER_PROCESS_AUTH_KEY, INTER_PROCESS_PORT, INTER_PROCESS_HOST,Scrim
from scrim_finder.db import ScrimFinderDB
from scrim_finder.nasc_bot.command import CommandParser
import scrim_finder.nasc_bot.aware_scheduler # Required for monkey patching schedule.

class NASCBot(discord.Client):

    def get_db(self):
        if (db := getattr(self, "db", None)) is not None:
            if db.connected:
                return db

        self.db = ScrimFinderDB()
        return self.db

    # =========== External Utilities =========== #
    def spawn_listener(self):
        print("Spawning event listener for frontend.")
        self.__listener_thread__ = Thread(target=self._on_queue_receive)
        self.__listener_thread__.daemon = True
        self.__listener_thread__.start()

    def spawn_lfs_watcher(self):
        def watcher():
            print("Spawning lfs watcher.")
            try:
                db = ScrimFinderDB()

                schedule.every(30).minutes.do(print, "Scheduler is still alive.")
                schedule.every(2).hours.at("30:00", "America/New_York").do(self._remove_overdue_lfs_posts, db)
                schedule.every().day.at("00:30", "America/New_York").do(self._post_postable_lfs_posts, db)

                while True:
                    schedule.run_pending()
                    sleep(60)

            except Exception as e:
                print("Error occurred in NASC Bot's lfs watcher Thread. This is a critical error and the service may now stop operating.")
                print(f"Exception was: {e.__class__}: {e}")
                traceback.print_tb(e.__traceback__)
                print("Attempting recovery with no knowledge of outcome.")

                sleep(60)
                self.spawn_lfs_watcher()

        self.__watcher_thread__ = Thread(target=watcher)
        self.__watcher_thread__.daemon = True
        self.__watcher_thread__.start()

    # =========== Bot Hooks =========== #
    def _on_queue_receive(self):
        """ A special method spawned in a different thread.
            This method will fire whenever the multiprocessing
            Listener gets a new message.
        """

        # Sleep to ensure no race conditions where we spawn a listener while
        # the other listener is still spinning down.
        sleep(.1)

        listener = Listener((INTER_PROCESS_HOST, INTER_PROCESS_PORT), authkey=INTER_PROCESS_AUTH_KEY)
        listener_connection = listener.accept()

        print("New listener was created on NASC Bot.")

        try:
            response_code = SystemCodes.ExceptionError
            queue_message = listener_connection.recv()
            print(f"Received a message on the queue: {queue_message}")

            if isinstance(queue_message, Scrim):
                if self._user_in_guilds(queue_message.team_contact):
                    user = self._get_user_by_discriminator(queue_message.team_contact)
                    response_code = self._add_scrim(queue_message, user)
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

    async def on_raw_reaction_add(self, payload):
        if payload.event_type != "REACTION_ADD":
            print("Wrong event type, ignoring.")

        channel = await self.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author.id != self.user.id:
            print(f"Reacted to message by author with id {message.author.id}. Bot id is {self.user.id}")
            return

        db = ScrimFinderDB()
        if (message_obj := db.select_message_by_id(payload.message_id)) is not None:
            _, _, message_type_id, reference_id = message_obj
            message_type = db.select_message_type_name_from_id(message_type_id)
             
            if message_type == "proposal":
                # We know this was a proposal message thus we know
                # that this reference_id must be a proposal_id
                proposal_id = reference_id
                _, scrim_id, _, rejected, _ = db.select_proposal(proposal_id)
                _, _, _, _, _, against = db.select_scrim(scrim_id)

                if rejected:
                    print("Reaction made after a rejection was already processed. Ignoring it.")
                    return

                if against is not None:
                    print("A match was already found for this scrim. Ignore this reaction.")
                    return

                confirm_unicode = '\N{THUMBS UP SIGN}'
                decline_unicode = '\N{THUMBS DOWN SIGN}'
                reaction_count = next(reaction for reaction in message.reactions if reaction.emoji.strip() == payload.emoji.name).count
                if reaction_count > 1 and payload.emoji.name == confirm_unicode:
                    self._send_confirmation(db, payload.message_id, proposal_id)

                elif reaction_count > 1 and payload.emoji.name == decline_unicode:
                    self._reject_proposal(db, proposal_id)

            elif message_type == "rejector":
                reaction_count = next(reaction for reaction in message.reactions if reaction.emoji.strip() == payload.emoji.name).count
                if reaction_count > 1 and payload.emoji.name == '\N{NO ENTRY SIGN}':
                    _, team_id, _, _, cancelled, against = db.select_scrim(reference_id)

                    if cancelled:
                        print("This match was already cancelled. Ignoring this reaciton.")
                        return

                    if against is not None:
                        print("A match was already found for this scrim. Ignore this reaction.")
                        return

                    self._delete_lfs_message(db, reference_id)
                    
                    # Send the user a message confirming the cancelation.
                    _, _, scrim_contact, _ = db.select_team(team_id)
                    user = self._get_user_by_discriminator(scrim_contact)

                    embed = discord.Embed(title=f"Cancelation Confirmed", color=0x00aa00)
                    self._dm_user(user, lambda channel: self._message_channel(db, embed, channel, None, None, embed=True))

                    proposals = db.select_proposals_from_scrim_id(reference_id)
                    for proposal_id, _, _, _, _ in proposals:
                        self._reject_proposal(db, proposal_id)

                    db.cancel_scrim(reference_id)

            else:
                print(f"Reaction was to a message of type {message_type}. No operation needed.")
        else:
            print(f"I have no history of this message. Ignoring.")

    async def on_member_join(self, member):
        pass

    async def on_guild_join(self, guild):
        pass

    async def on_message(self, message: discord.Message):
        # If AnalyticsBot has not been mentioned, then ignore the message.
        if 'SchedulerBot' not in [mention.name for mention in message.mentions]:
            return

        cp = CommandParser(message)
        await cp.run()

    # =========== Bot Utilities =========== #
    def _add_reactions(self, message, reactions):
        for reaction in reactions:
            asyncio.run_coroutine_threadsafe(message.add_reaction(reaction), self.loop)

    def _add_scrim(self, scrim: Scrim, user: discord.User):
        db = ScrimFinderDB()

        # Get the team id, and see if this team already has a scrim at this time.
        if (team_id := db.select_team_by_name_and_contact(scrim.team_name, scrim.team_contact, scrim.contact_type)) is None:
            
            # Create a new team, and move on. We know this team
            # does not already have a scrim at this time as
            # this team didn't exist yet.
            team_id = db.insert_team(scrim.team_name, scrim.team_contact, scrim.contact_type)
        else:
            # Check if this team already has a scrim played at this time.
            if team_id in [team_id for (_, team_id, _, _, cancelled, _) in db.select_scrims_by_played_at(scrim.played_at) if not cancelled]:
                print("This team already has a scrim at this time.")
                return UserCodes.DoubleBooking

            # See if this team already has a non-rejected proposal
            # at this time.
            if db.count_proposals_with_team_and_played_at(team_id, scrim.played_at) != 0:
                print("This team already has a non-rejected proposal at this time.")
                return UserCodes.PendingProposal

        map_ids = [db.select_map_id_from_name(map_name) for map_name in scrim.map_names]
        scrim_type_id = db.select_scrim_type_id_by_name(scrim.scrim_type)
        matching_scrim_ids = db.select_matching_scrims(team_id, scrim.played_at, scrim_type_id, map_ids)

        if matching_scrim_ids == []:
            print("No matching scrims found. Creating new scrim.")
            scrim_id = db.insert_scrim(scrim.team_name, scrim.scrim_type, scrim.team_contact, scrim.contact_type, scrim.played_at, scrim.map_names)
            self._send_lfs_messages(db, scrim_id)

            # DM user a cancel message.
            maps = sorted(scrim.map_names, key=lambda map_name: 1 if map_name == "no preference" else 0)
            date_string = scrim.played_at.strftime("%a, %b/%d at %I:%M%p EST")
            embed = discord.Embed(title="Scrim Generated", description="If you need to cancel please react to this message.")
            embed.add_field(name="Time", value=date_string, inline=False)
            for index, map_name in enumerate(maps):
                embed.add_field(name=f"Map {index + 1}", value=map_name.capitalize(), inline=True)

            def message_callback(channel):
                self._message_channel(db, embed, channel, "rejector", scrim_id, embed=True, reactions=['\N{NO ENTRY SIGN}'])

            self._dm_user(user, message_callback)

            return SystemCodes.ScrimCreated
        else:
            scrim_team_data = {
                matching_scrim_id: db.select_team_from_scrim_id(matching_scrim_id) for matching_scrim_id in matching_scrim_ids
            }

            # Select any value from the scrim team data and
            # propose this scrim. This allows us to
            # have a "large recrusive loop" where:
            #   React -> _add_scrim()
            #   _add_scrim() -> new proposal
            #   new proposal -> rejected
            #   rejected -> _add_scrim()
            #   ...
            #   new_proposal -> accepted
            #     -- or --
            #   _add_scrim -> new scrim. 
            scrim_id = next(iter(scrim_team_data))
            _, team_name, team_contact, _ = scrim_team_data[scrim_id]

            # Get the matches and the map for the scrim_id
            # in order to create a scrim object of the original scrim.
            print(f"Discovered Team Name: {team_name}, Discovered Team Contact: {team_contact}")
            matches = db.select_matches_by_scrim_id(scrim_id)
            maps = [db.select_map_name_from_id(map_id) for _, map_id, _ in matches]
            original_scrim = Scrim(team_name, scrim.scrim_type, team_contact, scrim.played_at, maps)

            # Get info on the proposal and the finalized map pool
            # to be used in the embed.
            proposal_id = self._propose_scrim(db, original_scrim, scrim_id, scrim)
            proposee_name = original_scrim.team_name
            proposer_name = scrim.team_name
            date_string = original_scrim.played_at.strftime("%a, %b/%d at %I:%M%p EST")
            map_pool = [map_name if map_name != 'no preference' else 'TBD' for map_name in self._get_map_pool(original_scrim.map_names, scrim.map_names)]

            # Create a record of the maps originally requested
            # for the proposal in case this proposal is rejected
            # and turned (magically) into a scrim.
            db.insert_original_maps(proposal_id, map_ids) 

            # Create an embed which will be sent to both the
            # contact for the scirm and the contact for the
            # proposal.
            embed = discord.Embed(title=f"Scrim Proposal", description=f"{scrim.scrim_type} scrim with '{proposee_name}' and '{proposer_name}'", color=0x005500)
            embed.add_field(name="Time", value=date_string, inline=False)
            for index, map_name in enumerate(map_pool):
                embed.add_field(name=f"Map {index + 1}", value=map_name.capitalize(), inline=True)

            # Loop over all the guilds the bot is in
            # in an attempt to find the 2 users.
            # This loop will then send the earlier created
            # embeds to both those users (and flags are here
            # to ensure it is only sent once per user.)
            dmed_proposer = False
            dmed_proposee = False
            create_message_callback = lambda channel: self._message_channel(db, embed, channel, "proposal", proposal_id, embed=True, reactions=['\N{THUMBS UP SIGN}', '\N{THUMBS DOWN SIGN}'])
            for guild in self.guilds:
                if dmed_proposee is False and (user := guild.get_member_named(original_scrim.team_contact)) is not None:
                    dmed_proposee = True
                    print(f"Dm-ing {original_scrim.team_contact}")
                    self._dm_user(user, create_message_callback)

                if dmed_proposer is False and (user := guild.get_member_named(scrim.team_contact)) is not None:
                    dmed_proposer = True
                    print(f"Dm-ing {scrim.team_contact}")
                    self._dm_user(user, create_message_callback)

            # TODO: Need to handle this case in a better way than just logging.
            # The proposal didn't go through and a team will get stuck without
            # some sort of time limit.
            if not dmed_proposee:
                print(f"Unable to dm {original_scrim.team_contact} for unknown reason. Bot was unable to locate this user.")
            if not dmed_proposer:
                print(f"Unable to dm {scrim.team_contact} for unknown reason. Bot was unable to locate this user.")

            return SystemCodes.ProposalCreated

    def _get_map_pool(self, map_set_1, map_set_2):
        total_maps = len(map_set_1)
        map_pool = [map_name for map_name in set(map_set_1 + map_set_2) if map_name != 'no preference']

        while len(map_pool) < total_maps: map_pool.append('no preference')

        return map_pool

    def _get_user_by_discriminator(self, discriminator):
        for guild in self.guilds:
            if (user := guild.get_member_named(discriminator)) is not None:
                return user
        
        return None

    def _dm_user(self, user: discord.User, message_channel_callback):
        if user.dm_channel is None:
            create_message = lambda fut: message_channel_callback(fut.result())

            fut = asyncio.run_coroutine_threadsafe(user.create_dm(), self.loop)
            fut.add_done_callback(create_message)
        else:
            message_channel_callback(user.dm_channel)

    def _delete_lfs_message(self, db: ScrimFinderDB, scrim_id):
        scrim_message_type = db.select_message_type_from_name("scrim")
        message_objects = db.select_message_by_reference_id(scrim_message_type, scrim_id)

        for message_id, channel_id, _, _ in message_objects:
            self._delete_message(channel_id, message_id)

    def _delete_message(self, channel_id, message_id):

        async def delete_message(channel_id, message_id):
            channel = await self.fetch_channel(channel_id)
            message = await channel.fetch_message(message_id)
            await message.delete()

        asyncio.run_coroutine_threadsafe(delete_message(channel_id, message_id), self.loop)

    def _message_channel(self, db, msg, channel: discord.abc.Messageable, message_type, reference_id, embed=False, reactions=list([])):
        print(f"Sending message of type {message_type} for object with id {reference_id} to discord.")

        try:
            if embed:
                fut = asyncio.run_coroutine_threadsafe(channel.send(embed=msg), self.loop)
            else:
                fut = asyncio.run_coroutine_threadsafe(channel.send(content=msg), self.loop)
            print("Message is sent.")

            if message_type is not None and reference_id is not None:
                def create_message_entry_callback(fut):
                    db.insert_message(fut.result().id, channel.id, message_type, reference_id)

                fut.add_done_callback(create_message_entry_callback)

            if reactions != []:
                def add_reaction_callback(fut):
                    self._add_reactions(fut.result(), reactions)

                fut.add_done_callback(add_reaction_callback)

        except Exception:
            print(f"Error while sending message to discord. This may not be fatal\n")
            traceback.print_exc()

    def _post_postable_lfs_posts(self, db: ScrimFinderDB):
        ids = db.select_postable_scrims()

        for scrim_id in ids:

            # Ensure a message has not already been sent for this scrim.
            if not db.select_message_by_reference_id(db.select_message_type_from_name("scrim"), scrim_id):
                self._send_lfs_messages(db, scrim_id)

    def _propose_scrim(self, db: ScrimFinderDB, existing_scrim, existing_scrim_id, proposed_scrim):
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
        proposed_scrim_type = db.select_scrim_type_id_by_name(proposed_scrim.scrim_type)
        proposal_id = db.insert_proposal(existing_scrim_id, team_id, proposed_scrim_type)

        map_pool = self._get_map_pool(existing_scrim.map_names, proposed_scrim.map_names)
        proposed_scrim.map_names = map_pool

        print(f"Generating match proposals with condensed match pool of: {map_pool}")
        for map_name in map_pool:
            db.insert_proposed_match(db.select_map_id_from_name(map_name), proposal_id)

        return proposal_id

    def _reject_proposal(self, db: ScrimFinderDB, proposal_id):
        _, scrim_id, pteam_id, rejected, original_scrim_type = db.select_proposal(proposal_id)
        _, steam_id, _, played_at, _, _ = db.select_scrim(scrim_id)
        _, _, scrim_contact, _ = db.select_team(steam_id)
        _, proposal_team, proposal_contact, _ = db.select_team(pteam_id)

        if rejected:
            print("This proposal has already been rejected.")
            return

        scrim_type_name = db.select_scrim_type_name_by_id(original_scrim_type)
        scrim_user = self._get_user_by_discriminator(scrim_contact)
        proposal_user = self._get_user_by_discriminator(proposal_contact)

        map_ids = db.select_original_maps(proposal_id)
        map_pool = [db.select_map_name_from_id(map_id) for map_id in map_ids]

        db.reject_proposal(proposal_id)
        self._send_rejection(db, scrim_user)
        self._send_rejection(db, proposal_user)

        # Since add scrim only creates one proposal object, once
        # this one is rejected (and therefore no longer) 
        # counted as a matching scrim, just attempt to readd the scrim
        # and either get the next proposal, or create this scrim.
        proposal_scrim = Scrim(proposal_team, scrim_type_name, proposal_contact, played_at, map_pool)
        self._add_scrim(proposal_scrim, proposal_user)

    def _remove_overdue_lfs_posts(self, db: ScrimFinderDB):
        print("Attempting to remove overdue posts.")
        ids = db.select_overdue_scrims()
        print(f"Found overdue ids: {ids}")

        for scrim_id in ids:
            self._delete_lfs_message(db, scrim_id)

    def _send_confirmation(self, db: ScrimFinderDB, message_id, proposal_id):
        proposal_message_type_id = db.select_message_type_from_name("proposal")

        messages = db.select_message_by_reference_id(proposal_message_type_id, proposal_id)

        if len(messages) != 2:
            print(f"Critical error while sending confirmation. Incorrect number of messages found: {messages}")

        confirmer_obj = messages[0] if messages[0][0] == message_id else messages[1]
        confirmee_obj = messages[1] if messages[0][0] == message_id else messages[0]

        confirmer_confirmation = db.count_total_confirmations(confirmer_obj[0])
        confirmee_confirmation = db.count_total_confirmations(confirmee_obj[0])

        if confirmer_confirmation == 1:
            print("This user has already confirmed. Ignoring this reaction.")
            return

        proposal_team_id, _, proposal_contact, _ = db.select_team_by_reference_id(confirmer_obj[2], confirmer_obj[3])
        scrim_team_id, _, scrim_contact, _ = db.select_team_from_scrim_id(db.select_scrim_id_from_proposal(proposal_id))

        # TODO: When we update to use more than just discord, update this.
        proposer = self._get_user_by_discriminator(proposal_contact)
        scrimer = self._get_user_by_discriminator(scrim_contact)

        if confirmee_confirmation == 1:
            db.insert_confirmation(message_id)

            print(f"Scrim between teams {proposal_team_id} and {scrim_team_id} has been confirmed.")
            scrimer_embed = discord.Embed(title=f"Scrim Confirmed", description=f"Please contact {proposal_contact} to get uplay info.", color=0x00aa00)
            proposer_embed = discord.Embed(title=f"Scrim Confirmed", description=f"Please contact {scrim_contact} to get uplay info.", color=0x00aa00)

            def proposer_callback(channel):
                self._message_channel(db, proposer_embed, channel, None, None, embed=True)

            def scrimer_callback(channel):
                self._message_channel(db, scrimer_embed, channel, None, None, embed=True)

            self._dm_user(proposer, proposer_callback)
            self._dm_user(scrimer, scrimer_callback)

            scrim_id = db.select_scrim_id_from_proposal(proposal_id)
            db.update_scrim_against(scrim_id, proposal_team_id)
            self._delete_lfs_message(db, scrim_id)

        else:
            db.insert_confirmation(message_id)

    def _send_lfs_messages(self, db: ScrimFinderDB, scrim_id):
        scrim_id, team_id, scrim_type_id, played_at, _, _ = db.select_scrim(scrim_id)
        if scrim_id not in [scrim_id for (scrim_id,) in db.select_postable_scrims()]:
            print("This scrim is for the incorrect day. Not posting and waiting for the watcher to post.")
            return

        map_names = [db.select_map_name_from_id(map_id) for (_, map_id, _) in db.select_matches_by_scrim_id(scrim_id)]
        scrim_type = db.select_scrim_type_name_by_id(scrim_type_id)
        _, team_name, _, _ = db.select_team(team_id)

        maps = sorted(map_names, key=lambda map_name: 1 if map_name == "no preference" else 0)
        date_string = played_at.strftime("%a, %b/%d at %I:%M%p EST")

        for guild in self.guilds:
            for channel in guild.channels:
                if channel.name == "scrims":
                    embed = discord.Embed(title=f"Team '{team_name}' is LFS", description="to schedule with them please post a scrim at the matching time at http://scrimsearch.theserverproject.com", color=0x000055)
                    embed.add_field(name="Time", value=date_string, inline=False)
                    embed.add_field(name="Type", value=scrim_type, inline=False)
                    for index, map_name in enumerate(maps):
                        embed.add_field(name=f"Map {index + 1}", value=map_name.capitalize(), inline=True)

                    self._message_channel(db, embed, channel, "scrim", scrim_id, embed=True)

    def _send_rejection(self, db, user):
        embed = discord.Embed(title="Scrim Rejected", description="This scrim was rejected by either you or the other party.", color=0xaa0000)
        def callback(channel):
            self._message_channel(db, embed, channel, None, None, embed=True)

        self._dm_user(user, callback)

    def _user_in_guilds(self, user_name):
        for guild in self.guilds:
            if guild.get_member_named(user_name) is not None:
                return True
        return False

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    intents.reactions = True

    if bot_settings.bot_token == "":
        print("Unable to start the bot. Token is missing.")
        exit()

    client = NASCBot(intents=intents)
    client.spawn_listener()
    client.spawn_lfs_watcher()
    client.run(bot_settings.bot_token)
