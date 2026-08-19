class Config(object):
    LOGGER = True

    # Telegram API Credentials
    API_ID = 34829388
    API_HASH = "30df7fd725bd39aa2e3b7a55b15a182b"
    TOKEN = "8954458459:AAERwS4ZGfRsWQXVVkCq-Wt49biCgfM7GHs"
    OWNER_ID = 8888788314

    # Databases (Yahan DATABASE_URL dalna zaroori hai)
    DATABASE_URL = "YAHAN_APNA_POSTGRESQL_LINK_PASTE_KAREIN"
    MONGO_DB_URI = "mongodb+srv://shubhxitachi_db_user:3r1jKiHGmAyd93wy@nezukonbot.wkzudm6.mongodb.net/?retryWrites=true&w=majority"

    # Other Settings
    START_IMG = "https://te.legra.ph/file/40eb1ed850cdea274693e.jpg"
    SUPPORT_CHAT = "nezukochatgc11"
    EVENT_LOGS = ()

    ALLOW_CHATS = True
    ALLOW_EXCL = True
    DEL_CMDS = True
    INFOPIC = True
    LOAD = []
    NO_LOAD = []
    STRICT_GBAN = True
    TEMP_DOWNLOAD_DIRECTORY = "./"
    WORKERS = 8


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
