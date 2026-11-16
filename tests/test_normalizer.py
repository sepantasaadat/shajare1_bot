import unittest

class TestPersianNormalizer(unittest.TestCase):
    def test_arabic_character_unification(self):
        from bot.services.normalizer import normalize_persian
        self.assertEqual(normalize_persian("موسيقي"), "موسیقی")
        self.assertEqual(normalize_persian("كودك"), "کودک")
        self.assertEqual(normalize_persian("نامۀ دوست"), "نامه دوست")

    def test_diacritic_removal(self):
        from bot.services.normalizer import normalize_persian
        self.assertEqual(normalize_persian("آبِ نانِ آوَازْ"), "آب نان آواز")

    def test_alif_folding_for_search(self):
        from bot.services.normalizer import normalize_for_search
        # In search, 'آ' should match 'ا', 'إ' and 'أ' should match 'ا'
        self.assertEqual(normalize_for_search("آواز"), normalize_for_search("اواز"))
        self.assertEqual(normalize_for_search("ایرانِ من"), "ایران من")
        self.assertEqual(normalize_for_search("آب نان آواز"), "اب نان اواز")

    def test_zwnj_and_whitespace_handling(self):
        from bot.services.normalizer import normalize_persian
        # Ensure redundant whitespace and multiple spaces are collapsed
        self.assertEqual(normalize_persian("با   ستاره ها"), "با ستاره ها")
        # Ensure ZWNJ is preserved in normalizer
        self.assertIn("\u200c", normalize_persian("چشم\u200cهایت"))

    def test_english_case_folding(self):
        from bot.services.normalizer import normalize_for_search
        self.assertEqual(normalize_for_search("Nasim Vasl"), "nasim vasl")

    def test_fuzzy_match(self):
        from bot.services.normalizer import fuzzy_match_score
        score = fuzzy_match_score("نسیم سحر", "آواز نسیم سحری آلبوم نسیم وصل")
        self.assertGreater(score, 70.0)

if __name__ == "__main__":
    unittest.main()
