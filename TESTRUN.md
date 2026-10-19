# Test run

What Claude plays in Studio through the MCP (skill `playtest`), item by item.
Start at the first unmarked item. Marks: `[x]` pass, `[!]` failed and fixed
(commit), `[?]` cannot be run this way (why), `[A]` handed to August (why).

## T0 Proof

- [x] A synthetic key, a click and a walk are seen to act in the game.
- [x] The sync landed: every script's size in Studio matches git (`tools/sync_sizes.py`).
- [x] `PlayerData` reports DataStore `Access`, not a mock (2026-10-19 14:29, after
  August turned Studio API access on). Persistence tests use a Studio test
  profile (`ServerStorage.StudioProfile = "Test_..."`), never his own save.

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
- [x] Save and load by rejoining (14:32, test profile): $16,105, 7 shards, two
  residents, a gifted pass and `lastSeen` all came back after Stop and Play.

## Phase 2 (M2, the street)

- [x] The bus countdown shows under the HUD; `bus` (dev) brings it: guests step
  off at the west stop, staggered, and browse east with their wish lists.
- [x] A guest's **Pitch** prompt within reach toasts "+15% toward your hotel"
  and turns to "Pitched!".
- [x] At the lane's end each guest picks a hotel with a vacant room of its type
  (Slime, two Pumpkin Heads to plot 2) or leaves (Mummies, Witch: no room).
- [x] A rare guest on the next bus is announced to the street a bus ahead (a Midnight Bus's Mythic Grand Banshee, a Legendary Vampire Count).
- [x] A request appears over an occupied room; **Help** at the door (within
  10 studs) fulfils it and tips 10 s of pay; an unanswered one closes after 30 s.
- [x] The rating panel (★ Rating), opened by a click, shows the five bars (15:18).

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
- [x] Holiday gives Moon Shards (+8 for an Epic Werewolf).
- [x] Perks (04:14): a Grand Banshee resident makes income ×1.1; a Ghost adds 5
  Cleanliness to the rating's categories; each resident's perk shows in Residents.
- [x] Offline earnings on rejoin (14:32): away 155 s, Wing $15.22/s online; the till
  rose $259.50 → $1,418.25 at join, ≈ 50 % × 15.22 × ~145 s plus a few seconds online.

## Phase 4 (M4, progression)

- [x] A fresh profile starts Gloom at Build; each step closes by itself when
  done: build → the tutorial Slime arrives (walk-ins wait for it) → desk →
  till → second room → a pitch → the Slime moves in (1 friendship) → the goal
  card (Coffin Suite unlocked, one free) → clean → a staff job → the preview → Done.
- [x] The free Coffin Suite costs $0 and the scheduled Vampire Count walks in
  three buses after the goal card (04:24), needing the Legendary's 10 friendship.
- [x] Rebirth (dev-forced, $4M run): Frostfang Lodge, $100, 20 Moon Shards,
  residents and unlocked room types kept, the plot rebuilt in Frostfang colours.
- [x] Moon Tree: two nodes bought for 5 shards each; income ×1.1.
- [x] A Frostfang walk-in (Snowball Sprite) takes the Igloo Room.
- [!] Phone (iPhone 14 landscape, 749×388): the HUD columns started above the
  top bar, Gloom covered the screen, build tools overflowed the height. Fixed:
  columns under the top bar, Gloom narrower at top centre and hidden while
  building, tools in three columns top-left.
- [x] The phone layout seen again (04:07): the left column, the right menu in
  two columns above the jump button, Gloom's text fitting, a window over Gloom
  that fills the screen and scrolls.
- [ ] Rebirth through the panel's button when every requirement is met.

## Phase 5 (M5, live systems)

- [x] A product's grant through `grantOnce` (dev `receipt`): 2x Cash makes the
  income multiplier 2 and counts down in play time; a cash pack pays 10 minutes
  of income; **the same purchase id twice grants once**.
- [x] Three daily requests are drawn; login day 1 pays once a day; a code works
  once, a second try and an unknown code are refused.
- [x] The Store lists every pass and product with its price, "Soon" until its
  id exists, and the active boost's countdown.
- [!] Gloom's bubble vanished after a purchase: `PlayerData.publish` wrote the
  profile's "Start" over the tutorial's "Build". Fixed (the profile stores "Build").
- [A] A real purchase and a real rewarded ad: the ids are August's to create
  (WAITING §3), and Roblox's purchase prompt is CoreGui (his click).
- [x] The Daily panel by clicks (15:21): a reroll replaced a request and used the
  day's one; six collects, then **Claim** → Done ✔ and the reward paid.
- [!] The Daily panel did not move while open: progress is a stat, and a stat
  change sent no state. Fixed (`PlayerData.onStat`; DailyService marks the
  player when an open request's stat moves): 5/6 → 6/6 live.

## Phase 6 (M6, polish)

- [x] Hunter Night (dev `hunters`): two hunters per hotel walk in from the east
  with a countdown under the HUD; **Boo!** by the hunter's prompt at ~15 studs
  sends it running; a hunter at the door nets a guest (a guest before a
  resident); one of two through the door is not a defended night.
- [x] Every sound id loads in a playtest (`IsLoaded`, `TimeLength`).
- [x] A Slime Puddle in a lobby trap slot ($500, drawn at `Trap_1`) scared the
  first hunter at the door away, once.
- [x] The facade: rays pass the Wing doorway (x 32–40) at 1.5 and 5 studs and hit
  the wall beside it; a packed hotel with its facade is 1,205 parts.
- [x] LOD: a packed hotel's 174 beds, pillows and lamps (58 lights) hide when
  the camera is far and come back when it returns.
- [?] Boo! at ~35 studs (15:25): the server **accepts** it (a prompt triggered at
  35.0 studs counted `boos` 1 and the hunter left), so reach is not the fault.
  Repeats did not reach the server, with no refusal either, and
  `PromptShown` never fired even at 20 studs: whether the prompt shows on
  screen at 30–40 studs cannot be told through the MCP (focus, a moving
  hunter). Left for a person: does Boo! appear and work from ~35 studs?
- [x] A resident in the Hunter Camp (dev `camp`) is away from the Wing; the
  camp's prompt rescues it.
- [x] A defended night (dev `defend`): +5 minutes of income, +10 Candy, the
  thank-you bus called at once.
- [x] Settings by their remote: low graphics turns shadows off; music off stops it.

## Phase 8 (the afternoon's drafts: gifts, Winter, cosmetics)

- [x] A gift (dev `gift`) goes through a real ProfileStore message and arrives in
  under 8 s: `gifted` and `passes` hold it, and it survives a rejoin.
- [x] The Store shows a **🎁 Gift** button on each of the nine passes and no gift
  rows; a real click opens the picker ("Nobody else is on your street yet" alone).
- [ ] Gifting to a second player: needs **Server and Clients** (two players).
- [x] Winter by the event calendar (+60 days): Season "Winter", Snowflakes from
  zero, the Events button ❄; the Snowman bought for 30 (50 → 20) and unlocked.
- [x] Cosmetics by the `Equip` remote: Pumpkin sign at the Board's front face,
  Fairy lights at the Entrance, the Gothic facade's colours (45 walls, 3 trims);
  an unknown id refused.
- [x] The Style tool by clicks (15:18): the menu's three slots; Icicle sign
  equipped and drawn round the board, the text clear; worn cosmetics came back
  from the save.
- [!] Style's Sign and Facade rows ran past the panel's edge (six cosmetics in a
  row). Fixed: rows wrap (two lines, rightmost button 790 of 876 px).
- [ ] Pictures of the cosmetics with their models: after the next import.

## Phase 7 (social, GDD §7)

- [x] A ping shows over the player's head; the street leaderboard (Rating,
  Likes) is in the player list; a hotel's own Like prompt is hidden from its owner.
- [!] The Street Favourite badge reached the sign a step late and the Likes
  column did not follow likes. Fixed (`SocialService.likesChanged`).
- [x] The global board stands by the bus stop with its three lists; without
  DataStore access it says so. Its scores: [A] (WAITING §3.1).
- [A] Liking another hotel, the friend bonus: need two players (**Test → Start
  Test Session → Server and Clients**, his).

## Phase 9 (the real models, after the import)

- [x] The 69 synced models match the Workspace imports part for part (628
  parts: mesh ids, sizes, textures, collision, LOD_Proxy hidden, no empty
  MeshPart); every script's size matches git.
- [x] A hotel of all 13 Haunted Manor pieces on two floors (26 pieces) and three
  floors of stairs build from the real kit: no piece falls back to a blockout.
- [x] Rays down over every floor (650): no lid; every hit above the floor is the
  room's own bed, furniture or centrepiece.
- [!] Rays through every doorway (312): the lobby's `Desk` stands 1.8 studs and
  the corner `Planter`s 1.5 studs in front of floor-1 doors in columns 0, 3, 4
  and 11 (and the `Till` clips column 7 by half a stud). As in the blockout.
  A layout choice: WAITING §2.10.
- [x] A walker up both storeys of Haunted Manor's stairs and of Frostfang
  Lodge's (built by `HotelKit.stairs(2, ...)` beside the street, their mesh ids
  checked): every waypoint reached, no Climbing or Freefall.
- [x] Guests off the Night Bus, a resident and a hunter are the real models
  (Slime, Ghost, Mummy, Skeleton, Vampire Count, Pumpkin Head, Witch, Hunter;
  no empty mesh); the bus is the real NightBus with its headlamp.
- [x] Frostfang Lodge's eight rooms and amenities, built by `HotelKit.piece(id, 2)`
  beside the street: rays down (200) find no lid, rays through each doorway
  (96, at ±1.5 studs) pass, every Door faces −Z. Not yet in a plot (a rebirth).
- [x] No script error from the game. `rbxassetid://203785492` "does not match
  requested type" is Roblox's own: no instance in the place holds that id.
- Pictures: `archive/screens/2026-10-19_real_models_hotel.jpg`,
  `archive/screens/2026-10-19_real_models_bus.jpg`.

## Phase 10 (the lobby rework, layout A, after the import)

- [x] The 11 imports (both `Lobby`, both `HotelSign`, seven cosmetics) set,
  read back, saved and synced: every synced copy matches its import part for
  part, no empty MeshPart. Six synced templates came without `PrimaryPart`
  (Rojo's live sync, `DEVNOTES.md`): the plot failed to build until
  `HotelKit` set `Root` itself (fixed, run again, the plot builds).
- [x] Rays out through every floor-1 door that opens onto the lobby (doors at
  x −33, −21, −9, 3, 15; 60 rays, 6.5 studs out at four heights): no hit. Rays
  along the whole back row (z 7.5, 9.5, 11.5 at 1, 3, 5 studs): no hit.
- [x] A walker (the player's avatar, 5 studs): street → threshold → inside →
  `Queue_1` at the desk → the back row → the `Clerk` behind the counter, every
  waypoint reached, no Climbing or Freefall.
- [x] Guests queue along the carpet at the desk; the sign stands at the
  forecourt's stair-side corner, its text drawn (seen from above).
- [ ] The in-game blind review: paused. August, 2026-10-19, in the game: "its
  a bit cramped. Could probably double everything just about. The roof is
  also a couple studs above the walls, not connected." The rooms' walls stop
  1 stud under the slab above (walls 10, clear height 11). Waits on his
  answer on the scale (WAITING §2.12).

## Phase 11 (the doubled scale, after the import)

His ruling, 2026-10-19 evening: 12-stud cells, 18-stud floors, walls up to
the slab (`CLAUDE.md`, "The scale of a person"; `MODELS.md`, "Hotel kit").

- [x] The 27 rescaled imports (both kits' rooms, amenities, `Lobby`,
  `StairCore`, `StairCoreTop`) set, read back (Box on every mesh, no
  Default, Root and proxy hidden, attachments made), saved and synced: 27/27
  synced copies match their imports (meshes, sizes, textures, collision), a
  `PrimaryPart` and attachments on each, no empty MeshPart.
- [x] A three-floor hotel built from the kit (`fill CoffinSuite`, 24 suites,
  test profile `Test_Scale1019`): every wall below the top floor meets the
  slab above (84/84, a ray up from each wall's top hits it within 0.05); the
  top floor's 60 walls stand open.
- [ ] Rays out through every door (24 doors, 288 rays at 1, 3, 5, 6.5 studs)
  and along the lobby's back row (9 rays): one door blocked. Coffin Suite at
  cells x 9–11, z 4–6 on floor 1 opens straight onto the stair core's back
  wall: `Grid` counts the core's cells as walkable from every side, but the
  core is walled at the back and sides. Not the rescale's (the grid logic is
  per cell). The back row: clear (only the avatar). **Fixed in `Grid`
  (2026-10-19):** the core's cells are no hallway, entered only across its
  front (the lobby's back row, the landing above); a door onto its back or
  side is refused as `DoorBlocked`. Specs (`tests/grid.spec.luau`, two new
  and the random layouts' paths kept out of the core): 9/0 in Studio's Edit
  datamodel on cloned modules, 6/3 with the old rule. Not yet in a playtest:
  the rays again, on a profile without that suite (a saved door onto the core
  now refuses every placement on its floor as `CutsOff`).
- [x] Walkers (the 5-stud avatar): street → threshold → `Queue_1` → the back
  row → `Clerk` → the core → up both storeys (15 steps each) → and back down:
  every waypoint reached, no Climbing or Freefall.
- [x] A guest (Vampire Count) to a floor-2 room: its path runs `Bottom` →
  `Path_1` → `Path_2` → `Top` → its door. On floor 2 the path crosses the
  stair core's cells (the same grid gap as the door above): the guest glides
  through the floor-2 flight. Fixed with the door: `Grid.path` goes round
  the core (spec). Not yet seen: a guest to a floor-2 room behind the core.
- [x] The build camera frames the 144-stud plot; a Standard Room's ghost is
  23.6 studs square on its four cells, its door marker over the cell in front.
- [x] The in-game blind review (street, raised, lobby, a room, the stairs;
  the desk's picture was lost when the playtest ended) and its triage
  (Haunted Manor README). The first review's open findings: 2 the sign's text
  draws, seen from the raised camera (straight-ahead still to see); 4 the
  stair's top is no longer a void, it is the open top floor (no roof, his);
  7 the "red slivers": the down flight's handrail standing up through the
  floor above, fixed; 8 the pale rectangle is the place's own
  `SpawnLocation` in the middle of the street (WAITING §2.13); 10 not seen.
- [x] The 25 re-staged models (rooms' jambs, the stairs' handrail) imported,
  set, read back, saved and synced (25/25 meshes, sizes, collision and
  textures match; six synced copies without `PrimaryPart`, which `HotelKit`
  sets itself). Every stair core's dressing now tops out at 17.85, under the
  upper floor (18): the handrail no longer stands through it.
- [x] The jambs and the street lamps seen in a playtest: lamps at ±15 from
  each entrance (x −15, 15, 165, 195 ...), a pair flanking the arch; the
  jamb trim stops where the arch springs. From the street straight ahead the
  sign's text draws (the first review's finding 2, closed).

## Phase 12 (free building, GDD §5.4, after the merge and the import)

Built on branch `claude/free-building-4b66e3` (2026-10-19) and verified
there only by stylua, selene, `rojo build`, luau-lsp against main's
baseline, the Blender validators and the pure specs under Lune (64 pass,
`tools/run_specs.luau`). **Nothing below has run in Studio.** Play it on a
fresh test profile (`Test_Free1019`): the schema step (version 2) builds every
saved hotel again from the start area.

- [ ] The specs in Studio (`tools/test_bundle.py`), `data` among them.
- [ ] A new hotel: the lobby shell, the `FrontDesk` at the lobby's −X end
  served toward +X, the start area (cells x 4–7, z 2–6) open and the five
  other areas under their plates on every floor; the spawn clear.
- [ ] The desk's points mirrored on the lobby: the tutorial's arrow at the
  desk, the Front Desk resident at `Clerk`, the queue in front of the desk,
  the check-in and collect prompts on the desk.
- [ ] Build mode: the Rooms, Amenities, Stairs, Decor and Floors tabs; a room
  refused on a closed area (`Area`), in the lobby (`Lobby`), on the entrance;
  2–4 Standard Rooms fit the start area.
- [ ] Areas: the labels over the closed areas on the floor in view; a tap on
  one offers it at its price; bought, its plates go on every floor; a back
  area refused until one beside it is owned.
- [ ] A floor bought: the Stairs tab says one is free; placed in the start
  area for $0; the slab above opens over it with its lip; walked up and
  down; a second stair costs; the last stair to a floor with a room refused
  for sale (`CutsOff`); a stair stacked on another continues it (StairCore
  below, StairCoreTop above).
- [ ] A guest to a room on floor 2 and floor 3: up the placed stairs (glide
  Bottom → Path_n → Top), to the door, to the bed; and back out at checkout.
- [ ] The desk moved (tap it, Move): the queue, the prompts, the clerk and
  the tutorial's arrow follow; a desk where the entrance can't reach it is
  refused.
- [ ] Decor: placed in a room on the 3-stud grid, turned with R; refused in
  the doorway, on the bed, across a wall; a Bookshelf only against a wall; a
  rug under an armchair; the room's plaque shows T2 at 100 points (T3 at 300
  for a 2×2); its tags meet a guest's preferences; a room moved carries its
  decor; a room sold sells its decor.
- [ ] Hallway decor: a bench in a cell's corner leaves the cell walkable; one
  across a cell's middle that would cut a door off refused; nothing in the
  entrance's mouth but a rug.
- [ ] Floors: a finish laid on a room, the lobby and the hallways; "Its own
  floor" brings the model's back.
- [ ] Rays and walkers as in phase 11 over a hotel of placed stairs (`fill`).

## August keeps

- How the street, the lobby and the rooms look (every look is a night draft).
- Whether the build camera and the piece strip feel right with a mouse and a thumb.

## Log

- 2026-10-19 03:20 T0 and Phase 1 items 1–8 pass (the night's playtest), commit `daf7ffa`.
- 2026-10-19 03:27 Phase 2 items 1–3 pass.
- 2026-10-19 03:32 Phase 3 items 1–4 pass; two client bugs fixed.
- 2026-10-19 03:40 Phase 4 items 1–5 pass; the phone layout fixed.
- 2026-10-19 03:45 Phase 5 items 1–3 pass; Gloom's disappearing bubble fixed.
- 2026-10-19 03:50 Phase 6 items 1–2 pass.
- 2026-10-19 04:11 Facade, rare check-in moment pass.
- 2026-10-19 04:04 Traps pass.
- 2026-10-19 04:01 Leftovers: announcement, Help, holiday, camp, defended night, settings pass.
- 2026-10-19 03:24 Stairs: the first landing (2 studs) jammed a walker; widened to 4, both storeys walked up and down.
- 2026-10-19 15:33 Phase 9: the real models synced, built, rayed and walked; the lobby desk in front of floor-1 doors to WAITING §2.10.
- 2026-10-19 15:34 Phase 9: Frostfang's rooms rayed beside the street, all clear.
- 2026-10-19 17:55 Phase 10: the new lobby imported, rayed and walked; PrimaryPart lost by Rojo's live sync, fixed in HotelKit; the in-game review paused for his scale question.
- 2026-10-19 night Phase 11: the doubled scale imported (27), walls meet the slab, walked up and down three floors, a guest up the stairs; a door onto the stair core's back and guests through the core on floor 2 (grid, follow-up); the in-game review's handrail, jambs and lamps fixed, 25 re-staged.
