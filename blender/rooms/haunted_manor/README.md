# Haunted Manor: inner walls, a door and furniture (built rooms)

His ruling, 2026-10-21 (GDD §5.4, A.12): rooms are built by the player from
inner walls and a door, and furnished. This set is the Manor's art for that,
to the contract in `MODELS.md`, "Inner walls, doors and furniture (built
rooms)". Built by `tools/build_built_rooms.py -- sets haunted_manor`; a night
draft (2026-10-21) for his review. **Nothing here has been seen in Studio.**

## What is in it (48 models)

| Model | What | Triangles |
|---|---|---|
| `Wall_Half` | 6-stud half edge, 0.4 thick centred on the edge, 17 tall; plum wainscot, lilac paper (the Standard Room's), gold chair rail, picture rail and crown, dark skirting, on both faces; its top face gold | 132 |
| `Wall_Door` | The same with an open pointed-arch doorway, clear x -2..2, y 0..7.2; dark wood trim, gold keystone, capped plinth blocks in the trim's wood; `Door`, `Sign` | 804 |
| `Wall_Post` | The 0.6 joint post, 17.02 tall, banded as the walls meeting it: dark skirting, plum wainscot, gold chair rail, lilac paper, gold picture rail and crown | 72 |
| 14 furniture, location 1 | `Bed`, `DoubleBed`, `PlanterBed`, `FourPosterBed`, `Sarcophagus`, `WitchBed`, `DenNest`, `Coffin`, `OperaChaise`, `SnackCounter`, `Jukebox`, `Gravestone`, `ReadingDesk`, `PipeOrgan` | 140-1,080 |
| 10 furniture, location 0 (in the Manor's style) | `Nightstand`, `Wardrobe`, `WritingDesk`, `DiningTable`, `BreakfastBuffet`, `BarStool`, `PoolTable`, `CardTable`, `Bathtub`, `FloorLamp` | 282-916 |
| 21 more by purpose (night draft 2026-10-21, below) | 13 furniture, location 0; `Furniture_CrystalBallTable`, location 1; 7 `Decor_<Id>`, location 1 | 288-1,200 |

Every furniture piece is `Furniture_<Id>` on its `Pieces.luau` row's w x d
squares and layer, with `Use` and its `Pose` (Lie: the beds, coffin,
sarcophagus, nest, chaise, bathtub; Sit: the bar stool, on a declared seat;
Stand: the rest, 1.5 in front of the front edge). Reused from the approved
room models (shapes re-authored in the furniture frame, faces that shared a
plane moved 0.02-0.05 apart): the Standard Room's bed (and widened for the
double and the four-poster), the Sarcophagus Suite's sarcophagus, the Potion
Loft's bed, the Den Room's nest (a third larger for its 3 x 3), the Coffin
Suite's coffin (its lid left off; its gold bat now on the foot; 6.0 long, below), the Snack
Bar's counter, a Graveyard Garden tombstone, and `Decor_PipeOrgan`'s geometry
as `Furniture_PipeOrgan`. New: the four-poster's canopy, planter bed,
chaise, jukebox, reading desk and the ten location-0 pieces.

## More furniture and decor by purpose (night draft 2026-10-21)

His ask that night: "flesh out with more decorations and furniture for
different purposes (i.e. snack bars, breakfast buffet tables, pool tables
etc. etc.)". 21 pieces so a player can make a dining room, a game room, a
lounge, an en-suite bathroom, a garden and a lobby feel real. Every pick,
tag and price is a PLACEHOLDER for his review (`Pieces.luau`, under "More
furniture and decor by purpose"); their shapes are
`tools/build_built_rooms_more.py`, which `tools/build_built_rooms.py` runs.

**Furniture or decor** (the rule used): furniture is what a guest is walked
to and uses (sits on, eats from, plays, washes at): it has a `Use` and
counts toward the Furniture bar. Decor is what is looked at or sets the
mood, toward the Decor bar. Furniture is location 0 (any room; this is the
model until a kit has its own). The decor is the Manor's (location 1):
location-0 decor is event decor to `Pieces.decorHere`, and `always` would
ask every kit for a model. No `keyFor`: a new room type is his call.

| Purpose | Model | Use | Tags | Top |
|---|---|---|---|---|
| Dining | `Furniture_DiningChair`: crimson cushion, plum gothic back, gold finials | Sit 1.82 | — | 4.54 |
| Dining | `Furniture_SaladBar` (3 x 1): four bowls, dressings on a step, plum canopy | Stand | snacks | 4.16 |
| Dining | `Furniture_CoffeeUrn`: gold urn with a tap on a cabinet, two cups | Stand | cocoa, snacks | 4.55 |
| Dining | `Furniture_DessertTrolley` (2 x 1): layer cake, jelly, cake stand, pie | Stand | snacks | 3.5 |
| Games | `Furniture_DartsBoard` (Wall): board, three darts, chalk scoreboard | Stand | fun | 5.85 |
| Games | `Furniture_ArcadeCabinet`: glowing screen and marquee, joystick | Stand | fun | 5.62 |
| Games | `Furniture_PingPongTable` (3 x 2): teal top, net, two bats, a ball | Stand | fun | 3.05 |
| Games | `Furniture_BoardGameShelf` (Wall, 2 x 1): stacks of game boxes | Stand | fun | 5.55 |
| Lounge | `Furniture_ChessTable`: an 8 x 8 board on a pedestal, a game on | Stand | quiet | 3.28 |
| Lounge | `Furniture_CoffeeTable` (2 x 1, top 1.48): teapot, cups, biscuits, a book | Stand | — | 2.1 |
| Bathroom | `Furniture_Washstand`: basin in a marble top, gothic mirror | Stand | damp | 5.3 |
| Bathroom | `Furniture_Toilet`: dark wood seat at 1.6 (a closed lid), cistern | Sit 1.6 | — | 3.32 |
| Garden | `Furniture_GardenBench` (2 x 1): for two, wood on wrought iron | Sit 1.75 | garden | 3.61 |
| Spooky | `Furniture_CrystalBallTable`: plum cloth, glowing ball (`Glow_Cold_1`), two candles, cards | Stand | darkness | 3.9 |
| Lobby | `Decor_PlantStand`: a fern in a pot on an iron stand | — | garden | 4.6 |
| Lobby | `Decor_HallStand`: umbrella well, oval mirror, a coat and a top hat | — | antique furniture | 6.5 |
| Lobby | `Decor_LuggageCart` (2 x 1): gold bellhop cart, trunk, hatbox, cases | — | — | 4.92 |
| Lounge | `Decor_Fireplace` (Wall, 2 x 1): stone pointed arch, fire (`Glow_Warm_1`), mantel candlesticks and clock | — | candles, antique furniture | 5.66 |
| Bathroom | `Decor_TowelRack` (Wall): gold rails, a crimson and a cream towel | — | damp | 4.37 |
| Garden | `Decor_Fountain` (2 x 2): two stone tiers, water, four streams, lily pads | — | garden, damp | 4.75 |
| Spooky | `Decor_Candelabra`: iron, five candles, each flame its own glow | — | candles, darkness | 5.76 |

`fun` is the pool table's tag; no species wants it yet. The gramophone he
might expect is the Manor's `Decor_RecordPlayer` already. **New rule in
the build** (`MODELS.md`, "Nothing floats"): a `Wall` piece may hang, a
solid touching the wall's plane counted as standing (`hung_check`); the
darts board and the towel rack hang, and show floating in the elevations
(no wall is drawn there).

Validated by the build (all passed, the first run refused two, fixed): the
decor checks (footprint, 0.4 inset, layer, Pieces' w/d/layer, the decor's
height to 0.3 as a fault, the wall pieces' backs on z = 1.1, no coplanar
faces: the bench's arms and legs and the candelabra's crossed arms were
coplanar, now apart), `Use` (Stand 1.5 in front; Sit on a seat by rule 6:
1.5-2.0 high, 2 wide a person, 1.2 deep, nothing over it), nothing floating,
the budgets (1,500). Every furniture piece's height agrees with its Pieces
row to 0.3 (no new height findings). **Not done**: a blind review of these
sheets; anything in Studio; a guest walking to them.

## Fixed after the blind review (2026-10-21)

A context-free review of the sheets; geometry faults fixed in the build
script, looks left for August:

- **`FourPosterBed`**: the solid tester hid the bed and its guest from the
  raised and top-down camera. The canopy is now an open frame: plum rails
  on the posts, a plum valance hanging from each side rail, the gold band
  on the foot rail. The finials sat 0.04 above the posts: seated on them.
- **`Coffin`**: 4.95 long, a 5-stud guest's feet hung over the foot. Now
  **6.0** (z -3..3 on its 2 x 3 squares), the outline's proportions kept
  along its length, the width as it was; `Use` (0, 1.62, 0.3): the head's
  top 0.1 behind the pillow, the feet 0.7 inside the foot.
- **Every `Lie` point** now fits the 5-stud person (a new check, below).
  Moved: the beds to z -0.05 (`Bed`, `DoubleBed`, `FourPosterBed`: the
  head on the pillow's back, the feet inside the footboard; at -0.8 they
  went through it), `WitchBed` (-0.7, 1.8, -0.05) (the legs beside the
  cat), `PlanterBed` z 0.25, `Sarcophagus` z 0.15 (on its 5.35 lid; at
  -0.6 the feet hung off the end), `DenNest` (0, 0.75, 0) (centred; the
  feet were in the rim). `OperaChaise` fitted as it was.
- **`BarStool`**: the seat was 2.0 against counters 3.4-3.8. Now **2.6**
  (the stool raised 0.6 on a longer pedestal; the foot ring where a seated
  person's feet hang), `Use` (Sit) at (0, 2.6, -0.2). Its top is 3.2 (the
  back): a height finding against Pieces' 2.6.
- **`Wall_Door`'s plinths**: a grey block (the darker plum) of the
  casing's width, like an uncapped end. Now plinth blocks in the trim's own
  wood, a little wider than the casing, with a moulded cap the casing lands
  on.
- **`PipeOrgan`**: the floor-level elevation showed its pipes standing on
  nothing behind the console. Its upper case now runs back under them.
- **Not a fault**: "a full-height bar behind the doorway, from the keystone
  down" is the room behind it in the assembled shot (the far T joint's post,
  the side door's jamb). The door piece rendered alone from the same angle
  (`review/door_alone.png`) has nothing there. The buffet's cloches sit
  0.75 inside the counter's ends (elevation).
- **Not fixed**: the `Bathtub` (2 x 1 squares) holds 4.4 inside; a straight
  5-stud person needs 3 x 2 (`Pieces`, his call; second review, below). Its `Use` is waived by
  name in the build (a tub is lain in reclining). The reviewer's look
  remarks (the striped counters, the wardrobe's gold top, the organ's
  pipes, the nest's size, the coffin's closed lid, the doorway's width) are
  August's.

## Fixed after the second review (2026-10-21)

A second context-free review of the sheets; fit, not style (the approved
looks kept). The lying check now covers the whole body, arms included
(`lie_faults`: the 5-stud person's width, 3.8 across the arms; arms may lie
past a bed's edge over nothing, never through a wall), and a new
`review/sitting_sheet.png` seats the person on every seat.

- **`Coffin`**: a solid box with velvet on top laid the guest on it. Now
  open and hollow: dark wood walls 0.15 thick, a red velvet lining and
  floor at 0.6, the rim at 1.5; `Use` (0, 0.6, 0.3), in it, the head on the
  pillow. The arms went through the walls, so it is **1.36 times wider**
  (5.16 across the shoulders, within its 2 squares' 5.2), the outline's
  proportions kept; length 6.0 as before.
- **`DenNest`**: the arms lay through the rim. The rim's inside is now
  4.8 x 5.8 (the rim 0.6 thick as before, the oval 1.2 instead of 1.42), the
  nest 6.15 x 7.38 on its 3 x 3; the guest lies on the cushion inside.
- **`Bathtub`**: `Use` lowered from the water's top (1.3) to the tub's
  floor (0.75), the guest in the water; the water is no surface to the
  checks (`liquid`). Still waived: it holds 4.4 x 1.8 inside, and a straight
  person with the arms at the sides needs about 5.2 x 3.9, **3 x 2
  squares** (his call, below).
- **`SnackCounter`**: top 3.45 → **3.75**, the jars and pie with it: a
  guest on the bar stool (seat 2.6) has the thighs at 3.5, under the top
  (the sitting sheet). `BreakfastBuffet` left at 2.65: it is stood at.
- **`ReadingDesk`**: the rail standing up at the back read from the side
  as a chair's back. The book stop is now along the low front edge, and a
  level pen tray along the back holds the inkpot.
- **The walls and the post**: the post's own dark foot ring and plum body
  ended the walls' bands abruptly at a corner and a free end, and its gold
  cap sat on the crowns like a small separate block. The post is now banded
  as the walls meeting it (skirting, wainscot, chair rail, paper, picture
  rail, crown), so every band turns the corner on it; each wall's top face
  is the crown's gold, so the two crowns and the post read as one cap at a
  crossing. The review room gained a + joint and a second free end.
- **`OperaChaise`** `Use` z -0.4 → -0.65 (the arms were through its back);
  **`WitchBed`**'s cat 0.3 to the right (the legs lay through its head).
- **Found by the sitting sheet**: the `BarStool`'s foot ring was a stud
  under a seated person's feet; now at 1.42. The `PipeOrgan`'s bench stood
  0.4 from the console, a seated player's thighs in it; now 0.75 out, the
  knees ending under the keys.

**For August** (none decided here): the `Bathtub`'s size (2 x 1 stays a
reclined tub, waived; 3 x 2 fits a guest lying straight); the coffin's and
the nests' new width (fit, but a look change he has not seen); the
`PipeOrgan` is a `Stand` piece by the contract, though it has a bench a
guest could sit on (`MODELS.md`'s Pose list).

## Validated (validation.json, by the build)

- Each FBX re-imported: part names, boxes to 0.02, triangle counts, one
  material, the atlas embedded.
- Walls: the colliding boxes exactly (`Wall`; `Wall_Left`, `Wall_Right`,
  `Wall_Lintel`; `Post`), the doorway clear, `Door` (0,0,0) and `Sign`
  (0,9.6,-0.5) looking -Z, nothing outside the frame (dressing within |z|
  0.28), each piece the same turned 180 degrees, no coplanar faces.
- **Assembly**: the FBXs laid round a 2 x 2 cell room (L corners, two T
  joints, two free ends, two doors, straight runs): 0 visible coplanar
  overlaps between pieces, 402 inside posts (where the contract puts them);
  since the second review also a + joint and two free ends.
- Furniture: the kit's decor checks (footprint and 0.4 inset, layer, w/d
  from Pieces, nothing colliding, no coplanar faces, the stool's seat by
  rule 6) and `Use`: Lie/Sit points on their surface (0.15) with nothing
  over them for 1.5, Stand points where the contract says.
- **Lying** (`lie_faults`; across the whole body since the second review):
  the 5-stud person 5 long centred on each
  `Lie` point, head toward -LookVector: in the footprint, on the piece
  (falls at most 0.6), nothing through it (at most 0.45 under the legs and
  torso, 0.8 under the head's last 1.2); on the built and the re-imported
  triangles. The old points failed it (the bed's feet through its
  footboard, the coffin's and sarcophagus's off the end, the nest's in its
  rim); all pass now, the tub waived.
- **Nothing floats** (new, `grounded_check`): every shell stands on the
  floor or touches one that does. The same audit over every FBX of both
  sets found the organ's pipes and the four-poster's finials; fixed.
- The bar stool's seat by rule 6 with its top at 2.4-2.8 (`MODELS.md`).
- Budgets: walls 1,200, the post 200, furniture 1,500; all well under.
  `LOD_Proxy` (a box) on pieces wider than 2 squares or over 4 tall.

**Height findings** (Pieces' `height` is the blockouts' placeholder; src/ was
not touched): `Bed` 2.0 vs 5.0, `DoubleBed` 2.0 vs 5.0, `WitchBed` 2.2 vs
5.0 (the approved gothic headboard), `SnackCounter` 3.4 vs 4.52 (its jars),
`BarStool` 2.6 vs 3.2 (its back, over the seat at 2.6), `Coffin` 2.0 vs 1.5
(open now: its rim), `SnackCounter` 3.4 vs 4.82 (its top at 3.75 now).
The code session updates those rows or August rules the headboard lower.

## Not validated

- Anything in Studio: the import, `import_fixup.luau` (it adds `Use`'s
  `Pose` attribute), how it looks lit.
- The code placing walls, doors and posts (not written yet); walls meeting
  the facade (the post closes that joint by the contract; not assembled
  here, and a wall ending at a facade window's middle would run into it).
- A guest walking to `Use`, lying or sitting: no walker has run.
- Blind review: run once (2026-10-21, above); the fixed sheets are not
  reviewed again.

## Review

`review/walls_sheet.png` (the room from the street and from behind, a corner,
a + joint, a free end, a corner's foot
and a T close up, the door from outside and from inside as a cutaway, the
door piece alone and its plinth close up), `review/furniture_sheet.png`
(every piece on its 3-stud squares beside the 5-stud person, `Use` as a red
mark with its facing), `review/elevations_sheet.png` (every piece level at
floor height, from the front and from the side, on its squares),
`review/sitting_sheet.png` (the 5-stud person on the bar stool at the Snack
Counter, and on the organ's bench, from the side and three-quarters),
`review/lying_sheet.png` (every `Lie` piece from above and from the side
with the 5-stud person lying on its `Use`; the four-poster also from the
raised camera). The 21 pieces of 2026-10-21 have their own sheets in
`review/more/`: `furniture_sheet.png`, `elevations_sheet.png` and
`sitting_sheet.png` (the chair, the toilet and the bench with the 5-stud
person sitting). Workbench on light grey (Studio was running: no EEVEE or
Cycles).

## Staged

All 48 FBX in `blender/_import/` (unprefixed; the Lodge's walls there are
`FrostfangLodge_Wall_*`). Re-staged after the second review (2026-10-21):
`Wall_Half`, `Wall_Door`, `Wall_Post`, `Furniture_Coffin`,
`Furniture_DenNest`, `Furniture_SnackCounter`, `Furniture_ReadingDesk`,
`Furniture_WitchBed`, `Furniture_BarStool`, `Furniture_PipeOrgan`. The
`Bathtub`'s and `OperaChaise`'s moved `Use` points live in
`import_fixup.luau` (their meshes are unchanged).
The 21 new pieces staged 2026-10-21 beside them: 14 `Furniture_<Id>` and 7
`Decor_<Id>` (the table above); nothing of the earlier batch removed.
