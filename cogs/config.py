import discord
from discord.ext import commands
import settings
import mysql.connector
import re
from core._errors import Error


class Config(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.group(aliases=["conf", "settings"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(":x: Invalid arguments. Command usage: `config <option> <extra>`.\n\n"
                           "**Options:**\n"
                           "**1.** `config maxcount <number>`\n"
                           "**2.** `config timeoutrole <role>`\n"
                           "**3.** `config prefix <prefix>`")
            ctx.command.reset_cooldown(ctx)

    @config.command()
    async def maxcount(self, ctx, count=None):
        try:
            count = int(count)

            if str(count) != "-1" and count <= 0:
                count = int("error")
        except Exception:
            await ctx.send(":x: You didn't give a valid number. `config maxount <number | -1>`\n*Use* `-1` *to reset the maxcount.*")
            return

        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute("UPDATE guildSettings SET maxCount = %s WHERE guild = %s", (count, ctx.guild.id))
        db.commit()
        db.close()

        if count == -1:
            await ctx.send(f"You've updated the maximum count to **9223372036854775807**.")
        else:
            await ctx.send(f"You've updated the maximum count to **{count}**.")

    @config.command()
    async def timeoutrole(self, ctx, role: discord.Role = None):
        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        if role is None:
            cursor.execute("UPDATE guildSettings SET timeoutRole = 0 WHERE guild = %s", (ctx.guild.id,))
            db.commit()

            await ctx.send(f"You've removed the timeout role.")
        else:
            cursor.execute("UPDATE guildSettings SET timeoutRole = %s WHERE guild = %s", (role.id, ctx.guild.id))
            db.commit()

            await ctx.send(f"You've updated the timeout role to **{role.mention}**.")
        db.close()

    @config.command()
    async def prefix(self, ctx, prefix=None):
        prefix = prefix or "c!"
        prefix = str(prefix)

        if len(prefix) > 5:
            await ctx.send(":x: The prefix cannot be longer than 5 characters.")
            return

        valid_chars = "`A-Z`, `a-z`, `!`, `<`, `>`, `~`, `.`, `,`, `^`, `-`, `$`, `/`, `%`, `+`, `=`"
        regex = re.sub(r'[^A-Za-z!~,.<>^/$%=+-]', '', prefix)

        if prefix == regex:
            db = mysql.connector.connect(host=settings.host, user=settings.user,
                                         passwd=settings.passwd, database=settings.database)
            cursor = db.cursor()

            cursor.execute("UPDATE guildSettings SET prefix = %s WHERE guild = %s", (prefix, ctx.guild.id))
            db.commit()
            db.close()

            await ctx.send(f"You've updated the prefix to **{prefix}**.")
        else:
            await ctx.send(f":x: Prefix contains invalid characters.\nValid characters are:\n{valid_chars}")

    @config.error
    async def config_error(self, ctx, error):
        error_class = Error(ctx, error, self.client)
        await error_class.error_check()


def setup(client):
    client.add_cog(Config(client))
