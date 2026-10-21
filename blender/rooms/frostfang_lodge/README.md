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
| `Wall_Half` | 6-stud half edge, 0.4 thick, 17 tall: 13 log courses over a dark wainscot (the lodge rooms'), light wood rails, a snow cornice, both faces | 276 |
| `Wall_Door` | The same with an open round-arched doorway, clear x -2..2, y 0..7.2; dark log trim, a snow keystone; `Door`, `Sign` | 996 |
| `Wall_Post` | The 0.6 joint post: log, dark foot, snow cap | 48 |
| 8 furniture, location 2 | `IceBed` (Igloo Room's bed), `IceSlab` (Ice Cave's slab under furs), `SnowNest` (Yeti Den's nest, a third larger), `GlacierCoil` (Glacier Suite's coiled bed, a third larger), `CocoaBar` (Cocoa Lounge's counter), new: `KnittingChair` (a rocking chair, a seat by rule 6, a yarn basket), `StarHammock` (navy with stars between snow-capped log posts), `SkyLounger` (a deck lounger) | 268-1,024 |

`Use` Poses: Lie for the beds, nest, coil, hammock and lounger; Sit for the
knitting chair; Stand for the cocoa bar. The location-0 furniture is only in
Haunted Manor's style so far (`blender/rooms/haunted_manor/`); the contract
lets the code take the Manor's until the Lodge has its own.

## Validated (validation.json, by the build)

As the Manor's set (its README): re-imported FBX checks, the walls' exact
boxes, opening, attachments, 180-degree sameness and no coplanar faces; the
assembled room (0 visible overlaps, 664 inside posts); furniture's decor
checks and `Use`. Budgets all under (the door 996 of 1,200 after its rails
lost their chamfer; the Manor's rails the same).

**Height findings** (Pieces' placeholder vs the model's top): `IceBed` 2.0 vs
3.6 (the igloo-dome headboard), `IceSlab` 1.8 vs 3.87 (the rock headboard),
`GlacierCoil` 2.4 vs 4.4 (the crystal pillars), `CocoaBar` 3.4 vs 4.8 (the
cocoa pot).

## Not validated

Studio (import, fix-up, light), the code placing walls, a walker to `Use`,
the facade joint, a blind review (the sheets are for it).

## Review

`review/walls_sheet.png`, `review/furniture_sheet.png` (Workbench, light grey).

## Staged

In `blender/_import/`: the walls as `FrostfangLodge_Wall_Half.fbx`,
`FrostfangLodge_Wall_Door.fbx`, `FrostfangLodge_Wall_Post.fbx` (the names
repeat the Manor's; rename to `Wall_*` on saving into
`assets/HotelKit/FrostfangLodge/`), the furniture unprefixed.

Bayou Spa (location 3) is not modelled: its style is still a draft.
