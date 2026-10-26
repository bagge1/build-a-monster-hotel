# Haunted Manor: the Karaoke Lounge's stage and microphone (GDD A.13)

The Karaoke Lounge type's pieces (GDD A.13.2, the Karaoke Lounge row; A.13.3,
the Stage set's microphone) in Haunted Manor's dress, to `MODELS.md`
"Decor", "Furniture" and "Activity furniture: visitors' spots". Built by
`tools/build_activity_karaoke.py`, which runs `tools/build_activity_bar.py`'s
definitions (and through it `tools/build_built_rooms.py`'s kit) without their
mains; a draft for August's look, 2026-10-26. **Nothing here has been seen in
Studio, and nothing is staged for import.** The models belong in
`HotelKit.HauntedManor`; they have their own set folder so no other set's
manifest is rewritten.

Kept apart from the Bar's `SmallStage` (a round apron deck at 1.0, curtains
drawn aside, a crescent, one performer `Dance`) but of its family: dark wood,
gold, the pointed arch, a microphone stand. Here a square deck on a plum
skirt, the lyrics screen where the SmallStage has its curtains, marquee
bulbs, two singers.

## What is in it

| Model | What | Spots | Top | Triangles |
|---|---|---|---|---|
| `Furniture_KaraokeStage` (2 x 2, `Floor`) | A wood deck at **0.8** on a plum skirt, its front corners cut; at its back a dark-wood pointed-arch frame (two posts, the arch to 6.95) lined with 15 warm marquee bulbs (`Glow_Warm_1`); in its arch the lyrics screen (`Glow_Cold_1`, y 3.6 to 6.4, pointed) on a night-blue panel, three lyric lines 0.02 proud (the sung part of the middle one crimson, from the room's left); a gold sill over a plum speaker cabinet with two gold-rimmed drivers; the back a crimson cloth grille under a gold rail; two vintage microphone stands at z -1.85, the capsules at the singers' mouths | `Use_1`, `Use_2` `Stand` on the deck at (-1.3, 0.8, -0.7) and (1.3, 0.8, -0.7), looking -Z (the room): one a square | 6.95 | 1,428 |
| `Furniture_Microphone` (1 x 1, `Floor`) | The same vintage stand: a domed iron foot 1.2 across, an iron pole 0.22, a gold collar and yoke holding a silver pill-shaped capsule with a gold band, its top at 4.96; at z -0.5 in its square, so a guest behind it stands in the square | none | 4.96 | 256 |

Parts: `Root`, `Body` (not colliding), the stage's `Glow_Cold_1` (the screen)
and `Glow_Warm_1` (the bulbs), `LOD_Proxy` on both (over 4 tall).
`import_fixup.luau` gives each `Use_<n>` its `Pose` attribute and lights the
glows Neon. The screen is one part the code can light; nothing changes what
it shows.

## The Pieces rows

| id | w x d | layer | height | keyFor | spots |
|---|---|---|---|---|---|
| `KaraokeStage` | 2 x 2 | Floor | 7.0 (as main; the model's top 6.95) | KaraokeLounge | `Use_1`, `Use_2` Stand |
| `Microphone` | 1 x 1 | Floor | 5.0 (as main; the model's top 4.96) | — | none |

Every w, d, layer and height is main's row: **no row needs to change.** The
kit's Pieces check ran against them (`validation.json` `pieces_rows`).

## Silhouettes (grey, three a piece)

`-- grey` builds them into `silhouettes/` (not in git, not for import):
`silhouettes/review/silhouettes_game.png` (the game's raised camera),
`silhouettes_front_1.png` (stages), `_2.png` (microphones). Every option
passed the same checks. They were drawn before the blind reviews (the
singers, the screen's height, the step and the stand's thickness changed
since; a rebuild of B and C now places them with the new spots).

- Stage **A** (chosen): the lyrics window, a screen in a pointed-arch frame
  behind the singers. The screen faces the room and the game's camera sees
  it over the singers' heads; it reads as karaoke at once, and the arch and
  marquee are the Manor's.
- Stage B: the prompter, a wedge monitor at the front sloped up at the
  singers, two speaker towers behind. The truer karaoke layout, but the
  screen faces away from the camera and the wedge reads as a box.
- Stage C: the magic mirror, an oval standing mirror with the lyrics in its
  glass. The most Manor, but it reads as a dressing mirror first.
- Microphone **A** (chosen): a vintage stand, the pill capsule in a yoke. The
  microphone everyone knows as "the singer's mic"; the same stand is on the
  stage.
- Microphone B: a tripod boom stand. Reads as studio equipment, and its boom
  reaches back into the singer.
- Microphone C: a gothic candlestick stand with a ball microphone in a
  crescent. Reads as a candlestick or lamp.

## Validated (validation.json)

On the built and the re-imported triangles: the kit's furniture rules
(footprint 3w x 3d, the 0.4 inset, at most 7 tall, `Body` not colliding, no
coplanar faces, glow colours only in glow parts, budget 1,500, the atlas, w,
d, layer and height as Pieces.luau says), nothing floats, no open edges;
`spots_check` for every `Use_<n>`: from 1 without a gap, a Pose from
MODELS.md's list, level, no two on a square; a `Stand` inside the footprint
goes to `stand_on_faults` (the Gym's rule): the deck flat to 0.15 under both
feet, and the standing 5-stud person (legs, torso, arms out to 3.8 across,
head, each block shrunk 0.03) clear of the body (the microphone's foot 0.1
in front of the legs, the capsule 0.3 in front of the face, the frame
behind). Both pass. Nothing was added to the shared validator; no other set
was rebuilt.

Not validated: anything in Studio (the attachments and Pose attributes exist
only in the manifest until `import_fixup.luau` runs), a visitor getting onto
the 0.8 deck and singing (no walker or clip has run), the glows lit (the
previews are Workbench, unlit), and the two singers against each other (each
is checked against the piece, not the other).

## Blind review 2026-10-26

Three runs, a fresh reviewer each on new pictures after each fix:
`review/blind/`, `blind2/`, `blind3/` (not in git).

Run 1:
1. The singers' heads hide the screen's lower lines: **confirmed, fixed** (from the game camera the heads covered the screen to about 3.3; the singers moved forward 0.4 and the screen raised 0.6, to 3.6..6.4: the heads now project to 2.8 on it).
2. The singers' arms overlap: **his call** (below).
3. The arms hang over the deck's edge and meet the frame's post: the overhang is **his call** (with 2); the post is **false** (`stand_on_faults` holds the figure, arms included, clear of the body; the posts stand at z 1.9 and more, the arms at -1.15..-0.25).
4. The front step off-centre: **false** (x -2.0..2.0, centred; the three-quarter view's perspective); made as wide as the deck's front edge anyway, then removed in run 2.
5. The standalone stand has no presence: **confirmed, fixed** (the foot, pole and capsule heavier).
6. Unlit, the screen reads as a headstone or a mirror: **his call** (it is Neon in the game; the previews cannot light it).
7. Two gold rings on the back read as eyes: **confirmed, fixed** (a cloth grille, then in run 2 a speaker's back).
8. A light patch at the screen's bottom between the heads: **false** (the screen itself between the heads).
9. The bulbs read as rivets: **his call** (Neon warm in the game; made 0.13 round).

Run 2:
1. The stands' feet clip the singers' feet: **confirmed in part, fixed** (0.03 clear by the check, read as touching: the stage's microphones 0.15 forward, 0.1 clear; the preview's guest at the standalone stand 0.15 clear).
2. The microphones stand over the one step, the way up: **confirmed, fixed** (the step went; the deck runs to the footprint's front as the SmallStage's does; how a guest gets onto a 0.8 deck is the code's, his call below).
3. The screen low from a lower camera: **his call** (from the game camera the whole screen clears the heads; under the cap of 7 a level view always sees heads over its lower part).
4. The back bare, a tombstone: **confirmed, fixed** (a crimson cloth grille on the cabinet's back under a gold rail).
5. Unlit, not karaoke: **his call** (run 1, 6).
6. The standalone guest stands half in the next square: **confirmed, fixed** (the stand forward to z -0.5 in its square; the guest behind it stands in the square).
7. The pole too slight: **confirmed, fixed** (0.22 across, the foot 1.2).
8. The drivers hidden behind the singers: **false** (seen whenever nobody sings).
9. The arms out over the edge: **his call** (run 1, 2).

Run 3 (the last round):
1. The singers' arms overlap: **his call** (the third time).
2. Each singer stands in their stand: **false** (`stand_on_faults`: the foot 0.1 clear of the legs, the pole 1.15 ahead of the body's middle; the raised camera's projection).
3. The stands block the way onto the stage: **false for collision** (`Body` does not collide); where guests step up is his call.
4. The heads hide the lower lines from the game camera: **false by geometry** (the heads' tops project to y 2.8 on the screen's plane from the game camera; the lines are at 4.3 to 5.6).
5. The bulbs uneven, none low on the posts: **confirmed, fixed after run 3** (three a post, 1.3 apart, from 1.6; not re-reviewed).
6. A striped pale patch at the screen's bottom left: **false** (the coplanar check passed; it is the screen between the heads).
7. The cabinet deeper than the frame, two boxes stacked: **his call** (look; the gold sill is the step).
8. The pole thin for phones: **his call** (doubled since run 1; thicker reads as a post).
9. Unlit, a mirror or jukebox top: **his call** (the third time; Neon in the game).
10. The speaker rings hidden by the singers: **false** (run 2, 8).

## His calls (for WAITING.md; this session did not edit it)

- **Singers' spacing.** One singer a 3-stud square puts them 2.6 apart; the
  5-stud figure is 3.8 across, so arms out they overlap 1.2 and the outer
  arms reach 0.6 past the deck. Three reviewers saw it (as at the Dance
  Floor). I recommend keeping the spots and a singing clip that holds the
  microphone (arms in); the alternative is one singer, centred.
- **Getting onto the stage.** The deck is 0.8 up with no step (as the
  SmallStage's 1.0). I recommend the code placing the singer on its spot (a
  short hop), as for the SmallStage's performer; a step needs a 2 x 3 stage.
- **The screen unlit and the lyrics' look.** A pale moon-blue screen
  (`Cold`, Neon in the game) with dark lines and a crimson wipe, warm marquee
  bulbs. I recommend them; the alternative is a dark screen with glowing
  lines (a second glow part).
- **Looks**: the cabinet under the screen deeper than the frame, the
  microphone pole's thickness (0.22), the screen's height (bounded by the
  cap of 7).
