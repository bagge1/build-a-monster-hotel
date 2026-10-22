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
| `Decor_LanternGrove_StainedGlass` | 2 x 1, Wall | A round stained-glass window at eye level (2.6 to 6.5, centre 4.55): the crest large over a dusk bayou (plum sky, the moon, teal water, two lily pads, a lotus, two fireflies) in a moulded round frame (dark cypress, cypress, brass: three stepped rings), a moss trim lying along the frame's top (15 to 165 degrees, tufts on the frame, clear of the glass); a firefly jar hung from a brass bracket either side, its light showing round its cap from above | `Glow_Cold_1` (the moon), `Glow_Warm_1`, `_2` (fireflies), `_3`, `_4` (jars) | 6.52 | 1,424 |
| `Decor_LanternGrove_Lamp` | 1 x 1, Floor | A dragonfly floor lamp: a lily-pad foot, a brass reed stem with two leaves, an eight-sided shade of warm glass, a brass rim; one crest, large (1.0 across), lying on a plum lid in a raised brass rim on the shade's top: from above a pale dragonfly on dusk in a ring of lamplight | `Glow_Warm_1` (the whole shade) | 5.3 | 572 |
| `Decor_LanternGrove_Gramophone` | 1 x 1, Floor | A cypress gramophone on brass ball feet: a plum-velvet front in a dark frame with the crest, a brass band under the lid, a brass turntable with a record and tonearm, a flower horn (brass outside, pale pink at the mouth deepening to a velvet throat) with the crest (0.72 across, outlined in dark cypress) perched on its rim | — | 4.86 | 1,496 |
| `Decor_LanternGrove_Pirogue` | 2 x 1, Floor | A cypress pirogue (the bayou's flat-bottomed canoe) as a planter, resting 0.3 up on a cradle of two dark cypress stands: light moss to its gunwales, a lotus, two dark lily pads (the crest, 0.84 across, lying on the larger), cattails with a firefly; a firefly jar hung from a crooked pole well inside the bow, its light showing round its cap from above; the crest on both sides | `Glow_Warm_1` (the jar), `_2` (the firefly) | 3.54 | 1,488 |
| `Decor_LanternGrove_Rug` | 3 x 2, Rug | Teal water in a rattan band and a dark cypress edge, a great lily pad (its notch to the front right, starting 0.95 out from the middle, clear of the crest) with the crest large (2.0 long, its head away from the door, outlined in dark cypress) inside a pale ripple, a lotus in each corner | — | 0.12 | 980 |

Richer than the Spa's shop decor by intent: brass trim on every piece, the
crest repeating, glows on three. From the raised build camera
(`review/raised.png`) every piece reads by silhouette and colour; straight
down at a phone's size (`review/topdown_phone.png`) the rug and its outlined
dragonfly, the lamp's plum lid and crest in its ring of light, the
gramophone's pink horn mouth round a dark throat with the outlined crest on
its rim, and the pirogue's light moss, dark pads, crest, lotus and lit jar
read; the window, on the wall, is a line. The outline (`DRAGONFLY_LIT`, a dark
cypress silhouette 0.07 wider) is used where the crest lies on a ground of its
own colours (the rug's pad, the horn's brass rim).

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

- **The blind review** (2026-10-21, context-free, both location sets):
  confirmed and fixed in `tools/build_rare_decor.py` the same day:
  1. From above on a phone the set vanished in its low-contrast palette: the
     crest outlined on the rug and the horn, one large crest on the lamp's
     plum lid in its ring of light, the horn's throat deepened to velvet, the
     pirogue's moss lighter and its pads dark with the crest on one, the
     jars' caps narrower so their light shows from above (`grove_jar`).
  2. The pirogue's hull ended in a V on the floor with no stand: it rests on
     a cradle of two stands.
  3. The window's moss was a lumpy blob over the frame: a trim along the
     frame's top.
  4. The rug's lily-pad notch ran into the dragonfly's tail: the notch starts
     0.95 out and points away from it.
  5. The lamp shade carried four small dragonflies: one crest, larger.
  6. The pirogue's jar arm reached past the hull's end: pole and jar stand
     well inside the bow.
  Not changed, his call: the lamp and the gramophone looking ordinary
  beyond the fixes above. Before the review, Claude's own look had made the
  pirogue's side crests larger (0.3 to 0.34: they read as smudges).
- Triangles near the 1,500 budget (gramophone 1,496, pirogue 1,488, window
  1,424): the pirogue's gunwales have 9 sections and its pole 5 sides to pay
  for the cradle.
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

## Imported

All five imported 2026-10-23, fixed up by `import_fixup.luau` (Box, read back) and saved as `assets/HotelKit/BayouSpa/Decor_LanternGrove_<Piece>.rbxm` (the kit's folder and mapping exist now); the synced templates match the import. Not yet seen in a playtest.
