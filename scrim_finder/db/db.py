import psycopg2

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

        cursor = self._connection.commit()
        cursor.execute(queries.Matches.insert(), (map_id, scrim_id))

        if (match_id := cursor.fetchone()) is not None:
            match_id = match_id[0]

        self._connection.commit()
        cursor.close()

        return match_id

    def insert_scrim(self, team_name, team_contact, contact_type, played_at, map_names):
        team_id = self.select_team_by_name_and_contact(team_name, team_contact, contact_type)

        if team_id is None:
            team_id = self.insert_team(team_name, team_contact, contact_type)

        cursor = self._connection.cursor()
        cursor.execute(queries.Scrims.insert_without_against(), (team_id, played_at))

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
        cursor.execute(queries.Maps.select_id_by_name(), (map_name.lower(),))

        if (map_id := cursor.fetchone()) is not None:
            map_id = map_id[0]

        self._connection.commit()
        cursor.close()

        return map_id

    def select_map_name_from_id(self, map_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Maps.select_name(), (map_id,))

        map_name = cursor.fetchone()

        self._connection.commit()
        cursor.close()

        return map_name

    def select_matches_by_scrim_id(self, scrim_id):
        cursor = self._connection.cursor()
        cursor.execute(queries.Matches.select_id_by_scrim_id, (scrim_id,))

        match_data = cursor.fetchall()

        self._connection.commit()
        cursor.close()

        return match_data

    def select_matching_scrims(self, played_at, map_ids):
        """ Returns a list of scrim_ids where the played_at is the same as the passed argument
            and the list of matches for the scrim are compatable with the passed map_ids.
        """

        matching_scrims = []

        # Get all scrims happening at the same time as this one.
        simultanious_scrims = self.select_scrims_by_played_at(played_at)
        for scrim in simultanious_scrims:

            # For each scrim, 
            scrim_id, _, _, against = scrim

            if against is not None:
                continue

            scrim_matches = self.select_matches_by_scrim_id(scrim_id)
            
            total_no_preference = 0
            total_matches = 0
            confirmed_maps = []
            for match in scrim_matches:
                _, map_id, _ = match

                if map_id == 1:
                    total_no_preference += 1
                else:
                    if map_id in map_ids:
                        confirmed_maps.append(map_id)
                
                total_matches += 1

            total_unconfirmed_maps = len(set(map_ids) - set(confirmed_maps))

            if total_no_preference >= total_unconfirmed_maps:
                matching_scrims.append(scrim_id)

        return matching_scrims

    def select_scrims_by_played_at(self, played_at):
        cursor = self._connection.cursor()
        cursor.execute(queries.Scrims.select_by_played_at(), (played_at,))

        scrim_data = cursor.fetchall()

        self._connection.commit()
        cursor.close()

        return scrim_data

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

    def select_team_from_scrim_id(self, scrim_id):
        cursor = self._connection.cursor()
        
        cursor.execute(queries.Scrims.select_team_id)

        if (team_id := cursor.fetchone()) is not None:
            team_id = team_id[0]

        cursor.execute(queries.Teams.select(), (team_id,))
        team_data = cursor.fetchone()

        self._connection.commit()
        cursor.close()

        return team_data
