import functools
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from scripts.migrate_posts import run_migration

logger = logging.getLogger(__name__)

def admin_only(func):
    """
    Decorator to restrict handler execution strictly to authorized Telegram user IDs.
    """
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        user_id = user.id if user else None
        admin_ids = context.bot_data.get("admin_user_ids", [])

        if not user_id or user_id not in admin_ids:
            logger.warning("Unauthorized access attempt to %s by user_id: %s", func.__name__, user_id)
            if update.message:
                await update.message.reply_text("⛔️ دسترسی به این دستور تنها برای مدیران ربات مجاز است.")
            return

        return await func(update, context, *args, **kwargs)
    return wrapper

@admin_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repo = context.bot_data.get("repo")
    if not repo:
        await update.message.reply_text("دسترسی به دیتابیس برقرار نیست.")
        return

    stats = repo.get_stats()
    levels_info = "\n".join(f"  • {k.replace('level_', 'سطح ')}: {v} قطعه" for k, v in stats.get("levels", {}).items())

    text = (
        "📊 <b>گزارش وضعیت گنجینه شجره</b>\n\n"
        f"🎵 <b>کل قطعات ثبت‌شده:</b> {stats.get('total_tracks')} قطعه\n"
        f"💿 <b>تعداد آلبوم‌ها:</b> {stats.get('total_albums')} آلبوم\n"
        f"💾 <b>حجم پایگاه داده:</b> {stats.get('db_size_kb')} کیلوبایت\n\n"
        f"🗂 <b>تفکیک سطوح آرشیو:</b>\n{levels_info}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

@admin_only
async def reload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    posts_path = context.bot_data.get("posts_path", "posts.json")
    db_path = context.bot_data.get("db_path", "shajare.db")

    await update.message.reply_text("⏳ در حال بازخوانی اطلاعات از فایل و به‌روزرسانی پایگاه داده...")
    try:
        count = run_migration(posts_path=posts_path, db_path=db_path)
        await update.message.reply_text(f"✅ بازخوانی موفقیت‌آمیز بود! تعداد {count} قطعه همگام‌سازی شد.")
    except Exception as e:
        logger.error("Error during reload command: %s", e, exc_info=True)
        await update.message.reply_text(f"❌ خطا در بازخوانی اطلاعات: {e}")
