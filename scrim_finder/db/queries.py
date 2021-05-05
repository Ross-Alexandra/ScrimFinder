class ContactTypes:
    @staticmethod
    def select_id_by_type():
        return "select type_id from contact_types where longname=%s;"

class GuildTeams:
    @staticmethod
    def insert():
        return "INSERT INTO guild_teams(team_id, guild_id, schedule_channel, proposal_channel) values(%s, %s, %s, %s);"

class Maps:
    @staticmethod
    def select_id_by_name():
        return "SELECT map_id FROM maps WHERE map_name=%s;"

    @staticmethod
    def select_name():
        return "SELECT map_name FROM maps WHERE map_id=%s;"

class Matches:
    @staticmethod
    def insert():
        return "INSERT INTO matches(map_id, scrim_id) values(%s, %s) RETURNING match_id;"

    @staticmethod
    def select_by_scrim_id():
        return "SELECT match_id, map_id, scrim_id FROM matches WHERE scrim_id=%s;"

class Proposals:
    @staticmethod
    def insert():
        return "INSERT INTO proposals(scrim_id, team_id) values(%s, %s) RETURNING proposal_id;"

    @staticmethod
    def select_id_by_team_and_scrim_id():
        return "SELECT proposal_id FROM proposals WHERE team_id=%s and scrim_id=%s;"

class ProposedMatches:
    @staticmethod
    def insert():
        return "INSERT INTO proposed_matches(map_id, proposal_id) values(%s, %s) RETURNING proposed_match_id;"

class Scrims:
    @staticmethod
    def insert():
        return "INSERT INTO scrims(team_id, played_at, against) values(%s, %s, %s, %s) RETURNING scrim_id;"

    @staticmethod
    def insert_without_against():
        return "INSERT INTO scrims(team_id, scrim_type, played_at) values(%s, %s, %s) RETURNING scrim_id;" 

    @staticmethod
    def select_by_played_at():
        return "SELECT scrim_id, team_id, scrim_type, played_at, against FROM scrims WHERE played_at=%s;"

    @staticmethod
    def select_scrim_type_id():
        return "SELECT scrim_type FROM scrims WHERE scrim_id=%s;"

    @staticmethod
    def select_team_id():
        return "SELECT team_id FROM scrims WHERE scrim_id=%s;"

class ScrimTypes:
    @staticmethod
    def select_id_by_longname():
        return "SELECT type_id FROM scrim_types WHERE longname=%s;"

class Teams:
    @staticmethod
    def insert():
        return "INSERT INTO teams(team_name, contact, contact_type) values(%s, %s, %s) RETURNING team_id;"

    @staticmethod
    def select():
        return "SELECT team_id, team_name, contact, contact_type FROM teams WHERE team_id=%s;"

    @staticmethod
    def select_id_by_name_and_contact():
        return "SELECT team_id FROM teams WHERE team_name=%s and contact=%s and contact_type=%s;"
