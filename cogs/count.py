import discord
from discord.ext import commands
import settings
import mysql.connector


class CurrentCount(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["currentcount"])
    async def count(self, ctx):
        guild = ctx.guild.id
        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM guildData WHERE guild = %s", (guild,))
        guild_data = cursor.fetchone()

        user = self.client.get_user(guild_data[2])

        if user is not None:
            user_text = f"\nThe last user who typed was: {user}."
        else:
            user_text = ""

        embed = discord.Embed(
            title=f"Current Count",
            description=f"The Current count is: {guild_data[1]}{user_text}",
            color=settings.embedcolor
        )
        embed.set_author(name=self.client.user.display_name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text=settings.footer)
        await ctx.send(embed=embed)
        db.close()


def setup(client):
    client.add_cog(CurrentCount(client))
