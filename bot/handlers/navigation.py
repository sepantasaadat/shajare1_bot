import asyncio
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.keyboards.menus import (
    make_main_menu_keyboard,
    make_levels_keyboard,
    make_albums_keyboard,
    make_tracklist_keyboard,
    make_contact_keyboard,
    make_cancel_search_keyboard,
    make_completion_keyboard,
    ALBUMS_DATA
)
from bot.services.forwarder import send_track
from bot.handlers.fal import handle_fal_homayouni

logger = logging.getLogger(__name__)

# Reverse map for display names
ALBUM_DISPLAY_NAMES = {v: k for k, v in ALBUMS_DATA.items()}

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    # Guard against concurrent clicks during bulk forwarding
    if context.user_data.get('is_forwarding'):
        try:
            await query.answer("لطفاً تا پایان ارسال آثار قبلی صبور باشید.", show_alert=True)
        except Exception:
            pass
        return

    await query.answer()
    data = query.data
    channel_name = context.bot_data.get("channel_name", "شجره")
    repo = context.bot_data.get("repo")

    if data == "noop":
        return

    if data == "back_to_main":
        await query.edit_message_text(
            text=(
                f"🌿 <b>گنجینه صوتی «{channel_name}»</b>\n\n"
                "برای ادامه، بخش مورد نظر خود را از منوی اصلی برگزینید:"
            ),
            reply_markup=make_main_menu_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    if data == "show_levels_menu":
        await query.edit_message_text(
            text=(
                "🗂 <b>سطوح آرشیو آثار</b>\n\n"
                "آرشیو کانال بر اساس دوره‌ها و سطوح مختلف دسته‌بندی شده است.\n"
                "لطفاً سطح مورد نظر را انتخاب نمایید:"
            ),
            reply_markup=make_levels_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    if data == "show_albums_menu":
        await query.edit_message_text(
            text=(
                "🎵 <b>آلبوم‌های استاد همایون شجریان</b>\n\n"
                "لطفاً آلبوم مورد نظر خود را انتخاب نمایید:"
            ),
            reply_markup=make_albums_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    if data == "contact_us":
        await query.edit_message_text(
            text=(
                "📩 <b>راه‌های ارتباط با ما</b>\n\n"
                "برای ارسال انتقادات، پیشنهادات یا در میان گذاشتن نظرات خود درباره کانال و ربات شجره، "
                "می‌توانید مستقیماً با مدیریت در ارتباط باشید:"
            ),
            reply_markup=make_contact_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    if data == "search_guide":
        context.user_data['waiting_for_search'] = True
        await query.edit_message_text(
            text=(
                "🔍 <b>حالت جستجوی اثر فعال شد</b>\n\n"
                "لطفاً بخشی از <b>نام قطعه، شعر، تصنیف یا آلبوم</b> مورد نظر خود را تایپ و ارسال فرمایید:"
            ),
            reply_markup=make_cancel_search_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    if data == "cancel_search":
        context.user_data['waiting_for_search'] = False
        await query.edit_message_text(
            text="جستجو لغو شد. بازگشت به منوی اصلی:",
            reply_markup=make_main_menu_keyboard()
        )
        return

    if data == "fale_homayouni":
        await handle_fal_homayouni(update, context)
        return

    # Handle single track play: play_<message_id>
    if data.startswith("play_"):
        try:
            msg_id = int(data[5:])
        except ValueError:
            return

        if repo:
            track = repo.get_track_by_message_id(msg_id)
            if track:
                await send_track(query.message.chat_id, track, context)
            else:
                await context.bot.send_message(query.message.chat_id, text="متاسفانه این اثر در آرشیو یافت نشد.")
        return

    # Handle bulk sending: bulk_<category>
    if data.startswith("bulk_"):
        category = data[5:]
        tracks = []
        display_name = category
        if category.startswith("alb_"):
            tracks = repo.get_tracks_by_album(category) if repo else []
            display_name = f"آلبوم «{ALBUM_DISPLAY_NAMES.get(category, category)}»"
        elif category.startswith("level"):
            try:
                lvl_num = int(category.replace("level", ""))
                tracks = repo.get_tracks_by_level(lvl_num) if repo else []
                display_name = f"سطح {lvl_num}"
            except ValueError:
                pass

        if not tracks:
            await context.bot.send_message(query.message.chat_id, text=f"اثری برای {display_name} ثبت نشده است.")
            return

        context.user_data['is_forwarding'] = True
        try:
            await query.edit_message_text(
                text=f"⏳ <b>در حال ارسال {len(tracks)} اثر از {display_name}...</b>\nلطفاً شکیبا باشید.",
                parse_mode=ParseMode.HTML
            )
            for i, t in enumerate(tracks):
                await send_track(query.message.chat_id, t, context)
                if (i + 1) % 20 == 0:
                    await asyncio.sleep(3)
                else:
                    await asyncio.sleep(1.0)
        finally:
            context.user_data['is_forwarding'] = False

        await context.bot.send_message(
            query.message.chat_id,
            text=f"✨ ارسال آثار <b>{display_name}</b> با موفقیت پایان یافت.\nبرای ادامه، بخش دلخواه خود را برگزینید:",
            reply_markup=make_completion_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    # Handle album or level selection (and pagination: <category>_page_<num>)
    category = data
    page = 0
    if "_page_" in data:
        parts = data.split("_page_")
        category = parts[0]
        try:
            page = int(parts[1])
        except ValueError:
            page = 0

    tracks = []
    display_name = category
    if category.startswith("alb_"):
        tracks = repo.get_tracks_by_album(category) if repo else []
        display_name = f"آلبوم «{ALBUM_DISPLAY_NAMES.get(category, category)}»"
    elif category.startswith("level"):
        try:
            lvl_num = int(category.replace("level", ""))
            tracks = repo.get_tracks_by_level(lvl_num) if repo else []
            display_name = f"سطح {lvl_num}"
        except ValueError:
            pass

    if not tracks:
        await query.edit_message_text(
            text=f"برای <b>{display_name}</b> اثری در آرشیو ثبت نشده است.",
            reply_markup=make_main_menu_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    tracklist_kb = make_tracklist_keyboard(category, tracks, page=page, page_size=6)
    text = (
        f"🎵 <b>فهرست آثار {display_name}</b>\n"
        f"<i>مجموعاً {len(tracks)} نغمه در این مجموعه قرار دارد.</i>\n\n"
        "برای شنیدن هر قطعه، دکمه مربوط به آن را لمس نمایید یا جهت دریافت تمام آثار، دکمه «ارسال یکجا» را برگزینید:"
    )
    await query.edit_message_text(
        text=text,
        reply_markup=tracklist_kb,
        parse_mode=ParseMode.HTML
    )
