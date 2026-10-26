# Haunted Manor: the Dance Floor's light-up floor, speaker and disco ball (GDD A.13)

The Dance Floor type's pieces (GDD A.13.2, the Dance Floor row; A.13.3, the
Stage set's speaker) in Haunted Manor's dress, to `MODELS.md` "Decor" (the
Rug layer), "Furniture" and "Activity furniture: visitors' spots". Built by
`tools/build_activity_dance.py`, which runs `tools/build_activity_bar.py`'s
definitions (and through it `tools/build_built_rooms.py`'s kit) without their
mains; a draft for August's look, 2026-10-26. **Nothing here has been seen in
Studio, and nothing is staged for import.** The models belong in
`HotelKit.HauntedManor`; they have their own set folder so no other set's
manifest is rewritten. The Bar's `SmallStage` is the Stage set's stage
(`blender/rooms/haunted_manor_bar/`).

## What is in it

| Model | What | Spots | Top | Triangles |
|---|---|---|---|---|
| `Furniture_LightFloor` (2 x 2, `Rug`) | The Victorian octagon-and-dot hall floor, 6 x 6, to its footprint's edges: an iron base (the grout) 0..0.08, 16 octagon tiles 1.4 across in a chequer, **each its own part**, `Glow_Magenta_1..8` and `Glow_Cold_1..8`, tops at 0.15; gold dots at the crossings (top 0.13), halved along the edges so floors laid side by side join into one pattern | `Use_1..Use_4` `Dance` at (-1.5, 0.15, -1.5), (1.5, 0.15, -1.5), (-1.5, 0.15, 1.5), (1.5, 0.15, 1.5), looking -Z: one a square, in the order of `src/server/ActivityKit.luau`'s blockout | 0.15 | 708 |
| `Furniture_Speaker` (1 x 1, `Floor`) | A plum cabinet between dark-wood corner posts on a plinth, a dark-wood pointed-arch roof the full depth with a gold spire; on the front a crimson cloth grille under a pointed arch with three black drivers in gold rims (0.66, 0.44, 0.22); on the back two bass ports | none | 5.18 | 1,048 |
| `Furniture_DiscoBall` (1 x 1, `Floor`) | A mirror ball 1.44 across of 30 x 16 white and silver facets, a gold cap, on an iron chain from the point of an iron pointed-arch frame (two 0.24 posts on long feet, the arch at 5.8 to 6.72, a gold spire to 7.0); the ball's bottom 4.68 | none | 7.0 | 1,234 |

Parts: `Root`, `Body` (not colliding), the floor's 16 `Glow_` tiles (not
colliding), and `LOD_Proxy` on the speaker and the ball (over 4 tall).
`import_fixup.luau` gives each `Use_<n>` its `Pose` attribute and lights the
tiles Neon: `Magenta` (255, 60, 200) and `Cold` (170, 210, 255).
**`Magenta` is a palette key MODELS.md rule 1 already names** (the Neon
facade's); the script adds it to the kit's keys exactly as
`tools/build_facades.py` does. The ball is in `Body`: nothing spins
(below).

## The Pieces rows

| id | w x d | layer | height | keyFor | spots |
|---|---|---|---|---|---|
| `LightFloor` | 2 x 2 | Rug | 0.15 (as main) | DanceFloor | `Use_1..4` Dance |
| `Speaker` | 1 x 1 | Floor | 5.0 (as main; the model's top 5.18, inside the 0.3) | — | none |
| `DiscoBall` | 1 x 1 | Floor | 7.0 (as main) | — | none |

Every w, d, layer and height is main's row: **no row needs to change.** The
kit's Pieces check ran against them (`validation.json` `pieces_rows`).

## Silhouettes (grey, three a piece)

`-- grey` builds them into `silhouettes/` (not in git, not for import):
`silhouettes/review/silhouettes_game.png` (the game's raised camera),
`silhouettes_top_floors.png`, `silhouettes_side_2.png` (speakers) and
`_3.png` (balls). Every option passed the same checks. They were drawn
before the blind reviews: the ball's size and height, the speaker's drivers
and back changed since.

- Floor **A** (chosen): octagon and dot. It reads as a tiled dance floor,
  is the Manor's Victorian hall floor, and runs to its edges, so floors laid
  side by side join into one pattern (MODELS.md: rugs meet edge to edge).
- Floor B: square tiles in a dark frame with gold corners. A finished
  single piece, but every join shows a double border.
- Floor C: a rose window laid in the floor. The most Manor, but its rings
  ignore the four squares the dancers stand on, and joined floors make a
  field of circles.
- Speaker **A** (chosen): a gothic cabinet under a pointed-arch roof. It
  reads as a speaker in the set's pointed-arch language.
- Speaker B: a bass box, a mid box, a gramophone horn on top. The horn reads
  as a camera.
- Speaker C: an upright coffin with drivers. It reads as a coffin, and the
  Manor already has one as a bed.
- Ball **B** (chosen): a pointed-arch frame, the ball hung from its point.
  Symmetric, the set's arch.
- Ball A: a gallows post with an arm. It reads as a lamp post (as the Gym's
  punching bag did).
- Ball C: a tripod cage of three bowed legs. The ball reads as caged.

## Validated (validation.json)

On the built and the re-imported triangles: the kit's furniture rules
(footprint 3w x 3d, the 0.4 inset for `Floor`, at most 7 tall, `Body` not
colliding, no coplanar faces, glow colours only in glow parts, budget 1,500,
the atlas, w, d, layer and height as Pieces.luau says), nothing floats, no
open edges; `spots_check` for every `Use_<n>` (from 1 without a gap, a Pose
from MODELS.md's list, level, no two on a square; `Dance`: inside the
footprint by the torso, flat to 0.15 under it, nothing of the piece within
the dancer's figure, 1.9 round and 5.2 tall). All three pass.

Added for the floor, `rug_check` (MODELS.md "Decor", Rug): the body reaches
all four footprint edges (-3..3 both ways), lies within 0..0.15, a ray every
0.25 finds it (no hole), its top steps 0.13 to 0.15, and every tile is a
`Glow_` part with its top at 0.15, where the dancers stand. The `Dance`
branch of the shared validator is the Bar's, unchanged; no other set was
rebuilt.

Four floors laid two by two (`review/8_four_floors.png`) join with the
dots whole across the seams and the chequer unbroken (4 tiles a side).

Not validated: anything in Studio (the attachments and Pose attributes exist
only in the manifest until `import_fixup.luau` runs), a visitor walking to
a spot and dancing (no walker or clip has run), the tiles lit in turn (the
code does not do it yet), and the ball spinning (nothing moves).

## Blind review 2026-10-26

Three runs, a fresh reviewer each on new pictures after each fix:
`review/blind/`, `blind2/`, `blind3/` (not in git).

Run 1:
1. The four dancers overlap at the arms; they hide the tiles from the game camera: **false by the contract** (one dancer a 3-stud square, the blockout's spots; the 3.8-wide figure's arms overlap 0.8 at 3 apart, as at the Bar's counter); **his call** (below).
2. The ball small, jammed into the apex with no chain, a beach ball's coarse checker; the stand reads as a gong stand; the ball beside the floor, not over it: **confirmed, fixed** (the ball 1.2 to 1.44 across, hung 0.3 lower on a visible chain, its facets 24 round); the stand's reading and the ball's place are **his call**.
3. The speaker reads as a grandfather clock; the cones small at game distance; a blank back: **confirmed in part, fixed** (larger drivers on a wider grille, the back finished); the case's shape is his call (look).
4. Black on black, hairline posts: **confirmed in part, fixed** (the case plum, lighter; the posts 0.2 to 0.24, the arch thicker).
5. The floor's colours read as a bathroom floor: **his call** (the palette, below); the tiles are Neon in the game, the preview shows no glow.
6. The stand in front of the speaker hides it; the feet stick out 1.5: the first is the preview's arrangement (**confirmed, the preview fixed**), the second **false** (the feet are inside the square, x and z within 1.0).
7. A dark seam between tiled floors: **false** (the base runs to the edge; four floors join, `8_four_floors.png`).

Run 2:
1. The dancers overlap: **his call** (run 1, 1).
2. The facets still coarse and blue-tinted, pinched at the top: **confirmed, fixed** (30 x 16 facets, white and silver); the pinch at the pole is a sphere's.
3. The ball at head height; a person walking through the arch meets it: **his call** (the decor cap of 7 and the 2.2-wide frame leave the ball's bottom at 4.68; its square is the piece's, but `Body` does not collide).
4. The speaker's back reads as a door with a knocker: **confirmed, fixed** (the arched panel and plate went; two bass ports low on the back).
5. Thin bars and finials invisible on a phone: **his call** (the Manor's iron, as at the Gym).
6. The halved gold dots along a lone floor's edge read as cut from a bigger rug: **his call** (the halves are what make joined floors seamless).
7. The speaker seven tall with an empty field over two drivers: **false** (5.18 tall, three drivers to 3.72, the arch's point over them).

Run 3 (the last round):
1. The dancers overlap: **his call** (the third time).
2. The ball nearly fills the arch, at head height, small from the game camera: **his call** (bigger reopens the fit, smaller reopens run 1's "a knob"; the 2.2 frame and the cap of 7 bound both).
3. The stand reads as a gong stand or a gallows: **his call** (the second reading as something else; option A read as a lamp post).
4. The floors will not tile, a dark rim and the checker's parity: **false** (the render it asked for, `8_four_floors.png`: no rim, the dots whole across the seams, the chequer alternating).
5. From the camera behind the player the speaker's top and back say wardrobe: **his call** (a grille on the back too, or the player turning speakers to face the room).
6. The unlit blue tiles merge with a grey floor: **his call** (the palette; they are Neon in the game).
7. The grille's pointed arch under a hood that reads round; the rims 16-sided: the rims are **false** (16 sides, within the budget); the arches' mismatch is **his call** (look).
8. The preview's stand in front of a speaker: **confirmed, fixed after run 3** (the ball moved off the floor's front corner in `1_game_camera.png`; not re-reviewed).

## His calls (for WAITING.md; this session did not edit it)

- **Dancers' spacing.** One dancer a 3-stud square puts them 3 apart; the
  5-stud figure is 3.8 across, so side by side their arms overlap 0.8, and
  three reviewers saw it. I recommend keeping the spots (the blockout's, one
  a square) and letting the dance clip keep the arms in, or turning the four
  to face the floor's middle so neighbours stand shoulder to back.
- **The tiles' colours**: magenta and moon-blue (Neon). I recommend them; the
  alternative is the Manor's own keys (`Cold` with `Warm` or `Magic`).
- **The disco ball's place.** A 1 x 1 `Floor` piece keeps its ball inside its
  own square and under 7, so it hangs beside the floor at 4.7 to 6.2, never
  over the dancers. I recommend a ceiling-hung ball over the floor's middle
  one day (a new layer in MODELS.md first); until then this stand.
- **The ball's stand** (a pointed arch; read as a gong stand or gallows) and
  its size in it. I recommend keeping it.
- **Spinning.** The ball is `Body`. If the code is to spin it, MODELS.md first
  needs a name for it (e.g. `Ball`); then the script splits it out.
- **Looks**: the speaker's case (read as a grandfather clock or wardrobe from
  behind; recommend keeping it, perhaps a grille on the back), the halved dots
  on a lone floor's edge (recommend keeping them), the dark iron from the game
  camera (recommend the Manor's iron, as at the Gym).
