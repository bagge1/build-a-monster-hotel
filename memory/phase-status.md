---
name: phase-status
description: What is built, what has been run in Studio, and what is next, per phase. Code sessions read it first; rewrite the state, never append rounds.
metadata:
  type: project
---

**Bayou's cypress and the world's pictures (2026-10-22 evening):** `Tree_Cypress` built in `tools/build_street_trees.py` (silhouettes A/B/C, A built; three blind-review rounds, triage in `blender/street/trees/README.md`); see its README for whether it is staged. The world photographed for the first time (Studio draws frames when in front): `archive/screens/2026-10-22_world_*.jpg`, blind review triaged in TESTRUN "The world" (looks to WAITING §2.46). The four geometry checks it raised were all false (TESTRUN). **Launch (2026-10-23):** `LAUNCH.md` is the plan and its table the state. The published game saves to `MonsterHotel_Live_*` (`StoreNames`), Studio to the old names. `tools/balance_model.py` runs (checked 2026-10-22).

**Code bugs found 2026-10-22, still open (code, not his):** `Rooms.check` now refuses a change leaving a ready room `Unreached` (CutsOff) or its key furniture split off where it stood (KeyCutOff), per A.12, but no spec proves it yet (a corridor walled off needs a world built for it: the start square's desk stands beside the door's hallway half cell). Fixed 2026-10-23: moving a stair checks against the world as it stood (`Rooms.canPlacePiece`, spec "moving the only stair never strands a ready room upstairs"). Fixed the same evening: e36cb42, 3102609, and the last commit of the night (the "-0" edge key normalised, a travel settles the chain's tick first, a rebirth resamples; played: a travel paid the 29 s since the last tick).

**The kits' shared furniture and glass (2026-10-21 afternoon):** Frostfang Lodge's and Bayou Spa's own versions of the 23 every-location pieces went through six blind-review rounds (triage in `blender/rooms/frostfang_lodge/README.md`, `bayou_spa/README.md`); the review figure `sit_blocks` was corrected (seats 0.6 deep); the 18 changed pieces are restaged in `blender/_import/` (133 FBX, WAITING §0.12, his import stalled at 13:38). The looks the reviewers pulled both ways, the seat height (feet 0.6–0.7 off the floor on every seat, all three hotels) and the bar stool's tuck are his (WAITING §2.45). **Found:** no code made `Glass` parts see-through; `HotelKit.rooted` now does (Glass, 0.55, PLACEHOLDER look), **not run in Studio**.

**Rare decor sets and souvenirs (GDD A.11.3; built and played by remotes 2026-10-21 morning, TESTRUN "Rare decor sets and souvenirs", profile `Test_Rare1021a`):** on the scrutinized recommendations, every number `Constants.Finds` PLACEHOLDER, his calls WAITING §2.38. Pure rules `Shared/Finds` (spec `finds`, 9 rules). `Pieces` rows: the Count's Study (`CountStudy_Rug`, `_Portrait`, `_Clock`, `_Globe`, `_Bust`, location 1, `found`, `set`; `Pieces.Sets` gives the name and the pity's order) and a `Souvenir_<Species>` row per species (`souvenir`, placeable at any hotel); The Aurora Lodge (Frostfang) and the Lantern Grove (Bayou) have their rows too (5e4cfd4, played by remotes). Profile `finds` (`found` by decor id, `misses` per location, `moveIns` per species; Reconcile adds it, no schema bump). `FindService`: a roll per happy stay of a Rare-or-better guest (2 %) and per player on a defended Hunter Night (25 %), the pity after 40 misses gives the next unfound piece, duplicates pay 5 min of income; souvenirs by move-in no. 3 or the species' first VIP contract; rebirth keeps (`KeepThroughRebirth`); `Moment` "Found"; state `finds`; dev `rare roll|misses|give|souvenir|reset|show`. `BuildService` refuses an unfound piece (`NotFound`), places copies at their price. `Rooms.bars` adds +0.25 Decor for a whole set in the oldest room holding it (`bars.sets`), once per set per hotel. `HotelKit.souvenir`: `Souvenir_Base` from `ServerStorage.Cosmetics` (`assets/Cosmetics/`, no project change) or its blockout, `Ribbon` the species' colour, `Trim` 0.6 of it, name on `Badge`, a blockout emblem disc with the initial on `Medal` (no emblem images exist). UI: the Decor tab's Found (gold ★) and unfound (dark ?) cards, the room view's set line, the Book's "souvenir ★ / n/3", the `FindsPanel` pop-up with Place it (UI.md "Found"). **Not yet:** his import of the five pieces and `Souvenir_Base` (then the models replace the blockouts), the cards, room view and Place it seen or clicked with Studio in front, pictures, expeditions' finds (not built). `tools/balance_model.py` leaves `found` rows out of the shop; it does not model the set bonus. Furniture walling a room's key spot off is refused (`KeyCutOff`) and such a room is not ready (ef710de, played).

**VIP contracts (GDD A.11.1; built and played by remotes 2026-10-21 morning, TESTRUN "VIP contracts", profile `Test_VIP1021a`):** on the scrutinized recommendations, his calls WAITING §2.38, every number `Constants.Contracts` PLACEHOLDER. Pure rules `Shared/Contracts` (spec `contracts`, 12 rules): from 2★ the ledger offers 3 for the played hotel (its location's species up to the rating's rarity, `RarityByStars`; room type buildable; one bar 0.5/1.0 above the hotel's best room of the type, a second at 0.5 from 3.5★; sometimes a plain look); offers a room has come to meet are pruned and redrawn; 1 running (2 from 4★); swaps 1 a day (+1 VIP Lobby), a Book page's 👑 asks for a species for a swap; clock 45 min of play at the contract's own hotel, stopped from Ready; a miss is gone and its slot redrawn; at most 3 completed a UTC day, none accepted past it. Profile `contracts` (a Ledger; Reconcile adds it, no schema bump); `ContractService`: Accept, Ready (holds a ready vacant room meeting it: Reserved with no guest, so the bus's vacancy count and other hotels never see it), Cancel; the VIP rides as an EXTRA SEAT (`BusService.setVips`, added after the bus is sized), steps off booked into the held room, `GuestService.markVip` (waits at the desk, pay × 2, `VipFor` gold label and glow); a happy stay in a room that met the spec at check-in pays `RewardMinutes` × rarity factor of income without the VIP's own pay, an unhappy one forfeits; session states go back to Accepted on rejoin, travel, rebirth or a lost hold. The first completion of a species gives its souvenir (`ContractService.onSouvenir` → `FindService`). UI: `VipPanel` (HUD left "👑 VIP", the desk's "VIP ledger" prompt F/LB, UI.md "VIP ledger"), the room view's VIP tag, the Book's `RequestVip`. Dev: `vip`, `vipstars`, `vipclock`, `vipoffer`, `vipdone`, `vipreset`. **Not yet:** the desk prompt with Studio in front, the room view's tag, an unhappy VIP, travel/rebirth while held, a phone, two players. **His calls:** the numbers, §4.3's extra-seat line, the reward at a new hotel ($10/s income floor), an unhappy VIP forfeiting.

**Endless content (GDD A.11, night brief step 9; built 2026-10-21 morning, TESTRUN "The showcase", "Residents level up", "Deeper mutations"):** each piece on A.11's scrutinized recommendation, every number PLACEHOLDER in `Constants`, his calls WAITING §2.38. **The showcase, street only** (A.11.4): pure rules `Shared/Showcase`; `SocialService` keeps the lifetime `likes` (on the sign), a weekly `likesWeek` counting each liker once a week, `played` (a like counts after `Showcase.LikeAfterPlay` of play that day) and `visited` (another player's floor-1 tiles walked into, once a day per owner → stat `hotelsVisited`, the daily kind "Visit 3 hotels", drawn only with company); each street's `StreetFavourite` by the weekly count; milestones 10/50/200/1000 give the sign cosmetics `Cosmetic_Like{Ribbon,Rosette,Trophy,GoldStar}` (blockouts) with a pop-up and Wear it; the Showcase panel (`ShowcasePanel`, HUD left) lists this server's hotels with **Visit** (`Visit` remote). Dev: `likefrom`, `played`, `visit`, `dailykind`. **Not yet:** two players (a real like, Visit, a walked visit); the global weekly board (after launch). **Residents level up** (A.11.6): `Shared/ResidentLevels`; a `ResidentRecord` keeps `level`, `xp` (nil = 1, 0); XP 1 a minute at work while the player plays (the Wing, or staff at the played hotel), the bar 20 × level and then **Level up** (`LevelUp` remote) for 10 × level minutes of the resident's own Wing rate; +10 % Wing earnings and +3 % staff efficiency a level (in `ResidentService.rate`, `staff`, `efficiencyOf`), cap 10; kept through rebirth (his call). Residents panel row `Level`, `LevelBadge` over each resident. Dev `xp <id> [amount]`. **Deeper mutations** (A.11.5): `Mutations` rows have a `group` (Size: Tiny, Giant; Look: the rest); guests, bus passengers and residents keep two fields, `mutation` (the look, by its old name) and `size`; `Events.rollMutations` rolls both independently, `Events.rollMutation` is the look roll with the season's or the month's row taken first (`Constants.Mutations.Monthly`: March Mossy, May Rainbow, July Sunburnt, September Moonlit, ×4, 3 %); pay added (`Mutations.payMultiplier(size, look)`, Economy's pay functions take `size` last); a stack fills both Book entries plus `Stacked`, the first gives "Stacked Host"; a month's look gives no set title; `Size` on guest and resident Configurations, scale and tint together in `MonsterKit`; `MonthlyMutation` workspace attribute, its announcement and Events line. **His calls:** a missed month coming back off-season, the monthly looks and names (WAITING §2.38).

**One world (his ruling 2026-10-20, GDD §3, §6.4; built and played by remotes 2026-10-21 morning, TESTRUN "The world"):** a street per location of the chain along world X, `Constants.World.StreetSpacing` 1400 apart (PLACEHOLDER), street s = location s, each Creepy Lane's layout moved (Creepy Lane unchanged, in `workspace.Street`; the others `Street_<s>`). `StreetLayout` takes an optional last `street` (default 1) where it cannot infer it and infers it from X otherwise (`streetAt`, `stops(s)`, `stopNamed`, `route(s)`, `hunterCamp(s)`, `link`, `blend`); stop names are unique (`West_2` …). A player keeps one plot index on every street: the played hotel is the live `Plot_<i>` in `workspace.Plots`, which moves to its street on a Travel or rebirth (`PlotService.rebuild`: the frame, `Street` attribute, the character streamed and moved to its forecourt); the chain's others are drawn static from their HotelRecords in `workspace.WorldPlots` (`Plot_<s>_<i>`, `Static`, `HeldBy`; no prompts, no handlers, a sign with the stars left). A bus per street with a hotel played (one timetable; `BusStreets`), its location's family only, sized, guaranteed and announced per street; guests carry `street` and browse and choose on it; a street left without a played hotel loses its street guests. Hunter Night on every street played, a camp per street. The forest covers all streets with a meadow along the road between them (`World.MeadowHalfWidth`) and trees blending by `StreetLayout.blend`; `Forest.DrawDistance` 1100 keeps ~5,000 trees drawn; `WorldGround` blends each location's `world` ground in bands; lamps in `Locations` `lamp`, their light only within 500 studs (`Lod`). Bayou Spa's `Tree_Cypress` is a Luau blockout in `ForestRenderer` with MODELS.md's tree parts (no model yet). Measured: server 1,248 parts / 188 lights for one player with three start hotels; client ~10.6k parts (forest ~10.1k), 63 lights. **Not yet:** pictures (Studio drew no frames that morning), two players on two streets, the leaderboards stay on Creepy Lane. **His calls:** the spacing, the looks of the other streets and the meadow, Bayou's tree set (WAITING).

**Built rooms (his rulings 2026-10-21, GDD §5.4, A.12; built and played in Studio 2026-10-21 night, TESTRUN "Built rooms", commits 78a5aea, 3727af0 and the clean-up):** rooms are no longer pieces. Profile schema 6 keeps `walls` (Rooms.edgeKey → `{door?, paid}`) and `rooms` (id → `{type, floor, hx, hz, finish}`), in the chain's hotels too; `layout` holds only desks and stairs. A new hotel (and a rebirth, a new location) starts with one built room: `Constants.Rooms.Start`, an L of four cells on the guests' right of the desk with a door and a Bed (PLACEHOLDER shape; at another location its first room type and key piece). Remotes `WallRun` (a straight run of half edges, $5 each), `Door` ($10), `MakeRoom`, `ClearRoom`; desks, stairs, decor, furniture and tiles held to `Rooms` (`canPlacePiece`, `canPlaceDecor`, `check`); a tile bought beside a room walls itself off (`Rooms.autoWalls`); a room a guest is in or due at must stay ready (`Busy`). `HotelKit.walls` draws `Wall_Half`/`Wall_Door`/`Wall_Post` from the kit or a blockout with MODELS.md's attachments; each room gets an invisible marker `R_<id>` in `Pieces` (`Door`, `Sign`, `KeySpot`, `Bed` = the key furniture's `Use`; plaque and prompts), so `piecePoint`/`roomPrompt` work for rooms. Guests are booked only into ready rooms (`HotelService.ready`), walk `Rooms.route` on the 3-stud squares through the door to `Rooms.keySpot` and onto `Use`; `Rooms.bonuses` give pay, stay, satisfaction and friendship in place of tiers; Comfort's room part is `Rooms.comfortPoints` (never falls). Build mode: tabs Walls (drag or tap, Half cells, Door, Remove), Rooms (cards per room), Furniture, Decor, Stairs/desks, Floors, Windows; a tap on a walled space with a door opens the type list (`RoomTypes`), a tap on a room the room view (`RoomView`: camera flies in, near walls fade, three bars). The tutorial starts at CheckIn; SecondRoom (walls, door, type) then Furnish (a Bed); the goal card's block goes to the side without rooms; the Coffin is free by voucher. Flip and `<PieceId>_Mirror` are gone. **Not yet:** the kit's wall and furniture models (staged by another session, after his import), a gamepad and a real phone. **His calls:** the start room's shape, the room view's look on a phone, the PLACEHOLDER prices (WAITING).

**Tonight (2026-10-20 night):** the 49 facade pieces are fixed up (all `Box`, proxies hidden), saved to `assets/HotelKit/<Kit>/Facade_*.rbxm` and `assets/Cosmetics/Cosmetic_<Style>Facade/` and synced (no empty mesh; PrimaryPart dropped by live sync as usual). Left of skill `import` step 5: compare mesh ids and sizes with the Workspace copies `Saved<Style>_Facade_*` (the last style, Slime, is still named `Facade_*`), then delete them, `ServerStorage._ClaudeSerialize` and `blender/_import/`. Then then the playtests left for tonight (TESTRUN "Tiles per floor, every floor walled").

**Tiles, desks and the facade round what is owned (2026-10-20, built and played in Studio, TESTRUN "Tiles, desks and the facade"):** his rulings of 2026-10-20 (GDD §5.4, A.1). The profile keeps `tiles` (Grid.tileKey as strings) and `tilesBought` (schema 3 rebuilt every hotel from the start square); `BuyTile` x, z; `Grid.facade` is the outline (walls, the arch, corner posts) that `HotelKit.facade` draws as a blockout or clones `Facade_Wall`/`Facade_Entrance`/`Facade_Corner` from the kit or a worn facade cosmetic's Folder; slabs over owned tiles only; plates over the rest of floor 1. No lobby model: `HotelPoints` (shared) finds `Entrance` on the facade, `Spawn` at the forecourt's `PathFoot`, desk points on the lowest-id desk. Several desks: each guest queues at the shortest line (`GuestService` `g.desk`), the desk's prompt checks in its own line, a sold desk's line moves. The goal card's free block: `BuildService.tutorialTiles`. PLACEHOLDERs and findings in WAITING §2.30 (only one room fits in the start square, so the tutorial's second room needs ~4 tiles). **Windows** (profile `windows` by Grid.edgeKey, `PlaceWindow`/`MoveWindow`/`SellWindow`, `Facade_Window_<Type>`, moved out by a tile purchase) built and played by remotes the same evening (TESTRUN "Windows"). Flip was removed with built rooms (2026-10-21). The facade models (2026-10-20): 49 pieces, seven per style (`Facade_Wall`, the four `Facade_Window_<Type>`, `Facade_Entrance`, `Facade_Corner`) for both kits and the five facade cosmetics, built by `tools/build_facades.py` into `blender/facade/<style>/`, validated in Blender only and staged in `blender/_import/`; waiting on his import (WAITING §0.11) and his look (§1.12, §2.34). After his yes: `Cosmetics.luau`'s facade rows as models, the four packs' passes and gifts (his go), `Store.luau`.

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
