import unittest
from unittest.mock import AsyncMock, MagicMock, patch

class TestFalAndStart(unittest.IsolatedAsyncioTestCase):
    async def test_fal_removes_previous_reply_markup_on_reroll(self):
        from bot.handlers.fal import handle_fal_homayouni

        update = MagicMock()
        update.callback_query.message.chat_id = 12345
        update.callback_query.edit_message_reply_markup = AsyncMock()

        context = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get_random_track.return_value = {
            "message_id": 726,
            "title_fa": "تصنیف نسیم وصل",
            "type": "forward"
        }
        context.bot_data = {"repo": mock_repo}
        context.bot.send_message = AsyncMock()

        with patch("bot.handlers.fal.send_track", new_callable=AsyncMock) as mock_send:
            await handle_fal_homayouni(update, context)
            update.callback_query.edit_message_reply_markup.assert_called_once_with(reply_markup=None)
            self.assertEqual(context.bot.send_message.call_count, 2)
            mock_send.assert_called_once()

    async def test_start_invalid_deep_link_shows_warning(self):
        from bot.handlers.start import start_command

        update = MagicMock()
        update.message.reply_text = AsyncMock()

        context = MagicMock()
        context.args = ["track_999999"]
        mock_repo = MagicMock()
        mock_repo.get_track_by_message_id.return_value = None  # Not found
        context.bot_data = {"repo": mock_repo, "channel_name": "شجره"}

        await start_command(update, context)

        # First call is warning, second is welcome message with keyboard
        self.assertEqual(update.message.reply_text.call_count, 2)
        warning_call = update.message.reply_text.call_args_list[0][0][0]
        self.assertIn("قطعه مورد نظر در آرشیو یافت نشد", warning_call)

if __name__ == "__main__":
    unittest.main()
