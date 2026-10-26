# Haunted Manor: the Cinema's film screen and seat row (GDD A.13)

The Cinema type's two new pieces (GDD A.13.2, the Cinema row) in Haunted
Manor's dress, to `MODELS.md` "Furniture" and "Activity furniture: visitors'
spots". Built by `tools/build_activity_cinema.py`, which runs
`tools/build_activity_bar.py`'s definitions (and through it
`tools/build_built_rooms.py`'s kit) without their mains; a draft for August's
look, 2026-10-26. **Nothing here has been seen in Studio, and nothing is
staged for import.** The models belong in `HotelKit.HauntedManor`; they have
their own set folder so no other set's manifest is rewritten.

## What is in it

| Model | What | Spots | Top | Triangles |
|---|---|---|---|---|
| `Furniture_FilmScreen` (3 x 1, `Wall`) | A pale screen (6.4 x 3.5, y 2.1..5.6) in a black border, a dark-wood dado under it, inside a dark-wood pointed-arch proscenium with a pyramid pinnacle on each post, on a low stage (deck 0.6) with a crimson skirt; a swagged crimson pelmet under the arch, crimson curtains drawn aside to the posts, a night-blue panel behind, a gold candle sconce on each post (`Glow_Warm_1`) | none (guests watch from the seats); neither `Use` nor `Use_<n>` | 6.95 | 684 |
| `Furniture_CinemaSeat` (3 x 1, `Floor`) | Three crimson velvet seats, tops at **1.7**, each back a crimson pointed arch on one dark-wood shell with three arches, closed to the plinth, a crimson pointed panel on the back behind each seat; four dark-wood armrests (tops 2.4, lighter caps) at the ends and between the seats; crimson-dark seat bases on a plinth | `Use_1..Use_3` `Watch`: (-2.75, 1.7, -0.25), (0, 1.7, -0.25), (2.75, 1.7, -0.25), looking **-Z** | 4.05 | 712 |

Both have `Root`, `Body` (not colliding) and a `LOD_Proxy` (wider than 2
squares); the screen its `Glow_Warm_1`. `import_fixup.luau` gives each
`Use_<n>` its `Pose` attribute.

**The `Watch` convention: LookVector -Z.** MODELS.md's furniture front is
-Z and a `Sit`'s LookVector is "the way the sitter faces"; every seat in the
kits looks -Z. So the row's front faces the screen and its spots look -Z;
the player turns the row's front toward the screen (picture
`review/10_cinema_game_camera.png`: the rows turned 180 degrees, facing it).
spots_check refuses a `Watch` spot not looking -Z.

**Why 3 x 1 for the screen, and `Wall`.** Three squares wide matches the
seat row, so a row centres on it; 3 x 1 inside the 0.4 inset and the 7-stud
cap gives an 8.2 x 6.95 frame and a 1.83:1 screen. One square deep because a
wall piece needs no depth and every extra row of squares is floor a row of
seats cannot use. `Wall` because a screen belongs only against a wall: the
layer makes the code refuse it anywhere else (Furnish: back on a wall) and
puts its back on the wall's face (z 1.1). It stands on its own stage, so the
contract's hanging rule is not needed. **The row is 3 x 1** as the task and
MODELS.md ("a row of seats, 3 wide") ask: three sitters 2.75 apart, each seat
2 wide between armrests (rule 6), the end armrests 0.35 and the inner 0.75
wide.

## Silhouettes (grey, three a piece)

`-- grey` builds them into `silhouettes/` (not in git, not for import):
`silhouettes/review/silhouettes_game.png` (the game's raised camera),
`silhouettes_front_1.png` (screens) and `_2.png` (rows), level from the
front, `silhouettes_seat_side.png` (the rows in section with a sitter). Every
grey row passed the same Watch check.

- Screen **A** (chosen): a pointed-arch proscenium on a low stage, curtains
  drawn aside. Reads as a cinema screen at once from the raised camera, and
  carries the Manor's arch and the Bar stage's curtains (one family).
- Screen B: a framed screen hung on the wall, a pelmet, floor-length
  curtains: the largest picture, but reads as a framed painting or a window.
- Screen C: a roll-down screen on a two-post stand with a roller case:
  reads as a projector screen in a classroom, the least Manor.
- Row **A** (chosen): three theatre seats, each back its own pointed arch,
  armrests between: reads as cinema seats, the arches the Manor's.
- Row B: a pew (one bench, one tall back with three pointed panels, end
  standards with points): reads as a church.
- Row C: a low velvet sofa row with a rolled back: reads as a lounge sofa.

## Validated (validation.json)

On the built and the re-imported triangles: the kit's furniture rules
(footprint 3w x 3d, the 0.4 inset, at most 7 tall, a `Wall` piece's back on
z 1.1, `Body` not colliding, no coplanar faces, glow colours only in glow
parts, budgets 1,500, the atlas), nothing floats, rule 6 for each of the
three seats (top 1.5 to 2.0, 1.2 deep, 2 wide, nothing over it for 3), and
`spots_check` for every `Use_<n>` (from 1 without a gap, a Pose from the
list, level, no two on a square; `Watch` looking -Z, inside the footprint, on
a declared seat, on its surface to 0.15 with nothing over it for 1.5, and the
seated 5-stud person, `sit_blocks`: torso, head, arms, thighs, shins, feet,
clear of the body). Both pieces pass. **The Watch check was proven to
refuse**: a scratch run with `Use_2` looking +Z and `Use_3` pushed 0.5 back
was refused (the LookVector, the thigh and the torso through the back).

`spots_check`'s new `Sit`/`Watch` branch lives in `build_activity_bar.py`
(the one validator of spots); the Bar's pieces never reach it (Stand,
Dance) and **the Bar was not rebuilt** with it.

**Pieces.luau has no rows for them** (the code branch adds them);
`validation.json` `pending_pieces_rows` is what the rows must say:
`FilmScreen` 3 x 1 `Wall`, height 6.95, `keyFor = { "Cinema" }`;
`CinemaSeat` 3 x 1 `Floor`, height 4.05; both `furniture = true`. The
screen carries no `Use`: code that expects one on every furniture piece must
skip it.

Not validated: anything in Studio (the attachments and Pose attributes exist
only in the manifest until `import_fixup.luau` runs), a visitor walking to a
seat and sitting (no walker or clip has run), the candles lit (Workbench
draws them unlit).

## Blind review 2026-10-26

Five runs, a fresh reviewer each on new pictures after each fix:
`review/blind/` .. `blind5/` (not in git).

Run 1:
1. Seats narrower than the avatar's arms: **confirmed by geometry, his call** (below).
2. The screen does not fill its squares: **false by the contract**: the body is 0.4 inside the footprint (x +-4.1 in +-4.5) and its back on the wall's face (z 1.1, the 0.4 is the wall).
3. Second row cannot see over the first: **confirmed by geometry** (a row-2 eye at 4.3 over row-1 heads at 4.7, six studs ahead): screen raised from 1.35..5.1 to 2.1..5.6; it cannot be cured on a flat floor under the 7-stud cap: **his call** (below).
4. Curtain tops poking above the head at the posts: **confirmed** (6.0 over the head's 5.95 at x 3.52), **fixed** (tops now under the head everywhere).
5. Armrests a thin plank in the section: **false**, a 0.01 sliver the section cut left (cut moved); the armrests are 0.75 wide, full depth, 0.7 over the seat (where the seated figure's arms start).
6. The back open below the shell: **confirmed, fixed** (shell to the plinth). The red lip over the scallops: false, the upholstery seen over the shell's edge from above.
7. Reads as a puppet theatre: **his call** (below).
8. Knees leave the footprint into the next row: **false by geometry**: the thighs end 1.45 ahead of the spot, the row in front starts its body 0.5 past the square line.
9. Pinnacles read as thorns: his call (look).

Run 2:
1. Seat too high, feet dangle: **false by the contract** (1.7 in 1.5..2.0, the kit's other seats 1.73..1.82; the figure's legs hang 1.1); lowering to 1.5 is his call.
2. Gap under the thighs: false, the cushion's bevelled edge at the section (the spot is on the cushion's top to 0.15).
3. Armrests on the seat: false, the reviewer read the crimson cushion as the armrest (the armrest tops are 2.4).
4. Seat pitch: his call (run 1, 1).
5. Screen small in its frame: his call (below).
6. Second row's view: his call (run 1, 3).
7. Cushion colour: false, the navy-grey is the sitter's thighs.
8. The back a flat wall: **confirmed, fixed** (a crimson pointed panel behind each seat; reopened as run 4, 1).
9. Sconces specks: his call; they glow in the game.
10. Curtain tie reads as a rope: false, the gathered tie-back as on the Bar's stage.

Run 3:
1. Seat pitch: his call. 2. The row hidden by its sitters, reads as a pew from behind: his call with run 4, 1.
3. A dark crescent over the screen under the arch: **confirmed, fixed** (a swagged crimson pelmet).
4. Screen small, second row: his call. 5. Puppet theatre, a walk-on stage: his call.
6. Knees into the next row: false (run 1, 8). 7. Footprint off-centre: false (x +-4.1, the camera's angle). 8. Detail scale: his call.

Run 4:
1. The back upholstered like the front; an empty row seen from behind may read as facing the camera: **his call** (it reopens run 2's "a wall"; recommend the panels in wood, not velvet).
2. The screen a trapezoid: false, the curtains covering its corners (item 7). Low: his call.
3. Seat pitch: his call. 4. A slate-blue box under each cushion: **confirmed, fixed** (crimson-dark bases).
5. Armrests barely exist: false by geometry (run 1, 5).
6. Puppet theatre / walk-on stage: his call.
7. Curtains over the screen's corners: **confirmed, fixed** (narrower curtains).
8. Sconces float: false (each bracket into its post; nothing floats passed). Size: his call.
9. The screen small on an 18-stud wall: his call (the 7-stud cap).

Run 5 (nothing new fixed):
1. Second row's sightline: his call. 2. The dark dado under the screen, dead space: his call with the screen size.
3. Seat pitch: his call. 4. Walk-on stage: his call (the `Body` does not collide; the code blocks its squares for guests).
5. Seat "1.5", below the knee: false, it is 1.7. 6. The back's panels: his call (run 4, 1).
7. Armrests slivers: false (run 1, 5). 8. Rows offset from the screen: false, both centred on x 0 in the scene.
9. Curtain hems into the stage: false, buried 0.02 by design. 10. Sconces: his call.

## His calls (for WAITING.md; this session did not edit it)

- **Seat pitch**: three sitters 2.75 apart in a 3 x 1 row, where a 3.8-wide
  seated person's arms overlap the next (the Bar's counter has the same).
  Recommend keeping 3 x 1 and the watch clip's arms down; a 4 x 1 row of
  three is the alternative.
- **The second row's view**: on a flat floor the front row's heads (4.7)
  hide most of a 7-stud screen. Recommend a raised row or riser later (a
  piece of its own), or lifting the 7-stud cap for the screen to about 9;
  the screen as built is as high as the cap allows with its frame.
- **The screen's look**: a proscenium on a stage (built; reviewers read
  "puppet theatre" three times) or B, a large framed screen on the wall.
  Recommend A, with a `Screen` part in MODELS.md so the code can light it or
  show a film (the code then reads as a cinema), and the dado under it
  possibly replaced by a larger screen.
- **The row's back**: crimson panels (built), plain wood, or wood panels.
  Recommend wood panels.
- **Looks**: the seat at 1.7 (recommend keeping), the sconces' size, the
  pinnacles.
- **Access**: a 3 x 1 row has no walkway; a guest reaches a seat from the
  square in front. The code keeps that square free, or the player spaces
  rows a square apart.
