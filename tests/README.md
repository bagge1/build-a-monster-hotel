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

## Writing one

A spec is a chunk, not a module: it runs inside `do ... end` after the harness,
so it sees `Shared` (the `ReplicatedStorage.Shared` folder), `describe`, `it`
and `expect` (`eq`, `near`, `truthy`, `atMost`, `atLeast`). Require what it
tests from `Shared`.

| Spec | What it holds the module to |
|---|---|
| `grid` | Doors open beside their own footprint; the lobby and stair core are never built on; no placement cuts a door off; every door has a straight-legged path in |
| `economy` | Costs grow with count and tier; selling never refunds more than was spent; tier, milestones, mutations and bonuses never lower pay; rarer and later species pay more; bonuses add within and multiply across; offline is capped; shards are a square root |
| `stay` | Satisfaction in 0–100; preferences, tiers, amenities and requests never lower it; waits and missed requests never raise it; reviews 1–5 and monotonic; tips never negative |
| `scoring` | An ineligible hotel is never picked; pitches and better hotels never score lower; the newcomer boost is Common/Uncommon only; ties go to the nearest |
| `rating` | Stars 1–5 in half steps; categories 0–100; better inputs never lower the stars; only the last reviews are kept |
| `bus` | One Legendary per half hour, one Mythic per two hours, an Epic every third bus; size grows with players within bounds; the guarantees are aboard |
| `data` | Every species' room exists in its location; every preference can be met; every room serves somebody; every playable location has a rebirth resident; event mutations are never rolled; the remote layer drops malformed messages |
