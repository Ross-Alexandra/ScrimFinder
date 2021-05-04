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
    def select_id_by_scrim_id():
        return "SELECT match_id FROM matches WHERE scrim_id=%s;"

class Scrims:
    @staticmethod
    def insert():
        return "INSERT INTO scrims(team_id, played_at, against) values(%s, %s, %s, %s) RETURNING scrim_id;"

    @staticmethod
    def insert_without_against():
        return "INSERT INTO scrims(team_id, played_at) values(%s, %s) RETURNING scrim_id;" 

    @staticmethod
    def select_by_played_at():
        return "SELECT scrim_id, team_id, played_at, against FROM scrims WHERE played_at=%s;"

    @staticmethod
    def select_team_id():
        return "SELECT team_id FROM scrims WHERE scrim_id=%s;"

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
