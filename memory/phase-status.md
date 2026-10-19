---
name: phase-status
description: What is built, what has been run in Studio, and what is next, per phase. Code sessions read it first; rewrite the state, never append rounds.
metadata:
  type: project
---

**State (2026-10-19, first night sprint):** M0–M6 built in code and played in
Studio, plus §7 social and §8.2 events. The game still draws Luau blockouts:
the Haunted Manor monsters and hotel kit are built in Blender and staged, not
yet imported (WAITING §0). Save and load are NOT proven:
DataStore access is off (WAITING §3.1), so every playtest ran on a mock profile.

| Phase | Built | Run in Studio | Next |
|---|---|---|---|
| M0 setup | Data tables, Constants, Net (typed remotes + RateLimit), PlayerData (ProfileStore), 7 specs | Specs 46/0 in a playtest | — |
| M1 greybox core | Street, plots, build mode, walk-ins, desk, till, cleaning, floors, stairs | Yes (TESTRUN phase 1) | Save/load by rejoining once API access is on |
| M2 the street | Night Bus, wish lists, pitching, scoring, rating panel | Yes (phase 2) | Legendary announcement seen; requests by Help prompt |
| M3 collection | Friendship, move-ins, residents, staff, offline income, Book | Yes (phase 3) | Offline earnings need DataStore |
| M4 progression | Rebirth, Moon Tree, Frostfang, Gloom tutorial, analytics, phone layout | Yes (phase 4) | Phone layout seen again after the last fix |
| M5 live | Store (placeholder ids), boosts, ads, dailies, login, codes | Yes (phase 5) | Real ids from Creator Hub (WAITING §3.2) |
| M6 polish | Hunter Night, traps, sound, settings, low graphics, LOD, facade, rare check-in moment; 15 UI images uploaded and used | Yes (phase 6) | Import the staged models (WAITING §0) |
| §7 social | Likes, Street Favourite, friend bonus, pings, street + global leaderboards | Partly (two-player parts are his) | Co-managers (WAITING §2.5) |
| §8.2 events | Full Moon weekend, Full Moon Hunt, Monster Parade, Halloween, Candy shop | Yes (specs, a purchase) | Winter content |

**Dev tools (Studio only, remove before release):** `workspace.DevCommand`
(DevGrant: cash, walkin, checkin, finish, request, bus, decide, resident,
friend, rebirth, runcash, receipt, pass, hunters, fill, data ...), and
`ServerStorage.StudioProfile`.

**Playtest lessons:** Studio must be in front (prompts and RenderStepped stop
in the background); mouse coordinates are viewport pixels (3434 wide), captures
1920 wide. `tools/sync_sizes.py` for the sync check.

**His rulings for the work in hand:** none yet; every night draft is in GDD
Appendix A and WAITING §2.
