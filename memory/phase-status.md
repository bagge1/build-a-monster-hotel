---
name: phase-status
description: What is built, what has been run in Studio, and what is next, per phase. Code sessions read it first; rewrite the state, never append rounds.
metadata:
  type: project
---

**State (2026-10-19, night):** M0–M6 built in code and played in
Studio, plus §7 social, §8.2 events (now with Winter), gift passes and worn
cosmetics (night drafts, GDD Appendix A.9–A.10). **Save, load and offline
earnings are proven** on the real DataStore (test profile `Test_Persist1019`).
**All 69 models are synced and in the game** (TESTRUN phase 9): checked part
for part against the imports, a hotel of every Haunted Manor piece built from
the kit, rays over floors and doorways, both kits' stairs walked, guests,
residents, the bus and a hunter seen as their models. The Studio copies and
`blender/_import/` are cleared. His review of the pictures (2026-10-19):
the sign stands in the entrance, nobody can stand at the desk, the lobby reads
as a patio. His rules are in `modelling/taste.md`; a **blind review** by a
context-free model now comes before he sees any picture (skill `blind-review`;
its first run and triage are in the Haunted Manor README).

**His first long playtest (2026-10-19 evening)** gave twelve fixes, done and
seen in a playtest (HUD row in the top bar, build camera zoom/turn, B and R
keys, grouped build tools, a chosen card put down by a second tap, a hover
outline and the piece menu reachable, the Book roomier, the facade sill and
slab rails no longer flicker, the till turned and moved, the room plaque
`RoomPlaque` over every door) and **new design** in GDD §4.3 and §5.4: the
Night Bus (two stops, browsing guests, no walk-ins, every 3 min, 40 %), a
forecourt, a forest the bus drives out of, and free building (areas, placed
stairs, a movable desk, rugs and decor, floors, tiers from furnishing, staff
seen working). **Customizing is the game's most important thing** (his words).
Open questions in WAITING §2.16 and §2.19. **Next: three sessions**: (A) the
street: **built on branch `claude/street-bus-forest-253849`** (the forecourt,
the Night Bus's two stops and browsing, no walk-ins, the forest; five trees
staged for import, WAITING §0 punkt 8; his calls §2.20–2.21), specs pass
under Lune, **not run in Studio** (TESTRUN phase 12, after the merge and a
Rojo restart); (B) free building; (C) staff walking
to their work.

**(B) Free building is built on branch `claude/free-building-4b66e3`**
(2026-10-19, not merged, **not run in Studio**): areas, placed stairs, the
`FrontDesk` piece (its points mirrored onto the lobby), decor on 3-stud
squares (`Grid`, `Furnish`, `Layout`), floor finishes, tiers T1–T3 from decor
points; PlayerData schema 2 rebuilds every hotel from the start area. The
lobby shell, desks, rugs and refitted decor are staged for import; the new
Haunted Manor decor is grey silhouettes for his pick (WAITING §2.24). Pure
specs now also run outside Studio: `lune run tools/run_specs.luau .` (Lune
and luau-lsp installed globally by rokit). After the merge: TESTRUN phase 12.
`tools/balance_model.py` stops on the changed tier formula until it models
furnishing.

**Gamepad navigation (GDD §11)** is built on branch `claude/gamepad-navigation` (2026-10-19, not merged, **not run in Studio**): `Controls.luau`, UI.md "Gamepad", TESTRUN "Gamepad navigation" (its stick and button items need his real controller).

**Earlier next steps:** (1) **The doubled scale** (his ruling 2026-10-19
evening, `CLAUDE.md` "The scale of a person": double only what makes the
hotel less cramped). Built, imported and played (`TESTRUN.md` phase 11):
walls meet the slab, three floors walked, a guest up the stairs, the build
camera; the in-game blind review triaged in the Haunted Manor README, its
fixes (the jambs, the stairs' handrail, the lamps) imported, synced and seen
in a playtest. Phase 11 is closed but for his calls (WAITING §2.13). The
grid gap it found (doors onto the stair core's back, guests through the core)
is fixed in `Grid` (commit ef0508f, its own session). (2) Open TESTRUN
items: piece menu by clicks, rebirth by the panel's button, a two-player gift,
pictures of the cosmetics after their import. Frostfang's rooms are not yet
built in a plot (a rebirth). Economy pacing: `tools/balance_model.py`
(archive/BALANCE-2026-10-19.md). Guests now walk twice as far inside a hotel
and ~70 s down the lane: watch the stay timings in phase 11.

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
