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

Every spec but `data` runs this way; `Net` loads too, against a stub `game`
(2026-10-26), so `net` runs here. Lune is a
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
| `furnish` | Decor turned into a room's frame and back lands where it was, the door side turning with the room; decor keeps out of the doorway, off the room's furniture and off itself, rugs under; wall decor only against a wall; tiers never fall with more decor and bigger rooms need more; dearer decor is worth more; every decor has a footprint and a layer; a floor finish changes a floor only to another finish; a furniture set's piece serves every type its set serves (A.13.3), and his keys stand (Game Room, Snack Bar, Graveyard Garden) |
| `economy` | Costs grow with count and tier; selling never refunds more than was spent; tier, milestones, mutations and bonuses never lower pay; rarer and later species pay more; bonuses add within and multiply across; offline is capped and carries neither the friend bonus nor a timed boost; shards are a square root |
| `stay` | Satisfaction in 0–100; preferences, tiers, amenities and requests never lower it; waits and missed requests never raise it; reviews 1–5 and monotonic; tips never negative |
| `scoring` | An ineligible hotel is never picked; pitches and better hotels never score lower; the newcomer boost is Common/Uncommon only; the tutorial's weight helps only a Common toward its own hotel; ties go to the nearest |
| `rating` | Stars 1–5 in half steps; categories 0–100; better inputs never lower the stars; only the last reviews are kept; a star request asks the next whole star (none at the top) and counts only at the hotel it was drawn for |
| `bus` | One Legendary per half hour, one Mythic per two hours, an Epic every third bus; size grows with players within bounds; the guarantees are aboard; the rarest guest is never outranked; the tutorial's Commons are Commons the vacant rooms take, never more than stand vacant, round the room types in turn; the tutorial's Vampire rides from the third bus after the goal card until it has reached its hotel, one at a time |
| `data` | Every species' room exists in its location; every preference can be met; every room serves somebody; every playable location has a rebirth resident; event mutations are never rolled; the remote layer drops malformed messages |
| `world` | One street per location of the chain, the first Creepy Lane as it stands; every street Creepy Lane moved along X, nothing else; streets never overlap; every street's plots are disjoint from each other and every other street's; a point's inferred street is the street it lies on (plots, stops, ring, road); a browse stays on its street; the road between two streets clears every plot; the look between streets never goes back; no tree on any street's lane, plots or road; every tree its street's location's, or the next one's between two |
| `staff` | Every post stands on its floor inside its area (the desk's footprint, its front cells, the entrance's mouth) for any count; an errand starts at the post and ends at the door; a walker is as far along as it has walked; the way back ends at the post; a path survives its encoding; a job is never done before its delay nor before the resident has stood at the door; better staff are never slower; Front Desk serves the first guest at the desk, never held up by one still walking in; a resident is home from the Hunter Camp once its time has passed |
| `store` | Every pass has one gift product at its price, giving a pass that exists; keys are unique; `Buy` prompts neither a gift (only `Gift`) nor the ad's product |
| `contracts` | VIP contracts (A.11.1): the ledger is shut below its stars; a better rating never draws rarer VIPs less, runs fewer at once or asks fewer bars; every offer is its location's, within the rating's rarity, of a buildable type, asks one bar above the best room now (so no room meets it) and is met by full bars, its look a plain one; a type full on every bar is never asked; better bars never undo a met spec; the reward grows with rarity and income, never negative; the clock runs only at its own hotel and before Ready, and a miss loses the offer (its slot drawn anew); never more than the daily cap completed and none accepted past it; running contracts capped by the rating; a swap or a Book request costs a swap and a request is that species, refused past the rating; a rejoin puts contracts back to Accepted, a species' first completion is first once |
| `visits` | Visits (A.13.1): only ready, reachable activity rooms with a free spot that meet a preference are visited, never a bedroom, and a guest with no match never visits; an unmet preference first; a spot is one guest's and a guest holds one; a visit is due 90–150 s after the last, a decision at most once per gap, none past the hotel's cap on walkers; a visit lasts 20–40 s and adds satisfaction once a stay; a visitor going or there makes its room busy, one walking back does not; visitors of a room no longer ready are sent home |
| `expeditions` | Expeditions (A.11.2, the pay his ruling of 2026-10-26): a destination only while its location is open; only Wing residents at home go, 1 to `Party` of them, one trip at a time; away until the trip ends (no perk, learning as in the Wing), home at its end without collecting; Best for this trip puts matching first, then level, then rarity; the pay is `Pay` × staying's earnings, online by the second and away by `Economy.offline`'s rate and cap, never more than staying; a trip back before the login never also fills the offline till; the find's chance never falls with length or matches, the matches never touch the pay, a long trip's find is guaranteed after `PityTrips` misses; Collect waits for the end and pays and rolls once; a rebirth's recall pays what was counted and rolls nothing; an old trip never sends home a resident on a new one |
| `moontree` | Moon Tree (§6.5): ids unique; every level below the top has a price, the price never falls with the level, none at the top; a level never gives less, nothing at 0, capped at the top; the offline node never adds more than an hour |
| `unlocks` | A piece is never met before each of its conditions (rooms, floor, rating, a Legendary) and met exactly at them; more of any never takes an unlock away; another location's piece is never met, location 0's everywhere; once unlocked it stays buildable with nothing (§6.4), and the tutorial unlocks early |
| `walk` | A path and its waits survive their encoding; a walk lasts its length at its speed plus its waits; a walker starts at the first point and stands at the last past the end; never faster than its speed, still while waiting, facing a unit way |
| `layout` | The profile's maps and the state's lists make the same world; unknown items are left out, every piece takes its row's footprint and kind; hallway decor has no room; tiles owned only when true, by string or number key; walls and rooms found as maps or lists |
| `format` | A written number never says more than it is nor less by its last digit, with one decimal at most; an exact tenth of a suffix reads exactly; a bigger number never reads smaller; cash never prints a NaN or a negative zero; a duration is never negative and reads back to its whole seconds (minutes past an hour); stars read as themselves |
| `net` | Every remote has a direction and known argument types, a client's a positive rate; every client remote takes its own well-formed message and refuses NaN, ±inf, a wrong type, an over-long string, a missing or an extra argument; a string at exactly `MaxString` passes |
| `hotelpoints` | Desks are the Desk pieces only, lowest piece id first as numbers; Entrance is read from the facade, Spawn is the forecourt's PathFoot, the desk's points from the first desk; a missing model or attachment is nil, never an error |
| `pieces` | Every piece, decor and finish has a unique id and a location that exists; a positive whole footprint and a known kind; every unlock is reachable (rating on the 1–5 half-star scale); every playable location has a room from the start; every rare set's pieces exist, are found, its location's and name the set; every key, furniture set, souvenir (one per species) and pass names something that exists; every type a furniture set serves exists |
| `species` | Every species has a unique id, a playable location, a known rarity, role and shape; its room is a Room in Pieces of its own location; its preferences are distinct and each given by some decor or amenity; a location's family is its species in roster order, every playable location has one |
| `locations` | Every location's id is its place in the list, names unique; the playable ones come first and `last()` is the chain's end; an unknown location reads as the first |
