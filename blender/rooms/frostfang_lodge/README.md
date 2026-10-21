# Frostfang Lodge: inner walls, a door and furniture (built rooms)

His ruling, 2026-10-21 (GDD §5.4, A.12): rooms are built by the player from
inner walls and a door, and furnished. This set is the Lodge's art for that,
to the contract in `MODELS.md`, "Inner walls, doors and furniture (built
rooms)". Built by `tools/build_built_rooms.py -- sets frostfang_lodge`; a
night draft (2026-10-21) for his review. **Nothing here has been seen in
Studio.**

## What is in it (11 models, and the 23 location-0 pieces below)

| Model | What | Triangles |
|---|---|---|
| `Wall_Half` | 6-stud half edge, 0.4 thick, 17 tall: 13 log courses over a dark wainscot (the lodge rooms'), light wood rails, a snow cornice, both faces; its top face snow | 276 |
| `Wall_Door` | The same with an open round-arched doorway, clear x -2..2, y 0..7.2; dark log trim, a snow keystone, capped plinth blocks in the trim's wood; `Door`, `Sign` | 1,172 |
| `Wall_Post` | The 0.6 joint post, banded as the walls meeting it: dark skirting and wainscot, light rails, the log courses, the snow cornice | 160 |
| 8 furniture, location 2 | `IceBed` (Igloo Room's bed), `IceSlab` (Ice Cave's slab under furs), `SnowNest` (Yeti Den's nest, a third larger), `GlacierCoil` (Glacier Suite's coiled bed, a third larger), `CocoaBar` (Cocoa Lounge's counter), new: `KnittingChair` (a rocking chair, a seat by rule 6, a yarn basket), `StarHammock` (navy with stars between snow-capped log posts), `SkyLounger` (a deck lounger) | 268-1,024 |

`Use` Poses: Lie for the beds, nest, coil, hammock and lounger; Sit for the
knitting chair; Stand for the cocoa bar. The Lodge's own location-0 furniture is
below (2026-10-21).

## Fixed after the blind review (2026-10-21)

- **`Wall_Door`'s plinths**: a block of another wood, the casing's width,
  like an uncapped end. Now plinth blocks in the trim's own wood, a little
  wider than the casing, with a moulded cap the casing lands on.
- **Every `Lie` point** fits the 5-stud person (the Manor's README, the new
  check): `IceBed` and `IceSlab` moved to z -0.05 (the head on the pillow's
  back), `SnowNest` (0, 0.75, 0) and `GlacierCoil` centred (the feet were
  in the rim), `SkyLounger` z -0.7 (the feet hung 0.3 off the cushion).
  `StarHammock` names its sling's rise (0.8, the head 1.1).
- **Floating** (a floor-level elevation of every piece and an audit of
  every shell): the cocoa mugs' handles stood a hair off the mugs and the
  knitting chair's blanket 0.06 behind its slats; both are now held. The
  `GlacierCoil`'s spires, the hammock's posts and ends, the cocoa bar and
  the chair's basket stand on the floor inside their squares: they only
  look apart (the spires are August's look).
- **Not a fault**: the bar behind the doorway is the room behind it (the
  Manor's README). `WillowHammock` is Bayou Spa's: not modelled.

## Fixed after the second review (2026-10-21)

Fit, not style (the Manor's README has the new checks: the lying person's
whole width, the sitting sheet).

- **`StarHammock`**: a parabola sagged 0.9 under a straight person, who
  hung over it at the posts' height. The sling's bottom is now flat under
  the body (a fourth-power curve) and rises steeply at the ends to the same
  ropes: 0.4 under the head and feet, the guest lying in the cloth. `Use`
  (0, 1.375, 0), centred; the pillow under the head; the sling's own rise
  allowance dropped (the default holds).
- **`SnowNest`**, **`GlacierCoil`**: the arms lay through the rim. Their
  inside is now 4.8 x 5.8 (the rims' thickness as before, the oval 1.2
  instead of 1.42/1.4), the guest inside; the coil's spires stand where they
  stood.
- **`SkyLounger`**: the guest lay flat with the raised back tilted behind
  the head and the pillow at the hinge. A `Lie` pose is flat (`MODELS.md`),
  so the lounger is laid flat: its back section down level with the seat,
  two teal cushions meeting at the hinge, the pillow at the head end, the
  blanket at the foot; `Use` (0, 1.05, 0.55).
- **`CocoaBar`**: top 3.45 → **3.75**, the pot, mugs and jar with it (the
  bar stool's seated guest has the thighs at 3.5). Since the blind review
  of 2026-10-21 (night) its front stands 0.6 further back (z -0.25) under
  the top, which overhangs it by 0.8: knee room for the stool, as the
  Manor's `SnackCounter` (the Manor's README).
- **The walls and the post**: banded as the walls meeting it (dark skirting
  and wainscot, light rails, the log courses, the snow cornice), each wall's
  top face snow: the Manor's README.

## Validated (validation.json, by the build)

As the Manor's set (its README): re-imported FBX checks, the walls' exact
boxes, opening, attachments, 180-degree sameness and no coplanar faces; the
assembled room (0 visible overlaps, 834 inside posts; a + joint since the
second review); furniture's decor
checks and `Use`, the lying fit and nothing floating (new, 2026-10-21).
Budgets all under (the door 1,172 of 1,200; its rails lost their chamfer
before; the Manor's rails the same).

**Height findings** (Pieces' placeholder vs the model's top): `IceBed` 2.0 vs
3.6 (the igloo-dome headboard), `IceSlab` 1.8 vs 3.87 (the rock headboard),
`GlacierCoil` 2.4 vs 4.4 (the crystal pillars), `CocoaBar` 3.4 vs 5.1 (the
cocoa pot; its top at 3.75 now).

## Not validated

Studio (import, fix-up, light), the code placing walls, a walker to `Use`,
the facade joint. The blind review ran once; the fixed sheets are not
reviewed again.

## Review

`review/walls_sheet.png`, `review/furniture_sheet.png`,
`review/elevations_sheet.png`, `review/lying_sheet.png`,
`review/sitting_sheet.png` (the knitting chair, and the Manor's bar stool at
the Cocoa Bar) (as the Manor's;
Workbench, light grey).

## Staged

Re-staged after the Manor's furniture review (2026-10-21, night):
`Furniture_CocoaBar.fbx` (the knee overhang).
Re-staged after the second review (2026-10-21): `FrostfangLodge_Wall_Half.fbx`,
`FrostfangLodge_Wall_Door.fbx`, `FrostfangLodge_Wall_Post.fbx`,
`Furniture_StarHammock.fbx`, `Furniture_SnowNest.fbx`,
`Furniture_GlacierCoil.fbx`, `Furniture_SkyLounger.fbx`,
`Furniture_CocoaBar.fbx`. Before, after the first review:
`FrostfangLodge_Wall_Door.fbx`,
`Furniture_CocoaBar.fbx`, `Furniture_KnittingChair.fbx`.

In `blender/_import/`: the walls as `FrostfangLodge_Wall_Half.fbx`,
`FrostfangLodge_Wall_Door.fbx`, `FrostfangLodge_Wall_Post.fbx` (the names
repeat the Manor's; rename to `Wall_*` on saving into
`assets/HotelKit/FrostfangLodge/`), the furniture unprefixed.

Bayou Spa (location 3) is modelled since 2026-10-21 (`blender/rooms/bayou_spa/`), a draft.

## The location-0 furniture in the Lodge's style (2026-10-21)

`MODELS.md`: the location-0 ("every location") furniture is modelled in
every kit in its style. These are the Lodge's 23, by
`tools/build_built_rooms_kits.py` (run by the main script): the Manor's
footprints, `Use` points and Poses, so the code treats them alike. The
style: pale birch with log legs and edges, carved snowflakes on the
panels, red and cream plaid, iron hardware, snow lying on the tall tops,
aurora stripes (teal, mint, violet) as accents.

| Model | What | Use |
|---|---|---|
| `Nightstand` | Birch on log feet, an aurora band on the drawer, a carved snowflake door, a mug and books | Stand |
| `Wardrobe` (2 x 1) | Birch armoire between four log posts, snowflake doors with iron strap hinges, an aurora band, a little log cabin roof with snow on both slopes (top 6.2) | Stand |
| `WritingDesk` (2 x 1) | Log legs and stretchers, aurora bands either side of the drawer, letter, inkpot, quill, mug | Stand |
| `DiningTable` (2 x 2) | Log legs, a red plaid runner, plates with napkins in aurora colours, a bowl of apples | Stand |
| `BreakfastBuffet` (3 x 1) | A table under a cream cloth, its skirt pleated, a red hem band, red snowflakes; two steel chafing dishes (one open: scrambled eggs), a cloche, pancakes with syrup and butter, plates | Stand |
| `BarStool` | Four birch legs, an iron foot ring at 1.42, a red plaid cushion at 2.6 (its seat to z -0.8), a log back rail | Sit (0, 2.6, -0.2) |
| `PoolTable` (3 x 2) | Dark log body on six log legs, green felt, birch rails with aurora sights | Stand |
| `CardTable` (2 x 2) | Green felt in a birch rim with an aurora-teal band, a log pedestal, cards and chips | Stand |
| `Bathtub` (2 x 1) | Birch staves in two iron hoops, water with foam, a rolled plaid towel, an iron pump | Lie (-0.3, 0.75, 0), waived |
| `FloorLamp` | A birch post with its dark marks on a log-slice foot, a cream shade with a red hem and a teal band, `Glow_Warm_1` | Stand |
| `DiningChair` | Birch, a plaid cushion at 1.82, a round-topped back with a carved snowflake over an aurora band | Sit (0, 1.82, -0.15) |
| `SaladBar` (3 x 1) | Snowflake panels; a well of ice with ten steel pans of salad, tongs; dressings on a step; a `Glass` sneeze guard (ice) on iron posts | Stand |
| `CoffeeUrn` | A red enamel cocoa urn over a drip tray, mugs, a log upstand with mugs and snow on top | Stand |
| `DessertTrolley` (2 x 1) | A Yule log cake with holly, a gingerbread house with a snowy roof, a jelly; a berry pie below | Stand |
| `DartsBoard` (Wall) | On a log slice with snow on it, darts with aurora flights, a chalk scoreboard | Stand |
| `ArcadeCabinet` | Navy sides with aurora waves, a frost-blue screen (`Glow_Cold_1`), an aurora marquee (`Glow_Magic_1`), snow on top | Stand |
| `PingPongTable` (3 x 2) | A navy top on log legs, a frosted net, red and teal bats | Stand |
| `BoardGameShelf` (Wall, 2 x 1) | Hung on the wall on two log brackets, 1.25 off the floor: birch, lidded game boxes in three bays, a log cornice with an aurora band and snow | Stand |
| `ChessTable` | A birch and dark-log board on a log pedestal, snow-white and navy men | Stand |
| `CoffeeTable` (2 x 1) | A birch slab with bark edges on two log rounds, a cocoa pot, mugs, gingerbread stars, a book | Stand |
| `Washstand` | A white basin in a stone top, an iron pump tap, a round-topped frosted mirror in a log frame | Stand |
| `Toilet` | White bowl on an oval 2.0 x 1.2, birch seat and lid at 1.72, a log-clad cistern with a snowflake panel | Sit (0, 1.72, -0.35) |
| `GardenBench` (2 x 1) | Birch planks on log legs and arms, two half-log back rails with snow along the top one | Sit (0, 1.75, -0.25) |

Validated by the build (`VALIDATED 34/34`; the set's walls and older
pieces are unchanged, their manifest records identical to before; only the
atlas gained 'birch', 'birch_shade' and 'felt', appended): footprint and 0.4 inset, layer and w/d
against `Pieces.luau`, no coplanar faces, nothing floating (the darts board
and the board-game shelf hang on the wall's plane), `Use` and its `Pose`,
the seats by rule 6 (the stool's at 2.6), budgets (all under 1,500), and
**every Sit piece held to the seated 5-stud person** (`sit_faults`, per
piece: `sit_figure`): the seats ended where the old figure's shins hung
(0.4 ahead of `Use`; 0.6 since the kits' blind review, below), and the
backs stand 0.3 behind the torso. The tub is waived as the Manor's (2 x 1
holds a reclined guest; 3 x 2 is August's call). Fixed during the build:
three coplanar pairs (a seat board's back face in the back legs', a tap's
column top in its spout's, a trolley post's face in the push bar's), three
pieces over budget (the aurora stripes' facets, the salad bar's bottles),
the darts board's backer too wide for 1 x 1 (now 2.2 across), the bench's
arms over the seat's 0.1 margin, three tops more than 0.3 over Pieces'
height (an apple, a lotus, a reed pen).

**Height findings** (Pieces' height against the model's top, not faults):
only `BarStool` (3.23 vs 2.6, its back rail; the Manor's has the same).

Review (Workbench on light grey, Studio running: no EEVEE or Cycles), in
`review/every/`: `furniture_sheet.png` (on their squares beside the 5-stud
person, `Use` in red), `top_sheet.png` (straight from above),
`elevations_sheet.png` (floor level, front and side), `lying_sheet.png`
(the tub with the person in it, waived), `sitting_sheet.png` (the stool at
its own Cocoa Bar; the stool, chair, toilet and bench with the person seated: side
as a section, front, three-quarter). Looked at by Claude; fixed from the
sheets: round snow lumps read as plates lying on the tops (now one long low drift), the wardrobe's gable ridge read as an open book (now a cabin roof running left to right). **Not done**: a blind review of these sheets; anything
in Studio.

### Fixed after the kits' blind review (2026-10-21)

A context-free review of the two kits' location-0 sheets; fixed in
`tools/build_built_rooms_kits.py` (and the figure in `build_built_rooms.py`),
the changed pieces rebuilt alone (`-- sets frostfang_lodge only BarStool,
DiningChair,Toilet,GardenBench,BoardGameShelf,BreakfastBuffet,SaladBar`):

- **The seated figure's rig** (the sitting sheets' side view; `sit_blocks` in
  `tools/build_built_rooms.py`, the one figure the sheets draw and `sit_faults`
  checks): its thighs were 0.9 thick and began at the torso's middle, and its
  shins, 0.9 deep, hung from 0.4 ahead of `Use`, under the thighs' middle, so
  every seat had to end under the torso's front and the side view showed lap
  and legs as one stepped block hanging in front of the seat. Now the thighs
  (0.6 thick) lie from under the torso's back to the knees 1.2 ahead, the
  shins (0.55 deep) hang from the knees (0.65 to 1.2 ahead), the feet under
  them; the soles stay 1.1 under the seat (the bar stools' rings). The new
  figure lies inside the old one's boxes, so every seat that passed still
  passes (Bayou's own throne and perch were not rebuilt).
- **The four seats run 0.6 ahead of `Use`**, under the thighs, ending before
  the shins (was 0.4, which the old rig forced): `BarStool` to z -0.8,
  `DiningChair` -0.75, `Toilet` -0.95 (its oval 2.0 x 1.4, centred at z
  -0.245, its back clear of the cistern), `GardenBench` -0.85 (its front legs
  moved to z -0.6). The backs still stand 0.3 behind the torso, and on the
  chairs (seats 1.72-1.82) the feet hang about 0.7 off the floor: rule 6's
  heights and the stools' rings, not changed.
- **The stool at the counter's side view** is a section too (the near arm
  hid the torso and thighs).
- **`BoardGameShelf`** stood on the floor as a bookcase. It is now hung on
  the wall: a case 1.45 deep from 1.25 up to its cornice, its back on the
  wall's plane (z 1.1), on two brackets fixed to the wall, nothing reaching
  the floor; held by the wall's plane (`hung_check`), as the darts board.
  Three bays of game boxes (were four), the boxes 1.0 deep. The contract is
  the Manor's (`Wall` layer, back on the wall, `Stand` 1.5 in front, 2 x 1);
  **the Manor's own shelf still stands on the floor** against the wall.
- **`BreakfastBuffet` and `SaladBar` read alike** (a panelled sideboard with
  food on top, both). The buffet is now a table under a cloth, its skirt in
  pleats with a hem band, the feet showing under it, served from two chafing
  dishes (one closed under a rolled lid, one open with a spoon), a cloche on
  a platter and a plate stack. The salad bar keeps its panelled cabinet and
  its `Glass` guard on posts and has a well of ice on its top with ten pans
  of salad in two rows (tongs in three, tomatoes or radishes heaped on two)
  and three dressings on the step. Names and `Use` as before.

Not changed (August's calls, `WAITING.md` §2.43): the `Bathtub`'s size, the
snow on the tall tops.

**Validated** (`validation.json`): the 7 rebuilt `VALIDATED 7/7` (the salad
bar once more after a trim: 1/1); the set 34/34 with no faults; every Sit
piece passes `sit_faults` with the new figure. Triangles: `BreakfastBuffet`
1,338, `SaladBar` 1,396, `BoardGameShelf` 1,196, `BarStool` 392,
`DiningChair` 768, `Toilet` 780, `GardenBench` 456. Height findings as
before (the buffet's top 3.28 against 3.0 is within 0.3).

Review: `review/every/` re-rendered for all 23 with the new figure
(Workbench). **Not done**: a second blind review; restaging (the 7 in
`blender/_import/` are the old ones); anything in Studio. The set's
`.blend` holds only the last partial build's pieces (rebuilt by the script).

### Blind review 2026-10-21 (second run)

Two context-free reviewers (another model) looked at the rebuilt pieces'
sheets. Each finding triaged, proved by the script's geometry; fixed in
`tools/build_built_rooms_kits.py` (the shared shapes changed Bayou's too),
rebuilt alone (`-- sets frostfang_lodge only SaladBar,Toilet,BoardGameShelf,
BreakfastBuffet,BarStool`):

1. **`SaladBar` an opaque slab from above** — Confirmed + fixed. Nothing
   makes `Glass` see-through: `import_fixup.luau` sets only `Glow_*` (Neon),
   `Root` and `LOD_Proxy`, and MODELS.md says the code only "may" make it
   glass, so the lid over the whole top (y 4.0, z -0.9..0.4) hid the pans in
   the game too. Now an open iron frame on four posts, its top open, a glass
   pane hung in front only (4.1-4.38: 1.1 over the food, 1.32 over the
   counter, at a standing guest's chest). *The three objects on the guard*:
   False by geometry (the dressings, tops at 3.92 under the guard at 4.0, at
   z 0.6-0.9 behind its back rail); they and their step are gone (budget).
   The pans now hold salad (finding 8, Bayou's): eight pans heaped with
   leaves, tomatoes, carrot sticks, cucumber, corn, eggs, olives, greens.
2. **`Toilet` cistern floats; the bowl reads as a goblet** — Confirmed as a
   read (the cistern stood on the bowl's back, a white block 0.84 wide that
   vanished against the floor). Now the cistern stands on a dark log casing
   down to the floor (z 0.56-1.02); the bowl stands on a wide foot (0.66,
   not a 0.44 stem under a flared bowl); the seat and lid are egg-shaped,
   narrowing to the front, the seat's rim showing round the lid, two iron
   hinges to the cistern. `Use` and the seat at 1.72 unchanged.
3. **At the Cocoa Bar the knees end ~0.5 short of the overhang** —
   Confirmed by geometry, not fixable in the model: on the square in front,
   turned to the counter, the stool's `Use` (0, 2.6, -0.2, the contract's)
   puts the knees at z -1.6 and the counter's top edge is at -1.05 (0.55
   short; the thighs, top 3.2, would pass under the top at 3.5). The 0.4
   inset on both pieces keeps their bodies 0.8 apart; even a seat to the
   inset with `Use` at -0.5 leaves the knees 0.25 short. **August's call
   (or the code's)**; recommendation: the code tucks a bar stool 0.7 toward
   a counter it faces (knees under the top, nothing touching).
4. (Bayou's lamp.)
5. **`BoardGameShelf` reads as a floor cabinet; a dark wedge at its lower
   right; the boxes read as speakers or safes** — Confirmed. Measured: the
   case's bottom at 1.25 (its apron 1.11), its brackets down to 0.3 on the
   wall; the dark wedge was the log bracket, not a missing bottom (the bottom
   board is 1.25-1.45). Now the case hangs from 2.6 (apron 2.46), two bays,
   the upper shelf at 4.0 in a 5-stud person's reach, the cornice at 5.55;
   short brackets from the case to 1.75 on the wall. Every game a wide flat
   box lying in a stack (plain base, bright lid with a picture on top and a
   title band on its front), one game open on a stack with a four-colour
   board and a pawn; no box on end.
6. **`BreakfastBuffet` reads as a desk; red snowflakes as asterisks** —
   Confirmed + fixed. Now sausages and scrambled eggs in two open steel
   chafing dishes, a log basket of rolls and a croissant, a bowl of oranges,
   an apple and a banana, orange juice in a jug and two glasses, pancakes
   with syrup and butter (the closed dish, cloche and plate stack gone); one
   white snowflake on a red roundel in the middle of the skirt.
7. **`DiningChair` and `BarStool` alike from above** — Confirmed (both a
   2.1 x 1.66 board under a square cushion). The stool's seat is now oval
   (2.1 x 1.52, the cushion's plaid ending at its edge); the chair keeps its
   square seat and its back.
11. **`BarStool` three materials, a towel-rail back** — Confirmed + fixed:
   one birch family with the dining chair (birch legs and seat, a log foot
   ring like the chair's stretchers, a low round-topped birch back with a
   carved white snowflake on two birch posts, 3.05-3.95).
12. **Two tops unreadable in the top sheet** — identified from
   `review_top`'s layout (by depth then name, four a row; the camera draws a
   row right to left): row 2's first is `BoardGameShelf`, row 6's third
   `Wardrobe`. Both are their snow from above (the shelf's snow cap on the
   cornice, the wardrobe's snow on its cabin roof). **August's call**,
   already `WAITING.md` §2.43 (snow on some pieces, white blocks from above);
   recommendation as there: no snow indoors, frost instead. Not changed.

Findings 4, 8 (the pans: fixed here too), 9 and 10 are Bayou's (its README).

**Validated**: the 5 rebuilt `VALIDATED 5/5`, no faults; every Sit piece
passes `sit_faults` (the stool's and the toilet's new seats included).
Triangles: `SaladBar` 1,492, `BreakfastBuffet` 1,346, `BoardGameShelf`
1,308, `Toilet` 806, `BarStool` 556 (budget 1,500). Height findings:
`BarStool` 3.96 vs 2.6 (its back; was 3.23); the salad bar 4.44 vs 4.2 and
the shelf 5.72 vs 5.6 are within 0.3.

Review: `review/every/` re-rendered for all 23 (Workbench). **Not done**: a
third blind review; restaging (`blender/_import/` holds the old ones);
anything in Studio.

Staged 2026-10-21 in `blender/_import/` as `FrostfangLodge_Furniture_<Id>.fbx`
(the 23; the names repeat the Manor's: rename to `Furniture_<Id>` on saving
into `assets/HotelKit/FrostfangLodge/`), beside what was there.

### Blind review 2026-10-21 (third run)

A third pair of context-free reviewers (another model) looked at the rebuilt pieces. Each finding triaged,
proved by the script's geometry where it could be; fixed in `tools/build_built_rooms_kits.py` (shared shapes
changed Bayou's too), rebuilt alone (`-- sets frostfang_lodge only Toilet,SaladBar,BoardGameShelf,
BreakfastBuffet,Nightstand,CoffeeUrn`):

1. **`Toilet` a cabinet beside a hatbox; from above like the `Washstand`** — Confirmed + fixed: one white ceramic toilet as the Manor's that passed (bowl on a foot running up into a white deck, a low white cistern 1.58-2.8 standing on it, only its lid log with bark edges); a birch seat ring at 1.72 round a dark opening with the white rim showing round it from above; the lid raised on two iron hinges against the cistern (z 0.4-0.49, behind the torso at 0.15); a spare roll on the lid. `Use` and seat height unchanged; `sit_faults` clean.
2. **`SaladBar` guard a glass cage (pane flat as a roof, frame on four sides)** — Confirmed + fixed: one row of five pans along the front (the guest stands only there, Stand), a pane sloping from 4.45 over the pans' back edge down to 3.8 over the front edge (0.8 over the food) between two iron end posts and brackets, open behind and above; plates behind. The carrot zigzag (three long sticks) Confirmed: now eight short sticks heaped; the pans hold lettuce, cherry tomatoes, cucumber slices, carrots, egg halves with yolks. The sheets now draw `Glass` see-through, as the code makes it in the game (`build_built_rooms.py` `_see_through`).
3. **`BreakfastBuffet` red octagon = stop sign; cups as crumbs** — Confirmed + fixed: the roundel (twelve-sided, red) is now a navy shield edged in gold with the white snowflake; the two orange glasses (r 0.1) are two cream mugs with red bands and handles (r 0.18).
4. **`BoardGameShelf` lopsided; top boxes clipping the cornice** — Lopsided False by geometry (both brackets were at x ±1.5..1.7, both sides 2.3-2.5: the three-quarter camera saw the right bracket inside the case, the left hidden), clipping False by geometry (0.44 air over the upper stacks) but both Confirmed as reads (the cornice's overhang and aurora hid the air from an elevated camera) + fixed: the brackets now stand under the two sides, short (to 2.0); the cornice overhangs 0.04; every bay has 0.14-0.6 air; games read as games (boxes stood up showing a four-colour board under a white title band, deep two-box stacks with a lid a hair wider, one game open with its board and pawns, dice).
5. (Bayou's stool.)
8. **Seated feet hang 0.6-0.7 over the floor** — Confirmed by geometry, not changed (as asked): the figure's soles are 1.1 under the seat (thighs 0.6 thick, shins 0.8, shoes 0.3), so the `DiningChair` (1.82) leaves them at 0.72, the `Toilet` (1.72) 0.62, the `GardenBench` (1.75) 0.65; the `BarStool`'s (2.6) rest on its ring at 1.5. **August's call**, kit-wide with the Manor's seats and MODELS.md rule 6 (1.5-2.0, "the legs are 2"): check a real avatar seated in Studio first.
9. **Blank or dotted tops** — identified from `review_top` (by depth then name, four a row, drawn right to left): row 2 #1 `BoardGameShelf` and row 6 #3 `Wardrobe` are snow (**August's call**, WAITING §2.43, not changed); row 2 #4 `ArcadeCabinet` is snow too (same call); row 3 #1 `CoffeeUrn` now has marshmallows in its two mugs; row 5 #3 `Nightstand` now a book lying open and marshmallows in the mug (the two closed books gone). **`CocoaBar`'s stripes** (circus tent) — False as a fault: it is the Cocoa Lounge's candy-cane counter by design (the approved room's); **August's call** if he wants it otherwise (recommendation: keep; else birch planks with one red band).

Findings 5, 6 and 7 are Bayou's (its README).

**Validated**: the 6 rebuilt `VALIDATED 6/6`, no faults; every Sit piece passes `sit_faults`. Triangles: `BreakfastBuffet` 1,486, `SaladBar` 1,468, `BoardGameShelf` 1,452, `CoffeeUrn` 1,158, `Nightstand` 816, `Toilet` 762 (budget 1,500). Height findings: `Toilet` 3.27 vs 3.6 (lower: the low cistern), `BarStool` 3.96 vs 2.6 as before.

Review: `review/every/` re-rendered for all 23 (Workbench). **Not done**: a fourth blind review; restaging (`blender/_import/` holds older ones); anything in Studio.

### Blind review 2026-10-21 (fourth run)

A fourth pair of context-free reviewers (another model). Each finding triaged, proved by the script's geometry; fixed in `tools/build_built_rooms_kits.py` (shared shapes changed Bayou's too), rebuilt alone (`-- sets frostfang_lodge only SaladBar,BreakfastBuffet,BoardGameShelf,Toilet,BarStool,Nightstand,CoffeeUrn`):

1. **`SaladBar` plates behind the guard; pane 1 over the counter's edge, pans flush, its lower edge held by nothing** — Confirmed + fixed (all three): the plates (z 0.5, the staff's side) now stand at the row's start in the pans' row (x -3.38, the guest's end; four pans, the cucumber pan gone for the room and the budget); the old pane's lower edge was at 3.8 over z -0.88, 1.02 over the counter (2.78) and 0.8 over the fill; now 4.6 over z -0.95, 1.6 over the pans' fill (3.0), its back 5.0; the ice well 0.17 back from the top's front edge (was 0.08), the pans 0.28 (was 0.19); each end a closed triangle (post, bracket along the pane's end, a strut from the post at 3.9 to the lower corner) and an iron rail along the lower edge.
2. **`BreakfastBuffet` red band past the top; the jug a pumpkin; cream/tan stripes as doors** — Band Confirmed (hem band z -1.08, its cream line -1.095, the top's front -1.06) + fixed: the cloth's top now runs to -1.1, past the band and badge. Jug Confirmed (orange, octagonal, r 0.25) + fixed: a white enamel pitcher with a navy spout and handle, orange juice in its mouth. Stripes Confirmed as a read + fixed differently: the pleats are one cream (as Bayou's third-run fix); no doors or handles, since this piece is a cloth-skirted table on purpose (as a panelled cabinet it read as the salad bar, the kits' first review).
3. **`BoardGameShelf` sides ending in dark stubs; a smeared rainbow under the top; the top at 5.25+** — Stubs Confirmed (the log-dark brackets under the sides, reaching to z 0.05, 0.4 behind the front) + fixed: each bracket a birch knee against the wall, its tip at z 0.45 (0.8 behind the front), the sides still ending flush with the apron at the case's bottom. Ribbon identified: the aurora band (teal, mint, violet, two waves) on the cornice's front; removed. Top Confirmed (cornice at 5.35, snow to 5.52) + fixed: the case 0.2 lower (from 2.4) and its upper bay 0.09 lower (1.12 clear, 0.17 air over the tallest game), the cornice's top at 5.06, a game box and a die lying on the snow (model top 5.41).
4. **`Toilet` a goblet foot; lid wider than the cistern; the back touching the lid; a grey tile under it** — Foot Confirmed (radius 0.66 at the floor, a 0.54 waist at 0.55) + fixed: widest at the floor (0.74) and straight up to the bowl (0.68 at 0.55), the block behind the bowl straight-sided (it widened from z 0.45 at the floor to 0.97). Lid Confirmed (±0.81 against the cistern's ±0.74, its front 0.25 behind the torso's back at z 0.15) + fixed: a flat plate ±0.7 with a birch panel inside its rim, its front at z 0.47 (0.32 clear), the cistern moved back 0.06. Tile False: it is the review's footprint plate (`_squares`, y -0.06..-0.01) drawn under every piece, not in the FBX.
7. **`Nightstand` and `CoffeeUrn` bits past the top's front edge** — Confirmed: the nightstand's top ended at z -0.88 with the aurora's violet stripe to -0.89, the carved flake to -0.91 and the iron knobs to -0.93; the urn's at -0.98 with the flake to -1.01 and the knob to -1.04. Not off-palette (violet is the Lodge's aurora). Fixed: the tops now overhang the fronts (-0.98, -1.08).
8. **`GardenBench`: thighs a fraction over the slats (front of the sitting sheet)** — False: the planks' top is 1.75, `Use` is 1.75 and the thighs' underside is `Use`; the camera looks down 14°, so the thighs' front edge, 0.6 past the seat's front, draws lower than the slats behind it. Not changed.
9. **Taste, August's call (not changed)**: the three big carved snowflakes on the salad bar's doors against one shield on the buffet. Recommendation: keep them, since carved flakes are the Lodge's panel language (as on the nightstand and wardrobe) and the shield is the buffet's own badge.

Findings 5 and 6 are Bayou's (its README). Of them, 6 (a seat tab behind the stool's cushion) was in the shared seat, so this `BarStool` lost its tab too, its back's posts raked up from the board's back edge.

**Validated**: the 7 rebuilt `VALIDATED 7/7`, no faults; every Sit piece passes `sit_faults`. Triangles: `BreakfastBuffet` 1,498, `SaladBar` 1,388, `BoardGameShelf` 1,324, `CoffeeUrn` 1,158, `Toilet` 818, `Nightstand` 816, `BarStool` 544 (budget 1,500). Height findings: `SaladBar` 5.03 vs 4.2 (the raised guard), `BarStool` 3.95 vs 2.6, `Toilet` 3.27 vs 3.6.

Review: `review/every/` re-rendered for all 23 (Workbench). **Not done**: a fifth blind review; restaging (`blender/_import/` holds older ones); anything in Studio.
