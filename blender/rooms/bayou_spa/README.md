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

Staged 2026-10-21 in `blender/_import/` as `BayouSpa_Furniture_<Id>.fbx`
(the 23; the names repeat the Manor's: rename to `Furniture_<Id>` on saving
into `assets/HotelKit/BayouSpa/`), beside what was there.
