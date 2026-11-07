import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import json
import os
import asyncio
import random
CHANNEL_NAME = "شجره"
POSTS_FILE = "posts.json"
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
    "با ستاره ها": "alb_ba_setareha",
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
        [InlineKeyboardButton("📂 سطوح (Levels)", callback_data="show_levels_menu"),
         InlineKeyboardButton("🎵 آلبوم‌ها", callback_data="show_albums_menu")],
        
        [InlineKeyboardButton("🎲 فال همایونی (پخش تصادفی)", callback_data="fale_homayouni")],
        
        [InlineKeyboardButton("🔍 جستجوی پیشرفته", callback_data="search_guide"),
         InlineKeyboardButton("📞 ارتباط با ما", callback_data="contact_us")]
    ]
    return InlineKeyboardMarkup(keyboard)

def make_levels_keyboard():
    keyboard = [
        [InlineKeyboardButton("level1", callback_data="level1")],
        [InlineKeyboardButton("level2", callback_data="level2")],
        [InlineKeyboardButton("level3", callback_data="level3")],
        [InlineKeyboardButton("level4", callback_data="level4")],
        [InlineKeyboardButton("level5", callback_data="level5")],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def make_albums_keyboard():
    keyboard = []
    row = []
    for persian_name, callback_id in ALBUMS_DATA.items():
        btn = InlineKeyboardButton(persian_name, callback_data=callback_id)
        row.append(btn)

        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
        
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")])

    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = make_main_menu_keyboard()
    await update.message.reply_text(
        f"سلام! به کانال {CHANNEL_NAME} خوش آمدید.\nلطفاً از منوی زیر انتخاب کنید:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back_to_main":
        await query.edit_message_text(
            text=f"به کانال: {CHANNEL_NAME} خوش آمدید\nمنوی اصلی:",
            reply_markup=make_main_menu_keyboard()
        )
        return

    if data == "show_levels_menu":
        await query.edit_message_text(
            text="لطفاً سطح (Level) مورد نظر را انتخاب کنید:",
            reply_markup=make_levels_keyboard()
        )
        return

    if data == "show_albums_menu":
        await query.edit_message_text(
            text="لطفاً آلبوم مورد نظر را انتخاب کنید:",
            reply_markup=make_albums_keyboard()
        )
        return

    if data == "contact_us":
        # اینجا آیدی تلگرام خودتان را قرار دهید
        admin_id = "@cheraghii1" 
        await query.edit_message_text(
            text=f"📞 راه‌های ارتباطی با ما:\n\nبرای ارتباط مستقیم می‌توانید به آیدی زیر پیام دهید:\n{admin_id}\n\nیا نظرات خود را همینجا بنویسید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]])
        )
        return

    if data == "search_guide":
        context.user_data['waiting_for_search'] = True
        
        await query.edit_message_text(
            text="🔍 **حالت جستجو فعال شد**\n\nحالا کلمه مورد نظر (نام آهنگ، شعر یا آلبوم) را تایپ کنید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ لغو جستجو", callback_data="cancel_search")]])
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
            await context.bot.send_message(query.message.chat_id, text="هنوز هیچ آهنگی در آرشیو موجود نیست!")
            return

        random_post = random.choice(all_posts)
        await context.bot.send_message(query.message.chat_id, text="🎲 نیت کنید... فال شما آمد:")
        await send_post(query.message.chat_id, random_post, context)
        await asyncio.sleep(1)  
        await context.bot.send_message(
            query.message.chat_id,
            text="بازگشت به منوی اصلی:",
            reply_markup=make_main_menu_keyboard()
        )
        return

    posts = context.bot_data.get("posts", {})
    level_posts = posts.get(data, []) 

    if not level_posts:
        display_name = data
        for p_name, c_id in ALBUMS_DATA.items():
            if c_id == data:
                display_name = p_name
                break
        
        await context.bot.send_message(
            query.message.chat_id,
            text=f"برای {display_name} پستی تعریف نشده است."
        )
        return

    display_name = data
    for p_name, c_id in ALBUMS_DATA.items():
        if c_id == data:
            display_name = p_name
            break
            
    await query.edit_message_text(text=f"در حال ارسال {len(level_posts)} پست از {display_name}...")

    for i, p in enumerate(level_posts):
        await send_post(query.message.chat_id, p, context)
        if (i + 1) % 20 == 0:
            await asyncio.sleep(3)  # longer pause every 20 messages
        else:
            await asyncio.sleep(1.0)

    await context.bot.send_message(query.message.chat_id, text="ارسال پست‌ها تمام شد.")
    
    await context.bot.send_message(
        query.message.chat_id,
        text="چه کار دیگری انجام دهیم؟",
        reply_markup=make_main_menu_keyboard()
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

    await update.message.reply_text(f"🔍 در حال جستجو برای: «{user_text}»...")

    for category, post_list in posts.items():
        for post in post_list:
            content = post.get("content", "")
            caption = post.get("caption", "")
            if (content and str(content).lower().find(query_text) != -1) or \
               (caption and str(caption).lower().find(query_text) != -1):
                found_posts.append(post)

    if not found_posts:
        await update.message.reply_text(
            f"❌ متاسفانه موردی یافت نشد.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]])
        )
    else:
        await update.message.reply_text(f"✅ تعداد {len(found_posts)} مورد پیدا شد:")
        for p in found_posts[:5]: 
            await send_post(update.message.chat_id, p, context)
            await asyncio.sleep(1.0)
        
        await update.message.reply_text(
            "پایان نتایج جستجو.",
            reply_markup=make_main_menu_keyboard()
        )

    context.user_data['waiting_for_search'] = False


def main():
    posts = load_posts(POSTS_FILE)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.bot_data["posts"] = posts

    app.add_handler(CommandHandler("start", start_command))

    app.add_handler(CallbackQueryHandler(button_callback))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_message))

    print(f"ربات {CHANNEL_NAME} با موفقیت اجرا شد...")
    app.run_polling()

if __name__ == "__main__":
    main()