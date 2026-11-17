import asyncio
import logging
import telegram
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
    make_bulk_forwarding_keyboard,
    make_search_results_keyboard,
    ALBUMS_DATA
)
from bot.services.forwarder import send_track
from bot.handlers.fal import handle_fal_homayouni

logger = logging.getLogger(__name__)

ALBUM_DISPLAY_NAMES = {v: k for k, v in ALBUMS_DATA.items()}

async def safe_edit_message_text(query, text: str, reply_markup=None, parse_mode=ParseMode.HTML):
    """
    Safely edit message text while catching harmless 'Message is not modified' errors.
    """
    try:
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    except telegram.error.BadRequest as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    data = query.data

    # Handle bulk forwarding cancellation (must be allowed even when is_forwarding is True)
    if data == "stop_bulk_forwarding":
        context.user_data['cancel_forwarding'] = True
        await query.answer("درخواست توقف ارسال ثبت شد.", show_alert=True)
        return

    # Guard against concurrent clicks during bulk forwarding
    if context.user_data.get('is_forwarding'):
        try:
            await query.answer("لطفاً تا پایان ارسال آثار قبلی صبور باشید.", show_alert=True)
        except Exception:
            pass
        return

    # Informative dialog for page indicator button
    if data == "noop":
        await query.answer(
            "ℹ️ شما در حال مشاهده این صفحه از فهرست هستید. برای جابه‌جایی از دکمه‌های قبلی و بعدی استفاده فرمایید.",
            show_alert=True
        )
        return

    # Immediate feedback on single-track play
    if data.startswith("play_"):
        await query.answer("🎧 در حال ارسال نغمه...", show_alert=False)
        try:
            msg_id = int(data[5:])
        except ValueError:
            return

        repo = context.bot_data.get("repo")
        if repo:
            track = repo.get_track_by_message_id(msg_id)
            if track:
                await send_track(query.message.chat_id, track, context)
            else:
                await context.bot.send_message(query.message.chat_id, text="متاسفانه این اثر در آرشیو یافت نشد.")
        return

    await query.answer()
    channel_name = context.bot_data.get("channel_name", "شجره")
    repo = context.bot_data.get("repo")

    if data == "back_to_main":
        await safe_edit_message_text(
            query,
            text=(
                f"🌿 <b>گنجینه صوتی «{channel_name}»</b>\n\n"
                "برای ادامه، بخش مورد نظر خود را از منوی اصلی برگزینید:"
            ),
            reply_markup=make_main_menu_keyboard()
        )
        return

    if data == "show_levels_menu":
        await safe_edit_message_text(
            query,
            text=(
                "🗂 <b>سطوح آرشیو آثار</b>\n\n"
                "آرشیو کانال بر اساس دوره‌ها و سطوح مختلف دسته‌بندی شده است.\n"
                "لطفاً سطح مورد نظر را انتخاب نمایید:"
            ),
            reply_markup=make_levels_keyboard()
        )
        return

    if data == "show_albums_menu":
        await safe_edit_message_text(
            query,
            text=(
                "🎵 <b>آلبوم‌های استاد همایون شجریان</b>\n\n"
                "لطفاً آلبوم مورد نظر خود را انتخاب نمایید:"
            ),
            reply_markup=make_albums_keyboard()
        )
        return

    if data == "contact_us":
        await safe_edit_message_text(
            query,
            text=(
                "📩 <b>راه‌های ارتباط با ما</b>\n\n"
                "برای ارسال انتقادات، پیشنهادات یا در میان گذاشتن نظرات خود درباره کانال و ربات شجره، "
                "می‌توانید مستقیماً با مدیریت در ارتباط باشید:"
            ),
            reply_markup=make_contact_keyboard()
        )
        return

    if data == "search_guide":
        context.user_data['waiting_for_search'] = True
        context.user_data['search_prompt_msg_id'] = query.message.message_id
        await safe_edit_message_text(
            query,
            text=(
                "🔍 <b>حالت جستجوی اثر فعال شد</b>\n\n"
                "لطفاً بخشی از <b>نام قطعه، شعر، تصنیف یا آلبوم</b> مورد نظر خود را تایپ و ارسال فرمایید:"
            ),
            reply_markup=make_cancel_search_keyboard()
        )
        return

    if data == "cancel_search":
        context.user_data['waiting_for_search'] = False
        await safe_edit_message_text(
            query,
            text="جستجو لغو شد. بازگشت به منوی اصلی:",
            reply_markup=make_main_menu_keyboard()
        )
        return

    if data == "fale_homayouni":
        await handle_fal_homayouni(update, context)
        return

    # Handle pagination in search results: search_page_<num>
    if data.startswith("search_page_"):
        try:
            page = int(data[12:])
        except ValueError:
            page = 0
        search_tracks = context.user_data.get('last_search_results', [])
        query_text = context.user_data.get('last_search_query', '')
        if not search_tracks:
            await query.answer("نتایج جستجو منقضی شده است. لطفاً دوباره جستجو فرمایید.", show_alert=True)
            return

        total_count = len(search_tracks)
        results_kb = make_search_results_keyboard(search_tracks, page=page, page_size=5)
        text = (
            f"🔍 <b>نتایج جستجو برای:</b> «<b>{query_text}</b>»\n"
            f"<i>مجموعاً {total_count} نغمه در آرشیو یافت شد.</i>\n\n"
            "برای شنیدن هر قطعه دکمه آن را لمس کنید یا جهت دریافت همه، دکمه «ارسال یکجا» را برگزینید:"
        )
        await safe_edit_message_text(query, text=text, reply_markup=results_kb)
        return

    # Handle bulk sending: bulk_<category> or bulk_search
    if data.startswith("bulk_"):
        category = data[5:]
        tracks = []
        display_name = category

        if category == "search":
            tracks = context.user_data.get('last_search_results', [])
            display_name = "نتایج جستجو"
        elif category.startswith("alb_"):
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
        context.user_data['cancel_forwarding'] = False
        sent_count = 0
        stopped_early = False

        try:
            await safe_edit_message_text(
                query,
                text=f"⏳ <b>در حال ارسال {len(tracks)} اثر از {display_name}...</b>\nلطفاً شکیبا باشید یا در صورت تمایل دکمه توقف را بزنید:",
                reply_markup=make_bulk_forwarding_keyboard()
            )

            for i, t in enumerate(tracks):
                if context.user_data.get('cancel_forwarding'):
                    stopped_early = True
                    break

                await send_track(query.message.chat_id, t, context)
                sent_count += 1

                if (i + 1) % 20 == 0:
                    await asyncio.sleep(3)
                else:
                    await asyncio.sleep(1.0)
        finally:
            context.user_data['is_forwarding'] = False

        # Update the old loading message so it does not stay in loading state forever
        if stopped_early:
            await safe_edit_message_text(
                query,
                text=f"🛑 <b>ارسال آثار {display_name} متوقف شد.</b>\nتعداد {sent_count} از {len(tracks)} اثر ارسال گردید.",
                reply_markup=None
            )
            finish_text = f"🛑 ارسال آثار <b>{display_name}</b> بنا به درخواست شما متوقف گردید."
        else:
            await safe_edit_message_text(
                query,
                text=f"✅ <b>ارسال تمام {sent_count} اثر از {display_name} با موفقیت پایان یافت.</b>",
                reply_markup=None
            )
            finish_text = f"✨ ارسال آثار <b>{display_name}</b> با موفقیت پایان یافت.\nبرای ادامه، بخش دلخواه خود را برگزینید:"

        await context.bot.send_message(
            query.message.chat_id,
            text=finish_text,
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
        await safe_edit_message_text(
            query,
            text=f"برای <b>{display_name}</b> اثری در آرشیو ثبت نشده است.",
            reply_markup=make_main_menu_keyboard()
        )
        return

    tracklist_kb = make_tracklist_keyboard(category, tracks, page=page, page_size=6)
    text = (
        f"🎵 <b>فهرست آثار {display_name}</b>\n"
        f"<i>مجموعاً {len(tracks)} نغمه در این مجموعه قرار دارد.</i>\n\n"
        "برای شنیدن هر قطعه، دکمه مربوط به آن را لمس نمایید یا جهت دریافت تمام آثار، دکمه «ارسال یکجا» را برگزینید:"
    )
    await safe_edit_message_text(query, text=text, reply_markup=tracklist_kb)
