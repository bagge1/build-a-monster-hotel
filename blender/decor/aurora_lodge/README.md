# The Aurora Lodge: Frostfang Lodge's rare decor set

GDD A.11.3 (one set of five per location at launch, found, not bought). To
`MODELS.md`, "Rare decor sets and souvenirs". Built by
`tools/build_rare_decor.py -- sets aurora_lodge`; a draft (2026-10-21) for
August's look. **Nothing here has been seen in Studio.** The name "Aurora
Lodge", the set id `AuroraLodge` and every piece are working picks, his to
rename or replace.

## The set (5 pieces, location 2)

One look: the Lodge's navy, snow, ice and gold, the aurora's mint and violet,
red for the sleigh. **The set's crest is the Frostfang, a wolf's head seen
from the front** (tall pointed ears, three ruff spikes a cheek, a long
muzzle), gold with a snow mask and inner ears and dark eyes and nose, **on
every piece** through `emblem()`. There are glows on two pieces: the
aurora in the painting, and lanterns.

| Model | Squares, layer | What | Glows | Top | Triangles |
|---|---|---|---|---|---|
| `Decor_AuroraLodge_Painting` | 2 x 1, Wall | The aurora over the Frostfang peaks, the Lodge's lit window under the pines, in a moulded round-topped frame (log, log, gold: three stepped rings) at eye level (frame 2.4 to 6.1); the crest standing on the crown (its ears at 6.97); an iron lantern on a bracket either side | `Glow_Magic_1`, `_2` (the aurora), `Glow_Warm_1` (the window), `_2`, `_3` (lanterns) | 6.97 | 1,420 |
| `Decor_AuroraLodge_WolfStatue` | 1 x 1, Floor | The Frostfang carved in ice, sitting and howling (snow chest ruff, a gold collar, the muzzle raised, ears laid back, the tail round its feet), on an octagonal stone plinth with two gold bands and a light cap; the crest on the plinth's front | — | 4.53 | 1,220 |
| `Decor_AuroraLodge_Telescope` | 1 x 1, Floor | A brass telescope aimed up at the aurora (navy tube, gold bands, cradle and dew cap, an ice lens, a finder) on a light wood tripod with gold spreaders and feet, on a round base: a gold rim and a navy star chart with the crest lying in front of the tripod, clear of the tube from above | — | 4.85 | 1,020 |
| `Decor_AuroraLodge_Sleigh` | 2 x 1, Floor | A red sleigh, a gold edge round both side panels, a swan-curl dash and a high curled back, on gold runners curling up in front; a navy blanket with the crest lying on it, the crest on both sides, a white fur cushion; a lantern hung over the dash on an iron crook | `Glow_Warm_1` | 3.65 | 1,404 |
| `Decor_AuroraLodge_Rug` | 3 x 2, Rug | Snow with a red stripe round a navy field, an ice medallion with the crest large (2.7 across, its head away from the door), the aurora waving across both ends (mint, violet), gold stars in the corners | — | 0.14 | 856 |

Richer than the Lodge's shop decor by intent: gold trim on every piece, a
figure (the wolf) and a scene (the painting), glows, and the crest repeating.
From the raised build camera (`review/raised.png`) every piece reads by
silhouette and colour; straight down at a phone's size
(`review/topdown_phone.png`, 360 px for a 24-stud room) the rug and its wolf,
the sleigh (red, gold edges, the crest on the navy blanket), the telescope's
navy disc with the crest and the pale wolf on its octagon read; the painting,
on the wall, is a line.

**The `Pieces` rows the code session must add** (none exist; src/ was not
touched): each `id` `AuroraLodge_<Piece>`, `set = "AuroraLodge"`,
`found = true`, `location = 2`, and `w`, `d`, `layer`, `height` as the
table; `manifest.json` has each piece's `pieces_row`, with a `colour` for
the swatch (the piece's main colour). Prices, points, tags, display names
and the set bonus are his (A.11.3 Numbers). A `Pieces.Sets` entry
`AuroraLodge` lists the five.

## Validated (by the build, `validation.json`)

`VALIDATED 5/5`, each FBX re-imported:

- The kit's decor checks on the built and the re-imported triangles:
  footprint and the 0.4 inset (the rug to its edge, at most 0.15 tall),
  layer, w/d/layer against the rows above (height not: no row yet), the
  painting's back on z = 1.1, nothing colliding, glow colours only in their
  `Glow_<Key>_<n>` parts, no coplanar faces, budgets (all under 1,500).
- Nothing floats (`grounded_check`; the painting hangs: `hung_check`).
- No `Use` and no seat (decor, not furniture).
- Part names, boxes to 0.02, triangle counts, one material, the atlas
  embedded. The palette is the Lodge's own (`build_hotel_frostfang_lodge.py`).

The checklist from the Count's Study's two blind reviews, held here by
construction: one crest outline on every piece, read from above; the wall
piece at eye level; a moulded frame (three stepped rings, fronts 0.80,
0.68, 0.76); no dark box from above (the plinth's cap is light, the
telescope's chart carries the crest).

## Not done

- **A blind review** (skill `blind-review`): not run. The fixes after the
  first sheets were Claude's own look: the sleigh read gold and grey from
  above (a gold core under a grey blanket), so its gold is now an edge on the
  side panels and the blanket navy with the crest; the wolf's ears were long
  enough to read as a hare's from the front, so they are shorter.
- Anything in Studio: the import, `import_fixup.luau`, how the glows look.
- His look: the set, its theme, each piece and the crest are proposals.
- The `Pieces` rows and any code.

## Review (Workbench on light grey only: Studio was running)

`review/set_sheet.png` (each piece on its squares beside the 5-stud person,
from the front three-quarters and from above), `review/elevations_sheet.png`
(front and side at floor level), `review/topdown.png` and
`review/topdown_phone.png` (the set in a 2 x 2 cell room, straight down),
`review/raised.png` (the same from the raised build camera). Not in git;
rebuilt by the script.

## Staged

`blender/_import/`: `Decor_AuroraLodge_Painting`, `_WolfStatue`,
`_Telescope`, `_Sleigh`, `_Rug` (`.fbx`), beside the earlier batch. They go
to `assets/HotelKit/FrostfangLodge/`.
