import os
import re
import logging
from typing import List, Optional, Dict, Any
from bot.database.db import DatabaseManager
from bot.services.normalizer import normalize_for_search, fuzzy_match_score

logger = logging.getLogger(__name__)

class TrackRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def upsert_track(self, data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO tracks (
            message_id, from_chat_id, type, title_fa, title_en,
            album_id, album_name, level, raw_caption, content
        ) VALUES (
            :message_id, :from_chat_id, :type, :title_fa, :title_en,
            :album_id, :album_name, :level, :raw_caption, :content
        )
        ON CONFLICT(message_id) DO UPDATE SET
            title_fa = COALESCE(:title_fa, tracks.title_fa),
            title_en = COALESCE(:title_en, tracks.title_en),
            album_id = COALESCE(:album_id, tracks.album_id),
            album_name = COALESCE(:album_name, tracks.album_name),
            level = COALESCE(:level, tracks.level),
            raw_caption = COALESCE(:raw_caption, tracks.raw_caption),
            content = COALESCE(:content, tracks.content)
        RETURNING id;
        """
        params = {
            "message_id": data.get("message_id"),
            "from_chat_id": data.get("from_chat_id", "@Shajare1"),
            "type": data.get("type", "forward"),
            "title_fa": data.get("title_fa"),
            "title_en": data.get("title_en"),
            "album_id": data.get("album_id"),
            "album_name": data.get("album_name"),
            "level": data.get("level"),
            "raw_caption": data.get("raw_caption"),
            "content": data.get("content")
        }
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return row["id"] if row else 0

    def get_track_by_message_id(self, message_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM tracks WHERE message_id = ? LIMIT 1;"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (message_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_tracks_by_album(self, album_id: str) -> List[Dict[str, Any]]:
        query = "SELECT * FROM tracks WHERE album_id = ? ORDER BY id ASC;"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (album_id,))
            return [dict(r) for r in cursor.fetchall()]

    def get_tracks_by_level(self, level: int) -> List[Dict[str, Any]]:
        query = "SELECT * FROM tracks WHERE level = ? ORDER BY id ASC;"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (level,))
            return [dict(r) for r in cursor.fetchall()]

    def get_all_tracks(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM tracks ORDER BY id ASC;"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query)
            return [dict(r) for r in cursor.fetchall()]

    def get_random_track(self, album_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if album_id:
            query = "SELECT * FROM tracks WHERE album_id = ? ORDER BY RANDOM() LIMIT 1;"
            params = (album_id,)
        else:
            query = "SELECT * FROM tracks ORDER BY RANDOM() LIMIT 1;"
            params = ()
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def search_tracks(self, raw_query: str, limit: int = 10) -> List[Dict[str, Any]]:
        normalized = normalize_for_search(raw_query)
        if not normalized:
            return []

        # Sanitize query for FTS5 syntax
        # Remove characters that cause FTS5 syntax errors: quotes, asterisks, brackets, colons
        clean_terms = re.findall(r'[\w\u0600-\u06FF]+', normalized)
        if not clean_terms:
            return []

        fts_query = " ".join(f'"{term}"*' for term in clean_terms)

        results = []
        seen_ids = set()

        # Step 1: Full-Text Search (FTS5)
        try:
            sql = """
            SELECT t.*
            FROM tracks t
            JOIN tracks_fts f ON t.id = f.rowid
            WHERE tracks_fts MATCH ?
            ORDER BY rank
            LIMIT ?;
            """
            with self.db.get_connection() as conn:
                cursor = conn.execute(sql, (fts_query, limit))
                for row in cursor.fetchall():
                    item = dict(row)
                    results.append(item)
                    seen_ids.add(item["message_id"])
        except Exception as e:
            logger.warning("FTS search encountered error: %s, falling back to substring/fuzzy", e)

        # Step 2: Fallback / complement with fuzzy matching if fewer than limit results
        if len(results) < limit:
            all_tracks = self.get_all_tracks()
            scored = []
            for t in all_tracks:
                if t["message_id"] in seen_ids:
                    continue
                # Score against title_fa, title_en, album_name, raw_caption
                candidates = [
                    t.get("title_fa") or "",
                    t.get("title_en") or "",
                    t.get("album_name") or "",
                    t.get("raw_caption") or ""
                ]
                max_score = max((fuzzy_match_score(normalized, c) for c in candidates), default=0.0)
                if max_score >= 60.0:
                    scored.append((max_score, t))

            scored.sort(key=lambda x: x[0], reverse=True)
            for _, track in scored[:limit - len(results)]:
                results.append(track)
                seen_ids.add(track["message_id"])

        return results

    def get_stats(self) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            total_tracks = conn.execute("SELECT COUNT(*) FROM tracks;").fetchone()[0]
            total_albums = conn.execute("SELECT COUNT(DISTINCT album_id) FROM tracks WHERE album_id IS NOT NULL;").fetchone()[0]
            
            levels_cursor = conn.execute("SELECT level, COUNT(*) FROM tracks WHERE level IS NOT NULL GROUP BY level ORDER BY level;")
            level_counts = {f"level_{row[0]}": row[1] for row in levels_cursor.fetchall()}

        size_kb = 0
        if os.path.exists(self.db.db_path):
            size_kb = round(os.path.getsize(self.db.db_path) / 1024, 2)

        return {
            "total_tracks": total_tracks,
            "total_albums": total_albums,
            "levels": level_counts,
            "db_size_kb": size_kb
        }
