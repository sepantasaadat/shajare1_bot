# Shajare Telegram Bot Modular Architecture & Feature Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `telegram_bot_shajare.py` and `posts.json` into a modular, production-ready Python package (`bot/`) backed by an SQLite database (`shajare.db`) with FTS5 search, Persian NLP normalization, album tracklist navigation, inline query sharing, deduplicated "فال همایونی", and admin controls while maintaining 100% backward compatibility.

**Architecture:**
- Clean separation of concerns: `bot/config.py`, `bot/database/` (SQLite + FTS5), `bot/services/` (normalizer & forwarder), `bot/keyboards/`, and `bot/handlers/`.
- Root entry point `telegram_bot_shajare.py` delegates directly to `bot.main:main()`, ensuring compatibility with the existing `shajare_bot.service` systemd unit on the VPS.
- Data migration pipeline converts `posts.json` into `shajare.db` while keeping `posts.json` intact as an immutable reference backup.

**Tech Stack:** Python 3.13, `python-telegram-bot` 22.5+, SQLite3 (with FTS5), `rapidfuzz` 3.14+, `httpx` 0.28+.

**Spec:** Execution roadmap established from deep codebase audit (Proposals 1-7).

## Global Constraints
- Version floors: Python >= 3.11, python-telegram-bot >= 22.5.
- All database operations must handle SQLite concurrent access gracefully (WAL mode, timeouts).
- HTML entity escaping is mandatory for all user-supplied text delivered in Telegram messages with `ParseMode.HTML`.
- Concurrency locks (`is_forwarding`) must prevent flooding when forwarding batches.
- Forwarder must implement exponential backoff for `telegram.error.RetryAfter`.
- Root entry point `telegram_bot_shajare.py` must remain functional with no broken imports.

## Review Focus
1. Persian NLP Normalization: Search queries with Arabic `ي/ك`, diacritics, or ZWNJ variations must find corresponding Persian records.
2. Single-Track Delivery vs. Bulk: Choosing an album must show a paginated tracklist allowing single-track forward, avoiding the flood of 15+ messages unless the user explicitly chooses bulk.
3. Concurrency Lock Safety: Re-entrant or concurrent clicks while forwarding must be safely rejected with an alert rather than deadlocking.
4. Inline Query Results: Telegram inline queries (`@ShajareBot query`) must return valid `InlineQueryResultArticle` items that forward or link the requested track without crashing.
5. Admin Authorization: `/stats` and `/reload` commands must silently ignore or politely reject unauthorized user IDs.

---

### Task 1: Persian NLP Normalizer Service

**Files:**
- Create: `bot/__init__.py`
- Create: `bot/services/__init__.py`
- Create: `bot/services/normalizer.py`
- Test: `tests/test_normalizer.py`

- [ ] **Step 1: Write failing test for Persian normalizer**
  Test Arabic letter conversion (`ي -> ی`, `ك -> ک`, `ة -> ه`), diacritic stripping (`َ ُ ِ ً ٍ ٌ ّ ْ`), ZWNJ normalization (`\u200c`), space collapsing, and case folding.
- [ ] **Step 2: Run test to verify failure**
  Run `py -3.13 -m unittest tests/test_normalizer.py`.
- [ ] **Step 3: Implement `bot/services/normalizer.py`**
  Provide `normalize_persian(text: str) -> str` and `fuzzy_match_score(query: str, target: str) -> float`.
- [ ] **Step 4: Run tests to verify pass**
  Verify all normalization cases pass cleanly.
- [ ] **Step 5: Commit changes**
  `git commit -m "feat(nlp): implement Persian text normalizer for search and matching"`

---

### Task 2: SQLite Database Schema & Migration Pipeline

**Files:**
- Create: `bot/database/__init__.py`
- Create: `bot/database/db.py`
- Create: `bot/database/repository.py`
- Create: `scripts/migrate_posts.py`
- Test: `tests/test_database_and_migration.py`

- [ ] **Step 1: Write failing test for DB schema, repository, and migration**
  Test table creation, track insertion, FTS5 virtual table trigger synchronization, search querying, level filtering, and migration from a test JSON dictionary.
- [ ] **Step 2: Run test to verify failure**
  Run `py -3.13 -m unittest tests/test_database_and_migration.py`.
- [ ] **Step 3: Implement `bot/database/db.py` and `bot/database/repository.py`**
  Setup SQLite schema with `tracks` table, `tracks_fts` FTS5 table, WAL mode, indices, and CRUD/search queries.
- [ ] **Step 4: Implement `scripts/migrate_posts.py`**
  Read `posts.json`, extract clean `title_fa`, `title_en`, `album_name`, `album_id`, `level`, and write rows to `shajare.db`.
- [ ] **Step 5: Run tests and execute migration on production `posts.json`**
  Run tests, then execute `py -3.13 scripts/migrate_posts.py` to create `shajare.db`. Verify 223 tracks migrated.
- [ ] **Step 6: Commit changes**
  `git commit -m "feat(db): implement SQLite FTS5 database layer and posts migration pipeline"`

---

### Task 3: Safe Message Forwarder & Modern Keyboards

**Files:**
- Create: `bot/services/forwarder.py`
- Create: `bot/keyboards/__init__.py`
- Create: `bot/keyboards/menus.py`
- Test: `tests/test_keyboards.py`

- [ ] **Step 1: Write failing test for keyboard layouts**
  Test generation of main menu, album menu, level menu, paginated tracklist menu, and fal menu.
- [ ] **Step 2: Run test to verify failure**
  Run `py -3.13 -m unittest tests/test_keyboards.py`.
- [ ] **Step 3: Implement `bot/services/forwarder.py`**
  Safe forwarding with `telegram.error.RetryAfter` exponential backoff, rate pacing, and error containment.
- [ ] **Step 4: Implement `bot/keyboards/menus.py`**
  Construct inline keyboards with pagination support (`make_tracklist_keyboard(items, page, total_pages, category)`), albums list, levels list, and main menu.
- [ ] **Step 5: Run tests to verify pass**
  Verify keyboard structures and callbacks.
- [ ] **Step 6: Commit changes**
  `git commit -m "feat(ui): implement safe forwarder and interactive paginated keyboards"`

---

### Task 4: Command & Event Handlers

**Files:**
- Create: `bot/handlers/__init__.py`
- Create: `bot/handlers/start.py`
- Create: `bot/handlers/navigation.py`
- Create: `bot/handlers/search.py`
- Create: `bot/handlers/fal.py`
- Create: `bot/handlers/admin.py`
- Test: `tests/test_handlers.py`

- [ ] **Step 1: Write unit tests for handler logic and permissions**
  Test deep link parsing (`/start track_726`), admin authorization decorator, search query resolution, and fal response generation.
- [ ] **Step 2: Run test to verify failure**
  Run `py -3.13 -m unittest tests/test_handlers.py`.
- [ ] **Step 3: Implement `bot/handlers/start.py`**
  `/start` command with deep-linking support for direct track delivery.
- [ ] **Step 4: Implement `bot/handlers/navigation.py`**
  Callbacks for levels, albums, pagination, single-track forward, and bulk delivery with locks.
- [ ] **Step 5: Implement `bot/handlers/search.py`**
  Private chat keyword search (FTS5 + fuzzy fallback) and `InlineQueryHandler` for sharing tracks in groups.
- [ ] **Step 6: Implement `bot/handlers/fal.py`**
  Deduplicated random track picker with curated Persian poetic bayts and re-roll button.
- [ ] **Step 7: Implement `bot/handlers/admin.py`**
  Admin-only `/stats` and `/reload` commands.
- [ ] **Step 8: Run handler unit tests to verify pass**
- [ ] **Step 9: Commit changes**
  `git commit -m "feat(handlers): add modular handlers for navigation, search, inline query, fal, and admin"`

---

### Task 5: App Configuration, Entry Point & System Integration

**Files:**
- Create: `bot/config.py`
- Create: `bot/main.py`
- Modify: `telegram_bot_shajare.py`
- Test: `tests/test_entrypoint.py`

- [ ] **Step 1: Implement `bot/config.py`**
  Configuration loader for `BOT_TOKEN`, `ADMIN_USER_IDS`, `DB_PATH`, `POSTS_PATH`, and channel constants.
- [ ] **Step 2: Implement `bot/main.py`**
  Application factory and runner: builds `Application`, registers all handlers, handles lifecycle.
- [ ] **Step 3: Wire root entry point `telegram_bot_shajare.py`**
  Refactor `telegram_bot_shajare.py` to import and call `bot.main:main()`, keeping backwards compatibility with `shajare_bot.service`.
- [ ] **Step 4: Write and run entry point tests**
  Verify module imports, configuration validation, and handler registration without starting network polling.
- [ ] **Step 5: Commit changes**
  `git commit -m "refactor(core): wire root entry point to modular bot package"`

---

### Task 6: Verification, Full Suite Test & Documentation

**Files:**
- Modify: `README.md` (or deployment guide)
- Remove: temporary scratch files

- [ ] **Step 1: Run complete test suite**
  Execute `py -3.13 -m unittest discover tests`.
- [ ] **Step 2: Update graphify knowledge graph**
  Execute `graphify update .`.
- [ ] **Step 3: Final check and git push**
  Verify `git status`, commit any remaining items, and push to GitHub.
