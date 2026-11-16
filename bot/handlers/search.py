import html
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.keyboards.menus import make_main_menu_keyboard
from bot.services.forwarder import send_track

logger = logging.getLogger(__name__)

async def handle_search_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting_for_search'):
        return

    user_text = update.message.text
    if not user_text:
        return

    escaped_text = html.escape(user_text.strip())
    repo = context.bot_data.get("repo")
    if not repo:
        await update.message.reply_text("پایگاه داده موقتاً در دسترس نیست.")
        return

    await update.message.reply_text(
        f"🔍 در حال جستجو برای: «<b>{escaped_text}</b>»...",
        parse_mode=ParseMode.HTML
    )

    found_tracks = repo.search_tracks(user_text.strip(), limit=10)

    if not found_tracks:
        no_res_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 جستجوی مجدد", callback_data="search_guide")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ])
        await update.message.reply_text(
            f"❌ متاسفانه اثری مطابق با «<b>{escaped_text}</b>» یافت نشد.\nمی‌توانید نام قطعه، گوشه یا آلبوم دیگری را جستجو فرمایید.",
            reply_markup=no_res_keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        total_count = len(found_tracks)
        display_count = min(total_count, 5)
        if total_count > 5:
            header_text = f"✅ تعداد <b>{total_count}</b> اثر یافت شد (نمایش ۵ اثر اول):"
        else:
            header_text = f"✅ تعداد <b>{total_count}</b> اثر یافت شد:"

        await update.message.reply_text(header_text, parse_mode=ParseMode.HTML)

        for track in found_tracks[:display_count]:
            await send_track(update.message.chat_id, track, context)
            await asyncio.sleep(1.0)

        search_finish_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 جستجوی دیگر", callback_data="search_guide")],
            [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
        ])
        await update.message.reply_text(
            "✨ پایان نتایج جستجو.\nبرای ادامه، بخش دلخواه را انتخاب کنید:",
            reply_markup=search_finish_keyboard
        )

    context.user_data['waiting_for_search'] = False

async def handle_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles Telegram inline queries (@BotUsername <query>) to share tracks in groups and chats.
    """
    inline_query = update.inline_query
    if not inline_query:
        return

    query_text = inline_query.query.strip()
    repo = context.bot_data.get("repo")
    if not repo:
        await inline_query.answer([], cache_time=10)
        return

    bot_username = context.bot.username or "Shajare1_bot"

    if query_text:
        tracks = repo.search_tracks(query_text, limit=15)
    else:
        # Show sample tracks if query is empty
        tracks = repo.get_all_tracks()[:10]

    results = []
    for t in tracks:
        msg_id = t["message_id"]
        title = t.get("title_fa") or f"نغمه شماره {msg_id}"
        album_name = t.get("album_name") or "آرشیو شجره"
        desc = f"آلبوم: {album_name}"
        if t.get("title_en"):
            desc += f" | {t['title_en']}"

        article_text = (
            f"🌿 <b>{title}</b>\n"
            f"💿 آلبوم: {album_name}\n\n"
            "🎧 برای شنیدن و دریافت کامل این اثر در ربات شجره، دکمه زیر را لمس فرمایید:"
        )
        share_url = f"https://t.me/{bot_username}?start=track_{msg_id}"
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎧 پخش در ربات شجره", url=share_url)]
        ])

        results.append(
            InlineQueryResultArticle(
                id=str(msg_id),
                title=title,
                description=desc,
                input_message_content=InputTextMessageContent(
                    article_text,
                    parse_mode=ParseMode.HTML
                ),
                reply_markup=reply_markup
            )
        )

    await inline_query.answer(results, cache_time=60, is_personal=False)
