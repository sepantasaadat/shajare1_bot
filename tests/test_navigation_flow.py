import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import telegram

class TestNavigationFlow(unittest.IsolatedAsyncioTestCase):
    async def test_noop_callback_shows_alert(self):
        from bot.handlers.navigation import button_callback

        update = MagicMock()
        update.callback_query.data = "noop"
        update.callback_query.answer = AsyncMock()

        context = MagicMock()
        context.user_data = {}
        context.bot_data = {}

        await button_callback(update, context)

        update.callback_query.answer.assert_called_once_with(
            "ℹ️ شما در حال مشاهده این صفحه از فهرست هستید. برای جابه‌جایی از دکمه‌های قبلی و بعدی استفاده فرمایید.",
            show_alert=True
        )

    async def test_stop_bulk_forwarding_callback(self):
        from bot.handlers.navigation import button_callback

        update = MagicMock()
        update.callback_query.data = "stop_bulk_forwarding"
        update.callback_query.answer = AsyncMock()

        context = MagicMock()
        context.user_data = {"is_forwarding": True}
        context.bot_data = {}

        await button_callback(update, context)

        self.assertTrue(context.user_data.get("cancel_forwarding"))
        update.callback_query.answer.assert_called_once_with(
            "درخواست توقف ارسال ثبت شد.",
            show_alert=True
        )

    async def test_play_shows_toast(self):
        from bot.handlers.navigation import button_callback

        update = MagicMock()
        update.callback_query.data = "play_726"
        update.callback_query.answer = AsyncMock()
        update.callback_query.message.chat_id = 12345

        context = MagicMock()
        context.user_data = {}
        mock_repo = MagicMock()
        mock_repo.get_track_by_message_id.return_value = {
            "message_id": 726,
            "title_fa": "تصنیف نسیم وصل",
            "type": "forward"
        }
        context.bot_data = {"repo": mock_repo}

        with patch("bot.handlers.navigation.send_track", new_callable=AsyncMock) as mock_send:
            await button_callback(update, context)
            mock_send.assert_called_once()
            update.callback_query.answer.assert_called_once_with(
                "🎧 در حال ارسال نغمه...",
                show_alert=False
            )

if __name__ == "__main__":
    unittest.main()
