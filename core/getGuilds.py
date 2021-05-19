from discord.ext import commands


class CoreGetGuilds(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def getguilds(self, ctx):
        await ctx.author.send(f"Guilds: {len(self.client.guilds)}")


def setup(client):
    client.add_cog(CoreGetGuilds(client))
