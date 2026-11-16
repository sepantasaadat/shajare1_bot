import os
import unittest
from unittest.mock import patch

class TestEntryPoint(unittest.TestCase):
    @patch.dict(os.environ, {"BOT_TOKEN": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz_dummy_token", "ADMIN_USER_IDS": "12345,67890"})
    def test_create_app(self):
        from bot.main import create_app
        from telegram.ext import CommandHandler, CallbackQueryHandler, InlineQueryHandler, MessageHandler

        app = create_app()
        self.assertIsNotNone(app)
        self.assertIn("repo", app.bot_data)
        self.assertEqual(app.bot_data["admin_user_ids"], [12345, 67890])

        # Check registered handler types in group 0
        handlers = app.handlers.get(0, [])
        handler_types = [type(h) for h in handlers]
        self.assertIn(CommandHandler, handler_types)
        self.assertIn(CallbackQueryHandler, handler_types)
        self.assertIn(InlineQueryHandler, handler_types)
        self.assertIn(MessageHandler, handler_types)

    def test_root_entrypoint_compatibility(self):
        import telegram_bot_shajare
        self.assertTrue(hasattr(telegram_bot_shajare, "main"))
        self.assertTrue(hasattr(telegram_bot_shajare, "CHANNEL_NAME"))
        self.assertTrue(hasattr(telegram_bot_shajare, "ALBUMS_DATA"))

if __name__ == "__main__":
    unittest.main()
