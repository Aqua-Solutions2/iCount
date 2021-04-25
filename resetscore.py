import discord
from discord.ext import commands
import mysql.connector
import settings


class ResetScore(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def resetscore(self, ctx, *, member: discord.Member):
        guild = ctx.guild.id
        db_counting = mysql.connector.connect(host=settings.host, user=settings.user, passwd=settings.passwd,
                                              database=settings.database)
        counting_cursor = db_counting.cursor()

        counting_cursor.execute(f"SELECT * FROM counting_userdata WHERE guild_id = {guild} AND user_id = {member.id}")
        result_tuple = counting_cursor.fetchone()

        if result_tuple is not None:
            counting_cursor.execute(f"DELETE FROM counting_userdata WHERE guild_id = {guild} AND user_id = {member.id}")
            db_counting.commit()

            embed = discord.Embed(
                title=f"Reset Score of {member}",
                description=f"You have succesfully reset the score of {member.mention}",
                color=settings.embedcolor
            )
        else:
            embed = discord.Embed(
                title="Reset Score",
                description=f"This user has not counted yet, so there is no score to reset.",
                color=settings.embedcolor
            )
        embed.set_author(name=self.client.user.display_name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text=settings.footer)
        await ctx.send(embed=embed)
        db_counting.close()

    @resetscore.error
    async def resetscore_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            pass


def setup(client):
    client.add_cog(ResetScore(client))
