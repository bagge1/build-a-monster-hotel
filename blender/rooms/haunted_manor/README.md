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
| `Wall_Door` | The same with an open pointed-arch doorway, clear x -2..2, y 0..7.2; dark wood trim, gold keystone, capped plinth blocks in the trim's wood; `Door`, `Sign` | 804 |
| `Wall_Post` | The 0.6 joint post, 17.02 tall: plum, dark foot, gold cap | 48 |
| 14 furniture, location 1 | `Bed`, `DoubleBed`, `PlanterBed`, `FourPosterBed`, `Sarcophagus`, `WitchBed`, `DenNest`, `Coffin`, `OperaChaise`, `SnackCounter`, `Jukebox`, `Gravestone`, `ReadingDesk`, `PipeOrgan` | 140-1,080 |
| 10 furniture, location 0 (in the Manor's style) | `Nightstand`, `Wardrobe`, `WritingDesk`, `DiningTable`, `BreakfastBuffet`, `BarStool`, `PoolTable`, `CardTable`, `Bathtub`, `FloorLamp` | 282-916 |

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
  5-stud person needs 3 x 1 (`Pieces`, his call). Its `Use` is waived by
  name in the build (a tub is lain in reclining). The reviewer's look
  remarks (the striped counters, the wardrobe's gold top, the organ's
  pipes, the nest's size, the coffin's closed lid, the doorway's width) are
  August's.

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
- **Lying** (new, `lie_faults`): the 5-stud person 5 long centred on each
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
`BarStool` 2.6 vs 3.2 (its back, over the seat at 2.6).
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

`review/walls_sheet.png` (the room from the street and from behind, a corner
and a T close up, the door from outside and from inside as a cutaway, the
door piece alone and its plinth close up), `review/furniture_sheet.png`
(every piece on its 3-stud squares beside the 5-stud person, `Use` as a red
mark with its facing), `review/elevations_sheet.png` (every piece level at
floor height, from the front and from the side, on its squares),
`review/lying_sheet.png` (every `Lie` piece from above and from the side
with the 5-stud person lying on its `Use`; the four-poster also from the
raised camera). Workbench on light grey (Studio was running: no EEVEE or
Cycles).

## Staged

All 27 FBX in `blender/_import/` (unprefixed; the Lodge's walls there are
`FrostfangLodge_Wall_*`). Re-staged after the fixes: `Wall_Door`,
`Furniture_FourPosterBed`, `Furniture_Coffin`, `Furniture_BarStool`,
`Furniture_PipeOrgan`. The moved `Use` points live in `import_fixup.luau`.
