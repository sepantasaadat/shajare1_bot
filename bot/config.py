import os
from typing import List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Telegram bot credentials
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Authorized Telegram user IDs for administrative commands (/stats, /reload)
raw_admins = os.environ.get("ADMIN_USER_IDS", "")
ADMIN_USER_IDS: List[int] = [
    int(x.strip()) for x in raw_admins.split(",") if x.strip().isdigit()
]

# Brand & archive metadata
CHANNEL_NAME = os.environ.get("CHANNEL_NAME", "شجره")

# Storage locations
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "shajare.db"))
POSTS_PATH = os.environ.get("POSTS_PATH", os.path.join(BASE_DIR, "posts.json"))
