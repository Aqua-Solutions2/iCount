import asyncio
import discord
from discord.ext import commands
import settings
import mysql.connector
from discord.utils import get

"""
Events:
0. null
1. On Number X
2. Each X Number
3. Starts with X
4. Ends With X
5. When score of user reaches X
6. Regex (SOON)

Actions:
0. null
1. Give role
2. Remove Role IF user has role
3. Pin Message
4. Send Message
5. Reset Count
6. Lock Channel
"""


class Automation(commands.Cog):
    events_list = ['null', 'On Number X', 'Each X Number', 'Starts with X', 'Ends With X', 'When score of user reaches X']
    actions_list = ['null', 'Give role', 'Remove Role IF user has role', 'Pin Message', 'Send Message', 'Reset Count', 'Lock Channel']
    max_automations = 5

    def __init__(self, client):
        self.client = client

    def replace_x(self, index, number):
        return self.events_list[index].replace('X', f'{number}')

    @commands.group(aliases=["am", "autom"])
    async def automation(self, ctx):
        if ctx.invoked_subcommand is None:
            events = ""
            for item in self.events_list:
                if item != "null":
                    events += "**" + str(self.events_list.index(item)) + ".** " + item + "\n"

            actions = ""
            for item in self.actions_list:
                if item != "null":
                    actions += "**" + str(self.actions_list.index(item)) + ".** " + item + "\n"

            embed = discord.Embed(
                title="Automation Help",
                description=f"X = The number you choose between 10 and 9223372036854775806.",
                color=settings.embedcolor
            )
            embed.add_field(name="Events", value=events, inline=False)
            embed.add_field(name="Actions", value=actions, inline=False)
            embed.add_field(name="Command Usage", value="`am create <event> <action> <number>`\n"
                                                        "`am delete <id>`\n"
                                                        "`am list`", inline=False)
            embed.add_field(name="Examples", value="`am create 1 1 10` - *Give a role when a user reaches number 10. (You can choose the role after you run the command.)*\n"
                                                   "`am create 4 3 69` - *Pin message when count ends with 69.*\n"
                                                   "`am delete 99` - *Delete automation with id 99.*\n"
                                                   "`am list` - *Get a list of all automations.*", inline=False)
            embed.set_footer(text=settings.footer)
            await ctx.send(embed=embed)

    @automation.command()
    async def create(self, ctx, event=0, action=0, number=0):
        try:
            event = int(event)
            action = int(action)
            number = int(number)
        except Exception:
            await ctx.send(":x: Invalid Arguments.")
            return

        if 0 < event <= 5 and 0 < action <= 6:
            pass
        else:
            await ctx.send(":x: Invalid Arguments.")
            return

        if 10 <= number < 9223372036854775807:
            pass
        else:
            await ctx.send(":x: Invalid arguments.")
            return

        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM guildAutomation WHERE guild = %s", (ctx.guild.id,))
        all_automations = cursor.fetchall()

        if len(all_automations) > self.max_automations:
            await ctx.send(f":x: You already have {self.max_automations} automations enabled.\n"
                           f"Delete an automation: `am delete <id>`")
        else:
            cursor.execute("SELECT * FROM guildAutomation WHERE guild = %s AND triggerNr = %s AND ACTION = %s AND number = %s", (ctx.guild.id, event, action, number))
            am_duplicate = cursor.fetchone()

            if am_duplicate is None:
                action_id = 0
                msg = "0"
                ask_message = False

                extra_questions = [1, 2, 4]
                if action in extra_questions:
                    if action == 1:
                        await ctx.send("What role do you want to give users? (Currently only ID's are supported.)")
                    elif action == 2:
                        await ctx.send("What role do you want to remove from users? (Currently only ID's are supported.)")
                    elif action == 4:
                        await ctx.send("What channel do you want to send a message in? (Currently only ID's are supported.)")

                    def check(message):
                        if message.author == ctx.author and message.channel == ctx.channel:
                            self.client.action_id = message.content
                            return True
                        else:
                            return False

                    try:
                        await self.client.wait_for('message', check=check, timeout=45)

                        try:
                            action_id = int(self.client.action_id)
                        except Exception:
                            await ctx.send(":x: No valid ID was given.")
                            db.close()
                            return

                        if action == 1 or action == 2:
                            role = get(ctx.guild.roles, id=action_id)
                            action_id = role.id
                        elif action == 4:
                            channel = get(ctx.guild.channels, id=action_id)
                            action_id = channel.id
                            ask_message = True
                        else:
                            await ctx.send(":x: An error has occured. Please try again.")
                            db.close()
                            return
                    except asyncio.TimeoutError:
                        await ctx.send(":x: No responds. Canceling the automation.")
                        db.close()
                        return

                if ask_message:
                    await ctx.send("What message do you want to send? (Currently placeholders are not supported.)")

                    def msg(message):
                        if message.author == ctx.author and message.channel == ctx.channel:
                            self.client.msg = message.content
                            return True
                        else:
                            return False

                    try:
                        await self.client.wait_for('message', check=msg, timeout=90)
                        msg = self.client.msg

                        if msg != "0":
                            lengte_msg = len(msg)
                            if lengte_msg > 255:
                                if lengte_msg - 255 == 1:
                                    await ctx.send(f":x: Your message is too long. The maximum allowed message length is 255 characters.\n"
                                                   f"Your message is {lengte_msg} characters, you need to remove 1 character.")
                                else:
                                    await ctx.send(f":x: Your message is too long. The maximum allowed message length is 255 characters.\n"
                                                   f"Your message is {lengte_msg} characters, you need to remove {lengte_msg - 255} characters.")
                                db.close()
                                return
                        else:
                            await ctx.send(":x: Invalid Message.")
                            db.close()
                            return
                    except asyncio.TimeoutError:
                        await ctx.send(":x: No responds. Canceling the automation.")
                        db.close()
                        return

                cursor.execute(settings.insert_guildautomation, (ctx.guild.id, event, action, number, action_id, msg))
                db.commit()

                if action == 1:
                    action = f"Give role <@&{action_id}>"
                elif action == 2:
                    action = f"Remove role <@&{action_id}> if user has the role"
                elif action == 4:
                    action = f"Send a message in <#{action_id}>:"

                    if msg != "0":
                        action += f"\n```\n{msg}```"
                else:
                    action = self.actions_list[action]

                embed = discord.Embed(
                    title="Automation Created",
                    description=f"__Event:__ {self.replace_x(event, number)}\n"
                                f"__Action:__ {action}",
                    color=settings.embedcolor
                )
                embed.set_footer(text=settings.footer)
                await ctx.send(embed=embed)
            else:
                await ctx.send(":x: You already have that exact automation.")
        db.close()

    @automation.command()
    async def delete(self, ctx, am_id=None):
        try:
            am_id = int(am_id)
        except Exception:
            await ctx.send(":x: Invalid Arguments.")
            return

        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM guildAutomation WHERE guild = %s AND id = %s", (ctx.guild.id, am_id))
        automation = cursor.fetchone()

        if automation is None:
            await ctx.send(f":x: There is no automation with id `{am_id}`.")
        else:
            cursor.execute("DELETE FROM guildAutomation WHERE guild = %s AND id = %s", (ctx.guild.id, am_id))
            db.commit()

            await ctx.send(f":white_check_mark: Automation with id `{am_id}` succesfully deleted.")
        db.close()

    @automation.command()
    async def list(self, ctx):
        db = mysql.connector.connect(host=settings.host, user=settings.user,
                                     passwd=settings.passwd, database=settings.database)
        cursor = db.cursor()

        cursor.execute("SELECT * FROM guildAutomation WHERE guild = %s", (ctx.guild.id,))
        all_automations = cursor.fetchall()

        db.close()

        if not all_automations:
            await ctx.send(":x: This server doesn't have any automations.")
            db.close()
            return

        desc = ""

        for automation in all_automations:
            am_id = automation[0]
            event = automation[2]
            action = automation[3]
            number = automation[4]
            action_id = automation[5]

            message = ""
            if action == 1:
                action = f"Give role <@&{action_id}>"
            elif action == 2:
                action = f"Remove role <@&{action_id}> if user has the role"
            elif action == 4:
                action = f"Send a message in <#{action_id}>:"
                message = f"```\n{automation[6]}```"
            else:
                action = self.actions_list[action]

            desc += f"**Automation** `{am_id}`\n> **Event:** {self.replace_x(event, number)}\n> **Action:** {action}\n{message}\n"

        embed = discord.Embed(
            title="Automations",
            description=desc,
            color=settings.embedcolor
        )
        embed.set_footer(text=settings.footer)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Automation(client))
