import os
import logging
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    MessageHandler,
    filters
)

from bot import config
from bot.database.db import DatabaseManager
from bot.database.repository import TrackRepository
from bot.handlers.start import start_command
from bot.handlers.navigation import button_callback
from bot.handlers.search import handle_search_message, handle_inline_query
from bot.handlers.admin import stats_command, reload_command
from scripts.migrate_posts import run_migration

logger = logging.getLogger("shajare_bot")

def create_app() -> Application:
    """
    Application factory for Shajare bot.
    Initializes database, migrates posts if necessary, wires bot_data,
    and registers all commands, callbacks, and message handlers.
    """
    token = config.BOT_TOKEN
    if not token:
        logger.critical("BOT_TOKEN environment variable is missing. Terminating.")
        raise SystemExit("CRITICAL: BOT_TOKEN environment variable is not set. Exiting.")

    db_mgr = DatabaseManager(config.DB_PATH)
    db_mgr.init_db()
    repo = TrackRepository(db_mgr)

    # Auto-bootstrap SQLite database from posts.json if empty or missing
    if repo.get_stats().get("total_tracks", 0) == 0 and os.path.exists(config.POSTS_PATH):
        logger.info("Database is empty; bootstrapping from %s...", config.POSTS_PATH)
        run_migration(config.POSTS_PATH, config.DB_PATH)

    app = ApplicationBuilder().token(token).build()

    # Wire persistent context across handlers
    app.bot_data["repo"] = repo
    app.bot_data["db_mgr"] = db_mgr
    app.bot_data["admin_user_ids"] = config.ADMIN_USER_IDS
    app.bot_data["channel_name"] = config.CHANNEL_NAME
    app.bot_data["posts_path"] = config.POSTS_PATH
    app.bot_data["db_path"] = config.DB_PATH

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("reload", reload_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(InlineQueryHandler(handle_inline_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_message))

    return app

def main():
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=logging.INFO
    )
    app = create_app()
    logger.info("ربات %s با موفقیت آماده به کار شد...", config.CHANNEL_NAME)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
