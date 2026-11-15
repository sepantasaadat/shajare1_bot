# Graph Report - shajare1_bot  (2026-11-15)

## Corpus Check
- 5 files · ~6,151 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .service 1)

## Summary
- 31 nodes · 54 edges · 5 communities (2 shown, 3 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `42ab1e67`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- telegram_bot_shajare.py
- handle_search_message
- button_callback
- Review Focus
- main

## God Nodes (most connected - your core abstractions)
1. `button_callback()` - 11 edges
2. `handle_search_message()` - 8 edges
3. `Review Focus` - 7 edges
4. `send_post()` - 6 edges
5. `main()` - 6 edges
6. `start_command()` - 5 edges
7. `load_posts()` - 3 edges
8. `make_main_menu_keyboard()` - 3 edges
9. `Task 4: Error Sanitization, Logging, and Fail-Fast Startup (SEC-05, SEC-07, SEC-08)` - 3 edges
10. `Security Audit Remediation Implementation Plan` - 3 edges

## Surprising Connections (you probably didn't know these)
- `Task 3: Concurrency Control & Forwarding Abuse Prevention (SEC-04)` --references--> `button_callback()`  [INFERRED]
  docs/superpowers/plans/2026-11-15-security-remediation.md → telegram_bot_shajare.py
- `Task 2: Input Sanitization & HTML Entity Escaping (SEC-03)` --references--> `handle_search_message()`  [INFERRED]
  docs/superpowers/plans/2026-11-15-security-remediation.md → telegram_bot_shajare.py
- `Task 4: Error Sanitization, Logging, and Fail-Fast Startup (SEC-05, SEC-07, SEC-08)` --references--> `send_post()`  [INFERRED]
  docs/superpowers/plans/2026-11-15-security-remediation.md → telegram_bot_shajare.py
- `Task 4: Error Sanitization, Logging, and Fail-Fast Startup (SEC-05, SEC-07, SEC-08)` --references--> `main()`  [INFERRED]
  docs/superpowers/plans/2026-11-15-security-remediation.md → telegram_bot_shajare.py

## Import Cycles
- None detected.

## Communities (5 total, 3 thin omitted)

### Community 2 - "button_callback"
Cohesion: 0.33
Nodes (5): button_callback(), make_albums_keyboard(), make_levels_keyboard(), make_main_menu_keyboard(), start_command()

### Community 3 - "Review Focus"
Cohesion: 0.22
Nodes (8): Global Constraints, Review Focus, Security Audit Remediation Implementation Plan, Task 1: Pinned Dependency Manifest (`requirements.txt`) (SEC-06), Task 2: Input Sanitization & HTML Entity Escaping (SEC-03), Task 3: Concurrency Control & Forwarding Abuse Prevention (SEC-04), Task 5: Hardened Systemd Service Template (SEC-02), Task 6: Graphify & Git Remote Push

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Review Focus` connect `Review Focus` to `main`?**
  _High betweenness centrality (0.366) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `button_callback()` (e.g. with `Task 3: Concurrency Control & Forwarding Abuse Prevention (SEC-04)` and `main()`) actually correct?**
  _`button_callback()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Why does `button_callback()` connect `button_callback` to `telegram_bot_shajare.py`, `handle_search_message`, `Review Focus`, `main`?**
  _High betweenness centrality (0.215) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `handle_search_message()` (e.g. with `Task 2: Input Sanitization & HTML Entity Escaping (SEC-03)` and `main()`) actually correct?**
  _`handle_search_message()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Why does `handle_search_message()` connect `handle_search_message` to `telegram_bot_shajare.py`, `button_callback`, `Review Focus`, `main`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `main()` (e.g. with `Task 4: Error Sanitization, Logging, and Fail-Fast Startup (SEC-05, SEC-07, SEC-08)` and `button_callback()`) actually correct?**
  _`main()` has 4 INFERRED edges - model-reasoned connections that need verification._