from discord.ext import commands
from settings import host, user, passwd, database, default_prefix, insert_guildsettings
import mysql.connector


class EventsOnMessage(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            db = mysql.connector.connect(host=host, database=database, user=user, passwd=passwd)
            cursor = db.cursor()

            cursor.execute(f"SELECT guild FROM guildSettings WHERE guild = %s", (message.guild.id,))
            check_settings = cursor.fetchone()

            if check_settings is None:
                record = (message.guild.id, f"{default_prefix}", 0, -1, 0, 0, "en")
                cursor.execute(insert_guildsettings, record)
                db.commit()

            bericht = message.content.replace(" ", "")

            if bericht == f"<@!{self.client.user.id}>prefix" or bericht == f"<@!{self.client.user.id}>":
                db = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database)
                cursor = db.cursor()

                cursor.execute("SELECT prefix FROM guildSettings WHERE guild = %s", (message.guild.id,))
                prefix_tuple = cursor.fetchone()

                if prefix_tuple is None:
                    prefix = default_prefix
                else:
                    prefix = prefix_tuple[0]

                await message.channel.send(f"The prefix of the bot is `{prefix}`\n"
                                           f"If you need help with the bot, please use `{prefix}help`")
            db.close()


def setup(client):
    client.add_cog(EventsOnMessage(client))
