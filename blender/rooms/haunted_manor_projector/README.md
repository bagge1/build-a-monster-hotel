# Haunted Manor: the Cinema's projector (GDD A.13)

The Cinema row's last "other furniture" piece (GDD A.13.2) in Haunted Manor's
dress, beside the Film Screen and the Cinema Seats
(`blender/rooms/haunted_manor_cinema/`), to `MODELS.md` "Furniture". Built by
`tools/build_projector_event.py -- projector`, which runs
`tools/build_activity_cinema.py`'s definitions without its main; a draft for
August's look, 2026-10-26. **Nothing here has been seen in Studio, and nothing
is staged for import.** The model belongs in `HotelKit.HauntedManor`; it has
its own set folder so no other set is rebuilt. The same script builds the
event decor (`blender/decor/event_decor/`), a set of its own because MODELS.md
puts event decor apart (one model for every kit, its own colours).

| Model | What | Spots | Top | Triangles |
|---|---|---|---|---|
| `Furniture_Projector` (1 x 1, `Floor`) | A black projector housing with a gold band on a dark-wood tripod stand (iron feet, collar and yoke), a gold lens barrel to the front (-Z; its glass `Glow_Warm_1`), a crank on the right (+X), two iron reels of film on arms above, front and back, in the plane of the lens | none (guests watch from the seats); neither `Use` nor `Use_<n>` | 4.49 | 1,372 |

`Root`, `Body` (not colliding), `Glow_Warm_1` (the lens) and a `LOD_Proxy`
(over 4 tall). The front is -Z, so the player turns it to face the screen, as
the seat rows (`review/6_cinema_game_camera.png`: both turned 180 degrees).

**The Pieces row is main's**: `Projector` 1 x 1 `Floor`, height 4.5,
`furniture = true`; the model agrees (top 4.49). The manifest's
`pieces_row: pending` is the shared `sdone()`'s wording; the row exists.

## Silhouettes (grey, two options)

`-- grey` builds all three pieces' options into `silhouettes/` (not in git):
`silhouettes/review/silhouettes_game.png` (the raised camera) and
`silhouettes_front.png` (level from the front), each beside the 5-stud person.
The event decor's options are on the same sheet.

- **A (chosen)**: the projector on a tripod stand. The lighter of the two, its
  two reels the one sign of a film projector; the cart reads as a side table
  with a gadget on it.
- B: the same projector on a little wooden cart with a shelf of film cans.

## Validated (validation.json)

On the built and the re-imported triangles: the kit's furniture rules
(footprint 3 x 3, the 0.4 inset, at most 7 tall, `Body` not colliding, no
coplanar faces, glow colours only in the glow part, budget 1,500, the atlas,
`w`, `d`, `layer` and height against main's Pieces row), nothing floats
(`grounded_check`), no spots. Passes.

Not validated: anything in Studio; the lens lit (Workbench draws it unlit);
the screen and the seats in the pictures are rebuilt by their own script into
`context/` (pictures only, never imported), not the imported models.

## Blind review 2026-10-26 (one run, covering the event decor too)

Pictures `review/blind/` (not in git). Triage:

1. The lens (3.06) below the seated guests' heads (4.7) and the seat backs
   (4.05): aimed at the screen, a beam would go into the rear row.
   **Confirmed by geometry; his call**: the row's height is 4.5. Recommend a
   tall pedestal (lens about 5.2, reels to about 6.5, the row's height 6.5),
   which also answers 3 and 4.
2. The reels face the wrong way (axis along the lens): **false**. The reels
   turn about X, so they stand in the lens's plane as on a real projector:
   edge-on from the front, two circles from the side
   (`review/4_front_and_side_level.png`); the picture was three-quarter.
3. Reads as a film camera on a camera tripod: **his call** (look). The
   two-reel box is both icons; a pedestal and a lamp house at the back would
   tell them apart (with 1).
4. Thin legs, a dark blob at the game's camera: **his call**, with 1 (a solid
   pedestal).
5. Off the screen's axis: **false**: it stands on x = 0 with the screen and
   the rows; the oblique camera shifts what is farther back to the left.
6. Reels empty, no film path: **false** for the film (a dark-wood coil
   r 0.3 in each reel); a film path into the body left out (no clutter,
   `taste.md`).

## His calls (for WAITING.md; this session did not edit it)

- **The projector's height**: as built at the row's 4.5, under the seated
  heads; recommend a pedestal to about 6.5 (the row's height with it) so it
  reads as projecting over the rows and not as a camera.
- **The look**: tripod (built) or a pedestal with a lamp house.
