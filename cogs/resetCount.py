import discord
from discord.ext import commands
import settings
import mysql.connector
from core._errors import Error


class ResetCount(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["rcount"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def resetcount(self, ctx, member: discord.Member = None):
        if member is None:
            await ctx.send(":x: You have to specify a user.")
            return

        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM userData WHERE guild = %s AND user = %s", (ctx.guild.id, member.id))
        guild_data = cursor.fetchone()

        if guild_data is None:
            await ctx.send(":x: This user hasn't counted yet.")
        else:
            cursor.execute("DELETE FROM userData WHERE guild = %s AND user = %s", (ctx.guild.id, member.id))
            db.commit()

            await ctx.send(f":white_check_mark: Removed Counting Data from {member}.")
        db.close()

    @resetcount.error
    async def resetcount_error(self, ctx, error):
        error_class = Error(ctx, error, self.client)
        await error_class.error_check()


def setup(client):
    client.add_cog(ResetCount(client))
