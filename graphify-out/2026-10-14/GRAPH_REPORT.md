# Graph Report - radius-chatops  (2026-10-14)

## Corpus Check
- 17 files · ~7,886 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .example 1)

## Summary
- 138 nodes · 422 edges · 14 communities (8 shown, 6 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `de42d395`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- error_embed
- Radius Discord Bot (Radius-ChatOps)
- group_commands.py
- DatabaseError
- db.py
- info_embed
- admin_commands.py
- AGENTS.md
- success_embed
- fetch

## God Nodes (most connected - your core abstractions)
1. `fetch()` - 37 edges
2. `error_embed()` - 36 edges
3. `warning_embed()` - 24 edges
4. `success_embed()` - 23 edges
5. `execute()` - 20 edges
6. `info_embed()` - 19 edges
7. `UserNotFound` - 18 edges
8. `DatabaseError` - 17 edges
9. `NasCommands` - 14 edges
10. `GroupCommands` - 13 edges

## Surprising Connections (you probably didn't know these)
- `AttributeCommands` --uses--> `DatabaseError`  [INFERRED]
  cogs/attribute_commands.py → utils/exceptions.py
- `GroupCommands` --uses--> `DatabaseError`  [INFERRED]
  cogs/group_commands.py → utils/exceptions.py
- `NasCommands` --uses--> `DatabaseError`  [INFERRED]
  cogs/nas_commands.py → utils/exceptions.py
- `NasCommands` --uses--> `UserNotFound`  [INFERRED]
  cogs/nas_commands.py → utils/exceptions.py
- `StatsCommands` --uses--> `DatabaseError`  [INFERRED]
  cogs/stats_commands.py → utils/exceptions.py

## Import Cycles
- None detected.

## Communities (14 total, 6 thin omitted)

### Community 0 - "error_embed"
Cohesion: 0.34
Nodes (4): NasCommands, setup(), error_embed(), warning_embed()

### Community 1 - "Radius Discord Bot (Radius-ChatOps)"
Cohesion: 0.11
Nodes (17): 1. 👤 User Management (`cogs/user_commands.py`), 2. 👥 Group & Profile Management (`cogs/group_commands.py`), 3. 🌐 NAS Device Management (`cogs/nas_commands.py`), 4. 📊 Statistics & Accounting (`cogs/stats_commands.py`), 5. 🔍 Attribute Inspection (`cogs/attribute_commands.py`), 6. ⚙️ Bot Administration & Utility (`cogs/admin_commands.py` & `main.py`), 📐 Arsitektur Sistem, Cara 1: Menggunakan Virtual Environment (Lokal) (+9 more)

### Community 2 - "group_commands.py"
Cohesion: 0.26
Nodes (9): _parse_nas_ips(), setup(), attribute_autocomplete(), group_nas_ip_autocomplete(), groupname_autocomplete(), nas_ip_autocomplete(), nasname_autocomplete(), operator_autocomplete() (+1 more)

### Community 3 - "DatabaseError"
Cohesion: 0.27
Nodes (9): setup(), UserCommands, DatabaseError, DuplicateUser, GroupNotFound, NASNotFound, OperationError, PoolNotInitialized (+1 more)

### Community 4 - "db.py"
Cohesion: 0.19
Nodes (7): close_db(), init_db(), load_cogs(), main(), on_ready(), ping(), main()

### Community 5 - "info_embed"
Cohesion: 0.19
Nodes (8): AttributeCommands, setup(), setup(), StatsCommands, create_embed(), info_embed(), ResponseType, UserNotFound

### Community 6 - "admin_commands.py"
Cohesion: 0.25
Nodes (3): AdminCommands, cog_autocomplete(), setup()

### Community 11 - "success_embed"
Cohesion: 0.38
Nodes (3): GroupCommands, execute(), success_embed()

## Knowledge Gaps
- **15 isolated node(s):** `graphify`, `📐 Arsitektur Sistem`, `1. 👤 User Management (`cogs/user_commands.py`)`, `2. 👥 Group & Profile Management (`cogs/group_commands.py`)`, `3. 🌐 NAS Device Management (`cogs/nas_commands.py`)` (+10 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 36 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch()` connect `fetch` to `error_embed`, `group_commands.py`, `db.py`, `info_embed`, `success_embed`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `error_embed()` connect `error_embed` to `group_commands.py`, `info_embed`, `admin_commands.py`, `success_embed`, `fetch`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `DatabaseError` connect `DatabaseError` to `error_embed`, `group_commands.py`, `success_embed`, `info_embed`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **What connects `graphify`, `📐 Arsitektur Sistem`, `1. 👤 User Management (`cogs/user_commands.py`)` to the rest of the system?**
  _15 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Radius Discord Bot (Radius-ChatOps)` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._