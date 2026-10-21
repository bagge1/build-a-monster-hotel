# The Count's Study: Haunted Manor's rare decor set

GDD A.11.3 (one set of five per location at launch, found, not bought; the
art first, A.11.7 step 0). To `MODELS.md`, "Rare decor sets and souvenirs".
Built by `tools/build_rare_decor.py` (which also builds `../souvenir/`); a
draft (2026-10-21) for August's look. **Nothing here has been seen in
Studio.** The name "Count's Study" and every piece are working picks (the
GDD's example set, minus the candelabra and organ the shop already has):
his to rename or replace.

## The set (5 pieces, location 1)

One look: crimson, black and gold, the Manor's night blue and bone; **the
set's crest, a gold bat with spread wings, on every piece**; glows on three.

| Model | Squares, layer | What | Glows | Top | Triangles |
|---|---|---|---|---|---|
| `Decor_CountStudy_Portrait` | 2 x 1, Wall | The Count in a gold pointed-arch frame with a crimson slip: black cape, high crimson collar, widow's peak, a moon behind; the crest on a crimson roundel on the apex; two candle sconces | `Glow_Eyes_1`, `_2` (his eyes), `Glow_Warm_1`, `_2` | 6.92 | 1,152 |
| `Decor_CountStudy_Globe` | 1 x 1, Floor | A night globe (gold continents on a night-blue sea) on a tilted axis in a gold meridian, a dark wood horizon ring on four struts, a turned stand; the crest on the meridian's top | — | 4.13 | 1,400 |
| `Decor_CountStudy_Clock` | 1 x 1, Floor | A longcase clock shaped as a coffin standing up, on gold ball feet: crimson inlay, pendulum behind a pointed window, moonlit dial at five to midnight; the crest on the crown | `Glow_Cold_1` (the dial) | 6.73 | 824 |
| `Decor_CountStudy_Bust` | 1 x 1, Floor | The Count's marble bust (black hair and cape, pointed ears) on a gold socle, a crimson column with gold bands; the crest on a black plaque; a raven on the capital | `Glow_Eyes_1`, `_2` | 4.89 | 1,132 |
| `Decor_CountStudy_Rug` | 3 x 2, Rug | Crimson in a black and gold border, a gold medallion with the crest large (its head away from the door), gold corners and diamonds | — | 0.145 | 412 |

Richer than the shop's decor by intent: more gold, a figure (the Count) on
two pieces, glows, and the crest repeating. From above (`review/raised.png`,
`topdown.png`) the rug carries the set; the others read by silhouette and
colour at the build camera's raised angle. Straight down at a phone's size
(`topdown_phone.png`, 360 px for a 24-stud room) the 1 x 1 pieces are dots
with colour; the rug and the globe still read.

**The `Pieces` rows the code session must add** (none exist; src/ was not
touched): each `id` `CountStudy_<Piece>`, `set = "CountStudy"`,
`found = true`, `location = 1`, and `w`, `d`, `layer`, `height` as the table
(`manifest.json`, `pieces_row` per piece). Prices, points, tags and the set
bonus are his (A.11.3 Numbers).

## Validated (by the build, `validation.json`)

- The kit's decor checks on the built and the re-imported triangles:
  footprint and the 0.4 inset (a rug to its edge, at most 0.15 tall), layer,
  w/d/layer against the rows above (height not: no row yet), the Wall
  piece's back on z = 1.1, nothing colliding, glow colours only in their
  `Glow_<Key>_<n>` parts, no coplanar faces, budgets (1,500).
- Nothing floats (`grounded_check`; the portrait hangs: `hung_check`).
- No `Use` and no seat (decor, not furniture).
- Each FBX re-imported: part names, boxes to 0.02, triangle counts, one
  material, the atlas embedded. The palette is the Manor's plus `eyes`
  (the `Eyes` glow key's colour, which the fix-up makes Neon).

## Not done

- Anything in Studio: the import, `import_fixup.luau`, how the glows look.
- A blind review (skill `blind-review`) of the sheets.
- His look: the set, its theme, each piece and the crest are proposals.
- The `Pieces` rows and any code (the Found tab, rolls, the set bonus).

## Review (Workbench on light grey only: Studio was running)

`review/set_sheet.png` (each piece on its squares beside the 5-stud person,
from the front three-quarters and from above), `review/elevations_sheet.png`
(front and side at floor level; the souvenir's last), `review/topdown.png`
and `review/topdown_phone.png` (the set and four souvenirs in a 2 x 2 cell
study, straight down), `review/raised.png` (the same from the raised build
camera). The souvenirs there are `Souvenir_Base` tinted as four species,
their cloches hidden (the code makes them glass).

## Staged

`blender/_import/`: `Decor_CountStudy_Portrait`, `_Globe`, `_Clock`,
`_Bust`, `_Rug` (`.fbx`), beside the earlier batch (nothing removed). They
go to `assets/HotelKit/HauntedManor/`.
