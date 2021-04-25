from discord.ext import commands
import time

start_time = time.time()


class CogsPing(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["uptime", "pong"])
    async def ping(self, ctx):
        ping = round(self.client.latency * 1000)

        current_uptime = time.time()
        difference = int(round(current_uptime - start_time))

        day = difference // (24 * 3600)
        difference = difference % (24 * 3600)
        hour = difference // 3600
        difference %= 3600
        minutes = difference // 60
        difference %= 60
        seconds = difference

        if day == 0:
            if hour == 0:
                if minutes == 0:
                    uptime = f"{seconds}s"
                else:
                    uptime = f"{minutes}m {seconds}s"
            else:
                uptime = f"{hour}h {minutes}m {seconds}s"
        else:
            uptime = f"{day}d {hour}h {minutes}m {seconds}s"

        await ctx.send(f":ping_pong: API Latency: `{ping}ms`.\n"
                       f":hammer_pick: Uptime: `{uptime}`.")


def setup(client):
    client.add_cog(CogsPing(client))
