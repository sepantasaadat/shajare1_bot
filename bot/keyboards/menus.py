import math
from typing import List, Dict, Any, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

ALBUMS_DATA = {
    "نسیم وصل": "alb_nasim_vasl",
    "با ستاره ها": "alb_ba_setareha",
    "نقش خیال": "alb_naghsh_khial",
    "ناشکیبا": "alb_nashakiba",
    "قیژک کولی": "alb_ghijak_koli",
    "خورشید آرزو": "alb_khorshid_arezo",
    "آب نان آواز": "alb_ab_nan_avaz",
    "سیمرغ": "alb_simorgh",
    "چه آتش ها": "alb_che_atash_ha",
    "نه فرشته ام نه شیطان": "alb_na_fereshte",
    "شب جدایی": "alb_shab_jodayi",
    "ای جان جان بی من مرو": "alb_ey_jan_jan",
    "مستور و مست": "alb_mastor_mast",
    "خداوندان اسرار": "alb_khodavandan_asrar",
    "رگ خواب": "alb_rag_khab",
    "شوق دوست": "alb_shogh_doost",
    "ایران من": "alb_iran_man",
    "افسانه چشمهایت": "alb_afsane_cheshmhayat",
    "گاه فراموشی": "alb_gah_faramoshi",
    "شین میم سین": "alb_shin_mim_sin",
    "امشب کنار غزل های من بخواب": "alb_emshab_kenar_ghazal"
}

def make_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🗂 سطوح آرشیو", callback_data="show_levels_menu"),
            InlineKeyboardButton("🎵 آلبوم‌ها", callback_data="show_albums_menu")
        ],
        [
            InlineKeyboardButton("🪶 فال همایونی (نغمه تصادفی)", callback_data="fale_homayouni")
        ],
        [
            InlineKeyboardButton("🔍 جستجوی اثر", callback_data="search_guide"),
            InlineKeyboardButton("📩 پیام به مدیریت", callback_data="contact_us")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def make_levels_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("▫️ سطح ۱", callback_data="level1"),
            InlineKeyboardButton("▫️ سطح ۲", callback_data="level2")
        ],
        [
            InlineKeyboardButton("▫️ سطح ۳", callback_data="level3"),
            InlineKeyboardButton("▫️ سطح ۴", callback_data="level4")
        ],
        [
            InlineKeyboardButton("▫️ سطح ۵", callback_data="level5")
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def make_albums_keyboard(albums_dict: Optional[Dict[str, str]] = None) -> InlineKeyboardMarkup:
    albums = albums_dict or ALBUMS_DATA
    keyboard = []
    row = []
    for persian_name, callback_id in albums.items():
        btn = InlineKeyboardButton(f"💿 {persian_name}", callback_data=callback_id)
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def make_tracklist_keyboard(
    category_prefix: str,
    tracks: List[Dict[str, Any]],
    page: int = 0,
    page_size: int = 6
) -> InlineKeyboardMarkup:
    """
    Paginated interactive track selector for an album or level.
    Users can pick an individual track or click bulk send.
    """
    total_tracks = len(tracks)
    total_pages = max(1, math.ceil(total_tracks / page_size))
    page = max(0, min(page, total_pages - 1))

    start_idx = page * page_size
    end_idx = min(start_idx + page_size, total_tracks)
    page_tracks = tracks[start_idx:end_idx]

    keyboard = []

    # Single track buttons
    for t in page_tracks:
        msg_id = t["message_id"]
        title = t.get("title_fa") or f"قطعه شماره {msg_id}"
        # Truncate title if excessively long for button
        if len(title) > 36:
            title = title[:33] + "..."
        keyboard.append([
            InlineKeyboardButton(f"▶️ {title}", callback_data=f"play_{msg_id}")
        ])

    # Bulk send button
    keyboard.append([
        InlineKeyboardButton("📦 ارسال یکجای تمام آثار این بخش", callback_data=f"bulk_{category_prefix}")
    ])

    # Pagination navigation
    if total_pages > 1:
        nav_row = []
        if page > 0:
            nav_row.append(
                InlineKeyboardButton("◀️ قبلی", callback_data=f"{category_prefix}_page_{page - 1}")
            )
        nav_row.append(
            InlineKeyboardButton(f"صفحه {page + 1} از {total_pages}", callback_data="noop")
        )
        if page < total_pages - 1:
            nav_row.append(
                InlineKeyboardButton("بعدی ▶️", callback_data=f"{category_prefix}_page_{page + 1}")
            )
        keyboard.append(nav_row)

    # Back button depending on category
    if category_prefix.startswith("alb_"):
        keyboard.append([InlineKeyboardButton("🎵 بازگشت به فهرست آلبوم‌ها", callback_data="show_albums_menu")])
    elif category_prefix.startswith("lvl_") or category_prefix.startswith("level"):
        keyboard.append([InlineKeyboardButton("🗂 بازگشت به فهرست سطوح", callback_data="show_levels_menu")])
    else:
        keyboard.append([InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")])

    return InlineKeyboardMarkup(keyboard)

def make_fal_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🪶 نغمه‌ای دیگر (تکرار فال)", callback_data="fale_homayouni")
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def make_cancel_search_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("❌ انصراف و بازگشت", callback_data="cancel_search")]
    ]
    return InlineKeyboardMarkup(keyboard)

def make_contact_keyboard(admin_url: str = "https://t.me/cheraghii1") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("💬 گفتگوی مستقیم در تلگرام", url=admin_url)],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def make_completion_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🗂 بازگشت به سطوح", callback_data="show_levels_menu"),
            InlineKeyboardButton("🎵 بازگشت به آلبوم‌ها", callback_data="show_albums_menu")
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
