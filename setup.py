import mysql.connector
from settings import host, user, passwd, database

db = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database)
cursor = db.cursor()


# cursor.execute("CREATE TABLE guildSettings (guild BIGINT PRIMARY KEY, prefix VARCHAR(8), channelId BIGINT, maxCount BIGINT, timeoutRole BIGINT, proEnabled TINYINT(1), language VARCHAR(2))")
# cursor.execute("CREATE TABLE guildData (guild BIGINT PRIMARY KEY, currentCount BIGINT, lastUser BIGINT)")
# cursor.execute("CREATE TABLE guildModules (guild BIGINT PRIMARY KEY, allowSpam TINYINT(1), restartError TINYINT(1), emoteReact TINYINT(1), recoverMode TINYINT(1), postEmbed TINYINT(1))")
cursor.execute("CREATE TABLE guildAutomation (id BIGINT AUTO_INCREMENT PRIMARY KEY, guild BIGINT, triggerNr TINYINT, action TINYINT, extra BIGINT)")
# cursor.execute("CREATE TABLE userNotify (id BIGINT AUTO_INCREMENT PRIMARY KEY, guild BIGINT, user BIGINT, number BIGINT, everyNumber TINYINT(1))")
# cursor.execute("CREATE TABLE userData (id BIGINT AUTO_INCREMENT PRIMARY KEY, guild BIGINT, user BIGINT, count INT)")

db.commit()
db.close()
