import html
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.constants import ParseMode, ChatType
from telegram.ext import ContextTypes

from bot.keyboards.menus import make_search_results_keyboard, make_main_menu_keyboard
from bot.services.forwarder import send_track

logger = logging.getLogger(__name__)

async def handle_search_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    is_waiting = context.user_data.get('waiting_for_search', False)
    is_private = update.effective_chat and update.effective_chat.type == ChatType.PRIVATE

    # Process search if explicitly requested or if sent in private chat
    if not (is_waiting or is_private):
        return

    # Clean up previous search prompt button if one was recorded
    prompt_msg_id = context.user_data.pop('search_prompt_msg_id', None)
    if prompt_msg_id and update.effective_chat:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=update.effective_chat.id,
                message_id=prompt_msg_id,
                reply_markup=None
            )
        except Exception:
            pass

    user_text = update.message.text.strip()
    if not user_text:
        return

    escaped_text = html.escape(user_text)
    repo = context.bot_data.get("repo")
    if not repo:
        await update.message.reply_text("پایگاه داده موقتاً در دسترس نیست.")
        return

    found_tracks = repo.search_tracks(user_text, limit=30)
    context.user_data['last_search_results'] = found_tracks
    context.user_data['last_search_query'] = user_text

    if not found_tracks:
        no_res_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 جستجوی مجدد", callback_data="search_guide")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ])
        await update.message.reply_text(
            f"❌ متاسفانه اثری مطابق با «<b>{escaped_text}</b>» یافت نشد.\nمی‌توانید نام قطعه، گوشه یا آلبوم دیگری را جستجو فرمایید:",
            reply_markup=no_res_keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        total_count = len(found_tracks)
        results_kb = make_search_results_keyboard(found_tracks, page=0, page_size=5)
        text = (
            f"🔍 <b>نتایج جستجو برای:</b> «<b>{escaped_text}</b>»\n"
            f"<i>مجموعاً {total_count} نغمه در آرشیو یافت شد.</i>\n\n"
            "برای شنیدن هر قطعه دکمه آن را لمس کنید یا جهت دریافت همه، دکمه «ارسال یکجا» را برگزینید:"
        )
        await update.message.reply_text(text, reply_markup=results_kb, parse_mode=ParseMode.HTML)

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
