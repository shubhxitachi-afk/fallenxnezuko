class Config(object):
    LOGGER = True

    # Telegram API Credentials
    API_ID = 34829388
    API_HASH = "30df7fd725bd39aa2e3b7a55b15a182b"
    TOKEN = "8954458459:AAERwS4ZGfRsWQXVVkCq-Wt49biCgfM7GHs"
    OWNER_ID = 8888788314

    # Databases
    DATABASE_URL = "postgresql://neondb_owner:npg_SbiFpKsRM5z2@ep-lucky-dew-ay5nrutb.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require"
    MONGO_DB_URI = "mongodb+srv://shubhxitachi_db_user:3r1jKiHGmAyd93wy@nezukonbot.wkzudm6.mongodb.net/?retryWrites=true&w=majority"

    # API Keys & Custom Settings
    CASH_API_KEY = "GL1I3O6OUMCWEDQ8"
    TIME_API_KEY = "06PTU1Q9M7US"
    EVENT_LOGS = ()
    START_IMG = "https://te.legra.ph/file/40eb1ed850cdea274693e.jpg"
    SUPPORT_CHAT = "nezukochatgc11"

    # Permission Lists
    BL_CHATS = []
    DRAGONS = []
    DEV_USERS = []
    DEMONS = []
    TIGERS = []
    WOLVES = []

    # Bot Internal Settings
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
