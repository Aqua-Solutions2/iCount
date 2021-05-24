from discord.ext import commands
import mysql.connector
import settings


class EventsGuildLeave(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(f"[{settings.botname}] The bot was removed from {guild}.")

        db = mysql.connector.connect(
            host=settings.host,
            database=settings.database,
            user=settings.user,
            passwd=settings.passwd
        )
        cursor = db.cursor()
        cursor.execute("DELETE FROM guildSettings WHERE guild = %s", (guild.id,))
        cursor.execute("DELETE FROM guildData WHERE guild = %s", (guild.id,))
        cursor.execute("DELETE FROM guildModules WHERE guild = %s", (guild.id,))
        cursor.execute("DELETE FROM userData WHERE guild = %s", (guild.id,))
        cursor.execute("DELETE FROM userNotify WHERE guild = %s", (guild.id,))
        cursor.execute("DELETE FROM guildAutomation WHERE guild = %s", (guild.id,))
        db.commit()
        db.close()


def setup(client):
    client.add_cog(EventsGuildLeave(client))
