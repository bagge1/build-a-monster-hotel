# Tests

Rules the pure shared modules must keep, run against the real modules in
Studio.

**A spec states rules, never values.** "Buying never costs less than selling
pays", "a rebirth never lowers income", "one large sale pays what ten small ones
do" survive any tuning; a test that pins a number fails the first time
balancing touches it.

## Running them

There is no Luau runtime outside Studio, so the tests run inside it through the
Studio MCP. Claude does this; August does not need to.

1. `python tools/test_bundle.py [spec ...]` joins `harness.luau` and every
   `<name>.spec.luau` (or the named ones) into `src/server/TestBundle.luau`, a
   gitignored ModuleScript that Rojo syncs and nothing in the game requires.
2. Start a playtest, then with the MCP, against the **Server** datamodel:
   `return require(game.ServerScriptService.Server.TestBundle:Clone())`. The
   answer is `<n> passed, <m> failed`, then one `FAIL` line per failure. **Not
   the Edit datamodel**: its module cache outlives a Rojo sync, so it tests
   yesterday's modules (`DEVNOTES.md`).
3. `python tools/test_bundle.py --clean`.

### Outside Studio, with Lune

The pure specs also run on the machine, in a second (2026-10-19, free
building), against the same modules in `src/shared`:

```bash
lune run tools/run_specs.luau . grid furnish economy
```

Every spec but `data` runs this way (its `Net` needs the engine). Lune is a
global tool (`rokit add --global lune-org/lune`); a run in Studio is still
what proves the synced game.

## Writing one

A spec is a chunk, not a module: it runs inside `do ... end` after the harness,
so it sees `Shared` (the `ReplicatedStorage.Shared` folder), `describe`, `it`
and `expect` (`eq`, `near`, `truthy`, `atMost`, `atLeast`). Require what it
tests from `Shared`.

| Spec | What it holds the module to |
|---|---|
| `grid` | Doors open beside their own footprint; the areas split the plot behind the lobby and only a neighbour is bought; rooms only in owned areas, never in the lobby or on the entrance; a new hotel fits 2–4 Standard Rooms; one desk on floor 1; a floor above is reached only by a stair and its last stair stays; stairs stack only on the same cells; hallway decor in a corner leaves a cell walkable, in its middle takes it, and never cuts a door off; no accepted change cuts a door off, and every room has a route in over stairs |
| `furnish` | Decor turned into a room's frame and back lands where it was, the door side turning with the room; decor keeps out of the doorway, off the room's furniture and off itself, rugs under; wall decor only against a wall; tiers never fall with more decor and bigger rooms need more; dearer decor is worth more; every decor has a footprint and a layer |
| `economy` | Costs grow with count and tier; selling never refunds more than was spent; tier, milestones, mutations and bonuses never lower pay; rarer and later species pay more; bonuses add within and multiply across; offline is capped; shards are a square root |
| `stay` | Satisfaction in 0–100; preferences, tiers, amenities and requests never lower it; waits and missed requests never raise it; reviews 1–5 and monotonic; tips never negative |
| `scoring` | An ineligible hotel is never picked; pitches and better hotels never score lower; the newcomer boost is Common/Uncommon only; ties go to the nearest |
| `rating` | Stars 1–5 in half steps; categories 0–100; better inputs never lower the stars; only the last reviews are kept |
| `bus` | One Legendary per half hour, one Mythic per two hours, an Epic every third bus; size grows with players within bounds; the guarantees are aboard |
| `data` | Every species' room exists in its location; every preference can be met; every room serves somebody; every playable location has a rebirth resident; event mutations are never rolled; the remote layer drops malformed messages |
| `staff` | An errand starts at the post and ends at the door; a walker is as far along as it has walked; the way back ends at the post; a path survives its encoding; a job is never done before its delay nor before the resident has stood at the door; better staff are never slower |
