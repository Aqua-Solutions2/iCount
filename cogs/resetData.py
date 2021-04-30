import discord
from discord.ext import commands
import mysql.connector
import settings


class ManualSetup(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def resetall(self, ctx):
        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM guildSettings WHERE guild = %s", (ctx.guild.id,))
        result = cursor.fetchone()

        prefix = result[1]

        if result[2] != 0:
            cursor.execute("DELETE FROM guildSettings WHERE guild = %s", (ctx.guild.id,))
            cursor.execute("DELETE FROM guildData WHERE guild = %s", (ctx.guild.id,))
            cursor.execute("DELETE FROM guildModules WHERE guild = %s", (ctx.guild.id,))
            cursor.execute("DELETE FROM userData WHERE guild = %s", (ctx.guild.id,))
            cursor.execute("DELETE FROM userNotify WHERE guild = %s", (ctx.guild.id,))
            cursor.execute("DELETE FROM userAutomation WHERE guild = %s", (ctx.guild.id,))
            db.commit()

            cursor.execute(settings.insert_guildsettings, (f"{ctx.guild.id}", f"{settings.default_prefix}", 0, -1, 0, 0))
            db.commit()

            embed = discord.Embed(
                description=f"**Reset Complete!** Do `{prefix}setup` to activate the bot again!",
                color=settings.embedcolor
            )
        else:
            embed = discord.Embed(
                description=f"**Reset Failed!** There is no data to reset!",
                color=settings.failcolor
            )
        embed.set_author(name=self.client.user.display_name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text=settings.footer)
        await ctx.send(embed=embed)
        db.close()

    @resetall.error
    async def resetall_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("You don't have enough permissions. You need to have the **OWNER** of this Guild to use this command.")
        else:
            raise error


def setup(client):
    client.add_cog(ManualSetup(client))
