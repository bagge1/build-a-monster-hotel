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

## What is in it (12 models)

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
