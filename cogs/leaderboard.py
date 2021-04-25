import discord
from discord.ext import commands
import settings
import mysql.connector


class Leaderboard(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["lb", "scoreboard", "top", "sb"])
    async def leaderboard(self, ctx, page: int = 1):
        pre_offset = page - 1
        offset = pre_offset * 10

        after_str = ""
        first_followup = offset

        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM userData WHERE guild = %s ORDER BY count DESC LIMIT 10 OFFSET %s", (ctx.guild.id, offset))
        result = cursor.fetchall()
        db.close()

        for row in result:
            first_followup = first_followup + 1

            try:
                top_name = self.client.get_user(row[2])
            except AttributeError:
                top_name = "Unknown#0000"

            total_user_counts = f"score: {row[3]}"

            pre_str = f"**{first_followup}.** {top_name} • **{total_user_counts}**\n"
            after_str = after_str + pre_str

        if after_str == "":
            after_str = "No Data Found!"

        embed = discord.Embed(
            description=f"{after_str}",
            color=settings.embedcolor
        )
        embed.set_author(name=f"{ctx.guild} Scoreboard", icon_url=f"{ctx.guild.icon_url}")
        embed.set_footer(text=f"{settings.footer} | Page {page}")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Leaderboard(client))
