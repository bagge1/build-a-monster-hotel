# Haunted Manor: the Gym's weight bench, treadmill and punching bag (GDD A.13)

The Gym type's three key pieces (GDD A.13.2, the Gym row; A.13.3, the
Fitness set) in Haunted Manor's dress, to `MODELS.md` "Furniture" and
"Activity furniture: visitors' spots". Built by `tools/build_activity_gym.py`,
which runs `tools/build_activity_bar.py`'s definitions (and through it
`tools/build_built_rooms.py`'s kit) without their mains; a draft for August's
look, 2026-10-26. **Nothing here has been seen in Studio, and nothing is
staged for import.** The models belong in `HotelKit.HauntedManor`; they have
their own set folder so no other set's manifest is rewritten.

## What is in it

| Model | What | Spot | Top | Triangles |
|---|---|---|---|---|
| `Furniture_WeightBench` (1 x 2, `Floor`) | A plum leather pad at **1.5** (1.7 wide under the body, 1.2 between the uprights) on an iron spine and two trestle feet; at the head end (+Z) two square iron uprights ending in gold spires, J-hooks on their fronts, a black barbell with round plates and gold collars racked at 3.58 over the lifter's face | `Use_1` `Lift`, placed as `Lie`: (0, 1.5, 0), looking -Z (feet to the front, head at the rack) | 4.5 | 492 |
| `Furniture_Treadmill` (1 x 2, `Floor`) | A black belt at **0.5** between iron skirts on gold ball feet, an iron motor hood at the back, iron hip rails at 2.12 to 2.25 with plum grips, two iron uprights to a dark-wood console with a shallow pointed-arch top and a gold-rimmed clock face lit moon-blue (`Glow_Cold_1`) toward the walker | `Use_1` `Stand` on the belt: (0, 0.5, -0.5), looking +Z (at the console) | 4.51 | 688 |
| `Furniture_PunchingBag` (1 x 1, `Floor`) | A gallows stand: an iron post at the back on a T foot (its long arm runs under the bag), an arm with a diagonal brace, a gold spire and a gold end knob; a plum leather bag 1.4 across, y 1.6 to 4.62, with two black bands, four straps up to a ring and an iron chain to the arm | `Use_1` `Stand` in front: (0, 0, -3), looking +Z | 6.47 | 742 |

Parts: `Root`, `Body` (not colliding), the treadmill's `Glow_Cold_1` (its
dial), and `LOD_Proxy` on all three (over 4 tall). `import_fixup.luau` gives
each `Use_<n>` its `Pose` attribute. The bar, the belt and the bag are in
`Body`: nothing moves. MODELS.md names no part for them, so they cannot be
split out until it does (rule 2 and CLAUDE.md: the name goes into the
contract first).

## The Pieces rows the code needs

| id | w x d | layer | height | keyFor | spots |
|---|---|---|---|---|---|
| `WeightBench` | 1 x 2 | Floor | **4.5** (main's row says 2.5) | Gym | `Use_1` Lift (placed as Lie) |
| `Treadmill` | 1 x 2 | Floor | 4.5 (as main) | Gym | `Use_1` Stand, on the belt |
| `PunchingBag` | 1 x 1 | Floor | 6.5 (as main) | Gym | `Use_1` Stand, in front |

Every w, d and layer matches main's rows, and so do the treadmill's and the
bag's heights. **The bench's height must change, 2.5 to 4.5:** the barbell is
racked at the lying person's reach. The pad is at 1.5, the bar at 3.58, its
plates clear of the 1.5 over the pad that the Lie check holds free, and the
uprights' spires reach 4.5. A bench without a rack (option C) would be 2.5,
but it reads as a plain bench. `validation.json` `height_findings` and
`pieces_rows` record it.

## Silhouettes (grey, three a piece)

`-- grey` builds them into `silhouettes/` (not in git, not for import):
`silhouettes/review/silhouettes_game.png` (the game's raised camera) and
`silhouettes_side_1.png` (benches), `_2.png` (treadmills), `_3.png` (bags).
Every grey option passed the same spot checks. They were drawn before the
blind reviews: the shared helpers (the bench's pad, the treadmill's deck,
the bag) have changed since, so a new `-- grey` run would differ in those
details.

- Bench **A** (chosen): a flat bench with the barbell racked on two uprights
  at its head end. It reads as a bench press, compact.
- Bench B: the uprights rise into a tall pointed arch at 5.6 (6.1 with its
  spire). It reads as a shrine or a gallows over the lifter's head.
- Bench C: no rack, two dumbbells on a shelf under the pad, 2.5 tall (the
  row's height). It reads as a plain bench.
- Treadmill **A** (chosen): the deck, hip rails, two uprights to the console
  with a clock face. It reads as a treadmill.
- Treadmill B: no rails, one gothic column carrying a lectern console. It
  reads as a lectern on a mat.
- Treadmill C: the uprights rise into a pointed arch at 6.7 over the console,
  2.2 over the row's 4.5. It reads as a gateway.
- Bag **A** (chosen): a gallows stand (post, arm and brace). The clearest bag
  stand, with a Manor touch.
- Bag B: a pointed-arch frame round the bag, the bag hung from its point.
  The bag is boxed in by the posts.
- Bag C: a round column on a plinth with a shepherd's-crook arm. It reads as
  a lamp post.

## Validated (validation.json)

On the built and the re-imported triangles: the kit's furniture rules
(footprint 3w x 3d, the 0.4 inset, at most 7 tall, `Body` not colliding, no
coplanar faces, glow colours only in glow parts, budget 1,500, the atlas,
w, d and layer as Pieces.luau says), nothing floats, and `spots_check` for
every `Use_<n>` (from 1 without a gap, a Pose from MODELS.md's list, level,
no two on a square). All three pass.

Two branches were added to the one spot validator in
`tools/build_activity_bar.py`. Both are purely additive: no other set's
spots reach them, and no other set was rebuilt.

- **`Lift`**: held to the checks of the placement the piece names
  (`piece.lift`; MODELS.md: "as Lie or Stand would place it"). A Lift that
  names neither is refused. The bench's is `Lie`: on the pad with nothing
  over it, and the lying 5-stud person (`lie_faults`) in the footprint, on
  the piece, with nothing rising through it, arms included. The rack's
  uprights stand 0.06 beside the head's 1.2 and 0.12 past the arms' end; the
  plates' bottom is 3.1, over the 3.0 the check holds free.
- **`Stand` inside the footprint** (the belt; `stand_on_faults`): the surface
  flat to 0.15 under both feet, and the standing person (`stand_blocks`, the
  review figure's blocks: legs, torso, arms 3.8 across, head) clear of the
  body. The rails stand 0.25 under the arms and 0.02 beside the legs; the
  console is 1.2 ahead of the head.

The bag's `Stand` keeps the existing check: on the floor 1.5 in front of the
front edge, facing +Z, its square free. The bag's front is 1.5 from the
boxer's chest.

**The treadmill's `Stand` on the belt is outside MODELS.md's words.** Its
`Stand` names only the square in front, and "it lies outside the footprint:
the code keeps that square free". The task asked for a Stand on the belt;
the contract needs a line saying a Stand may lie on the piece (as `Lift`'s
does), and the code must not reserve the square in front for this one
(below).

Not validated: anything in Studio (the attachments and Pose attributes exist
only in the manifest until `import_fixup.luau` runs), a visitor walking to a
spot, lying, walking the belt or punching (no walker or clip has run), and
the dial lit (the code does it).

## Blind review 2026-10-26

Three runs, a fresh reviewer each on new pictures after each fix:
`review/blind/`, `blind2/`, `blind3/` (not in git).

Run 1:
1. The bench disappears under its user and is too low: **confirmed, fixed** (the pad rises from 1.3 to 1.5, a seat's height, and widens to 1.7 under the body). The figure overhanging the frame: **false** (the pad runs 5.1, past the 5-stud body at both ends).
2. The barbell arched: **confirmed as a reading** (the pointed arch behind the bar's line). The arch was raised clear of it, then **removed after run 2**.
3. The uprights too close, the hands would grip outside the plates: **his call** (below: the bar's length against the 0.4 inset).
4. The bag's spot is off its footprint, the stand's foot toward the user: **false by the contract** (a Stand is the square in front, kept free by the code; the foot ends at z -0.95, 0.55 short of the spot's square).
5. The treadmill doesn't read from behind; the hood reads as an ottoman: **confirmed in part, fixed** (the hood iron and lower, part of the deck); the belt covered by its walker is inherent.
6. The bag reads as a lantern on a lamp post: **confirmed in part, fixed** (the bag 1.4 across, its bands black, not gold); reopened in runs 2 and 3.
7. The red wedge panels read as tail lights: **confirmed, fixed** (removed).
8. The deck is narrower than the user: **false by the contract** (one square wide; the 3.8-wide figure's arms overhang, as at the Bar). The purple fragment at the leg: **confirmed** (the grip 0.01 into the review figure's leg), **fixed** (rails 0.02 clear of the legs).
9. The gold feet lift the deck off the floor: **confirmed, fixed** (the skirts reach 0.02).

Run 2:
1. The lifter lies inside the pad: **false** (the figure's bottom is the pad's top at 1.5; the Lie check holds it to 0.15).
2. The bench reads as a coffin or a bed (full length, legs on it; gold studs): **studs confirmed, fixed** (removed); the full-length lie is **his call** (below).
3. The bar curved, the plates read as gears: **confirmed** (the second time), **fixed** (the arch removed, the uprights end in gold spires; the plates 16-sided).
4. The console at face height, flush with the head: **false** (its bottom at 3.58, the walker's chest; 1.2 ahead of the head). The rig reads as a gateway: his call (look).
5. The boxer touches the bag: **false** (1.5 between the chest and the bag's front; the render's angle).
6. The bag reads as a canister on a gallows: **confirmed, fixed** (four straps from the bag's shoulder to a ring, the chain above them); reopened in run 3.
7. Near-black from the game camera: **his call** (the Manor's iron; below).
8. An upright through the user's arm: **false** (0.12 past the arms' end, 0.06 beside the head; the Lie check passes).
9. A stray purple sliver on the treadmill: **confirmed as a reading, fixed** (the grips 1.3 long, read as grips).
10. The bag's spot is off its patch: **false by the contract** (run 1, 4).

Run 3 (the last round):
1. The barbell is narrower than the grip: **his call** (the third time; below).
2. The belt torso-wide, the rails under the arms: the overhang is **false by the contract** (run 1, 8); the rails are 0.25 under the static arms, so an arm swing reaching them is the walk clip's (below).
3. The pad full length reads as a bed or coffin: **his call** (run 2, 2).
4. The bar passes through the uprights: **false** (the bar at z 1.45 runs in front of the uprights' faces at 1.62, resting on hooks).
5. The bag reads as a barrel on a gallows: **his call** (the third reading as something else; the gallows is the Manor touch).
6. The bag's spot is off the tile and beside the bag: **false** (the contract; the spot is at x 0 facing +Z, the bag at x 0).
7. The treadmill reads as a plinth with a mantel clock, no dial, no belt texture: the dial is there, so that part is **false**; the clock as the console is the Manor touch; a belt texture is **his call** (stripes on a walked surface; taste.md allows a deliberate pattern there).
8. Loose gold cubes at the treadmill's corners: **confirmed, fixed after run 3** (the feet round, 10-sided, tucked under the skirts; they touched before, nothing floats passed; not re-reviewed).
9. The posts nearly touch the head: holds for the static figure (0.06 clear); a lift clip that raises the head is the code's (below).

## His calls (for WAITING.md; this session did not edit it)

- **The bar's length.** The 0.4 inset caps the barbell at 2.2 across. The
  5-stud figure's hands hang at about +-1.46, so three reviewers saw them
  outside the plates. I recommend letting the bar alone reach about +-1.45,
  past the inset but inside its square: an exception in MODELS.md, and two
  benches side by side then nearly meet. The alternative is the clip
  gripping inside the plates, which looks narrow.
- **The lifter's pose.** MODELS.md's Lie puts the whole 5-stud person on the
  piece, so the pad runs full length and the legs lie on it. Two reviewers
  read it as a bed or a coffin. I recommend a `Lift` placement with the feet
  on the floor: a pad about 3.5 long, the hips at its foot end, the shins
  down either side. That needs a line in MODELS.md and its own check.
- **Stand on the belt.** MODELS.md's `Stand` is the square in front. The
  treadmill's is on the belt, so the contract needs that line, and the code
  must not keep the square in front free for this piece. I recommend the
  line.
- **Moving parts.** The bar, the belt and the bag are `Body`. If the code is
  to lift the bar, scroll the belt or swing the bag, MODELS.md first needs
  names for them (e.g. `Barbell`, `Belt`, `Bag`); then the script splits them
  out.
- **Looks**: the gallows stand (read as a lamp post, a canister, a barrel on
  a gibbet; recommend keeping it, with the straps), the clock console
  (recommend keeping), the dark iron from the game camera (recommend keeping
  the Manor's iron; the plum pad and bag carry the colour), and a striped
  belt (recommend none).
- **The bench's height**: Pieces.luau's `WeightBench` row 2.5 to 4.5.
