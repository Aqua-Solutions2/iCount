from discord.ext import commands


class EventsOnReady(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        bot_name = self.client.user.display_name
        print(f"[{bot_name}] The bot is online and ready to use!")


def setup(client):
    client.add_cog(EventsOnReady(client))
