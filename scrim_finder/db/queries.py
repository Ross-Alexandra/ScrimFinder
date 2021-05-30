from os import stat


class Confirmations:
    @staticmethod
    def count_by_message_id():
        return "select count(*) as message_count from confirmations where message_id=%s;"

    @staticmethod
    def insert():
        return "INSERT INTO confirmations(message_id) values(%s) RETURNING confirmation_id;"

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

class Messages:
    @staticmethod
    def insert():
        return "INSERT INTO messages(message_id, message_type, reference_id) values(%s, %s, %s);"

    @staticmethod
    def select():
        return "SELECT message_id, message_type, reference_id FROM messages WHERE message_id=%s;"

    @staticmethod
    def select_all_by_reference_id():
        return "SELECT message_id, message_type, reference_id FROM messages WHERE message_type=%s and reference_id=%s;" 

    @staticmethod
    def select_team_by_reference_id():
        return """with proposal_team_ids as (
                    select 
                        distinct reference_id,
                        team_id
                    from 
                        messages join proposals on(messages.reference_id = proposals.proposal_id)
                    where reference_id=%(ref_id)s
                ),
                scrim_team_ids as (
                    select 
                        distinct reference_id,
                        team_id
                    from 
                        messages join scrims on(messages.reference_id = scrims.scrim_id)
                    where reference_id=%(ref_id)s
                )
                select
                    team_id,
                    team_name,
                    contact,
                    contact_type
                from 
                    (proposal_team_ids full join scrim_team_ids using (team_id)) natural join teams;
        """

class MessageTypes:
    @staticmethod
    def select_id_by_longname():
        return "SELECT type_id FROM message_types WHERE longname=%s;"

    @staticmethod
    def select_longname_by_id():
        return "SELECT longname FROM message_types WHERE type_id=%s;"

class Matches:
    @staticmethod
    def insert():
        return "INSERT INTO matches(map_id, scrim_id) values(%s, %s) RETURNING match_id;"

    @staticmethod
    def select_by_scrim_id():
        return "SELECT match_id, map_id, scrim_id FROM matches WHERE scrim_id=%s;"

class Proposals:

    @staticmethod
    def count_by_team_id_and_played_at():
        return """select 
                	count(*)
                  from 
	                proposals join scrims using (scrim_id)
                  where
	                proposals.team_id=%s and played_at=%s and rejected=false;
    """
      
    @staticmethod
    def insert():
        return "INSERT INTO proposals(scrim_id, team_id) values(%s, %s) RETURNING proposal_id;"

    @staticmethod
    def select():
        return "SELECT proposal_id, scrim_id, team_id, rejected FROM proposals WHERE proposal_id=%s;"

    @staticmethod
    def select_id_by_team_and_scrim_id():
        return "SELECT proposal_id FROM proposals WHERE team_id=%s and scrim_id=%s;"

    @staticmethod
    def select_proposal_from_scrim_id():
        return "Select proposal_id, scrim_id, team_id, rejected FROM proposals WHERE scrim_id=%s;"

    @staticmethod
    def select_proposal_from_team_id():
        return "SELECT proposal_id, scrim_id, team_id, rejected FROM proposals WHERE team_id=%s;"

    @staticmethod
    def select_scrim_id():
        return "SELECT scrim_id FROM proposals WHERE proposal_id=%s;"

    @staticmethod
    def set_rejected():
        return "UPDATE proposals SET rejected=TRUE WHERE proposal_id=%s;"

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
    def select():
        return "SELECT scrim_id, team_id, scrim_type, played_at, against FROM scrims WHERE scrim_id=%s;"

    @staticmethod
    def select_by_played_at():
        return "SELECT scrim_id, team_id, scrim_type, played_at, against FROM scrims WHERE played_at=%s;"

    @staticmethod
    def select_scrim_type_id():
        return "SELECT scrim_type FROM scrims WHERE scrim_id=%s;"

    @staticmethod
    def select_team_id():
        return "SELECT team_id FROM scrims WHERE scrim_id=%s;"

    @staticmethod
    def update_against():
        return "UPDATE scrims SET against=%s WHERE scrim_id=%s;"

class ScrimTypes:
    @staticmethod
    def select_id_by_longname():
        return "SELECT type_id FROM scrim_types WHERE longname=%s;"

    @staticmethod
    def select_longname_by_id():
        return "SELECT longname FROM scrim_types WHERE type_id=%s;"

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
