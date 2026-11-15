# Security Audit Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remediate all code, configuration, dependency, and input-handling security vulnerabilities identified in the authorized security audit for `shajare1_bot`.

**Architecture:** 
1. Harden `telegram_bot_shajare.py` with HTML escaping via `html.escape`, per-user async forwarding concurrency locking (`is_forwarding`), sanitized user-facing exception messages, fail-fast token validation, and structured standard logging.
2. Pin dependencies in a newly created `requirements.txt`.
3. Provide a hardened production `shajare_bot.service` unit file template with unprivileged user configuration and systemd sandboxing.
4. Provide instructions and verification for token revocation on Telegram BotFather and Git history remediation.

**Tech Stack:** Python 3.10+, `python-telegram-bot` (v22.5), standard `logging`, standard `html`, systemd.

**Spec:** Security Audit Report findings SEC-01 through SEC-08.

## Global Constraints

- Never commit secrets or unredacted tokens into code or configuration.
- Preserve existing Persian copywriting, musical theme, and inline keyboard layouts.
- Keep all dependencies strictly isolated within the project virtual environment.
- Run `graphify update .` to keep the knowledge graph synchronized after code modifications.

## Review Focus

1. Search input containing `<script>`, `a & b`, `<test>` must not trigger Telegram entity parsing errors.
2. Concurrent clicks on level buttons by the same user must be blocked with an alert while a batch is in flight.
3. Errors during post forwarding must not expose internal Python stack traces or exception strings to chat users.
4. Missing `BOT_TOKEN` on startup must fail fast with `SystemExit`.
5. Pinned `requirements.txt` must match versions verified in the environment.

---

### Task 1: Pinned Dependency Manifest (`requirements.txt`) (SEC-06)

**Files:**
- Create: `requirements.txt`

**Interfaces:**
- Produces: Deterministic package list for CI/scanners and VPS deployment.

- [ ] **Step 1: Create `requirements.txt` with pinned dependencies**
```text
python-telegram-bot==22.5
httpx==0.28.1
httpcore==1.0.9
anyio==4.11.0
certifi==2025.11.12
```

- [ ] **Step 2: Verify dependency installation dry-run**
Run: `py -3.13 -m pip install -r requirements.txt --dry-run`
Expected: Successfully validated requirements without conflicts.

- [ ] **Step 3: Commit**
```bash
git add requirements.txt
git commit -m "security: add pinned requirements.txt manifest (SEC-06)"
```

---

### Task 2: Input Sanitization & HTML Entity Escaping (SEC-03)

**Files:**
- Modify: `telegram_bot_shajare.py`

**Interfaces:**
- Consumes: `user_text` from `update.message.text`
- Produces: Sanitized HTML strings using `html.escape`

- [ ] **Step 1: Import `html` standard library module**
Add `import html` to imports in `telegram_bot_shajare.py`.

- [ ] **Step 2: Escape user search queries before HTML interpolation**
In `handle_search_message`:
Escape `user_text.strip()` before formatting in:
- `f"🔍 در حال جستجو برای: «<b>{escaped_text}</b>»..."`
- `f"❌ متاسفانه اثری مطابق با «<b>{escaped_text}</b>» یافت نشد.\nمی‌توانید کلمه دیگری را جستجو کنید."`

- [ ] **Step 3: Verify with Python compilation and entity test**
Run: `py -3.13 -m py_compile telegram_bot_shajare.py`
Expected: Exit code 0.

- [ ] **Step 4: Commit**
```bash
git add telegram_bot_shajare.py
git commit -m "security: escape user inputs in HTML messages to prevent entity parsing DoS (SEC-03)"
```

---

### Task 3: Concurrency Control & Forwarding Abuse Prevention (SEC-04)

**Files:**
- Modify: `telegram_bot_shajare.py`

**Interfaces:**
- Consumes: `context.user_data`
- Produces: Mutex lock on `is_forwarding` per chat/user

- [ ] **Step 1: Implement `is_forwarding` guard in `button_callback`**
Before entering the bulk forwarding loop for levels or albums:
```python
if context.user_data.get('is_forwarding'):
    await query.answer("لطفاً تا پایان ارسال آثار قبلی صبور باشید.", show_alert=True)
    return
```

- [ ] **Step 2: Wrap forwarding loop in try...finally block**
```python
context.user_data['is_forwarding'] = True
try:
    for i, p in enumerate(level_posts):
        await send_post(query.message.chat_id, p, context)
        if (i + 1) % 20 == 0:
            await asyncio.sleep(3)
        else:
            await asyncio.sleep(1.0)
finally:
    context.user_data['is_forwarding'] = False
```

- [ ] **Step 3: Verify syntax and logic**
Run: `py -3.13 -m py_compile telegram_bot_shajare.py`
Expected: Exit code 0.

- [ ] **Step 4: Commit**
```bash
git add telegram_bot_shajare.py
git commit -m "security: add per-user concurrency lock to prevent forward flooding (SEC-04)"
```

---

### Task 4: Error Sanitization, Logging, and Fail-Fast Startup (SEC-05, SEC-07, SEC-08)

**Files:**
- Modify: `telegram_bot_shajare.py`

**Interfaces:**
- Produces: Standard logger `logger = logging.getLogger("shajare_bot")`, sanitized user errors, fail-fast `SystemExit`

- [ ] **Step 1: Configure standard Python logging**
Add standard logging configuration at top of `telegram_bot_shajare.py`:
```python
import logging

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("shajare_bot")
```

- [ ] **Step 2: Sanitize exception handling in `send_post`**
Replace raw `f"خطا در ارسال پیام: {e}"` with internal log and generic Persian message:
```python
except Exception as e:
    logger.error("Error forwarding post to chat %s: %s", chat_id, e, exc_info=True)
    await context.bot.send_message(
        chat_id,
        text="متأسفانه در ارسال این اثر خطایی رخ داد. لطفاً لحظاتی دیگر تلاش فرمایید."
    )
    return
```

- [ ] **Step 3: Fail fast when `BOT_TOKEN` is missing in `main()`**
In `main()`:
```python
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN environment variable is missing. Terminating.")
    raise SystemExit("CRITICAL: BOT_TOKEN environment variable is not set. Exiting.")
```

- [ ] **Step 4: Verify syntax and compile**
Run: `py -3.13 -m py_compile telegram_bot_shajare.py`
Expected: Exit code 0.

- [ ] **Step 5: Commit**
```bash
git add telegram_bot_shajare.py
git commit -m "security: sanitize error output, add structured logging, and fail fast on missing token (SEC-05, SEC-07, SEC-08)"
```

---

### Task 5: Hardened Systemd Service Template (SEC-02)

**Files:**
- Create: `shajare_bot.service`

**Interfaces:**
- Produces: Reference hardened systemd service file with unprivileged user and sandboxing directives.

- [ ] **Step 1: Create hardened `shajare_bot.service`**
```ini
[Unit]
Description=Shajare Telegram Bot Service
After=network.target

[Service]
Type=simple
User=shajare
Group=shajare
WorkingDirectory=/opt/shajare1_bot
EnvironmentFile=/etc/default/shajare_bot
ExecStart=/opt/shajare1_bot/venv/bin/python /opt/shajare1_bot/telegram_bot_shajare.py
Restart=always
RestartSec=5

# Systemd Security & Sandboxing
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
ProtectKernelTunables=true
ProtectControlGroups=true
ReadWritePaths=/opt/shajare1_bot

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 2: Commit**
```bash
git add shajare_bot.service
git commit -m "security: provide hardened systemd service unit template (SEC-02)"
```

---

### Task 6: Graphify & Git Remote Push

**Files:**
- Modify: `graphify-out/` (via `graphify update .`)

**Interfaces:**
- Produces: Synchronized knowledge graph and remote push to GitHub.

- [ ] **Step 1: Update Graphify knowledge graph**
Run: `& "C:\Users\PC Ishragh\AppData\Local\Programs\Python\Python313\Scripts\graphify.exe" update .`
Expected: Knowledge graph refreshed with all AST updates.

- [ ] **Step 2: Push changes to GitHub**
Run: `git push origin main`
Expected: Commits pushed to `origin/main`.
