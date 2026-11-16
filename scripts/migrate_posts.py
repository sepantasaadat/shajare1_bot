import os
import sys
import json
import logging
from typing import Dict, Any

# Ensure project root is in sys.path when running as a script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.database.db import DatabaseManager
from bot.database.repository import TrackRepository
from bot.services.normalizer import normalize_persian

logger = logging.getLogger(__name__)

ALBUMS_MAP = {
    "alb_nasim_vasl": "نسیم وصل",
    "alb_ba_setareha": "با ستاره ها",
    "alb_naghsh_khial": "نقش خیال",
    "alb_nashakiba": "ناشکیبا",
    "alb_ghijak_koli": "قیژک کولی",
    "alb_khorshid_arezo": "خورشید آرزو",
    "alb_ab_nan_avaz": "آب نان آواز",
    "alb_simorgh": "سیمرغ",
    "alb_che_atash_ha": "چه آتش ها",
    "alb_na_fereshte": "نه فرشته ام نه شیطان",
    "alb_shab_jodayi": "شب جدایی",
    "alb_ey_jan_jan": "ای جان جان بی من مرو",
    "alb_mastor_mast": "مستور و مست",
    "alb_khodavandan_asrar": "خداوندان اسرار",
    "alb_rag_khab": "رگ خواب",
    "alb_shogh_doost": "شوق دوست",
    "alb_iran_man": "ایران من",
    "alb_afsane_cheshmhayat": "افسانه چشمهایت",
    "alb_gah_faramoshi": "گاه فراموشی",
    "alb_shin_mim_sin": "شین میم سین",
    "alb_emshab_kenar_ghazal": "امشب کنار غزل های من بخواب"
}

def parse_caption(caption: str, default_album_name: str = "") -> tuple[str, str, str]:
    """
    Parse captions like:
    'avaz nasim sahari, آواز نسیم سحری آلبوم نسیم وصل'
    'liberation moonlight introduction, آلبوم خداوند اسرار'
    Returns: (title_fa, title_en, album_name)
    """
    if not caption:
        return "", "", default_album_name

    title_en = ""
    remainder = caption.strip()

    if "," in remainder:
        parts = remainder.split(",", 1)
        title_en = parts[0].strip()
        remainder = parts[1].strip()

    album_name = default_album_name
    title_fa = ""

    if "آلبوم" in remainder:
        parts = remainder.split("آلبوم", 1)
        title_fa = normalize_persian(parts[0].strip())
        parsed_alb = normalize_persian(parts[1].strip())
        if parsed_alb:
            album_name = parsed_alb
    else:
        title_fa = normalize_persian(remainder)

    return title_fa, title_en, album_name

def run_migration(posts_path: str = "posts.json", db_path: str = "shajare.db") -> int:
    """
    Migrate posts from posts.json into SQLite database shajare.db.
    Returns total count of unique tracks migrated.
    """
    if not os.path.exists(posts_path):
        raise FileNotFoundError(f"Source file {posts_path} not found.")

    with open(posts_path, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)

    db_mgr = DatabaseManager(db_path)
    db_mgr.init_db()
    repo = TrackRepository(db_mgr)

    # Dictionary to aggregate track records by message_id
    tracks_by_msg_id: Dict[int, Dict[str, Any]] = {}

    # 1. Process album posts first (they carry titles, captions, and album mapping)
    for key, posts_list in data.items():
        if key.startswith("alb_"):
            alb_id = key
            alb_persian = ALBUMS_MAP.get(alb_id, "")
            for p in posts_list:
                msg_id = p.get("message_id")
                if not msg_id:
                    continue
                raw_caption = p.get("caption", "")
                title_fa, title_en, album_name = parse_caption(raw_caption, alb_persian)
                
                # If title_fa is empty (e.g. caption was just 'liberation moonlight introduction, آلبوم خداوند اسرار')
                if not title_fa and title_en:
                    title_fa = title_en

                tracks_by_msg_id[msg_id] = {
                    "message_id": msg_id,
                    "from_chat_id": p.get("from_chat_id", "@Shajare1"),
                    "type": p.get("type", "forward"),
                    "title_fa": title_fa,
                    "title_en": title_en,
                    "album_id": alb_id,
                    "album_name": album_name,
                    "level": None,
                    "raw_caption": raw_caption,
                    "content": p.get("content")
                }

    # 2. Process level posts (level1 to level5)
    for key, posts_list in data.items():
        if key.startswith("level"):
            try:
                lvl_num = int(key.replace("level", ""))
            except ValueError:
                lvl_num = None

            for p in posts_list:
                msg_id = p.get("message_id")
                if not msg_id:
                    continue
                if msg_id in tracks_by_msg_id:
                    tracks_by_msg_id[msg_id]["level"] = lvl_num
                else:
                    # Level-only track without album metadata
                    tracks_by_msg_id[msg_id] = {
                        "message_id": msg_id,
                        "from_chat_id": p.get("from_chat_id", "@Shajare1"),
                        "type": p.get("type", "forward"),
                        "title_fa": f"نغمه شماره {msg_id}",
                        "title_en": "",
                        "album_id": None,
                        "album_name": None,
                        "level": lvl_num,
                        "raw_caption": p.get("caption", ""),
                        "content": p.get("content")
                    }

    # 3. Insert / upsert all aggregated tracks into DB
    count = 0
    for track_data in tracks_by_msg_id.values():
        repo.upsert_track(track_data)
        count += 1

    logger.info("Successfully migrated %d tracks into %s", count, db_path)
    return count

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    migrated_count = run_migration("posts.json", "shajare.db")
    print(f"Migration completed: {migrated_count} unique tracks migrated into shajare.db.")
