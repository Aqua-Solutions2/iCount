import discord
from discord.ext import commands
import mysql.connector
import settings


class UnlinkCmd(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def link(self, ctx):
        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        await ctx.channel.set_permissions(self.client.user, send_messages=True, read_messages=True, add_reactions=True,
                                          embed_links=True, manage_messages=True, read_message_history=True, external_emojis=True, manage_permissions=True)

        cursor.execute("UPDATE guildSettings SET channelId = %s WHERE guild = %s", (ctx.channel.id, ctx.guild.id))
        cursor.execute("DELETE FROM guildData WHERE guild = %s", (ctx.guild.id,))
        db.commit()

        cursor.execute(settings.insert_guilddata, (ctx.guild.id, 0, 0))
        db.commit()

        db.close()

        await ctx.send(":white_check_mark: Link Successful. You can start counting.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def unlink(self, ctx):
        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute("UPDATE guildSettings SET channelId = 0 WHERE guild = %s", (ctx.guild.id,))
        cursor.execute("DELETE FROM guildData WHERE guild = %s", (ctx.guild.id,))
        db.commit()

        db.close()

        await ctx.send(":white_check_mark: Unlink Successful.")

    @link.error
    async def link_error(self, ctx, error):
        error = getattr(error, "original", error)
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have enough permissions. You need to have the **MANAGE SERVER** permission to use this command.")
        elif isinstance(error, discord.Forbidden):
            await ctx.send("The bot has not enough permissions. Try giving the bot Administrator Permissions to run the setup command. Then you can remove those permissions.\n"
                           "If you don't want that, just make sure the bot has the permission **Manage Permissions** in the counting channel.\n"
                           "After that, run the ` c!setup ` command in the same channel.")
        else:
            raise error

    @unlink.error
    async def unlink_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have enough permissions. You need to have the **MANAGE SERVER** permission to use this command.")
        else:
            raise error


def setup(client):
    client.add_cog(UnlinkCmd(client))
