# Haunted Manor: the Billiard Hall's cue rack, scoreboard and wall lamp (GDD A.13)

The Billiard Hall type's other furniture (GDD A.13.2, the Billiard Hall row;
its key piece, the `PoolTable`, is in `blender/rooms/haunted_manor/` with its
Play spots) in Haunted Manor's dress, to `MODELS.md` "Decor", "Furniture"
and "Activity furniture: visitors' spots". Built by
`tools/build_activity_billiards.py`, which runs
`tools/build_activity_karaoke.py`'s definitions (and through it
`tools/build_activity_bar.py`'s and `tools/build_built_rooms.py`'s kit)
without their mains; a draft for August's look, 2026-10-26. **Nothing here
has been seen in Studio, and nothing is staged for import.** The models
belong in `HotelKit.HauntedManor`; they have their own set folder so no other
set's manifest is rewritten.

All three are `Wall` pieces that hang: the back on the wall's plane (z = 1.1
for a 1-deep piece), held by the wall as the `DartsBoard` is (`hung_check`).
None has a visitor's spot (`ActivityKit.luau`: `spots = none, body =
onWall`). Of the PoolTable's family: dark wood, the table's green (`moss`)
in the lamp's shade, gold, the Manor's plum and crimson, the pointed arch.

## What is in it

| Model | What | Top | Triangles |
|---|---|---|---|
| `Furniture_CueRack` (1 x 1, `Wall`) | A dark-wood pointed-arch backboard (0.85 to 6.08) with a plum inset; a wood ledge on two corbels (their feet 0.6 over the floor) with a gold cup for each butt; a slotted wood rail at 4.6; five cues upright, 4.3 long (black bumper, wood butt, crimson or black wrap between gold rings, pale shaft, white ferrule, blue chalked tip), 0.22 across at the butt (thicker than true, so no hairline from the game camera) | 6.08 | 1,120 |
| `Furniture_Scoreboard` (2 x 1, `Wall`) | A dark-wood board 5.0 long, hung over the heads (5.05 to 6.35); two gold wires of bone and crimson beads in fives (ten a wire, the score pushed right) across a plum panel between wood end posts; a pointed-arch crest to 6.95 with an eight-ball medallion (black, a white circle, the 8 as two ink rings), gold finials | 6.95 | 948 |
| `Furniture_WallLamp` (1 x 1, `Wall`) | A dark-wood pointed-arch plate with a gold boss; an iron gooseneck (0.16 thick, a Bezier in eight runs) leaving it at 45 degrees and curving over into the gold collar of a green shade 1.16 across, 1.6 out from the wall, its rim at 5.7; the bulb `Glow_Warm_1` under the rim (its bottom 5.6, 0.6 over a 5-stud head) | 6.70 | 620 |

Parts: `Root`, `Body` (not colliding), the lamp's `Glow_Warm_1`, `LOD_Proxy`
on each (over 4 tall). `import_fixup.luau` lights the glow Neon. No light
source is in the model.

## The Pieces rows

| id | w x d | layer | main's height | the model's top | needs |
|---|---|---|---|---|---|
| `CueRack` | 1 x 1 | Wall | 6.0 | 6.08 | nothing |
| `Scoreboard` | 2 x 1 | Wall | 6.0 | 6.95 | **height 7.0** |
| `WallLamp` | 1 x 1 | Wall | 6.5 | 6.70 | nothing |

w, d and layer match main's rows. **One row must change: `Scoreboard`'s
height to 7.0** (`validation.json` `height_findings`, not refused): at 6.0
the board hung at head height and every guest at the wall hid it from the
game camera (blind review 1, finding 1); it now hangs over the heads under
the cap of 7. `src/` is not touched here; the code session changes the row.

## Silhouettes (grey, three a piece)

`-- grey` builds them into `silhouettes/` (not in git, not for import):
`silhouettes/review/silhouettes_game.png` (the game's raised camera),
`silhouettes_front_1.png` (cue racks), `_2.png` (scoreboards), `_3.png`
(lamps), `silhouettes_side.png`. Every option passed the same checks. They
were drawn before the blind review (since: the rack 0.3 higher without its
finial, the scoreboard raised and its beads bigger, the lamp 0.4 higher).

- Cue rack **A** (chosen): the upright wall rack, a ledge of cups and a rail.
  The pool hall's own rack, and it hangs (a `Wall` piece by the hanging
  rule, the floor under it free).
- Cue rack B: a fan from a low stand on the floor. Reads as cues at once, but
  it stands on the floor and its base is a plain block.
- Cue rack C: two cues crossed over a shield. A trophy, not a rack that holds
  cues.
- Scoreboard **A** (chosen): the bead board. The billiard hall's own
  scoreboard; the Game Room's `DartsBoard` already carries a chalk board,
  which C would repeat.
- Scoreboard B: a hymn board of number cards. Reads as a window grid.
- Scoreboard C: a chalk slate with tallies. The clearest "score", but generic
  (a pub's, the darts board's).
- Lamp **A** (chosen): the gooseneck with one green shade, the pool table's
  green; the arm grows out of the plate and runs into the shade.
- Lamp B: a hexagonal lantern on a bracket. The Manor's generic lamp, not a
  pool hall's.
- Lamp C: two little shades on a T-arm, the pool-table lamp in small. Busier,
  and its shades read as tiny.

## Validated (validation.json)

On the built and the re-imported triangles: the kit's furniture rules
(footprint 3w x 3d, the 0.4 inset, at most 7 tall, a `Wall` piece's back on
z = 1.1, `Body` not colliding, no coplanar faces but on the wall's face, glow
colours only in glow parts, budget 1,500, the atlas, w, d and layer as
Pieces.luau says; its height a finding), nothing floats (`hung_check`: every
shell stands on the floor or touches one that does, the wall's plane counting
as one), no open edges. All three pass. Nothing was added to the shared
validator; no other set was rebuilt.

Not validated: anything in Studio (the import, the glow lit), a piece turned
to each of the four walls by the build mode, the pieces on a 17-stud wall at
phone resolution. The previews are Workbench (unlit; Studio was running, no
EEVEE or Cycles).

## Blind review 2026-10-26

Two runs, a fresh reviewer each: pictures in `review/` (not in git; run 2
saw the rebuilt ones, `1_game_camera.png`, `2_front_level.png`,
`3_side_level.png`, `4_close_three_quarter.png`).

Run 1:
1. The scoreboard at head height, hidden by any guest at the wall: **confirmed, fixed** (beads at 4.17 and 4.73, the head 4..5; raised to 5.05..6.35, the crest to 6.95: the Pieces height finding above).
2. The scoreboard reads as an abacus; the crest's white disc as a clock or a hole; the chalk cubes as notes: **confirmed in part, fixed** (the 8 drawn on the ball, the chalk ledge gone); that a bead board reads as an abacus is **his call** (below).
3. The shade 0.3 over the head, the thin arm lost from the game camera: **confirmed, fixed** (the lamp 0.4 higher, the bulb 0.6 over the head; the arm 0.12 to 0.16).
4. The iron plate reads as a luggage tag, the half-hidden boss as a crescent: **confirmed, fixed** (the plate dark wood; the arm leaves the boss's middle at 45 degrees).
5. The rack hovers just over the floor; a shin snag: **confirmed in part, fixed** (the corbels' feet 0.3 over the floor read as a lifted cabinet; lifted to 0.6, the finial dropped to keep the top 6.08); the snag is **false for collision** (`Body` does not collide).
6. The rack reads as an arched door; the figure covers it: the figure is **false** (the preview put a person in front of it; moved back, it no longer hides it); the arch reading is **his call** (the cues read in every close view).
7. The scoreboard too small for a phone: **confirmed, fixed** (beads 0.34 across from 0.28, ten a wire from 15, the medallion with its 8).
8. The green shade off the palette: **his call** (the pool table's felt green, the billiard convention).

Run 2 (the last round; nothing after it re-reviewed):
1. The rack low, shin height, neither hung nor standing: collision **false** (`Body` does not collide); where it hangs is **his call** (below).
2. The lamp low and far out, through a jumping head; the glow hidden inside the shade from above: **his call** (the cap of 7 holds the arm's top at 6.7; a light the code adds would show the glow from above).
3. The scoreboard an abacus: **his call** (the second time). The two wires holding different counts: **false** (ten each: 6 + 4 and 8 + 2; the colour groups of five make them look uneven).
4. The arm hidden straight on, leaving the plate at its top edge, the shade closed from above: the edge is **false** (the boss at 5.75, the plate 5.15 to 6.5: its middle; the three-quarter view's angle); a shade seen from above is closed by nature, **his call** with 2.
5. The rack oversized, an empty panel over the tips: **false** (the tips at 5.6, the inset's point at 5.85, the board's at 6.08).
6. The rack's band (0.6 to 6.1) unlike the others' (5 to 7): **his call** with 1.

## His calls (for WAITING.md; this session did not edit it)

- **The scoreboard's look.** A bead board is the billiard hall's own scorer,
  but two reviewers read it as an abacus. I recommend keeping it, the eight
  ball on its crest saying pool; the alternative is silhouette C, a chalk
  slate with tallies (it repeats the darts board's).
- **Where the cue rack hangs.** Cues 4.3 long under the cap of 7 hang it low
  (its corbels 0.6 over the floor). I recommend keeping it hung; the
  alternative is silhouette B, standing on the floor.
- **The lamp's height and the glow from above.** The shade's rim at 5.7, 1.6
  out from the wall, the bulb under it; from the raised camera you see the
  shade's top. I recommend it as built and a light added by the code under
  the shade; the alternative is a shorter arm (less over the guests, less
  over the table side).
- **The green shade** (`moss`, the table's felt) in the Manor's palette: I
  recommend it.
- **Scoreboard height 7.0 in Pieces.luau** (the code session's).
