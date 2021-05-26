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
                message_by_bot = 0

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
                                message_by_bot = await channel.send(f"**{message.author}**: {message_inhoud}")
                            else:
                                if emote_react == 1:
                                    await message.add_reaction(emoji=settings.succes_emote)

                            cursor.execute("SELECT * FROM userData WHERE user = %s AND guild = %s", (message.author.id, guild))
                            user_data = cursor.fetchone()

                            if user_data is None:
                                cursor.execute(settings.insert_userdata, (guild, message.author.id, 1))
                                user_score = 1
                            else:
                                cursor.execute(f"UPDATE userData SET count = count + 1 WHERE guild = %s AND user = %s", (guild, message.author.id))
                                user_score = user_data[3] + 1
                            db.commit()

                            if maxcount == -1:
                                maxcount = 9223372036854775807

                            if message_inhoud >= maxcount:
                                number = 0
                                embed_desc = f"Maximum count archieved ({maxcount})! Count reset to 0."
                            else:
                                number += 1

                            new_number = number

                            cursor.execute("SELECT * FROM userNotify WHERE user = %s AND guild = %s", (message.author.id, guild))
                            notifications = cursor.fetchall()

                            for notification in notifications:
                                try:
                                    if notification[4] == 0 and notification[3] == number:
                                        await message.author.send(f"**Automatic Notification:** The count is now on `{number}`.")
                                    elif notification[4] == 1 and notification[3] % number == 0:
                                        await message.author.send(f"**Automatic Notification:** The count is now on `{number}`.")
                                except Exception:
                                    pass

                            cursor.execute("SELECT * FROM guildAutomation WHERE guild = %s", (guild,))
                            automations = cursor.fetchall()

                            for automation in automations:
                                try:
                                    event = automation[2]
                                    action = automation[3]
                                    am_number = automation[4]

                                    doorgaan = True

                                    if event == 1 and number == am_number:
                                        pass
                                    elif event == 2 and number % am_number == 0:
                                        pass
                                    elif event == 3 and str(number).startswith(str(am_number)):
                                        pass
                                    elif event == 4 and str(number).endswith(str(am_number)):
                                        pass
                                    elif event == 5 and user_score == am_number:
                                        pass
                                    else:
                                        doorgaan = False

                                    if doorgaan:
                                        if action == 1:
                                            role = get(message.guild.roles, id=automation[5])
                                            await message.author.add_roles(role)
                                        elif action == 2:
                                            role = get(message.guild.roles, id=automation[5])
                                            await message.author.remove_roles(role)
                                        elif action == 3:
                                            all_pins = await channel.pins()
                                            if len(all_pins) >= 50:
                                                oldest_pin = all_pins[-1]
                                                old_pin = await message.channel.fetch_message(oldest_pin.id)
                                                await old_pin.unpin(reason="Removed oldest pin because channel reached pin limit.")

                                            if message_by_bot == 0:
                                                await message.pin(reason="Automation Pin by iCount.")
                                            else:
                                                await message_by_bot.pin(reason="Automation Pin by iCount.")
                                        elif action == 4:
                                            am_channel = get(message.guild.channels, id=automation[5])
                                            await am_channel.send(automation[6])
                                        elif action == 5:
                                            new_number = 0
                                            embed_desc = "The count has been reset to 0."
                                        elif action == 6:
                                            await message.channel.set_permissions(message.guild.default_role, send_messages=False)
                                except Exception:
                                    pass
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
                                embed_desc = "Wrong number! The count has been reset to 0."
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
