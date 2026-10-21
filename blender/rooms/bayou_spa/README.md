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
| `Wall_Door` | The same with an open round-arched doorway, clear x -2..2, y 0..7.2; dark cypress trim, a lily-green keystone, capped plinth blocks; `Door`, `Sign` | — | 17 | 956 |
| `Wall_Post` | The 0.6 joint post, banded as the walls meeting it | — | 17.02 | 72 |
| `Furniture_LilyPadBed` (3 x 3) | A giant lily pad, its rim turned up, on a moss mound; veins, a pale petal blanket, a lotus-bud pillow, two lotus flowers | Lie (0, 0.82, 0) | 1.28 | 1,030 |
| `Furniture_WillowHammock` (3 x 2) | Woven rattan (two-tone chords) slung between two gnarled cypress posts crowned with weeping willow, a firefly jar on each (`Glow_Warm_1`, `_2`); the Star Hammock's sling profile | Lie (0, 1.375, 0) | 3.9 | 828 |
| `Furniture_MudTub` (2 x 3) | An oval tub of cypress staves (alternate faces a lighter wood, no raised seams), two copper hoops, mud to the brim with bubbles, a rolled towel under the head, towels folded on the rim | Lie (0, 0.6, 0), on the floor under the mud | 2.26 | 856 |
| `Furniture_HerbBed` (2 x 3) | Weathered bed, moss mattress, lavender quilt with sage bands, a headboard of rattan reed bundles bound in copper with three herb bundles hung drying, a planter of herbs as its footboard | Lie (0, 1.8, 0.3) | 4.4 | 1,262 |
| `Furniture_SteamPool` (3 x 3) | A round hot pool in a ring of boulders (some mossy), steam curling off the two back stones, a lantern on the back stone (`Glow_Warm_1`), a smooth stone headrest, lily pads and a lotus on the water | Lie (0, 0.3, 0), on the floor under the water | 2.56 | 1,496 |
| `Furniture_CypressThrone` (2 x 2) | A throne carved from a cypress stump: root flare, moss cushion, root-knee arms, a high carved back with a lighter inset, Spanish moss over its shoulders, a firefly jar on a crooked branch (`Glow_Warm_1`) | Sit (0, 1.8, -0.8), a declared seat 2.1 x 1.3 | 5.0 | 630 |
| `Furniture_LagoonPerch` (3 x 3) | A smooth moonstone boulder with a lily-pad cushion, facing a little lagoon in front (lily pads, a lotus, a frog); a glowing crescent moon on a cord from a reed stalk (`Glow_Cold_1`); cattails | Sit (0, 1.73, 2.2), a declared seat 2.1 x 1.2 | 4.07 | 1,418 |
| `Furniture_JazzStage` (3 x 2) | A low porch stage of two-tone weathered boards on a velvet skirt, three footlights (`Glow_Warm_1`-`_3`), a vintage microphone, an upright bass, a stool with a straw boater, a string of warm bulbs between two posts (`Glow_Warm_4`) | Stand | 5.12 | 1,220 |
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
  1.2 deep, nothing over them for 3), **nothing floating**, no coplanar
  faces, budgets (all under 1,500; walls under 1,200 and 200).
- Fixed during the build: the pool's and perch's boulders dipped 0.08-0.1
  under the floor (lifted); three pieces were over 1,500 triangles (facets
  trimmed, one lily pad less).

**Height findings** (Pieces' placeholder vs the model's top, not faults;
src/ untouched): `LilyPadBed` 0.8 vs 1.28, `WillowHammock` 3.0 vs 3.9,
`HerbBed` 2.0 vs 4.4 (the headboard), `SteamPool` 1.2 vs 2.56 (the steam),
`JazzStage` 1.2 vs 5.12 (the microphone, bass and light posts), `LilyBasin`
1.0 vs 2.89 (the cattails).

## Not validated

Studio (import, fix-up, light), the code placing walls, a walker to `Use`,
the facade joint. **No blind review yet**: the sheets were looked at by the
building session only.

## Review

`review/walls_sheet.png`, `review/furniture_sheet.png`,
`review/elevations_sheet.png`, `review/lying_sheet.png` (top-down and side
with the 5-stud person lying), `review/sitting_sheet.png` (the throne and
the perch with the person seated); Workbench on light grey (Studio was
running: no EEVEE or Cycles). Not in git; rebuilt by the script.

## Staged

In `blender/_import/`: the walls as `BayouSpa_Wall_Half.fbx`,
`BayouSpa_Wall_Door.fbx`, `BayouSpa_Wall_Post.fbx` (the names repeat the
other kits'; rename to `Wall_*` on saving into `assets/HotelKit/BayouSpa/`),
the nine furniture pieces unprefixed (`Furniture_LilyPadBed.fbx` …).
