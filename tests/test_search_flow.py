import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram.constants import ChatType

class TestSearchFlow(unittest.IsolatedAsyncioTestCase):
    async def test_search_renders_paginated_keyboard(self):
        from bot.handlers.search import handle_search_message

        update = MagicMock()
        update.effective_chat.type = ChatType.PRIVATE
        update.effective_chat.id = 12345
        update.message.text = "نسیم"
        update.message.chat_id = 12345
        update.message.reply_text = AsyncMock()

        context = MagicMock()
        context.user_data = {"waiting_for_search": True}
        mock_repo = MagicMock()
        mock_repo.search_tracks.return_value = [
            {"message_id": 101, "title_fa": "تصنیف نسیم وصل", "album_name": "نسیم وصل"},
            {"message_id": 102, "title_fa": "آواز نسیم سحری", "album_name": "نسیم وصل"}
        ]
        context.bot_data = {"repo": mock_repo}

        await handle_search_message(update, context)

        # Ensure reply_text was called with a reply_markup containing search results
        self.assertTrue(update.message.reply_text.called)
        call_args = update.message.reply_text.call_args[1]
        self.assertIn("reply_markup", call_args)
        kb = call_args["reply_markup"]
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row if btn.callback_data]
        self.assertIn("play_101", callbacks)
        self.assertIn("play_102", callbacks)
        self.assertIn("bulk_search", callbacks)

    async def test_natural_text_search_without_prior_prompt(self):
        from bot.handlers.search import handle_search_message

        update = MagicMock()
        update.effective_chat.type = ChatType.PRIVATE
        update.effective_chat.id = 12345
        update.message.text = "ایران من"
        update.message.chat_id = 12345
        update.message.reply_text = AsyncMock()

        # waiting_for_search is NOT set
        context = MagicMock()
        context.user_data = {}
        mock_repo = MagicMock()
        mock_repo.search_tracks.return_value = [
            {"message_id": 201, "title_fa": "قلاب", "album_name": "ایران من"}
        ]
        context.bot_data = {"repo": mock_repo}

        await handle_search_message(update, context)

        # Should still search and return results
        self.assertTrue(update.message.reply_text.called)
        self.assertIn("last_search_results", context.user_data)

    async def test_cleans_up_search_prompt_button(self):
        from bot.handlers.search import handle_search_message

        update = MagicMock()
        update.effective_chat.type = ChatType.PRIVATE
        update.effective_chat.id = 12345
        update.message.text = "سیمرغ"
        update.message.chat_id = 12345
        update.message.reply_text = AsyncMock()

        context = MagicMock()
        context.user_data = {"waiting_for_search": True, "search_prompt_msg_id": 999}
        context.bot.edit_message_reply_markup = AsyncMock()
        mock_repo = MagicMock()
        mock_repo.search_tracks.return_value = []
        context.bot_data = {"repo": mock_repo}

        await handle_search_message(update, context)

        # Ensure edit_message_reply_markup was called to remove prompt keyboard
        context.bot.edit_message_reply_markup.assert_called_once_with(
            chat_id=12345,
            message_id=999,
            reply_markup=None
        )

if __name__ == "__main__":
    unittest.main()
