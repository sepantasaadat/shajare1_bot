import os
import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER UNIQUE NOT NULL,
    from_chat_id TEXT NOT NULL DEFAULT '@Shajare1',
    type TEXT NOT NULL DEFAULT 'forward',
    title_fa TEXT,
    title_en TEXT,
    album_id TEXT,
    album_name TEXT,
    level INTEGER,
    raw_caption TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tracks_album ON tracks(album_id);
CREATE INDEX IF NOT EXISTS idx_tracks_level ON tracks(level);
CREATE INDEX IF NOT EXISTS idx_tracks_message_id ON tracks(message_id);

CREATE VIRTUAL TABLE IF NOT EXISTS tracks_fts USING fts5(
    title_fa,
    title_en,
    album_name,
    raw_caption,
    content='tracks',
    content_rowid='id',
    tokenize='unicode61'
);

-- Triggers to keep FTS table in sync with tracks table
CREATE TRIGGER IF NOT EXISTS tracks_ai AFTER INSERT ON tracks BEGIN
    INSERT INTO tracks_fts(rowid, title_fa, title_en, album_name, raw_caption)
    VALUES (new.id, new.title_fa, new.title_en, new.album_name, new.raw_caption);
END;

CREATE TRIGGER IF NOT EXISTS tracks_ad AFTER DELETE ON tracks BEGIN
    INSERT INTO tracks_fts(tracks_fts, rowid, title_fa, title_en, album_name, raw_caption)
    VALUES ('delete', old.id, old.title_fa, old.title_en, old.album_name, old.raw_caption);
END;

CREATE TRIGGER IF NOT EXISTS tracks_au AFTER UPDATE ON tracks BEGIN
    INSERT INTO tracks_fts(tracks_fts, rowid, title_fa, title_en, album_name, raw_caption)
    VALUES ('delete', old.id, old.title_fa, old.title_en, old.album_name, old.raw_caption);
    INSERT INTO tracks_fts(rowid, title_fa, title_en, album_name, raw_caption)
    VALUES (new.id, new.title_fa, new.title_en, new.album_name, new.raw_caption);
END;
"""

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA busy_timeout = 5000;")
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
        logger.info("Database initialized successfully at %s", self.db_path)
