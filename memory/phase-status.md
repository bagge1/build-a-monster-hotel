---
name: phase-status
description: What is built, what has been run in Studio, and what is next, per phase. Code sessions read it first; rewrite the state, never append rounds.
metadata:
  type: project
---

**State (2026-10-19, 15:33):** M0–M6 built in code and played in
Studio, plus §7 social, §8.2 events (now with Winter), gift passes and worn
cosmetics (night drafts, GDD Appendix A.9–A.10). **Save, load and offline
earnings are proven** on the real DataStore (test profile `Test_Persist1019`).
**All 69 models are synced and in the game** (TESTRUN phase 9): checked part
for part against the imports, a hotel of every Haunted Manor piece built from
the kit, rays over floors and doorways, both kits' stairs walked, guests,
residents, the bus and a hunter seen as their models. The Studio copies and
`blender/_import/` are cleared. One finding: the lobby's desk and planters
stand in front of floor-1 doors (WAITING §2.10, his choice; recommendation (a),
a Grid rule).

**Next, in order:** (1) WAITING §2.10 once he has chosen. (2) Stage the next
import: both kits' `HotelSign` (posts fixed, `1de1317`; Frostfang's as
`FrostfangLodge_HotelSign`) and the seven cosmetics
(`blender/cosmetics/hotel/`); `blender/_import/` is empty. (3) Open TESTRUN
items: piece menu by clicks, rebirth by the panel's button, a two-player gift,
pictures of the cosmetics after their import. Frostfang's rooms and amenities
are synced but not yet built in a plot (needs a rebirth on the test profile).
Economy pacing: `tools/balance_model.py` (archive/BALANCE-2026-10-19.md).

| Phase | Built | Run in Studio | Next |
|---|---|---|---|
| M0 setup | Data tables, Constants, Net (typed remotes + RateLimit), PlayerData (ProfileStore), 7 specs | Specs 46/0 in a playtest | — |
| M1 greybox core | Street, plots, build mode, walk-ins, desk, till, cleaning, floors, stairs | Yes (TESTRUN phase 1, 9); save/load proven; real kit's stairs walked | — |
| M2 the street | Night Bus, wish lists, pitching, scoring, rating panel | Yes (phase 2) | Legendary announcement seen; requests by Help prompt |
| M3 collection | Friendship, move-ins, residents, staff, offline income, Book | Yes (phase 3); offline earnings proven | — |
| M4 progression | Rebirth, Moon Tree, Frostfang, Gloom tutorial, analytics, phone layout | Yes (phase 4) | Phone layout seen again after the last fix |
| M5 live | Store (placeholder ids), boosts, ads, dailies, login, codes | Yes (phase 5) | Real ids from Creator Hub (WAITING §3.2) |
| M6 polish | Hunter Night, traps, sound, settings, low graphics, LOD, facade, rare check-in moment; 15 UI images uploaded and used; 69 models in the game | Yes (phase 6, 9) | The lobby desk (WAITING §2.10); Frostfang's rooms in a plot |
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
