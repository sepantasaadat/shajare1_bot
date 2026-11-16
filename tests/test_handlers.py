import unittest
from unittest.mock import AsyncMock, MagicMock, patch

class TestHandlers(unittest.IsolatedAsyncioTestCase):
    async def test_admin_only_decorator(self):
        from bot.handlers.admin import admin_only

        mock_func = AsyncMock(return_value="executed")
        decorated = admin_only(mock_func)

        # Unauthorized user
        update_unauth = MagicMock()
        update_unauth.effective_user.id = 999999
        update_unauth.message.reply_text = AsyncMock()
        context = MagicMock()
        context.bot_data = {"admin_user_ids": [12345, 67890]}

        await decorated(update_unauth, context)
        mock_func.assert_not_called()
        update_unauth.message.reply_text.assert_called_once()

        # Authorized user
        update_auth = MagicMock()
        update_auth.effective_user.id = 12345
        update_auth.message.reply_text = AsyncMock()
        await decorated(update_auth, context)
        mock_func.assert_called_once()

    def test_extract_deep_link_track_id(self):
        from bot.handlers.start import extract_deep_link_track_id

        self.assertEqual(extract_deep_link_track_id(["track_726"]), 726)
        self.assertEqual(extract_deep_link_track_id(["track=726"]), 726)
        self.assertIsNone(extract_deep_link_track_id([]))
        self.assertIsNone(extract_deep_link_track_id(["invalid"]))

    def test_fal_verses_selection(self):
        from bot.handlers.fal import get_random_bayt
        bayt = get_random_bayt()
        self.assertIsInstance(bayt, str)
        self.assertGreater(len(bayt), 10)

if __name__ == "__main__":
    unittest.main()
