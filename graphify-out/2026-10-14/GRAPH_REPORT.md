# Graph Report - radius-chatops  (2026-10-14)

## Corpus Check
- 19 files · ~7,892 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .example 1)

## Summary
- 157 nodes · 460 edges · 11 communities (7 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 28 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `de42d395`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- fetch
- Radius Discord Bot
- group_commands.py
- DatabaseError
- db.py
- UserNotFound
- admin_commands.py
- AGENTS.md

## God Nodes (most connected - your core abstractions)
1. `fetch()` - 37 edges
2. `error_embed()` - 36 edges
3. `warning_embed()` - 24 edges
4. `success_embed()` - 23 edges
5. `execute()` - 20 edges
6. `DatabaseError` - 20 edges
7. `UserNotFound` - 20 edges
8. `info_embed()` - 19 edges
9. `Radius Discord Bot` - 15 edges
10. `NasCommands` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Changelog` --references--> `UserNotFound`  [INFERRED]
  README.md → utils/exceptions.py
- `Exception Classes` --references--> `UserNotFound`  [INFERRED]
  README.md → utils/exceptions.py
- `Changelog` --references--> `RadiusException`  [INFERRED]
  README.md → utils/exceptions.py
- `Exception Classes` --references--> `RadiusException`  [INFERRED]
  README.md → utils/exceptions.py
- `Changelog` --references--> `DatabaseError`  [INFERRED]
  README.md → utils/exceptions.py

## Import Cycles
- None detected.

## Communities (11 total, 4 thin omitted)

### Community 0 - "fetch"
Cohesion: 0.22
Nodes (8): GroupCommands, NasCommands, setup(), execute(), fetch(), error_embed(), success_embed(), warning_embed()

### Community 1 - "Radius Discord Bot"
Cohesion: 0.07
Nodes (26): 1. Buat virtual environment, 2. Install dependency, 3. Siapkan file environment, 🔍 Autocomplete, 📊 Better Formatting, Catatan Keamanan, 🎨 Color-Coded Responses, Contoh Penggunaan (+18 more)

### Community 2 - "group_commands.py"
Cohesion: 0.22
Nodes (11): _parse_nas_ips(), setup(), attribute_autocomplete(), group_nas_ip_autocomplete(), groupname_autocomplete(), nas_ip_autocomplete(), nasname_autocomplete(), operator_autocomplete() (+3 more)

### Community 3 - "DatabaseError"
Cohesion: 0.23
Nodes (16): setup(), UserCommands, Changelog, Error Handling & Logging, Error Response Pattern, Exception Classes, Group Management, Logging Levels (+8 more)

### Community 4 - "db.py"
Cohesion: 0.19
Nodes (7): close_db(), init_db(), load_cogs(), main(), on_ready(), ping(), main()

### Community 5 - "UserNotFound"
Cohesion: 0.24
Nodes (6): AttributeCommands, setup(), setup(), StatsCommands, info_embed(), UserNotFound

### Community 6 - "admin_commands.py"
Cohesion: 0.25
Nodes (3): AdminCommands, cog_autocomplete(), setup()

## Knowledge Gaps
- **25 isolated node(s):** `graphify`, `Gambaran Umum`, `User Management`, `Monitoring & Analytics`, `Logging Levels` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 48 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Radius Discord Bot` connect `Radius Discord Bot` to `DatabaseError`?**
  _High betweenness centrality (0.285) - this node is a cross-community bridge._
- **Why does `Changelog` connect `DatabaseError` to `Radius Discord Bot`, `UserNotFound`?**
  _High betweenness centrality (0.257) - this node is a cross-community bridge._
- **Why does `DatabaseError` connect `DatabaseError` to `fetch`, `group_commands.py`, `UserNotFound`?**
  _High betweenness centrality (0.181) - this node is a cross-community bridge._
- **What connects `graphify`, `Gambaran Umum`, `User Management` to the rest of the system?**
  _25 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Radius Discord Bot` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._