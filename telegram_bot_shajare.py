from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import json
import os
import asyncio
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
    "امشب کنار غزل های من بخواب": "alb_emshab_kenar_ghazal",
    "ایران من": "alb_iran_man",
    "افسانه چشمهایت": "alb_afsane_cheshmhayat",
    "گاه فراموشی": "alb_gah_faramoshi",
    "شین میم سین": "alb_shin_mim_sin"
}

def load_posts(path: str):
    if not os.path.exists(path):
        base = {f"level{i}": [] for i in range(1, 6)}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(base, f, ensure_ascii=False, indent=2)
        return base
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

async def send_post(chat_id: int, post: dict, context: ContextTypes.DEFAULT_TYPE):
    typ = post.get("type", "text")
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
        try:
            await context.bot.forward_message(chat_id, from_chat_id=from_chat, message_id=msg_id)
        except Exception as e:
            await context.bot.send_message(chat_id, text=f"خطا در فوروارد پیام: {e}")

    else:
        await context.bot.send_message(chat_id, text=f"نوع پست پشتیبانی نمی‌شود: {typ}")

def make_levels_keyboard():
    
    keyboard = [
        [InlineKeyboardButton("level1", callback_data="level1")],
        [InlineKeyboardButton("level2", callback_data="level2")],
        [InlineKeyboardButton("level3", callback_data="level3")],
        [InlineKeyboardButton("level4", callback_data="level4")],
        [InlineKeyboardButton("level5", callback_data="level5")],
        [InlineKeyboardButton("🎵 آلبوم‌ها", callback_data="show_albums_menu")],
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
    reply_markup = make_levels_keyboard()
    await update.message.reply_text(
        f"سلام! به کانال: {CHANNEL_NAME}خوش آمدید\nگزینه مورد نظر را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "show_albums_menu":
        await query.edit_message_text(
            text="لطفاً آلبوم مورد نظر را انتخاب کنید:",
            reply_markup=make_albums_keyboard() 
        )
        return 

    if data == "back_to_main":
        await query.edit_message_text(
            text=f"به کانال: {CHANNEL_NAME} خوش آمدید\nگزینه مورد نظر را انتخاب کنید:",
            reply_markup=make_levels_keyboard() 
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
        
        await query.edit_message_text(text=f"برای {display_name} پستی تعریف نشده است.")
        
        markup = make_albums_keyboard() if data.startswith("alb_") else make_levels_keyboard()
        
        await context.bot.send_message(
            query.message.chat_id,
            text="یک گزینه دیگر انتخاب کنید:",
            reply_markup=markup
        )
        return

    display_name = data
    for p_name, c_id in ALBUMS_DATA.items():
        if c_id == data:
            display_name = p_name
            break
            
    await query.edit_message_text(text=f"در حال ارسال {len(level_posts)} پست از {display_name}...")

    for p in level_posts:
        await send_post(query.message.chat_id, p, context)
        await asyncio.sleep(0.5)

    await context.bot.send_message(query.message.chat_id, text="ارسال پست‌ها تمام شد.")
    
    markup = make_albums_keyboard() if data.startswith("alb_") else make_levels_keyboard()
    await context.bot.send_message(
        query.message.chat_id,
        text="یک گزینه دیگر انتخاب کنید:",
        reply_markup=markup
    )


def main():
    posts = load_posts(POSTS_FILE)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.bot_data["posts"] = posts

    app.add_handler(CommandHandler("start", start_command))

    app.add_handler(CallbackQueryHandler(button_callback))

    print("ربات در حال اجرا است...")
    app.run_polling()

if __name__ == "__main__":
    main()