from scrim_finder.schedule_bot.command import Command

class Clear(Command):

    @staticmethod
    def command_string():
        return "=clear"

    async def clear_all(self, channel):
        async for message in channel.history(limit=100):
            if message.author.name == "AnalyticsBot":
                await message.delete()

    async def clear_errors(self, channel):
        async for message in channel.history(limit=100):
            if message.author.name == "AnalyticsBot" and message.content.startswith("Error:"):
                await message.delete()

    async def clear_most_recent(self, channel):
        async for message in channel.history(limit=100, oldest_first=False):
            if message.author.name == "AnalyticsBot":
                return await message.delete()

    async def execute(self, message, *args):
        try:
            print([mention.id for mention in message.channel_mentions])

        except Exception as e:
            print(e)
            await message.channel.send(content="Error: An exception occurred while processing your request :(")
        finally:
            await message.delete()

    @staticmethod
    def help():
        return "This command will register this server for use with the bot!\nPlease use the command as =register #schedule-channel #confirmation-channel\n\nThe schedule channel is used for the bot to post and update a schedule; the confirmation channel is used to confirm scrims."

    def has_access(self, user_id, guild_id):
        """ Everyone can run clear commands. """
        return True

    def can_execute(self, user_id, guild_id, *args):
        """ No restricted arguments. """
        return True
