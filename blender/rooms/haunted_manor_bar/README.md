# Haunted Manor: the Bar's counter and small stage (GDD A.13)

The Bar type's two key pieces (GDD A.13.2, the Bar row; A.13.3, the Stage
set) in Haunted Manor's dress, to `MODELS.md` "Furniture" and "Activity
furniture: visitors' spots". Built by `tools/build_activity_bar.py` (which
runs `tools/build_built_rooms.py`'s definitions without its main); a draft
for August's look, 2026-10-26. **Nothing here has been seen in Studio, and
nothing is staged for import.** The models belong in `HotelKit.HauntedManor`
with the rest of `blender/rooms/haunted_manor/`; they have their own set
folder so that set's manifest is not rewritten while others build into it.

## What is in it

| Model | What | Spots | Top | Triangles |
|---|---|---|---|---|
| `Furniture_BarCounter` (3 x 1, Floor) | A plum counter with three crimson pointed-arch panels between dark posts, a dark wood top at **3.7** (overhanging the front 0.4 for a bar stool's knees), a gold foot rail; on it a gold tap tower, two pints, a goblet, a candle (`Glow_Warm_1`). Behind it, inside the same footprint, a back bar: a ledge at 3.95, bottles on two shelves either side of a gold-framed pointed-arch mirror, two glowing potions (`Glow_Magic_1`), a cornice with gold finials | `Use_1..Use_3` `Stand`: (-3, 0, -3), (0, 0, -3), (3, 0, -3), looking +Z | 6.79 | 1,452 |
| `Furniture_SmallStage` (2 x 2, Floor) | A round-fronted deck at **1.0** on a crimson skirt, a gold footlight trough with five warm bulbs (`Glow_Warm_1`) along its front, a microphone stand; at the back a dark wood pointed arch, crimson curtains drawn aside before a night-blue panel with a gold crescent | `Use_1` `Dance`: (0, 1.0, 0.3), looking -Z | 6.95 | 792 |

Both have `Root`, `Body` (not colliding), their glows and a `LOD_Proxy`
(wider than 2 squares or over 4 tall). `import_fixup.luau` gives each
`Use_<n>` its `Pose` attribute.

**Why 3 x 1 for the counter.** The contract's footprint is whole 3-stud
squares with the body 0.4 inside: 3 x 1 is 8.2 x 2.2 of body, enough for a
1.6-deep counter and a 0.6-deep back bar, and its three front squares give
the three `Stand` spots MODELS.md asks for (one a square, 1.5 in front). A
3 x 2 would add an aisle behind the counter (a server's place) that no
guest uses and that blocks a second row of squares; there is no bartender
in the design. His call below.

## Silhouettes (grey, three a piece)

`-- grey` builds them into `silhouettes/` (not in git, not for import):
`silhouettes/review/silhouettes_game.png` (the game's raised camera) and
`silhouettes_front_1.png`, `_2.png` (level, from the front).

- Counter **A** (chosen): the counter with a back bar (shelves of bottles,
  an arched mirror), 6.55. Reads as a bar at once from the raised camera; the
  back bar is the "back shelf feel" inside the frame. One-sided: it belongs
  against a wall.
- Counter B: an island counter the full depth, a low stepped bottle rack on
  its back half and a tap tower, 5.5. Works mid-room from both sides, but
  reads more as a buffet or tap counter.
- Counter C: the counter under a canopy on two end posts with glasses
  hanging from it, a low bottle ledge, 6.7. Busier, reads as a market stall.
- Stage **B** (chosen): a round-fronted apron deck under a pointed-arch
  backdrop with curtains drawn aside, 6.95. Unmistakably a stage, faces its
  audience, and carries the Manor's pointed arch.
- Stage A: a plain square deck with a side step and footlights, 4.5: reads
  as a platform or podium (a plain single-idea shape, taste.md).
- Stage C: a square deck with a proscenium at the front (posts, valance,
  drapes), 6.9: frames the performer but its front posts stand between the
  performer and the room.

## Validated (validation.json)

On the built and the re-imported triangles: the kit's furniture rules
(footprint 3w x 3d, the 0.4 inset, at most 7 tall, `Body` not colliding, no
coplanar faces, glow colours only in glow parts, budgets 1,500, the atlas),
nothing floats, and `spots_check` for every `Use_<n>` (from 1 without a gap,
a Pose from MODELS.md's list, level, no two on a square; `Stand` on the
floor at a front square's middle 1.5 in front facing +Z with its square free
of the body; `Dance` on a flat deck inside the footprint with the 5-stud
person's whole figure, 3.8 across and 5.2 tall, clear of the body). Both
pieces pass.

**Pieces.luau has no rows for them** (the code branch adds them); the kit's
Pieces check ran against the script's `PENDING`, and
`validation.json` `pending_pieces_rows` is what the rows must say:
`BarCounter` 3 x 1 Floor, height 6.79, `keyFor = { "Bar" }`; `SmallStage`
2 x 2 Floor, height 6.95; both `furniture = true`.

Not validated: anything in Studio (the import, the attachments and Pose
attributes exist only in the manifest until `import_fixup.luau` runs), a
visitor walking to a spot, standing or dancing (no walker or clip has run),
the glows lit (Workbench shows them unlit).

## Blind review 2026-10-26

Three runs (a fresh reviewer each, on new pictures after each fix):
`review/blind/`, `blind2/`, `blind3/` (not in git).

Run 1:
1. No room behind the counter for a server: **his call** (below).
2. The stage's step read as a dropped crate (the deck is 1 high): **confirmed, fixed** (removed; `Body` does not collide and the code places the performer). Its "extra footprint square": false, it was inside the 2 x 2.
3. Maroon shapes between the guests and the counter: **false**, the counter's crimson arch panels seen between the guests; spots_check proves the three front squares free.
4. Gold blocks on the deck read as litter: **confirmed, fixed** (the four footlight hoods became one gold trough with five bulbs).
5. Microphone stand a hairline: **confirmed, fixed** (pole 0.14 thick, a larger head). "Off to the side": false, it is at x 0 with the performer (the camera's angle).
6. Counter too tall: **false by the contract** (MODELS.md: a counter 3.4 to 3.8; the BarStool's 2.6 seat is built to it); lowering to 3.4 is **his call** (below).
7. Stage reads as a wardrobe from the side; narrow: from the side any backdrop is a slab (the game camera reads it as a stage); the width is the 2 x 2 asked for: **his call** with the size.
8. Bare backs: **his call** (below).
9. Blank gold plates (the arch's keystone, the crest over the mirror): **confirmed, fixed** (both removed).
10. Curtains did not separate from the panel, all dark: **confirmed, fixed** (curtains crimson, the back bar's panel plum).
11. Navy poking out behind the arch top: **false**, the backdrop panel behind the frame, under its gable (6.85 against 6.95).
12. Candelabra in the counter's middle: it is the tap tower; moved after run 2.

Run 2:
1. Guests 3 studs apart clip arms (a 3.8-wide person): **confirmed by geometry, his call**: the contract puts one spot on each square (MODELS.md), which is 3 apart; two spots on three squares, or the clip's arms down, are the alternatives.
2. The performer stands 2.15 behind the microphone: **confirmed, his call**: the `Dance` spot keeps the whole 3.8-wide figure clear, so the stand cannot be at a singer's mouth; a singer's pose at the mic, or the mic as a prop to one side, is the choice.
3. Microphone above the head: **false**, measured from the floor; its head is 4.46 over the deck, a performer's mouth about 4.4 over it.
4. Bare backs: his call (below).
5. Jogs where the stage's posts meet its arch: **confirmed, fixed** (the head as deep as the posts). The back bar's: false (0.02).
6. The foot rail in the guests' squares: **false**, it is at z -1.05, inside the footprint; the guests' fronts are at -2.5.
7. Tap tower before the mirror at the middle spot: **confirmed, fixed** (moved to x -1.5, a pint at the middle).
8. Mirror reads as a window: his call (run 3, 3).
9. Counter thin: the 3 x 1 footprint; his call with item 1 of run 1.

Run 3:
1. Counter too tall (second time): **his call**: 3.7 is inside the contract's 3.4 to 3.8; recommend keeping it unless he lowers the contract (the BarStool would follow).
2. Arch too narrow, curtains in a dancer's way: **false by geometry** (spots_check: nothing within 1.9 of the spot up to 5.2 over the deck; the nearest curtain is 1.97 away); the width is his call with the size.
3. Mirror reads as a daylit window: **his call** (a look); recommend a darker blue (`moon_dark`).
4. Counter top dark on a dark front from the game camera: **his call**; recommend a lighter wood top.
5. Guests offset from the counter: **false**, the spots are the square centres x -3, 0, 3 (spots_check to 0.01); the end guests' arms reach 0.4 past the 9-stud counter.
6. Microphone base on the footlight lip: **false**, 0.07 clear.
7. Bare backs: his call (below).
8. Top shelf out of reach: false, nobody takes a bottle; the back bar is within the 7-stud limit.
9. Footlight bulbs read as rivets: **false in this render**: they are `Glow_Warm_1`, lit (Neon and a light) by the import fix-up; Workbench draws them unlit.

## His calls (for WAITING.md; this session did not edit it)

- **The counter's footprint**: 3 x 1 with the back bar inside it (built),
  or 3 x 2 with an aisle behind for a server. Recommend 3 x 1.
- **Backs**: both pieces are one-sided (the back bar and the backdrop face
  the room; their backs are plain). Finished backs cost about 300 triangles
  the counter has not got (1,452 of 1,500). Recommend: wall-side pieces, as
  built.
- **Spacing at the counter**: three `Stand` spots 3 apart, where a 3.8-wide
  person's arms overlap the next. Recommend keeping one a square (the
  contract) and the drink clip's arms down.
- **The performer and the microphone**: `Dance` with the stand as a prop
  2 in front (built), or a singer's pose at the stand. Recommend `Dance`
  until the clips exist.
- **Looks**: the mirror's blue (recommend darker), the counter top's wood
  (recommend lighter), the counter's 3.7 (recommend keeping), the stage's
  2 x 2 width.
