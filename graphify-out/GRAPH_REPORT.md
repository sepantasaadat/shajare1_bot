# Graph Report - shajare1_bot  (2026-11-10)

## Corpus Check
- 4 files · ~5,066 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 19 nodes · 38 edges · 4 communities (1 shown, 3 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `71308884`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- telegram_bot_shajare.py
- handle_search_message
- button_callback
- start_command

## God Nodes (most connected - your core abstractions)
1. `button_callback()` - 10 edges
2. `handle_search_message()` - 6 edges
3. `send_post()` - 5 edges
4. `start_command()` - 5 edges
5. `main()` - 5 edges
6. `load_posts()` - 3 edges
7. `make_main_menu_keyboard()` - 3 edges
8. `make_levels_keyboard()` - 2 edges
9. `make_albums_keyboard()` - 2 edges

## Surprising Connections (you probably didn't know these)
- `main()` --indirect_call--> `start_command()`  [INFERRED]
  telegram_bot_shajare.py → telegram_bot_shajare.py  _Bridges community 3 → community 0_
- `main()` --indirect_call--> `button_callback()`  [INFERRED]
  telegram_bot_shajare.py → telegram_bot_shajare.py  _Bridges community 2 → community 0_
- `main()` --indirect_call--> `handle_search_message()`  [INFERRED]
  telegram_bot_shajare.py → telegram_bot_shajare.py  _Bridges community 1 → community 0_
- `button_callback()` --calls--> `send_post()`  [EXTRACTED]
  telegram_bot_shajare.py → telegram_bot_shajare.py  _Bridges community 1 → community 2_
- `start_command()` --references--> `DEFAULT_TYPE`  [EXTRACTED]
  telegram_bot_shajare.py →   _Bridges community 1 → community 3_

## Import Cycles
- None detected.

## Communities (4 total, 3 thin omitted)

### Community 2 - "button_callback"
Cohesion: 0.50
Nodes (3): button_callback(), make_albums_keyboard(), make_levels_keyboard()

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `button_callback()` connect `button_callback` to `telegram_bot_shajare.py`, `handle_search_message`, `start_command`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `main()` (e.g. with `button_callback()` and `handle_search_message()`) actually correct?**
  _`main()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Why does `handle_search_message()` connect `handle_search_message` to `telegram_bot_shajare.py`, `start_command`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `start_command()` connect `start_command` to `telegram_bot_shajare.py`, `handle_search_message`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._