import discord
from discord.ext import commands
import settings
import mysql.connector


class Notify(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["notifyme", "alert", "alertme"])
    async def notify(self, ctx, number=None, parameter=None):
        try:
            number = int(number)

            if number <= 0:
                number = int("error")
        except Exception:
            await ctx.send(":x: You didn't give a valid number. `notify <number> [--each]`")
            return

        if parameter is None:
            each = 0
        elif parameter == "--each":
            each = 1
        else:
            await ctx.send(":x: Invalid arguments. `notify <number> [--each]`")
            return

        user_notify_data = (ctx.guild.id, ctx.author.id, number, each)

        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM userNotify WHERE guild = %s AND user = %s", (ctx.guild.id, ctx.author.id))
        user_notify = cursor.fetchall()

        if user_notify is not None:
            if len(user_notify) > 10:
                await ctx.send("You cannot make any notifications anymore. You reached the limit of 10 notifications per server.")
                db.close()
                return

            for row in user_notify:
                if each == 0 and row[4] == 0:
                    if row[3] == number:
                        await ctx.send(":x: Notifications for that number are already enabled.")
                        db.close()
                        return
                elif each == 1 and row[4] == 0:
                    if row[3] % number == 0:
                        cursor.execute("DELETE FROM userNotify WHERE guild = %s AND user = %s AND number = %s AND everyNumber = %s", (ctx.guild.id, ctx.author.id, row[3], row[4]))
                        db.commit()
                elif each == 0 and row[4] == 1:
                    if number % row[3] == 0:
                        await ctx.send(":x: Notifications for that number are already enabled.")
                        db.close()
                        return

        cursor.execute(settings.insert_usernotify, user_notify_data)
        db.commit()
        db.close()

        await ctx.send(":white_check_mark: The notification has been enabled.")

    @commands.command(aliases=["notif", "alerts", "notiflist", "alertslist"])
    async def notifications(self, ctx):
        desc = ""
        number = 1

        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM userNotify WHERE guild = %s AND user = %s", (ctx.guild.id, ctx.author.id))
        user_notify = cursor.fetchall()

        db.close()

        if user_notify is None:
            await ctx.send(":x: You don't have any notifications.")
        elif not user_notify:
            await ctx.send(":x: You don't have any notifications.")
        else:
            for row in user_notify:
                if row[4] == 1:
                    desc += f"**{number}.** When someone counts a multiplication of **{row[3]}**. ID: `{row[0]}`\n"
                else:
                    desc += f"**{number}.** When someone counts the number **{row[3]}**. ID: `{row[0]}`\n"
                number += 1

            embed = discord.Embed(
                title=f":clipboard: Notifications of {ctx.author}",
                description=desc,
                color=settings.embedcolor
            )
            embed.set_footer(text=settings.footer)
            await ctx.send(embed=embed)

    @commands.command(aliases=["removenotif", "delalert", "removealert"])
    async def delnotif(self, ctx, option=None):
        if option != "all":
            try:
                option = int(option)

                if option <= 0:
                    option = int("error")
            except ValueError:
                await ctx.send(":x: You didn't give a valid number. `delnotif <ID | all>`")
                return

        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        if option == "all":
            cursor.execute("DELETE FROM userNotify WHERE guild = %s AND user = %s", (ctx.guild.id, ctx.author.id))
            await ctx.send(f":white_check_mark: All notifications have been deleted.")
        else:
            cursor.execute("SELECT * FROM userNotify WHERE guild = %s AND user = %s AND id = %s", (ctx.guild.id, ctx.author.id, option))
            user_notify = cursor.fetchone()

            if user_notify is None:
                await ctx.send(":x: No notification was found with that ID.")
            else:
                cursor.execute("DELETE FROM userNotify WHERE guild = %s AND user = %s AND id = %s", (ctx.guild.id, ctx.author.id, option))
                await ctx.send(f":white_check_mark: Notification `{option}` has been deleted.")
        db.commit()
        db.close()


def setup(client):
    client.add_cog(Notify(client))
