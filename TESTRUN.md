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

## Launch run (LAUNCH.md #11, his ask 2026-10-23)

**Until launch this section is the order**: run it before anything below. It
gathers every open item below into what can run unattended, by what a session
needs set up. Each line names its original by section; mark both the same way,
one log line. Three parts, in order: two players (he starts it), alone (Claude
restarts freely), after Publish (a real server, him awake). Looks and values
that are his are not in the night: they stay `[A]` where they stand below.

### The night guard

Read before the first call, and again after any error.

- **Studio has one user.** Take `.locks/studio` (LAUNCH.md, "How the work
  runs") before the first MCP call. While another session holds it, he does
  not start Server and Clients and nothing here starts. Never while he is
  importing.
- **The two-player session is started by him and cannot be started again
  tonight** (`start_stop_play` cannot start it; only he can add a client).
  While its windows are open:
  - never `start_stop_play`, in any window;
  - never touch a playing player's profile from another datamodel (an Edit
    `execute_luau` loading ProfileStore, another Studio): the session lock
    kicks the player ("Your save data was opened elsewhere", `PlayerData`);
  - a fix found here is committed but not re-run here: its re-run goes to
    part 2, or to the morning as `[A]` if it needs two players;
  - the one leave (`Player:Kick`) is the part's last item.
- **`DevCommand` acts on the first player only** (`DevGrant`:
  `Players:GetPlayers()[1]`). Player 2 gets cash, guests and residents from a
  Script parented in the running server that calls the services on that player
  (it shares the game's modules), or does things itself by its own remotes
  from its client's `execute_luau`. Each client is its own Studio in
  `list_roblox_studios`: tell them apart by `Players.LocalPlayer.UserId`.
- **Closing the two-player session**: stopping play leaves the windows. Close
  the `Server` and client windows by their process titles and keep the edit
  window (skill `playtest`, "Two players"); then part 2.
- **Alone, restarts are free**: `start_stop_play` as often as an item needs, a
  fresh profile per group (`ServerStorage.StudioProfile = "Test_Launch<date><x>"`
  before Play), the device simulator set before Play and stopped after. A stop
  is a logout: grant again after it.
- **When Studio dies, hangs, or needs a Connect or a Rojo restart**: retry the
  call once; then log it, write it in `WAITING.md` §0 (in Swedish), release
  the lock, and go on with work that needs no Studio. Never restart Rojo,
  never Publish, never change a value to make an item pass (a number that
  disagrees is a finding for `WAITING.md`).
- **An item that cannot run this way** is marked `[?]` with why, and the run
  goes on. Nothing here waits on him.
- **Studio in front** only while he sleeps (`CLAUDE.md`); items marked
  *front* need it. No heavy renders while Studio runs.
- **Commit and push after each group**, so a session that dies is picked up at
  the first unmarked line here. Usage and the 5-hour window: skill
  `night-sprint`.

### 1. Two players (his start: Test → Start Test Session → Server and Clients, 2 clients)

Same street first, then two streets, then the leave.

- [ ] T0 for this session: both clients and the server answer
  `execute_luau`, the sync landed (`tools/sync_sizes.py`), the console is
  clean; player 2 has cash from a server Script (the guard).
- [ ] Gifting to a second player (Phase 8).
- [ ] Liking another hotel (Phase 7). The friend bonus only if the test
  players count as friends; otherwise that half is `[?]`.
- [ ] A second player visiting sees the staff walk and the "✓" (Staff at work).
- [ ] The showcase with two (The showcase): a real like and the 10-minute
  rule's refusal, the giver's toast, **Visit**, walking into the other lobby
  counting toward the daily, the weekly favourite moving between the hotels.
- [ ] Two players seeing another's VIP (VIP contracts, the room view's item).
- [ ] Two players on two streets at once, each street's bus and Hunter Night
  (The world).
- [ ] **Last:** player 2 leaves (`Player:Kick` from the server): its hotel
  leaves the street, the plot is free, its profile is saved and released (read
  on the Server after the kick). The rejoin is not tried (his click): part 2
  proves persistence.
- [ ] The windows closed (the guard).

### 2. Alone (Claude starts and stops)

**a. Launch's own**

- [x] Persistence: build, earn, stop, Play again on the same profile: the
  hotel, cash and residents are back. (2026-10-24 night, `Test_Launch1024b`:
  Bayou, 2 floors, the stair, 6 decor, 15 walls, 8 residents, cash back.)
- [A] No "server size" warning on Play (Pacing; Server Size is 10). (2026-10-24
  night: Studio's place still says `MaxPlayers` 60 and warns on every Play;
  Creator Hub's 10 is not in the open Studio copy. WAITING §4.)
- [x] Bayou Spa's kit and facade and the VIP lounge set in the game (LAUNCH
  #5): at `chainopen 3`, Bayou's walls, door, posts, desk, furniture, decor,
  stairs and facade are kit clones; the VIP lounge decor placed (`pass`).
  (2026-10-24 night: every one by MeshId from `HotelKit.BayouSpa`, the five
  VIP pieces from the lounge set; `archive/screens/2026-10-24_bayou_stairs_vip.jpg`.)
- [x] Each facade pack's facade on the hotel when owned (`cosmetic`).
  (2026-10-24 night: Gothic, Neon, Candy, Pirate equipped in turn, the walls
  each its pack's `Facade_Wall` mesh, 43 facade parts.)
- [?] F on the imported kit rooms and amenities: each has its `_Mirror` (Flip).
  (Flip was removed with built rooms, "Removed: Flip" below.)
- [ ] Bookshelf and Wardrobe placed (Launch import): why the test's positions
  placed nothing.
- [x] Notifications: `notify` queues and logs "would send" (the real send is
  part 3). (2026-10-24 night: one for the player in the game is dropped, as it
  should; one for another user logs "would send TillFull to 1 (not set up)".)
- [x] The rigged monsters (LAUNCH #6), once imported, not before: each body
  shape walks, idles, is happy and sad, checks in and works as staff; a Tiny
  and a Giant; no error. (2026-10-24 night, after the import: all five shapes'
  bones turn within the radius (3–5 a model in 1.5 s), a guest walks, Tiny and
  Giant scale; a warning per part fixed (`MonsterAnimator`'s welds); happy,
  sad, check-in and staff were proved on the Skeleton 2026-10-23 and not run
  again per shape; how they look is his, `archive/screens/2026-10-24_rigged_residents.jpg`.)

**b. Build mode on a fresh hotel** (*front* where a click or key is real)

- [ ] Phase 13, its eight open items: the tabs and refusals, areas, a floor
  and its stairs, a guest to floors 2 and 3, decor, hallway decor, floors, rays
  and walkers over placed stairs (`fill`).
- [x] Phase 11: rays out through every door, on a profile without a door onto
  the stair core. (2026-10-24 night, `Test_Launch1024e`, built rooms: no stair
  core any more; at each location a person-sized box (3 × 6.5) through the
  start room's door touches no colliding part, and through each of the 9
  plain walls always does, in all three kits.)
- [ ] Gamepad navigation: the keyboard item (B, R, `,` `.`, the chat;
  *front*), every window's selection, build mode with the gamepad last.
- [ ] Built rooms, stage 3: a gamepad's A and a two-finger pan cannot be sent:
  mark both `[?]`.

**c. Rating**

- [ ] Rating: staff coverage and cleaning on time, its five open items.

**d. A new player**

- [x] Phase 12: no walk-ins without a bus; the tutorial's Slime and Vampire
  Count. (2026-10-24 night, `Test_Launch1024c`: the Slime on a fresh profile,
  source Tutorial, before any bus; 30 s with two rooms vacant and no bus: no
  guest; goal card at bus 1, the Vampire Count added at bus 3 and riding bus
  4, booked to the Coffin Suite, straight to the hotel `ToHotel`.)
- [ ] Tutorial Commons: the weighting's stops; the ping menu's three cases.
- [?] Built rooms, stage 1–2: Collect, on a profile without Auto Collect.
  (2026-10-24 night: a fresh `Test_` profile still owns his passes, Auto
  Collect among them; it needs an account without it, part 3.)

**e. Phone** (simulator before Play: `iphone_14` landscape, then
`ipad_10th_generation`)

- [x] Phase 12: frame time with the forest and a full bus, against phase 11's.
  (2026-10-24 night, iPhone 14 simulated on his PC, the forest and a bus:
  16.7 ms a frame on average, 19.8 at worst, at the 60 fps cap; a PC's
  number, not a phone's: his phone is part 3.)
- [x] The free build camera: one finger pans (pinch cannot be sent: `[?]`).
  (2026-10-24 night: a 120 px touch drag moved the camera 36 studs. Found:
  build mode's tools and the HUD's right menu cover the strip on a phone,
  `archive/screens/2026-10-24_phone_build_overlap.jpg`: WAITING §1.14.)
- [A] VIP contracts: the room view's layout on a phone. (Not run in the night;
  the room view on a phone is already his, Built rooms "[A] How the room view
  looks on a phone", and the build mode's phone layout is WAITING §1.14.)

**f. Pictures** (*front*; each set to a blind review before he sees it)

- [ ] Launch import: the placed models.
- [ ] Phase 8: the cosmetics with their models.
- [ ] Phase 12: the in-game blind review of the street. It replaces Phase
  10's, which waited on the scale (answered 2026-10-19): mark that one with it.
- [ ] Phase 12, the forest: low graphics, a Frostfang plot's band.
- [ ] Rare decor: the Decor tab's cards, the set line, **Place it**, the Book's
  mark, clicked.
- [ ] VIP contracts: the desk's "VIP ledger" prompt by F.
- [ ] Phase 6: Boo! from about 35 studs, by a real key.

**g. Long runs, last, as the night allows**

- [ ] The hotel chain: a real run toward 5★ against his times.
- [ ] Residents level up: the cap in a real run, a level's staff effect.
- [ ] Deeper mutations: a stacked guest off a real bus, its pay and
  announcement.

### 3. After Publish (his Publish; a real server, him awake)

- [ ] `DevCommand` does nothing on a published server: no command
  registered, `DevResult` never set.
- [ ] The live store: a published server writes `MonsterHotel_Live_*`
  (`StoreNames`), and no `Test_` key is there.
- [ ] A notification really sent (after his key, `WAITING.md` §3.3).
- [ ] A real purchase and a real rewarded ad (Phase 5, his click).
- [ ] His 15 minutes on his own phone (`WAITING.md` §4).
- [ ] A real controller, if he has one (Gamepad navigation's three `[A]`).

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
- [x] (2026-10-19 21:09, `Test_Menu1019`, by mouse clicks in build mode: a click on a room opened its menu (Move, "Sell +$28"); Sell removed it and paid; Move, then a click on a free spot, moved it (no cost). Upgrade is gone from the menu since tiers come from decor (phase 13); decorating is the Decor tab.) Upgrade, decorate, move and sell from the piece menu, by clicks.
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
- [!] The phone again (2026-10-19 evening, iPhone 14 landscape, 749×388, every
  panel opened in turn): seven fit. The Residents rows' role buttons ran past
  the panel's right edge (Security and Holiday at x 692–910 of 34–714), and the
  Ping menu's six rows (316 px) ran below the screen. Fixed: the eight buttons
  share the row's width with their text shrinking to fit (14 at most, never
  broken mid-word), and the Ping menu takes two columns on a short screen
  (bottom at 280 of 388). Picture: `archive/screens/2026-10-19_phone_residents.jpg`.
- [x] Rebirth through the panel's button when every requirement is met
  (2026-10-19 20:03, test profile `Test_Eve1019a`: 4★ by the game's rating sums over
  inputs set by a Studio helper Script (27 suites put at tier 3, 30 five-star
  reviews) plus four real check-ins, $5M run, a Vampire Count; the Moon button, then **Move now: +24 Moon
  Shards** clicked: Frostfang Lodge, 24 shards, 1 move, $100, no pieces, all 6
  residents kept).

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
  (96, at ±1.5 studs) pass, every Door faces −Z. In a plot after the panel's rebirth (2026-10-19 evening):
  `fill IglooRoom`, 43 pieces on 3 floors, 812 MeshParts all from Frostfang's
  kit, none empty; Snowball Sprite and Ice Imp walked into Igloo Rooms on
  floors 2 and 3 (the floor-3 walk took about 70 s).
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

## Staff at work (GDD §4.6 "Staff are seen working", Appendix A.5; after the merge)

Merged into main 2026-10-19 19:52 and played 19:55–19:58 (the evening's loop,
`archive/NATTLOGG-2026-10-19-kväll.md`). Played again once free building is in, with free building's placed stairs and movable desk
in too, since the errand reads the posts from the lobby's attachments and the
way from `GuestService.pathToDoor`.

- [x] The staff spec: `python tools/test_bundle.py staff`, then the bundle in
  the Server datamodel: all pass.
- [x] A Room Service resident (`DevCommand` `resident Slime`, assigned in the
  panel), a guest on floor 1 and `request`: the resident leaves its post at
  once, walks the hallway to the door, stands outside it facing in and
  knocks; "✓ Room Service" rises at the door when the request closes; it
  walks back to its post. The request closes no sooner than 12 s ÷ its
  efficiency after it opened (server log or a stopwatch).
- [!] (2026-10-19 21:06, `Test_Floor3_1019`, `fill StandardRoom`: the resident set off for room 43 on floor 3 by the placed stairs (its path up to y 37), but the path was 1,445 studs, so the request ran out first and it turned back after 24 s. Not fixed: the walk speed and the request's time are his, WAITING §2.29.) The same for a room on floor 3: up both flights by the guests' stairs,
  through no wall or slab (rays along `Path`); a long walk ends the job 2 s
  after it reaches the door, before the request's 30 s run out.
- [x] Housekeeping: a checkout leaves a dirty room; the resident walks to it,
  "✓ Housekeeping" rises when the room turns clean, and it walks back.
- [x] (Closed by the guest's checkout, not by the player.) Answered first: answer the request (or clean the room) yourself while
  the resident is on its way: it turns round where it stands, no "✓".
- [x] Two requests and one Room Service: it serves the older first, walks
  back, then takes the other. Two Room Service residents serve both at once,
  each from its own post (`Slot` 1 and 2 side by side).
- [x] Reassigned mid-errand (to Front Desk, or back to the Wing): it is at
  its new post at once, nothing left walking.
- [x] (At its post at once; check-in by Front Desk not watched.) Front Desk stays behind the desk and checks guests in; Bellhop,
  Entertainment and Security stay at their posts.
- [A] (Two players need his Test → Start Test Session.) A second player visiting sees the walk and the "✓" too.
- [x] Studio's output: no `[residents] tick failed`.

## Phase 12 (the street: forecourt, Night Bus, forest; after the merge)

Built on `claude/street-bus-forest-253849` (GDD §3, §4.3, §5.4, A.1, A.3).
Verified there by stylua, selene, `rojo build` and the specs under Lune
(`bus`, `street` and the other pure specs; `data` needs Studio); **nothing of
it has run in Studio.** Needs August's Rojo restart first (the
`assets/Scenery` mapping, WAITING §0 punkt 8). Merged into main 2026-10-19
20:27 and played 20:27–20:33 (test profile `Test_Street1019`) before the
restart: every script synced (72/72); only the empty `Scenery` folder was
missing, and the forest reads it by `FindFirstChild`, so the blockout trees
drew as they would with it empty.

- [x] (After his restart, 2026-10-19 evening: `Scenery` holds the five trees, each with Root as PrimaryPart and a LOD_Proxy, no empty MeshPart.) The sync landed (`tools/sync_sizes.py`), `ReplicatedStorage.Scenery`
  exists; the spec bundle passes in a playtest, `street` and `data` included.
- [x] (Rays every 2 studs over x −70..70, z −6..64 on plot 2: no miss; lane,
  pavement, yard 1.00, path 1.05, the kerb 1.30; a 0.5 edging along the
  pavement either side of the path, as built. A walker lane → arch, no climb
  or fall.) The forecourt: plot fronts at z = ±48; the pavements one strip along
  each lane edge; each plot's yard with the path to the arch; the sign at the
  stair-side corner (not in front of the entrance); a bought trap drawn
  beside the path. Rays down over the lane, pavement, yard and path find a
  floor at y = 1 everywhere, no gap and no step but the kerb; a walker goes
  lane → pavement → path → arch.
- [x] (A Slime Puddle in Trap_1 at (−8, 36); the first hunter fled ~7 s before
  it arrived, the second came on: one scare a night.) Hunter Night: a hunter walks up the path and a trap beside it scares it.
- [x] (Sampled every 0.5 s: in at x −266 on z 15, stops at x −95 and 85, east
  bend to z −234 at x 358; its box never touched anything but the road.) The bus comes out of the trees north-west of the street, round the
  west bend onto the lane's north half, stops with its door at x = −90, then
  at x = 90, and goes round the east bend into the trees; it never passes
  through the leaderboard, the Hunter Camp, a lamp or a shelter (sample its
  box along the drive). Call the Bus brings it in out of the forest.
- [x] (Two at each stop; Browsing about a minute, then ToHotel and Queued.
  Pitch not pressed.) Half the guests step off at each stop; each browses the pavements
  (north and south, east and west in turn), stepping toward each owned
  hotel's entrance and looking about 2 s; **Pitch** works the whole minute;
  then it walks across the lane if needed, along the pavement and up the path
  to its pick's desk queue.
- [x] (A Pumpkin Head and a Witch with only Standard Rooms on the street:
  Leaving → Waiting at (87.6, 26.2) and (85.2, 26.2) on the north pavement
  → Boarding the next bus and gone.) A guest no hotel takes, one that gave up at the desk and one that
  checked out all walk to the nearest stop and wait on the pavement; the next
  bus at that stop takes them. Nobody walks off the end of the lane.
- [x] (`nextbus` said two, four came for one player.) The bus's size: `nextbus` before an arrival and the guests counted
  after it: 40 % of the street's Vacant rooms rounded up, 2–4 per player.
- [ ] (No walk-in seen in ~2 minutes with 43 vacant rooms; the tutorial's
  Slime and Vampire Count wait for the new-player run.) No walk-ins: with rooms vacant and no bus, no guest appears. The
  tutorial's Slime walks in from the pavement about 6 s after the first room,
  before the first bus; the Vampire Count rides the third bus after the goal
  card, booked, and walks straight to the hotel.
- [ ] (After the import and his restart: all 677 are the models, 2,279
  MeshParts (the blockouts were 3,385 parts), 692 drawn: 646 far trees as
  their proxy, 46 near ones whole; a walker into a bare tree's trunk kept
  2.41 studs from its centre and slid round it. Low graphics and a
  Frostfang band not tried. Before: 677 blockout trees: 240 crooked, 241 bare, 26 hollow, 170 firs; none on
  a plot, yard, lane or pavement (the three nearest stand in the gap between
  plots 5 and 6 and past the lane's ends, only the Baseplate near). Models,
  proxies, low graphics and Frostfang's band wait for the import.) The forest: trees all round, none on a plot, its forecourt or Wing, the
  lane, the pavements or the road; blockouts before the import, the models
  after (§0 punkt 8). A person walks into a bare tree's trunk and stops at a
  fir's lowest tier; trees beyond 260 studs are their proxies; low graphics
  draws about half; a Frostfang plot's band is snowy firs; every hollow tree
  faces the street.
- [ ] Performance on the phone emulation (the forest, a full bus browsing):
  frame time against phase 11's.
- [ ] The in-game blind review (skill `blind-review`): the street at eye
  height, the raised camera over a forecourt, the bus at a stop with guests
  stepping off, the forest's edge behind the plots and at a bend.

## Phase 13 (free building, GDD §5.4, after the merge and the import)

Built on branch `claude/free-building-4b66e3` (2026-10-19) and verified
there only by stylua, selene, `rojo build`, luau-lsp against main's
baseline, the Blender validators and the pure specs under Lune (64 pass,
`tools/run_specs.luau`). **Nothing below has run in Studio.** Play it on a
fresh test profile (`Test_Free1019`): the schema step (version 2) builds every
saved hotel again from the start area. Merged into main 2026-10-19 20:36 and
played 20:37–20:42 by the game's remotes **before the import** (the old lobby,
desk and all, stood beside the new `FrontDesk` piece until August imports,
WAITING §0.9): what needs the new models or the build menu's clicks stays open.

- [x] (All 14 files, 90/90.) The specs in Studio (`tools/test_bundle.py`), `data` among them.
- [x] (2026-10-19 22:35 after the import, `Test_FreeImp1019`: the lobby is the shell (floor, front walls, arch, lamps), the desk its own piece (counter, key rack, till); no empty MeshPart; rays over the lobby find the ground at one height but for the counter; a walker street → arch → queue → spawn, no climb or fall. The closed areas' plates not looked at.) A new hotel: the lobby shell, the `FrontDesk` at the lobby's −X end
  served toward +X, the start area (cells x 4–7, z 2–6) open and the five
  other areas under their plates on every floor; the spawn clear.
- [x] (Before the move: Clerk (−68, 60), Queue_1 (−58, 60), Desk (−62, 60); the
  tutorial's arrow and the prompts not looked at.) The desk's points mirrored on the lobby: the tutorial's arrow at the
  desk, the Front Desk resident at `Clerk`, the queue in front of the desk,
  the check-in and collect prompts on the desk.
- [ ] (By the remote: refused `Area` on a closed area, `Lobby` in the lobby,
  `DoorBlocked` and `DoorUnreachable` behind two front rooms, `Cash` when
  short; two Standard Rooms fit the front of the start area. The tabs are
  the menu's, not clicked.) Build mode: the Rooms, Amenities, Stairs, Decor and Floors tabs; a room
  refused on a closed area (`Area`), in the lobby (`Lobby`), on the entrance;
  2–4 Standard Rooms fit the start area.
- [ ] (By the remote: area 5 behind the start area $1000, area 3 beside it
  $3000. Labels and the tap not seen.) Areas: the labels over the closed areas on the floor in view; a tap on
  one offers it at its price; bought, its plates go on every floor; a back
  area refused until one beside it is owned.
- [ ] (Floor 2 bought; a stair at (8, 2) for $0; a walker up its glide
  (30, 1, 72) → landing y 10.6 → (42, 19, 72) and along floor 2's hallway,
  no climb or fall. A second stair's price and `CutsOff` not tried.) A floor bought: the Stairs tab says one is free; placed in the start
  area for $0; the slab above opens over it with its lip; walked up and
  down; a second stair costs; the last stair to a floor with a room refused
  for sale (`CutsOff`); a stair stacked on another continues it (StairCore
  below, StairCoreTop above).
- [ ] (Floor 2: two Skeletons' paths up the placed stair's glide to their
  doors at y 19, and one to floor 1. Floor 3 not built.) A guest to a room on floor 2 and floor 3: up the placed stairs (glide
  Bottom → Path_n → Top), to the door, to the bed; and back out at checkout.
- [x] (By the remote, `Move` to (10, 0) r3: Clerk (56, 60), Queue_1 (46, 60),
  Desk (50, 60) followed; the tap and the arrow not seen.) The desk moved (tap it, Move): the queue, the prompts, the clerk and
  the tutorial's arrow follow; a desk where the entrance can't reach it is
  refused.
- [ ] (Candles at square (18, 11) in a room for $40; refused `Doorway` at
  (17, 8). The rest open.) Decor: placed in a room on the 3-stud grid, turned with R; refused in
  the doorway, on the bed, across a wall; a Bookshelf only against a wall; a
  rug under an armchair; the room's plaque shows T2 at 100 points (T3 at 300
  for a 2×2); its tags meet a guest's preferences; a room moved carries its
  decor; a room sold sells its decor.
- [ ] Hallway decor: a bench in a cell's corner leaves the cell walkable; one
  across a cell's middle that would cut a door off refused; nothing in the
  entrance's mouth but a rug.
- [ ] (Oak Boards on a room and the hallways, Dark Boards on the lobby,
  accepted; not looked at.) Floors: a finish laid on a room, the lobby and the hallways; "Its own
  floor" brings the model's back.
- [ ] Rays and walkers as in phase 11 over a hotel of placed stairs (`fill`).

## Rating: staff coverage and cleaning on time (GDD §5.3, Appendix A.4; after the merge)

Built on its own branch, specs only (`lune run tools/run_specs.luau . rating
stay economy`). Merged 2026-10-19 20:50 and played (test profile
`Test_Rate1019`, two Standard Rooms, two check-ins). Read the categories from the plot's
`Categories` attribute (recomputed every 5 s) or the rating panel.

- [x] (Service 64.4, Cleanliness 100.) A hotel with rooms and stays but no staff: Service and Cleanliness the
  same as before the merge (nothing added without staff or cleanings).
- [x] (Skeleton at 100 %: 64.4 → 74.4; back to the Wing: 64.4.) Assign a Front Desk resident: Service rises by up to 10 (6 for a
  resident at 60 %) within 5 s; unassign it and it falls back.
- [ ] (Two rooms: a Slime added +10, 74.4 → 84.4; the 8-room half not tried.) Room Service in a hotel of 4 rooms: up to +10 Service; with 8 rooms the
  same resident gives half of that.
- [ ] Housekeeping in a hotel of 4 rooms: up to +10 Cleanliness; Service and
  the other categories unchanged by it.
- [ ] Clean a dirty room by hand within 40 s, several times: Cleanliness
  rises toward +10 (on-time share). Leave a room dirty past 40 s: the share
  drops at once (an overdue room counts late before it is cleaned).
- [ ] Nobody stayed yet (a fresh hotel) with staff assigned: Service stays 0;
  no rooms: Cleanliness 0 but for perks.
- [ ] Every category stays within 0–100 with many staff (`DevGrant resident`)
  and perks; the stars move by at most the categories' share.

## Tutorial Commons and the named ping (GDD §11 1:45, §7; after the merge)

Built on `worktree-agent-af840fbd28a857dd3` (GDD Appendix A.7, WAITING
§2.25). Verified there by stylua, selene, `rojo build` and the pure specs
under Lune (`bus`, `scoring` and the rest, 86/86). Merged 2026-10-19 20:51 and
played 20:52–20:56 on fresh profiles `Test_Tut1019b`/`c` through the
tutorial's first steps by the game's own prompts and remotes.

- [x] (All 14 files, 97/97.) The spec bundle passes in a playtest, `bus` and `scoring` included.
- [x] (One room for $50: the Slime walked in ~5 s later, queued at ~19 s; checked
  in by the desk's prompt; Collect by the HUD; a second room at SecondRoom;
  the bus then: drawn "Skeleton, Werewolf", arrived Skeleton and Slime, the
  size unchanged; the Skeleton picked this hotel's room 3. Pitch and a second
  player's 4★ hotel not tried. **Found:** the tutorial's Slime gave up at
  the desk after 60 s like any guest (a 1★ review, the CheckIn step stuck
  until a bus); fixed: the tutorial's guest never gives up at the desk, seen
  queued 70 s.) A fresh profile (`DevCommand tutorial Build`): build two Standard
  Rooms, check the Slime in; the next bus (`bus`) carries up to 2 Commons
  that take a Standard Room (`nextbus` before it shows the drawn list; the
  Commons replace its tail at arrival), the bus's size unchanged, its Epic or
  Legendary still aboard. They browse, can be pitched, and pick the new hotel
  (with a second player's 4★ hotel vacant beside it, most of the time).
- [ ] The weighting stops after 2 such buses (`data`: `tutorialCommonBuses`
  2) and on Skip; it never starts while the step is Build or CheckIn (the
  Slime keeps its room); a hotel with only a Coffin Suite vacant gets none.
- [ ] (With a Vampire Count announced: "Need a Coffin Suite!" over the head.
  The browsing and empty-street cases not tried.) The ping menu's "Need a room": with a Vampire Count announced
  (`legendary`), it reads "Need a Coffin Suite!" over the head; with Commons
  browsing and nothing announced, the room the rarest of them wants ("Need an
  Attic Room!" for a Ghost); with the street empty, "Need a room for that
  guest!".

## Gamepad navigation (GDD §11, after the merge)

Built on branch `claude/gamepad-navigation` (2026-10-19): `Controls.luau`
(input actions, panels, ButtonB and ButtonY), every `Ui.window` and the Ping
menu as panels, the HUD's keys and build mode's keys as input actions, a
cursor on the plot for build mode (UI.md "Gamepad"). Verified there only by
stylua, selene, `rojo build` and the pure specs under Lune. Merged
2026-10-19 21:01 and the keyboard items played (test profile
`Test_Pad1019`). The Studio MCP sends keys and clicks, not a gamepad:
the keyboard items run that way; a gamepad item runs only where
`execute_luau` can stand in (selecting with `GuiService.SelectedObject`,
reading an `InputContext`), and the feel of the sticks and buttons is
August's, on a real controller.

- [x] (`UiKeys` 3000 sink [Back, Menu], `HudKeys` 1000 [BuildButton,
  ResidentsButton], `BuildKeys` and `BuildPad` 2000 sink, off; B and R fired
  from there.) The contexts exist and work where they are: `PlayerScripts.GameInputContexts`
  holds `UiKeys` (3000), `HudKeys` (1000), `BuildKeys` and `BuildPad`
  (2000, off until build mode opens). If no action fires, an `InputContext`
  may need another parent (DEVNOTES: the avatar's `CharacterContext` lives
  in `StarterPlayer.PlayerModule`).
- [ ] (B opened build mode, `BuildKeys` on and the HUD hidden; B again
  closed it; R opened Residents; a mouse click on Book opened it. R inside
  build mode, `,` `.` and the chat not tried.) Keyboard, unchanged: B opens and closes build mode (once per press, not
  open-and-shut), R opens Residents outside build mode and rotates the ghost
  inside it, `,` and `.` turn the build camera; none of them acts while
  typing in the chat.
- [ ] Every window (Rating, Residents, Book, Moon, Store, Daily, Events,
  Settings, the piece menu, traps, style, the Ping menu): opened with
  `GuiService.SelectedObject` set by `execute_luau` on its HUD button and
  activated, its top-left button is selected; it stays selected through a
  redraw (the till ticking redraws the Store); closed, the selection is nil.
- [ ] Build mode with the gamepad as the last input: opens on the first card;
  a card chosen lets the selection go and a ghost stands at the plot's
  middle; `BuildPad` is on only while nothing is selected.
- [A] (A real controller: the Studio MCP cannot press a gamepad button.)
  ButtonY selects the HUD's Build button and lets go again; the D-pad walks
  the columns and the window's buttons, never out of an open window; A
  presses; ButtonB closes the window on top.
- [A] (A real controller.) Build mode: the left stick moves the ghost (or the
  gold cursor) the way it points on the screen, at every turn of the view;
  the avatar does not walk or jump meanwhile; A places, and on a room, decor
  or a closed area opens its menu (Move, Sell, Buy selected); RB rotates;
  D-pad up/down changes floor, left/right turns the view; the right stick
  turns and zooms (up is in); B stops placing, then leaves the cards, then
  leaves build mode; a prompt's X (the desk's) still works outside build
  mode.
- [A] (A real controller.) The strip's lines name the gamepad's buttons
  (RB, A, B, Y) after a gamepad press and the keys after a key or a click.

## Pacing and the tutorial's free area (GDD §4.2, §11, his go 2026-10-20)

Built 2026-10-20: the bus 3–8 per player, every stay doubled, Legendary
friendship 5, and `BuildService.tutorialArea` at the goal card. Verified only
by stylua, selene, the pure specs under Lune and `tools/balance_model.py`.

- [x] A fresh test profile through the tutorial: at the goal card a front
  area beside the start area is owned (area 1 or 3, its plate gone in build
  mode), the next area's price is the third ($3,000), and the free Coffin
  Suite is placed in it with its door onto the lobby.
- [x] The Vampire Count arrives about three buses later and checks in.
- [x] A bus on a one-player server brings 3 or more guests; a Common's stay
  lasts 3 minutes.
- [A] Output on Play: no "server size" warning once Server Size is 6. The
  warning fires today (the place's server size is 60): his setting, WAITING §4.2.

## Tiles, desks and the facade round what is owned (GDD §5.4, A.1, his rulings 2026-10-20)

Built 2026-10-20: the plot bought a tile at a time ($50 × 1.03^n), a new
hotel's 4 × 4 square x 4–7, z 0–3, one or more `FrontDesk`s (a second $500),
the facade drawn along the owned tiles' outline on every floor, no lobby
model (`HotelPoints`), the goal card's free 3 × 4 block. Played on test
profile `Test_Tiles1020a`.

- [x] A fresh profile: 16 tiles owned, the desk at x 5–6, z 1 facing the
  street with its queue in the entrance's mouth, 14 walls, the arch and 4
  corner posts round the square; plates over the rest of floor 1.
- [x] Buying a tile moves the walls out: one tile, 16 walls and 8 posts; floor
  2 bought and a 2 × 2 block beside the square, 18 walls and the arch on floor
  1, 16 on floor 2 (its street side open, railed), slab 2 over the owned tiles
  only; prices $50, $52, $53, $55.
- [x] A second desk ($500): two guests queue one at each desk (each at its
  own `Queue_1`); desk 2's prompt checks in its own guest only; selling desk 1
  sends its waiting guest to desk 2's line; the last desk cannot be sold.
- [x] A walker from the path's foot through the arch into both rooms; rays
  across every outline edge on both floors hit a wall (34) or the front rail
  (4), and none of the 122 inner edges is blocked.
- [x] The goal card (`tutorial Goal`) gives the left 3 × 4 block when a room
  stands in the right one, and the free Coffin Suite is placed on it.
- [!] A click on a gold tile in build mode buys it (bought tile 8, 0). Found:
  the plates were rebuilt on every state change (the till ticks each second),
  dropping the lit one; fixed, the hover now stays lit.
- [x] Rejoined on the same profile: the tiles, the desk and the rooms come back.
- [x] A fresh profile (`Test_Tiles1020b`) by remotes and the desk's prompt:
  a room, the tutorial Slime queued and checked in at the desk, Gloom's arrow
  on the desk (`HotelPoints` on the client). Collect could not finish: the
  test account owns AutoCollect, so pay skips the till (an older fault, not
  the tiles'); jumped to SecondRoom. There Gloom's new line shows, no second
  room fits in the start square, four tiles bought (~$210) and the room at
  (8, 1) take the step on to Bus.
- [A] How the small start, the gold tiles and the facade look (his).

## Flip (GDD A.1, his ask 2026-10-20)

Built 2026-10-20: F (L1, ⇋ Flip) mirrors a room or amenity being placed or
moved; saved as `m`; the door on its other front cell; the server places
`<PieceId>_Mirror`, or a blockout that mirrors itself; refused (`NoMirror`)
for a kit piece with no mirror yet. Played on `Test_Tiles1020a`.

- [x] A flipped Standard Room with the kit's model and no mirror: refused,
  `NoMirror`.
- [x] With the kit's Standard Room hidden in that play session only (the
  blockout path): placed flipped at x 10–11, z 1–2; its `Door` at local x +6,
  onto cell (11, 0); a guest checked in walked queue → hallway → (11, 0) →
  the door → the bed, and was InRoom.
- [x] Build mode's `Flip` action (F, ButtonL1) and the ⇋ Flip button exist;
  build mode opened by firing the HUD's own action.
- [x] By real input (night 2026-10-21, `Test_Tiles1021`, the kit's Standard
  Room hidden in that play session): the Standard Room card clicked, F moved
  the ghost's door marker from x 42 to x 54, a click on the plot built it
  flipped (door at x 54); with an Armchair in it, a click on the room, Move,
  F and a click: the door back to x 42, the chair from x 52.5 to 43.5
  (mirrored about the room's middle, 48). A booked room refuses Move (`Busy`,
  by design). The Place button is reached by sweeping the mouse over the plot,
  which drags the ghost along: with a mouse, place by clicking the plot.
- [A] Every kit room and amenity needs its `_Mirror` from the kit's
  `finish()` (MODELS.md) before F works on the imported models.

## Windows (GDD A.1, his rulings 2026-10-20)

Built 2026-10-20: plain facade walls; a window bought ($100 PLACEHOLDER) and
placed on any outer wall section from four types, moved, swapped and sold
(full refund); a Twin sash on each front wall beside the arch at the start;
a window moved out along its line when a tile makes its wall an inside one,
refunded when it has nowhere to go; `Facade_Window_<Type>` from the kit or a
facade cosmetic, a blockout opening until then. Played on `Test_Tiles1020a`.

- [x] The start's two Twin sash windows on floor 1's front walls (x 4, x 7).
- [x] Placed a Round (−$100), swapped it for an Arched (the Round refunded),
  moved it, sold it (+$100); refused on the arch, on floor 2's open street
  side and on an inside edge (`NotWall`).
- [x] A window on a back wall moved out to the new back wall when the tile
  behind it was bought.
- [x] All four blockout shapes drawn on one wall (picture seen by Claude, not
  yet by August).
- [x] By real input (night 2026-10-21, `Test_Tiles1021`): the Windows tab
  clicked shows the four cards, the Round card clicked, the hovered wall
  1:9:0:0 lit (`Highlight` on it), a click placed the Round (−$100), a
  right-click stopped placing and a click on the window opened its menu:
  Move, Sell +$100, Another kind.
- [A] How the four kinds look: the kit's models (MODELS.md) replace the
  blockout shapes.

## Build camera turn (his report 2026-10-20)

- [x] The , and . keys turn the build camera (fired as the `Camera` action);
  the D-pad's view turn too. Roblox's own camera actions are all off in build
  mode (they do not take the right button).
- [!] By the MCP's mouse (night 2026-10-21): a right-drag did not turn: injected
  mouse moves carry `Delta` (0, 0), and the turn read only `Delta`. Fixed: the
  turn follows the cursor's own travel (`rightDragX`), right for both. Then a
  right-drag of 400 px on the plot turned the camera 183°; one that starts on
  the Rooms button does not turn; a right-click without a drag stopped placing
  (the ghost gone, the camera unturned). How it feels is his (WAITING §2.31).

## Tiles per floor, every floor walled (GDD A.1, his rulings 2026-10-20)

Built 2026-10-20: tiles bought on each floor apart (a tile upstairs over an
owned one below, adjacency per floor, a floor's first anywhere over the one
below), floor f's ladder ×2^(f−1) (PLACEHOLDER), a stair needs the tiles
above its well; every outline edge of every floor walled, the street side
too; profile schema 4 (tiles and purchases per floor) rebuilt every hotel
from the start square. Specs only so far.

- [x] On a fresh profile (`Test_Tiles1021`, night 2026-10-21): floor 2 bought
  ($500) has no facade piece; a stair at (4, 2) refused `TileAbove`; a tile
  at (9, 9) refused `NoTileBelow`; (4, 3) the first, $100; (7, 0) refused
  `NotNext`; (5, 3) beside it, $103; floor 2's walls round its own two tiles
  (6 walls, 4 posts, its street side 2:4:3:0 and 2:5:3:0 included). With the
  tiles above it bought the stair is refused `DoorBlocked` until an owned
  tile upstairs is free to step onto, then placed free (the floor's first).
- [x] The goal card's free tiles (`tutorial Goal`): fixed here, the windows
  commit had called `windowsOut` before it was defined (selene caught it).

## The hotel chain (GDD §6.4, his rulings 2026-10-20)

Built 2026-10-21 night: `Chain` (shared rules), `ChainService` (Travel, opening,
background earnings from the guests' measured income), the new rebirth in
`ProgressionService`, staff per hotel (`ResidentService`, `hotel`), Bayou Spa's
draft rows (WAITING §2.36), schema 5 rebuilt. Every number PLACEHOLDER
(WAITING §2.35). Played on test profile `Test_Chain1021`.

- [x] A fresh profile: schema 5, Haunted Manor, the chain empty. The floor cap
  2, +1 with the pass (the test account owns Extra Floor: floor 3 sold, as
  it should).
- [x] Opening in order: Travel 3 first refused `OpenInOrder`; Travel 2 opened
  Frostfang Lodge for $250,000 (PLACEHOLDER), the plot drawn with Frostfang's
  own facade; the Manor kept in the chain with its tiles, desk and floors.
- [x] Background earnings: the Manor at $10/s earned +$16 in 6.3 s while
  Frostfang was played (25 %); a $10M grant does not move the played hotel's
  rate, a Snowball Sprite paying 84 in an Igloo Room moves it (4.6 $/s after
  15 s, the 5-minute average).
- [x] Travel back and forth: each hotel's tiles (16 and 17) and facade come
  back; a resident on Frostfang's Front Desk has no slot at the Manor, the
  Manor's Housekeeper has.
- [x] Bayou Spa opened ($10M): the blockout hotel and Lily Pad Room; the bus
  after the next brings Bayou guests (Mossling, Firefly Sprite: the bus is
  drawn one ahead).
- [x] Rebirth refused without 5★ everywhere; forced (`rebirth`): +20 Moon
  Shards at $4M, the chain gone, Haunted Manor from the start square,
  Frostfang's staff to the Wing, the Manor's kept; the second rebirth +1
  Prestige Star, income multiplier 1.05; floors bought to 4 (3 by rebirth +
  the pass), the 5th refused `FloorCap`.
- [x] The panel by a real click on the HUD's Travel: your hotels (Playing,
  Open $250K, Open the one before), the rebirth's three 5★ lines and what it
  gives, the Moon Tree; Open clicked moved the player to Frostfang (−$250K).
- [ ] With guests over a long run: whether a real player reaches 5★ at each
  location in his times (`tools/balance_model.py`, WAITING §2.35).
- [A] The values (share, prices, cap, Prestige effect) and Bayou Spa's species
  (WAITING §2.35, §2.36).

## The free build camera (GDD §5.4, his ruling 2026-10-21)

Built 2026-10-21 night: the camera looks at a point kept inside the hotel's
owned tiles (a cell's margin), W/S/A/D move it (the avatar does not walk),
the wheel zooms, a right-drag turns and tilts (12°–89°), ⬇ Top snaps to top
view and back, one finger pans on a phone. Played on `Test_Tiles1021`, real
keys and mouse.

- [x] W held 1 s: the camera 30 studs forward, the avatar 0 studs.
- [x] D: the camera along its own right (dot 1.00); A held 4 s stops at the
  hotel's edge (world x 36: cells x 4–7 and a cell's margin).
- [x] A right-drag 200 px upward tilts it from 50.9° to the 12° floor.
- [x] ⬇ Top: straight down (picture seen).
- [ ] On a phone: one finger pans, two zoom and twist (pinch cannot be sent).
- [A] Whether its speeds and the tilt's direction feel right (his).

## Built rooms (GDD §5.4, A.12)

Built 2026-10-21 night (his rulings of 2026-10-21): rooms are inner walls on
half edges, a door and a chosen type, furnished like decor; profile schema 6
(`walls`, `rooms`, also in the chain's hotels); a new hotel starts with one
built Standard Room (an L of four cells on the guests' right of the desk,
`Constants.Rooms.Start`, PLACEHOLDER shape); remotes `WallRun`, `Door`,
`MakeRoom`, `ClearRoom`; walls, doors and posts drawn from the kit's
`Wall_Half`/`Wall_Door`/`Wall_Post` or a blockout carrying MODELS.md's
attachments; guests booked into ready rooms only, walked on the 3-stud
squares through the door to the key furniture's `Use`; the three bars'
bonuses in place of the tiers; Comfort from `Rooms.comfortPoints`. Played on
`Test_Rooms1021a`…`d`.

### Stage 1–2: data, server, guests, rating, tutorial (by remotes)

- [x] A fresh profile: the desk, the start room (9 walls, a door, 5 posts),
  its plaque, ready; the Slime booked into it, checked in, walked from the
  desk's square along the squares through its door to the bed's `Use` and
  lay there (picture `archive/screens/2026-10-21_rooms_start_room_guest_on_bed.jpg`).
- [!] The room marker's attachments were set before being parented (off by
  the root's frame): fixed (parent first), seen at the door (57, 24) looking
  out of the room, the bed's `Use` at (54, 43.5).
- [x] Walls refused where A.12 says: on the mouth (`Mouth`), against the desk
  (`Piece`), a wall taken down between two rooms (`MergesRooms`), a room's
  wall taken down onto the hallway (`RoomTaken`), a door walled up while its
  guest is due (`Busy`), a writing desk across a wall, a desk inside a room
  (`Decor`/`Wall`), a placed Room piece (`Built`).
- [!] Location-0 furniture (Nightstand, Writing Desk …) was refused
  `Location`: `Pieces.decorHere` lets furniture of every location stand.
- [x] A second room by remotes: two tiles, 4 half edges of wall ($20), a
  door ($10), Standard Room chosen, a Bed ($50): ready; a Skeleton booked into
  it walked through its door (x 94.5 at the door's half edge) to the square
  beside the bed and onto it; its pay 1.4 (Furniture bar 0.8: × 1.4).
- [x] Comfort never falls as rooms are added: 2 → 4 (the second room ready)
  → 5.2 (a nightstand in it); nothing it lacks lowers it.
- [x] A check-out leaves the room Dirty with Clean on at its door; held at
  the door (prompt) it is Vacant again.
- [x] Each hotel of the chain keeps its own rating samples (8acb0e8): Manor
  Service 58.9 → Frostfang opened fresh: Service 0, its own start room →
  back at the Manor: Service 58.9.
- [!] A new Frostfang hotel got a Standard Room: the start room takes the
  location's first room type and its key piece (Igloo Room, Ice Bed).
- [x] Tutorial: CheckIn first (the start room is there), SecondRoom closed by
  the second room's type, Furnish by its Bed, then Bus; the goal card's block
  on the side without rooms (left when the second room stands on the right),
  the start room walled off from new tiles by itself (`Rooms.autoWalls`), the
  Coffin placed free (voucher), a Coffin Suite built (`room` dev) took the
  Vampire Count.
- [ ] Collect: the test account owns Auto Collect (its till stays 0), so the
  step was jumped by `tutorial`.

### Stage 3: the build mode (real mouse and keys, `Test_Rooms1021e`)

- [x] Build opened by a click: tabs Walls, Rooms, Furniture, Decor / Stairs,
  desks, Floors, Windows; no Rooms/Amenities cards, no Flip.
- [x] Two gold tiles bought by clicks.
- [x] Walls by a real drag along a cell row: the ghost showed each half edge
  (green inside, the facade's refused, "2 walls · $10"); released, the two
  inside half edges built ($5 each), the facade's refused (`NotInside`)
  (picture `2026-10-21_rooms_wall_drag_ghost.jpg`).
- [x] A tap on a cell edge built its two half edges; Door then a tap put a
  door in the half edge under the pointer ($10).
- [x] Half cells toggled on: a tap built one 6-stud half edge ($5); Remove
  and a tap took it down (half back).
- [x] Rooms tab, a tap inside the walled space: the type list, its title
  the space's size (4 cells), every location-1 type and amenity with its
  tooltip (who stays or what it gives, key furniture, minimum and full
  size), the locked ones with their unlock (picture
  `2026-10-21_rooms_type_list.jpg`); Choose on Standard Room made it.
- [x] Furniture tab, the Bed card, the ghost in the room, a click placed it
  ($50): the room ready, Comfort 2 → 4.
- [x] The room view by a real click on the room: the camera flew in (looking
  at the room's middle, 96, 36), the walls toward the camera faded, the
  panel: type, tooltip, "Ready for guests · 4 cells", Size 0 %, Furniture
  50 % (+25 % pay, +8 happiness), Decor 0 % (picture
  `2026-10-21_rooms_room_view.jpg`); Close flew back; Change type opened the
  list for the same space.
- [x] A guest of the bus booked into the clicked room, checked in, walked in
  and lay on its bed; the room view says "a guest is in" (picture
  `2026-10-21_rooms_room_view_guest.jpg`).
- [!] On a phone (iPhone 14, landscape) the room view's panel ran off the
  top: on a short screen it now sits top-left, scaled to fit, the tools
  hidden while it is open and the strip beside it; seen (picture
  `2026-10-21_rooms_room_view_phone.jpg`).
- [A] How the room view looks on a phone: the panel's text is small at its
  scale and the HUD's right column covers part of the room (his look).
- [ ] A gamepad's A on an edge and on a room (no controller here).
- [ ] A two-finger pan while the wall tool is on (one finger draws walls).

### Stage 4: clean-up (`Test_Rooms1021f`)

Removed: Flip and `<PieceId>_Mirror` (`HotelKit.mirrorable`, Grid's `m`,
`Furnish.mirror`/`mirrorSquares`, their specs), the room and amenity
blockout and `PlotService.roomInfo`. Left unused, since removing them would
take their specs' rules with them: Grid's door and reach rules for `Room` and
`Amenity` pieces, and `Furnish`'s room frame and tiers with `Layout`'s
`roomTier`/`container`/`canPlaceDecor` (the game asks `Rooms`).

- [x] A fresh profile after the clean-up: the desk and the ready start room,
  the tutorial at CheckIn; no error of the game's own.
- [x] A tile bought beside the start room put up its two walls by itself
  (`1:8:4:1`, `1:8:5:1`); the room stayed ready.
- [x] A rebirth (`rebirth`): the start square, the desk and a new ready start
  room.
- [A] The kit's `Wall_Half`, `Wall_Door`, `Wall_Post` and `Furniture_*`
  (staged in `blender/_import` by another session) after his import: seen in
  the game in place of the blockouts.
- [A] Whether the start room's L of four cells on the guests' right reads as
  "one room to its right" (`Constants.Rooms.Start`, PLACEHOLDER shape).

### Ready means the key furniture is reached (`Test_Ready1021a`)

Found in play 2026-10-21 (Test_Rare1021a): furniture could wall a room's bed
off from its door, the room stayed ready and check-in sent the guest home (a
VIP lost). Now `Rooms.ready` asks for a guest route through the door to a
square beside the key furniture (`Rooms.keySpot`, else `KeyUnreached`: "guests
can't get to the Bed or Double Bed"), and `Rooms.check` refuses a change that
would cut a ready room's key furniture off (`KeyCutOff`).

- [x] A 2 × 2 Standard Room built (`room 8 2 2 2`, its Bed against the back
  wall at squares 32–34, 14–15); a row of Snack Baskets placed by the
  `PlaceDecor` remote across it at z 13: x 32–38 placed ($40 each), x 39 (the
  piece that would close the row) refused `KeyCutOff` and not charged; the
  room stayed ready and vacant.
- [x] A Slime booked into it (`guest`), checked in: its path went through the
  door, round the end of the row by the one gap and to the key spot beside
  the bed, then onto the bed's `Use`.
- [x] The closing basket forced into the profile past the rules (as an old
  save could hold it): not ready, `KeyUnreached`, no key spot; a guest
  pointed at the room by `GuestService.assign` was not booked (sent home,
  `[guests] no way from the desk …`); the basket taken out: ready again.

## The world (GDD §3, §6.4)

Built 2026-10-21 morning (night brief step 7b, his ruling 2026-10-20: "All the
hotels stand in one world, far apart, seen from the other plots"): a street per
location along world X, `World.StreetSpacing` 1400 apart (PLACEHOLDER), each
Creepy Lane's layout moved; the played hotel live on its street, the chain's
others drawn static on theirs (`workspace.WorldPlots`); a bus and Hunter Night
per street with a hotel played; the forest and the ground blending along the
road between streets; Bayou Spa's cypress a Luau blockout. Played by remotes
and `execute_luau` only (no window focus) on `Test_World1021a`.

- [x] A fresh profile: plot 3 on Creepy Lane, 10 live plots in `Plots`, 30
  drawn plots in `WorldPlots`, `Street`, `Street_2`, `Street_3`,
  `WorldGround`, a Hunter Camp per street. No errors of the game's own.
- [x] `chainopen 2`: the live `Plot_3` moved to street 2 (origin x 1328), the
  character to its forecourt (1400, 4.5, 32), the Manor drawn on Creepy Lane
  from its record (133 parts, no prompts), street 3's plot 3 empty; the bus
  list `BusStreets` "2".
- [x] `chainopen 3`: on street 3 (2800), both others drawn with their signs
  ("…'s Haunted Manor 1.5★", "…'s Frostfang Lodge"), `BusStreets` "3".
- [x] A bus on each street played: street 3's brought Mud Puppy, Bog Frog,
  Mossling (Bayou Spa's) off at its west stop (x 2530); street 2's Frost
  Troll, Snowball Sprite (x 1130); Creepy Lane's Skeleton, Werewolf (x −270).
  The client drew `NightBus_3` on street 3's road. `nextbus` lists each
  street's next bus from its own family.
- [!] Guests stranded on a street left with no hotel played (no bus would
  come for them): fixed, they go with the street's last bus; seen after a
  restart (street 2's two gone 2 s after travelling to 1).
- [x] Rejoin with Frostfang played: spawned on street 2, Manor and Bayou drawn.
- [x] Hunter Night while on street 2: the hunter walks in from street 2's
  east end (x 1888) to plot 3's entrance (1400, 48).
- [x] Seen from a plot (by geometry; trees are not queryable): from street 1's
  last plots (north and south) to street 2's first plots, 545–790 studs, no
  tree within 6 studs of the line (nearest 19–22); inside the fog's end (900).
  From the middle plot it is 1040: past the fog.
- [x] Measured, one player, all three hotels (start squares, the Bayou one
  half-filled by an interrupted `fill`: 2,038 parts): server 1,248 parts and
  188 lights before the fill (each street 180 parts / 60 lamps); client at
  Creepy Lane 10,612 parts (the forest 10,099: ~5,000 trees inside
  `Forest.DrawDistance`, about as many as one street's forest drew before),
  far plots streamed out (Bayou's 2,038-part hotel not on the client), lights
  110 → 63 after the lamps' light was limited to 500 studs (`Lod`).
- [x] Pictures from a plot toward the next street, and of each street's look
  (2026-10-22 evening, Studio in front, `Test_World1021a`, `chainopen 2`, `3`):
  seven views in `archive/screens/2026-10-22_world_*.jpg`; Studio draws frames
  when it is in front. **Blind review** (one reviewer, 17 findings), triage:
  *his call* (WAITING §2.46): no roof from the raised camera, the black
  unowned-tile plate, Bayou not reading as a swamp and its lime curb glow,
  Frostfang's box facade, lamps too dense, three pavings at the entrance, the
  rectangular clearings, the dark square-cornered road between streets.
  *False:* the Bayou hotel as a two-floor slab (the test profile's
  interrupted `fill` bought every tile on two floors; Bayou has no facade kit,
  so its walls are the blockout); a lamp in front of the door (picture 2
  shows the path between two lamps); no bus (between buses).
  **Checked by the code, all false:** "snowy firs" seen from Creepy Lane are
  its dark firs tinted by the fog (FogEnd 900; `StreetLayout.blend` gives
  location 1 out to `LaneEnd`); trees "inside buildable plots" stand in the
  gaps between plots (`Forest.cleared` keeps every plot's whole grid and its
  Wing clear, plus `Clearing`); the flat orange objects at the street ends are
  the bus stops' shelters (`StreetService.shelter`, a Luau blockout: no model
  yet); the near side's "curb gaps" are the gaps between plots (each
  forecourt's `Edge_Left`/`Edge_Right` spans its own plot).
- [ ] Two players on two streets at once (each street's bus and Hunter Night
  together): needs **Server and Clients**, his start.
- [A] The looks: Frostfang's and Bayou's ground and lamps, the meadow between
  streets, the blockout cypress, the spacing (WAITING).

## The showcase (GDD A.11.4, street only)

Built 2026-10-21 morning (night brief step 9, piece 1), on A.11.4's
scrutinized recommendation; street only is his call (WAITING §2.38), built as
the draft recommends and reversible. Every number `Constants.Showcase`,
PLACEHOLDER. Played by remotes and `execute_luau` only (no window focus) on
`Test_Endless1021a`.

- [x] Specs: `showcase` (weekly count once per liker a week, a week from
  Monday, the play-time rule, milestones, each street's favourite, the lobby
  test) under Lune.
- [x] A fresh profile: `likes` 0, `likesWeek` `{week 0, count 0}`, `played`
  counting from the join. No errors of the game's own.
- [x] Ten likes received from nine made-up likers (`likefrom 91..99`, then 99
  again): lifetime 10, weekly 9 (99 counted once), the Ribbon sign in
  `cosmetics`, the pop-up "♥ 10 likes! You earned the Ribbon sign." shown on
  the client; an 11th from 99: lifetime 11, weekly still 9.
- [x] The sign: "…'s Hotel ★ Street Favourite / 1.5★ · ♥ 11" (the street's
  weekly favourite, alone on the street); plot attributes `StreetFavourite`
  true, `Likes` 11.
- [x] **Wear it** (the `Equip` it sends): `equipped.Sign` the ribbon, its
  blockout `Cosmetic_LikeRibbon` drawn on the sign (5 parts).
- [x] The Showcase panel (HUD's ♥ Showcase): Head "♥ 11 in all · ♥ 9 this
  week · Rosette sign at 50", Hint "…once you have played 9 more minutes
  today", one row `Hotel_3` "1. …'s Hotel ★ Street Favourite", "Haunted
  Manor · ♥ 9 this week · ♥ 11 in all", **Yours**; "Nobody else is playing
  here yet".
- [x] `Visit` to your own plot and to an empty plot: refused (the character
  did not move).
- [x] The lobby test: at the forecourt `false`, stood on start tile (5, 2)
  `true`.
- [x] The daily "Visit 3 hotels" (`dailykind Visit`): two visits counted from
  three (owner 777 twice counts once): "Visit 3 hotels 2/3".
- [ ] Two players: a real like (the 10-minute rule's refusal, the giver's
  toast), **Visit** to the other hotel, walking into its lobby counting
  toward the daily, the weekly favourite moving between two hotels. Needs
  **Server and Clients**, his start.
- [A] The four milestone cosmetics' look (blockouts: the sign frame in four
  colours) and the panel's look.

## Residents level up (GDD A.11.6)

Built 2026-10-21 morning (night brief step 9, piece 2) on A.11.6's
scrutinized recommendation: one time-based XP scale, the bar then a cash
price in the resident's own Wing rate, cap 10 for all, Wing earnings and
staff efficiency per level; levels kept through a rebirth (his call, WAITING
§2.38: the draft's, reversible). Every number `Constants.Residents.Level*`,
PLACEHOLDER. Played by remotes and `execute_luau` only on `Test_Endless1021b`.

- [x] Specs: `levels` (level 1 by default, longer bars, the bar stops full,
  nothing past the cap, levels never lower pay or efficiency, each level
  pays back slower) under Lune.
- [x] XP at work: a Slime in the Wing and a Ghost on Housekeeping each 0.10
  XP in 6 s (1 a minute); the Ghost's efficiency 1.0 (best role).
- [x] Level up refused with the bar not full; refused "Cash" when short
  (the Ghost's 450 with $214).
- [x] The Slime's bar filled (`xp 1 100` stops at 20/20) and Level up paid
  $150 (10 min of its 0.25/s): Lv 2, XP 0/40, its Wing income 0.25 →
  0.275/s measured (AutoCollect), the next price $330.
- [x] The Ghost to Lv 2: efficiency 1.0 → 1.03, its Wing rate 0.825/s, the
  next price $991.
- [x] The Residents panel: each row's `Level` ("Lv 2", "0/40 XP", the bar,
  "Working…"); `LevelBadge` "Lv 2" over the Slime, "Lv 1" over the Ghost.
- [x] A rebirth: both residents kept at Lv 2 with their XP.
- [ ] The cap reached in a real run (held by the spec only), and a level's
  staff effect seen in the rating's coverage and Security's scare rate.
- [A] The badge's and the row's look; whether levels go through a rebirth
  (WAITING §2.38).

## Deeper mutations (GDD A.11.5)

Built 2026-10-21 morning (night brief step 9, piece 3) on A.11.5's
scrutinized recommendation: a size (Tiny, Giant) and a look stack, rolled
independently; their pay added; two fields, `size` and `mutation` (the look,
kept by name so `== "Golden"` holds); the month's mutation a row of the look
table in its month (March Mossy, May Rainbow, July Sunburnt, September
Moonlit); a stack fills both Book entries, marks the page and the first
gives a title; the month's looks a Seasons row with no set title. Whether a
missed month may come back off-season is his call (WAITING §2.38; not
built). Every number `Constants.Mutations`, PLACEHOLDER. Played by remotes
and `execute_luau` only on `Test_Endless1021c`.

- [x] Specs: `mutations` (sizes and looks, independent rolls, added pay,
  the month's row in its month only with Shadow and Golden still rolled,
  the Seasons row, the stack's words), `data` and `events` updated to the
  two rolls; all 151 green under Lune.
- [x] Residents: a Giant Golden, a Giant and a Golden Slime; Wing rates
  1.5, 0.5 and 1.25 /s (base 0.25: ×6 added, ×2, ×5); `Size` and `Mutation`
  on their Configurations; drawn at scale 1.5 in Foil, 1.5 plain, 1.0 in Foil;
  the Residents panel names "Giant Golden Slime".
- [x] The Book on the stack's move-in: Slime's `Golden`, `Giant`, `Stacked`;
  title "Stacked Host" announced; the page's Mutations line "· Giant Golden ·"
  and Seasons line "· · stack ✓".
- [x] The calendar at 2027-03-16 (`eventclock 3504`): `MonthlyMutation`
  Mossy, the banner "This month's mutation: look out for Mossy guests!", the
  Events panel's line; `find Ghost Mossy Tiny`: Tiny, Mossy, Stacked, and no
  "Mossy Host" title.
- [x] Six buses: a Tiny Slime off the bus with `Size` Tiny and no look,
  drawn at scale 0.5 and labelled "Tiny Slime".
- [ ] A stacked guest off a real bus and its check-in pay (0.29 % of
  guests: by the spec and the residents' pay only); the announcement of a
  stacked Legendary.
- [A] The four monthly looks (Mossy grass, Rainbow glass, Sunburnt red,
  Moonlit neon), their names and months, the title's name; whether a missed
  month comes back off-season (WAITING §2.38).

## VIP contracts (GDD A.11.1)

Built 2026-10-21 morning on A.11.1's scrutinized recommendations (his calls,
WAITING §2.38; reversible PLACEHOLDERs, every number `Constants.Contracts`):
the VIP an extra bus seat booked to the hotel, its room held from Ready; a
spec drawn one bar above the hotel's best room of the type; the clock play
time at the contract's own hotel, stopped from Ready; a missed contract gone
and its slot drawn anew; at most 3 completed a UTC day; a Book page asks for
a species for a swap. Souvenirs (A.11.3) are not built: the first contract of
a species fires `ContractService.onSouvenir` and a stat only. Played by
remotes and `execute_luau` only (no window focus) on `Test_VIP1021a`, two
playtests.

- [x] Specs: `contracts` (12 rules), all 163 green under Lune (every spec but
  `data`).
- [x] Shut below 2★: the panel reads "opens at 2★, your hotel is 1.5★"; at
  3★ (`vipstars 3`) three offers drawn, Standard Room only (the only type
  buildable then), each one bar above the start room's.
- [!] A drawn offer became free money once a room was built for a twin
  contract (Golden Skeleton, Decor 100 %): fixed, offers a room meets are
  dropped and drawn anew (`Contracts.prune`, spec); seen in the second
  playtest (the persisted offer 3 replaced on load).
- [x] Accept → Ready refused while no room meets it ("No Standard Room meets
  it yet", "…isn't free" while the tutorial Slime was in it); decor placed
  by `PlaceDecor` (Record player, Blackout curtains) → Decor 100 %; Ready
  held room 2 (plaque `State` Reserved); the clock stood at 60 s from Ready.
- [x] The bus: the street's next bus drawn with 3 (no vacant room), arrived
  with 4, the VIP last, stepping off at the east stop "VIP for oden" in gold
  with its glow (client label read), straight to plot 3 (no browse), Queued
  10 s, checked in by Front Desk staff into room 2, pay 12.5/s (Common ×
  Golden 5 × Furniture bar 1.25 × VIP 2). The browsing Skeleton did not get
  the held room.
- [!] Completed on a happy stay (review 5): +$12.6K, "VIPs today 1/3", the
  `VipDone` pop-up, stats `vipContracts`, `vipFirst_Skeleton` (the souvenir
  stub), its slot drawn anew. The reward counted the VIP's own doubled pay
  in the income: fixed (`baseRate`), and in the second playtest a Rare
  Zombie (pay 24/s) paid exactly $18,000 = $10/s floor × 15 min × 2.
- [x] Cancel ("Let the room go") and Ready again; Booked→Arriving→Staying,
  played 2 s over the whole run.
- [x] Missed: `vipclock 2600` then 100 → gone, stat `vipMissed`, not
  re-listed, its slot drawn anew (offer 5).
- [x] Book requests: Zombie (already offered, no swap), Vampire Count refused
  "needs a 4★ hotel", Pumpkin Head and Ghost refused (room not buildable),
  Mummy then Werewolf each took the last offer for a swap, then "No swaps
  left today"; the Book's 👑 on Slime, Skeleton, Mummy, Zombie, Witch,
  Werewolf.
- [x] Daily cap: `vipdone 3` → Accept refused "new contracts tomorrow", the
  panel's note and a dark Accept; the ledger (done 3, swaps 2, offers) came
  back from the DataStore in the second playtest.
- [?] The desk's "VIP ledger" prompt (F): prompts are not shown with Studio
  in the background (no `PromptShown`); the server's answer, the `VipLedger`
  Moment, opened the panel. Needs Studio in front.
- [ ] The room view's "👑 meets your VIP's ask" / "held for your VIP" (build
  mode, not opened by remotes); an unhappy VIP (no reward); a travel or a
  rebirth while a room is held; a phone's layout; two players seeing another's VIP.
- [A] The numbers (unlock 2★, 3 offers, 45 min, 3 a day, 15 min × rarity,
  ×2 pay), the VIP extra seat's line in §4.3, how a reward is sized for a new
  hotel ($10/s floor: $9K–18K at 1–3★), and whether an unhappy VIP should
  forfeit (WAITING §2.38).

## Rare decor sets and souvenirs (GDD A.11.3)

Built 2026-10-21 morning on A.11.3's scrutinized recommendations (his calls,
WAITING §2.38; every number `Constants.Finds`, PLACEHOLDER): the Count's
Study (5 pieces, Haunted Manor) found by rolls on happy stays of Rare-or-better
guests (2 %) and a defended Hunter Night (25 %, one per player), the pity
after 40 misses giving the next unfound piece, duplicates in cash once all
are found; a souvenir per species by move-in no. 3 or its first VIP
contract; found once, copies placed for cash; the set bonus (+0.25 Decor)
once per set per hotel, the oldest room holding it; rebirth keeps the finds.
No models imported yet: every set piece and the souvenir are Luau blockouts.
Played by remotes and `execute_luau` only (no window focus) on
`Test_Rare1021a`, two playtests.

- [x] Specs: `finds` (9 rules), all 172 green under Lune (every spec but `data`).
- [x] By pity: `rare roll 40 0` → 40 misses, the 41st gave the Rug (the
  set's first in order); by roll: `rare roll 1 1` gave the Bust (random
  among the unfound); the `Found` pop-up ("★ Found!", "The Count's Study:
  2/5 found", size, layer, "Build → Decor, under Found", the copy's price).
- [x] The real hooks: a happy Common Slime stay rolled nothing (misses held
  at 40); a happy Rare Zombie's stay at 40 misses gave the Portrait (the
  next unfound) and reset the run; a defended Hunter Night (`hunters`,
  `defend`) rolled once (misses 3 → 4) beside its cash.
- [x] Souvenirs: Slime's move-ins 2 and 3 (`resident Slime`) → the souvenir
  on the 3rd, not again on the 4th; a VIP contract (Zombie, Furniture 100 %,
  held room 2, extra seat, checked in, happy) → `Souvenir_Zombie` by
  `ContractService.onSouvenir` ("Zombie's first VIP contract" pop-up, "A
  souvenir!"), contract `first` Zombie.
- [x] Placing: an unfound Globe and Ghost souvenir refused `NotFound`; the
  Rug, Portrait (wall, back on the room's wall) and Bust placed for $80,
  $200, $120; the Zombie souvenir for $200: its blockout drawn with
  `Ribbon` the Zombie's colour, `Trim` 0.6 of it, `Badge` "Zombie" on its
  front, the emblem a blockout disc with "Z" on `Medal`'s top, `Glass` glass.
- [x] Set bonus once: two 16-cell Standard Rooms with a whole set each
  (rooms 23 and 25): room 23 (the older) Decor 0.567 + 0.25 = 0.817 with
  `sets` CountStudy, room 25 the same pieces 0.567 and no bonus; earlier two
  3 × 3 rooms both full (1.0) with the bonus only in room 9; the state's room
  rows `bonus` true / false and "5/5" (the room view's line).
- [x] Duplicate: with all five found, a hit paid $3K (5 min of income) and
  the "Found again" pop-up (its wording fixed and seen in the second playtest).
- [x] Rebirth keeps: after `rebirth` the seven finds and Slime's move-ins
  stayed, the placed copies went with the hotel; finds back from the
  DataStore in the second playtest.
- [!] Found while playing: furniture can cut a room's key spot off from its
  door (a Wardrobe beside the Bed): `Rooms.ready` said ready, check-in found
  no path and sent the VIP home. Built rooms' rule, not changed here (in the
  report).
- [?] The Decor tab's Found and unfound cards, the room view's set line, the
  pop-up's **Place it** and the Book's souvenir mark: drawn from the state
  (read and right), but not opened or clicked (no window focus); pictures
  (Studio drew no frames in the background).
- [A] The look of the set and the souvenir after his import, the emblem
  disc, every number (WAITING §2.38).
- [x] Frostfang Lodge's and Bayou Spa's sets (2026-10-21, `Test_Rare1021b`,
  by remotes): after `chainopen 2`, `rare roll 41 0` gave `AuroraLodge_Rug`
  by pity (40 misses, the 41st), a second run the Painting (the set's
  order); after `chainopen 3`, the same gave `LanternGrove_Rug`, and nothing
  of the other locations' sets. No models imported: blockouts.

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
- 2026-10-19 19:58 Staff at work: spec 7/7; Room Service out 1.0 s, at the door 2.1 s, done 13.3 s, back 14.3 s, walked on the client post → hall → door (facing it) → post; Housekeeping two rooms in turn with "✓"; turned back when the guest left; reassigned mid-errand stands at the new post; two Room Service (Slot 1, 2) take rooms 1 and 3 at once, the Mummy (efficiency 0.6) done at ~20 s. Floor 3 waits for free building's stairs.
- 2026-10-19 20:03 Rebirth by the panel's button (Test_Eve1019a) and Frostfang's rooms in a plot pass.
- 2026-10-19 20:07 The phone: all panels opened; Residents' role row and the Ping menu fixed and seen fitting.
- 2026-10-19 20:33 Phase 12 (street) after the merge: specs 82/82 (13 files); forecourt rayed and walked; the bus's drive and stops, browsing, the stops' waiting and boarding, a trap's scare; the forest's placement (blockouts). Scenery, the tree import, the tutorial's guests, the phone's frame time and the in-game review open.
- 2026-10-19 20:42 Phase 13 (free building) after the merge, before the import: specs 90/90; refusals, areas, a free stair and a walker up it to floor 2, guests' paths to floor 2, the desk moved with its points, decor and its doorway refusal, finishes. The menu's clicks, floor 3 and everything after the import open.
- 2026-10-19 20:49 Rating's staff coverage after the merge: Front Desk +10 and Room Service +10 to Service, back when unassigned (a second Assign within 0.25 s is dropped by the rate limit, not a fault).
- 2026-10-19 20:56 Tutorial Commons and the named ping after the merge: specs 97/97; the tutorial to Clean on a fresh profile; the first tutorial bus brought two Commons, one picked the hotel; the ping named the Coffin Suite. Fixed: the tutorial's guest gave up at the desk. The till's E prompt could not be triggered through the MCP beside the desk's (both E, OnePerButton, 3 studs apart): WAITING §1.10.
- 2026-10-19 21:02 Gamepad navigation after the merge: the input contexts exist with their priorities; B, R and a mouse click act as before; no error. The gamepad's own items are August's (a real controller).
- 2026-10-19 21:06 Staff to floor 3 in a full hotel: up the placed stairs, but a 1,445-stud path outlasts the request (WAITING §2.29).
- 2026-10-19 21:09 The piece menu by clicks: a room's menu opened by a click on it, Sell and Move done by clicks.
- 2026-10-19 22:35 Free building after the import: 52 pieces saved and synced (agent, skill `import`); the lobby shell and the FrontDesk seen and walked. The trees wait for the Rojo restart.
- 2026-10-19 22:39 The forest with the real trees after his Rojo restart: 677 models, 646 as proxies, a trunk stops a walker.
- 2026-10-19 22:42 The forest longer and thicker by the play area (his ruling): 4,723 trees (a 60-stud thicket of 735, 3,988 beyond, out to 600 studs), 9,604 parts with only the 120 near the camera whole; no error. Pictures: `archive/screens/2026-10-19_forest_thicket.jpg`, `archive/screens/2026-10-19_forest_long.jpg`.
- 2026-10-20 21:39 Pacing and the tutorial's free area (test profile Test_Rel1020a; steps to SecondRoom, Goal and Done jumped by `tutorial`, buses called by `bus`): two Standard Rooms in the start area; at the goal card area 1 owned beside area 2 and the card reads "in your new area"; the Coffin Suite placed free at (0, 2) in it (paid 0, voucher spent); the first bus drew 3 guests for a one-player hotel with 3 vacant rooms; the Vampire Count booked after bus 2 and on bus 3, checked in to the suite; stays by the server's timers: Slime 180 s, Vampire Count 600 s. The server-size warning fires (60). The new bus horn (9114660894, 2.8 s) loads and plays when a bus arrives.
- 2026-10-20 22:42 Tiles, desks and the facade (Test_Tiles1020a): the start square, tiles bought by remote and by a click, the outline walled on two floors (rays, a walker), two desks with a guest at each, a desk sold with a guest waiting, the goal card's block and the free Coffin Suite, rejoin; fixed: the tile plates redrawn every second. No errors of the game's own.
- 2026-10-20 22:56 Flip (Test_Tiles1020a): refused without a mirror model; on the blockout path a flipped Standard Room's door on its other cell and a guest walked in through it; build mode's Flip action and button present. Also: a tile purchase now redraws only the slabs, plates and facade (a quick run of purchases lost one to the rate limit while each rebuilt the whole hotel). No errors of the game's own.
- 2026-10-20 23:03 Windows (Test_Tiles1020a): the start's two Twin sash, place, swap, move, sell and the refusals by remote; a window moved out by a tile purchase; the four blockout shapes. No errors of the game's own.
- 2026-10-20 23:07 Build camera turn: , . and the view turn work; Roblox's camera actions off while building; the right-drag made independent of `processed`, its real-mouse check left for a night run (WAITING §2.31).
- 2026-10-20 23:19 The ten new Haunted Manor decor after their import (Test_Decor1020, by remote, no window focus): all ten placed through `PlaceDecor` in the start area and a Standard Room; read back on the server: each model's base on the floor (the Wall Clock hangs from 2.92), nothing colliding, Root hidden, the Side Table's flame Neon with its light; the Bookshelf and Wall Clock refused on hallway floor ("Wall", by design) and placed in the room with their backs on its wall's face (z 95.60 both). Seen in screen captures (`archive/screens/2026-10-20_decor_ingame_*.jpg`). No errors of the game's own. Each floor piece was placed twice (the client saw the first model later than the script waited); harmless on the test profile.
- 2026-10-21 02:38 Facades in the game (Test_Facade1021): both kits' and the five packs' real pieces on a three-floor hotel, four window types, 432 rays out of the walls blocked, the arch 25/25 open, a walker through it; Frostfang after a rebirth. Two blind reviews triaged (`blender/facade/README.md`, "In the game"). No errors of the game's own.
- 2026-10-21 02:38 Tiles per floor (Test_Tiles1021): every refusal by remote (TileAbove, NoTileBelow, NotNext, DoorBlocked), prices $100 and $103, floor 2 walled round its own tiles, a stair placed free; the goal card's block (24 to 36 tiles).
- 2026-10-21 02:38 Real input with Studio in front (Test_Tiles1021): Windows (tab, card, hover, place, the window's menu) and Flip (the ghost's door, a flipped room built, Move with F mirrors its decor) by clicks and the F key; the build camera's right-drag fixed (injected moves carry no Delta; the turn now follows the cursor) and played: a drag turns, one from a button does not, a plain right-click stops placing. No errors of the game's own (one `ContentId 203785492` type warning, not in the repo).
- 2026-10-21 02:57 The hotel chain (Test_Chain1021): opening in order, Travel and back (each hotel's tiles, facade and staff), background earnings measured from guests only, Bayou Spa's blockout hotel and guests, the new rebirth twice (shards, the chain gone, Prestige Star, the floor cap), the panel by real clicks. No errors of the game's own.
- 2026-10-21 03:09 The free build camera (Test_Tiles1021, real keys and mouse): WASD moves it within the hotel's area and not the avatar, the right-drag tilts, Top snaps down. No errors of the game's own.
- 2026-10-21 04:05 Built rooms (Test_Rooms1021a-f): stages 1-2 by remotes (schema 6, the start room, walls refused where A.12 says, a second room typed and furnished, guests walked through doors to the beds with the bars' pay, Comfort only rising, cleaning at the door, each chain hotel its own samples, the tutorial with the start room); stage 3 by real mouse and keys and a simulated phone (walls drawn by drag and tap, Half cells, Door, Remove, the type list, the Bed, the room view); stage 4 the clean-up, auto walls on a tile beside a room, a rebirth. Fixed: attachments set before parenting, location-0 furniture refused, Frostfang's start room, the phone's room view off the top. No errors of the game's own.
- 2026-10-21 07:52 The world (Test_World1021a, by remotes, no window focus): three streets, Travel moving the live plot and the character, the chain drawn static on the other streets, a bus per street with its own family, Hunter Night on street 2, sightlines from street-end plots measured, parts and lights measured; fixed: guests stranded on a street left without a bus, far street lamps' lights. No pictures (Studio drew no frames). No errors of the game's own.
- 2026-10-21 08:01 The showcase (A.11.4) played by remotes on Test_Endless1021a: likes, weekly count, milestone, favourite, panel, daily visits; two-player items open.
- 2026-10-21 08:06 Residents level up (A.11.6) played by remotes on Test_Endless1021b: XP at work, refusals, two level-ups with the Wing rate and efficiency measured, panel and badge, levels through a rebirth.
- 2026-10-21 08:12 Deeper mutations (A.11.5) played by remotes on Test_Endless1021c: stacked residents' pay, scale and tint, the Book's stack and title, the month's mutation in March by the event clock, a Tiny bus guest; balance_model's guards flag the pay lines.
- 2026-10-21 08:35 VIP contracts (A.11.1) played by remotes on Test_VIP1021a (two playtests): offered at 3★, accepted, a room furnished to the spec and held, the VIP an extra seat on the bus booked into room 2, completed with its reward; a missed one; the daily cap; Book requests and swaps. Two fixes (free offers pruned, the reward without the VIP's own pay). The desk prompt needs Studio in front.
- 2026-10-21 09:27 Rare decor sets and souvenirs (A.11.3) played by remotes on Test_Rare1021a (two playtests): finds by pity, roll, a happy Rare stay and a defended Hunter Night; souvenirs by move-in no. 3 and a VIP contract; placing for cash and NotFound refusals; the set bonus once per set per hotel (0.567 → 0.817 in the older room only); a duplicate; rebirth and rejoin keep the finds. One fix (the duplicate's wording). Found: furniture can wall off a room's key spot (built rooms). No errors of the game's own.
- 2026-10-21 09:39 Ready means the key furniture is reached (Test_Ready1021a, by remotes, no window focus): a row of decor refused at the piece that would wall the bed off (KeyCutOff), a guest booked and walked round the row to the bed; the row closed by force: not ready (KeyUnreached) and no guest booked into it. No errors of the game's own.
- 2026-10-21 10:22 Rare decor at Frostfang Lodge and Bayou Spa (Test_Rare1021b, by remotes, no window focus): a find by pity at location 2 gave the Aurora Lodge's Rug, then its Painting; at location 3 the Lantern Grove's Rug. No errors of the game's own.
- 2026-10-22 23:45 The world's pictures (Test_World1021a, Studio in front): seven views of the three streets, a blind review triaged (WAITING §2.46, four geometry checks open). No errors of the game's own.

## Launch import (2026-10-23)

Played by remotes on the published place, profile `Test_Launch1023a`, Studio not in front (no pictures).

- [x] The 136 saved models synced: no empty MeshPart, a PrimaryPart on each, scripts match the repo.
- [x] Haunted Manor: the start hotel's walls, door, posts and Bed are kit clones (MeshIds match); nine placed decor and furniture pieces too.
- [x] Glass: 0.55 and material Glass on the vending machine, popcorn cart, salad bar (all three locations) and the facade windows.
- [x] Frostfang Lodge and Bayou Spa (`chainopen 2`, `3`): walls, door, posts and furniture are kit clones. Bayou's FrontDesk is still a blockout (no desk in its kit yet: launch #5).
- [x] No game errors; plot parts 184 / 152 / 147.
- [ ] Bookshelf and Wardrobe were not placed by the test's positions (no refusal came back): look into it.
- [ ] Pictures of the placed models, with Studio in front.
- [x] 2026-10-24 night, Launch run part 2a: persistence, Bayou's kit and the VIP lounge, the four facade packs, notifications and the rigged monsters pass; server size `[A]`, Flip `[?]`. Also run: a booked room that stops being ready sends its guest back (the night's fix), a door only in a wall with its outline on the wall pointed at (the night's fix, by a real mouse).
- [x] 2026-10-24 night, part 2d: no walk-ins, the tutorial's Slime and its Vampire Count pass; Collect `[?]` (the test profile owns Auto Collect); Tutorial Commons not run.
- [x] 2026-10-24 night, part 2e: frame time (PC simulation) and the one-finger pan pass; build mode's phone layout overlaps (WAITING §1.14); the VIP room view on a phone `[A]`.
- [x] 2026-10-24 night, part 2b: the doorways clear and the walls solid in all three kits; Phase 13's items (written before built rooms) and the gamepad not run.
