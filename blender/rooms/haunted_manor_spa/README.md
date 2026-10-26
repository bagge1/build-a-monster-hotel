# Haunted Manor: the Spa's hot tub and massage table (GDD A.13)

The Spa type's two key pieces (GDD A.13.2, the Spa row; A.13.3: the Poolside
set serves the Spa too) in Haunted Manor's dress, built to `MODELS.md`
"Furniture" and "Activity furniture: visitors' spots". They are built by
`tools/build_activity_spa.py`, which runs `tools/build_activity_bar.py`'s
definitions (and through it `tools/build_built_rooms.py`'s kit) without their
mains. This is a draft for August's look, 2026-10-26. **Nothing here has been
seen in Studio, and nothing is staged for import.** The models belong in
`HotelKit.HauntedManor`; they have their own set folder so that no other set's
manifest is rewritten.

## What is in it

| Model | What | Spots | Top | Triangles |
|---|---|---|---|---|
| `Furniture_HotTub` (**3 x 3**, `Floor`) | A round tub standing on the floor: 16 staves in violet and plum under two gold hoops, a pale stone (bone) coping at **2.45**, teal water at **2.3** over a stone bench at **1.2** that runs round an octagonal footwell. Each corner has two pale treads (0.6 and 1.2). On the back corners' upper treads stand a gold brazier on an iron stand, holding dark steam stones over glowing embers (`Glow_Warm_2`), and a gold three-branch candelabra (`Glow_Warm_1`). | `Use_1..Use_4` `Sit` on the bench: (0, 1.2, 2.55) looking -Z, (2.55, 1.2, 0) looking -X, (0, 1.2, -2.55) looking +Z, (-2.55, 1.2, 0) looking +X. All four face the middle, one per square. | 3.71 | 1,436 |
| `Furniture_MassageTable` (1 x 2, `Floor`) | A plum leather pad at **2.3** under a cream sheet, on four turned dark-wood legs and an apron with a gold band. A plum horseshoe face cradle sits at the head end (+Z), 0.1 under the pad's top, on a dark-wood stem. A shelf below holds two rolled cream towels and two oil bottles (amber, wine). | `Use_1` `Lie`: (0, 2.33, 0) looking -Z (the feet toward the front, the head on the cradle; the guest lies face down, which is the clip's) | 2.33 | 768 |

Parts: `Root` and `Body` (not colliding) on both. The tub also has
**`Water`** (one part, not colliding, CanQuery false: the code makes it
water), `Glow_Warm_1` (the candelabra's three flames) and `Glow_Warm_2` (the
embers), plus a `LOD_Proxy`, since it is wider than 2 squares.
`import_fixup.luau` gives each `Use_<n>` its `Pose` attribute.

**Why 3 x 3.** The seated 5-stud person is 3.8 across with the arms, and its
shins hang 1.1 under the seat with the feet 0.5 ahead of it. Inside a 2 x 2
tub (Pieces' size: walls at +-2.2), one sitter's arms reach within 0.3 of the
walls. A second sitter does not fit:
- side by side, the arms meet;
- face to face, the feet overlap;
- on an adjacent wall, the arms cross.

So 2 x 2 holds **one** visitor (option A). 3 x 2 holds three (B). 3 x 3 holds
four in a round tub (C). `figures_check` proves the four apart, and
`sit_faults` proves each one clear of the body. The arms clear the coping's
inner edge by about 0.05.

**Why the rim is 2.45.** The floor cannot be dug. The bench must stand 1.1
over the tub's floor for the hanging shins, and MODELS.md's tub wants the
water to the waist with the head above it. That puts the water at
seat + 1.1 = 2.3 and the coping at 2.45 (Pieces' 2.5). The treads (0.6, 1.2)
are the way up. The code puts the guest on the spot (the body does not
collide).

## The Pieces rows the code needs

| id | main's row | needs | keyFor | spots |
|---|---|---|---|---|
| `HotTub` | 2 x 2, Floor, height 2.5 | **3 x 3**, Floor, height **3.7** | Spa | `Use_1..4` Sit (in water) |
| `MassageTable` | 1 x 2, Floor, height 2.8 | 1 x 2, Floor, height **2.35** | Spa | `Use_1` Lie |

- **HotTub's w x d must change.** The script overrides the row for the kit's
  Pieces check (`PROPOSED`), and `validation.json` `pieces_rows` records it.
- **MassageTable's height is a finding** (`height_findings`: 2.8 against the
  top's 2.33). The bolster that brought it to 2.67 went after blind review 2.

## Silhouettes (grey, three a piece)

`-- grey` builds them into `silhouettes/` (not in git, not for import):
- `silhouettes/review/silhouettes_game.png` (the game's raised camera)
- `silhouettes_side_1.png` (tubs) and `_2.png` (tables)
- `silhouettes_top_tubs.png`

They were rebuilt after the reviews with the shared helpers, so they show
today's corner treads and cradle. Every grey option passes the same spot
checks.

- Tub A: 2 x 2 (the row's size), a square tub with cut corners and a bench
  along the back. **One visitor**; it shows why the size must change.
- Tub B: 3 x 2, a long square tub with a U of bench: three visitors, one at
  the back and one at each end. It reads as a bath or a small pool.
- Tub **C** (chosen): 3 x 3, round, the bench all round: four visitors. It
  reads as a hot tub at once, and four is the most a 3-square piece holds.
- Table **A** (chosen): four turned legs, an apron, a shelf below. It reads
  as a massage table, and the shelf carries the spa props.
- Table B: two gothic trestle ends with pointed arches. It reads as a bench
  or a trestle table.
- Table C: a cabinet base with pointed-arch panels. It reads as an altar or
  a sarcophagus.

## Validated (validation.json)

These checks ran on the built and the re-imported triangles:
- the kit's furniture rules: footprint 3w x 3d, the 0.4 inset, at most 7
  tall, `Body` not colliding, no coplanar faces, glow colours only in glow
  parts, budget 1,500, the atlas, and w, d and layer as the row says
  (HotTub's proposed row);
- nothing floats;
- `spots_check` for every `Use_<n>`.

Both pieces pass.

**One branch was added to the shared spot validator** in
`tools/build_activity_bar.py`, and it is purely additive: it is reached only
by a `Sit` under a piece's `Water`, and no other set has one. No other set
was rebuilt. The branch, `soak_faults`, checks:
- the Water is not colliding;
- the spot is on a declared seat, with the solid body (the water left out)
  under it to 0.15 and nothing over it for 1.5;
- the water's top over the seated torso (its middle and four corners) is
  1.0 to 2.0 over the seat: in it to the waist, the shoulders and head above
  it;
- the seated 5-stud person (`sit_blocks`, arms included) is clear of the
  solid body.

`soak_findings` records each spot: seat 1.2, water 2.3, shoulders 3.2, head
top 4.2.

**Added in the spa script, for these pieces only:**
- `tub_seat`: rule 6's seat checks (1.2 deep along the sitter's look, 2.0
  across, nothing over it for 3) on the solid body, its top at 1.1 to 1.4
  instead of 1.5 to 2.0, because the bench is under water.
- `figures_check`: no two seated figures overlap.

**Both checks were proven to refuse**, on scratch copies (since deleted):
- water at 3.4 was refused ("the water over the seated torso ... 3.40, not
  2.20..3.20");
- spots at r 2.9 were refused ("the piece goes through the seated person's
  one arm").

The massage table's `Lie` is the standard check (`lie_faults`): the lying
5-stud person is in the footprint and on the piece, with nothing rising
through it. Its head lies on the cradle (z 1.5 to 2.5; the cradle 1.5 to
2.58, its top 2.2, a drop of 0.13).

Not validated:
- anything in Studio: the attachments and Pose attributes exist only in the
  manifest until `import_fixup.luau` runs;
- a visitor walking to a spot, getting into the tub, sitting in the water or
  lying face down (no walker or clip has run);
- the Water made water, and the candles and embers lit (the code does it).

## Blind review 2026-10-26

Three runs, each by a fresh reviewer on new pictures after the fixes before
it: `review/blind/`, `blind2/` and `blind3/` (not in git).

Run 1:
1. No walk-in route; the rim about 3 high. **False on the heights** (the rim
   is 2.45, the bench 1.2). The step reading was **confirmed**; run 2
   reopened it.
2. The guest's head is on the pad, not the cradle. **False**: the head lies
   at z 1.5 to 2.5 on the cradle, which it covers from the game's camera.
3. The face cradle reads as a toilet seat. **Confirmed, fixed**: it is now a
   padded horseshoe 0.1 under the pad, on a dark stem.
4. A lit candle under the table by the linen, unseen from the camera.
   **Confirmed, fixed**: the candles are gone; a second oil bottle is there
   instead.
5. The props are specks, and the steam puffs read as a pebble stack.
   **Confirmed, fixed**: the brazier stands on a stand, its bowl over the rim,
   and the candelabra replaces three loose candles.
6. The four corner blocks read as leftovers of a square base. **Confirmed,
   fixed**: all four are steps alike; run 2 reopened it.
7. The back seat looks higher than the side seats. **False**: every seat is
   at 1.2 (`soak_findings`).
8. The tub is near-black from the game camera, and the lower hoop is off the
   steps' line. **Confirmed, fixed**: the staves are violet and plum, and the
   lower hoop sits just over the treads (1.26).
9. Crowded with four. Overlap is **false** (`figures_check`); the number of
   visitors is **his call** (below).

Run 2:
1. The bolster clips through the flat-lying guest's legs. **Confirmed,
   fixed**: the bolster is removed. It passed the Lie rule (0.38 under the
   legs), but the flat clip would go through it.
2. No way in; gaps between the corner blocks. **His call** (the second time;
   below).
3. Arms into the rim and into a neighbour's head. **False**: the static
   figure clears the coping by 0.05 and the others by `figures_check`. It is
   the camera's projection.
4. The table is narrower than the avatar, the arms in mid-air. **False by the
   contract**: a 1-square table; the 3.8-wide figure's arms overhang, as at
   the Gym's bench. A face-down massage pose with the arms down at the sides
   is the clip's.
5. The brazier's contents read as crystal or crumpled paper, and the black
   iron is off the palette. **Confirmed, fixed**: the wisps are removed, the
   embers glow under the stones (`Glow_Warm_2`), and the bowl is gold.
6. The corner blocks read as blockout crates. **Confirmed, fixed**: each
   corner has two treads now.
7. The coping is the floor's flat grey. **Confirmed, fixed**: the coping and
   treads are pale stone (bone).
8. The candelabra is a thin wisp. **Confirmed, fixed**: a thicker stem, base
   and arms.
9. The guest is not flush with the table. **False**: that is the review
   figure's arm block (0.9 against the torso's 1.0).
10. The cradle reads as a horseshoe magnet. **His call** (below).

Run 3 (the last round):
1. The brazier stands on a step. **His call**: the back corners carry the
   props, and the front two are the way in.
2. The steps stop halfway; there is a climb over the rim. **False on the
   numbers** (the rim is 2.45, the treads 0.6 and 1.2, the bench 1.2 inside).
   The rim's height is **his call** (the third time; below).
3. The two treads do not match: a wedge and a small block. **His call**
   (look).
4. The table is narrower than the avatar. **False by the contract**, as
   run 2's item 4.
5. The water is up to the brim. **False**: it is 0.15 under the coping, as
   the Pool's. The water can drop only 0.1 (the waist rule).
6. The dark legs vanish into the plum pad. **Confirmed, fixed after run 3**:
   a cream sheet over the pad (0.03 thick; the Lie point is on it). It has
   not been re-reviewed.
7. Without guests it reads as a fountain basin: no steam, jets or bubbles.
   **His call**: steam would need an emitter name in MODELS.md.
8. The brazier reads as a birdbath. **His call**: unlit here; the embers
   glow at runtime.
9. The feet meet in the middle. **False** (`figures_check`).
10. The candelabra is on the rim, tabletop size. **False on the place**: it
    stands on the back-right upper tread, outside the coping. Its size is
    **his call**.

## His calls (for WAITING.md; this session did not edit it)

- **HotTub 3 x 3, four visitors.** I recommend it: the row's 2 x 2 holds one.
  The alternative is 3 x 2 with three (option B).
- **The rim at 2.45 and the corner treads as the way in.** Three reviewers
  saw no way in. I recommend keeping it: the waist-deep water needs the rim,
  and the code places the guest. The alternative is water to the hips (rim
  about 1.9), where the guest barely reads as in the water.
- **The props on the back treads** (the brazier and the candelabra) and the
  treads' look (a wedge and a diagonal block). I recommend keeping them.
- **Steam.** Solid steam read wrong twice. I recommend a name in MODELS.md
  (an attachment such as `Steam_1` over the brazier and the water) for the
  code to put a ParticleEmitter on.
- **The face cradle**: the horseshoe (open at the head end) against a closed
  pad. I recommend the horseshoe.
- **The massage table's row height**, 2.8 to 2.35.
- **The face-down pose and the arms hanging at the sides** are the clip's.
  Today's `Lie` says nothing about face up or down.
