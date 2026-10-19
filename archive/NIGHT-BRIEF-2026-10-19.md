# Night brief — 2026-10-19

Prepared with August on 2026-10-19 (~02:30) for the first night sprint on
Build a Monster Hotel. The session that runs it follows skill `night-sprint`
and writes its log as `archive/NATTLOGG-2026-10-19.md`.

## His go (given in the preparing session's chat, 2026-10-19)

- Work continuously through the night into the day; he reviews tomorrow.
- **Commit and push each finished step** to the private GitHub repo.
- **Playtests may write the game's DataStores** (the game is not live).
- Assets Claude creates may be implemented fully; he adjusts them tomorrow.
- **Scale of a person:** standard ~5-stud avatar, 6-stud grid cells (CLAUDE.md).
- Values are the GDD's starting values. Don't rebalance them; findings go to `WAITING.md`.

## The brief, in order

0. **Setup.** The session starts in `D:\Roblox`, not inside the project.
   - Rename `D:\Roblox\tycoon-game` to `D:\Roblox\build-a-monster-hotel`, then
     move the session there (`change_directory`).
   - Run `python tools/setup_machine.py`, which makes the memory junction for the new path.
   - If GitHub is logged in (`gh auth status`):
     - create the **private** repo `build-a-monster-hotel`;
     - point `origin` at it;
     - commit `research/`, `docs/GDD.md`, `CLAUDE.md`, this brief and the night log;
     - push.

   If GitHub isn't logged in, commit locally and put the GitHub login in `WAITING.md` §3.

   Then tell August, if he's still up: start `rojo serve` in the new folder and click **Connect**.

   *Done:* the folder is renamed, the junction exists, and the commit is pushed or logged.
1. **M0, project setup** (GDD §13.1, §14.1).
   - Data tables for species, rooms, mutations and locations, holding GDD §4–§6 values in `src/shared`.
   - `Constants`.
   - A typed remote layer with `RateLimit`.
   - `PlayerData` on ProfileStore (pattern: `D:\Roblox\playbook\PATTERNS.md`).
   - The bootstrap's Init/Start in `pcall`.
   - Test harness wired.
   - `MODELS.md` sections for the hotel kit and monsters, **before any model**.

   *Done:* `rojo build` succeeds, StyLua and Selene are clean, specs pass.
2. **M1, greybox core** (GDD §3–§5).
   - Plot claim on a 6-stud grid.
   - Build mode for rooms (Luau blockouts carrying `MODELS.md` attachments).
   - Walk-in guests, check-in, pay per second, till.
   - Save and load.
   - `TESTRUN.md` items written.

   *Done:* Claude has played it in Studio (skill `playtest`).
3. **M2, the street** (GDD §4.3–§4.4, §5.3).
   - Night Bus schedule.
   - Guest scoring and wish lists.
   - Pitching.
   - Rating v1.
   - Cleaning and requests.
   - Client-rendered NPCs (§13.2).

   *Done:* played in Studio.
4. **M3, the collection** (GDD §4.5–§4.6).
   - Friendship.
   - Residents and offline income.
   - Staff roles.
   - Monster Book.
   - Mutations.

   *Done:* played in Studio.
5. **If there's time:** M4's rebirth and the Gloom tutorial (GDD §6.4, §11), or monster and hotel-kit
   models in Blender (skill `modelling`), staged for his import in `WAITING.md` §0.

**Blocked steps:**
- **Studio not connected:** keep building the code and specs, write "not run in Studio" in the log and
  `phase-status`, and put **Connect** in `WAITING.md` §0.
- **A design fork:** take the reversible option, write it in the log, and put the question in
  `WAITING.md` §2 (Swedish).

Skip to the next step rather than waiting.

## Rules for the night

- Check usage before every step:
  - weekly ≥ 90 %: wrap up and end;
  - 5-hour ≥ 95 % (his ruling for this night, 2026-10-19; the default is 90 %): finish the step, commit, sleep past the reset.
- Never start, stop or restart `rojo serve`.
- No value changes. No looks settled as final: everything visual is for his review.
- Read the time from `date`.
- One playtest per step.
- No heavy renders while Studio runs.
- Stage files by path only.
