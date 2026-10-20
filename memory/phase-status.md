---
name: phase-status
description: What is built, what has been run in Studio, and what is next, per phase. Code sessions read it first; rewrite the state, never append rounds.
metadata:
  type: project
---

**Tiles, desks and the facade round what is owned (2026-10-20, built and played in Studio, TESTRUN "Tiles, desks and the facade"):** his rulings of 2026-10-20 (GDD §5.4, A.1). The profile keeps `tiles` (Grid.tileKey as strings) and `tilesBought` (schema 3 rebuilt every hotel from the start square); `BuyTile` x, z; `Grid.facade` is the outline (walls, the arch, corner posts) that `HotelKit.facade` draws as a blockout or clones `Facade_Wall`/`Facade_Entrance`/`Facade_Corner` from the kit or a worn facade cosmetic's Folder; slabs over owned tiles only; plates over the rest of floor 1. No lobby model: `HotelPoints` (shared) finds `Entrance` on the facade, `Spawn` at the forecourt's `PathFoot`, desk points on the lowest-id desk. Several desks: each guest queues at the shortest line (`GuestService` `g.desk`), the desk's prompt checks in its own line, a sold desk's line moves. The goal card's free block: `BuildService.tutorialTiles`. PLACEHOLDERs and findings in WAITING §2.30 (only one room fits in the start square, so the tutorial's second room needs ~4 tiles). **Flip** (F, L1, ⇋ Flip; `m` per piece, `<PieceId>_Mirror` or a self-mirroring blockout, `NoMirror` until the kit writes mirrors) and **windows** (profile `windows` by Grid.edgeKey, `PlaceWindow`/`MoveWindow`/`SellWindow`, `Facade_Window_<Type>`, moved out by a tile purchase) built and played by remotes the same evening (TESTRUN "Flip", "Windows"); their real-input items wait for a night run. Next: the facade models (kits, then the five styles), another session's work.

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
Open questions in WAITING §2.16 and §2.19.

**The three branches are merged into main and played in Studio
(2026-10-19 evening loop, `archive/NATTLOGG-2026-10-19-kväll.md`):** staff
seen working (TESTRUN "Staff at work"; floor 3 not yet), the street (phase
12: specs, forecourt rays and a walker, the bus's drive, browsing, stops,
a trap; played before his Rojo restart, so `Scenery` is still missing) and
free building (phase 13, played by remotes before the import: refusals,
areas, a placed stair walked, the desk moved, decor, finishes). **Waits on
him:** WAITING §0.8–0.9, a Rojo restart and one import of all 57 files in
`blender/_import/` (five trees, 52 free-building pieces: the lobby shell,
`FrontDesk`, decor). Until then the old lobby with its desk stands beside the
new `FrontDesk` piece. After the import: phase 13's model items, the new
player's run (tutorial, bus, desk) and the in-game blind review. Also built
that evening: CI lint (§13.1), VIP Lobby's gold name tag (§10.2, WAITING
§2.22), Bellhop shortens check-in (§4.6, A.5 PLACEHOLDER, WAITING §2.23), the
phone's Residents row and Ping menu; and, merged and played the same
evening, the rating's staff coverage (§5.3, WAITING §2.26), the tutorial's
Commons on its first buses and a ping naming the wanted room (§11, §7,
WAITING §2.25), gamepad navigation by the Input Action System (`Controls`;
keyboard and mouse played, a real controller is his, WAITING §1.11). The
tutorial's guest no longer gives up at the desk. The new player's tutorial
is played Build → Done. **Pacing, his go 2026-10-20** (WAITING §2.27–2.28,
GDD §18): bus 3–8 per player, stays doubled, Legendary friendship 5, and the
goal card gives free tiles for the Coffin Suite
(`BuildService.tutorialTiles`). Modelled: rebirth 1:50 / 2:41 h, still over
60–90 min (`archive/BALANCE-2026-10-20.md`); **not run in Studio**. A full
hotel's walks up can outlast a request (§2.29). A full hotel measured 1,642 parts and
110 point lights (budget ~3,000 parts); the forest's blockouts are 3,385
parts until the tree models arrive. PlayerData schema 3 rebuilds every hotel
from the start square. Pure specs run outside Studio: `lune run
tools/run_specs.luau . <spec ...>`, every spec but `data` (it needs the
engine; with no names the run stops on it). **Release:** checklist in
WAITING §4; August's session takes the store ids (§3.2).

**Rating: staff coverage and cleaning on time** (GDD §5.3, A.4
PLACEHOLDER) built on branch `worktree-agent-ab7f9c16cd8daf5cb` (2026-10-19
night): Front Desk/Room Service coverage add to Service, Housekeeping
coverage and cleanings within 40 s to Cleanliness, on top of the old
formulas; specs pass under Lune, **not run in Studio** (TESTRUN "Rating:
staff coverage…", after the merge); his call WAITING §2.26.

**The tutorial's Commons and the named ping** (§11 1:45, §7) are built on
branch `worktree-agent-af840fbd28a857dd3` (2026-10-19, not merged, **not run
in Studio**): the first 2 tutorial buses bring Commons for the new hotel's
vacant rooms, +10 toward it (PLACEHOLDER all, WAITING §2.25); "Need a room"
names the rarest street guest's room. After the merge: TESTRUN "Tutorial
Commons and the named ping".

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
| M5 live | Store (real ids and icons since 2026-10-20: 5 passes, 8 products, the ad reward, 5 gifts), boosts, ads, dailies, login, codes; notifications (`NotifyService`, 2026-10-20: till full, Full Moon tonight, a MemoryStore queue sent through Open Cloud by the game's servers) | Yes (phase 5); the real ids not yet seen in a playtest; notifications' queue played in Studio, the send only logged (no key yet) | Facade packs (149 each) once modelled; notifications wait on his key, secret, HTTP and the two strings (WAITING §3.3); Managed Pricing (WAITING §3.2) |
| M6 polish | Hunter Night, traps, sound, settings, low graphics, LOD, facade, rare check-in moment; 15 UI images uploaded and used; 69 models in the game | Yes (phase 6, 9) | The lobby desk (WAITING §2.10); Frostfang's rooms in a plot |
| §7 social | Likes, Street Favourite, friend bonus, pings, street + global leaderboards | Partly (two-player parts are his) | Co-managers (WAITING §2.5) |
| §8.2 events | Full Moon weekend, Full Moon Hunt, Monster Parade, Halloween, Candy shop, Winter (Snowflakes, shop) | Yes (specs, purchases) | Crossover guests (WAITING §2.8) |
| §10 gifts, cosmetics | Gift products per pass (profile messages), facade packs, Sign/Lobby/Facade slots, Style tool | Yes (remotes, a click); two-player gift not yet | Cosmetic models in Blender |

**Dev tools (Studio only; on a published server none is registered or listened for, 2026-10-20):** `workspace.DevCommand`
(DevGrant: cash, walkin, checkin, finish, request, bus, decide, resident,
friend, rebirth, runcash, receipt, pass, hunters, fill, data ...), and
`ServerStorage.StudioProfile`.

**Playtest lessons:** Studio must be in front (prompts and RenderStepped stop
in the background); mouse coordinates are viewport pixels (3434 wide), captures
1920 wide. `tools/sync_sizes.py` for the sync check.

**Haunted Manor's ten new decor (2026-10-20)**: his picks and yes in GDD §18; modelled to MODELS.md "Decor"'s new rules (Pieces agreement, seats, no coplanar faces, enforced by `hotel_kit`), imported, saved and seen placed in a playtest (TESTRUN 23:19). His small calls WAITING §2.24; his decor/customization picks from `docs/DECOR_IDEAS.md` WAITING §2.33 (Frostfang has no decor for *quiet* or *silence*).

**His rulings for the work in hand:** none yet; every night draft is in GDD
Appendix A and WAITING §2.
