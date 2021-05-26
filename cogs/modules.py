import discord
from discord.ext import commands
import settings
import mysql.connector
from core._errors import Error


class Modules(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["modules"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def module(self, ctx, module=None, state=None):
        show_modules = False
        modules_list = ["allow-spam", "count-fail", "emote-react", "recover", "embed"]
        modules_db = ["allowSpam", "restartError", "emoteReact", "recoverMode", "postEmbed"]

        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM guildModules WHERE guild = %s", (ctx.guild.id,))
        guild_modules = cursor.fetchone()

        if guild_modules is None:
            guild_modules = (ctx.guild.id, 0, 0, 0, 0, 0)
            cursor.execute(settings.insert_guildmodules, guild_modules)

        if module is None:
            show_modules = True
        elif module in modules_list:
            index = modules_list.index(module)

            if state == "on":
                state = 1
            elif state == "off":
                state = 0
            else:
                await ctx.send("No valid state was given. Command usage: `module <module> <on | off>`")
                db.close()
                return

            if module == "emote-react":
                if guild_modules[1] == 1 and state == 1:
                    await ctx.send("You cannot enable `allow-spam` and `emote-react` at the same time because of the discord ratelimit.")
                    db.close()
                    return
                elif ctx.guild.member_count > 500 and state == 1:
                    await ctx.send("Sorry but your server has 500+ members. Due to performance reasons you cannot enable `emote-react`.")
                    db.close()
                    return

            cursor.execute(f"UPDATE guildModules SET {modules_db[index]} = %s WHERE guild = %s", (state, ctx.guild.id))
            db.commit()

            if state == 0:
                await ctx.send(f":white_check_mark: Module `{module}` has been disabled.")
            else:
                await ctx.send(f":white_check_mark: Module `{module}` has been enabled.")
        else:
            show_modules = True

        if show_modules:
            modules_desc = ["Allow people to count multiple times in a row.", "Resets the count when someone fails to count the correct number.", "Reacts with an emote whenever a user counts.", "Remove invalid messages when the bot restarts.", "Repost the message in an embed."]

            modules = ""

            index = 0
            for item in guild_modules:
                if item == 0 or item == 1:
                    if item == 0:
                        modules += f":black_circle: `{modules_list[index]}` {modules_desc[index]}\n"
                    else:
                        modules += f":radio_button: `{modules_list[index]}` {modules_desc[index]}\n"

                    index += 1

            embed = discord.Embed(
                title=":clipboard: Available Modules",
                description=f"Command usage: `module <module> <on | off>`\n\n"
                            f"{modules}",
                color=settings.embedcolor
            )
            embed.set_footer(text=settings.footer)
            await ctx.send(embed=embed)
        db.close()

    @module.error
    async def module_error(self, ctx, error):
        error_class = Error(ctx, error, self.client)
        await error_class.error_check()


def setup(client):
    client.add_cog(Modules(client))
