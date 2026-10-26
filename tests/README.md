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

**Bundle only what Lune cannot run** (`data`): every spec at once runs past
Roblox's script timeout in a playtest (2026-10-25: `busy`'s fuzz and the
rest, "Script timeout: exhausted allowed execution time"), and Lune runs the
others.

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
| `grid` | Doors open beside their own footprint; a flipped 2-wide piece's door moves to its other front cell, a 3-wide one stays; a new hotel owns the 4 × 4 square on the entrance and only a neighbour tile is bought; tiles are bought on each floor apart, upstairs over owned tiles below, and a stair needs the tiles above it; anything stands on any owned tile, never on one not owned or the entrance's mouth; the start square fits the desk across from the arch and a Standard Room; one or more desks on floor 1, the last kept; the facade walls exactly each floor's outline, the street side too; windows only on outer walls, moved out along their line; a floor above is reached only by a stair and its last stair stays; stairs stack only on the same cells; hallway decor in a corner leaves a cell walkable, in its middle takes it, and never cuts a door off; no accepted change cuts a door off, and every room has a route in over stairs |
| `furnish` | Decor turned into a room's frame and back lands where it was, the door side turning with the room; decor keeps out of the doorway, off the room's furniture and off itself, rugs under; wall decor only against a wall; tiers never fall with more decor and bigger rooms need more; dearer decor is worth more; every decor has a footprint and a layer |
| `economy` | Costs grow with count and tier; selling never refunds more than was spent; tier, milestones, mutations and bonuses never lower pay; rarer and later species pay more; bonuses add within and multiply across; offline is capped and carries neither the friend bonus nor a timed boost; shards are a square root |
| `stay` | Satisfaction in 0–100; preferences, tiers, amenities and requests never lower it; waits and missed requests never raise it; reviews 1–5 and monotonic; tips never negative |
| `scoring` | An ineligible hotel is never picked; pitches and better hotels never score lower; the newcomer boost is Common/Uncommon only; the tutorial's weight helps only a Common toward its own hotel; ties go to the nearest |
| `rating` | Stars 1–5 in half steps; categories 0–100; better inputs never lower the stars; only the last reviews are kept |
| `bus` | One Legendary per half hour, one Mythic per two hours, an Epic every third bus; size grows with players within bounds; the guarantees are aboard; the rarest guest is never outranked; the tutorial's Commons are Commons the vacant rooms take, never more than stand vacant, round the room types in turn; the tutorial's Vampire rides from the third bus after the goal card until it has reached its hotel, one at a time |
| `data` | Every species' room exists in its location; every preference can be met; every room serves somebody; every playable location has a rebirth resident; event mutations are never rolled; the remote layer drops malformed messages |
| `world` | One street per location of the chain, the first Creepy Lane as it stands; every street Creepy Lane moved along X, nothing else; streets never overlap; every street's plots are disjoint from each other and every other street's; a point's inferred street is the street it lies on (plots, stops, ring, road); a browse stays on its street; the road between two streets clears every plot; the look between streets never goes back; no tree on any street's lane, plots or road; every tree its street's location's, or the next one's between two |
| `staff` | An errand starts at the post and ends at the door; a walker is as far along as it has walked; the way back ends at the post; a path survives its encoding; a job is never done before its delay nor before the resident has stood at the door; better staff are never slower; Front Desk serves the first guest at the desk, never held up by one still walking in; a resident is home from the Hunter Camp once its time has passed |
| `contracts` | VIP contracts (A.11.1): the ledger is shut below its stars; a better rating never draws rarer VIPs less, runs fewer at once or asks fewer bars; every offer is its location's, within the rating's rarity, of a buildable type, asks one bar above the best room now (so no room meets it) and is met by full bars, its look a plain one; a type full on every bar is never asked; better bars never undo a met spec; the reward grows with rarity and income, never negative; the clock runs only at its own hotel and before Ready, and a miss loses the offer (its slot drawn anew); never more than the daily cap completed and none accepted past it; running contracts capped by the rating; a swap or a Book request costs a swap and a request is that species, refused past the rating; a rejoin puts contracts back to Accepted, a species' first completion is first once |
