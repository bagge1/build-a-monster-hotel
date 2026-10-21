# The Lantern Grove: Bayou Spa's rare decor set

GDD A.11.3 (one set of five per location at launch, found, not bought). To
`MODELS.md`, "Rare decor sets and souvenirs". Built by
`tools/build_rare_decor.py -- sets lantern_grove`; a draft (2026-10-21) for
August's look (Bayou Spa itself is a draft, WAITING §2.36). **Nothing here
has been seen in Studio.** The name "Lantern Grove", the set id
`LanternGrove` and every piece are working picks, his to rename or replace.

## The set (5 pieces, location 3)

One look: the Spa's palette (`BS_PALETTE`): cypress, brass, a plum dusk,
teal water, lily greens and lotus pinks, lantern and firefly light. **The
set's crest is a dragonfly seen from above** (four pale moonstone wings, a
brass head, thorax and long tail), the bayou's own creature, **on every
piece** through `emblem()`. There are glows on three pieces.

| Model | Squares, layer | What | Glows | Top | Triangles |
|---|---|---|---|---|---|
| `Decor_LanternGrove_StainedGlass` | 2 x 1, Wall | A round stained-glass window at eye level (2.6 to 6.5, centre 4.55): the crest large over a dusk bayou (plum sky, the moon, teal water, two lily pads, a lotus, two fireflies) in a moulded round frame (dark cypress, cypress, brass: three stepped rings), Spanish moss draped over its top; a firefly jar hung from a brass bracket either side | `Glow_Cold_1` (the moon), `Glow_Warm_1`, `_2` (fireflies), `_3`, `_4` (jars) | 6.55 | 1,416 |
| `Decor_LanternGrove_Lamp` | 1 x 1, Floor | A dragonfly floor lamp: a lily-pad foot, a brass reed stem with two leaves, an eight-sided shade of warm glass with the crest on four of its panels (heads up the slope: from above four dragonflies round a lotus bud), a brass rim and cap | `Glow_Warm_1` (the whole shade) | 5.82 | 1,128 |
| `Decor_LanternGrove_Gramophone` | 1 x 1, Floor | A cypress gramophone on brass ball feet: a plum-velvet front in a dark frame with the crest, a brass band under the lid, a brass turntable with a record and tonearm, a flower horn (brass outside, lotus pink inside) with a brass dragonfly perched on its rim | — | 4.85 | 1,348 |
| `Decor_LanternGrove_Pirogue` | 2 x 1, Floor | A cypress pirogue (the bayou's flat-bottomed canoe) as a planter: moss to its light gunwales, a lotus, two lily pads, cattails with a firefly; a firefly jar hung from a crooked pole over the bow; the crest on both sides and on the bow's deck | `Glow_Warm_1` (the jar), `_2` (the firefly) | 3.59 | 1,436 |
| `Decor_LanternGrove_Rug` | 3 x 2, Rug | Teal water in a rattan band and a dark cypress edge, a great lily pad (its notch to the front right) with the crest large (2.0 long, its head away from the door) inside a pale ripple, a lotus in each corner | — | 0.12 | 832 |

Richer than the Spa's shop decor by intent: brass trim on every piece, the
crest repeating, glows on three. From the raised build camera
(`review/raised.png`) every piece reads by silhouette and colour; straight
down at a phone's size (`review/topdown_phone.png`) the rug and its
dragonfly, the lamp's glowing octagon with its four dragonflies, the
gramophone's pink horn mouth and the pirogue's boat shape read; the window,
on the wall, is a line.

**The `Pieces` rows the code session must add** (none exist; src/ was not
touched): each `id` `LanternGrove_<Piece>`, `set = "LanternGrove"`,
`found = true`, `location = 3`, and `w`, `d`, `layer`, `height` as the
table; `manifest.json` has each piece's `pieces_row`, with a `colour` for
the swatch. Prices, points, tags, display names and the set bonus are his
(A.11.3 Numbers). A `Pieces.Sets` entry `LanternGrove` lists the five.

## Validated (by the build, `validation.json`)

`VALIDATED 5/5`, each FBX re-imported. The same checks as the Aurora
Lodge's (`../aurora_lodge/README.md`): footprint and inset, layer, the
window's back on z = 1.1, nothing colliding, glows in their parts, no
coplanar faces, budgets (all under 1,500), nothing floating (the window
hangs), no `Use` or seat, part names, boxes, one material, the atlas.

The Count's Study's blind-review checklist, held by construction: one crest
outline on every piece, read from above; the wall piece at eye level; a
moulded frame (three stepped rings); no dark box from above (the
gramophone's dark lid is under the horn and the turntable).

## Not done

- **A blind review** (skill `blind-review`): not run. Claude's own look after
  the first sheets made the pirogue's side crests larger (0.3 to 0.34: they
  read as smudges).
- Anything in Studio: the import, `import_fixup.luau`, how the glows look
  (the lamp's whole shade is a `Warm` glow: Neon in Studio).
- His look: the set, its theme, each piece and the crest are proposals.
- The `Pieces` rows and any code.

## Review (Workbench on light grey only: Studio was running)

`review/set_sheet.png`, `review/elevations_sheet.png`, `review/topdown.png`,
`review/topdown_phone.png`, `review/raised.png`, as the Aurora Lodge's. Not
in git; rebuilt by the script.

## Staged

`blender/_import/`: `Decor_LanternGrove_StainedGlass`, `_Lamp`,
`_Gramophone`, `_Pirogue`, `_Rug` (`.fbx`), beside the earlier batch. They
go to `assets/HotelKit/BayouSpa/`, which does not exist yet: nor does its
mapping in `default.project.json` (only `HauntedManor` and `FrostfangLodge`
are mapped), so saving them needs that mapping and a Rojo restart (his).
