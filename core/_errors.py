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
                await self.cooldown()
            elif isinstance(self.error, commands.MemberNotFound):
                await self.member_not_found()
            elif isinstance(self.error, commands.MissingRequiredArgument):
                await self.arguments()
            elif isinstance(self.error, commands.ChannelNotFound):
                await self.channel_not_found()
            elif isinstance(self.error, commands.RoleNotFound):
                await self.role_not_found()
            elif isinstance(self.error, commands.MissingPermissions):
                await self.no_perms("member")
            elif isinstance(self.error, commands.BotMissingPermissions):
                await self.no_perms()
            else:
                raise self.error

    # Do not call these functions in any other file,
    # these functions can only be called in error_check()
    async def cooldown(self):
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

    async def arguments(self):
        await self.ctx.send(":x: Invalid Arguments.")

    async def no_perms(self, user="bot"):
        if user == "bot":
            await self.ctx.send(":x: I don't have enough permissions.")
        elif user == "member":
            await self.ctx.send(":x: You don't have enough permissions to execute this command.")

    async def member_not_found(self):
        await self.ctx.send(":x: The member was not found.")

    async def channel_not_found(self):
        await self.ctx.send(":x: The channel was not found.")

    async def role_not_found(self):
        await self.ctx.send(":x: The role was not found.")
