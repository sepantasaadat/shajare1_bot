"""
Shajare Telegram Bot Entrypoint

This script acts as the root entry point for backward compatibility with existing
systemd unit configurations (shajare_bot.service) while delegating all application
lifecycle, modular handlers, and database interactions to the `bot` package.
"""

import os
import sys

# Ensure root directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import config
from bot.keyboards.menus import ALBUMS_DATA
from bot.services.forwarder import send_track as send_post
from bot.main import create_app, main

CHANNEL_NAME = config.CHANNEL_NAME
BASE_DIR = config.BASE_DIR
POSTS_FILE = config.POSTS_PATH
BOT_TOKEN = config.BOT_TOKEN

def load_posts(path: str):
    """Backward compatibility helper for reading legacy posts.json."""
    import json
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    main()
