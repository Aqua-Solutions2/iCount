from discord.ext import commands
import settings
import mysql.connector


class SetCount(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["set-count"])
    @commands.has_permissions(manage_guild=True)
    async def setcount(self, ctx, count=None):
        db = mysql.connector.connect(host=settings.host, database=settings.database,
                                     user=settings.user, passwd=settings.passwd)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM guildSettings WHERE guild = %s", (ctx.guild.id,))
        guild_settings = cursor.fetchone()

        if guild_settings is None:
            await ctx.send(":x: You don't have a counting channel. Set one up first.")
        else:
            try:
                count = int(count)

                if 0 <= count <= 1000000000000000:
                    pass
                else:
                    count = int("error")

                cursor.execute("UPDATE guildData SET currentCount = %s WHERE guild = %s", (count - 1, ctx.guild.id,))
                db.commit()

                try:
                    counting_channel = self.client.get_channel(guild_settings[2])

                    if counting_channel is not None:
                        await counting_channel.send(f"**New Count:** {count - 1}")
                    else:
                        await ctx.send("I could not find the counting channel.")
                except Exception:
                    await ctx.send("I cannot send a message in the counting channel.")

                await ctx.send(f"The count has succesfully been set to {count}.")
            except ValueError:
                await ctx.send(":x: You didn't give a valid number between 0 and 1000000000000000.")

        db.close()

    @setcount.error
    async def setcount_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have enough permissions. You need at least `Manage Server` to use this command.")
        else:
            raise error


def setup(client):
    client.add_cog(SetCount(client))
