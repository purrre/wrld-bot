import os
from dotenv import load_dotenv
load_dotenv()

MAIN_PREFIX = ',' # main prefix the bot uses
DEV_PREFIX = ',,' # only need to set/change if you're gonna use DEV mode

DEV = False # whether or not to use DEV mode, check the README

HEALTH = False # whether or not to start the server with a /health endpoint (for downtime notifs)
PORT = 5555 # only need to change if you have health set to true

# boost level: upload size
upload_limits = {
    0: 10,
    1: 25,
    2: 50,
    3: 100
}

TOKEN = os.getenv("BOT_TOKEN") if not DEV else os.getenv("DEV_TOKEN")
PREFIX = MAIN_PREFIX if not DEV and DEV_PREFIX else DEV_PREFIX