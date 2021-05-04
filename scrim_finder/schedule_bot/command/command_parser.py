import io
import re
import requests

from scrim_finder.schedule_bot.command import Command

class CommandParser:

    def __init__(self, message):
        self.message = message

    async def run(self):
        # Strip any mentions out of the content of the message.
        message_content = re.sub(r'<.+?>', '', self.message.content).strip()
        author = self.message.author
        guild = self.message.guild

        for subclass in Command.__subclasses__():
            if message_content.lower().startswith(subclass.command_string()):
                command = subclass()
 
                if command.has_access(author.id, guild.id):
                    command_arguments = message_content.split(" ")

                    if command.can_execute(author.id, guild.id, *command_arguments):
                        if command_arguments[1] == "--help":
                            return await self.message.channel.send(content=command.help())

                        command_response = await command.execute(self.message, *command_arguments)
                    else:
                        error_message = command.execute_permission_error_message(author, guild, command_arguments)
                        return await self.message.channel.send(content=error_message)

                    command.cleanup()
                else:
                    error_message = command.access_permission_error_message(author, guild, command_arguments)
                    return await self.message.channel.send(content=error_message)

                return command_response

        print(f"Unknown command: {message_content.lower()}")
