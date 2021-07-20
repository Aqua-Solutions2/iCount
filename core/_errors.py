import discord
from discord.ext import commands
import settings
import time


class Error:

    def __init__(self, ctx=None, error=None, client=None):
        self.ctx = ctx
        self.error = error
        self.client = client

    # checking which error it is
    async def error_check(self):
        if self.error is None:
            return
        elif self.ctx is None:
            raise self.error
        else:
            if isinstance(self.error, commands.CommandOnCooldown):
                error_time = self.error.retry_after

                if error_time >= 3600:
                    error_time_left = time.strftime("%-Hu %-Mm %-Ss", time.gmtime(error_time))
                elif error_time >= 60:
                    error_time_left = time.strftime("%-Mm %-Ss", time.gmtime(error_time))
                else:
                    error_time_left = round(error_time, 1)

                if error_time_left == 1 or error_time_left == 1.0:
                    seconds = "second"
                else:
                    seconds = "seconds"

                embed = discord.Embed(
                    description=f":x: Please wait {error_time_left} {seconds} to use this commmand again.",
                    color=settings.embedcolor
                )
                await self.ctx.send(embed=embed)
            elif isinstance(self.error, commands.MemberNotFound):
                await self.ctx.send(":x: The member was not found.")
            elif isinstance(self.error, commands.MissingRequiredArgument):
                await self.ctx.send(":x: Invalid Arguments.")
            elif isinstance(self.error, commands.ChannelNotFound):
                await self.ctx.send(":x: The channel was not found.")
            elif isinstance(self.error, commands.RoleNotFound):
                await self.ctx.send(":x: The role was not found.")
            elif isinstance(self.error, commands.MissingPermissions):
                await self.no_perms("member")
            elif isinstance(self.error, commands.BotMissingPermissions):
                await self.no_perms()
            elif isinstance(self.error, discord.Forbidden):
                await self.ctx.send("Sorry, I don't have enough permissions. Please make sure I have enough permissions to create and edit channels and to delete messages.\n"
                                    "I use these permissions to create a counting channel. You can create one yourself and use the `link` command.")
            else:
                raise self.error

    async def no_perms(self, user="bot"):
        if user == "bot":
            await self.ctx.send(":x: I don't have enough permissions.")
        elif user == "member":
            await self.ctx.send(":x: You don't have enough permissions to execute this command.")
