import os
import sqlite3
import tempfile
import unittest

class TestDatabaseAndRepository(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_shajare.db")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_schema_init_and_crud(self):
        from bot.database.db import DatabaseManager
        from bot.database.repository import TrackRepository

        db_mgr = DatabaseManager(self.db_path)
        db_mgr.init_db()
        repo = TrackRepository(db_mgr)

        track_data = {
            "message_id": 726,
            "from_chat_id": "@Shajare1",
            "type": "forward",
            "title_fa": "آواز نسیم سحری",
            "title_en": "avaz nasim sahari",
            "album_id": "alb_nasim_vasl",
            "album_name": "نسیم وصل",
            "level": 1,
            "raw_caption": "avaz nasim sahari, آواز نسیم سحری آلبوم نسیم وصل"
        }
        row_id = repo.upsert_track(track_data)
        self.assertGreater(row_id, 0)

        track = repo.get_track_by_message_id(726)
        self.assertIsNotNone(track)
        self.assertEqual(track["title_fa"], "آواز نسیم سحری")
        self.assertEqual(track["album_name"], "نسیم وصل")

        # FTS5 search
        results = repo.search_tracks("نسیم سحری")
        self.assertTrue(any(t["message_id"] == 726 for t in results))

        # Query by album
        album_tracks = repo.get_tracks_by_album("alb_nasim_vasl")
        self.assertEqual(len(album_tracks), 1)

        # Query by level
        level_tracks = repo.get_tracks_by_level(1)
        self.assertEqual(len(level_tracks), 1)

        # Random track
        rand = repo.get_random_track()
        self.assertIsNotNone(rand)
        self.assertEqual(rand["message_id"], 726)

    def test_migration_pipeline(self):
        import json
        from scripts.migrate_posts import run_migration
        from bot.database.db import DatabaseManager
        from bot.database.repository import TrackRepository

        posts_sample = {
            "level1": [
                {"type": "forward", "from_chat_id": "@Shajare1", "message_id": 713},
                {"type": "forward", "from_chat_id": "@Shajare1", "message_id": 726}
            ],
            "alb_nasim_vasl": [
                {"type": "forward", "from_chat_id": "@Shajare1", "message_id": 726, "caption": "avaz nasim sahari, آواز نسیم سحری آلبوم نسیم وصل"}
            ]
        }
        json_path = os.path.join(self.tmp_dir.name, "sample_posts.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(posts_sample, f, ensure_ascii=False)

        count = run_migration(posts_path=json_path, db_path=self.db_path)
        self.assertEqual(count, 2)  # 2 unique messages: 713 and 726

        db_mgr = DatabaseManager(self.db_path)
        repo = TrackRepository(db_mgr)
        track726 = repo.get_track_by_message_id(726)
        self.assertEqual(track726["album_id"], "alb_nasim_vasl")
        self.assertEqual(track726["level"], 1)

        stats = repo.get_stats()
        self.assertEqual(stats["total_tracks"], 2)

if __name__ == "__main__":
    unittest.main()
