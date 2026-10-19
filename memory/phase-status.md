---
name: phase-status
description: What is built, what has been run in Studio, and what is next, per phase. Code sessions read it first; rewrite the state, never append rounds.
metadata:
  type: project
---

**State (2026-10-19 afternoon):** M0–M6 built in code and played in
Studio, plus §7 social, §8.2 events (now with Winter), gift passes and worn
cosmetics (night drafts, GDD Appendix A.9–A.10). **Save, load and offline
earnings are proven** on the real DataStore (test profile `Test_Persist1019`).
All 69 models (both locations' monsters, Hunter, Night Bus, both hotel kits)
are imported, set and saved in `assets/`, but **not yet synced**: Rojo needs
one more restart (WAITING §0.3). Their 69 Studio copies wait in
`ServerStorage._ImportHold` for the sync check (compare mesh ids, sizes,
collision), then delete them and `_ClaudeSerialize`.

**Next, in order:** (1) after his restart: the sync check, the cleanup, and
the playtest with real models (a walker on both kits' stairs, guests,
residents, the bus, hunters; rays over floors and doorways; pictures to
WAITING §1). (2) Stage the next import: both kits' `HotelSign` (posts fixed,
`1de1317`; Frostfang's as `FrostfangLodge_HotelSign`) and the seven
cosmetics (`blender/cosmetics/hotel/`), clearing `blender/_import/` of the 69
first. (3) Open TESTRUN items: piece menu by clicks, rebirth by the panel's
button, a two-player gift. Economy pacing:
`tools/balance_model.py` (archive/BALANCE-2026-10-19.md).

| Phase | Built | Run in Studio | Next |
|---|---|---|---|
| M0 setup | Data tables, Constants, Net (typed remotes + RateLimit), PlayerData (ProfileStore), 7 specs | Specs 46/0 in a playtest | — |
| M1 greybox core | Street, plots, build mode, walk-ins, desk, till, cleaning, floors, stairs | Yes (TESTRUN phase 1); save/load proven | Stairs walked again with the real kit |
| M2 the street | Night Bus, wish lists, pitching, scoring, rating panel | Yes (phase 2) | Legendary announcement seen; requests by Help prompt |
| M3 collection | Friendship, move-ins, residents, staff, offline income, Book | Yes (phase 3); offline earnings proven | — |
| M4 progression | Rebirth, Moon Tree, Frostfang, Gloom tutorial, analytics, phone layout | Yes (phase 4) | Phone layout seen again after the last fix |
| M5 live | Store (placeholder ids), boosts, ads, dailies, login, codes | Yes (phase 5) | Real ids from Creator Hub (WAITING §3.2) |
| M6 polish | Hunter Night, traps, sound, settings, low graphics, LOD, facade, rare check-in moment; 15 UI images uploaded and used; 69 models saved | Yes (phase 6) | Rojo restart, then play with the real models |
| §7 social | Likes, Street Favourite, friend bonus, pings, street + global leaderboards | Partly (two-player parts are his) | Co-managers (WAITING §2.5) |
| §8.2 events | Full Moon weekend, Full Moon Hunt, Monster Parade, Halloween, Candy shop, Winter (Snowflakes, shop) | Yes (specs, purchases) | Crossover guests (WAITING §2.8) |
| §10 gifts, cosmetics | Gift products per pass (profile messages), facade packs, Sign/Lobby/Facade slots, Style tool | Yes (remotes, a click); two-player gift not yet | Cosmetic models in Blender |

**Dev tools (Studio only, remove before release):** `workspace.DevCommand`
(DevGrant: cash, walkin, checkin, finish, request, bus, decide, resident,
friend, rebirth, runcash, receipt, pass, hunters, fill, data ...), and
`ServerStorage.StudioProfile`.

**Playtest lessons:** Studio must be in front (prompts and RenderStepped stop
in the background); mouse coordinates are viewport pixels (3434 wide), captures
1920 wide. `tools/sync_sizes.py` for the sync check.

**His rulings for the work in hand:** none yet; every night draft is in GDD
Appendix A and WAITING §2.
