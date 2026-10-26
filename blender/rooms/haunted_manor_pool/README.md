# Haunted Manor: the Indoor Pool's pool and lounger (GDD A.13)

The Indoor Pool type's key piece and its first Poolside piece (GDD A.13.2, the
Indoor Pool row; A.13.3, the Poolside set) in Haunted Manor's dress, to
`MODELS.md` "Furniture" and "Activity furniture: visitors' spots". Built by
`tools/build_activity_pool.py`, which runs `tools/build_activity_bar.py`'s
definitions (and through it `tools/build_built_rooms.py`'s kit) without their
mains; a draft for August's look, 2026-10-26. **Nothing here has been seen in
Studio, and nothing is staged for import.** The models belong in
`HotelKit.HauntedManor`; they have their own set folder so no other set's
manifest is rewritten.

## What is in it

| Model | What | Spots | Top | Triangles |
|---|---|---|---|---|
| `Furniture_Pool` (4 x 2, `Floor`) | A basin standing on the floor: a plum wall with a row of crimson lozenge tiles under a stone coping at **0.86** (stepped over; the floor cannot be dug), a short stone finial post on each corner, a teal floor with a night-blue tile border, the water 0.14 under the coping; on the back rim's middle a stone pier with a gargoyle crouched on it, leaning out over the water, its stream falling from its open mouth onto a small splash ring | `Use_1..Use_3` `Swim`: (-3.5, 0.72, -0.52), (0, 0.72, -0.52), (3.5, 0.72, -0.52), looking -Z | 3.15 | 1,228 |
| `Furniture_Lounger` (1 x 2, `Floor`) | A dark-wood deck lounger on four legs, side rails and slats, a crimson cushion at **1.1** raised into a head rest over the head's last 1.25 (to 1.8), a pointed-arch board behind it, a folded cream towel with a teal stripe at the foot | `Use_1` `Lie`: (0, 1.1, -0.05), looking -Z (the feet toward the front, the head on the rest at +Z) | 2.12 | 240 |

Parts: both `Root` and `Body` (not colliding); the pool also **`Water`** (one
part, not colliding, CanQuery false: the code makes it water), **`Jet_1`** (the
stream and its splash ring, not colliding: MODELS.md "Decor", a fountain's
falling stream, which the code may dress) and a `LOD_Proxy` (wider than 2
squares). `import_fixup.luau` gives each `Use_<n>` its `Pose` attribute.

**Why 4 x 2.** MODELS.md's `Swim` puts a swimmer 1.5 inside the pool's inner
edge, and two spots never share a square. With a 0.5 wall and its coping, a
3 x 2 pool (GDD A.13.2's size, the code branch's row) leaves the swimmers a
strip 4.1 x 1.1 down its middle: two swimmers 4 apart, or three 2.4 apart
(torsos 2 wide nearly touching). 4 x 2 gives a strip 7.1 x 1.1: three
swimmers 3.5 apart, each on its own square, the same three as the Bar's
counter and the Cinema's row, and it reads as a swimming pool, not a tub.
3 x 3 (option C) holds four but reads as a fountain basin. The code branch's
`Pool` row (3 x 2, height 1.5) must change to 4 x 2, height 3.15: his call
below.

## Silhouettes (grey, three a piece)

`-- grey` builds them into `silhouettes/` (not in git, not for import):
`silhouettes/review/silhouettes_game.png` (the game's raised camera),
`silhouettes_front_1.png` (pools), `_2.png` (loungers). Every grey option
passed the same spot checks.

- Pool A: 3 x 2, a plain rectangle, the gargoyle on the back rim: two swimmers
  (above); compact but nearly a tub.
- Pool **B** (chosen): 4 x 2, a lap pool with a finial post on each corner and
  the gargoyle: three swimmers, reads as a pool at once.
- Pool C: 3 x 3, an octagonal basin, the gargoyle on the back facet: four
  swimmers, reads as a cloister fountain (and the Graveyard Garden has a
  Fountain).
- Lounger **A** (chosen): a wooden deck lounger on four legs: reads as a
  poolside lounger.
- Lounger B: a wrought-iron daybed on splayed side frames with a rolled head
  end: reads as a daybed.
- Lounger C: a stone slab on two gothic trestles with a bolster: reads as a
  tomb slab or a bench.

## Validated (validation.json)

On the built and the re-imported triangles: the kit's furniture rules
(footprint 3w x 3d, the 0.4 inset, at most 7 tall, `Body` not colliding, no
coplanar faces, glow colours only in glow parts, budget 1,500, the atlas),
nothing floats, and `spots_check` for every `Use_<n>` (from 1 without a gap,
a Pose from MODELS.md's list, level, no two on a square). **Swim**
(`swim_faults`, new in `build_activity_bar.py`): the one `Water` part present
and not colliding, the spot on its top to 0.02, and nothing else of the
piece (rim, pier, gargoyle, stream) within 1.5 round the spot from the basin's
floor to 2.5 over the water. **Lie** (a branch of `spots_check` calling the
kit's `lie_faults`): inside the footprint, on its surface, nothing over it,
and the lying 5-stud person in the footprint, on the piece, nothing rising
more than 0.45 under the legs and torso or 0.8 under the head's last 1.2.
Both pieces pass. The rim is 0.86 tall (stepped over); nothing collides.

The Lie and Swim branches are new arms of the one spot validator in
`build_activity_bar.py`; the Bar's and the Cinema's pieces never reach them
(Stand, Dance, Watch) and **neither set was rebuilt**.

**Pieces.luau on main has no rows for them**; `validation.json`
`pending_pieces_rows` is what the rows must say: `Pool` 4 x 2 `Floor`, height
3.15, `keyFor = { "IndoorPool" }`; `Lounger` 1 x 2 `Floor`, height 2.12; both
`furniture = true` (the code branch `claude/room-types` has Pool 3 x 2 height
1.5 and Lounger 1 x 2 height 2.0).

**The swim depth (a finding, `validation.json` `swim_findings`).** MODELS.md
puts a swimmer's middle 1.5 under the water (shoulders at the surface, the
head over it, the feet 4 under it). The floor cannot be dug, so the water is
0.72 over the floor: the body's middle is 0.78 under the floor and the feet
3.28 under it, through the 1-stud slab into the room below. The renders draw
the swimmer only above the basin's floor (the head, the shoulders under the
water). His call below.

Not validated: anything in Studio (the attachments and Pose attributes exist
only in the manifest until `import_fixup.luau` runs), a visitor walking to a
spot, stepping over the rim, swimming or lying (no walker or clip has run),
the `Water` made water and `Jet_1` dressed (the code does it; nothing does
yet).

## Blind review 2026-10-26

Three runs, a fresh reviewer each on new pictures after each fix:
`review/blind/`, `blind2/`, `blind3/` (not in git).

Run 1:
1. Half the swimmers' heads under water, "drowning": **false**, the review figure's skin-coloured arms under the water; the figure's sleeves now blue.
2. Five to seven guests crammed in: **false**, three spots 3.5 apart (the same misreading of the arms).
3. The lounger reads as a bed (flat, pillow, headboard): **confirmed, fixed** (the cushion rises into a head rest within the Lie rule's 0.8; the pillow went).
4. Arms past the lounger's edges, feet past its end: **false by the contract** (MODELS.md's Lie: arms may lie past the edge over nothing; the feet end 0.05 past the cushion, on the frame; lie_faults passes).
5. The stream reads as a pipe with a capped end under the water: **confirmed, fixed** (tapered, ending on a splash ring at the surface); reopened in runs 2 and 3.
6. A star on the floor reads as shards: **confirmed** (the floor's tile star seen through the water), made blunter; removed after run 2.
7. Gargoyle small, reads as a bat or cat: **his call** (below).
8. The pier seen through the water, "sunk": **confirmed, fixed** (its front moved inside the rim; finished in run 2).
9. Reads as a fountain; the gold and red diamonds as a casino skirt: **in part fixed** (the tiles one colour, crimson); the rest his call.
10. Lounger low: **false**, the cushion at 1.1 (a lounger's height for a 5-stud person; a bed's is 2).

Run 2:
1. The lying guest wider than the lounger: **false by the contract** (run 1, 4); two loungers side by side clip arms: **his call** (as at the Bar and the Cinema: one spot a square).
2. The head inside the head rest: **confirmed for the review figure** (a flat block on the Lie point); the rest rises 0.7 under the head, inside the contract's 0.8: **his call** with the clip (the Lie clip with the head raised).
3. The stream a pole: **his call / the code's** (`Jet_1` is for the code's water effect).
4. Gargoyle paws float past the cap: **confirmed, fixed** (paws on the cap).
5. Swimmers read as crates: **his call** with the swim clip (the review figure is blocks).
6. Stray polygon on the floor: **confirmed, fixed** (the star removed).
7. Pier seen through the water: **confirmed, fixed** (its front inside the wall, the lining continuous).
8. Lounger reads as a daybed: his call (look).
9. Diamond band reads as a casino skirt: **his call** (second time; below).
10. The towel floats from the side: **false**, it lies on the cushion (nothing floats passed).

Run 3 (the last round):
1. The stream reads as a pole holding the gargoyle up: **his call / the code's** (third time; the code dresses `Jet_1`, see below).
2. Swimmers read as crates; sunk 4 under a floor a player stands on: **his call** (the depth finding, below).
3. Lounger reads as a bed or cot: his call (look; reopened after run 1's fix).
4. The lying guest's head in the head rest: his call (run 2, 2).
5. Reads as a fountain or plunge tub: **his call** (the footprint and the finials).
6. The stream's top cap in front of the lower jaw: **confirmed** (0.06 ahead of it), **fixed after run 3** (its top between the jaws; not re-reviewed). The splash ring opaque: the code's to dress.
7. Gargoyle too small and dark to read on a phone: **his call** (below).
8. Arms past the square: his call (run 2, 1).
9. The water low in the basin: **false by design**, 0.14 under the coping as a pool's is.
10. Lounger exactly as long as the guest: **false by the contract** (1 x 2 is 5.2 of body for the 5-stud person).

## His calls (for WAITING.md; this session did not edit it)

- **The footprint**: 4 x 2 with three swimmers (built), or GDD's 3 x 2 with
  two. Recommend 4 x 2; the code branch's `Pool` row follows (4 x 2, height
  3.15).
- **The swim depth**: the contract's swimmer reaches 4 under the water, so
  with an undug floor its legs go through the slab into the room below.
  Recommend the code hide the swimmer's legs while it swims (only the head
  and shoulders show, which is what a pool shows), or a swim clip with the
  legs folded; a raised tank pool (rim about 4) is the alternative and loses
  the step-over rim.
- **The stream**: three reviewers read the opaque `Jet_1` as a pole.
  Recommend the code make it translucent water with a falling effect, as
  MODELS.md lets it for `Jet_<n>`.
- **The gargoyle's size**: about 1.5 tall on a 1.7 pier; larger pushes its
  stream onto the middle swimmer's 1.5. Recommend keeping it, or two
  swimmers and a larger gargoyle.
- **Looks**: the crimson lozenge band (reviewers: a casino skirt; recommend
  keeping, or plain stone), the corner finials (fountain read), the lounger's
  head rest and arched board (recommend keeping).
- **Spacing**: loungers side by side and swimmers 3.5 apart clip a 3.8-wide
  person's arms; recommend one spot a square, as at the Bar and the Cinema.
