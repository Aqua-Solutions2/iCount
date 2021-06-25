from discord.ext import commands
import mysql.connector
import settings


class EventsGuildJoin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"[{settings.botname}] The bot was invited to {guild}.")

        record = (guild.id, f"{settings.default_prefix}", 0, -1, 0, 0, "en")

        db = mysql.connector.connect(
            host=settings.host,
            database=settings.database,
            user=settings.user,
            passwd=settings.passwd
        )
        cursor = db.cursor()
        try:
            cursor.execute(settings.insert_guildsettings, record)
        except mysql.connector.errors.IntegrityError:
            cursor.execute("DELETE FROM guildSettings WHERE guild = %s", (guild.id,))
            cursor.execute("DELETE FROM guildData WHERE guild = %s", (guild.id,))
            cursor.execute("DELETE FROM guildModules WHERE guild = %s", (guild.id,))
            cursor.execute("DELETE FROM userData WHERE guild = %s", (guild.id,))
            cursor.execute("DELETE FROM userNotify WHERE guild = %s", (guild.id,))
            cursor.execute("DELETE FROM userAutomation WHERE guild = %s", (guild.id,))
            db.commit()

            cursor.execute(settings.insert_guildsettings, record)
        db.commit()
        db.close()


def setup(client):
    client.add_cog(EventsGuildJoin(client))
