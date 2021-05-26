import asyncio
import os
import discord
from discord.ext import commands
import settings
import mysql.connector

intents = discord.Intents.default()
intents.members = True


def get_prefix(client, message):
    db = mysql.connector.connect(host=settings.host, user=settings.user,
                                 passwd=settings.passwd, database=settings.database)
    cursor = db.cursor()

    cursor.execute("SELECT prefix FROM guildSettings WHERE guild = %s", (message.guild.id,))
    prefix_tuple = cursor.fetchone()
    db.close()

    if prefix_tuple is None:
        return settings.default_prefix
    else:
        return prefix_tuple[0]


client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
client.remove_command("help")
client.action_id = 0
client.msg = "0"


async def change_status():
    await client.wait_until_ready()
    while client.is_ready():
        status = discord.Activity(name=f"{settings.default_prefix}help", type=discord.ActivityType.watching)
        await client.change_presence(activity=status)
        await asyncio.sleep(300)


for folder in settings.folder_list:
    for filename in os.listdir(f'./{folder}'):
        if filename.endswith('.py') and not filename.startswith('_'):
            try:
                client.load_extension(f'{folder}.{filename[:-3]}')
                print(f"[{settings.botname}] {folder}.{filename[:-3]}: OK")
            except Exception as e:
                if filename == "config.py":
                    raise e
                else:
                    print(f"[{settings.botname}] {folder}.{filename[:-3]}: ERROR")

client.loop.create_task(change_status())
client.run(settings.token)
