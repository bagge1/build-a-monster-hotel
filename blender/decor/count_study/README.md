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
| `Decor_CountStudy_Portrait` | 2 x 1, Wall | The Count at eye level (frame 2.5 to 6.58, centre 4.54) in a moulded gilt pointed-arch frame (three stepped rings: amber, honey, gold) with a crimson slip: black cape, high crimson collar, widow's peak, a moon behind; the crest standing on the apex; two candle sconces | `Glow_Eyes_1`, `_2` (his eyes), `Glow_Warm_1`, `_2` | 6.94 | 1,452 |
| `Decor_CountStudy_Globe` | 1 x 1, Floor | A night globe (gold continents on a night-blue sea) on a tilted axis in a gold meridian, a dark wood horizon ring on four struts, a turned stand; the crest standing on the meridian's top, leaned back 30 degrees | — | 4.32 | 1,480 |
| `Decor_CountStudy_Clock` | 1 x 1, Floor | A longcase clock shaped as a coffin standing up, on gold ball feet: crimson inlay, pendulum behind a pointed window, moonlit dial at five to midnight; a black cornice with a gold band under a crimson coffin-lid gable with a gold ridge; the crest standing on the ridge, leaned back 30 degrees | `Glow_Cold_1` (the dial) | 6.78 | 944 |
| `Decor_CountStudy_Bust` | 1 x 1, Floor | The Count's bust, head and shoulders in white marble (shoulders 1.8 wide, head 0.72 by 0.9), black hair, pointed ears, a high crimson-lined collar framing the head; on a gold socle, a crimson column (capital 2.16) with gold bands; the crest on a black plaque | `Glow_Eyes_1`, `_2` | 4.17 | 1,214 |
| `Decor_CountStudy_Rug` | 3 x 2, Rug | Crimson in a black and gold border, a gold medallion with the crest large (2.7 across, its head away from the door), gold corners and diamonds | — | 0.145 | 492 |

Richer than the shop's decor by intent: more gold, a figure (the Count) on
two pieces, glows, and the crest repeating. From above (`review/raised.png`,
`topdown.png`) the rug carries the set; the others read by silhouette and
colour at the build camera's raised angle. Straight down at a phone's size
(`topdown_phone.png`, 360 px for a 24-stud room) the rug and its bat, the
globe, the clock's crimson top and the souvenirs' rosettes read; the bust is
a white spot in its collar.

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
- A second blind review of the fixes (below).
- His look: the set, its theme, each piece and the crest are proposals.
- The `Pieces` rows and any code (the Found tab, rolls, the set bonus).

## Blind review 2026-10-21, and what changed

A context-free reviewer saw the first sheets; the set's findings, all
confirmed and fixed in `tools/build_rare_decor.py`:

1. **The crest was not one mark** (a toothy jaw on the rug, a gem with
   wings on the portrait, small wings elsewhere). Now one outline, `BAT_R`
   (head between two tall ears, wings sweeping up to points, three rounded
   membrane scallops, a round foot), gold, on every piece through `crest()`:
   2.7 across on the rug, 1.24 on the clock, 1.1 on the portrait, 0.9 on the
   globe, 0.64 on the bust's plaque. The crimson roundel behind it is gone.
2. **The bust read as a bird on a post** (a 1-stud head on a 3.5 pedestal,
   the collar bigger than the head, a raven). Column now to 2.16, marble
   shoulders 1.8 wide under a 0.72-wide head (0.4 of the shoulders), the
   collar two crimson-lined wings behind the head reaching 0.25 past it and
   to its middle; the raven removed.
3. **Clock and bust were dark boxes from above.** The clock's top is a
   crimson gable with a gold ridge and the crest; the bust shows white
   head and shoulders in a crimson collar.
4. **The portrait hung too low** (frame from 1.4). Now 2.5 to 6.58, 0.8 of
   its size (the crest keeps under the 7-stud top), sconces raised with it.
5. **The frame was a flat band.** Three stepped rings, fronts at 0.82, 0.70
   and 0.77 from the wall's 1.1, in three golds.

Not changed (his call): the globe's plainness, the palette, the flat-colour
style.

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
`_Bust`, `_Rug` (`.fbx`), re-staged after the blind review's fixes
(replacing the first draft's), beside the earlier batch. They
go to `assets/HotelKit/HauntedManor/`.

## Imported

All five imported 2026-10-23, fixed up by `import_fixup.luau` (Box, read back) and saved as `assets/HotelKit/HauntedManor/Decor_CountStudy_<Piece>.rbxm`; the synced templates match the import. Not yet seen in a playtest.
