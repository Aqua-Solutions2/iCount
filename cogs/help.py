import discord
from discord.ext import commands
import settings
import mysql.connector
from core._errors import Error


class HelpMsg(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="help")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def helpcmd(self, ctx):
        db = mysql.connector.connect(host=settings.host, database=settings.database,
                                     user=settings.user, passwd=settings.passwd)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM guildSettings WHERE guild = %s", (ctx.guild.id,))
        guild_settings = cursor.fetchone()

        if guild_settings is None:
            print(f"[ERROR] guild_settings not found help.py (Guild: {ctx.guild}, ID: {ctx.guild.id})")
            prefix = settings.default_prefix
        else:
            prefix = guild_settings[1]

        db.close()

        if ctx.author.id == ctx.guild.owner_id:
            embed = discord.Embed(
                description=f"**__Owner Commands__**\n"
                            f"\n• **{prefix}resetall** - Remove all data from the bot in the guild."
                            f"\n• **{prefix}export** - Export all the data into a .JSON file."
                            f"\n• **{prefix}import** - Import all the data from .JSON file. (upload the file with the command)"
                            f"\n\n**__Staff Commands__**\n"
                            f"\n• **{prefix}setup** - Quickly set up a counting channel."
                            f"\n• **{prefix}link** - Link a counting channel manually."
                            f"\n• **{prefix}unlink** - Unlink the current counting channel."
                            f"\n• **{prefix}module <name> [on | off]** - Enable or disable modules."
                            f"\n• **{prefix}resetscore <name>** - Reset a user's score."
                            f"\n• **{prefix}automations** - Get a list of all the automations."
                            f"\n• **{prefix}create-automation <trigger> <action> [extra]** - Add an automation."
                            f"\n• **{prefix}delete-automation <id>** - Remove an automation."
                            f"\n• **{prefix}setcount <number>** - Set the count."
                            f"\n\n**__Member Commands__**\n"
                            f"\n• **{prefix}help** - Displays this Embed."
                            f"\n• **{prefix}ping** - Get the latency and uptime of the bot."
                            f"\n• **{prefix}invite** - Get an invite to add the bot."
                            f"\n• **{prefix}notifications** - Get a list of your notifications in the server."
                            f"\n• **{prefix}notify [each] <count>** - Get a notification whenever the server reach whatever count you want."
                            f"\n• **{prefix}del-notification <id>** - Remove a notification."
                            f"\n• **{prefix}leaderboard** - Get a leaderboard with members that counted the most."
                            f"\n• **{prefix}userinfo <name>** - See how many times you counted in the server."
                            f"\n• **{prefix}count** - Tells you on which number the count is.",
                color=settings.embedcolor
            )
        else:
            embed = discord.Embed(
                description=f"\n\n**__Staff Commands__**\n"
                            f"\n• **{prefix}setup** - Quickly set up a counting channel."
                            f"\n• **{prefix}link** - Link a counting channel manually."
                            f"\n• **{prefix}unlink** - Unlink the current counting channel."
                            f"\n• **{prefix}module <name> [on | off]** - Enable or disable modules."
                            f"\n• **{prefix}resetscore <name>** - Reset a user's score."
                            f"\n• **{prefix}automations** - Get a list of all the automations."
                            f"\n• **{prefix}create-automation <trigger> <action> [extra]** - Add an automation."
                            f"\n• **{prefix}delete-automation <id>** - Remove an automation."
                            f"\n• **{prefix}setcount <number>** - Set the count."
                            f"\n\n**__Member Commands__**\n"
                            f"\n• **{prefix}help** - Displays this Embed."
                            f"\n• **{prefix}ping** - Get the latency and uptime of the bot."
                            f"\n• **{prefix}invite** - Get an invite to add the bot."
                            f"\n• **{prefix}notifications** - Get a list of your notifications in the server."
                            f"\n• **{prefix}notify <count> [--each]** - Get a notification whenever the server reach whatever count you want."
                            f"\n• **{prefix}del-notification <id>** - Remove a notification."
                            f"\n• **{prefix}leaderboard** - Get a leaderboard with members that counted the most."
                            f"\n• **{prefix}userinfo <name>** - See how many times you counted in the server."
                            f"\n• **{prefix}count** - Tells you on which number the count is.",
                color=settings.embedcolor
            )
        embed.set_author(name=self.client.user.display_name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text=settings.footer)
        await ctx.send(embed=embed)

    @helpcmd.error
    async def help_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            db = mysql.connector.connect(host=settings.host, database=settings.database,
                                         user=settings.user, passwd=settings.passwd)
            cursor = db.cursor()

            cursor.execute("SELECT * FROM guildSettings WHERE guild = %s", (ctx.guild.id,))
            guild_settings = cursor.fetchone()

            if guild_settings is None:
                print(f"[ERROR] guild_settings not found help.py (Guild: {ctx.guild}, ID: {ctx.guild.id})")
                prefix = settings.default_prefix
            else:
                prefix = guild_settings[1]

            db.close()

            embed = discord.Embed(
                description=f"\n• **{prefix}help** - Displays this Embed."
                            f"\n• **{prefix}ping** - Get the latency and uptime of the bot."
                            f"\n• **{prefix}invite** - Get an invite to add the bot."
                            f"\n• **{prefix}notifications** - Get a list of your notifications in the server."
                            f"\n• **{prefix}notify [each] <count>** - Get a notification whenever the server reach whatever count you want."
                            f"\n• **{prefix}del-notification <id>** - Remove a notification."
                            f"\n• **{prefix}leaderboard** - Get a leaderboard with members that counted the most."
                            f"\n• **{prefix}userinfo <name>** - See how many times you counted in the server."
                            f"\n• **{prefix}count** - Tells you on which number the count is.",
                color=settings.embedcolor
            )
            embed.set_author(name=self.client.user.display_name, icon_url=self.client.user.avatar_url)
            embed.set_footer(text=settings.footer)
            await ctx.send(embed=embed)
        else:
            error_class = Error(ctx, error, self.client)
            await error_class.error_check()


def setup(client):
    client.add_cog(HelpMsg(client))
