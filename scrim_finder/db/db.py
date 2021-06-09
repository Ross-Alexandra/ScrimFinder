import psycopg2
from datetime import datetime

import scrim_finder.db.db_settings as db_settings
import scrim_finder.db.queries as queries

class ScrimFinderDB:

    def __init__(self):
        self._connection = psycopg2.connect(
            host=db_settings.db_host,
            database=db_settings.db,
            user=db_settings.db_user,
            password=db_settings.db_pass,
            port=db_settings.db_port
        )
        self.connected = True

    def close(self):
        self.connected = False
        self._connection.close()

    def cancel_scrim(self, scrim_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Scrims.update_cancelled(), (True, scrim_id))

        self._connection.commit()
        cursor.close()

    def convert_contact_type_to_id(self, contact_type):
        cursor = self._connection.cursor()
        cursor.execute(queries.ContactTypes.select_id_by_type(), (contact_type,))

        try:
            contact_type_id = cursor.fetchall()[0]
        except Exception as e:
            print(f"Error received while attempting to fetch contact_type_id. Did you attempt to fetch an unsupported contact type?\n{e}")
            self._connection.rollback()
            cursor.close()

        self._connection.commit()
        cursor.close()
        return contact_type_id

    def count_proposals_with_team_and_played_at(self, team_id, played_at):
        cursor = self._connection.cursor()
        cursor.execute(queries.Proposals.count_by_team_id_and_played_at(), (team_id, played_at))

        if (proposal_count := cursor.fetchone()) is not None:
            proposal_count = proposal_count[0]
        else:
            proposal_count = 0
        
        self._connection.commit()
        cursor.close()

        return proposal_count

    def count_total_confirmations(self, message_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Confirmations.count_by_message_id(), (message_id,))

        if (confirmation_count := cursor.fetchone()) is not None:
            confirmation_count = confirmation_count[0]

        self._connection.commit()
        cursor.close()

        return confirmation_count

    def insert_confirmation(self, message_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Confirmations.insert(), (message_id,))

        if (confirmation_id := cursor.fetchone()) is not None:
            confirmation_id = confirmation_id[0]

        self._connection.commit()
        cursor.close()

        return confirmation_id

    def insert_guild_team(self, team_name, contact, contact_type, guild_id, schedule_channel, proposal_channel):
        team_id = self.select_team_by_name_and_contact(team_name, contact, contact_type)

        if team_id is None:
            team_id = self.insert_team(team_name, contact, contact_type)

        if team_id is None:
            return None

        cursor = self._connection.cursor()
        cursor.execute(queries.GuildTeams.insert(), (team_id, guild_id, schedule_channel, proposal_channel))

        self._connection.commit()
        cursor.close()
        return team_id

    def insert_match(self, map_name, scrim_id):
        map_id = self.select_map_id_from_name(map_name)

        if map_id is None:
            return None

        cursor = self._connection.cursor()
        cursor.execute(queries.Matches.insert(), (map_id, scrim_id))

        if (match_id := cursor.fetchone()) is not None:
            match_id = match_id[0]

        self._connection.commit()
        cursor.close()

        return match_id

    def insert_message(self, message_id, channel_id, message_type, reference_id):
        type_id = self.select_message_type_from_name(message_type)

        if type_id is None:
            print(f"Unable to insert message object as there is no known id for {message_type}")
            return None

        cursor = self._connection.cursor()
        cursor.execute(queries.Messages.insert(), (message_id, channel_id, type_id, reference_id))

        self._connection.commit()
        cursor.close()

        return message_id

    def insert_original_maps(self, proposal_id, map_ids):
        cursor = self._connection.cursor()
        for map_id in map_ids:
            cursor.execute(queries.OriginalMaps.insert(), (proposal_id, map_id))

        self._connection.commit()
        cursor.close()

    def insert_proposal(self, scrim_id, team_id, original_scrim_type_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Proposals.insert(), (scrim_id, team_id, original_scrim_type_id))

        if (proposal_id := cursor.fetchone()) is not None:
            proposal_id = proposal_id[0]

        self._connection.commit()
        cursor.close()

        return proposal_id

    def insert_proposed_match(self, map_id, proposal_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.ProposedMatches.insert(), (map_id, proposal_id))

        if (pmatch_id := cursor.fetchone()) is not None:
            pmatch_id = pmatch_id[0]

        self._connection.commit()
        cursor.close()

        return pmatch_id

    def insert_scrim(self, team_name, scrim_type, team_contact, contact_type, played_at, map_names):
        team_id = self.select_team_by_name_and_contact(team_name, team_contact, contact_type)
        if team_id is None:
            team_id = self.insert_team(team_name, team_contact, contact_type)

        scrim_type_id = self.select_scrim_type_id_by_name(scrim_type)
        if scrim_type_id is None:
            return None

        cursor = self._connection.cursor()
        cursor.execute(queries.Scrims.insert_without_against(), (team_id, scrim_type_id, played_at))

        if (scrim_id := cursor.fetchone()) is not None:
            scrim_id = scrim_id[0]

        self._connection.commit()
        cursor.close()

        for map_name in map_names:
            self.insert_match(map_name, scrim_id)

        return scrim_id

    def insert_team(self, team_name, contact, contact_type):
        contact_type_id = self.convert_contact_type_to_id(contact_type)

        if contact_type_id is None:
            print(f"Error: Attempted to add unsupported contact type \"{contact_type}\"")
            return None

        cursor = self._connection.cursor()
        cursor.execute(queries.Teams.insert(), (team_name, contact, contact_type_id))

        try:
            created_id = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error receieved while attempting to fetch created team id: {e}")
            self._connection.rollback()
            cursor.close()
            return None

        self._connection.commit()
        cursor.close()
        return created_id

    def select_map_id_from_name(self, map_name):
        cursor = self._connection.cursor()
        cursor.execute(queries.Maps.select_id_by_name(), (map_name.strip().lower(),))

        if (map_id := cursor.fetchone()) is not None:
            map_id = map_id[0]

        self._connection.commit()
        cursor.close()

        return map_id

    def select_map_name_from_id(self, map_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Maps.select_name(), (map_id,))

        if (map_name := cursor.fetchone()) is not None:
            map_name = map_name[0]

        self._connection.commit()
        cursor.close()

        return map_name

    def select_matches_by_scrim_id(self, scrim_id):
        """ list(match_id, map_id, scrim_id) """

        cursor = self._connection.cursor()
        cursor.execute(queries.Matches.select_by_scrim_id(), (scrim_id,))

        match_data = cursor.fetchall()

        self._connection.commit()
        cursor.close()

        return match_data

    def select_matching_scrims(self, team_id, played_at, scrim_type, map_ids):
        """ Returns a list of scrim_ids where the played_at is the same as the passed argument
            and the list of matches for the scrim are compatable with the passed map_ids.
        """

        # Define internal helper function.
        def maps_match(maps_1, maps_2, no_preference):
            """ Extremely over optimized, but I wanted to prove it could be done in O(n) """

            if len(maps_1) != len(maps_2):
                return False

            # Scrape out the no_preference id's.
            # These will be accounted for later, but
            # should not be tallied with the rest of the maps.
            no_preference_1 = maps_1.count(no_preference)
            no_preference_2 = maps_2.count(no_preference)
            maps_1 = [map_id for map_id in maps_1 if map_id != no_preference]
            maps_2 = [map_id for map_id in maps_2 if map_id != no_preference]

            # Get the combined list as this is done a few times.
            combined_maps = set(maps_1 + maps_2)

            # Convert each set of maps into a set (O(n)) and set
            # each internal id to 0.
            map_1_counts = {map_id: 0 for map_id in combined_maps}
            map_2_counts = {map_id: 0 for map_id in combined_maps}

            # Walk through list of maps and count each occurrence in
            # the respective dictionaries. 1 pass therefore O(n)
            for map_id in maps_1:
                map_1_counts[map_id] += 1

            for map_id in maps_2:
                map_2_counts[map_id] += 1

            # List + List = O(1)
            # List => set = O(n)
            # Therefore do a O(n) operation,
            # then for each of the ids, compare
            # their counts. If they're equal then
            # this map is confirmed n times (where 
            # n = the count). Equality Checking
            # is O(1) so this loop is O(n).
            confirmed_maps = []
            maps_1_imbalance = []
            maps_2_imbalance = []
            for map_id in combined_maps:
                
                # If the counts are equal, then confirm this map
                # n times.
                if map_1_counts[map_id] == map_2_counts[map_id]:
                    # ([a] * n).count(a) == n.
                    confirmed_maps += ([map_id] * map_2_counts[map_id])

                # Otherwise, if map_1_counts has more then
                # There are map_2_counts matches and 
                # (map_1_counts - map_2_counts) map 1 imbalances.
                elif map_1_counts[map_id] > map_2_counts[map_id]:
                    confirmed_maps += ([map_id] * map_2_counts[map_id])
                    maps_1_imbalance += ([map_id] * (map_1_counts[map_id] - map_2_counts[map_id]))
                
                # Otherwise, opposite of above.
                else:
                    confirmed_maps += ([map_id] * map_1_counts[map_id])
                    maps_2_imbalance += ([map_id] * (map_2_counts[map_id] - map_1_counts[map_id]))

            return len(maps_1_imbalance) <= no_preference_2 and len(maps_2_imbalance) <= no_preference_1

        matching_scrims = []

        # Get all scrims happening at the same time as this one.
        simultanious_scrims = self.select_scrims_by_played_at(played_at)
        print(f"Found {len(simultanious_scrims)} matching scrims.")

        no_map_preference_id = self.select_no_map_preference_id()
        no_scrim_type_preference_id = self.select_no_scrim_type_preference_id()

        for scrim in simultanious_scrims:
            scrim_id, _, scrim_type_id, _, cancelled, against = scrim
            print(f"Checking for scrim match against scrim with id {scrim_id}")

            if cancelled:
                print("This scrim has already been cancelled.")
                continue

            if against is not None:
                print("This scrim already has an opponent.")
                continue

            if scrim_type_id != no_scrim_type_preference_id and scrim_type != no_scrim_type_preference_id and scrim_type_id != scrim_type:
                print("This scrim does not match the match type.")
                continue

            if any(pteam_id == team_id for pteam_id in self.select_proposal_team_ids_from_scrim(scrim_id)):
                print("This team already has a proposal on this scrim.")
                continue

            if any(rejected == False for (_, _, _, rejected, _) in self.select_proposals_from_scrim_id(scrim_id)):
                print("This scrim already has an active proposal.")
                continue

            scrim_matches = self.select_matches_by_scrim_id(scrim_id)
            scrim_maps = [map_id for _, map_id, _ in scrim_matches]

            if maps_match(map_ids, scrim_maps, no_map_preference_id):
                print(f"Scrim with id {scrim_id} matches.")
                matching_scrims.append(scrim_id)
            else:
                print("Maps did not match.")

        return matching_scrims

    def select_message_by_id(self, message_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Messages.select(), (message_id,))

        message = cursor.fetchone()

        self._connection.commit()
        cursor.close()

        return message
    
    def select_message_by_reference_id(self, message_type_id, reference_id):
        """" message_id, channel_id, message_type, reference_id """
        cursor = self._connection.cursor()
        cursor.execute(queries.Messages.select_all_by_reference_id(), (message_type_id, reference_id))

        messages = cursor.fetchall()

        self._connection.commit()
        cursor.close()

        return messages

    def select_message_type_from_name(self, name):
        cursor = self._connection.cursor()
        cursor.execute(queries.MessageTypes.select_id_by_longname(), (name,))

        if (type_id := cursor.fetchone()) is not None:
            type_id = type_id[0]

        self._connection.commit()
        cursor.close()

        return type_id

    def select_message_type_name_from_id(self, type_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.MessageTypes.select_longname_by_id(), (type_id,))

        if (longname := cursor.fetchone()) is not None:
            longname = longname[0]

        self._connection.commit()
        cursor.close()

        return longname

    def select_no_map_preference_id(self):
        cursor = self._connection.cursor()

        cursor.execute(queries.Maps.select_id_by_name(), ("no preference",))

        if (map_id := cursor.fetchone()) is not None:
            map_id = map_id[0]

        self._connection.commit()
        cursor.close()

        return map_id

    def select_no_scrim_type_preference_id(self):
        cursor = self._connection.cursor()

        cursor.execute(queries.ScrimTypes.select_id_by_longname(), ("no preference",))

        if (type_id := cursor.fetchone()) is not None:
            type_id = type_id[0]

        self._connection.commit()
        cursor.close()

        return type_id

    def select_original_maps(self, proposal_id):
        """ list(map_id) """
        cursor = self._connection.cursor()
        cursor.execute(queries.OriginalMaps.select_by_proposal_id(), (proposal_id,))

        maps = cursor.fetchall()

        self._connection.commit()
        cursor.close()

        return maps

    def select_overdue_scrims(self):
        """ list(scrim_id) """
        cursor = self._connection.cursor()
        cursor.execute(queries.Scrims.select_overdue_scrims())

        scrim_ids = cursor.fetchall()

        self._connection.commit()
        cursor.close()

        return scrim_ids

    def select_postable_scrims(self):
        """ list(scrim_id) """
        cursor = self._connection.cursor()
        cursor.execute(queries.Scrims.select_postable_scrims())

        scrim_ids = cursor.fetchall()

        self._connection.commit()
        cursor.close()

        return scrim_ids

    def select_proposal(self, proposal_id):
        """ proposal_id, scrim_id, team_id, rejected, original_scrim_type """

        cursor = self._connection.cursor()
        cursor.execute(queries.Proposals.select(), (proposal_id,))

        proposal = cursor.fetchone()

        self._connection.commit()
        cursor.close()

        return proposal

    def select_proposal_id_by_team_id_and_scrim_id(self, team_id, scrim_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Proposals.select_id_by_team_and_scrim_id(), (team_id, scrim_id))

        if (proposal_id := cursor.fetchone()) is not None:
            proposal_id = proposal_id[0]

        self._connection.commit()
        cursor.close()

        return proposal_id

    def select_proposal_team_ids_from_scrim(self, scrim_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Proposals.select_proposal_from_scrim_id(), (scrim_id,))

        proposals = cursor.fetchall()
        team_ids = []
        for proposal in proposals:
            _, _, team_id, _, _ = proposal
            team_ids.append(team_id)

        self._connection.commit()
        cursor.close()

        return team_ids

    def select_proposals_from_scrim_id(self, scrim_id):
        """ proposal_id, scrim_id, team_id, rejected, original_scrim_id """
        cursor = self._connection.cursor()
        cursor.execute(queries.Proposals.select_proposal_from_scrim_id(), (scrim_id,))

        proposals = cursor.fetchall()

        self._connection.commit()
        cursor.close()

        return proposals

    def select_scrim(self, scrim_id):
        """ scrim_id, team_id, scrim_type_id, played_at, cancelled, against """

        cursor = self._connection.cursor()
        cursor.execute(queries.Scrims.select(), (scrim_id,))

        scrim = cursor.fetchone()

        self._connection.commit()
        cursor.close()

        return scrim

    def select_scrims_by_played_at(self, played_at):
        """ scrim_id, team_id, scrim_type, played_at, cancelled, against """ 

        cursor = self._connection.cursor()
        cursor.execute(queries.Scrims.select_by_played_at(), (played_at,))

        scrim_data = cursor.fetchall()

        self._connection.commit()
        cursor.close()

        return scrim_data

    def select_scrim_id_from_proposal(self, proposal_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Proposals.select_scrim_id(), (proposal_id,))

        if (scrim_id := cursor.fetchone()) is not None:
            scrim_id = scrim_id[0]

        self._connection.commit()
        cursor.close()

        return scrim_id

    def select_scrim_type_id_by_name(self, type_name):
        cursor = self._connection.cursor()
        cursor.execute(queries.ScrimTypes.select_id_by_longname(), (type_name,))

        if (type_id := cursor.fetchone()) is not None:
            type_id = type_id[0]
        
        self._connection.commit()
        cursor.close()

        return type_id

    def select_scrim_type_id_from_scrim_id(self, scrim_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Scrims.select_scrim_type_id(), (scrim_id,))

        if (type_id := cursor.fetchone()) is not None:
            type_id = type_id[0]

        self._connection.commit()
        cursor.close()

        return type_id


    def select_scrim_type_name_by_id(self, type_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.ScrimTypes.select_longname_by_id(), (type_id,))

        if (longname := cursor.fetchone()) is not None:
            longname = longname[0]
        
        self._connection.commit()
        cursor.close()

        return longname

    def select_team(self, team_id):
        """ team_id, team_name, contact, contact_type """

        cursor = self._connection.cursor()
        cursor.execute(queries.Teams.select(), (team_id,))

        team = cursor.fetchone()

        self._connection.commit()
        cursor.close()

        return team

    def select_team_by_name_and_contact(self, team_name, contact, contact_type):
        contact_type_id = self.convert_contact_type_to_id(contact_type)

        if contact_type_id is None:
            print(f"Error: Attempted to retrieve team with unsupported contact type \"{contact_type}\".")
        
        cursor = self._connection.cursor()
        cursor.execute(queries.Teams.select_id_by_name_and_contact(), (team_name, contact, contact_type_id))

        # cursor.fetchone() will either return (team_id,) or None depending.
        # team_id should be equal to either team_id or None depending on the same thing
        # thus convert out the tuple.
        if (team_id := cursor.fetchone()) is not None:
            team_id = team_id[0]

        self._connection.commit()
        cursor.close()
        return team_id

    def select_team_by_reference_id(self, message_type_id, reference_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Messages.select_team_by_reference_id(), {"ref_id": reference_id})

        team_data = cursor.fetchone()

        self._connection.commit()
        cursor.close()

        return team_data

    def select_team_from_scrim_id(self, scrim_id):
        cursor = self._connection.cursor()
        
        cursor.execute(queries.Scrims.select_team_id(), (scrim_id,))

        if (team_id := cursor.fetchone()) is not None:
            team_id = team_id[0]

        cursor.execute(queries.Teams.select(), (team_id,))
        team_data = cursor.fetchone()

        self._connection.commit()
        cursor.close()

        return team_data

    def reject_proposal(self, proposal_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Proposals.set_rejected(), (proposal_id,))

        self._connection.commit()
        cursor.close()

    def update_scrim_against(self, scrim_id, team_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Scrims.update_against(), (team_id, scrim_id))

        self._connection.commit()
        cursor.close()
