from discord.ext import commands
from settings import folder_list
import os


class CoreUnload(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def unload(self, ctx, types=None, extension=None):
        if ctx.author.id == 643072638075273248:
            if types is not None and extension is not None:
                if types.lower() in folder_list:
                    if extension == "*":
                        for filenames in os.listdir(f'./{types}'):
                            try:
                                if filenames.endswith('.py'):
                                    print(f"Unload {filenames[:-3]}, by {ctx.author}")
                                    self.client.unload_extension(f'{types}.{filenames[:-3]}')
                            except Exception:
                                pass
                        await ctx.send(f"Alle cogs in {types} zijn uitgeschakeld. Status OK")
                    else:
                        self.client.unload_extension(f'{types}.{extension}')
                        print(f"Unload {extension}, door {ctx.author} in {types}")
                        await ctx.send(f"Cog {extension} uitgeschakeld. Status OK")


def setup(client):
    client.add_cog(CoreUnload(client))
