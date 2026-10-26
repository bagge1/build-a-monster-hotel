# Frostfang Lodge: the Sauna's bench, stove and bucket (GDD A.13)

These are the Sauna type's three pieces (GDD A.13.2, the Sauna row: Frostfang, location 2) in Frostfang Lodge's
dress: pale birch and pine boards, iron, and ice-blue accents. They are built to `MODELS.md`'s "Furniture" and
"Activity furniture: visitors' spots" by `tools/build_activity_sauna.py`. That script runs
`tools/build_activity_bar.py`'s definitions without their main, and through them `tools/build_built_rooms.py`'s
kit and the Lodge's palette. This is a draft for August's look, made 2026-10-26.

**Nothing here has been seen in Studio, and nothing is staged for import.** The models belong in
`HotelKit.FrostfangLodge`. They have their own set folder so that no other set's manifest is rewritten.

## What is in it

| Model | What | Spots | Top | Triangles |
|---|---|---|---|---|
| `Furniture_SaunaBench` (2 x 1, `Floor`) | A two-tier bench. Flat birch slats with air gaps make the seat tier at **1.8** and the foot tier at **0.7**, with birch-board risers between them. Light-pine end boards step down with the tiers and rise at the back into the backrest's posts; each has an ice-blue snowflake carved on it. Two birch backrest boards sit under a pine cap at **3.0**. | `Use_1`, `Use_2` `Sit` at (-1.5, 1.8, 0.4) and (1.5, 1.8, 0.4), looking -Z, one per square. The feet rest on the foot tier. | 3.0 | 496 |
| `Furniture_SteamStone` (1 x 1, `Floor`) | An iron stove box (1.84 x 1.44) on four short legs. It has a black fire door with an iron-rimmed, round-topped window onto the fire (`Glow_Warm_1`), a low stack of dark logs at the window's foot and a gold knob. On top, a low cage of iron rods holds 14 grey stones, each a different size, squash, turn and tilt, heaped in a dome over the rail. | none | 2.12 | 1,104 |
| `Furniture_WaterBucket` (1 x 1, `Floor`) | Birch staves in two iron hoops, with an iron bail handle. Ice-blue water has three chunks of ice in it. A log ladle stands in the bucket with its birch handle out over the rim. | none | 1.48 | 772 |

Each model has the parts `Root` and `Body` (not colliding); the stove also has `Glow_Warm_1`. None needs a
`LOD_Proxy`: none is over 2 squares wide or 4 tall. `import_fixup.luau` gives each `Use_<n>` its `Pose`
attribute and lights the glow. **Steam is not modelled.** The Spa's README asks August for an emitter name in
`MODELS.md` for it.

## The Pieces rows

| id | w x d | layer | height | location | keyFor | spots |
|---|---|---|---|---|---|---|
| `SaunaBench` | 2 x 1 | Floor | 3.0 (the model's top 3.0) | 2 | Sauna | `Use_1`, `Use_2` Sit |
| `SteamStone` | 1 x 1 | Floor | 2.0 (the model's top 2.12, within the kit's 0.3) | 0 | — | none |
| `WaterBucket` | 1 x 1 | Floor | 1.5 (the model's top 1.48) | 2 | — | none |

Every w, d, layer and height above is main's row, so **no row needs to change.** The kit's Pieces check ran against
these rows (`validation.json` `pieces_rows`). The bench's spots also match `src/server/ActivityKit.luau`'s
blockout (`seats(W, 1.8, "Sit")`: two spots at 1.8, one per square). `SteamStone` is a location-0 piece (the Spa
uses it too), so this is the Lodge's version of it; the other kits do not have one yet.

## Silhouettes (grey, three a piece)

Running the script with `-- grey` builds them into `silhouettes/`. They are not in git and not for import. The
sheets are:
- `silhouettes/review/silhouettes_game.png`: the game's raised camera.
- `silhouettes_side_benches.png`: the benches from the side, guests seated.
- `silhouettes_front_stoves_buckets.png`: the stoves and buckets from the front.

Every option passed the same checks. They were drawn before the blind reviews. The stove's stones, door and size
and the slats have changed since.

The benches:
- **A (chosen): 2 x 1, boxed.** The seat tier at 1.8 holds two, with the foot tier at 0.7 under their soles,
  boarded risers and stepped end boards. It fits main's row and the code's blockout unchanged, and it reads as a
  built-in sauna bench (an upper bench with a foot bench under it).
- **B: 2 x 2, three tiers.** A foot step at 0.4, the lower seat at 1.5 and the upper seat at 2.6 behind it, with
  the upper sitters' feet on the lower tier, as on a bar stool's ring. That gives four sitters. It is the truest
  sauna, but it doubles the footprint and changes the row (2 x 2, height 3.8) and the blockout's spots. **This is
  August's call** (below).
- **C: 2 x 1, open.** The same tiers on a frame of round log legs and rails, with a tall backrest of vertical
  slats. It reads as a park or gym bench.

The stoves:
- **A (chosen): an iron box with a stone cage on top.** It reads as a sauna stove (kiuas), and its fire door faces
  the room.
- **B: a hearth of stones.** It reads as a campfire or a rock pile.
- **C: a round drum stove with a wooden guard rail.** It reads well, but the guard fills the square and hides the
  drum.

The buckets:
- **A (chosen): a bucket with an iron bail and a ladle standing in it.** It reads as a bucket and ladle from above.
- **B: a Nordic kiulu, with one stave running up into a handle.** It is truer, but from the camera the handle is a
  post.
- **C: a smaller bucket on a log-slice stool.** It is busy, and the bucket is small.

## Validated (validation.json)

These checks ran on the built and on the re-imported triangles:
- the kit's furniture rules: the footprint 3w x 3d, the 0.4 inset, at most 7 tall, `Body` not colliding, no
  coplanar faces, glow colours only in glow parts, the budget of 1,500, the atlas, and w, d, layer and height as
  the row says;
- nothing floats;
- `spots_check` for every `Use_<n>`.

All three pieces pass. **Nothing was added to the shared validator.** Three checks were added in the sauna script,
for these pieces only:
- `tier_seat`: rule 6's seat checks (1.5..2.0, 1.2 deep, 2.0 a person, nothing over it for 3) with a height range
  per seat. B's upper tier holds to the bar stool's 2.4..2.8.
- `feet_check`: under both soles of every bench spot (1.1 under the seat, at 18 points under the two feet) the body is
  at most 0.12 below. In other words, the feet stand on the foot tier.
- `figures_check`: sitters on different tiers do not meet. Only B has two tiers of sitters.

The first build was refused because the risers and the end boards went through the seated person's feet (the soles
reach 0.1 back under the seat's front). The risers and boards were moved behind the soles. This shows the checks
refuse.

Not validated:
- anything in Studio;
- a guest walking to the bench and sitting (no walker or clip has run);
- the fire lit;
- steam;
- the two sitters against each other. Side by side, one square apart, their arms (3.8 across) overlap by 0.8, as on
  the Cinema's row of three.

## Blind review 2026-10-26

Three runs were made, each by a fresh reviewer on new pictures after the fixes before it. The pictures are in
`review/` (not in git): `1_game_camera`, `2_front_three_quarter`, `3_back_three_quarter`, `5_top`,
`7_bench_side_in_use`, `9_bench_empty` and `10_close_stove_bucket`.

Run 1:
1. The stove reads as a barbecue grill: a flat layer of stones under the cage's rail. **Confirmed, fixed**: the
   stones are heaped in a dome over a low rail. Run 3 reopened it.
2. The fire door reads as a vent: three barred slots. **Confirmed, fixed**: it is now one round-topped window.
3. A snowflake on the one hot thing in the room. **Confirmed, fixed**: the snowflake is off the stove.
4. The stove is small for its square. **Confirmed for its width, fixed**: it is 1.84 x 1.44 now, against 1.5 x
   1.24 before. Its height is the row's (**his call**, below).
5. The tiers are step height. **False by the contract**: the seat at 1.8 is rule 6's (1.5..2.0) for the 5-stud
   person. A lower tier that is also a seat is option B (**his call**).
6. Roblox's sit pose throws the legs forward. **False by the contract**: `MODELS.md`'s Sit and the kit's seated
   figure are what is checked. The pose is the clip's.
7. The seated guests' arms clip. **False by the contract**: one guest per square, as the Cinema's row. Recorded
   above.
8. The slats have no gaps. **Confirmed, fixed**: the gaps are 0.1 now, the boards flat.
9. The wood is not pale. **Confirmed, fixed**: the end boards and cap are light pine (`wood_light`), not log brown.
10. The towel balances on the thin top rail. **Confirmed, fixed**: the towel is removed.
11. The ladle reaches into the next square. **False**: it is inside the 0.4 inset (x 0.98 of 1.1).

Run 2:
1. The bench is too small and hidden by its sitters, and the feet hover past the foot tier. **False on the feet**:
   `feet_check` holds them on the tier, and `7_bench_side_in_use` shows it. The seat height is rule 6's. The
   bench's size is **his call** (option B).
2. The stones read as hex nuts or a honeycomb. **Confirmed, fixed**: each stone now differs in size, squash, turn
   and tilt, with seven sides and four rings.
3. The door's brass rim around the warm fire reads as a ring around a dark hole, and the crossed logs as a slash.
   **Confirmed, fixed**: the rim is iron now, the fire is the warmer `lamp` colour, and the logs lie level in a low
   stack.
4. The slats read as rods. **Confirmed, fixed**: the boards are square-edged. The colours are the kit's birch and
   pine under Workbench light (**his look**).
5. The snowflake reads as an asterisk. **His look**: it is the Lodge kit's carved snowflake, which is on every
   piece of Lodge furniture. It is on both ends.
6. The bench does not fill its squares, and the legs reach the next square. **False**: the 0.4 inset is the
   contract, and the feet end at z -1.1, inside the footprint.
7. The rods are hair-thin. **Confirmed, fixed**: the cage rods are 0.055, the bail 0.05 and the ladle handle 0.065.

Run 3 (the last round; its findings are not fixed or reviewed again):
1. The stove still reads as a grill or brazier: there is no flue. **His call** (below).
2. The stove is knee high. **His call**: its height is the row's 2.0.
3. Unlit, the fire door reads as a wooden hatch. **False at runtime**: the code lights `Glow_Warm_1` Neon.
   Workbench draws it flat.
4. The bench's two ends do not match. **False**: both ends are alike by construction. In `9_bench_empty` the far
   end is seen edge-on from inside.
5. The sitters hide the end boards, and their arms meet. **False by the contract**, as in run 1.
6. The lower tier is a step. **His call** (option B).
7. The snowflake is grey-blue, like a cast bracket. **His look**: it is the palette's `ice`.
8. There is no log character: the frame is square-cut boards. **His look**: a sauna bench is boarded, and the
   Lodge's log legs are on option C.
9. The rail, the bail and the handle are still thin. **His look**: they are thickened once already. Any thicker
   and they read clumsy.
10. The ladle sticks out a stud. **False on floating**: the bowl holds it (the nothing-floats check). Its angle is
    **his look**.

## His calls (for WAITING.md; this session did not edit it)

- **The bench's size.** I recommend A: 2 x 1, two sitters, main's row and the code's blockout, the feet on the
  foot tier. The alternative is B: 2 x 2 with three tiers and four sitters. B changes the row (w x d 2 x 2, height
  3.8) and `ActivityKit.luau`'s spots.
- **The stove's height and a flue.** Three reviewers read the knee-high box as a grill. I recommend raising the
  row's height to about 3.0, which allows a taller firebox and a taller stone cage, the stones still a dome over
  it. A flue pipe up to the slab would leave decor's 7-stud limit and the footprint's frame. The alternative is to
  keep 2.0.
- **Steam.** This is the Spa's open call: a `MODELS.md` name, such as a `Steam_1` attachment over the stones, for
  the code's ParticleEmitter.
- **The look**: the Lodge's carved ice-blue snowflake on the bench ends, the colours, and the ice in the bucket.
