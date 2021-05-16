import discord
from discord.ext import commands
import mysql.connector
import settings
from discord.utils import get


class EventsCounting(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot is False:
            bericht = str(message.content)
            if bericht.startswith("!"):
                return

            db = mysql.connector.connect(host=settings.host, database=settings.database,
                                         user=settings.user, passwd=settings.passwd)
            cursor = db.cursor()

            guild = message.guild.id
            cursor.execute("SELECT * FROM guildSettings WHERE guild = %s", (guild,))
            guild_settings = cursor.fetchone()

            if guild_settings is None:
                print(f"[ERROR] guild_settings not found onCount.py (Guild: {message.guild}, ID: {guild})")
                db.close()
                return

            channel_id = guild_settings[2]
            timeoutrole = guild_settings[4]
            maxcount = guild_settings[3]

            if message.channel.id == channel_id:
                # tijdelijke variable
                embed_desc = None
                new_number = None

                try:
                    channel = self.client.get_channel(channel_id)
                except Exception:
                    print(f"[ERROR] Invalid channel onCount.py (Guild: {message.guild}, ID: {guild})")
                    db.close()
                    return

                cursor.execute("SELECT * FROM guildModules WHERE guild = %s", (guild,))
                guild_modules = cursor.fetchone()

                if guild_modules is None:
                    guild_modules = (guild, 0, 0, 0, 0, 0)

                allow_spam = guild_modules[1]
                restart_error = guild_modules[2]
                emote_react = guild_modules[3]
                post_embed = guild_modules[5]

                cursor.execute("SELECT * FROM guildData WHERE guild = %s", (guild,))
                guild_data = cursor.fetchone()

                if guild_data is None:
                    print(f"[ERROR] guild_data not found onCount.py (Guild: {message.guild}, ID: {guild})")
                    db.close()
                    return

                last_user = guild_data[2]
                number = guild_data[1]

                if allow_spam == 1:
                    last_user = -1

                if message.author.id == last_user:
                    await message.delete()
                else:
                    try:
                        message_inhoud = int(message.content)
                        if message_inhoud == number + 1:
                            if post_embed == 1:
                                await message.delete()
                                await channel.send(f"**{message.author}**: {message_inhoud}")
                            else:
                                if emote_react == 1:
                                    await message.add_reaction(emoji=settings.succes_emote)

                            cursor.execute("SELECT user FROM userData WHERE user = %s AND guild = %s", (message.author.id, guild))
                            user_data = cursor.fetchone()

                            if user_data is None:
                                cursor.execute(settings.insert_userdata, (guild, message.author.id, 1))
                            else:
                                cursor.execute(f"UPDATE userData SET count = count + 1 WHERE guild = %s AND user = %s", (guild, message.author.id))
                            db.commit()

                            if maxcount == -1:
                                maxcount = 9223372036854775807

                            if message_inhoud >= maxcount:
                                number = 0
                                embed_desc = f"Maximum count archieved ({maxcount})! Count reset to 0."
                            else:
                                number += 1

                            new_number = number
                        else:
                            if restart_error == 0:
                                await message.delete()
                            else:
                                if post_embed == 1:
                                    await message.delete()
                                    await channel.send(f"**{message.author}**: {message_inhoud}")
                                else:
                                    if emote_react == 1:
                                        await message.add_reaction(emoji=settings.error_emote)

                                new_number = 0
                                embed_desc = "Wrong number! The count has now been reset to 0."
                    except ValueError:
                        await message.delete()

                if new_number is not None:
                    cursor.execute(f"UPDATE guildData SET lastUser = %s, currentCount = %s WHERE guild = %s", (message.author.id, new_number, guild))
                    db.commit()

                if channel is not None and embed_desc is not None:
                    embed = discord.Embed(
                        title="Count Reset!",
                        description=f"{embed_desc}",
                        color=settings.embedcolor
                    )
                    embed.set_author(name=self.client.user.display_name, icon_url=self.client.user.avatar_url)
                    embed.set_footer(text=settings.footer)
                    await channel.send(embed=embed)

                    try:
                        if timeoutrole != 0:
                            role = get(message.guild.roles, id=timeoutrole)

                            if role is not None:
                                await message.author.add_roles(role)
                    except discord.errors.Forbidden:
                        await channel.send(":x: I have no permission to give the user a role.\n"
                                           "Please make sure I have the Manage roles permission and that my role is above the timeout role.")
            db.close()


def setup(client):
    client.add_cog(EventsCounting(client))
