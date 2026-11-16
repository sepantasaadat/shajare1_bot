import logging
from typing import List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.keyboards.menus import make_main_menu_keyboard
from bot.services.forwarder import send_track

logger = logging.getLogger(__name__)

def extract_deep_link_track_id(args: Optional[List[str]]) -> Optional[int]:
    """
    Parse deep-linking payload like ['track_726'] or ['track=726'] into integer 726.
    """
    if not args:
        return None
    raw = args[0].strip()
    if raw.startswith("track_"):
        val = raw[6:]
    elif raw.startswith("track="):
        val = raw[6:]
    else:
        return None

    try:
        return int(val)
    except ValueError:
        return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_name = context.bot_data.get("channel_name", "شجره")
    repo = context.bot_data.get("repo")

    # Check for deep-linking arguments (e.g. /start track_726)
    track_id = extract_deep_link_track_id(context.args)
    if track_id and repo:
        track = repo.get_track_by_message_id(track_id)
        if track:
            title = track.get("title_fa") or f"قطعه شماره {track_id}"
            alb_name = track.get("album_name") or "آرشیو"
            await update.message.reply_text(
                f"🌿 <b>{title}</b>\n💿 آلبوم: {alb_name}\n\n<i>در حال ارسال نغمه...</i>",
                parse_mode=ParseMode.HTML
            )
            await send_track(update.message.chat_id, track, context)

            keyboard = []
            if track.get("album_id"):
                keyboard.append([
                    InlineKeyboardButton(f"💿 مشاهده کامل آلبوم «{alb_name}»", callback_data=track["album_id"])
                ])
            keyboard.append([InlineKeyboardButton("🔙 منوی اصلی ربات", callback_data="back_to_main")])
            await update.message.reply_text(
                "برای شنیدن دیگر نغمه‌ها از منوی زیر استفاده کنید:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

    welcome_text = (
        f"🌿 <b>به گنجینه صوتی «{channel_name}» خوش آمدید</b> 🌿\n"
        "<i>آرشیو و راهنمای آثار استاد همایون شجریان</i>\n\n"
        "لطفاً بخش یا نغمه مورد نظر خود را از منوی زیر انتخاب نمایید:"
    )
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=make_main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )
