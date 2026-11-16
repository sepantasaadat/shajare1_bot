import random
import asyncio
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.keyboards.menus import make_fal_keyboard
from bot.services.forwarder import send_track

logger = logging.getLogger(__name__)

CURATED_BAYTS = [
    "دل می‌رود ز دستم صاحب دلان خدا را\nدردا که راز پنهان خواهد شد آشکارا",
    "مرا عهدیست با جانان که تا جان در بدن دارم\nهواداران کویش را چو جان خویشتن دارم",
    "هواخواه توام جانا و می‌دانم که می‌دانی\nکه هم نادیده می‌بینی و هم ننوشته می‌خوانی",
    "یوسف گمگشته بازآید به کنعان غم مخور\nکلبه احزان شود روزی گلستان غم مخور",
    "غم زمانه خورم یا قدح کشم خوشدل\nکه در زمانه ندانم چه در خور کار است",
    "در ازل پرتو حسنت ز تجلی دم زد\nعشق پیدا شد و آتش به همه عالم زد",
    "ای صبا گر بگذری بر کوی مه افشان من\nبوی زلف یار بر دلدادگان آسان رسان",
    "چو شب به راه تو ماندم که ماه من باشی\nچراغ خلوت تنهایی دلم باشی",
    "رو سر بنه به بالین تنها مرا رها کن\nترک من خراب شب گرد مبتلا کن",
    "من غلام قمرم غیر قمر هیچ مگو\nپیش من جز سخی شمع و شکر هیچ مگو",
    "سمن بویان غبار غم چو بنشینند بنشانند\nپری رویان قرار از دل چو بربندند بستانند",
    "مژده ای دل که مسیحا نفسی می‌آید\nکه ز انفاس خوشش بوی کسی می‌آید"
]

def get_random_bayt() -> str:
    return random.choice(CURATED_BAYTS)

async def handle_fal_homayouni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id if query and query.message else update.effective_chat.id
    repo = context.bot_data.get("repo")

    if not repo:
        await context.bot.send_message(chat_id, text="متأسفانه آرشیو نغمات موقتاً در دسترس نیست.")
        return

    random_track = repo.get_random_track()
    if not random_track:
        await context.bot.send_message(chat_id, text="هنوز اثری در آرشیو ثبت نشده است.")
        return

    bayt = get_random_bayt()
    fal_text = (
        "🪶 <b>فال همایونی</b>\n\n"
        f"<i>«{bayt}»</i>\n\n"
        "نغمه هدیه به گوش دل شما:"
    )

    await context.bot.send_message(chat_id, text=fal_text, parse_mode=ParseMode.HTML)
    await send_track(chat_id, random_track, context)
    await asyncio.sleep(1)
    await context.bot.send_message(
        chat_id,
        text="🌿 برای شنیدن نغمه‌ای دیگر یا بازگشت به منو، برگزینید:",
        reply_markup=make_fal_keyboard()
    )
