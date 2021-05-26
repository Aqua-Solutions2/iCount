import discord
from discord.ext import commands
import mysql.connector
import settings
from core._errors import Error


class UnlinkCmd(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @unlink.error
    async def link_error(self, ctx, error):
        error_class = Error(ctx, error, self.client)
        await error_class.error_check()


def setup(client):
    client.add_cog(UnlinkCmd(client))
