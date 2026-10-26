# Haunted Manor: Poolside and Fitness extras (GDD A.13)

Six smaller pieces for the Indoor and Outdoor Pool and the Gym (GDD A.13.2;
A.13.3's Poolside and Fitness sets) in Haunted Manor's look. They match the
Pool and Gym sets built the same night (`haunted_manor_pool/`,
`haunted_manor_gym/`). The contract is `MODELS.md` "Furniture" and "Activity
furniture: visitors' spots", with the Rug and Wall layer rules from "Decor".

They are built by `tools/build_activity_extras.py`, which runs
`tools/build_activity_billiards.py`'s definitions (and through it the
karaoke, bar and built-rooms kit) without their mains. This is a draft for
August's look, 2026-10-26. **Nothing here has been seen in Studio, and
nothing is staged for import.** The models belong in
`HotelKit.HauntedManor`.

The set has its own folder, not the Pool and Gym scripts. Rebuilding those
two sets would rewrite their manifests, validation and review sheets. This
way there is one silhouette sheet and one review for all six.

## What is in it

| Model | Option | What | Spot | Top | Triangles |
|---|---|---|---|---|---|
| `Furniture_Parasol` (**2 x 2**, `Floor`) | B | A bat-wing canopy 5.16 across: eight crimson and black panels whose edges draw up between the ribs. The rim is at 5.95 and the apex has a gold finial. Gold beads hang under the rib tips, and iron struts run from a gold runner. It stands on an iron pole in a stone base | none | 6.95 | 668 |
| `Furniture_PoolLadder` (1 x 1, `Floor`) | B | Two stone steps (0.43, then 0.86, the Pool's coping height). Its back (+Z) goes against the pool. Iron newel posts with gold finials stand at the front, and the handrails run back over the top step and turn down at its back edge | none | 2.98 | 556 |
| `Furniture_DivingBoard` (1 x 2, `Floor`) | A | A springboard with its tip at the front (-Z, toward the pool). The wood board has a plum top at 2.0 and rests on a stone platform and an iron pointed-arch fulcrum. Two stone steps at the back, and iron handrails beside them | none | 3.24 | 616 |
| `Furniture_DumbbellRack` (2 x 1, `Floor`) | A | A two-tier iron rack: end frames with gold finials, and five black hex dumbbells with gold handles on each tier, the larger ones on the low front tier | `Use_1` `Lift`, placed as `Stand`: (-1.5, 0, -3), looking +Z | 3.0 | 1,032 |
| `Furniture_ExerciseMat` (1 x 2, `Rug`) | A | A plum mat inside a crimson border band that reaches the footprint's edge, with a gold crescent at the foot end | `Use_1` `Lift`, placed as `Lie`: (0, 0.09, 0), looking -Z (feet to the front) | 0.105 | 172 |
| `Furniture_WallMirror` (2 x 1, `Wall`) | A | A tall pointed-arch mirror on a plinth against the wall: a dark-wood frame, a gold lip, a pale moon-blue pane and a gold finial on its point | none | 6.5 | 322 |

Parts: `Root`, `Body` (not colliding), and `LOD_Proxy` on the parasol and
the mirror (over 4 tall). `import_fixup.luau` gives each `Use_<n>` its
`Pose` attribute.

The spots are the blockout's (`src/server/ActivityKit.luau`): the rack's
`front(-1.5)` and the mat's `(0, h, 0)`, both `Lift`. The other four have
`spots = none`. `MODELS.md` lets a `Lift` be placed as `Lie` or `Stand`;
the mat's is `Lie` (an assumption: a mat is lain on). If August wants it
standing, it is a one-word change.

## The Pieces rows

| id | w x d | layer | height | Against main |
|---|---|---|---|---|
| `Parasol` | **2 x 2** | Floor | 7.0 | **w x d must change** (main: 1 x 1) |
| `PoolLadder` | 1 x 1 | Floor | 3.0 | as main |
| `DivingBoard` | 1 x 2 | Floor | 3.0 | as main (the top 3.24 is inside the 0.3 tolerance; 3.25 would be exact) |
| `DumbbellRack` | 2 x 1 | Floor | 3.0 | as main |
| `ExerciseMat` | 1 x 2 | Rug | 0.1 | as main |
| `WallMirror` | 2 x 1 | Wall | 6.5 | as main |

**Why the parasol is 2 x 2.** On 1 x 1, the 0.4 inset caps the canopy at
2.16 across, narrower than the 5-stud person's arms (3.8). It shades nobody
and reads as a cocktail umbrella (silhouette A). The kit's Pieces check ran
against 2 x 2 (`ROW_CHANGES` in the script; `validation.json`
`row_changes`, `pieces_rows`). The row must change before import, or the
model must go back to option A.

## Silhouettes (grey, two a piece)

`-- grey` builds them into `silhouettes/` (not in git, not for import):
`silhouettes/review/silhouettes_game.png` (the game's raised camera, the
pool row in front of a pool stand-in, the gym row against a wall) and
`silhouettes_front_1.png` and `_2.png` (level). Every option passed the kit's
checks.

- Parasol A (1 x 1): too small, as above. **B** (2 x 2) was chosen: it reads
  as a parasol and covers a person.
- Pool ladder A: a pointed-arch iron step ladder with treads up and down. It
  reads as a playground step ladder. **B** was chosen: steps meet the 0.86
  coping of a pool that stands on the floor, which is how a guest gets in.
- Diving board **A** was chosen: a springboard on a platform with handrails,
  the clearest read. B is a plank on an arched pier with a hooped ladder,
  and reads as a gangplank.
- Dumbbell rack **A** was chosen: an open two-tier iron rack, which reads as
  a gym. B is a wood cabinet with an arched backboard, which reads as a
  sideboard.
- Exercise mat **A** was chosen: a border band and a crescent. B, three
  folding panels, puts coplanar side faces on the panels, and its seams read
  as a grid.
- Wall mirror: B (a triptych) was chosen first. The blind review read it as
  a church window, so it went back to **A**, one tall mirror (below).

## Validated (validation.json)

The kit's furniture rules were checked on the built and the re-imported
triangles, and all six pass:

- footprint 3w x 3d, with w, d and layer as the rows above
- the 0.4 inset; a Rug's body reaches the footprint's edge instead and is at
  most 0.15 tall
- at most 7 tall
- `Body` not colliding
- no coplanar faces (rail segments are turned half a facet by turns, or two
  segments in one plane share a side facet's plane)
- budget 1,500 and the atlas

Nothing floats: `hung_check`, where the wall's plane counts as the floor for
the mirror. The mirror's back is on z = 1.1. `spots_check` ran on the rack's
`Stand` (on the floor at the left front square's middle, its square free)
and on the mat's `Lie` (on its surface, the lying 5-stud person in the
footprint, on the piece, nothing through it).

Not validated:

- anything in Studio
- a visitor walking to a spot or lifting (no walker or clip has run)
- the steps and the springboard beside the real Pool model (the review used
  a stand-in of its rim and water, because the Pool's FBX is not on this
  machine)
- a Wall piece turned to each wall by the build mode

## Blind review 2026-10-26 (one round)

The pictures are in `review/blind/` (not in git). The reviewer was a fresh
agent. The fixes below were made after the round and **have not been
re-reviewed**.

1. The mirror reads as a church window (three lancets, matte blue panes):
   **confirmed**, and **fixed in part**: back to option A, one tall mirror.
   The matte pane is **his call** (below). Diagonal sheen strips were tried
   before the review and removed: from the game camera they read as
   scratches (taste.md).
2. The springboard sits at knee height and reads as a bench: **confirmed**,
   **fixed**. The board's top went from 1.3 to 2.0, with a taller platform,
   two steps and the handrails to 3.24.
   The tip stopping short of the water is **false by the contract**: the 0.4
   insets leave 0.8 between the board and the pool's rim. Letting it reach
   is **his call** (below).
3. The mat is narrower than the lying guest's arms: **confirmed** (3 wide
   against 3.8). `MODELS.md`'s Lie lets the arms lie past the edge, so
   widening it is **his call** (a row change).
4. The mat reads as a rug: **his call**. It is a Rug-layer piece, at most
   0.15 tall, so no rolled end is possible.
5. The pool steps' rails are narrower than the avatar's arms: **confirmed**
   (1.76 apart). A 1 x 1 footprint cannot hold 3.8, and no guest uses the
   steps (no spot). Making them 2 x 1 is **his call**.
6. The parasol's rim is at head height: **confirmed** (5.5, with beads to
   5.4), **fixed**. The rim is now at 5.95; the top cannot pass 7.
7. Hair-thin rods, too-small dumbbells: **confirmed**, **fixed**.
   - parasol: pole 0.08 to 0.12, struts 0.03 to 0.045
   - rails: 0.06/0.07 to 0.09
   - rack: members thicker, and dumbbell heads +0.04 in radius
8. The steps have no Manor in them and are the same grey as the stand-in:
   **his call**. The stone matches the Pool's own coping, and the stand-in
   was coloured like it.
9. The hooked rail's gold end reads as a lantern: **confirmed as a
   reading**, **fixed**: the end ball is iron.
10. The level picture is seen from behind: **false**. It is from the front
    (-Z); seen that way, Roblox's +X is on the left, so the row runs right
    to left.

## His calls (for WAITING.md; this session did not edit it)

- **The parasol on 2 x 2** (Pieces row 1 x 1 to 2 x 2). I recommend it.
- **The mirror's surface.** A matte pale pane reads as glass or a window.
  I recommend a `Mirror` part in `MODELS.md` (like `Glass`), so the code can
  give it Reflectance, and the script splitting the pane out. The
  alternative is a silvery-white pane in `Body`.
- **The springboard's tip over the water.** The inset keeps it 0.8 short of
  the rim. I recommend an exception letting the tip reach the footprint's
  edge (as for the weight bench's bar).
- **The mat's size** (1 x 2 to 2 x 2, the arms on it). I recommend keeping
  1 x 2: a mat that size is real, and the arms past the edge are as at the
  bench.
- **The steps' width** (1 x 1 to 2 x 1). I recommend 1 x 1: nobody climbs
  them yet.
- **Looks**: the mat as a mat (recommend as is), the steps' plain stone
  (recommend as is, the Pool's coping stone), and the mat's `Lift` as Lie
  rather than Stand (recommend Lie).
