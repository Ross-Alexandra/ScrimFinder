from abc import abstractmethod, ABCMeta

class Command(metaclass=ABCMeta):

    def __init__(self):
        pass

    def access_permission_error_message(self, user, guild, arguments):
        return f"Error: Neither {user.name} ({user.id}) nor {guild.name} ({guild.id}) have permission for this command."

    def cleanup(self):
        pass

    def execute_permission_error_message(self, user, guild, arguments):
        return f"Error: Neither {user.name} ({user.id}) nor {guild.name} ({guild.id}) have permissions to run {arguments[0]} with {arguments[1:]}."

    @staticmethod
    @abstractmethod
    def command_string(): 
        """ The command's string which will be included when a user
            attempt to run the command. """
        
        return

    @abstractmethod
    def has_access(self, user_id, guild_id):
        """ Checks whether a discord user or guild has permissions to run this command."""
        pass

    @abstractmethod
    def can_execute(self, user_id, guild_id, args):
        """ Checks whether a discord user or guild has permissions to access data requested in args"""
        pass

    @abstractmethod
    async def execute(self, message):
        """ The code to be run when a command is executed. """
        pass

    @staticmethod
    @abstractmethod
    async def help():
        """ The usage message of this command """
        pass

    @staticmethod
    def _get_match_type(raw_string: str):
        if "scrim" in raw_string:
            return "scrim"
        elif "qual" in raw_string:
            return "qualifier"
        elif "league" in raw_string:
            return "league"
        else: 
            return None
