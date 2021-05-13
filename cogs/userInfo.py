import discord
from discord.ext import commands
import settings
import mysql.connector


class UserInfo(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["user"])
    async def userinfo(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author

        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM userData WHERE user = %s AND guild = %s", (member.id, ctx.guild.id))
        user_data = cursor.fetchone()

        if user_data is not None:
            user_count = user_data[3]
        else:
            user_count = 0

        db.close()

        if user_count == 1:
            await ctx.send(f"**{member}** has counted {user_count} time in this server.")
        else:
            await ctx.send(f"**{member}** has counted {user_count} times in this server.")


def setup(client):
    client.add_cog(UserInfo(client))
