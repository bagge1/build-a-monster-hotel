# Event decor: the Jack-o'-Lantern and the Snowman (every location)

The two season-shop decor pieces (GDD §8.2: the Halloween Candy shop's
Jack-o'-Lantern, 30 Candy, tags candles and garden; the Winter shop's Snowman,
30 Snowflakes, tags cold and snow, "the Frostfang crossover"). In `Pieces.luau`
both are location 0, not `always`, not furniture: event decor
(`Pieces.isEventDecor`), placeable at any hotel once bought (`decorHere`). So
by MODELS.md "Decor" they are **one model for every kit**, in their own set,
their colours their own (`EV_PALETTE`), saved one day into
`assets/HotelKit/HauntedManor/Decor_<Id>.rbxm` where the code looks after the
location's kit. Built by `tools/build_projector_event.py -- event` (the same
script as the Cinema's projector, `blender/rooms/haunted_manor_projector/`); a
draft for August's look, 2026-10-26. **Nothing here has been seen in Studio,
and nothing is staged for import.**

| Model | What | Top | Triangles |
|---|---|---|---|
| `Decor_JackOLantern` (1 x 1 `Floor`) | An orange pumpkin of eight lobes over darker grooves, 2.0 across; a carved face to the front (-Z): triangle eyes, a nose, a grin with two teeth, one part `Glow_Warm_1` (candlelight through the cuts); a bent green stem | 1.94 | 1,072 |
| `Decor_Snowman` (1 x 1 `Floor`) | Three snowballs on a little drift, a black top hat with a red band, coal eyes, smile and buttons, a carrot nose, a red scarf with a cream stripe and its tail down the front, twig arms raised | 4.50 | 1,480 |

`Root`, `Body` (not colliding) and the lantern's `Glow_Warm_1`; no LOD_Proxy
(decor, as the kit makes it). **The Pieces rows are main's** (1 x 1 `Floor`,
heights 2.0 and 4.5); the models agree.

## Silhouettes (grey, two options a piece)

On the projector set's sheet:
`blender/rooms/haunted_manor_projector/silhouettes/review/silhouettes_game.png`
and `silhouettes_front.png` (not in git).

- Jack-o'-Lantern **A (chosen)**: one big carved pumpkin. Its face is the
  largest the footprint allows and reads at once from the raised camera.
- B: a smaller carved pumpkin stacked on a squat plain one: the face at
  two-thirds the size.
- Snowman **A (chosen)**: three balls and a top hat. The iconic snowman, a
  layered outline (three tiers, the brim).
- B: two big balls and a knitted bobble hat: heavier, the hat reads as an elf's.

## Validated (validation.json)

On the built and the re-imported triangles: the kit's decor rules
(footprint, 0.4 inset, layer, height against Pieces to 0.3, `Body` not
colliding, no coplanar faces, glow colours only in the glow part, budget
1,500, the atlas) and nothing floats (`grounded_check`: every shell on the
floor or touching one that does). Both pass.

Not validated: anything in Studio; the face lit (Workbench draws it unlit);
placement by the build mode.

## Blind review 2026-10-26 (one run, with the projector)

Pictures in `blender/rooms/haunted_manor_projector/review/blind/` (not in
git). Triage:

1. The lantern's face lopsided (an eye smaller, the mouth shifted):
   **false**. The eyes are one outline mirrored and the nose and grin are
   centred; the picture was taken from the left, and the eyes sit on a
   curved front. Level from the front they match (`review/4_front_level.png`).
   The two teeth are offset on purpose.
2. The pumpkin giant, waist height: **his call** (look). It fills its square
   at the row's height 2.0 (the model 1.94 tall, 2.0 across); a smaller
   pumpkin would read less at the phone's distance. Recommend keeping.
3. The snowman's bottom ball coarsely faceted: **confirmed, fixed** (12 to
   14 sides, 7 to 9 rings; 1,480 triangles). Not re-reviewed (one run).
4. The snow drift under it reads as a plate indoors; both arms raised read as
   "hands up": **his call** (look). Recommend keeping the drift (it seats
   the ball on the floor).

## His calls (for WAITING.md; this session did not edit it)

- **Looks**: the pumpkin's size (recommend keeping), the drift and the raised
  arms (recommend keeping), the colours (pumpkin orange; red and cream scarf).
