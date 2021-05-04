import scrim_finder.schedule_bot.bot_settings as bot_settings
import discord
import re

from scrim_finder.schedule_bot.command import CommandParser

class SchedulerBot(discord.Client):

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

if __name__ == "__main__":
    client = SchedulerBot()
    client.run(bot_settings.bot_token)
