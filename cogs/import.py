from discord.ext import commands
import settings
import mysql.connector
import json
from core import _checks as checks
from core._errors import Error


class CogsImport(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="import")
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def import_cmd(self, ctx):
        if ctx.author.id == ctx.guild.owner_id:
            if str(ctx.message.attachments) == "[]":
                await ctx.send(":x: You have to upload a file (.json) to this command.")
                ctx.command.reset_cooldown(ctx)
                return

            if ctx.message.attachments[0].size > 25000:
                await ctx.send(":x: The file is larger than 25kb, we do not allow files bigger than 25kb.")
                ctx.command.reset_cooldown(ctx)
                return

            split_filename = str(ctx.message.attachments).split("filename='")[1]
            bestandsnaam = str(split_filename).split("' ")[0]

            if bestandsnaam.lower().endswith(".json"):
                import_bestand = await ctx.message.attachments[0].read()
            else:
                await ctx.send(":x: The file needs to have the extension `.json`. Other filetypes are not supported.")
                ctx.command.reset_cooldown(ctx)
                return

            if not str(import_bestand).startswith("b'{"):
                await ctx.send(":x: Invalid JSON-file.")
                ctx.command.reset_cooldown(ctx)
                return

            data = json.loads(import_bestand)

            try:
                guild_id = data["guild-id"]
                prefix = data['prefix']
                channel_id = data['channel-id']
                maxcount = data['maxcount']
                timeoutrole = data['timeoutrole']
                language = 'en'  # data['language']  # Coming Soon
                count = data['count']
                lastuser = data['lastuser']
                modules = data['modules']
                userdata = data['userdata']
                notifications = data['notifications']
                automation = data['automation']
            except KeyError:
                await ctx.send(":x: Invalid JSON-file.")
                return

            check = checks.Checks(ctx)
            prefix = check.prefix(prefix)
            maxcount = check.maxcount(maxcount)
            lastuser = check.ids(lastuser)
            count = check.count(count, maxcount)
            channel_id = check.id_in_guild(channel_id, guild_id)
            timeoutrole = check.id_in_guild(timeoutrole, guild_id)
            modules = check.modules(modules)

            db = mysql.connector.connect(host=settings.host, database=settings.database,
                                         user=settings.user, passwd=settings.passwd)
            cursor = db.cursor()

            # Remove all data from database.
            cursor.execute("DELETE FROM guildSettings WHERE guild = %s", (ctx.guild.id,))
            cursor.execute("DELETE FROM guildData WHERE guild = %s", (ctx.guild.id,))
            cursor.execute("DELETE FROM guildModules WHERE guild = %s", (ctx.guild.id,))
            db.commit()

            # Insert all data into database.
            cursor.execute(settings.insert_guildsettings, (ctx.guild.id, f"{prefix}", channel_id, maxcount, timeoutrole, 0, language))
            cursor.execute(settings.insert_guilddata, (ctx.guild.id, count, lastuser))
            cursor.execute(settings.insert_guildmodules, (ctx.guild.id, modules[0], modules[1], modules[2], modules[3], modules[4]))
            db.commit()

            for user in userdata:
                try:
                    user_count = int(userdata[user])
                    user_id = int(user)

                    if user_count >= 0 and user_id > 0:
                        cursor.execute("DELETE FROM userData WHERE guild = %s AND user = %s", (ctx.guild.id, user_id))
                        db.commit()

                        cursor.execute(settings.insert_userdata, (ctx.guild.id, user_id, user_count))
                        db.commit()
                except Exception:
                    pass

            users = []
            for notification in notifications:
                try:
                    user_id = int(notifications[notification]['user'])
                    mode = int(notifications[notification]['mode'])
                    number = int(notifications[notification]['number'])

                    if mode == 1 or mode == 0:
                        pass
                    else:
                        continue

                    if number <= 0:
                        continue

                    if user_id <= 0:
                        continue

                    if user_id not in users:
                        users.append(user_id)
                        cursor.execute("DELETE FROM userNotify WHERE guild = %s AND user = %s", (ctx.guild.id, user_id))
                        db.commit()

                    cursor.execute(settings.insert_usernotify, (ctx.guild.id, user_id, number, mode))
                    db.commit()
                except Exception:
                    pass

            for flow in automation:
                try:
                    trigger = int(automation[flow]['trigger'])
                    action = int(automation[flow]['action'])
                    number = int(automation[flow]['number'])
                    action_id = int(automation[flow]['actionId'])
                    msg = automation[flow]['message']

                    if number >= 10:
                        cursor.execute("DELETE FROM guildAutomation WHERE guild = %s AND triggerNr = %s AND action = %s AND number = %s", (ctx.guild.id, trigger, action, number))
                        db.commit()

                        cursor.execute(settings.insert_guildautomation, (ctx.guild.id, trigger, action, number, action_id, msg))
                        db.commit()
                except Exception:
                    pass

            await ctx.send(":white_check_mark: Imported all data.\n"
                           "*Some settings/data might not be imported correctly if you changed the file manually.*")
            db.close()

    @import_cmd.error()
    async def import_error(self, ctx, error):
        error_class = Error(ctx, error, self.client)
        await error_class.error_check()


def setup(client):
    client.add_cog(CogsImport(client))
