# Launch

The soft launch of Build a Monster Hotel: what it needs, who does it, in what
order. Agreed with August in a grilling session on 2026-10-23; his rulings are
in `docs/GDD.md` §18 (2026-10-23), what waits on him in `WAITING.md` §4.

## The goal

- **A public soft launch, this weekend (24–25 October 2026)** if it is ready;
  the content decides, not the date. **Nothing is cut:** every workstream below
  ships. No ads before launch day; August runs some ads from then (his budget).
- **Feature freeze** from 2026-10-23: fixes, models, imports, animations,
  balance, tests and his calls only. After launch: Expeditions (A.11.2),
  co-managers, emotes, Winter crossover guests, the third notification, the
  community (group) and its join reward.
- **Everyone starts from zero** at launch, August too: the published game gets
  its own DataStores, Studio another.

## How the work runs

- **Sessions in parallel**, each on its own worktree branch, briefed from this
  file. The orchestrating session merges a branch into `main` once its specs
  (`lune run tools/run_specs.luau . <spec>`) and `stylua src/ && selene src/`
  pass (August's go, 2026-10-23). No session writes the live DataStore.
- **One Blender build and one Studio user at a time.** Before running Blender
  or using the Studio MCP, a session takes the lock: create the file
  `.locks/blender` or `.locks/studio` in the main checkout
  (`D:\Roblox\build-a-monster-hotel\.locks\`) containing its session name and
  the time; if the file exists, do other work and try later; delete it when
  done. Blender stays at below-normal priority with `-t 4` (CLAUDE.md).
  Never use Studio while August is importing.
- **Usage:** the 90 % weekly stop is lifted until launch (his ruling). August
  has a manual reset: the orchestrator sends him a push notification when the
  weekly limit nears 100 %, and when an import is staged.
- **When August is AFK or asleep nobody waits on him:** take other work, write
  the assumption down, carry on. Playtests that need Studio in front run only
  then.
- **Looks:** Bayou Spa's monsters and kit, the VIP lounge set and the four
  facade packs go to him in **one approval round**: silhouettes, a blind
  review and finished renders, a yes or no per model. A no that cannot be
  redone in time ships as it is and is changed after launch.

## Workstreams

| # | Work | Who | Needs | State |
|---|---|---|---|---|
| 1 | Bugs: a moved or placed stair can strand a booked floor (`BuildService` move/place, `Rooms.canPlacePiece`); a spec for CutsOff/KeyCutOff; Glass seen in Studio | orchestrator | Studio for Glass | done 2026-10-23: stair fixed with a spec; Glass 0.55 seen in a playtest |
| 2 | Live and Studio DataStores apart (ProfileStore and leaderboards; no `Test_` keys in the live store) | orchestrator | — | built (`StoreNames`), not yet run on a published server |
| 3 | The 136-FBX import (WAITING §0.12): settings, save, sync check, seen in the game (skill `import`) | August imports, orchestrator the rest | Studio | done 2026-10-23: saved, and seen as kit clones in a playtest at all three locations (TESTRUN "Launch import"); no pictures yet |
| 4 | Bayou Spa's 10 monsters (`Species.luau` rows), with the rig of #6 | session | Blender | built and approved 2026-10-23 (merged); waits on the rig, then one rigged import |
| 5 | Bayou Spa's kit (walls, door, post, desk, furniture, decor, stairs, facade) and the VIP lounge decor set the VIP Lobby pass promises (§10.2) | session | Blender | done 2026-10-23: built, approved, imported and saved (kit 15, facade 7, VIP lounge 5); not yet seen in a playtest |
| 6 | Real animations: an armature per body shape (Blob, Biped, Float, Serpent) in the build scripts, imported as Rig Type Custom; the six clips of §12 (walk, idle, happy, sad, check-in, staff) played on the client by `Bone.Transform`, nothing uploaded. Proved on one species first (every colour part deforms, Tiny/Giant scale, phone cost), then all 27 rebuilt | session | Blender, Studio | prototype merged; Skeleton imported 2026-10-23, being proved in Studio by session `animations` |
| 7 | Balance run (Fable): `tools/balance_model.py` against §6.3's targets; economy and pacing values only (not Robux prices, server size or looks); the code rewards (`WELCOME`, `SPOOKY`, new `HALLOWEEN`); every change logged with a reason; August approves the summary, then PLACEHOLDER is struck | session (Fable) | — | done 2026-10-23: approved and merged (`archive/BALANCE-2026-10-23.md`) |
| 8 | Game icon and thumbnails: three of each, from the game and Blender; he picks | session | Studio or Blender | session `store-art` (with the facade-pack passes of #9) |
| 9 | Creator Hub, by the orchestrator in the browser: Server Size 10 (= `Constants.Street.Plots`), more translation languages (auto translation is on, his), private servers 100 Robux/month, the four facade-pack passes and their gifts with icons, the maturity questionnaire filled in for his read before it is sent | orchestrator | #5, #8 | server size, private servers and languages done 2026-10-23 (universe 10771829930); passes and questionnaire open |
| 10 | Notifications: his Open Cloud key and the `OpenCloudKey` secret (WAITING §3.3); the two message strings by Claude | August, then orchestrator | — | open |
| 11 | The launch run: TESTRUN's open items that one person can run with Studio's multi-client test (no friends test: August and Claude test, his ruling), the DevCommand lock on a real server, Publish, his 15 minutes on his own phone, the game made public (his) | orchestrator, August | all above | last; its order and night guard in `TESTRUN.md`, "Launch run" (2026-10-23): he starts Server and Clients, the rest runs unattended |
