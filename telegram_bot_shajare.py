from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import json
import os
import asyncio
CHANNEL_NAME = "شجره"
POSTS_FILE = "posts.json"
BOT_TOKEN = "8549850754:AAHplEUEuK21cEwwOhbTtSPlFbaUetlmS7M"

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
    
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("level1", callback_data="level1")],
        [InlineKeyboardButton("level2", callback_data="level2")],
        [InlineKeyboardButton("level3", callback_data="level3")],
        [InlineKeyboardButton("level4", callback_data="level4")],
        [InlineKeyboardButton("level5", callback_data="level5")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"سلام! کانال: {CHANNEL_NAME}\nیک سطح انتخاب کنید:",
        reply_markup=reply_markup
    )
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data 
    posts = context.bot_data.get("posts", {})
    level_posts = posts.get(data, [])    
    if not level_posts:
        await query.edit_message_text(text=f"برای {data} پستی تعریف نشده است.")
        return
    await query.edit_message_text(text=f"در حال ارسال {len(level_posts)} پست از {data}...")

    for p in level_posts:
        await send_post(query.message.chat_id, p, context)
        await asyncio.sleep(0.5) 


    await context.bot.send_message(query.message.chat_id, text="ارسال پست‌ها تمام شد.")

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