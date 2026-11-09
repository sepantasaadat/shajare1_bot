import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import json
import os
import asyncio
import random

CHANNEL_NAME = "شجره"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_FILE = os.path.join(BASE_DIR, "posts.json")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

ALBUMS_DATA = {
    "نسیم وصل": "alb_nasim_vasl",
    "با ستاره ها": "alb_ba_setareha",
    "نقش خیال": "alb_naghsh_khial",
    "ناشکیبا": "alb_nashakiba",
    "قیژک کولی": "alb_ghijak_koli",
    "خورشید آرزو": "alb_khorshid_arezo",
    "آب نان آواز": "alb_ab_nan_avaz",
    "سیمرغ": "alb_simorgh",
    "چه آتش ها": "alb_che_atash_ha",
    "نه فرشته ام نه شیطان": "alb_na_fereshte",
    "شب جدایی": "alb_shab_jodayi",
    "ای جان جان بی من مرو": "alb_ey_jan_jan",
    "مستور و مست": "alb_mastor_mast",
    "خداوندان اسرار": "alb_khodavandan_asrar",
    "رگ خواب": "alb_rag_khab",
    "شوق دوست": "alb_shogh_doost",
    "ایران من": "alb_iran_man",
    "افسانه چشمهایت": "alb_afsane_cheshmhayat",
    "گاه فراموشی": "alb_gah_faramoshi",
    "شین میم سین": "alb_shin_mim_sin",
    "امشب کنار غزل های من بخواب": "alb_emshab_kenar_ghazal"
}

def load_posts(path: str):
    if not os.path.exists(path):
        base = {f"level{i}": [] for i in range(1, 6)}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(base, f, ensure_ascii=False, indent=2)
        return base
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

async def send_post(chat_id: int, post: dict, context: ContextTypes.DEFAULT_TYPE, max_retries: int = 3):
    typ = post.get("type", "text")
    for attempt in range(max_retries):
        try:
            if typ == "text":
                await context.bot.send_message(chat_id, text=post.get("content", ""))
            elif typ == "photo":
                await context.bot.send_photo(chat_id, photo=post.get("content"), caption=post.get("caption"))
            elif typ == "document":
                await context.bot.send_document(chat_id, document=post.get("content"), caption=post.get("caption"))
            elif typ == "forward":
                from_chat = post.get("from_chat_id")
                msg_id = post.get("message_id")
                if not from_chat or not msg_id:
                    await context.bot.send_message(chat_id, text="تنظیمات فوروارد نادرست است: from_chat_id یا message_id وجود ندارد.")
                    return
                await context.bot.forward_message(chat_id, from_chat_id=from_chat, message_id=msg_id)
            else:
                await context.bot.send_message(chat_id, text=f"نوع پست پشتیبانی نمی‌شود: {typ}")
            return  # Success - exit the retry loop
        except telegram.error.RetryAfter as e:
            wait_time = e.retry_after + 1
            print(f"Rate limit hit! Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except telegram.error.TimedOut:
            await asyncio.sleep(2 ** attempt)
        except Exception as e:
            await context.bot.send_message(chat_id, text=f"خطا در ارسال پیام: {e}")
            return

def make_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🗂 سطوح آرشیو", callback_data="show_levels_menu"),
            InlineKeyboardButton("🎵 آلبوم‌ها", callback_data="show_albums_menu")
        ],
        [
            InlineKeyboardButton("🪶 فال همایونی (نغمه تصادفی)", callback_data="fale_homayouni")
        ],
        [
            InlineKeyboardButton("🔍 جستجوی اثر", callback_data="search_guide"),
            InlineKeyboardButton("📩 پیام به مدیریت", callback_data="contact_us")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def make_levels_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("▫️ سطح ۱", callback_data="level1"),
            InlineKeyboardButton("▫️ سطح ۲", callback_data="level2")
        ],
        [
            InlineKeyboardButton("▫️ سطح ۳", callback_data="level3"),
            InlineKeyboardButton("▫️ سطح ۴", callback_data="level4")
        ],
        [
            InlineKeyboardButton("▫️ سطح ۵", callback_data="level5")
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def make_albums_keyboard():
    keyboard = []
    row = []
    for persian_name, callback_id in ALBUMS_DATA.items():
        btn = InlineKeyboardButton(f"💿 {persian_name}", callback_data=callback_id)
        row.append(btn)

        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
        
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")])

    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        f"🌿 <b>به گنجینه صوتی «{CHANNEL_NAME}» خوش آمدید</b> 🌿\n"
        "<i>آرشیو و راهنمای آثار استاد همایون شجریان</i>\n\n"
        "لطفاً بخش یا نغمه مورد نظر خود را از منوی زیر انتخاب نمایید:"
    )
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=make_main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back_to_main":
        await query.edit_message_text(
            text=(
                f"🌿 <b>گنجینه صوتی «{CHANNEL_NAME}»</b>\n\n"
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
        admin_url = "https://t.me/cheraghii1"
        contact_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 گفتگوی مستقیم در تلگرام", url=admin_url)],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ])
        await query.edit_message_text(
            text=(
                "📩 <b>راه‌های ارتباط با ما</b>\n\n"
                "برای ارسال انتقادات، پیشنهادات یا در میان گذاشتن نظرات خود درباره کانال و ربات شجره، "
                "می‌توانید مستقیماً با مدیریت در ارتباط باشید:"
            ),
            reply_markup=contact_keyboard,
            parse_mode=ParseMode.HTML
        )
        return

    if data == "search_guide":
        context.user_data['waiting_for_search'] = True
        cancel_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ انصراف و بازگشت", callback_data="cancel_search")]
        ])
        await query.edit_message_text(
            text=(
                "🔍 <b>حالت جستجوی اثر فعال شد</b>\n\n"
                "لطفاً بخشی از <b>نام قطعه، شعر، تصنیف یا آلبوم</b> مورد نظر خود را تایپ و ارسال فرمایید:"
            ),
            reply_markup=cancel_keyboard,
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
        posts_data = context.bot_data.get("posts", {})
        all_posts = []
        for key, post_list in posts_data.items():
            all_posts.extend(post_list)
        
        if not all_posts:
            await context.bot.send_message(query.message.chat_id, text="هنوز اثری در آرشیو ثبت نشده است.")
            return

        random_post = random.choice(all_posts)
        await context.bot.send_message(
            query.message.chat_id,
            text="🪶 <i>نیت کنید و گوش دل بسپارید... فال شما:</i>",
            parse_mode=ParseMode.HTML
        )
        await send_post(query.message.chat_id, random_post, context)
        await asyncio.sleep(1)  
        await context.bot.send_message(
            query.message.chat_id,
            text="🌿 برای شنیدن دیگر نغمه‌ها از منوی زیر استفاده کنید:",
            reply_markup=make_main_menu_keyboard()
        )
        return

    posts = context.bot_data.get("posts", {})
    level_posts = posts.get(data, []) 

    level_names = {
        "level1": "سطح ۱",
        "level2": "سطح ۲",
        "level3": "سطح ۳",
        "level4": "سطح ۴",
        "level5": "سطح ۵",
    }
    display_name = level_names.get(data)
    if not display_name:
        for p_name, c_id in ALBUMS_DATA.items():
            if c_id == data:
                display_name = f"آلبوم «{p_name}»"
                break
    if not display_name:
        display_name = data

    if not level_posts:
        await context.bot.send_message(
            query.message.chat_id,
            text=f"برای <b>{display_name}</b> اثری در آرشیو ثبت نشده است.",
            parse_mode=ParseMode.HTML
        )
        return

    await query.edit_message_text(
        text=f"⏳ <b>در حال ارسال {len(level_posts)} اثر از {display_name}...</b>\nلطفاً صبور باشید.",
        parse_mode=ParseMode.HTML
    )

    for i, p in enumerate(level_posts):
        await send_post(query.message.chat_id, p, context)
        if (i + 1) % 20 == 0:
            await asyncio.sleep(3)  # longer pause every 20 messages
        else:
            await asyncio.sleep(1.0)

    completion_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🗂 بازگشت به سطوح", callback_data="show_levels_menu"),
            InlineKeyboardButton("🎵 بازگشت به آلبوم‌ها", callback_data="show_albums_menu")
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")
        ]
    ])
    await context.bot.send_message(
        query.message.chat_id,
        text=f"✨ ارسال آثار <b>{display_name}</b> با موفقیت پایان یافت.\nبرای ادامه، بخش دلخواه خود را برگزینید:",
        reply_markup=completion_keyboard,
        parse_mode=ParseMode.HTML
    )

async def handle_search_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting_for_search'):
        return 

    user_text = update.message.text
    if not user_text:
        return

    query_text = user_text.strip().lower()
    posts = context.bot_data.get("posts", {})
    found_posts = []

    await update.message.reply_text(
        f"🔍 در حال جستجو برای: «<b>{user_text.strip()}</b>»...",
        parse_mode=ParseMode.HTML
    )

    for category, post_list in posts.items():
        for post in post_list:
            content = post.get("content", "")
            caption = post.get("caption", "")
            if (content and str(content).lower().find(query_text) != -1) or \
               (caption and str(caption).lower().find(query_text) != -1):
                found_posts.append(post)

    if not found_posts:
        no_res_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 جستجوی مجدد", callback_data="search_guide")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ])
        await update.message.reply_text(
            f"❌ متاسفانه اثری مطابق با «<b>{user_text.strip()}</b>» یافت نشد.\nمی‌توانید کلمه دیگری را جستجو کنید.",
            reply_markup=no_res_keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        total_count = len(found_posts)
        if total_count > 5:
            header_text = f"✅ تعداد <b>{total_count}</b> اثر یافت شد (نمایش ۵ اثر اول):"
        else:
            header_text = f"✅ تعداد <b>{total_count}</b> اثر یافت شد:"

        await update.message.reply_text(header_text, parse_mode=ParseMode.HTML)

        for p in found_posts[:5]: 
            await send_post(update.message.chat_id, p, context)
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

def main():
    if not BOT_TOKEN:
        print("هشدار: متغیر محیطی BOT_TOKEN تنظیم نشده است.")

    posts = load_posts(POSTS_FILE)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.bot_data["posts"] = posts

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_message))

    print(f"ربات {CHANNEL_NAME} با موفقیت اجرا شد...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
