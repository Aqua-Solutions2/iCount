# import alle gevoelige gegevens
import credentials
import datetime

botname = "iCount"
footer = f'© {datetime.datetime.now().year} - {botname}'
default_prefix = 'c!'

embedcolor = 0xF4A950
failcolor = 0xFF0000
succescolor = 0x00FF00

succes_emote = '✅'
error_emote = '❌'

folder_list = ["core", "events", "cogs"]

insert_guildsettings = "INSERT INTO guildSettings (guild, prefix, channelId, maxCount, timeoutRole, proEnabled, language) VALUES (%s, %s, %s, %s, %s, %s, %s)"
insert_guilddata = "INSERT INTO guildData (guild, currentCount, lastUser) VALUES (%s, %s, %s)"
insert_guildmodules = "INSERT INTO guildModules (guild, allowSpam, restartError, emoteReact, recoverMode, postEmbed) VALUES (%s, %s, %s, %s, %s, %s)"
insert_guildautomation = "INSERT INTO guildAutomation (guild, triggerNr, actions, extra) VALUES (%s, %s, %s, %s)"
insert_usernotify = "INSERT INTO userNotify (guild, user, number, everyNumber) VALUES (%s, %s, %s, %s)"
insert_userdata = "INSERT INTO userData (guild, user, count) VALUES (%s, %s, %s)"

# Gevoelige informatie

host = credentials.host
user = credentials.user
database = credentials.database
passwd = credentials.passwd

token = credentials.token
