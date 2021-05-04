import discord
from discord.ext import commands
import settings
import mysql.connector
import json
import os
from virustotal_python import Virustotal


class CogsImport(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="import")
    # @commands.is_owner()
    async def import_cmd(self, ctx):
        if False and str(ctx.message.attachments) == "[]":
            await ctx.send("You have to upload a file (.json) to this command.")
            return
        else:
            # split_filename = str(ctx.message.attachments).split("filename='")[1]
            # bestandsnaam = str(split_filename).split("' ")[0]
            bestandsnaam = ""

            if True or bestandsnaam.endswith(".json"):
                # try:
                #     os.remove(f"data/importdata/{ctx.guild.id}.json")
                # except Exception:
                #     pass

                # import_bestand = await ctx.message.attachments[0].save(fp=f"data/importdata/{ctx.guild.id}.json")

                file_path = f"data/importdata/eicar.json"
                bestand = {
                    "file": (os.path.basename(file_path), open(os.path.abspath(file_path), "rb"))
                }
            else:
                await ctx.send("The file needs to have the extension `.json`. Other filetypes are not supported.")
                return

        with Virustotal(API_KEY=settings.vtotal_api_key, API_VERSION="v3") as vtotal:
            return_data = vtotal.request("files", files=bestand, method="POST")

        return

        with open(f"data/importdata/{ctx.guild.id}.json", "r") as import_file:
            data = json.load(import_file)

        prefix = data['prefix']
        channel_id = data['channel-id']
        maxcount = data['maxcount']
        timeoutrole = data['timeoutrole']
        language = data['language']
        count = data['count']
        lastuser = data['lastuser']
        modules = data['modules']
        userdata = data['userdata']
        notifications = data['notifications']
        automation = data['automation']

        import_file.close()

        db = mysql.connector.connect(host=settings.host, database=settings.database,
                                     user=settings.user, passwd=settings.passwd)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM guildSettings WHERE guild = %s", (ctx.guild.id,))
        guild_settings = cursor.fetchone()

        if guild_settings is None:
            print(f"[ERROR] guild_settings not found onCount.py (Guild: {ctx.guild.id}, ID: {ctx.guild.id})")
            db.close()
            return

        cursor.execute("SELECT * FROM guildData WHERE guild = %s", (ctx.guild.id,))
        guild_data = cursor.fetchone()

        if guild_data is None:
            guild_data = (ctx.guild.id, 0, 0)

        cursor.execute("SELECT * FROM guildModules WHERE guild = %s", (ctx.guild.id,))
        guild_modules = cursor.fetchone()

        if guild_modules is None:
            guild_modules = (ctx.guild.id, 0, 0, 0, 0, 0)

        cursor.execute("SELECT * FROM guildAutomation WHERE guild = %s", (ctx.guild.id,))
        guild_automation = cursor.fetchall()

        if guild_automation is None:
            guild_automation = ()

        cursor.execute("SELECT * FROM userData WHERE guild = %s", (ctx.guild.id,))
        user_data = cursor.fetchall()

        if user_data is None:
            user_data = ()

        cursor.execute("SELECT * FROM userNotify WHERE guild = %s", (ctx.guild.id,))
        user_notify = cursor.fetchall()

        if user_notify is None:
            user_notify = ()

        db.close()

        user_data_dict = {}
        for user in user_data:
            user_data_dict[f"{user[2]}"] = user[3]

        notifications_data = {}
        for notification in user_notify:
            user_data_dict[f"{notification[0]}"] = {
                "user": notification[2],
                "mode": notification[4],
                "number": notification[3]
            }

        automation_data = {}
        for automation in guild_automation:
            user_data_dict[f"{automation[0]}"] = {
                "trigger": automation[2],
                "action": automation[3],
                "extra": automation[4]
            }

        try:
            os.remove(f"data/exportdata/{ctx.guild.id}.json")
        except Exception:
            pass

        export_data = {
            "guild-id": ctx.guild.id,
            "prefix": guild_settings[1],
            "channel-id": guild_settings[2],
            "maxcount": guild_settings[3],
            "timeoutrole": guild_settings[4],
            "language": guild_settings[6],
            "count": guild_data[1],
            "lastuser": guild_data[2],
            "modules": {
                "allow-spam": guild_modules[1],
                "restart-error": guild_modules[2],
                "emote-react": guild_modules[3],
                "recover-mode": guild_modules[4],
                "post-embed": guild_modules[5]
            },
            "userdata": user_data_dict,
            "notifications": notifications_data,
            "automation": automation_data
        }

        with open(f"data/exportdata/{ctx.guild.id}.json", "w") as export_file:
            json.dump(export_data, export_file, indent=4)

        try:
            await ctx.author.send(f"Database Export data for guild {ctx.guild} ({ctx.guild.id})", file=discord.File(f"data/exportdata/{ctx.guild.id}.json"))
            await ctx.send(":white_check_mark: Export Data send into you DMs.")
        except discord.errors.Forbidden:
            await ctx.send(":x: I cannot send a message to you. Please enable private messaging in the privacy settings of this server.")


def setup(client):
    client.add_cog(CogsImport(client))
