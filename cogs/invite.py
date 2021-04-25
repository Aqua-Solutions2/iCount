import discord
from discord.ext import commands
import settings


class InviteCmd(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(
            description=f":link: Invite me here: [Click Here](https://discord.com/api/oauth2/authorize?client_id={self.client.user.id}&permissions=805366864&redirect_uri=https%3A%2F%2Fdiscord.gg%2FY43Ydu446p&scope=bot)",
            color=settings.embedcolor
        )
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(InviteCmd(client))
