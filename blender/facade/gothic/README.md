# `Cosmetic_GothicFacade` (pass FacadeGothic)

The look (a draft he said yes to, GDD decision log 2026-10-20): dark slate, pointed windows, red stained-glass trim, small gargoyles on the corners.
Built by `tools/build_facades.py -- styles gothic` to `MODELS.md`, "Facade";
what all seven sets share, the choices made in building them and the blind
reviews are in `blender/facade/README.md`. Goes to `assets/Cosmetics/Cosmetic_GothicFacade/` once imported.

| Piece | Triangles / budget | Parts | Validated | What it is |
|---|---|---|---|---|
| `Facade_Wall` | 108 / 1,500 | Wall, LOD_Proxy | passed | a plain wall: dark slate with a stone coping, wine inside |
| `Facade_Window_TwinSash` | 1,456 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | dark slate with a stone coping, wine inside; a TwinSash window: a stone surround, a red stained-glass trim, stone tracery; the twin a pair of lancets, the round a rose |
| `Facade_Window_Arched` | 824 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | dark slate with a stone coping, wine inside; a Arched window: a stone surround, a red stained-glass trim, stone tracery; the twin a pair of lancets, the round a rose |
| `Facade_Window_Round` | 1,116 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | dark slate with a stone coping, wine inside; a Round window: a stone surround, a red stained-glass trim, stone tracery; the twin a pair of lancets, the round a rose |
| `Facade_Window_Wide` | 2,424 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | dark slate with a stone coping, wine inside; a Wide window: a stone surround, a red stained-glass trim, stone tracery; the twin a pair of lancets, the round a rose |
| `Facade_Entrance` | 1,124 / 3,000 | Wall_Left, Wall_Right, ArchLeft, ArchRight, ArchTop, Glass, Dressing, Glow_Warm_1, LOD_Proxy | passed | a pointed arch of alternating stone voussoirs, a red rose window over it, an iron lantern |
| `Facade_Corner` | 424 / 800 | Post, Dressing | passed | a dark slate post with a stone gargoyle on a corbel at the top |

**Validated in Blender** (`validation.json`): every piece refused by
`finish()` until it met the contract, then checked again on its re-imported
FBX (boxes, envelope, ends, openings seen through the wall, the entrance's
clear 9 × 9, the corner's quadrant, no flickering faces, glows, budgets).
The layout round an L of owned cells: 25 pairs of pieces that meet
(10 at outside corners, 2 at the inside one, 13 end to end),
no faults.

**Not validated**: anything in Studio (the import, `import_fixup.luau`, the
look lit, the glows), the code placing the pieces (`HotelKit.facade`).
Studio runtime is not tested.

Review pictures (not in git, rebuilt by the script): `review/sheet.png` (the
layout, the entrance with a 5-stud person, the outside and inside corners,
the plain wall and the four windows from outside and inside).
