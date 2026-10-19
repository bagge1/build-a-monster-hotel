# Test run

What Claude plays in Studio through the MCP (skill `playtest`), item by item.
Start at the first unmarked item. Marks: `[x]` pass, `[!]` failed and fixed
(commit), `[?]` cannot be run this way (why), `[A]` handed to August (why).

## T0 Proof

- [x] A synthetic key, a click and a walk are seen to act in the game.
- [x] The sync landed: every script's size in Studio matches git (`tools/sync_sizes.py`).
- [A] `PlayerData` reports DataStore `Access`, not a mock. **It reports `NoAccess`**:
  Studio API access is off (WAITING.md §3.1).

## Phase 1 (M1, greybox core)

Run with Studio in front (a background Studio stops `RenderStepped` and prompts).
Mouse coordinates are viewport pixels: a capture is scaled to 1920 wide, so
multiply a capture's x and y by viewport width / 1920 (3434 / 1920 on his screen).

- [x] Joining claims the nearest free plot (plot 2 first) and spawns the player at the lobby's `Spawn`.
- [x] An empty hotel rates 1★ and shows $100 (§6.3).
- [x] **Build** opens build mode: the overview camera, the piece strip with prices
  and lock reasons, the tools down the right edge.
- [x] A real click on the grid places a Standard Room ($50, then $57: ×1.15); the
  ghost turns red over a taken cell with the reason.
- [x] A walk-in arrives from the lane, walks to the desk queue; the desk prompt
  checks it in; it walks the grid to its bed.
- [x] An occupied room pays $1/s for a Slime into the till.
- [x] Check-out leaves a tip and a review, the room Dirty with **Clean** on.
- [x] Holding **Clean** 2 s at the door makes it Vacant; the till prompt moves
  the till to the wallet.
- [x] Floors 2 and 3 bought: slabs, railings, stairs. A walker climbs both
  storeys and comes back down (after the landing was widened to 4 studs).
- [x] A guest to a floor 2 room walks the stairs' own turns and the floor's hallway.
- [ ] Upgrade, decorate, move and sell from the piece menu, by clicks.
- [A] Save and load by rejoining: blocked on WAITING.md §3.1 (no DataStore access).

## Phase 2 (M2, the street)

- [x] The bus countdown shows under the HUD; `bus` (dev) brings it: guests step
  off at the west stop, staggered, and browse east with their wish lists.
- [x] A guest's **Pitch** prompt within reach toasts "+15% toward your hotel"
  and turns to "Pitched!".
- [x] At the lane's end each guest picks a hotel with a vacant room of its type
  (Slime, two Pumpkin Heads to plot 2) or leaves (Mummies, Witch: no room).
- [ ] A Legendary on the next bus is announced to the street a bus ahead.
- [ ] A request appears over an occupied room; **Help** at the door fulfils it
  and tips (dev `request` opens one now).
- [ ] The rating panel (★ Rating) shows the five bars.

## Phase 3 (M3, the collection)

- [x] A Standard Room with Puddle Rug and Snack Basket (both of the Slime's
  preferences) gives a happy stay: friendship +1, the Slime's Book page found.
- [x] A second happy stay at the threshold (2 for a Common) moves the Slime in;
  friendship starts again at 0.
- [x] A Housekeeping resident cleans a dirty room by itself; a Front Desk
  resident checks a waiting guest in after 6 s.
- [x] **Residents** lists each resident with its Wing pay, the six roles (its
  best one marked) and a holiday button; **Book** shows found pages, mutations
  and friendship meters.
- [!] Two drawings of one resident at its post: a republished Wing replaced
  its folder and the client kept the old one. Fixed (ResidentRenderer).
- [!] The windows' close cross drew as an empty box (Fredoka One has no ✕): now "X".
- [ ] Holiday gives Moon Shards; offline earnings on rejoin (needs DataStore access).

## August keeps

- How the street, the lobby and the rooms look (every look is a night draft).
- Whether the build camera and the piece strip feel right with a mouse and a thumb.

## Log

- 2026-10-19 03:20 T0 and Phase 1 items 1–8 pass (the night's playtest), commit `daf7ffa`.
- 2026-10-19 03:27 Phase 2 items 1–3 pass.
- 2026-10-19 03:40 Phase 3 items 1–4 pass; two client bugs fixed.
- 2026-10-19 03:24 Stairs: the first landing (2 studs) jammed a walker; widened to 4, both storeys walked up and down.
