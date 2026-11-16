import unittest
from telegram import InlineKeyboardMarkup

class TestKeyboards(unittest.TestCase):
    def test_main_menu_keyboard(self):
        from bot.keyboards.menus import make_main_menu_keyboard
        kb = make_main_menu_keyboard()
        self.assertIsInstance(kb, InlineKeyboardMarkup)
        # Check expected callbacks exist
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row if btn.callback_data]
        self.assertIn("show_levels_menu", callbacks)
        self.assertIn("show_albums_menu", callbacks)
        self.assertIn("fale_homayouni", callbacks)
        self.assertIn("search_guide", callbacks)

    def test_albums_keyboard(self):
        from bot.keyboards.menus import make_albums_keyboard
        kb = make_albums_keyboard()
        self.assertIsInstance(kb, InlineKeyboardMarkup)
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row if btn.callback_data]
        self.assertIn("alb_nasim_vasl", callbacks)
        self.assertIn("back_to_main", callbacks)

    def test_tracklist_keyboard_pagination(self):
        from bot.keyboards.menus import make_tracklist_keyboard
        mock_tracks = [
            {"message_id": 100 + i, "title_fa": f"قطعه {i}"} for i in range(12)
        ]
        # Page 0 (tracks 0 to 5)
        kb_page0 = make_tracklist_keyboard("alb_nasim_vasl", mock_tracks, page=0, page_size=6)
        callbacks0 = [btn.callback_data for row in kb_page0.inline_keyboard for btn in row if btn.callback_data]
        self.assertIn("play_100", callbacks0)
        self.assertIn("play_105", callbacks0)
        self.assertNotIn("play_106", callbacks0)
        self.assertIn("bulk_alb_nasim_vasl", callbacks0)
        self.assertIn("alb_nasim_vasl_page_1", callbacks0)

        # Page 1 (tracks 6 to 11)
        kb_page1 = make_tracklist_keyboard("alb_nasim_vasl", mock_tracks, page=1, page_size=6)
        callbacks1 = [btn.callback_data for row in kb_page1.inline_keyboard for btn in row if btn.callback_data]
        self.assertIn("play_106", callbacks1)
        self.assertIn("play_111", callbacks1)
        self.assertIn("alb_nasim_vasl_page_0", callbacks1)

    def test_fal_keyboard(self):
        from bot.keyboards.menus import make_fal_keyboard
        kb = make_fal_keyboard()
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row if btn.callback_data]
        self.assertIn("fale_homayouni", callbacks)
        self.assertIn("back_to_main", callbacks)

if __name__ == "__main__":
    unittest.main()
