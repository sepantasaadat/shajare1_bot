import asyncio
import logging
from typing import Dict, Any
import telegram
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def send_track(
    chat_id: int,
    track: Dict[str, Any],
    context: ContextTypes.DEFAULT_TYPE,
    max_retries: int = 3
) -> bool:
    """
    Safely delivers a track to a chat with rate limit handling,
    exponential backoff, and error isolation.
    Returns True on success, False on failure.
    """
    typ = track.get("type", "forward")
    for attempt in range(max_retries):
        try:
            if typ == "forward":
                from_chat = track.get("from_chat_id", "@Shajare1")
                msg_id = track.get("message_id")
                if not from_chat or not msg_id:
                    await context.bot.send_message(
                        chat_id,
                        text="تنظیمات فوروارد نادرست است: from_chat_id یا message_id وجود ندارد."
                    )
                    return False
                await context.bot.forward_message(chat_id, from_chat_id=from_chat, message_id=msg_id)
            elif typ == "text":
                await context.bot.send_message(chat_id, text=track.get("content", ""))
            elif typ == "photo":
                await context.bot.send_photo(
                    chat_id,
                    photo=track.get("content"),
                    caption=track.get("raw_caption") or track.get("caption")
                )
            elif typ == "document":
                await context.bot.send_document(
                    chat_id,
                    document=track.get("content"),
                    caption=track.get("raw_caption") or track.get("caption")
                )
            else:
                await context.bot.send_message(chat_id, text=f"نوع پست پشتیبانی نمی‌شود: {typ}")
                return False
            return True
        except telegram.error.RetryAfter as e:
            wait_time = e.retry_after + 1
            logger.warning("Rate limit hit! Waiting %s seconds before retry...", wait_time)
            await asyncio.sleep(wait_time)
        except telegram.error.TimedOut:
            logger.warning("Telegram request timed out. Retrying attempt %d...", attempt + 1)
            await asyncio.sleep(2 ** attempt)
        except Exception as e:
            logger.error("Error delivering track to chat %s: %s", chat_id, e, exc_info=True)
            await context.bot.send_message(
                chat_id,
                text="متأسفانه در ارسال این اثر خطایی رخ داد. لطفاً لحظاتی دیگر تلاش فرمایید."
            )
            return False
    return False
