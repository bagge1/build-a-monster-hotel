# Bayou Spa: inner walls, a door and furniture (built rooms)

His ruling, 2026-10-21 (GDD §5.4, A.12): rooms are built by the player from
inner walls and a door, and furnished. This set is Bayou Spa's art for that,
to the contract in `MODELS.md`, "Inner walls, doors and furniture (built
rooms)". Built by `tools/build_built_rooms.py -- sets bayou_spa` (2026-10-21).
**A draft**: the location itself is a draft for his picks (`WAITING.md`
§2.36), and there were no approved Bayou room models to reuse, so every
shape is new. **Nothing here has been seen in Studio.**

The style asked for: a swamp spa, cosy not grim. Mossy weathered cypress,
sage, lily greens and lotus pinks, mud and still water, steam, warm lantern
and firefly light (its own palette, `BS_PALETTE`, ending in the glows
`flame`, `lamp`, `firefly` (Warm) and `moonglow` (Cold)).

## What is in it (12 models, and the 23 location-0 pieces below)

| Model | What | Use | Top | Triangles |
|---|---|---|---|---|
| `Wall_Half` | 6-stud half edge, 0.4 thick, 17 tall: a cypress wainscot under soft sage, light cypress chair and picture rails, a moss crown with a scalloped moss fringe hanging under it (4 scallops a half edge, meeting at a point on the ends), both faces | — | 17 | 324 |
| `Wall_Door` | The same with an open round-arched doorway, clear x -2..2, y 0..7.2; dark cypress trim, a light cypress keystone under a moss cap hanging in three scallops, capped plinth blocks; `Door`, `Sign` | — | 17 | 1,068 |
| `Wall_Post` | The 0.6 joint post, banded as the walls meeting it, its upright edges chamfered 0.08 | — | 17.02 | 136 |
| `Furniture_LilyPadBed` (3 x 3) | A giant lily pad, its rim turned up, on a moss mound; veins, a linen petal sheet under the head and torso and a pale petal blanket over the legs (4 wide, the whole body on them), a lotus-bud pillow, two lotus flowers | Lie (0, 0.82, 0) | 1.28 | 1,074 |
| `Furniture_WillowHammock` (3 x 2) | Woven rattan (two-tone chords) 3.9 wide, slung between two gnarled cypress posts crowned with weeping willow, a firefly jar on a hook branch off each post's front (`Glow_Warm_1`, `_2`); the sling level under the whole body (to x ±2.5), rising past its ends to the ropes | Lie (0, 1.375, 0) | 3.9 | 872 |
| `Furniture_MudTub` (2 x 3) | An oval tub of cypress staves (alternate faces a lighter wood, no raised seams), two copper hoops, mud to the brim with bubbles, a rolled towel under the head, towels folded on the rim | Lie (0, 0.6, 0), on the floor under the mud | 2.26 | 856 |
| `Furniture_HerbBed` (2 x 3) | Weathered bed, moss mattress, lavender quilt with sage bands, a headboard of rattan reed bundles bound in copper with three herb bundles hung drying against the reeds, a planter of herbs as its footboard | Lie (0, 1.8, 0) | 4.4 | 1,262 |
| `Furniture_SteamPool` (3 x 3) | A round hot pool (floor 0.1, water 1.1-1.15, wall 1.2) in a ring of flat-bottomed boulders (some mossy), steam curling off the two back stones, a lantern on the back stone (`Glow_Warm_1`), a smooth stone headrest, lily pads and a lotus on the water | Lie (0, 0.1, 0), on the floor under the water | 2.83 | 1,492 |
| `Furniture_CypressThrone` (2 x 2) | A throne carved from a cypress stump: root flare, moss cushion 3.84 wide between root-knee arms standing 3.92 apart, a high carved back (4.9 wide) with a lighter inset, Spanish moss over its shoulders, a firefly jar on a crooked branch (`Glow_Warm_1`) | Sit (0, 1.8, -0.8), a declared seat 2.1 x 1.2 (its front at z -1.2, where the shins hang) | 5.0 | 638 |
| `Furniture_LagoonPerch` (3 x 3) | A smooth moonstone boulder, long across and shallow (4.1 x 2.1), a lily-pad cushion at its front, facing a little lagoon (lily pads, a lotus, a frog); a glowing crescent moon on a cord from a reed stalk (`Glow_Cold_1`); cattails; its stones flat-bottomed | Sit (0, 1.73, 1.95), a declared seat 2.1 x 1.2 | 4.07 | 1,438 |
| `Furniture_JazzStage` (3 x 2) | A low porch stage of two-tone weathered boards on a velvet skirt, three footlights (`Glow_Warm_1`-`_3`), a vintage microphone, an upright bass, a stool with a straw boater, a string of warm bulbs between two posts (`Glow_Warm_4`), its lowest bulb 5.4 over the deck | Stand | 6.99 | 1,220 |
| `Furniture_LilyBasin` (3 x 3) | A round stone pond with a pale coping, still water, five notched lily pads, two lotus flowers, a mossy rock, a frog on the rim, cattails with a firefly on one (`Glow_Warm_1`) | Stand | 2.89 | 1,484 |

Poses chosen here (his to change): the soaking pieces (`MudTub`,
`SteamPool`) are `Lie` in a liquid, as the Manor's `Bathtub` (the mud and the
water are no surface to the checks), both big enough to hold the 5-stud
person straight, so no waiver; `LagoonPerch` is a seat (`Sit`), `JazzStage`
and `LilyBasin` are `Stand` (the guest stands in front, listening or
looking). Nothing is `Glass` or `Jet_<n>`: the steam is plain geometry on the
stones (no part the code dresses). `LOD_Proxy` on every 3-wide piece and
those over 4 tall, as the kit makes it.

## Validated (validation.json, by the build)

All 12 built and re-imported from their FBX clean (`VALIDATED 12/12`):

- Walls: the exact colliding boxes, the doorway 4 x 7.2 clear, `Door` and
  `Sign` where the contract puts them, nothing outside the frame, the piece
  the same turned 180°, no coplanar faces; assembled round a 2 x 2 room (L
  corners, a T, a + joint, free ends, two doors): **0 visible overlaps**,
  429 inside posts.
- Furniture: footprint and 0.4 inset, layer and w/d against `Pieces.luau`,
  `Use` and its `Pose`, the **5-stud person lying** on every Lie point across
  its whole width (arms included: on the piece, nothing through the body,
  the head on its pillow), the **seats** by rule 6 (1.5-2.0 high, 2 wide,
  1.2 deep, nothing over them for 3), the **5-stud person seated** on every
  Sit point (new, `sit_faults`, this set only so far: torso, head, arms,
  level thighs, hanging shins and feet as boxes, no face of the piece inside
  any, 0.03 slack), **nothing floating**, no coplanar faces, budgets (all
  under 1,500; walls under 1,200 and 200).
- Fixed during the build: the pool's and perch's boulders dipped 0.08-0.1
  under the floor (lifted); three pieces were over 1,500 triangles (facets
  trimmed, one lily pad less).

**Height findings** (Pieces' placeholder vs the model's top, not faults;
src/ untouched): `LilyPadBed` 0.8 vs 1.28, `WillowHammock` 3.0 vs 3.9,
`HerbBed` 2.0 vs 4.4 (the headboard), `SteamPool` 1.2 vs 2.83 (the steam),
`JazzStage` 1.2 vs 6.99 (the light posts), `LilyBasin` 1.0 vs 2.89 (the
cattails).

## Blind review (2026-10-21) and its fixes

A context-free review of `review/` found eight faults of fit and
construction; all fixed in the build script, re-validated (12/12, 0 visible
overlaps in the assembly) and re-staged:

1. **The seated figure stood** (legs straight down through the throne's
   seat; standing on the perch). The sheet's figure was seated already
   (thighs level, shins down), but the near armrest hid its thighs in the
   side view, the seat front ran through its shins, and from the front knee
   and shin were one slab. Now the side view is a section just outside the
   torso (the near arm and armrest cut away), the thighs a lighter blue and
   dark feet point 0.3 past the knees; a new check, `sit_faults`, holds every
   Bayou seat to that figure. The throne's seat front moved to z -1.2 (was
   -1.6), its arms out to 1.96-2.56 (were 1.25-1.88; they and their knobs
   went through the person's arms), the cushion 3.84 wide, the back 4.9; the
   perch's boulder is 4.1 x 2.1 (was a round 4.1 x 2.9), the cushion and
   `Use` 0.25 forward, the shins hanging clear in front of the stone.
2. **JazzStage**'s bulbs sagged to 2.6 over the deck. Raised to 5.4 over it
   (posts 5.88, the string nearly taut), clear of a 5-stud person's head by
   0.4. The review asked for 7: a `Floor` piece is at most 7 tall (MODELS.md)
   on a 0.9 deck, so no bulb can be over 6.1 above it.
3. **WillowHammock** was 2.4 wide and its x^4 curve rose 0.36 under the head
   and feet: the sling is 3.9 wide and level to x ±2.5 (the body's ends),
   rising in three chords a side to the ropes; the lanterns moved to hook
   branches off the posts' fronts (x ±3.77, z -0.88), clear of it.
4. **SteamPool**: the guest lay at the rim's height. The floor is 0.1 (was
   0.3), the water 1.1-1.15 (was 0.95-1.0), the wall 1.2: only the head's
   top shows over the water. The rim boulders stand flat (`boulder()`; they
   were spheres on their points), and so do the perch's two stones.
5. **HerbBed**: the head ran under the three herb bundles. The bundles hang
   against the reeds (z 2.78, were 2.7) and `Use` is at z 0 (was 0.3): the
   head's top 0.08 short of them.
6. **LilyPadBed**: the petal blanket stopped at the waist and the upper body
   bridged a 0.14 gap over the pad. A linen petal sheet now runs under the
   head and torso; it and the blanket are 4 wide (the arms on them).
7. **The dark slit at a joint** was the post's square edge, 0.1 proud of the
   wainscot, in shade (the Manor's and the Lodge's show the same). The Bayou
   post's upright edges are chamfered 0.08: no dark slit in the joint
   close-ups.
8. **The bright green block on the arch's crown** was the lily-green
   keystone: now a light cypress keystone (0.88 x 0.85) under a moss cap
   hanging in three scallops.

Not changed (his call): the doorway's width, the lily basin and the steam
pool alike from above, the walls not swampy enough, the willow trees' shape;
the Stand points are the contract.

The Manor's and the Lodge's seats are not yet held to `sit_faults`
(`SIT_FIGURE`, per style): turn it on when they are next rebuilt.

## Not validated

Studio (import, fix-up, light), the code placing walls, a walker to `Use`,
the facade joint. The fixes were seen in the Workbench sheets only.

## Review

`review/walls_sheet.png`, `review/furniture_sheet.png`,
`review/elevations_sheet.png`, `review/lying_sheet.png` (top-down and side
with the 5-stud person lying), `review/sitting_sheet.png` (the throne and
the perch with the person seated, the side view a section); Workbench on light grey (Studio was
running: no EEVEE or Cycles). Not in git; rebuilt by the script.

## Staged

In `blender/_import/` (the nine the blind review changed re-staged
2026-10-21: `Wall_Door`, `Wall_Post`, `LilyPadBed`, `WillowHammock`,
`HerbBed`, `SteamPool`, `CypressThrone`, `LagoonPerch`, `JazzStage`): the walls as `BayouSpa_Wall_Half.fbx`,
`BayouSpa_Wall_Door.fbx`, `BayouSpa_Wall_Post.fbx` (the names repeat the
other kits'; rename to `Wall_*` on saving into `assets/HotelKit/BayouSpa/`),
the nine furniture pieces unprefixed (`Furniture_LilyPadBed.fbx` …).

## The location-0 furniture in the Spa's style (2026-10-21)

`MODELS.md`: the location-0 ("every location") furniture is modelled in
every kit in its style. These are the Spa's 23, by
`tools/build_built_rooms_kits.py` (run by the main script): the Manor's
footprints, `Use` points and Poses, so the code treats them alike. The
style: weathered cypress on flared root feet, drift-grey tops, louvred
two-tone rattan panels, moss hanging off the edges, copper and brass, lily
pads, lotus flowers, frogs, firefly jars.

| Model | What | Use |
|---|---|---|
| `Nightstand` | Cypress on root feet, rattan drawer and door, moss off the top, a firefly jar (`Glow_Warm_1`), a towel with a lotus | Stand |
| `Wardrobe` (2 x 1) | Louvred rattan doors in dark frames, a round-arched top with a lily-pad medallion, Spanish moss off the cornice | Stand |
| `WritingDesk` (2 x 1) | Root legs, a weathered top with moss off its corner, a lily-pad paperweight, a copper inkpot and reed pen, a pot of moss | Stand |
| `DiningTable` (2 x 2) | Root legs, a woven rattan runner, plates on lily-pad mats, a lotus in a stone bowl | Stand |
| `BreakfastBuffet` (3 x 1) | A table under a linen cloth, its skirt pleated over a woven rattan hem band, moss off its end; two copper chafing dishes (one open: beignets), a copper cloche, a copper coffee pot, plates, berries | Stand |
| `BarStool` | A cypress root pedestal, a copper foot ring at 1.42 (0.72 across), a lotus-pink cushion at 2.6 (its seat to z -0.8), a woven rattan back up to the shoulders under a round-topped cypress crest with a lotus (top 4.5) | Sit (0, 2.6, -0.2) |
| `PoolTable` (3 x 2) | Cypress on six root legs, moss off the apron, green felt, weathered rails, lotus sights | Stand |
| `CardTable` (2 x 2) | Green felt in a cypress rim, a root pedestal, cards, chips, a firefly jar (`Glow_Warm_1`) | Stand |
| `Bathtub` (2 x 1) | A copper soaking tub on four frogs, water with two lily pads, a brass tap, a frog on the rim | Lie (-0.3, 0.75, 0), waived |
| `FloorLamp` | A big glowing jar of fireflies (`Glow_Warm_1`, 1.2 across, 1.2 tall) cradled in three prongs on a crooked cypress branch on a stone, a brass foot and lid, a small lily pad with a lotus on top, cattails | Stand |
| `DiningChair` | Root legs, a lotus cushion at 1.82 on a rattan seat, a peacock fan back of woven rattan | Sit (0, 1.82, -0.15) |
| `SaladBar` (3 x 1) | Rattan panels, moss off the top; a well of ice with ten brass pans of herbs, radishes, corn, berries and greens, tongs; dressings on a step; a `Glass` guard on brass posts | Stand |
| `CoffeeUrn` | A copper tea urn, cups on saucers, an upstand with jars of chamomile, lavender and herbs, moss off its top | Stand |
| `DessertTrolley` (2 x 1) | A lotus-pink layer cake with a lotus, a frog-green jelly, beignets; a pecan pie below | Stand |
| `DartsBoard` (Wall) | On a round woven rattan backer with Spanish moss off its rim, lotus flights, a slate scoreboard | Stand |
| `ArcadeCabinet` | Cypress with lily-green sides and a lily pad each, a moon-glow screen (`Glow_Cold_1`), a firefly marquee (`Glow_Warm_1`) with moss over it | Stand |
| `PingPongTable` (3 x 2) | A deep water-green top on root legs, a reed-green net, lotus and lily bats | Stand |
| `BoardGameShelf` (Wall, 2 x 1) | Hung on the wall on two cypress brackets, 1.25 off the floor: cypress, a rattan back, lidded game boxes in three bays, moss off the cornice | Stand |
| `ChessTable` | A linen and dark-cypress board on a root pedestal, linen and moss men | Stand |
| `CoffeeTable` (2 x 1) | A live-edge cypress slab on two root stumps, a copper teapot, cups, a lotus bowl, a frog | Stand |
| `Washstand` | A stone basin, a copper tap, an oval moonstone mirror in cypress with moss over it, a lotus | Stand |
| `Toilet` | White bowl on an oval 2.0 x 1.2, cypress seat and lid at 1.72, a rattan-fronted cistern, a fern on top | Sit (0, 1.72, -0.35) |
| `GardenBench` (2 x 1) | Weathered planks on root legs, a rattan back, moss and a frog on its top rail | Sit (0, 1.75, -0.25) |

Validated by the build (`VALIDATED 35/35`; the set's walls and older
pieces are unchanged, their manifest records identical to before; only the
atlas gained 'berry' and 'felt', appended): footprint and 0.4 inset, layer and w/d
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
only `BarStool` (3.34 vs 2.6, its back rail; the Manor's has the same).

Review (Workbench on light grey, Studio running: no EEVEE or Cycles), in
`review/every/`: `furniture_sheet.png` (on their squares beside the 5-stud
person, `Use` in red), `top_sheet.png` (straight from above),
`elevations_sheet.png` (floor level, front and side), `lying_sheet.png`
(the tub with the person in it, waived), `sitting_sheet.png` (the stool at
the Manor's Snack Counter (the Spa has no counter; its top is the Cocoa Bar's 3.75); the stool, chair, toilet and bench with the person seated: side
as a section, front, three-quarter). Looked at by Claude; fixed from the
sheets: none beyond the build's own refusals. **Not done**: a blind review of these sheets; anything
in Studio.

### Fixed after the kits' blind review (2026-10-21)

A context-free review of the two kits' location-0 sheets; fixed in
`tools/build_built_rooms_kits.py` (and the figure in `build_built_rooms.py`),
the changed pieces rebuilt alone (`-- sets bayou_spa only BarStool,
DiningChair,Toilet,GardenBench,BoardGameShelf,BreakfastBuffet,SaladBar,
FloorLamp`):

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
- **`FloorLamp`**: the light was a small firefly jar under a lily pad 2
  wide; it read as a pole with something small on it. The light is now the
  lamp: a big glowing jar of fireflies (`Glow_Warm_1`, 1.2 across, 3.7 to
  4.84) cradled in three prongs at the top of the crooked branch, a brass
  foot and lid, a small lily pad with a lotus on the lid.
- **`BarStool`** had no back to speak of (a band 0.7 high). Now woven
  rattan between two posts up to the shoulders under a round-topped light
  cypress crest with a lotus (top 4.5), 0.3 behind the torso; its foot ring
  0.72 across (was 0.64), under the feet.

Not changed (August's calls, `WAITING.md` §2.43): the `Bathtub`'s size.

**Validated** (`validation.json`): the 8 rebuilt `VALIDATED 8/8`; the set
35/35 with no faults; every Sit piece passes `sit_faults` with the new
figure. Triangles: `BreakfastBuffet` 1,434, `SaladBar` 1,476,
`BoardGameShelf` 1,052, `BarStool` 576, `DiningChair` 616, `Toilet` 848,
`GardenBench` 872, `FloorLamp` 870. Height findings: `BarStool` 4.5 vs 2.6
(its back; was 3.34); the lamp's top 5.26 against 5.5 is within 0.3.

Review: `review/every/` re-rendered for all 23 with the new figure
(Workbench). **Not done**: a second blind review; restaging (the 8 in
`blender/_import/` are the old ones); anything in Studio; the set's own
`review/sitting_sheet.png` (throne, perch) still shows the old figure. The
set's `.blend` holds only the last partial build's pieces.

### Blind review 2026-10-21 (second run)

Two context-free reviewers (another model) looked at the rebuilt pieces'
sheets. Each finding triaged, proved by the script's geometry; fixed in
`tools/build_built_rooms_kits.py` (the shared shapes changed the Lodge's
too), rebuilt alone (`-- sets bayou_spa only SaladBar,Toilet,FloorLamp,
BoardGameShelf,BreakfastBuffet,BarStool,DiningChair`):

1. **`SaladBar` an opaque slab from above, teal as the ping-pong table; the
   guard under a stud over the trays** — Confirmed + fixed. Nothing makes
   `Glass` see-through: `import_fixup.luau` sets only `Glow_*` (Neon),
   `Root` and `LOD_Proxy`, and MODELS.md says the code only "may" make it
   glass, so the water-teal lid over the whole top (y 4.0, z -0.9..0.4) hid
   the pans in the game too; it was 0.97 over the food, the guest standing
   at `Stand` (0, 0, -3.0), 1.95 in front of the counter. Now an open brass
   frame on four posts, its top open, a glass pane (`moonstone`) hung in
   front only, 4.1-4.38: 1.1 over the food's beds, 0.94 over the tallest
   tomato, 1.32 over the counter, at a standing guest's chest, who reaches
   in under it. The ice is crushed white (`steam`), not `water_light`, so
   nothing from above is the ping-pong table's teal.
2. **`Toilet` cistern floats; from above an oval side table with a plant** —
   Confirmed as a read (the cistern stood on the bowl's back, a white block
   0.84 wide; a fern in a pot stood on the cistern; the seat was an oval 2
   wide and 1.4 deep). Now the cistern stands on a dark cypress casing down
   to the floor (z 0.56-1.02); the bowl on a wide foot; the seat and lid
   egg-shaped, narrowing to the front, the seat's rim showing round the
   lid, two brass hinges to the cistern; the fern gone. `Use` and the seat
   at 1.72 unchanged.
3. **`BarStool` at the counter sits with its back to it in the front views**
   — False. The stool's `Use` looks -Z and its back stands at z 0.68-0.84,
   behind the sitter; at the counter it is turned 180°, so the back is at
   z -3.62..-3.86, away from the counter (top edge -1.05), as the side view
   shows. The row's "front" and three-quarter views look from -Z, from
   behind the sitter, so the back stands between the camera and the person,
   not between the person and the counter. (The knees short of the counter
   are the Lodge's finding 3, the same for every kit: August's call.)
4. **`FloorLamp` a honey pot; from above a potted plant** — Confirmed for
   the top. The jar is `Glow_Warm_1`, which `import_fixup.luau` makes Neon
   (warm 255, 200, 140) with a light, so its olive is the Workbench atlas
   colour, not the game's; but the closed brass lid with a lily pad and a
   lotus hid the glow from above. Now a lantern: six brass straps cage the
   jar, its mouth an open brass ring (the glow showing inside it and round
   it from above) under an arched bail handle; the lily pad and lotus sit on
   the stone at its foot.
5. **`BoardGameShelf` reads as a floor cabinet** — Confirmed. Measured: the
   case's bottom at 1.25 (its apron 1.11), its brackets down to 0.3 on the
   wall. Now it hangs from 2.6 (apron 2.46), two bays, the upper shelf at
   4.0 in a 5-stud person's reach, the cornice at 5.55; short brackets from
   the case to 1.75 on the wall. Every game a wide flat box lying in a stack
   (plain base, bright lid with a picture and a title band), one open with a
   four-colour board and a pawn.
6. **`BreakfastBuffet`: the chafing dish a treasure chest, the egg tray a
   sushi board** — Confirmed + fixed. No closed lid or cloche: shrimp and
   grits and scrambled eggs heaped in two open copper chafing dishes, a
   rattan basket and a plate of sugared beignets, a stone bowl of a peach, a
   berry, a green apple and an orange, the copper coffee pot, a cup on its
   saucer.
7. **`DiningChair` and `BarStool` alike from above** — Confirmed (both a
   square cushion). The stool's seat is now oval (2.1 x 1.52); the chair
   keeps its square seat and its fan back.
8. **`SaladBar` trays flat colours with a stick** — Confirmed + fixed: eight
   pans heaped with leaves in two greens, tomatoes, carrot sticks, cucumber
   slices, corn, eggs, beets, greens; tongs in the leaves.
9. **`DiningChair` back post kinked, an orange nub** — Confirmed: the back
   legs ran up to 3.0 inside the fan (z 0.64-0.82) and their copper caps (r
   0.11 at 3.02) poked out of its rim (the rim at x 0.98 there, the caps to
   1.01) and its back. The legs now end at 2.42, under the fan's lower edge,
   the fan resting on them; no caps.
10. **`GardenBench` rear plank another colour** — False: all three planks
   are one `drift` loop; the rear one lies under the back's top rail and
   its moss (z 0.62-0.92 at 3.0-3.16) and is in their shadow in the
   Workbench render.

Findings 11 and 12 are the Lodge's (its README).

**Validated**: the 7 rebuilt `VALIDATED 7/7`, no faults; every Sit piece
passes `sit_faults` (the stool's and the toilet's new seats included).
Triangles: `SaladBar` 1,464, `BreakfastBuffet` 1,398, `FloorLamp` 1,178,
`BoardGameShelf` 1,164, `Toilet` 726, `BarStool` 620, `DiningChair` 568
(budget 1,500). Height findings as before (`BarStool` 4.5 vs 2.6); the salad
bar 4.44 vs 4.2 is within 0.3, the lamp 5.26 vs 5.5 too.

Review: `review/every/` re-rendered for all 23 (Workbench). **Not done**: a
third blind review; restaging (`blender/_import/` holds the old ones);
anything in Studio.

Staged 2026-10-21 in `blender/_import/` as `BayouSpa_Furniture_<Id>.fbx`
(the 23; the names repeat the Manor's: rename to `Furniture_<Id>` on saving
into `assets/HotelKit/BayouSpa/`), beside what was there.

### Blind review 2026-10-21 (third run)

A third pair of context-free reviewers (another model) looked at the rebuilt pieces. Each finding triaged,
proved by the script's geometry where it could be; fixed in `tools/build_built_rooms_kits.py` (shared shapes
changed the Lodge's too), rebuilt alone (`-- sets bayou_spa only Toilet,SaladBar,BoardGameShelf,
BreakfastBuffet,BarStool,DiningChair,FloorLamp`):

1. **`Toilet` a cabinet beside a hatbox; from above a brown oval beside a box, no white** — Confirmed + fixed: one white ceramic toilet as the Manor's that passed (bowl on a foot running up into a white deck, a low white cistern 1.58-2.8 standing on it, only its lid cypress with a lotus); a light cypress seat ring at 1.72 round a dark water opening with the white rim showing round it from above; the lid raised on two brass hinges against the cistern (z 0.4-0.49, behind the torso at 0.15); a spare roll. `Use` and seat height unchanged; `sit_faults` clean.
2. **`SaladBar` pane floating between posts, trays both sides under a one-sided guard; carrots a smile, eggs a napkin** — Confirmed + fixed: the guest stands only at the front (Stand), so the pans are one row of five along it and the pane slopes from 4.45 over their back edge down to 3.8 over the front edge between two brass end posts and brackets that hold its ends, open behind and above; plates behind. Carrots are eight short sticks heaped, eggs are halves with yolks (on greens), with lettuce, cherry tomatoes (new palette `tomato`, `carrot` appended) and cucumber slices. The sheets now draw `Glass` see-through as the game does.
3. **`BreakfastBuffet` a blank cream slab from above, a striped sideboard with a teapot** — Confirmed + fixed: a hot station: three open copper warming pans heaped in strong colours (shrimp on grits, scrambled eggs with chives, sausages), a brass gantry behind them with two copper heat lamps on arms between the pans glowing (`Glow_Warm_1`, 0.75 over the food), a stack of plates, the copper pot; the skirt's pleats one linen (no stripes). The basket, fruit and cup went for the budget.
4. **`BoardGameShelf` games read as books** — Confirmed + fixed (shared with the Lodge): boxes stood up showing a four-colour board under a white title band, deep two-box stacks with a lid a hair wider, one game open with its board and pawns, dice; two games and two dice on the cornice, so from above it is more than a plank; the brackets under the sides.
5. **`BarStool`: forearms through the counter; a barber's or office chair** — Arms False by geometry: at the Snack Counter the stool's `Use` is (0, 2.6, -2.8) looking +Z, the arms z -3.25..-2.35, y 3.35-4.6; the counter's top edge is at z -1.05 and its jars at 0.3, 1.1 clear; the front and three-quarter cameras sit behind the sitter, so the figure overlaps the counter in the picture (the rig is not at fault). Chair look Confirmed + fixed: four cypress root legs joined by the copper foot ring (feet on it at 1.5), the oval seat, a low curved backrest (3.0-3.42) on two short posts; no slats, medallion or tulip base.
6. **`FloorLamp` opaque yellow panels, a loop held by nothing, the stalk into its bottom** — Confirmed + fixed: the whole jar was `Glow_Warm_1`. Now an open brass lantern (dish, six side straps, an open top ring, three straps to a knob), the glowing core 0.3 inside the cage seen between the straps and through the top; hung by its loop from the hook of a cypress shepherd's crook; no panels.
7. **`DiningChair` fan held at two points, tapering to a point over the seat** — Confirmed (hub 0.23 over the seat board, nothing under it) + fixed: the fan is a half disc standing on a light cypress rail (1.71-2.06) across the seat's back that takes the back legs' tops.
8. **Seated feet hang 0.6-0.7 over the floor** — Confirmed by geometry, not changed (as asked): soles 1.1 under the seat; `DiningChair` 1.82 leaves them at 0.72, `Toilet` 1.72 at 0.62, `GardenBench` 1.75 at 0.65; the stool's rest on its ring. **August's call** (kit-wide, MODELS.md rule 6), after a real avatar is seated in Studio.

Finding 9 is the Lodge's (its README).

**Validated**: the 7 rebuilt `VALIDATED 7/7`, no faults; every Sit piece passes `sit_faults`. Triangles: `BreakfastBuffet` 1,482, `BoardGameShelf` 1,476, `SaladBar` 1,440, `FloorLamp` 1,262, `Toilet` 962, `DiningChair` 612, `BarStool` 588 (budget 1,500). Height findings: `BreakfastBuffet` 4.42 vs 3.0 (the heat lamps), `Toilet` 3.27 vs 3.6, `BarStool` 3.42 vs 2.6 (was 4.5).

Review: `review/every/` re-rendered for all 23 (Workbench). **Not done**: a fourth blind review; restaging (`blender/_import/` holds older ones); anything in Studio.

### Blind review 2026-10-21 (fourth run)

A fourth pair of context-free reviewers (another model). Each finding triaged, proved by the script's geometry; fixed in `tools/build_built_rooms_kits.py` (shared shapes changed the Lodge's too), rebuilt alone (`-- sets bayou_spa only SaladBar,BreakfastBuffet,BoardGameShelf,Toilet,BarStool,FloorLamp,CoffeeUrn`):

1. **`SaladBar` pane low and held at its top only; the salad bar and buffet one silhouette** — Pane Confirmed + fixed (shared with the Lodge): the old pane's lower edge was 3.8 over z -0.88, 1.02 over the counter; now 4.6, 1.6 over the pans' fill (3.0), each end a closed brass triangle (post, bracket, strut to the lower corner) with a rail along the lower edge; the ice well 0.17 back from the edge (was 0.08), the pans 0.28; four pans, the plates at the row's start (the guest's end). Silhouette Confirmed (both 8.2 long on root feet at x ±3.7, a three-panel front, moss, brass on top) + fixed: the salad bar is now an open cypress trestle table (two crossed legs at each end, a stretcher, an open shelf at 1.38-1.5 with a basket of rolls and a stack of stone bowls, an apron under the top); the buffet keeps the skirted table.
2. **`BreakfastBuffet` heat lamps over the seams, none over the first pan, 0.5 over the trays** — Confirmed (two hoods at x -1.875 and -0.125 between pans at -2.75, -1.0, 0.75; glow at 3.74, 0.78 over the rims at 2.96) + fixed: one hood over each pan, centred, its glow at 4.56 (1.6 over the rims), the gantry bar at 5.25-5.37. The cloth's top now also runs past the rattan hem band (-1.09 against -1.082; the Lodge's finding 2).
3. **`BoardGameShelf` sides ending in dark stubs** — Confirmed + fixed (shared): each bracket a cypress knee against the wall, its tip 0.8 behind the case's front (was a cypress-dark wedge to 0.4 behind it); the case 0.2 lower, the cornice's top at 5.06, its two games and dice seen from above (model top 5.53).
4. **`Toilet` plinth wider at its top than at the floor; the lid wider than the cistern, too close to the back** — Confirmed (the block behind the bowl ran from z 0.45 at the floor to 0.97 at 0.9; the lid ±0.81 against the cistern's ±0.74, its front 0.25 behind the torso) + fixed (shared): the block straight-sided to z 1.02, the pedestal widest at the floor (0.74 to 0.68 at 0.55), the lid a flat plate ±0.7 with a cypress panel inside its rim, its front 0.32 behind the torso, the cistern moved back 0.06. The grey square tile: False, the review's footprint plate (`_squares`), not in the FBX.
5. **`FloorLamp` lantern off the base from above; the crook kinked** — Off the base False by geometry (the lantern's axis at x 0.45 was inside the stone's 0.7; its rim ran -0.04..0.94, half over it), but Confirmed as a read + fixed: the stone now 0.9 across, so the lantern hangs over it. Kinks Confirmed (nine straight segments, the thickness stepping from 0.1 to 0.07) + fixed: one smooth rod (`tube`: a gentle lean, then a round crook of radius 0.39 in nine steps), thinning evenly from 0.1 to 0.065; the cattails moved off the wider stone.
6. **`BarStool` seat plate a tab behind the cushion** — Confirmed (a 1.88 × 0.56 tongue at z 0.3-0.86 behind the cushion, which ends at 0.6) + fixed in the shared seat (the Lodge's stool had the same tab): no tongue; the posts rise raked from the seat board's back edge into the backrest. `sit_faults` clean.
9. **Taste, August's call (not changed)**: the leaf garlands hanging off counter edges reading as mould. Recommendation: keep moss as the Spa's sign but fewer and lighter: one short light-green tuft at one corner of a piece instead of dark scallops along whole edges.

Findings 7 and 8 are the Lodge's (its README); the shared `CoffeeUrn` top now overhangs its front here too (-1.08).

**Validated**: the 7 rebuilt `VALIDATED 7/7`, no faults; every Sit piece passes `sit_faults`. Triangles: `BreakfastBuffet` 1,482, `BoardGameShelf` 1,468, `SaladBar` 1,300, `CoffeeUrn` 1,126, `FloorLamp` 1,090, `Toilet` 1,018, `BarStool` 576 (budget 1,500). Height findings: `BreakfastBuffet` 5.37 vs 3.0 (the raised heat lamps), `SaladBar` 5.03 vs 4.2 (the raised guard), `BarStool` 3.42 vs 2.6, `Toilet` 3.27 vs 3.6.

Review: `review/every/` re-rendered for all 23 (Workbench). **Not done**: a fifth blind review; restaging (`blender/_import/` holds older ones); anything in Studio.
