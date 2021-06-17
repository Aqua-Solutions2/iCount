from discord.ext import commands
import settings
import mysql.connector
from core._errors import Error
from core import  _checks as checks


class SetCount(commands.Cog):
    max_count = 5000000000000000

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["set-count"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def setcount(self, ctx, count=None):
        check = checks.Checks(ctx)
        count = check.count(count, self.max_count)

        if count == 0:
            await ctx.send(f":x: You didn't give a valid number. `setcount <1 - {self.max_count}>`")
            return

        db = mysql.connector.connect(host=settings.host, database=settings.database,
                                     user=settings.user, passwd=settings.passwd)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM guildSettings WHERE guild = %s", (ctx.guild.id,))
        guild_settings = cursor.fetchone()

        if guild_settings is None:
            await ctx.send(":x: You don't have a counting channel. Set one up first.")
        else:
            cursor.execute("UPDATE guildData SET currentCount = %s WHERE guild = %s", (count - 1, ctx.guild.id,))
            db.commit()

            try:
                counting_channel = self.client.get_channel(guild_settings[2])

                if counting_channel is not None:
                    await counting_channel.send(f"**New Count:** {count - 1}")
                else:
                    await ctx.send(":x: I could not find the counting channel.")
            except Exception:
                await ctx.send(":x: I cannot send a message in the counting channel.")

            await ctx.send(f":white_check_mark: The count has succesfully been set to {count}.")

        db.close()

    @setcount.error
    async def setcount_error(self, ctx, error):
        error_class = Error(ctx, error, self.client)
        await error_class.error_check()


def setup(client):
    client.add_cog(SetCount(client))
