# Haunted Manor: inner walls, a door and furniture (built rooms)

His ruling, 2026-10-21 (GDD §5.4, A.12): rooms are built by the player from
inner walls and a door, and furnished. This set is the Manor's art for that,
to the contract in `MODELS.md`, "Inner walls, doors and furniture (built
rooms)". Built by `tools/build_built_rooms.py -- sets haunted_manor`; a night
draft (2026-10-21) for his review. **Nothing here has been seen in Studio.**

## What is in it (27 models)

| Model | What | Triangles |
|---|---|---|
| `Wall_Half` | 6-stud half edge, 0.4 thick centred on the edge, 17 tall; plum wainscot, lilac paper (the Standard Room's), gold chair rail, picture rail and crown, dark skirting, on both faces | 132 |
| `Wall_Door` | The same with an open pointed-arch doorway, clear x -2..2, y 0..7.2; dark wood trim, gold keystone, plinths; `Door`, `Sign` | 628 |
| `Wall_Post` | The 0.6 joint post, 17.02 tall: plum, dark foot, gold cap | 48 |
| 14 furniture, location 1 | `Bed`, `DoubleBed`, `PlanterBed`, `FourPosterBed`, `Sarcophagus`, `WitchBed`, `DenNest`, `Coffin`, `OperaChaise`, `SnackCounter`, `Jukebox`, `Gravestone`, `ReadingDesk`, `PipeOrgan` | 140-860 |
| 10 furniture, location 0 (in the Manor's style) | `Nightstand`, `Wardrobe`, `WritingDesk`, `DiningTable`, `BreakfastBuffet`, `BarStool`, `PoolTable`, `CardTable`, `Bathtub`, `FloorLamp` | 282-916 |

Every furniture piece is `Furniture_<Id>` on its `Pieces.luau` row's w x d
squares and layer, with `Use` and its `Pose` (Lie: the beds, coffin,
sarcophagus, nest, chaise, bathtub; Sit: the bar stool, on a declared seat;
Stand: the rest, 1.5 in front of the front edge). Reused from the approved
room models (shapes re-authored in the furniture frame, faces that shared a
plane moved 0.02-0.05 apart): the Standard Room's bed (and widened for the
double and the four-poster), the Sarcophagus Suite's sarcophagus, the Potion
Loft's bed, the Den Room's nest (a third larger for its 3 x 3), the Coffin
Suite's coffin (its lid left off; its gold bat now on the foot), the Snack
Bar's counter, a Graveyard Garden tombstone, and `Decor_PipeOrgan`'s geometry
as `Furniture_PipeOrgan`. New: the four-poster's canopy, planter bed,
chaise, jukebox, reading desk and the ten location-0 pieces.

## Validated (validation.json, by the build)

- Each FBX re-imported: part names, boxes to 0.02, triangle counts, one
  material, the atlas embedded.
- Walls: the colliding boxes exactly (`Wall`; `Wall_Left`, `Wall_Right`,
  `Wall_Lintel`; `Post`), the doorway clear, `Door` (0,0,0) and `Sign`
  (0,9.6,-0.5) looking -Z, nothing outside the frame (dressing within |z|
  0.28), each piece the same turned 180 degrees, no coplanar faces.
- **Assembly**: the FBXs laid round a 2 x 2 cell room (L corners, two T
  joints, two free ends, two doors, straight runs): 0 visible coplanar
  overlaps between pieces, 328 inside posts (where the contract puts them).
- Furniture: the kit's decor checks (footprint and 0.4 inset, layer, w/d
  from Pieces, nothing colliding, no coplanar faces, the stool's seat by
  rule 6) and `Use`: Lie/Sit points on their surface (0.15) with nothing
  over them for 1.5, Stand points where the contract says.
- Budgets: walls 1,200, the post 200, furniture 1,500; all well under.
  `LOD_Proxy` (a box) on pieces wider than 2 squares or over 4 tall.

**Height findings** (Pieces' `height` is the blockouts' placeholder; src/ was
not touched): `Bed` 2.0 vs 5.0, `DoubleBed` 2.0 vs 5.0, `WitchBed` 2.2 vs
5.0 (the approved gothic headboard), `SnackCounter` 3.4 vs 4.52 (its jars).
The code session updates those rows or August rules the headboard lower.

## Not validated

- Anything in Studio: the import, `import_fixup.luau` (it adds `Use`'s
  `Pose` attribute), how it looks lit.
- The code placing walls, doors and posts (not written yet); walls meeting
  the facade (the post closes that joint by the contract; not assembled
  here, and a wall ending at a facade window's middle would run into it).
- A guest walking to `Use`, lying or sitting: no walker has run.
- Blind review: not run yet; the sheets are for it.

## Review

`review/walls_sheet.png` (the room from the street and from behind, a corner
and a T close up, the door from outside and from inside as a cutaway),
`review/furniture_sheet.png` (every piece on its 3-stud squares beside the
5-stud person, `Use` as a red mark with its facing). Workbench on light grey.

## Staged

All 27 FBX in `blender/_import/` (unprefixed; the Lodge's walls there are
`FrostfangLodge_Wall_*`).
