# Logical Review and UX Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement comprehensive fixes for all 10 identified workflow flaws, dead ends, and UX friction points across `bot/keyboards/menus.py`, `bot/handlers/navigation.py`, `bot/handlers/search.py`, `bot/handlers/fal.py`, and `bot/handlers/start.py`.

**Architecture:**
- Search: Convert search results from forced bulk delivery into an interactive, paginated tracklist with single-play options and bulk option. Enable natural text querying in private chat.
- Navigation & Bulk Forwarding: Add cancellation mechanism (`[🛑 توقف ارسال]`) with `cancel_forwarding` flag, update stale loading message upon finish, and add toast notifications on single-track play.
- Cleanup: Automatically remove obsolete buttons in search prompts and Fal re-rolls to avoid message clutter.
- Resilience: Handle Telegram `BadRequest: Message is not modified` gracefully, and provide clear user feedback on invalid deep-links and page indicators (`noop`).

**Tech Stack:** Python 3.13, `python-telegram-bot` 22.5+, SQLite3 FTS5, `rapidfuzz`.

## Global Constraints
- Zero regressions in existing test suite.
- HTML entity escaping on all user text.
- Preserve backward compatibility for VPS deployment.

---

### Task 1: Keyboards & Search Results UI (Items 1, 4, 10)
**Files:**
- Modify: `bot/keyboards/menus.py`
- Test: `tests/test_keyboards.py`

- [ ] Add `make_search_results_keyboard(query_text, tracks, page, page_size)` with pagination and single-track buttons.
- [ ] Add `make_bulk_forwarding_keyboard()` with `[🛑 توقف ارسال]`.
- [ ] Update `test_keyboards.py` to test new keyboard structures.

---

### Task 2: Search Handler & Text Query Redirection (Items 1, 2, 3)
**Files:**
- Modify: `bot/handlers/search.py`
- Test: `tests/test_search_flow.py`

- [ ] Update `handle_search_message` to render interactive paginated results instead of auto-dumping.
- [ ] Support natural private chat text queries without requiring prior `search_guide` button click.
- [ ] Clean up orphan `search_prompt_msg_id` inline keyboard when search is executed.

---

### Task 3: Navigation, Bulk Cancellation & UX Polish (Items 4, 5, 8, 9, 10)
**Files:**
- Modify: `bot/handlers/navigation.py`
- Test: `tests/test_navigation_flow.py`

- [ ] Implement `stop_bulk_forwarding` callback to break the loop safely.
- [ ] Update original loading message to "تکمیل شد" or "متوقف شد" upon bulk exit.
- [ ] Add toast notification (`query.answer("🎧 در حال ارسال نغمه...", show_alert=False)`) for `play_`.
- [ ] Informative dialog on `noop` button with `show_alert=True`.
- [ ] Protect `edit_message_*` calls with `try...except telegram.error.BadRequest`.
- [ ] Add handlers for `search_page_<num>` and `bulk_search`.

---

### Task 4: Fal Clutter Prevention & Deep-Link Error Feedback (Items 6, 7)
**Files:**
- Modify: `bot/handlers/fal.py`
- Modify: `bot/handlers/start.py`
- Test: `tests/test_fal_and_start.py`

- [ ] In `fal.py`, remove previous reply markup before sending a new fortune on re-roll.
- [ ] In `start.py`, display clear error notification when deep link track is missing.

---

### Task 5: Full Project Verification & Regression Testing
**Files:**
- Run: `tests/`
- Run: `graphify update .`

- [ ] Run full test suite with `py -3.13 -m unittest discover tests`.
- [ ] Verify clean git state.
