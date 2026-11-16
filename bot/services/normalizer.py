import re
from typing import Optional

try:
    from rapidfuzz import fuzz
except ImportError:
    fuzz = None  # Fallback if rapidfuzz not present

ARABIC_TO_PERSIAN = {
    '\u064a': '\u06cc',  # Arabic yeh -> Persian yeh
    '\u0649': '\u06cc',  # Alef maksura -> Persian yeh
    '\u0643': '\u06a9',  # Arabic kaf -> Persian kaf
    '\u0629': '\u0647',  # Teh marbuta -> heh
    '\u06c0': '\u0647',  # Heh with yeh above -> heh
    '\u0624': '\u0648',  # Waw with hamza -> waw
    '\u0626': '\u06cc',  # Yeh with hamza -> yeh
    '\u0625': '\u0627',  # Alef with hamza below -> alef
    '\u0623': '\u0627',  # Alef with hamza above -> alef
}

DIACRITICS_PATTERN = re.compile(r'[\u064b-\u065f\u0670]')  # Fatha, kasra, damma, tanwin, sukun, shadda, etc.

PERSIAN_NUMBERS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_NUMBERS = "٠١٢٣٤٥٦٧٨٩"
ENGLISH_NUMBERS = "0123456789"
DIGIT_MAP = str.maketrans(PERSIAN_NUMBERS + ARABIC_NUMBERS, ENGLISH_NUMBERS * 2)

def normalize_persian(text: Optional[str]) -> str:
    """
    Standardize Persian text:
    - Unifies Arabic characters (yeh, kaf, etc.) to standard Persian
    - Strips Arabic tashkeel / diacritics
    - Normalizes zero-width non-joiners (ZWNJ) and collapses redundant whitespace
    - Translates Persian/Arabic numerals to standard digits
    """
    if not text:
        return ""

    # Replace Arabic glyphs
    res = text
    for ar_char, fa_char in ARABIC_TO_PERSIAN.items():
        res = res.replace(ar_char, fa_char)

    # Strip diacritics
    res = DIACRITICS_PATTERN.sub('', res)

    # Convert digits
    res = res.translate(DIGIT_MAP)

    # Clean zero-width non-joiners (\u200c)
    res = re.sub(r'[\u200c\u200d\u200e\u200f]+', '\u200c', res)
    res = re.sub(r'\s*\u200c\s*', '\u200c', res)

    # Collapse multiple whitespaces
    res = re.sub(r'[ \t\r\f\v]+', ' ', res)
    return res.strip()

def normalize_for_search(text: Optional[str]) -> str:
    """
    More aggressive normalization tailored for search queries:
    - Applies base Persian normalization
    - Folds 'آ' to 'ا' so searches match regardless of alif variant
    - Replaces ZWNJ with space so compound words match separate words
    - Converts English characters to lowercase
    """
    if not text:
        return ""

    res = normalize_persian(text).lower()
    # Fold Alef with madda ('آ') to bare Alef ('ا')
    res = res.replace('\u0622', '\u0627')
    # Replace ZWNJ with a space for indexing/tokenization
    res = res.replace('\u200c', ' ')
    # Re-collapse whitespace
    res = re.sub(r'\s+', ' ', res)
    return res.strip()

def fuzzy_match_score(query: str, target: str) -> float:
    """
    Calculate fuzzy similarity score (0.0 to 100.0) between query and target.
    """
    if not query or not target:
        return 0.0
    q = normalize_for_search(query)
    t = normalize_for_search(target)
    if fuzz:
        return float(max(fuzz.partial_ratio(q, t), fuzz.token_set_ratio(q, t)))
    # Fallback substring check if rapidfuzz is unavailable
    if q in t:
        return 100.0
    return 0.0
