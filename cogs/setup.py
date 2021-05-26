import discord
from discord.ext import commands
import mysql.connector
import settings
from core._errors import Error


class Setup(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def setup(self, ctx):
        guild = ctx.guild.id
        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM guildSettings WHERE guild = %s", (guild,))
        guild_settings = cursor.fetchone()

        try:
            channel = self.client.get_channel(guild_settings[2])
        except Exception:
            channel = None

        if channel is None:
            counting_channel = await ctx.guild.create_text_channel('counting')
            await counting_channel.set_permissions(self.client.user, send_messages=True, read_messages=True,
                                                   add_reactions=True, embed_links=True, manage_messages=True,
                                                   read_message_history=True, external_emojis=True, manage_permissions=True)

            cursor.execute("UPDATE guildSettings SET channelId = %s WHERE guild = %s", (counting_channel.id, guild))
            cursor.execute("DELETE FROM guildData WHERE guild = %s", (guild,))
            db.commit()

            cursor.execute(settings.insert_guilddata, (guild, 0, 0))
            db.commit()

            embed_desc = f":white_check_mark: You can now use the counting features in {counting_channel.mention}"
        else:
            embed_desc = f":x: You already did the setup command!\nPlease do `{guild_settings[1]}help` if you need any help."

        embed = discord.Embed(
            description=embed_desc,
            color=settings.embedcolor
        )
        embed.set_author(name=self.client.user.display_name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text=settings.footer)
        await ctx.send(embed=embed)
        db.close()

    @setup.error
    async def setup_error(self, ctx, error):
        error_class = Error(ctx, error, self.client)
        await error_class.error_check()


def setup(client):
    client.add_cog(Setup(client))
