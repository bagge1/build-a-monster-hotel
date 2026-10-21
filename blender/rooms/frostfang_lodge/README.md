# Frostfang Lodge: inner walls, a door and furniture (built rooms)

His ruling, 2026-10-21 (GDD §5.4, A.12): rooms are built by the player from
inner walls and a door, and furnished. This set is the Lodge's art for that,
to the contract in `MODELS.md`, "Inner walls, doors and furniture (built
rooms)". Built by `tools/build_built_rooms.py -- sets frostfang_lodge`; a
night draft (2026-10-21) for his review. **Nothing here has been seen in
Studio.**

## What is in it (11 models)

| Model | What | Triangles |
|---|---|---|
| `Wall_Half` | 6-stud half edge, 0.4 thick, 17 tall: 13 log courses over a dark wainscot (the lodge rooms'), light wood rails, a snow cornice, both faces; its top face snow | 276 |
| `Wall_Door` | The same with an open round-arched doorway, clear x -2..2, y 0..7.2; dark log trim, a snow keystone, capped plinth blocks in the trim's wood; `Door`, `Sign` | 1,172 |
| `Wall_Post` | The 0.6 joint post, banded as the walls meeting it: dark skirting and wainscot, light rails, the log courses, the snow cornice | 160 |
| 8 furniture, location 2 | `IceBed` (Igloo Room's bed), `IceSlab` (Ice Cave's slab under furs), `SnowNest` (Yeti Den's nest, a third larger), `GlacierCoil` (Glacier Suite's coiled bed, a third larger), `CocoaBar` (Cocoa Lounge's counter), new: `KnittingChair` (a rocking chair, a seat by rule 6, a yarn basket), `StarHammock` (navy with stars between snow-capped log posts), `SkyLounger` (a deck lounger) | 268-1,024 |

`Use` Poses: Lie for the beds, nest, coil, hammock and lounger; Sit for the
knitting chair; Stand for the cocoa bar. The location-0 furniture is only in
Haunted Manor's style so far (`blender/rooms/haunted_manor/`); the contract
lets the code take the Manor's until the Lodge has its own.

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
  bar stool's seated guest has the thighs at 3.5).
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

Bayou Spa (location 3) is not modelled: its style is still a draft.
